"""
HTML report generation for StateEye.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from .analyzer import AnalysisSummary
from .config import ReportConfig
from .storage import StateEyeDB


def build_report(db: StateEyeDB, run_id: int, summary: AnalysisSummary, dst: Path, cfg: ReportConfig) -> None:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    states = db.fetch_states(run_id)
    fragments = db.fetch_fragments([row["id"] for row in states]) if cfg.include_fragments else {}

    def classify(state_id: int) -> str:
        if state_id in summary.clones:
            return "clone"
        if state_id in summary.near_duplicates:
            return "near-duplicate"
        return "unique"

    rows = []
    for row in states:
        ss_rel = os.path.relpath(row["screenshot_path"], dst.parent)
        fragment_html = ""
        if cfg.include_fragments and row["id"] in fragments:
            fragment_html = "<div class='fragments'>" + "".join(
                [
                    f"<div class='fragment'><strong>{f['tag']}</strong>"
                    f"<div>{f['snippet']}</div>"
                    + (
                        f"<img src='{os.path.relpath(f['screenshot_path'], dst.parent)}' alt='fragment'/>"
                        if f["screenshot_path"]
                        else ""
                    )
                    + "</div>"
                    for f in fragments[row["id"]]
                ]
            ) + "</div>"

        rows.append(
            f"""
            <section class="state {classify(row['id'])}">
                <h3>State {row['id']} ({classify(row['id'])})</h3>
                <p><strong>URL:</strong> {row['url']}</p>
                <p><strong>Depth:</strong> {row['depth']}</p>
                <p><strong>Title:</strong> {row['title']}</p>
                <div class="screenshot"><img src="{ss_rel}" alt="screenshot"/></div>
                {fragment_html}
            </section>
            """
        )

    html = f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>{cfg.title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 1.5rem; }}
            header {{ margin-bottom: 1rem; }}
            .counts span {{ margin-right: 1rem; }}
            .state {{ border: 1px solid #e2e2e2; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }}
            .state.clone {{ border-color: #d9534f; background: #fff5f5; }}
            .state.near-duplicate {{ border-color: #f0ad4e; background: #fffaf2; }}
            .state.unique {{ border-color: #5cb85c; background: #f7fff7; }}
            .screenshot img {{ max-width: 100%; border: 1px solid #ccc; border-radius: 4px; }}
            .fragment {{ border: 1px dashed #ccc; padding: 0.5rem; margin: 0.5rem 0; }}
            .fragment img {{ max-width: 400px; display: block; }}
        </style>
    </head>
    <body>
        <header>
            <h1>{cfg.title}</h1>
            <div class="counts">
                <span>States: {len(states)}</span>
                <span>Unique: {len(summary.unique_states)}</span>
                <span>Near-duplicates: {len(summary.near_duplicates)}</span>
                <span>Clones: {len(summary.clones)}</span>
            </div>
        </header>
        {''.join(rows)}
    </body>
    </html>
    """
    dst.write_text(html, encoding="utf-8")

    json_dst = dst.with_suffix(".json")
    json_dst.write_text(
        json.dumps(
            {
                "counts": {
                    "states": len(states),
                    "unique": len(summary.unique_states),
                    "near_duplicates": len(summary.near_duplicates),
                    "clones": len(summary.clones),
                },
                "clones": summary.clones,
                "near_duplicates": summary.near_duplicates,
                "unique_states": summary.unique_states,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

