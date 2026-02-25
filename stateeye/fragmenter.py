"""
Fragment extraction helpers.

Extracts major UI states (nav, sections, forms, etc.) from a page,
crops their screenshots, captures their DOM content, and computes hashes
for fragment-level classification.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import Page

from .similarity import dom_hash as compute_dom_hash, perceptual_hash
from .storage import FragmentRecord


# Target major structural elements — these are the "states".
FRAGMENT_SELECTOR = (
    "header, nav, main, section, article, form, aside, footer, "
    "[role='navigation'], [role='main'], [role='banner'], [role='contentinfo']"
)


def _safe_text(html_str: str, limit: int = 200) -> str:
    soup = BeautifulSoup(html_str, "lxml")
    text = soup.get_text(separator=" ", strip=True)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def _xpath_for_handle(handle) -> str:
    try:
        return handle.evaluate(
            """(node) => {
                function idx(node){
                    let i=1;
                    let sib = node.previousSibling;
                    while(sib){
                        if(sib.nodeType === 1 && sib.nodeName === node.nodeName){ i++; }
                        sib = sib.previousSibling;
                    }
                    return i;
                }
                function xpath(node){
                    if(node.id) return 'id("' + node.id + '")';
                    if(node === document.body) return '/html/body';
                    let ix = idx(node);
                    return xpath(node.parentNode) + '/' + node.nodeName.toLowerCase() + '[' + ix + ']';
                }
                return xpath(node);
            }"""
        )
    except Exception:
        return ""


def _decompose_large_containers(page: Page, handles, vp_area: float):
    """Replace large containers (main, section, article) with their children."""
    CONTAINERS = ("main", "section", "article")
    result = []
    for handle in handles:
        try:
            box = handle.bounding_box()
            tag = handle.evaluate("(el) => el.tagName.toLowerCase()")
        except Exception:
            continue
        if not box:
            continue
        area = box["width"] * box["height"]
        # If it's a large container, break it into its direct children
        if tag in CONTAINERS and area > vp_area * 0.3:
            children = handle.query_selector_all(":scope > *")
            if children:
                result.extend(children)
            else:
                result.append(handle)
        else:
            result.append(handle)
    return result


def extract_fragments(
    page: Page,
    screenshot_path: Path,
    min_area: int = 3000,
    limit: int = 50,
    state_id: int = -1,
    fragments_dir: Path | None = None,
    doms_dir: Path | None = None,
) -> List[FragmentRecord]:
    handles = page.query_selector_all(FRAGMENT_SELECTOR)
    if not handles:
        return []

    # Break large containers (main, section, article) into children
    vp = page.viewport_size or {"width": 1280, "height": 720}
    vp_area = vp["width"] * vp["height"]
    handles = _decompose_large_containers(page, handles, vp_area)
    if not handles:
        return []

    fragments: List[FragmentRecord] = []
    screenshot_path = Path(screenshot_path)
    base = screenshot_path.stem
    with Image.open(screenshot_path) as full_img:
        for idx, handle in enumerate(handles):
            try:
                box = handle.bounding_box()
            except Exception:
                continue
            if not box:
                continue
            area = box["width"] * box["height"]
            if area < min_area:
                continue

            xpath = _xpath_for_handle(handle)
            tag = handle.evaluate("(el) => el.tagName.toLowerCase()")

            # Get outerHTML for DOM-level comparison
            try:
                outer_html = handle.evaluate("(el) => el.outerHTML") or ""
            except Exception:
                outer_html = ""

            snippet = _safe_text(outer_html)
            frag_dom_hash = compute_dom_hash(outer_html) if outer_html else ""

            # Save state HTML file
            if doms_dir and outer_html:
                dom_file = doms_dir / f"{base}_state_{idx}.html"
                try:
                    dom_file.write_text(outer_html, encoding="utf-8")
                except Exception:
                    pass

            frag_dir = fragments_dir if fragments_dir else screenshot_path.parent
            frag_img_path = frag_dir / f"{base}_frag_{idx}.png"
            left = int(box["x"])
            top = int(box["y"])
            right = int(box["x"] + box["width"])
            bottom = int(box["y"] + box["height"])
            try:
                cropped = full_img.crop((left, top, right, bottom))
                cropped.save(frag_img_path)
            except Exception:
                frag_img_path = None

            frag_hash = perceptual_hash(frag_img_path) if frag_img_path else ""
            fragments.append(
                FragmentRecord(
                    state_id=state_id,
                    xpath=xpath,
                    tag=tag,
                    snippet=snippet,
                    screenshot_path=str(frag_img_path) if frag_img_path else None,
                    bbox={
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"],
                    },
                    hash=frag_hash,
                    dom_content=outer_html,
                    dom_hash=frag_dom_hash,
                )
            )
            if len(fragments) >= limit:
                break

    return fragments
