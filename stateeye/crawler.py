from __future__ import annotations

import datetime
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from .analyzer import classify_state_incremental
from .config import CrawlConfig, SimilarityConfig, load_credentials
from .fragmenter import extract_fragments
from .similarity import dom_hash, perceptual_hash
from .storage import ActionRecord, StateEyeDB, StateRecord


class StateEyeCrawler:
    def __init__(self, crawl_cfg: CrawlConfig, sim_cfg: SimilarityConfig):
        self.cfg = crawl_cfg
        self.sim_cfg = sim_cfg
        # Normalize URL: add https:// if no scheme and not a file path
        url = self.cfg.url.strip()
        if not url.startswith(("http://", "https://", "file:///")) and not Path(url).exists():
            url = "https://" + url
            self.cfg.url = url
        self.run_dir = crawl_cfg.run_folder()
        self.cfg.run_name = self.run_dir.name
        self.screenshots_dir = self.run_dir / "screenshots"
        self.doms_dir = self.run_dir / "doms"
        self.fragments_dir = self.run_dir / "fragments"
        self._credentials: Dict[str, str] | None = None
        self._start_time: float = 0.0
        self._home_url: str = ""
        self._is_local: bool = False
        self._visited_urls: set = set()   # URLs we actually navigated to
        self._known_urls: set = set()     # ALL URLs we know about (visited + queued)
        self._url_to_page: Dict[str, int] = {}   # normalized_url -> node index (0-based)
        self._graph_edges: List[dict] = []        # click transitions
        parsed = urlparse(self.cfg.url)
        self._base_domain = parsed.netloc or ""
        # Also store root domain for subdomain matching (e.g. www.w3schools.com -> w3schools.com)
        parts = self._base_domain.split(".")
        self._root_domain = ".".join(parts[-2:]) if len(parts) >= 2 else self._base_domain
        for d in [self.run_dir, self.screenshots_dir, self.doms_dir, self.fragments_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def _elapsed(self) -> str:
        secs = int(time.time() - self._start_time)
        mins, s = divmod(secs, 60)
        return f"{mins}m {s:02d}s"

    # ── Smart waiting ────────────────────────────────────────────────

    def _wait_for_page_ready(self, page, timeout_ms: int | None = None) -> None:
        timeout = timeout_ms or self.cfg.action_timeout_ms
        try:
            page.wait_for_load_state("networkidle", timeout=min(timeout, 3000))
        except PlaywrightTimeoutError:
            pass

    def _safe_goto(self, page, url: str) -> None:
        same_page = page.url.rstrip("/") == url.rstrip("/")
        try:
            if same_page:
                page.reload(wait_until="load", timeout=self.cfg.action_timeout_ms)
            else:
                page.goto(url, wait_until="domcontentloaded", timeout=self.cfg.action_timeout_ms)
        except PlaywrightTimeoutError:
            pass
        self._wait_for_page_ready(page)

    def _is_page_alive(self, page) -> bool:
        """Check if the page is still usable."""
        try:
            page.url  # simple property access — throws if closed
            return True
        except Exception:
            return False

    # ── Page scrolling ───────────────────────────────────────────────

    def _scroll_page(self, page) -> None:
        """Scroll top to bottom to trigger lazy-loaded content."""
        try:
            total = page.evaluate("() => document.body.scrollHeight")
            step = self.cfg.viewport_height  # full viewport per step (faster)
            pos = 0
            while pos < total:
                page.evaluate(f"window.scrollTo(0, {pos})")
                page.wait_for_timeout(150)
                pos += step
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(100)
        except Exception:
            pass

    # ── Main crawl ───────────────────────────────────────────────────

    def crawl(self) -> Tuple[int, StateEyeDB]:
        self._start_time = time.time()
        run_name = self.cfg.run_name or self.run_dir.name
        created_at = datetime.datetime.now().isoformat()
        db = StateEyeDB(self.run_dir / "stateeye.db")
        run_id = db.create_run(run_name, self.cfg.url, created_at, asdict(self.cfg))

        self._is_local = (
            self.cfg.url.startswith("file:///")
            or not self.cfg.url.startswith("http")
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.cfg.headless)
            context = browser.new_context(
                viewport={"width": self.cfg.viewport_width, "height": self.cfg.viewport_height}
            )
            page = context.new_page()

            print(f"[crawl] [{self._elapsed()}] Starting crawl of {self.cfg.url} | mode={self.cfg.mode}", flush=True)
            print(f"[crawl] [{self._elapsed()}] Max depth={self.cfg.max_depth}, max states={self.cfg.max_states}", flush=True)

            # ── Phase 1: Navigate & login ONCE ──
            original_url = self.cfg.url
            self._safe_goto(page, original_url)
            self._apply_pre_actions(page)

            if self.cfg.auto_fill_forms:
                filled_count = self._auto_fill_forms(page)
                if filled_count > 0:
                    print(f"[crawl] [{self._elapsed()}] Filled {filled_count} form fields, submitting login...", flush=True)
                    self._try_submit_login(page)
                    self._wait_for_page_ready(page)
                elif self._get_credentials():
                    # No form on landing page — find a login/signup link
                    print(f"[crawl] [{self._elapsed()}] No form on landing page, searching for login link...", flush=True)
                    if self._navigate_to_login(page):
                        filled_count = self._auto_fill_forms(page)
                        if filled_count > 0:
                            print(f"[crawl] [{self._elapsed()}] Filled {filled_count} fields on login page, submitting...", flush=True)
                            self._try_submit_login(page)
                            self._wait_for_page_ready(page)
                            # Return to original URL to crawl in authenticated state
                            print(f"[crawl] [{self._elapsed()}] Login done at {page.url}, returning to {original_url}", flush=True)
                            self._safe_goto(page, original_url)
                        else:
                            print(f"[warn] [{self._elapsed()}] Login page found but no fillable fields", flush=True)
                    else:
                        print(f"[warn] [{self._elapsed()}] No login link found on landing page", flush=True)

            self._home_url = page.url
            self._known_urls.add(self._home_url.rstrip("/"))
            print(f"[crawl] [{self._elapsed()}] Ready at: {self._home_url}", flush=True)

            # ── Phase 2: Click-based BFS with fragment-level states ──
            url_queue: List[Tuple[str, int]] = [(self._home_url, 0)]
            captured_fragments: List[dict] = []  # all fragments across pages
            class_counts: Dict[str, int] = {"unique": 0, "clone": 0, "near-duplicate": 0}
            page_counter = 0
            fragment_counter = 0

            while url_queue and page_counter < self.cfg.max_states:
                # Time limit
                if self.cfg.max_runtime_s > 0 and (time.time() - self._start_time) >= self.cfg.max_runtime_s:
                    print(f"[crawl] [{self._elapsed()}] Time limit reached ({self.cfg.max_runtime_s}s), stopping", flush=True)
                    break

                url, depth = url_queue.pop(0)

                url_norm = url.rstrip("/")
                if url_norm in self._visited_urls:
                    continue
                self._visited_urls.add(url_norm)
                self._known_urls.add(url_norm)

                # Navigate directly to the URL
                print(f"[visit] [{self._elapsed()}] depth={depth} -> {url}", flush=True)

                # Check page health; recreate if needed
                if not self._is_page_alive(page):
                    try:
                        page = context.new_page()
                        print(f"[warn] [{self._elapsed()}] Page recovered", flush=True)
                    except Exception:
                        print(f"[warn] [{self._elapsed()}] Cannot recover page, stopping", flush=True)
                        break

                try:
                    self._safe_goto(page, url)
                except PlaywrightTimeoutError:
                    print(f"[warn] [{self._elapsed()}] Timeout navigating to {url}, skipping", flush=True)
                    continue
                except Exception as exc:
                    print(f"[warn] [{self._elapsed()}] Error navigating: {exc}", flush=True)
                    continue

                # Check actual URL after navigation (redirects)
                actual_url = page.url.rstrip("/")
                if actual_url != url_norm and actual_url in self._visited_urls:
                    print(f"[skip] [{self._elapsed()}] Redirected to already-visited: {page.url}", flush=True)
                    continue
                self._visited_urls.add(actual_url)
                self._known_urls.add(actual_url)

                # Scroll the page to reveal all content
                self._scroll_page(page)

                # Capture page-level screenshot and DOM (for report)
                page_counter += 1
                node_idx = page_counter - 1  # 0-based for graph
                self._url_to_page[url_norm] = node_idx
                self._url_to_page[actual_url] = node_idx
                dom_file = self.doms_dir / f"page_{page_counter}.html"
                screenshot_file = self.screenshots_dir / f"page_{page_counter}.png"

                try:
                    self._capture_page(page, dom_file, screenshot_file)
                except Exception:
                    continue

                page_dom = dom_file.read_text(encoding="utf-8")
                page_dhash = dom_hash(page_dom)
                page_shash = perceptual_hash(screenshot_file)

                title = page.title()
                state = StateRecord(
                    url=page.url,
                    title=title,
                    dom_path=str(dom_file),
                    screenshot_path=str(screenshot_file),
                    dom_hash=page_dhash,
                    screenshot_hash=page_shash,
                    depth=depth,
                    path=[],
                    metadata={"url": page.url},
                    is_terminal=depth >= self.cfg.max_depth,
                )
                state_id = db.insert_state(run_id, state)

                # Extract fragments (states) — each is a "state"
                fragments = extract_fragments(
                    page,
                    screenshot_path=screenshot_file,
                    min_area=self.cfg.fragment_min_area,
                    limit=self.cfg.fragment_limit,
                    state_id=state_id,
                    fragments_dir=self.fragments_dir,
                    doms_dir=self.doms_dir,
                )

                # Classify each fragment against all previous fragments
                for frag in fragments:
                    if not frag.dom_content and not frag.hash:
                        frag.classification = "unique"
                        fragment_counter += 1
                        class_counts["unique"] += 1
                        continue
                    fragment_counter += 1

                    classification, best_dom, best_vis = classify_state_incremental(
                        frag.dom_content, frag.hash, frag.dom_hash,
                        captured_fragments, self.sim_cfg,
                    )
                    frag.classification = classification
                    frag.best_dom_score = best_dom
                    frag.best_vis_dist = best_vis
                    captured_fragments.append({
                        "dom_hash": frag.dom_hash,
                        "screenshot_hash": frag.hash,
                        "dom_content": frag.dom_content,
                    })
                    class_counts[classification] += 1
                    print(
                        f"[classify] [{self._elapsed()}] <{frag.tag}> {classification} "
                        f"(dom={best_dom:.2f}, vis={best_vis}) | "
                        f"unique={class_counts['unique']} "
                        f"clones={class_counts['clone']} "
                        f"near-dup={class_counts['near-duplicate']}",
                        flush=True,
                    )

                db.insert_fragments(fragments)

                print(
                    f"[state] [{self._elapsed()}] Page #{page_counter}: "
                    f"{len(fragments)} states at depth {depth}: {page.url}",
                    flush=True,
                )

                # Explore page by clicking links & buttons
                if depth < self.cfg.max_depth:
                    new_urls, click_count = self._explore_page_by_clicking(page, url)
                    print(f"[action] [{self._elapsed()}] Clicked {click_count} elements, discovered {len(new_urls)} new pages", flush=True)

                    for discovered_url in new_urls:
                        dnorm = discovered_url.rstrip("/")
                        if dnorm not in self._known_urls:
                            self._known_urls.add(dnorm)
                            url_queue.append((discovered_url, depth + 1))

            page.close()
            browser.close()

        print(
            f"[crawl] [{self._elapsed()}] Finished. {page_counter} pages, {fragment_counter} states | "
            f"unique={class_counts['unique']} "
            f"clones={class_counts['clone']} "
            f"near-dup={class_counts['near-duplicate']}",
            flush=True,
        )
        self._write_alchemy_graph(db, run_id)
        return run_id, db

    # ── Page capture ─────────────────────────────────────────────────

    def _capture_page(self, page, dom_file: Path, screenshot_file: Path) -> None:
        dom_content = page.content()
        dom_file.write_text(dom_content, encoding="utf-8")
        page.screenshot(path=str(screenshot_file), full_page=True)

    # ── Graph generation ─────────────────────────────────────────────

    def _write_alchemy_graph(self, db: StateEyeDB, run_id: int) -> None:
        """Write alchemyGraph.json with nodes (states) and links (edges)."""
        states = db.fetch_states(run_id)
        fragments_map = db.fetch_fragments([s["id"] for s in states])

        nodes = []
        for i, state in enumerate(states):
            url_norm = state["url"].rstrip("/")
            node_id = self._url_to_page.get(url_norm, i)

            # Build candidateElements from fragments
            frags = fragments_map.get(state["id"], [])
            candidate_elements = []
            for f in frags:
                try:
                    bbox = json.loads(f["bbox_json"]) if f["bbox_json"] else {}
                except Exception:
                    bbox = {}
                candidate_elements.append({
                    "top": int(bbox.get("y", 0)),
                    "left": int(bbox.get("x", 0)),
                    "xpath": f["xpath"] or "",
                    "width": int(bbox.get("width", 0)),
                    "height": int(bbox.get("height", 0)),
                })

            nodes.append({
                "name": f"state{node_id}",
                "url": state["url"],
                "candidateElements": candidate_elements,
                "fanIn": 0,
                "fanOut": 0,
                "id": node_id,
                "failedEvents": [],
                "hasNearDuplicate": False,
                "distToNearestState": -1.0,
                "cluster": -1,
                "timeAdded": int(time.time() * 1000),
                "nearestState": "",
            })

        # Resolve edges to node IDs
        links = []
        for edge in self._graph_edges:
            source_id = self._url_to_page.get(edge["source_url"])
            target_id = self._url_to_page.get(edge["target_url"])
            if source_id is not None and target_id is not None:
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "text": edge["text"],
                    "element": edge["element"],
                    "eventType": edge["eventType"],
                })

        # Compute fanIn / fanOut
        node_map = {n["id"]: n for n in nodes}
        for link in links:
            if link["source"] in node_map:
                node_map[link["source"]]["fanOut"] += 1
            if link["target"] in node_map:
                node_map[link["target"]]["fanIn"] += 1

        graph = {"nodes": nodes, "links": links}
        graph_file = self.run_dir / "alchemyGraph.json"
        graph_file.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        print(
            f"[crawl] [{self._elapsed()}] Graph: {len(nodes)} nodes, {len(links)} edges -> {graph_file.name}",
            flush=True,
        )

    # ── Click-based exploration (like a real tester) ────────────────

    def _explore_page_by_clicking(self, page, current_url: str) -> Tuple[List[str], int]:
        """Discover links from the page and optionally click buttons.

        Phase 1: Extract all <a href> URLs directly from the DOM (instant,
        no clicking needed).  This is orders of magnitude faster than
        click-navigate-back for each link.

        Phase 2: Click a small number of non-form buttons to discover
        dynamic content / JS-driven navigation.

        Returns (discovered_urls, total_clicks).
        """
        discovered: List[str] = []
        actions_count = 0

        # ── Phase 1: Harvest URLs from href attributes (fast, no clicks) ──
        try:
            # Use a single JS call to collect all hrefs — avoids per-element round-trips
            raw_links = page.evaluate("""() => {
                const results = [];
                for (const a of document.querySelectorAll('a[href]')) {
                    const rect = a.getBoundingClientRect();
                    // Include links even if off-screen (nav menus, footers, etc.)
                    const href = a.href;  // fully resolved by browser
                    const rawHref = a.getAttribute('href') || '';
                    const text = (a.innerText || '').trim().substring(0, 40);
                    if (href) results.push({href: href, rawHref: rawHref, text: text});
                }
                return results;
            }""")
        except Exception:
            raw_links = []

        seen_here: set = set()
        for link in raw_links:
            href = link.get("href", "")
            raw_href = link.get("rawHref", "")
            text = link.get("text", "") or raw_href
            if not href:
                continue
            parsed = urlparse(href)
            # Skip external domains (allow same root domain incl. subdomains)
            if parsed.netloc and not parsed.netloc.endswith(self._root_domain):
                continue
            # Skip non-http schemes (mailto:, javascript:, tel:, etc.)
            if parsed.scheme and parsed.scheme not in ("http", "https", "file", ""):
                continue
            # Strip fragment for dedup but keep full URL for queue
            resolved_no_frag = href.split("#")[0].rstrip("/")
            if not resolved_no_frag:
                continue
            if resolved_no_frag in self._known_urls or resolved_no_frag in seen_here:
                continue
            seen_here.add(resolved_no_frag)
            discovered.append(href.split("#")[0])  # queue without fragment
            # Record graph edge
            self._graph_edges.append({
                "source_url": current_url.rstrip("/"),
                "target_url": resolved_no_frag,
                "text": text,
                "element": f"A[href={raw_href}][text={text}]",
                "eventType": "link",
            })

        if discovered:
            print(
                f"[harvest] [{self._elapsed()}] Extracted {len(discovered)} new URLs from page links",
                flush=True,
            )

        # ── Phase 2: Click a limited number of non-form buttons ──
        clicked_btn_keys: set = set()
        max_button_clicks = 10  # cap to avoid wasting time
        for _safety in range(max_button_clicks):
            if not self._is_page_alive(page):
                break
            # Time check — don't burn the whole budget on buttons
            if self.cfg.max_runtime_s > 0 and (time.time() - self._start_time) >= self.cfg.max_runtime_s:
                break
            try:
                buttons = page.query_selector_all(
                    "button, input[type='submit'], input[type='button'], [role='button']"
                )
            except Exception:
                break

            found_new = False
            for btn in buttons:
                try:
                    if not btn.is_visible():
                        continue
                    # Skip buttons inside forms (don't submit random forms)
                    in_form = btn.evaluate("(el) => !!el.closest('form')")
                    if in_form:
                        continue
                    text = ""
                    try:
                        text = (btn.inner_text() or "").strip()[:40]
                    except Exception:
                        pass
                    btn_key = text or "button"
                    if btn_key in clicked_btn_keys:
                        continue
                    clicked_btn_keys.add(btn_key)
                    found_new = True

                    btn.scroll_into_view_if_needed(timeout=2000)
                    btn.click(timeout=self.cfg.action_timeout_ms)
                    self._wait_for_page_ready(page)
                    actions_count += 1

                    after_url = page.url
                    navigated = after_url.rstrip("/") != current_url.rstrip("/")

                    print(
                        f"[click] [{self._elapsed()}] <{btn_key}> "
                        f"{'-> ' + after_url if navigated else '(same page)'}",
                        flush=True,
                    )

                    if navigated:
                        after_norm = after_url.rstrip("/")
                        if after_norm not in self._known_urls:
                            discovered.append(after_url)
                        self._graph_edges.append({
                            "source_url": current_url.rstrip("/"),
                            "target_url": after_norm,
                            "text": btn_key,
                            "element": f"BUTTON[text={btn_key}]",
                            "eventType": "click",
                        })
                        self._safe_goto(page, current_url)
                    break  # re-query buttons (handles stale after click)
                except Exception:
                    try:
                        self._safe_goto(page, current_url)
                    except Exception:
                        pass
                    break

            if not found_new:
                break

        return discovered, actions_count

    def _find_link_by_href(self, page, href: str):
        """Re-find a visible <a> element by its href (handles go stale after nav)."""
        try:
            anchors = page.query_selector_all("a[href]")
            for a in anchors:
                try:
                    if a.get_attribute("href") == href and a.is_visible():
                        return a
                except Exception:
                    continue
        except Exception:
            pass
        return None

    # ── Pre-actions (kept for login flows) ───────────────────────────

    def _apply_action(self, page, action: ActionRecord) -> None:
        handle = page.query_selector(action.selector)
        if not handle:
            return
        if action.action_type == "click":
            handle.click(timeout=self.cfg.action_timeout_ms)
        elif action.action_type == "fill":
            value = action.value or "test"
            handle.fill(value, timeout=self.cfg.action_timeout_ms)
        elif action.action_type == "submit":
            handle.evaluate("(el) => el.submit && el.submit()")

    def _apply_pre_actions(self, page) -> None:
        if not self.cfg.pre_actions:
            return
        for item in self.cfg.pre_actions:
            action = ActionRecord(
                name=item.get("name") or item.get("selector", ""),
                selector=item["selector"],
                action_type=item.get("action_type", "click"),
                value=item.get("value"),
                description=item.get("description", ""),
            )
            self._apply_action(page, action)
            self._wait_for_page_ready(page)

    # ── One-time login ────────────────────────────────────────────────

    def _try_submit_login(self, page) -> None:
        try:
            submit = page.query_selector(
                "input[type='submit'], button[type='submit'], "
                "form button, "
                "button:has-text('Log in'), button:has-text('Login'), "
                "button:has-text('Sign in'), button:has-text('Submit'), "
                "button:has-text('Sign up'), button:has-text('Register'), "
                "button:has-text('Create account'), "
                "button:has-text('Enter'), button:has-text('Go')"
            )
            if submit:
                submit.click(timeout=self.cfg.action_timeout_ms)
                self._wait_for_page_ready(page)
                print(f"[crawl] [{self._elapsed()}] Login submitted -> {page.url}", flush=True)
            else:
                page.keyboard.press("Enter")
                self._wait_for_page_ready(page)
                print(f"[crawl] [{self._elapsed()}] Login via Enter key -> {page.url}", flush=True)
        except Exception as exc:
            print(f"[warn] [{self._elapsed()}] Could not submit login: {exc}", flush=True)

    # ── Navigate to login page ───────────────────────────────────────

    def _navigate_to_login(self, page) -> bool:
        """Find and click a login/signup link or button on the current page.

        Searches for common login-related text and href patterns.  Returns
        True if a navigation to a login page was triggered.
        """
        # Text-based selectors (most reliable across sites)
        text_selectors = [
            "a:has-text('Log in')", "a:has-text('Login')",
            "a:has-text('Log In')", "a:has-text('LOG IN')",
            "a:has-text('Sign in')", "a:has-text('Sign In')",
            "a:has-text('Signin')", "a:has-text('SIGN IN')",
            "button:has-text('Log in')", "button:has-text('Login')",
            "button:has-text('Log In')", "button:has-text('LOG IN')",
            "button:has-text('Sign in')", "button:has-text('Sign In')",
            "a:has-text('Sign up')", "a:has-text('Sign Up')",
            "a:has-text('Signup')", "a:has-text('SIGN UP')",
            "a:has-text('Register')", "a:has-text('Create account')",
            "button:has-text('Sign up')", "button:has-text('Sign Up')",
            "button:has-text('Register')", "button:has-text('Get started')",
        ]
        # Href-pattern selectors (fallback)
        href_selectors = [
            "a[href*='login']", "a[href*='signin']", "a[href*='sign-in']",
            "a[href*='log-in']", "a[href*='auth']",
            "a[href*='signup']", "a[href*='sign-up']", "a[href*='register']",
            "a[href*='account']",
        ]

        for selector in text_selectors + href_selectors:
            try:
                el = page.query_selector(selector)
                if el and el.is_visible():
                    label = ""
                    try:
                        label = (el.inner_text() or "").strip()[:40]
                    except Exception:
                        label = selector
                    el.click(timeout=self.cfg.action_timeout_ms)
                    self._wait_for_page_ready(page)
                    print(
                        f"[crawl] [{self._elapsed()}] Clicked '{label}' -> {page.url}",
                        flush=True,
                    )
                    return True
            except Exception:
                continue
        return False

    # ── Credential-aware form filling ─────────────────────────────────

    def _get_credentials(self) -> Dict[str, str]:
        if self._credentials is not None:
            return self._credentials
        if self.cfg.credentials_file:
            self._credentials = load_credentials(self.cfg.credentials_file)
            if self._credentials:
                print(f"[crawl] [{self._elapsed()}] Loaded credentials ({len(self._credentials)} fields)", flush=True)
        if self._credentials is None:
            self._credentials = {}
        return self._credentials

    def _match_credential(self, attrs: dict, creds: dict) -> str:
        name = attrs.get("name", "").lower()
        input_type = attrs.get("type", "").lower()
        el_id = attrs.get("id", "").lower()
        placeholder = attrs.get("placeholder", "").lower()
        autocomplete = attrs.get("autocomplete", "").lower()
        combined = f"{name} {el_id} {placeholder} {autocomplete}"
        if input_type == "password" or "pass" in combined:
            return creds.get("password", "password")
        if input_type == "email" or "email" in combined or "mail" in combined:
            return creds.get("email", "user@example.com")
        if any(k in combined for k in ("user", "login", "uname", "account")):
            return creds.get("username", "admin")
        if "name" in combined and "user" not in combined:
            return creds.get("name", "Test User")
        if any(k in combined for k in ("phone", "tel", "mobile")):
            return creds.get("phone", "555-0100")
        if input_type == "number":
            return "1"
        if input_type in ("text", ""):
            return creds.get("username", "test")
        return ""

    def _auto_fill_forms(self, page) -> int:
        creds = self._get_credentials()
        filled = 0
        try:
            inputs = page.query_selector_all(
                "input:not([type='hidden']):not([type='submit']):not([type='button'])"
                ":not([type='checkbox']):not([type='radio']):not([type='file']), textarea"
            )
        except Exception:
            return 0
        for handle in inputs:
            try:
                existing = handle.input_value()
                if existing:
                    continue
                attrs = handle.evaluate("""(el) => ({
                    name: el.name || '',
                    type: el.type || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    autocomplete: el.autocomplete || ''
                })""")
                value = self._match_credential(attrs, creds)
                if value:
                    handle.fill(value, timeout=self.cfg.action_timeout_ms)
                    filled += 1
            except Exception:
                continue
        return filled
