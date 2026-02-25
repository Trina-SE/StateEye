"""
Near-duplicate and clone analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .config import SimilarityConfig
from .similarity import (
    combined_score,
    dom_similarity,
    is_clone,
    is_near_duplicate,
    visual_distance,
)
from .storage import ComparisonRecord, StateEyeDB


@dataclass
class AnalysisSummary:
    clones: List[int]
    near_duplicates: List[int]
    unique_states: List[int]


def classify_state_incremental(
    dom_content: str,
    screenshot_hash: str,
    dom_hash: str,
    existing_states: List[dict],
    sim_cfg: SimilarityConfig,
) -> Tuple[str, float, int]:
    """Classify a new state against all existing states incrementally.

    Returns (classification, best_dom_score, best_vis_dist).
    """
    best_dom = 0.0
    best_vis = 999
    result = "unique"

    for prev in existing_states:
        # Fast path: identical DOM hash means clone
        if dom_hash == prev["dom_hash"]:
            return ("clone", 1.0, 0)

        dom_score = dom_similarity(dom_content, prev["dom_content"])
        vis_dist = visual_distance(screenshot_hash, prev["screenshot_hash"])
        combo = combined_score(dom_score, vis_dist, sim_cfg.visual_near_duplicate_threshold)

        if is_clone(dom_score, vis_dist, sim_cfg):
            return ("clone", dom_score, vis_dist)
        if is_near_duplicate(dom_score, vis_dist, combo, sim_cfg):
            if result != "near-duplicate" or dom_score > best_dom:
                best_dom = dom_score
                best_vis = vis_dist
            result = "near-duplicate"
        elif result == "unique":
            if dom_score > best_dom:
                best_dom = dom_score
                best_vis = vis_dist

    return (result, best_dom, best_vis)


def analyze_run(db: StateEyeDB, run_id: int, sim_cfg: SimilarityConfig) -> AnalysisSummary:
    states = db.fetch_states(run_id)
    clone_ids: List[int] = []
    near_duplicate_ids: List[int] = []

    for i, state_a in enumerate(states):
        dom_a = Path(state_a["dom_path"]).read_text(encoding="utf-8")
        for state_b in states[i + 1 :]:
            dom_b = Path(state_b["dom_path"]).read_text(encoding="utf-8")
            dom_score = dom_similarity(dom_a, dom_b)
            vis_dist = visual_distance(state_a["screenshot_hash"], state_b["screenshot_hash"])
            combined = combined_score(dom_score, vis_dist, sim_cfg.visual_near_duplicate_threshold)

            clone = is_clone(dom_score, vis_dist, sim_cfg)
            nd = is_near_duplicate(dom_score, vis_dist, combined, sim_cfg)
            db.insert_comparison(
                run_id,
                ComparisonRecord(
                    state_a=state_a["id"],
                    state_b=state_b["id"],
                    dom_score=dom_score,
                    visual_distance=vis_dist,
                    combined_score=combined,
                    is_clone=clone,
                    is_near_duplicate=nd,
                ),
            )
            if clone:
                clone_ids.extend([state_a["id"], state_b["id"]])
            elif nd:
                near_duplicate_ids.extend([state_a["id"], state_b["id"]])

    clone_ids = sorted(set(clone_ids))
    near_duplicate_ids = sorted(set(near_duplicate_ids) - set(clone_ids))
    all_ids = {row["id"] for row in states}
    unique_ids = sorted(all_ids - set(clone_ids) - set(near_duplicate_ids))
    return AnalysisSummary(
        clones=clone_ids,
        near_duplicates=near_duplicate_ids,
        unique_states=unique_ids,
    )

