"""
Generate real Playwright regression tests from crawled states (pages).

Each state (page) gets its own test case:
  1. Navigate to the page URL
  2. Take a full-page screenshot
  3. Compare the screenshot against the baseline
  4. Report PASS / FAIL

Clone optimization: if states A and B are clones (same DOM hash +
same screenshot hash), only ONE is tested (the representative).
The other is skipped.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
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


def _classify_states(states, dom_contents):
    """Classify each state relative to previous states.

    Clone:      same DOM hash + same screenshot hash
    Nd2-data:   same DOM hash (diff screenshot) OR structural similarity >= 0.9
    Nd3-struct: structural similarity >= 0.5
    Distinct:   no match
    """
    ND2_THRESHOLD = 0.9
    ND3_THRESHOLD = 0.5
    classifications = {}

    for i, state in enumerate(states):
        best_cls = None
        for j in range(0, i):
            other = states[j]
            if state["dom_hash"] and state["dom_hash"] == other["dom_hash"]:
                if state["screenshot_hash"] and state["screenshot_hash"] == other["screenshot_hash"]:
                    best_cls = "clone"
                    break
                else:
                    best_cls = "nd2-data"
                    continue

            struct_a = dom_contents.get(state["id"], "")
            struct_b = dom_contents.get(other["id"], "")
            if struct_a and struct_b:
                sim = SequenceMatcher(None, struct_a, struct_b).ratio()
                if sim >= ND2_THRESHOLD and best_cls not in ("clone",):
                    best_cls = "nd2-data"
                elif sim >= ND3_THRESHOLD and best_cls not in ("clone", "nd2-data"):
                    best_cls = "nd3-struct"

        classifications[state["id"]] = best_cls or "distinct"

    return classifications


def generate_tests(db: StateEyeDB, run_id: int, dst: Path) -> Path:
    run = db.fetch_run(run_id)
    base_url = run["url"]
    cfg = json.loads(run["config_json"])

    # Fetch all states (pages) for this run
    states = db.fetch_states(run_id)

    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    artifacts_dir = dst.parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Read DOM content for structural comparison
    dom_contents = {}
    for s in states:
        dom_file = Path(s["dom_path"]) if s["dom_path"] else None
        if dom_file and dom_file.exists():
            try:
                raw = dom_file.read_text(encoding="utf-8", errors="replace")
                structural = re.sub(r">([^<]+)<", "><", raw)
                structural = re.sub(r"\s+", " ", structural).strip()
                dom_contents[s["id"]] = structural
            except Exception:
                dom_contents[s["id"]] = ""
        else:
            dom_contents[s["id"]] = ""

    # Classify states
    classifications = _classify_states(states, dom_contents)

    # Build test data per state (page)
    # Skip duplicates: clone and nd2-data states share the same template,
    # so only the first representative needs testing.
    seen_clone_sigs = {}   # (dom_hash, screenshot_hash) -> first state id
    seen_nd2_structs = {}  # structural_key -> first state id
    test_states = []

    for s in states:
        state_id = s["id"]
        dom_hash = s["dom_hash"] or ""
        scr_hash = s["screenshot_hash"] or ""
        classification = classifications.get(state_id, "distinct")
        sig = (dom_hash, scr_hash)
        struct = dom_contents.get(state_id, "")

        skip = False
        representative_of = None

        if classification == "clone" and dom_hash and sig in seen_clone_sigs:
            skip = True
            representative_of = seen_clone_sigs[sig]
        elif classification == "nd2-data" and struct and struct in seen_nd2_structs:
            skip = True
            representative_of = seen_nd2_structs[struct]

        if dom_hash and sig not in seen_clone_sigs:
            seen_clone_sigs[sig] = state_id
        if classification == "nd2-data" and struct and struct not in seen_nd2_structs:
            seen_nd2_structs[struct] = state_id

        test_states.append({
            "id": state_id,
            "url": _str(s["url"]),
            "title": _str(s["title"]),
            "depth": int(s["depth"]) if s["depth"] else 0,
            "baseline_screenshot": _str(s["screenshot_path"]),
            "dom_hash": dom_hash,
            "classification": classification,
            "skip": skip,
            "representative_of": representative_of,
        })

    template = f'''"""
Auto-generated regression tests by StateEye.

Run with:  python {Path(dst).name}

Each state (page) gets its own test.
Clone and Nd2-data states are skipped — only the representative is tested.
"""

import sys
import os
import json
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


def grayscale_phash_distance(img_path_a: str, img_path_b: str) -> int:
    """Compare structure only by converting to grayscale first (ignores color)."""
    try:
        with Image.open(img_path_a) as a, Image.open(img_path_b) as b:
            return imagehash.phash(a.convert("L")) - imagehash.phash(b.convert("L"))
    except Exception as e:
        print(f"    [warn] Could not compare grayscale images: {{e}}")
        return 999


def run_tests():
    results = []
    passed = 0
    failed = 0
    skipped = 0

    artifacts = Path(__file__).resolve().parent / "artifacts"
    artifacts.mkdir(exist_ok=True)

    print("=" * 60)
    print("StateEye Regression Tests (State-Level)")
    print("=" * 60)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={{"width": 1400, "height": 900}})
        page = context.new_page()

        for idx, test in enumerate(TEST_STATES):
            test_name = f"test_state_{{idx+1}}"
            url = test["url"]
            title = test["title"]
            baseline = test["baseline_screenshot"]
            classification = test["classification"]
            is_skip = test["skip"]
            errors = []

            # Sanitize title for console output
            safe_title = title.encode("utf-8", errors="replace").decode("utf-8")
            print(f"[test] {{test_name}}: {{safe_title}}")
            print(f"       URL: {{url}} | {{classification}}")

            # Skip clone duplicates
            if is_skip:
                skipped += 1
                rep = test["representative_of"]
                print(f"       SKIP (clone of state #{{rep}})")
                results.append({{"name": test_name, "status": "SKIP", "errors": []}})
                print()
                continue

            # Step 1: Navigate to the page
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
            except Exception as e:
                errors.append(f"Navigation failed: {{e}}")
                failed += 1
                results.append({{"name": test_name, "status": "FAIL", "errors": errors}})
                print(f"       FAIL: {{errors[0]}}")
                print()
                continue

            # Step 2: Full-page screenshot comparison
            if baseline and os.path.exists(baseline):
                new_screenshot = str(artifacts / f"{{test_name}}.png")
                try:
                    page.screenshot(path=new_screenshot, full_page=True)
                except Exception as e:
                    errors.append(f"Screenshot failed: {{e}}")
                    new_screenshot = None

                if new_screenshot and os.path.exists(new_screenshot):
                    distance = phash_distance(baseline, new_screenshot)
                    print(f"       Visual distance: {{distance}}")
                    if distance > VISUAL_THRESHOLD:
                        gray_dist = grayscale_phash_distance(baseline, new_screenshot)
                        print(f"       Grayscale distance: {{gray_dist}}")
                        if gray_dist <= VISUAL_THRESHOLD:
                            print(f"       Color-only change detected (structure intact) — PASS")
                        else:
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


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
'''
    dst.write_text(template, encoding="utf-8")
    return dst
