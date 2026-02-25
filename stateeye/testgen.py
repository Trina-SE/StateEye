"""
Generate real Playwright regression tests from crawled states.

Each state (fragment) gets its own test case:
  1. Navigate to the page containing this state
  2. Verify the state element exists at its xpath
  3. Compare the state's screenshot against the baseline
  4. Report PASS / FAIL

Clone optimization: if states A and B are clones, only ONE is tested
(the representative). The other is skipped. This reduces the total
number of tests a tester needs to run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .storage import StateEyeDB


def _str(val) -> str:
    """Safely convert a DB value to str (handles bytes from sqlite)."""
    if val is None:
        return ""
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    # Remove surrogate characters that break print() on Windows
    return str(val).encode("utf-8", errors="replace").decode("utf-8")


def _safe_float(val, default=0.0) -> float:
    try:
        if val is None or isinstance(val, bytes):
            return default
        return round(float(val), 2)
    except (ValueError, TypeError):
        return default


def _safe_int(val, default=0) -> int:
    try:
        if val is None or isinstance(val, bytes):
            return default
        return int(val)
    except (ValueError, TypeError):
        return default


def generate_tests(db: StateEyeDB, run_id: int, dst: Path) -> Path:
    run = db.fetch_run(run_id)
    base_url = run["url"]
    cfg = json.loads(run["config_json"])
    headless = cfg.get("headless", True)

    # Fetch all fragments with their page info and classification
    all_frags = db.fetch_all_fragments(run_id)

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    artifacts_dir = dst.parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Build test data per state (fragment)
    # Clone skipping: group by dom_hash, keep first of each clone group
    seen_dom_hashes = {}  # dom_hash -> first fragment id
    test_states = []

    for frag in all_frags:
        dom_hash = frag["dom_hash"] or ""
        classification = frag["classification"] or "unique"
        frag_id = frag["id"]

        # Clone skipping: if this fragment's dom_hash was already seen
        # and it's a clone, mark it as skipped (will test the representative only)
        skip = False
        representative_of = None
        if classification == "clone" and dom_hash and dom_hash in seen_dom_hashes:
            skip = True
            representative_of = seen_dom_hashes[dom_hash]

        if dom_hash and dom_hash not in seen_dom_hashes:
            seen_dom_hashes[dom_hash] = frag_id

        test_states.append({
            "id": frag_id,
            "tag": _str(frag["tag"]),
            "xpath": _str(frag["xpath"]),
            "snippet": _str(frag["snippet"])[:80],
            "baseline_screenshot": _str(frag["screenshot_path"]),
            "url": _str(frag["url"]),
            "title": _str(frag["title"]),
            "depth": int(frag["depth"]) if frag["depth"] else 0,
            "classification": classification,
            "best_dom_score": _safe_float(frag["best_dom_score"]),
            "best_vis_dist": _safe_int(frag["best_vis_dist"], 999),
            "skip": skip,
            "representative_of": representative_of,
        })

    template = f'''"""
Auto-generated regression tests by StateEye.

Run with:  python {Path(dst).name}

Each state (UI fragment) gets its own test.
Clone states are skipped — only the representative is tested.
If a clone changes, it will be detected when re-crawled.
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_root = str(Path(__file__).resolve().parents[1])
if _root not in sys.path:
    sys.path.insert(0, _root)

from playwright.sync_api import sync_playwright
from PIL import Image
import imagehash

BASE_URL = {json.dumps(base_url)}
HEADLESS = True
VISUAL_THRESHOLD = 18

TEST_STATES = {json.dumps(test_states, indent=2).replace(': true', ': True').replace(': false', ': False').replace(': null', ': None')}


def phash_distance(img_path_a: str, img_path_b: str) -> int:
    try:
        with Image.open(img_path_a) as a, Image.open(img_path_b) as b:
            return imagehash.phash(a) - imagehash.phash(b)
    except Exception as e:
        print(f"    [warn] Could not compare images: {{e}}")
        return 999


