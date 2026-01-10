"""
Configuration models for StateEye.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import datetime
from urllib.parse import urlparse


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


@dataclass
class CrawlConfig:
    """
    Options that control the crawling and state extraction process.
    """

    url: str
    output_dir: Path = Path("stateeye_runs")
    max_depth: int = 3
    max_states: int = 40
    headless: bool = True
    wait_after_action_ms: int = 800
    wait_on_load_ms: int = 1200
    action_timeout_ms: int = 4000
    viewport_width: int = 1400
    viewport_height: int = 900
    fragment_min_area: int = 4000
    fragment_limit: int = 32
    allowed_actions: List[str] = field(default_factory=lambda: ["click", "fill", "submit"])
    disallowed_domains: List[str] = field(default_factory=list)
    run_name: Optional[str] = None
    pre_actions: List[dict] = field(default_factory=list)
    auto_fill_forms: bool = True

    def run_folder(self) -> Path:
        if self.run_name:
            name = self.run_name
        else:
            parsed = urlparse(self.url)
            host = parsed.netloc or parsed.path or "site"
            safe_host = host.replace(":", "_").replace("/", "_")
            name = f"{safe_host}-output-{_timestamp()}"
        return Path(self.output_dir) / name


@dataclass
class SimilarityConfig:
    """
    Thresholds for clone and near-duplicate classification.
    """

    dom_clone_threshold: float = 0.97
    dom_near_duplicate_threshold: float = 0.9
    visual_clone_threshold: int = 2  # Hamming distance for perceptual hash
    visual_near_duplicate_threshold: int = 6
    combined_near_duplicate_score: float = 0.6


@dataclass
class ReportConfig:
    """
    Report generation options.
    """

    include_fragments: bool = True
    include_actions: bool = True
    title: str = "StateEye Report"
