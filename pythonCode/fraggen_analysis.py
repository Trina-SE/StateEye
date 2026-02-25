"""
Bridge script called by the StateEye GUI after a crawl completes.

Runs the fragment-based analysis on an existing crawl directory and
writes a fraggen_classification.json that the GUI reads for its summary.
"""

import argparse
import json
import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parents[1])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from stateeye.config import SimilarityConfig
from stateeye.storage import StateEyeDB
from stateeye.analyzer import analyze_run


def main():
    parser = argparse.ArgumentParser(description="StateEye fragment analysis")
    parser.add_argument("--crawl-dir", required=True, help="Path to crawl output directory")
    args = parser.parse_args()

    crawl_dir = Path(args.crawl_dir)
    db_path = crawl_dir / "stateeye.db"
    if not db_path.exists():
        print(f"No database found at {db_path}", file=sys.stderr)
        sys.exit(1)

    db = StateEyeDB(db_path)
    run_id = db.latest_run_id()
    if run_id is None:
        print("No runs found in the database.", file=sys.stderr)
        db.close()
        sys.exit(1)

    sim_cfg = SimilarityConfig()
    summary = analyze_run(db, run_id, sim_cfg)

    total = len(summary.clones) + len(summary.near_duplicates) + len(summary.unique_states)
    report = {
        "summary": {
            "clone": len(summary.clones),
            "near_duplicates": len(summary.near_duplicates),
            "nd2": 0,
            "nd3": 0,
            "distinct": len(summary.unique_states),
        },
        "total_states": total,
    }

    out_path = crawl_dir / "fraggen_classification.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    db.close()
    print(f"Analysis written to {out_path}")


if __name__ == "__main__":
    main()