def run_tests():
    results = []
    passed = 0
    failed = 0
    skipped = 0

    artifacts = Path(__file__).resolve().parent / "artifacts"
    artifacts.mkdir(exist_ok=True)

    print("=" * 60)
    print("StateEye Regression Tests")
    print("=" * 60)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={{"width": 1400, "height": 900}})
        page = context.new_page()

        loaded_url = None  # track current page to avoid re-navigation

        for idx, test in enumerate(TEST_STATES):
            test_name = f"test_state_{{idx+1}}"
            tag = test["tag"]
            xpath = test["xpath"]
            url = test["url"]
            title = test["title"]
            baseline = test["baseline_screenshot"]
            classification = test["classification"]
            snippet = test["snippet"]
            is_skip = test["skip"]
            errors = []

            label = snippet.strip() if snippet.strip() else xpath
            # Sanitize label to remove surrogate characters that break Windows console
            label = label.encode("utf-8", errors="replace").decode("utf-8")
            print(f"[test] {{test_name}}: <{{tag}}> {{label}}")
            print(f"       URL: {{url}} | {{classification}}")

            # Skip clone duplicates
            if is_skip:
                skipped += 1
                rep = test["representative_of"]
                print(f"       SKIP (clone of state #{{rep}})")
                results.append({{"name": test_name, "status": "SKIP", "errors": []}})
                print()
                continue

            # Step 1: Navigate (only if URL changed)
            if loaded_url != url:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        pass
                    loaded_url = url
                except Exception as e:
                    errors.append(f"Navigation failed: {{e}}")
                    failed += 1
                    results.append({{"name": test_name, "status": "FAIL", "errors": errors}})
                    print(f"       FAIL: {{errors[0]}}")
                    print()
                    continue

            # Step 2: Check state element exists
            if xpath:
                try:
                    el = page.query_selector(f"xpath={{xpath}}")
                    if el and el.is_visible():
                        print(f"       Element: found and visible")
                    else:
                        errors.append(f"State missing: <{{tag}}> at {{xpath}}")
                except Exception:
                    errors.append(f"State error: <{{tag}}> at {{xpath}}")

            # Step 3: Screenshot comparison
            if baseline and os.path.exists(baseline):
                new_screenshot = str(artifacts / f"{{test_name}}.png")
                try:
                    if xpath:
                        el = page.query_selector(f"xpath={{xpath}}")
                        if el:
                            el.screenshot(path=new_screenshot)
                        else:
                            page.screenshot(path=new_screenshot, full_page=True)
                    else:
                        page.screenshot(path=new_screenshot, full_page=True)
                except Exception as e:
                    errors.append(f"Screenshot failed: {{e}}")
                    new_screenshot = None

                if new_screenshot and os.path.exists(new_screenshot):
                    distance = phash_distance(baseline, new_screenshot)
                    print(f"       Visual distance: {{distance}}")
                    if distance > VISUAL_THRESHOLD:
                        errors.append(f"Visual regression: distance={{distance}}")
            else:
                print(f"       Visual: baseline not found, skipping")

            # Verdict
            if errors:
                failed += 1
                status = "FAIL"
                for e in errors:
                    print(f"       FAIL: {{e}}")
            else:
                passed += 1
                status = "PASS"
                print(f"       PASS")

            results.append({{"name": test_name, "status": status, "errors": errors}})
            print()

        page.close()
        browser.close()

    total = passed + failed + skipped
    print("=" * 60)
    print(f"Results: {{passed}} passed, {{failed}} failed, {{skipped}} skipped ({{total}} total)")
    print("=" * 60)

    results_file = artifacts / "test_results.json"
    results_file.write_text(
        json.dumps({{"passed": passed, "failed": failed, "skipped": skipped, "tests": results}}, indent=2),
        encoding="utf-8",
    )
    print(f"Results saved to: {{results_file}}")

    return failed == 0


import json

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
'''
    dst.write_text(template, encoding="utf-8")
    return dst
