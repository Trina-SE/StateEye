"""
Bridge script that the StateEye GUI calls to run an automated crawl.

Accepts the arguments passed by stateeye_gui.py and delegates to the
stateeye crawl engine, producing a result.json in the output directory
that the GUI can parse for its summary.
"""

import argparse
import json
import sys
import traceback
from pathlib import Path

# Ensure the project root is on sys.path so ``import stateeye`` works
# regardless of working directory.
_project_root = str(Path(__file__).resolve().parents[1])
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from stateeye.config import CrawlConfig, SimilarityConfig, ReportConfig
from stateeye.crawler import StateEyeCrawler
from stateeye.analyzer import analyze_run
from stateeye.report import build_report
from stateeye.testgen import generate_tests


def main():
    parser = argparse.ArgumentParser(description="StateEye GUI crawl runner")
    parser.add_argument("--mode", default="hybrid", help="Crawl mode")
    parser.add_argument("--target", required=True, help="URL or local file path")
    parser.add_argument("--runtime-mins", type=int, default=1)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-states", type=int, default=40)
    parser.add_argument("--output-dir", required=True, help="Directory for output")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--credentials", default=None, help="Path to credentials.txt")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = CrawlConfig(
        url=args.target,
        max_depth=int(args.max_depth),
        max_states=int(args.max_states),
        headless=False,
        output_dir=out_dir.parent,
        run_name=out_dir.name,
        mode=args.mode,
        credentials_file=args.credentials,
        max_runtime_s=int(args.runtime_mins) * 60,
    )

    sim_cfg = SimilarityConfig()
    crawler = StateEyeCrawler(cfg, sim_cfg)

    run_id = None
    db = None
    exit_status = "EXHAUSTED"
    states_data = {}

    try:
        run_id, db = crawler.crawl()

        summary = analyze_run(db, run_id, sim_cfg)

        # Generate report and tests
        report_path = out_dir / "report.html"
        build_report(db, run_id, summary, report_path, ReportConfig())
        generate_tests(db, run_id, out_dir / "generated_tests.py")

        for s in db.fetch_states(run_id):
            states_data[str(s["id"])] = {
                "url": s["url"],
                "depth": s["depth"],
            }
    except Exception as exc:
        exit_status = "ERROR"
        print(f"[error] Crawl failed: {exc}", flush=True)
        traceback.print_exc()

    # Always write result.json so the GUI can show something
    result = {
        "exitStatus": exit_status,
        "states": states_data,
        "edges": [],
        "statistics": {
            "stateStats": {
                "totalNumberOfStates": len(states_data),
            }
        },
    }
    result_path = out_dir / "result.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if db:
        db.close()
    print(f"Crawl complete. Output: {out_dir}")


if __name__ == "__main__":
    main()
