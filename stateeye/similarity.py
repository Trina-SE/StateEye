"""
Similarity utilities for StateEye.
"""

from __future__ import annotations

import hashlib
import html
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Tuple

from bs4 import BeautifulSoup
from PIL import Image
import imagehash


def normalize_dom(raw_dom: str) -> str:
    soup = BeautifulSoup(raw_dom, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    normalized = soup.prettify()
    normalized = re.sub(r"\s+", " ", normalized)
    return html.unescape(normalized).strip()


def dom_hash(raw_dom: str) -> str:
    normalized = normalize_dom(raw_dom)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def dom_similarity(dom_a: str, dom_b: str) -> float:
    norm_a = normalize_dom(dom_a)
    norm_b = normalize_dom(dom_b)
    return SequenceMatcher(None, norm_a, norm_b).ratio()


def perceptual_hash(image_path: Path) -> str:
    with Image.open(image_path) as img:
        return str(imagehash.phash(img))


def visual_distance(hash_a: str, hash_b: str) -> int:
    return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)


def combined_score(dom_score: float, visual_dist: int, visual_threshold: int) -> float:
    visual_score = max(0.0, 1.0 - (visual_dist / max(visual_threshold, 1)))
    return 0.6 * dom_score + 0.4 * visual_score


def is_clone(dom_score: float, visual_dist: int, cfg) -> bool:
    return dom_score >= cfg.dom_clone_threshold and visual_dist <= cfg.visual_clone_threshold


def is_near_duplicate(dom_score: float, visual_dist: int, combined: float, cfg) -> bool:
    if is_clone(dom_score, visual_dist, cfg):
        return False
    dom_nd = dom_score >= cfg.dom_near_duplicate_threshold
    visual_nd = visual_dist <= cfg.visual_near_duplicate_threshold
    return (dom_nd and visual_nd) or combined >= cfg.combined_near_duplicate_score

