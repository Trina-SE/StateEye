"""
Command line interface for StateEye.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze_run
from .config import CrawlConfig, ReportConfig, SimilarityConfig
from .crawler import StateEyeCrawler
from .report import build_report
from .storage import StateEyeDB
from .testgen import generate_tests


def _add_crawl_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", required=True, help="Root URL to crawl")
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-states", type=int, default=40)
    parser.add_argument("--headless", action="store_true", default=False)
    parser.add_argument("--run-name", help="Optional name for the run folder")
    parser.add_argument(
        "--preactions",
        help="Path to a JSON file with a list of pre-actions (fill/click/submit) to run before crawling.",
    )
    parser.add_argument(
        "--disable-autofill",
        action="store_true",
        help="Disable automatic form filling heuristics.",
    )


def handle_crawl(args: argparse.Namespace) -> None:
    pre_actions = []
    if args.preactions:
        pre_actions = json.loads(Path(args.preactions).read_text(encoding="utf-8"))
    cfg = CrawlConfig(
        url=args.url,
        max_depth=args.max_depth,
        max_states=args.max_states,
        headless=args.headless,
        run_name=args.run_name,
        pre_actions=pre_actions,
        auto_fill_forms=not args.disable_autofill,
    )
    sim_cfg = SimilarityConfig()
    crawler = StateEyeCrawler(cfg, sim_cfg)
    run_id, db = crawler.crawl()
    summary = analyze_run(db, run_id, sim_cfg)
    report_path = cfg.run_folder() / "report.html"
    build_report(db, run_id, summary, report_path, ReportConfig())
    generate_tests(db, run_id, summary, report_path.parent / "generated_tests.py")
    db.close()
    print(f"Run stored in: {cfg.run_folder()}")
    print(f"Report: {report_path}")


def handle_analyze(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir)
    db = StateEyeDB(run_dir / "stateeye.db")
    run_id = db.latest_run_id()
    if run_id is None:
        raise SystemExit("No runs found in the specified directory.")
    run = db.fetch_run(run_id)
    cfg = CrawlConfig(url=run["url"])
    sim_cfg = SimilarityConfig()
    summary = analyze_run(db, run_id, sim_cfg)
    report_path = run_dir / "report.html"
    build_report(db, run_id, summary, report_path, ReportConfig())
    if args.generate_tests:
        generate_tests(db, run_id, summary, run_dir / "generated_tests.py")
    db.close()
    print(f"Report written to {report_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StateEye: Fragment-aware web regression testing")
    sub = parser.add_subparsers(dest="command", required=True)

    crawl = sub.add_parser("crawl", help="Crawl a site and generate a report")
    _add_crawl_options(crawl)
    crawl.set_defaults(func=handle_crawl)

    analyze = sub.add_parser("analyze", help="Analyze an existing run folder")
    analyze.add_argument("--run-dir", required=True, help="Path to a previous run directory")
    analyze.add_argument("--generate-tests", action="store_true", help="Regenerate tests")
    analyze.set_defaults(func=handle_analyze)

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
