"""SQLite-backed persistence for students and their progress.

Uses only the standard library (`sqlite3`) so there's nothing to install or run.
The student profile is stored as a JSON blob and completed milestones as a JSON
array -- the exact shape that ports to a Postgres `JSONB` column later without
changing the engine or API.

A single ProfileStore instance owns one connection. Pass a path (or ":memory:"
for tests). All engine recomputation stays in the engine modules; this file is
storage only.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Optional

from app.models import StudentProfile

_SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id            TEXT PRIMARY KEY,
    profile_json  TEXT NOT NULL,
    milestones_json TEXT NOT NULL DEFAULT '[]',
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS progress_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    kind       TEXT NOT NULL,          -- 'skill' | 'milestone'
    ref        TEXT NOT NULL,          -- skill_id or milestone_id
    value      TEXT,                   -- new level, or 'done'/'undone'
    at         TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (student_id) REFERENCES students(id)
);
"""


class StudentNotFound(Exception):
    pass


class ProfileStore:
    def __init__(self, path: str = ":memory:") -> None:
        # check_same_thread=False keeps it usable from FastAPI's threadpool;
        # access here is simple and serialized enough for this milestone.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ----- students -------------------------------------------------------
    def create_student(self, profile: StudentProfile) -> str:
        sid = str(uuid.uuid4())
        self._conn.execute(
            "INSERT INTO students (id, profile_json) VALUES (?, ?)",
            (sid, profile.model_dump_json()),
        )
        self._conn.commit()
        return sid

    def _row(self, student_id: str) -> sqlite3.Row:
        row = self._conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        if row is None:
            raise StudentNotFound(student_id)
        return row

    def get_profile(self, student_id: str) -> StudentProfile:
        return StudentProfile.model_validate_json(self._row(student_id)["profile_json"])

    def get_completed_milestones(self, student_id: str) -> set[str]:
        return set(json.loads(self._row(student_id)["milestones_json"]))

    def _save_profile(self, student_id: str, profile: StudentProfile) -> None:
        self._conn.execute(
            "UPDATE students SET profile_json = ?, updated_at = datetime('now') "
            "WHERE id = ?",
            (profile.model_dump_json(), student_id),
        )
        self._conn.commit()

    # ----- progress -------------------------------------------------------
    def set_skill_level(self, student_id: str, skill_id: str, level: int) -> StudentProfile:
        """Update one self-rated skill level and persist. Returns new profile."""
        level = max(0, min(5, int(level)))
        profile = self.get_profile(student_id)
        profile.skills.levels[skill_id] = level
        self._save_profile(student_id, profile)
        self._log(student_id, "skill", skill_id, str(level))
        return profile

    def set_milestone(self, student_id: str, milestone_id: str, done: bool) -> set[str]:
        """Toggle a milestone's completion and persist. Returns completed set."""
        completed = self.get_completed_milestones(student_id)
        if done:
            completed.add(milestone_id)
        else:
            completed.discard(milestone_id)
        self._conn.execute(
            "UPDATE students SET milestones_json = ?, updated_at = datetime('now') "
            "WHERE id = ?",
            (json.dumps(sorted(completed)), student_id),
        )
        self._conn.commit()
        self._log(student_id, "milestone", milestone_id, "done" if done else "undone")
        return completed

    def advance_semester(self, student_id: str) -> StudentProfile:
        """Move the student to the next semester (capped at 8) and persist."""
        profile = self.get_profile(student_id)
        profile.academic.current_semester = min(8, profile.academic.current_semester + 1)
        self._save_profile(student_id, profile)
        self._log(student_id, "semester", "current", str(profile.academic.current_semester))
        return profile

    def _log(self, student_id: str, kind: str, ref: str, value: Optional[str]) -> None:
        self._conn.execute(
            "INSERT INTO progress_log (student_id, kind, ref, value) VALUES (?,?,?,?)",
            (student_id, kind, ref, value),
        )
        self._conn.commit()

    def progress_history(self, student_id: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT kind, ref, value, at FROM progress_log WHERE student_id = ? "
            "ORDER BY id",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self._conn.close()
