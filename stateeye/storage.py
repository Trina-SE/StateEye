"""
Lightweight SQLite storage used by StateEye.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class ActionRecord:
    name: str
    selector: str
    action_type: str
    value: Optional[str]
    description: str


@dataclass
class StateRecord:
    url: str
    title: str
    dom_path: str
    screenshot_path: str
    dom_hash: str
    screenshot_hash: str
    depth: int
    path: List[ActionRecord]
    metadata: Dict
    is_terminal: bool = False


@dataclass
class FragmentRecord:
    state_id: int
    xpath: str
    tag: str
    snippet: str
    screenshot_path: Optional[str]
    bbox: Dict
    hash: str


@dataclass
class ComparisonRecord:
    state_a: int
    state_b: int
    dom_score: float
    visual_distance: int
    combined_score: float
    is_clone: bool
    is_near_duplicate: bool


class StateEyeDB:
    """
    Wrapper around SQLite for storing runs, states, fragments, and comparisons.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS runs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT,
                created_at TEXT,
                config_json TEXT
            );
            CREATE TABLE IF NOT EXISTS states(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                url TEXT,
                title TEXT,
                dom_path TEXT,
                screenshot_path TEXT,
                dom_hash TEXT,
                screenshot_hash TEXT,
                depth INTEGER,
                path_json TEXT,
                metadata_json TEXT,
                is_terminal INTEGER DEFAULT 0,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            CREATE TABLE IF NOT EXISTS fragments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_id INTEGER,
                xpath TEXT,
                tag TEXT,
                snippet TEXT,
                screenshot_path TEXT,
                bbox_json TEXT,
                hash TEXT,
                FOREIGN KEY(state_id) REFERENCES states(id)
            );
            CREATE TABLE IF NOT EXISTS comparisons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                state_a INTEGER,
                state_b INTEGER,
                dom_score REAL,
                visual_distance INTEGER,
                combined_score REAL,
                is_clone INTEGER,
                is_near_duplicate INTEGER,
                FOREIGN KEY(run_id) REFERENCES runs(id)
            );
            """
        )
        self.conn.commit()

    def create_run(self, name: str, url: str, created_at: str, config: Dict) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO runs(name, url, created_at, config_json) VALUES (?, ?, ?, ?)",
            (name, url, created_at, json.dumps(config, default=str)),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def insert_state(self, run_id: int, state: StateRecord) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO states(
                run_id, url, title, dom_path, screenshot_path, dom_hash, screenshot_hash,
                depth, path_json, metadata_json, is_terminal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                state.url,
                state.title,
                state.dom_path,
                state.screenshot_path,
                state.dom_hash,
                state.screenshot_hash,
                state.depth,
                json.dumps([asdict(a) for a in state.path]),
                json.dumps(state.metadata),
                int(state.is_terminal),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def insert_fragments(self, fragments: Iterable[FragmentRecord]) -> None:
        cur = self.conn.cursor()
        rows = [
            (
                f.state_id,
                f.xpath,
                f.tag,
                f.snippet,
                f.screenshot_path,
                json.dumps(f.bbox),
                f.hash,
            )
            for f in fragments
        ]
        cur.executemany(
            """
            INSERT INTO fragments(state_id, xpath, tag, snippet, screenshot_path, bbox_json, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def insert_comparison(self, run_id: int, comp: ComparisonRecord) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO comparisons(
                run_id, state_a, state_b, dom_score, visual_distance,
                combined_score, is_clone, is_near_duplicate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                comp.state_a,
                comp.state_b,
                comp.dom_score,
                comp.visual_distance,
                comp.combined_score,
                int(comp.is_clone),
                int(comp.is_near_duplicate),
            ),
        )
        self.conn.commit()

    def fetch_states(self, run_id: int) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM states WHERE run_id = ? ORDER BY id ASC", (run_id,)
        )
        return cur.fetchall()

    def fetch_state(self, state_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM states WHERE id = ?", (state_id,))
        return cur.fetchone()

    def fetch_run(self, run_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
        return cur.fetchone()

    def latest_run_id(self) -> Optional[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        return int(row["id"]) if row else None

    def fetch_fragments(self, state_ids: List[int]) -> Dict[int, List[sqlite3.Row]]:
        placeholders = ",".join("?" for _ in state_ids)
        cur = self.conn.cursor()
        cur.execute(
            f"SELECT * FROM fragments WHERE state_id IN ({placeholders})",
            state_ids,
        )
        mapping: Dict[int, List[sqlite3.Row]] = {}
        for row in cur.fetchall():
            mapping.setdefault(row["state_id"], []).append(row)
        return mapping

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
