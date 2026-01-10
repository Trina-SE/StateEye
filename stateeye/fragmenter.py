"""
Fragment extraction helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import Page

from .similarity import perceptual_hash
from .storage import FragmentRecord


FRAGMENT_SELECTOR = (
    "header, nav, main, section, article, form, aside, footer, button, a, "
    "input, textarea, select, option, table, tr, td, th, li, ul, ol, div[role='button']"
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


def extract_fragments(
    page: Page,
    screenshot_path: Path,
    min_area: int = 4000,
    limit: int = 32,
    state_id: int = -1,
) -> List[FragmentRecord]:
    handles = page.query_selector_all(FRAGMENT_SELECTOR)
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
            snippet_html = handle.inner_html() or ""
            snippet = _safe_text(snippet_html)

            frag_img_path = screenshot_path.parent / f"{base}_frag_{idx}.png"
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
                )
            )
            if len(fragments) >= limit:
                break

    return fragments

