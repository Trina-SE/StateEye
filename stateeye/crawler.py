"""
Crawling and state extraction powered by Playwright.
"""

from __future__ import annotations

import datetime
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from .config import CrawlConfig, SimilarityConfig
from .fragmenter import extract_fragments
from .similarity import dom_hash, perceptual_hash
from .storage import ActionRecord, StateEyeDB, StateRecord


def _css_selector(handle) -> str:
    try:
        return handle.evaluate(
            """(el) => {
                if (el.id) return '#' + el.id;
                const parts = [];
                while (el && el.nodeType === 1 && el.tagName.toLowerCase() !== 'body') {
                    let selector = el.tagName.toLowerCase();
                    if (el.classList.length) {
                        selector += '.' + Array.from(el.classList).join('.');
                    }
                    const siblings = Array.from(el.parentNode ? el.parentNode.children : []);
                    const index = siblings.filter(s => s.tagName === el.tagName).indexOf(el);
                    if (index >= 0) {
                        selector += `:nth-of-type(${index + 1})`;
                    }
                    parts.unshift(selector);
                    el = el.parentNode;
                }
                return parts.join(' > ');
            }"""
        )
    except Exception:
        return ""


def _describe_action(handle) -> Tuple[str, str]:
    try:
        text = (handle.inner_text() or "").strip()
    except Exception:
        text = ""
    try:
        aria = handle.get_attribute("aria-label") or ""
    except Exception:
        aria = ""
    description = text or aria
    tag = ""
    try:
        tag = handle.evaluate("(el) => el.tagName.toLowerCase()")
    except Exception:
        pass
    if description:
        return tag, description
    return tag, tag


class StateEyeCrawler:
    def __init__(self, crawl_cfg: CrawlConfig, sim_cfg: SimilarityConfig):
        self.cfg = crawl_cfg
        self.sim_cfg = sim_cfg
        self.run_dir = crawl_cfg.run_folder()
        # freeze the run name so subsequent calls return the same folder
        self.cfg.run_name = self.run_dir.name
        self.screenshots_dir = self.run_dir / "screenshots"
        self.doms_dir = self.run_dir / "doms"
        self.fragments_dir = self.run_dir / "fragments"
        self._pre_actions_done = False
        for d in [self.run_dir, self.screenshots_dir, self.doms_dir, self.fragments_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def crawl(self) -> Tuple[int, StateEyeDB]:
        run_name = self.cfg.run_name or self.run_dir.name
        created_at = datetime.datetime.now().isoformat()
        db = StateEyeDB(self.run_dir / "stateeye.db")
        run_id = db.create_run(run_name, self.cfg.url, created_at, asdict(self.cfg))

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.cfg.headless)
            context = browser.new_context(
                viewport={"width": self.cfg.viewport_width, "height": self.cfg.viewport_height}
            )

            queue: List[Tuple[List[ActionRecord], int]] = [([], 0)]
            visited = set()
            state_counter = 0

            while queue and state_counter < self.cfg.max_states:
                path, depth = queue.pop(0)
                page = context.new_page()
                try:
                    self._replay_actions(page, path)
                except PlaywrightTimeoutError:
                    page.close()
                    continue

                state_counter += 1
                dom_file = self.doms_dir / f"state_{state_counter}.html"
                screenshot_file = self.screenshots_dir / f"state_{state_counter}.png"

                try:
                    self._capture_page(page, dom_file, screenshot_file)
                except Exception:
                    page.close()
                    continue

                dom_content = dom_file.read_text(encoding="utf-8")
                dhash = dom_hash(dom_content)
                shash = perceptual_hash(screenshot_file)

                is_duplicate = dhash in visited
                visited.add(dhash)

                title = page.title()
                state = StateRecord(
                    url=page.url,
                    title=title,
                    dom_path=str(dom_file),
                    screenshot_path=str(screenshot_file),
                    dom_hash=dhash,
                    screenshot_hash=shash,
                    depth=depth,
                    path=path,
                    metadata={"url": page.url},
                    is_terminal=is_duplicate or depth >= self.cfg.max_depth,
                )
                state_id = db.insert_state(run_id, state)

                fragments = extract_fragments(
                    page,
                    screenshot_path=screenshot_file,
                    min_area=self.cfg.fragment_min_area,
                    limit=self.cfg.fragment_limit,
                    state_id=state_id,
                )
                db.insert_fragments(fragments)

                if state.is_terminal:
                    page.close()
                    continue

                if depth < self.cfg.max_depth:
                    actions = self._collect_actions(page)
                    for action in actions:
                        new_path = path + [action]
                        queue.append((new_path, depth + 1))

                page.close()

            browser.close()

        return run_id, db

    def _capture_page(self, page, dom_file: Path, screenshot_file: Path) -> None:
        page.wait_for_timeout(self.cfg.wait_on_load_ms)
        dom_content = page.content()
        dom_file.write_text(dom_content, encoding="utf-8")
        page.screenshot(path=str(screenshot_file), full_page=True)

    def _replay_actions(self, page, path: List[ActionRecord]) -> None:
        page.goto(self.cfg.url, wait_until="domcontentloaded", timeout=self.cfg.action_timeout_ms)
        page.wait_for_timeout(self.cfg.wait_on_load_ms)
        # Only run pre-actions once at the start (e.g., login) to avoid loops
        if not self._pre_actions_done and not path:
            self._apply_pre_actions(page)
            self._pre_actions_done = True
            if self.cfg.auto_fill_forms:
                self._auto_fill_forms(page)
        for action in path:
            self._apply_action(page, action)
            page.wait_for_timeout(self.cfg.wait_after_action_ms)
            if self.cfg.auto_fill_forms:
                self._auto_fill_forms(page)

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
            page.wait_for_timeout(self.cfg.wait_after_action_ms)

    def _auto_fill_forms(self, page) -> None:
        fillers = {
            "input[type='text']": "test",
            "input[type='email']": "user@example.com",
            "input[type='password']": "password",
            "input[type='number']": "1",
            "input[name*='user']": "admin",
            "input[name*='login']": "admin",
            "input[name*='email']": "user@example.com",
            "input[name*='pass']": "secret",
        }
        for selector, value in fillers.items():
            for handle in page.query_selector_all(selector):
                try:
                    existing = handle.input_value()
                    if existing:
                        continue
                    handle.fill(value, timeout=self.cfg.action_timeout_ms)
                except Exception:
                    continue

    def _collect_actions(self, page) -> List[ActionRecord]:
        handles = page.query_selector_all(
            "a[href], button, input[type='submit'], input[type='button'], [role='button']"
        )
        actions: List[ActionRecord] = []
        seen = set()
        for handle in handles:
            selector = _css_selector(handle)
            if not selector or selector in seen:
                continue
            seen.add(selector)
            tag, description = _describe_action(handle)
            actions.append(
                ActionRecord(
                    name=description or tag,
                    selector=selector,
                    action_type="click",
                    value=None,
                    description=description or tag,
                )
            )
        return actions
