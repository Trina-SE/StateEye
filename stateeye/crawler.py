"""
Crawling and state extraction powered by Playwright.

Uses a single persistent browser page so that login credentials are
entered only once and session cookies are preserved throughout the crawl.

Strategy: click-based BFS — clicks links like a real tester, but tracks
all discovered URLs so it never clicks the same link twice.
"""

from __future__ import annotations

import datetime
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
        parsed = urlparse(self.cfg.url)
        self._base_domain = parsed.netloc or ""
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
            page.wait_for_load_state("networkidle", timeout=min(timeout, 5000))
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
            step = self.cfg.viewport_height // 2
            pos = 0
            while pos < total:
                page.evaluate(f"window.scrollTo(0, {pos})")
                page.wait_for_timeout(300)
                pos += step
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(200)
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
            self._safe_goto(page, self.cfg.url)
            self._apply_pre_actions(page)

            if self.cfg.auto_fill_forms:
                filled_count = self._auto_fill_forms(page)
                if filled_count > 0:
                    print(f"[crawl] [{self._elapsed()}] Filled {filled_count} form fields, submitting login...", flush=True)
                    self._try_submit_login(page)
                    self._wait_for_page_ready(page)

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

                # Extract fragments (components) — each is a "state"
                fragments = extract_fragments(
                    page,
                    screenshot_path=screenshot_file,
                    min_area=self.cfg.fragment_min_area,
                    limit=self.cfg.fragment_limit,
                    state_id=state_id,
                )
                db.insert_fragments(fragments)

                print(
                    f"[state] [{self._elapsed()}] Page #{page_counter}: "
                    f"{len(fragments)} components at depth {depth}: {page.url}",
                    flush=True,
                )

                # Classify each fragment against all previous fragments
                for frag in fragments:
                    if not frag.dom_content and not frag.hash:
                        continue
                    fragment_counter += 1

                    classification, best_dom, best_vis = classify_state_incremental(
                        frag.dom_content, frag.hash, frag.dom_hash,
                        captured_fragments, self.sim_cfg,
                    )
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
            f"[crawl] [{self._elapsed()}] Finished. {page_counter} pages, {fragment_counter} components | "
            f"unique={class_counts['unique']} "
            f"clones={class_counts['clone']} "
            f"near-dup={class_counts['near-duplicate']}",
            flush=True,
        )
        return run_id, db

    # ── Page capture ─────────────────────────────────────────────────

    def _capture_page(self, page, dom_file: Path, screenshot_file: Path) -> None:
        dom_content = page.content()
        dom_file.write_text(dom_content, encoding="utf-8")
        page.screenshot(path=str(screenshot_file), full_page=True)

    # ── Click-based exploration (like a real tester) ────────────────

    def _explore_page_by_clicking(self, page, current_url: str) -> Tuple[List[str], int]:
        """Click visible links and buttons like a real tester.

        - Only clicks links to URLs we've never seen before (_known_urls)
        - Skips buttons inside <form> (no random form submissions)
        - After each click that navigates, goes back to continue

        Returns (discovered_urls, total_clicks).
        """
        discovered: List[str] = []
        actions_count = 0

        # ── Phase 1: Collect unvisited link info ──
        links_to_click: List[dict] = []
        seen_here: set = set()
        try:
            anchors = page.query_selector_all("a[href]")
            for a in anchors:
                try:
                    if not a.is_visible():
                        continue
                    href = a.get_attribute("href") or ""
                    if not href:
                        continue
                    parsed = urlparse(href)
                    if parsed.netloc and parsed.netloc != self._base_domain:
                        continue
                    if parsed.scheme and parsed.scheme not in ("http", "https", "file", ""):
                        continue
                    resolved = urljoin(page.url, href).rstrip("/")
                    # Skip if we already know about this URL (visited OR queued)
                    if resolved in self._known_urls or resolved in seen_here:
                        continue
                    seen_here.add(resolved)
                    text = ""
                    try:
                        text = (a.inner_text() or "").strip()[:40]
                    except Exception:
                        pass
                    links_to_click.append({"href": href, "text": text or href, "resolved": resolved})
                except Exception:
                    continue
        except Exception:
            pass

        # ── Phase 2: Click each new link ──
        for info in links_to_click:
            if info["resolved"] in self._known_urls:
                continue  # may have been added by a prior click in this loop
            if not self._is_page_alive(page):
                break
            try:
                handle = self._find_link_by_href(page, info["href"])
                if not handle:
                    continue

                handle.scroll_into_view_if_needed(timeout=2000)
                handle.click(timeout=self.cfg.action_timeout_ms)
                self._wait_for_page_ready(page)
                actions_count += 1

                after_url = page.url
                navigated = after_url.rstrip("/") != current_url.rstrip("/")

                print(
                    f"[click] [{self._elapsed()}] <{info['text']}> "
                    f"{'-> ' + after_url if navigated else '(same page)'}",
                    flush=True,
                )

                if navigated:
                    after_norm = after_url.rstrip("/")
                    if after_norm not in self._known_urls:
                        discovered.append(after_url)
                    # Go back to continue exploring this page
                    self._safe_goto(page, current_url)
            except Exception:
                try:
                    self._safe_goto(page, current_url)
                except Exception:
                    pass
                continue

        # ── Phase 3: Click non-form buttons ──
        clicked_btn_keys: set = set()
        for _safety in range(20):
            if not self._is_page_alive(page):
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
