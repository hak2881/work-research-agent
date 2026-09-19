from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


VERIFICATION_LEVELS = {
    "slack",
    "official-docs",
    "admin",
    "code",
    "execution",
    "production",
}
CONFIDENCE_LEVELS = {"explicit", "verified", "inferred", "unresolved"}
WORK_ITEM_STATES = {
    "planned",
    "ready",
    "in_progress",
    "verification_pending",
    "completed",
    "blocked",
    "cancelled",
    "superseded",
}
WORK_ITEM_ORIGINS = {"explicit", "proposed"}
ESTIMATE_BASES = {"source", "engineering"}
ACCEPTANCE_STATUSES = {"proposed", "accepted", "rejected", "verified"}
WBS_ITEM_TYPES = {"task", "milestone"}
WBS_STATUSES = {"예정", "진행 중", "확인 대기", "완료", "보류"}
SCHEDULE_BASES = {"confirmed", "planned", "proposed", "unknown"}
POLICY_STATES = {"agreed", "no_confirmed_policy", "not_applicable"}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def normalize_remote_url(value: str) -> str:
    remote = value.strip()
    if remote.startswith("git@") and ":" in remote:
        host_path = remote[4:]
        host, path = host_path.split(":", 1)
        remote = f"https://{host}/{path}"
    elif remote.startswith("ssh://git@"):
        parsed = urlparse(remote)
        remote = f"https://{parsed.hostname or ''}{parsed.path}"
    if remote.endswith(".git"):
        remote = remote[:-4]
    return remote.rstrip("/").lower()


class HistoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def close(self) -> None:
        self.connection.close()

    def _initialize(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                customer TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                source_type TEXT NOT NULL,
                source_uri TEXT NOT NULL,
                title TEXT NOT NULL,
                claim TEXT NOT NULL,
                excerpt TEXT NOT NULL DEFAULT '',
                verification_level TEXT NOT NULL,
                confidence TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                UNIQUE(project_id, source_uri, claim)
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(
                evidence_id UNINDEXED,
                title,
                claim,
                excerpt
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                external_key TEXT NOT NULL,
                title TEXT NOT NULL,
                state TEXT NOT NULL,
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(project_id, external_key)
            );

            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                remote_url TEXT NOT NULL,
                normalized_remote TEXT NOT NULL,
                local_path TEXT NOT NULL,
                default_branch TEXT,
                head_sha TEXT,
                synced_at TEXT NOT NULL,
                access_state TEXT NOT NULL,
                UNIQUE(project_id, normalized_remote)
            );

            CREATE TABLE IF NOT EXISTS commits (
                id INTEGER PRIMARY KEY,
                repository_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                sha TEXT NOT NULL,
                author_name TEXT,
                authored_at TEXT,
                subject TEXT NOT NULL,
                UNIQUE(repository_id, sha)
            );

            CREATE TABLE IF NOT EXISTS commit_files (
                repository_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
                commit_sha TEXT NOT NULL,
                path TEXT NOT NULL,
                status TEXT NOT NULL,
                PRIMARY KEY(repository_id, commit_sha, path)
            );

            CREATE TABLE IF NOT EXISTS source_links (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                from_type TEXT NOT NULL,
                from_key TEXT NOT NULL,
                to_type TEXT NOT NULL,
                to_key TEXT NOT NULL,
                confidence TEXT NOT NULL,
                evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL,
                UNIQUE(project_id, from_type, from_key, to_type, to_key)
            );

            CREATE TABLE IF NOT EXISTS project_documents (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                external_key TEXT NOT NULL,
                source_uri TEXT NOT NULL,
                document_type TEXT NOT NULL,
                title TEXT NOT NULL,
                version TEXT,
                content_hash TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                UNIQUE(project_id, external_key)
            );

            CREATE TABLE IF NOT EXISTS work_items (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                external_key TEXT NOT NULL,
                parent_key TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                state TEXT NOT NULL,
                workstream TEXT,
                priority TEXT,
                estimate_min REAL,
                estimate_max REAL,
                estimate_unit TEXT,
                estimate_confidence TEXT,
                origin TEXT NOT NULL,
                estimate_basis TEXT,
                acceptance_criteria TEXT NOT NULL DEFAULT '[]',
                assumptions TEXT NOT NULL DEFAULT '[]',
                exclusions TEXT NOT NULL DEFAULT '[]',
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(project_id, external_key)
            );

            CREATE TABLE IF NOT EXISTS work_item_dependencies (
                work_item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
                dependency_item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                PRIMARY KEY(work_item_id, dependency_item_id)
            );

            CREATE TABLE IF NOT EXISTS work_item_events (
                id INTEGER PRIMARY KEY,
                work_item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                note TEXT NOT NULL,
                from_state TEXT,
                to_state TEXT,
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                repository_sha TEXT,
                occurred_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS work_item_estimates (
                id INTEGER PRIMARY KEY,
                work_item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
                estimate_key TEXT NOT NULL,
                basis TEXT NOT NULL,
                estimate_min REAL NOT NULL,
                estimate_max REAL NOT NULL,
                unit TEXT NOT NULL,
                confidence TEXT NOT NULL,
                assumptions TEXT NOT NULL DEFAULT '[]',
                exclusions TEXT NOT NULL DEFAULT '[]',
                dependencies TEXT NOT NULL DEFAULT '[]',
                workstreams TEXT NOT NULL DEFAULT '[]',
                repository_sha TEXT,
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                recorded_at TEXT NOT NULL,
                UNIQUE(work_item_id, estimate_key)
            );

            CREATE TABLE IF NOT EXISTS work_item_acceptance_criteria (
                id INTEGER PRIMARY KEY,
                work_item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
                criterion_key TEXT NOT NULL,
                criterion TEXT NOT NULL,
                origin TEXT NOT NULL,
                status TEXT NOT NULL,
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(work_item_id, criterion_key)
            );

            CREATE TABLE IF NOT EXISTS work_item_schedule_snapshots (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                wbs_document_key TEXT NOT NULL,
                work_item_key TEXT NOT NULL,
                display_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                owner TEXT,
                collaborators_json TEXT NOT NULL DEFAULT '[]',
                wbs_status TEXT NOT NULL,
                schedule_basis TEXT NOT NULL,
                baseline_start TEXT,
                baseline_end TEXT,
                forecast_start TEXT,
                forecast_end TEXT,
                actual_start TEXT,
                actual_end TEXT,
                selected_estimate_key TEXT,
                actual_effort REAL,
                actual_effort_unit TEXT,
                change_note TEXT,
                source_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                captured_at TEXT NOT NULL,
                UNIQUE(project_id, wbs_document_key, work_item_key),
                UNIQUE(project_id, wbs_document_key, display_id)
            );

            CREATE TABLE IF NOT EXISTS policy_document_snapshots (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                policy_document_key TEXT NOT NULL,
                policy_key TEXT NOT NULL,
                area TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                body_markdown TEXT NOT NULL,
                policy_state TEXT NOT NULL,
                effective_from TEXT,
                reviewed_at TEXT NOT NULL,
                authority_evidence_id INTEGER REFERENCES evidence(id) ON DELETE SET NULL,
                captured_at TEXT NOT NULL,
                UNIQUE(project_id, policy_document_key, policy_key)
            );

            CREATE TABLE IF NOT EXISTS architecture_snapshots (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                version TEXT NOT NULL,
                summary TEXT NOT NULL,
                diagram_mermaid TEXT NOT NULL,
                details_markdown TEXT NOT NULL,
                source_refs TEXT NOT NULL DEFAULT '[]',
                verification_status TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                UNIQUE(project_id, version)
            );
            """
        )
        self.connection.commit()

    def _project(self, slug: str) -> sqlite3.Row:
        row = self.connection.execute(
            "SELECT * FROM projects WHERE slug = ?", (slug,)
        ).fetchone()
        if row is None:
            raise ValueError(f"unknown project: {slug}")
        return row

    def upsert_project(
        self, slug: str, name: str, customer: str | None = None
    ) -> dict[str, Any]:
        timestamp = _now()
        self.connection.execute(
            """
            INSERT INTO projects(slug, name, customer, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                customer = excluded.customer,
                updated_at = excluded.updated_at
            """,
            (slug, name, customer, timestamp, timestamp),
        )
        self.connection.commit()
        return _row(self._project(slug)) or {}

    def find_projects(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        value = query.strip()
        if not value:
            return []
        pattern = f"%{value}%"
        rows = self.connection.execute(
            """
            SELECT p.*,
                   (SELECT COUNT(*) FROM evidence e WHERE e.project_id = p.id) AS evidence_count,
                   (SELECT MAX(e.captured_at) FROM evidence e WHERE e.project_id = p.id) AS latest_evidence_at,
                   (SELECT COUNT(*) FROM repositories r WHERE r.project_id = p.id) AS repository_count,
                   (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id) AS task_count
            FROM projects p
            WHERE p.slug LIKE ? COLLATE NOCASE
               OR p.name LIKE ? COLLATE NOCASE
               OR COALESCE(p.customer, '') LIKE ? COLLATE NOCASE
            ORDER BY
                CASE
                    WHEN p.slug = ? COLLATE NOCASE THEN 0
                    WHEN p.name = ? COLLATE NOCASE THEN 1
                    WHEN p.customer = ? COLLATE NOCASE THEN 2
                    ELSE 3
                END,
                p.updated_at DESC
            LIMIT ?
            """,
            (pattern, pattern, pattern, value, value, value, limit),
        ).fetchall()
        return [dict(row) for row in rows]

    def record_evidence(
        self,
        *,
        project_slug: str,
        source_type: str,
        source_uri: str,
        title: str,
        claim: str,
        verification_level: str,
        confidence: str,
        excerpt: str = "",
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        if verification_level not in VERIFICATION_LEVELS:
            raise ValueError(f"invalid verification_level: {verification_level}")
        if confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"invalid confidence: {confidence}")
        project = self._project(project_slug)
        captured = captured_at or _now()
        self.connection.execute(
            """
            INSERT INTO evidence(
                project_id, source_type, source_uri, title, claim, excerpt,
                verification_level, confidence, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, source_uri, claim) DO UPDATE SET
                source_type = excluded.source_type,
                title = excluded.title,
                excerpt = excluded.excerpt,
                verification_level = excluded.verification_level,
                confidence = excluded.confidence,
                captured_at = excluded.captured_at
            """,
            (
                project["id"],
                source_type,
                source_uri,
                title,
                claim,
                excerpt,
                verification_level,
                confidence,
                captured,
            ),
        )
        evidence = self.connection.execute(
            "SELECT * FROM evidence WHERE project_id = ? AND source_uri = ? AND claim = ?",
            (project["id"], source_uri, claim),
        ).fetchone()
        assert evidence is not None
        self.connection.execute(
            "DELETE FROM evidence_fts WHERE evidence_id = ?", (str(evidence["id"]),)
        )
        self.connection.execute(
            "INSERT INTO evidence_fts(evidence_id, title, claim, excerpt) VALUES (?, ?, ?, ?)",
            (str(evidence["id"]), title, claim, excerpt),
        )
        self.connection.commit()
        return _row(evidence) or {}

    def upsert_task(
        self,
        project_slug: str,
        external_key: str,
        title: str,
        state: str,
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        project = self._project(project_slug)
        self.connection.execute(
            """
            INSERT INTO tasks(project_id, external_key, title, state, source_evidence_id, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, external_key) DO UPDATE SET
                title = excluded.title,
                state = excluded.state,
                source_evidence_id = excluded.source_evidence_id,
                updated_at = excluded.updated_at
            """,
            (project["id"], external_key, title, state, source_evidence_id, _now()),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM tasks WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        return _row(row) or {}

    def record_document(
        self,
        project_slug: str,
        external_key: str,
        source_uri: str,
        document_type: str,
        title: str,
        *,
        version: str | None = None,
        content_hash: str,
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        project = self._project(project_slug)
        captured = captured_at or _now()
        self.connection.execute(
            """
            INSERT INTO project_documents(
                project_id, external_key, source_uri, document_type, title,
                version, content_hash, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, external_key) DO UPDATE SET
                source_uri = excluded.source_uri,
                document_type = excluded.document_type,
                title = excluded.title,
                version = excluded.version,
                content_hash = excluded.content_hash,
                captured_at = excluded.captured_at
            """,
            (
                project["id"],
                external_key,
                source_uri,
                document_type,
                title,
                version,
                content_hash,
                captured,
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM project_documents WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        return _row(row) or {}

    def upsert_work_item(
        self,
        project_slug: str,
        external_key: str,
        title: str,
        *,
        state: str,
        parent_key: str | None = None,
        description: str = "",
        workstream: str | None = None,
        priority: str | None = None,
        estimate_min: float | None = None,
        estimate_max: float | None = None,
        estimate_unit: str | None = None,
        estimate_confidence: str | None = None,
        origin: str = "explicit",
        estimate_basis: str | None = None,
        acceptance_criteria: Iterable[str] = (),
        assumptions: Iterable[str] = (),
        exclusions: Iterable[str] = (),
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        if state not in WORK_ITEM_STATES:
            raise ValueError(f"invalid work item state: {state}")
        if estimate_min is not None and estimate_max is not None and estimate_min > estimate_max:
            raise ValueError("estimate_min must not exceed estimate_max")
        if origin not in WORK_ITEM_ORIGINS:
            raise ValueError(f"invalid work item origin: {origin}")
        if estimate_basis is not None and estimate_basis not in ESTIMATE_BASES:
            raise ValueError(f"invalid estimate basis: {estimate_basis}")
        project = self._project(project_slug)
        previous = self.connection.execute(
            "SELECT * FROM work_items WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        timestamp = _now()
        self.connection.execute(
            """
            INSERT INTO work_items(
                project_id, external_key, parent_key, title, description, state,
                workstream, priority, estimate_min, estimate_max, estimate_unit,
                estimate_confidence, origin, estimate_basis, acceptance_criteria,
                assumptions, exclusions, source_evidence_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, external_key) DO UPDATE SET
                parent_key = excluded.parent_key,
                title = excluded.title,
                description = excluded.description,
                state = excluded.state,
                workstream = excluded.workstream,
                priority = excluded.priority,
                estimate_min = excluded.estimate_min,
                estimate_max = excluded.estimate_max,
                estimate_unit = excluded.estimate_unit,
                estimate_confidence = excluded.estimate_confidence,
                origin = excluded.origin,
                estimate_basis = excluded.estimate_basis,
                acceptance_criteria = excluded.acceptance_criteria,
                assumptions = excluded.assumptions,
                exclusions = excluded.exclusions,
                source_evidence_id = excluded.source_evidence_id,
                updated_at = excluded.updated_at
            """,
            (
                project["id"],
                external_key,
                parent_key,
                title,
                description,
                state,
                workstream,
                priority,
                estimate_min,
                estimate_max,
                estimate_unit,
                estimate_confidence,
                origin,
                estimate_basis,
                json.dumps(list(acceptance_criteria), ensure_ascii=False),
                json.dumps(list(assumptions), ensure_ascii=False),
                json.dumps(list(exclusions), ensure_ascii=False),
                source_evidence_id,
                timestamp,
                timestamp,
            ),
        )
        row = self.connection.execute(
            "SELECT * FROM work_items WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        assert row is not None
        if previous is None or previous["state"] != state:
            self.connection.execute(
                """
                INSERT INTO work_item_events(
                    work_item_id, event_type, note, from_state, to_state,
                    source_evidence_id, repository_sha, occurred_at
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?)
                """,
                (
                    row["id"],
                    "created" if previous is None else "state_changed",
                    "Work item created" if previous is None else "Work item state updated",
                    previous["state"] if previous is not None else None,
                    state,
                    source_evidence_id,
                    timestamp,
                ),
            )
        self.connection.commit()
        return self._work_item_dict(row)

    def record_work_item_event(
        self,
        project_slug: str,
        external_key: str,
        event_type: str,
        note: str,
        *,
        state: str | None = None,
        source_evidence_id: int | None = None,
        repository_sha: str | None = None,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        if state is not None and state not in WORK_ITEM_STATES:
            raise ValueError(f"invalid work item state: {state}")
        project = self._project(project_slug)
        item = self.connection.execute(
            "SELECT * FROM work_items WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        if item is None:
            raise ValueError(f"unknown work item: {external_key}")
        timestamp = occurred_at or _now()
        target_state = state or item["state"]
        self.connection.execute(
            """
            INSERT INTO work_item_events(
                work_item_id, event_type, note, from_state, to_state,
                source_evidence_id, repository_sha, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["id"],
                event_type,
                note,
                item["state"],
                target_state,
                source_evidence_id,
                repository_sha,
                timestamp,
            ),
        )
        if state is not None:
            self.connection.execute(
                "UPDATE work_items SET state = ?, updated_at = ? WHERE id = ?",
                (state, timestamp, item["id"]),
            )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM work_item_events WHERE work_item_id = ? ORDER BY id DESC LIMIT 1",
            (item["id"],),
        ).fetchone()
        return _row(row) or {}

    def record_work_item_estimate(
        self,
        project_slug: str,
        external_key: str,
        estimate_key: str,
        basis: str,
        estimate_min: float,
        estimate_max: float,
        unit: str,
        *,
        confidence: str,
        assumptions: Iterable[str] = (),
        exclusions: Iterable[str] = (),
        dependencies: Iterable[str] = (),
        workstreams: Iterable[str] = (),
        repository_sha: str | None = None,
        source_evidence_id: int | None = None,
        recorded_at: str | None = None,
    ) -> dict[str, Any]:
        if basis not in ESTIMATE_BASES:
            raise ValueError(f"invalid estimate basis: {basis}")
        if estimate_min > estimate_max:
            raise ValueError("estimate_min must not exceed estimate_max")
        item = self._resolve_work_item(project_slug, external_key)
        self.connection.execute(
            """
            INSERT INTO work_item_estimates(
                work_item_id, estimate_key, basis, estimate_min, estimate_max,
                unit, confidence, assumptions, exclusions, dependencies,
                workstreams, repository_sha, source_evidence_id, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(work_item_id, estimate_key) DO UPDATE SET
                basis = excluded.basis,
                estimate_min = excluded.estimate_min,
                estimate_max = excluded.estimate_max,
                unit = excluded.unit,
                confidence = excluded.confidence,
                assumptions = excluded.assumptions,
                exclusions = excluded.exclusions,
                dependencies = excluded.dependencies,
                workstreams = excluded.workstreams,
                repository_sha = excluded.repository_sha,
                source_evidence_id = excluded.source_evidence_id,
                recorded_at = excluded.recorded_at
            """,
            (
                item["id"],
                estimate_key,
                basis,
                estimate_min,
                estimate_max,
                unit,
                confidence,
                json.dumps(list(assumptions), ensure_ascii=False),
                json.dumps(list(exclusions), ensure_ascii=False),
                json.dumps(list(dependencies), ensure_ascii=False),
                json.dumps(list(workstreams), ensure_ascii=False),
                repository_sha,
                source_evidence_id,
                recorded_at or _now(),
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM work_item_estimates WHERE work_item_id = ? AND estimate_key = ?",
            (item["id"], estimate_key),
        ).fetchone()
        result = _row(row) or {}
        for field in ("assumptions", "exclusions", "dependencies", "workstreams"):
            result[field] = json.loads(result.get(field, "[]"))
        return result

    def upsert_acceptance_criterion(
        self,
        project_slug: str,
        external_key: str,
        criterion_key: str,
        criterion: str,
        *,
        origin: str,
        status: str,
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        if origin not in WORK_ITEM_ORIGINS:
            raise ValueError(f"invalid acceptance criterion origin: {origin}")
        if status not in ACCEPTANCE_STATUSES:
            raise ValueError(f"invalid acceptance criterion status: {status}")
        item = self._resolve_work_item(project_slug, external_key)
        self.connection.execute(
            """
            INSERT INTO work_item_acceptance_criteria(
                work_item_id, criterion_key, criterion, origin, status,
                source_evidence_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(work_item_id, criterion_key) DO UPDATE SET
                criterion = excluded.criterion,
                origin = excluded.origin,
                status = excluded.status,
                source_evidence_id = excluded.source_evidence_id,
                updated_at = excluded.updated_at
            """,
            (
                item["id"],
                criterion_key,
                criterion,
                origin,
                status,
                source_evidence_id,
                _now(),
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            """
            SELECT * FROM work_item_acceptance_criteria
            WHERE work_item_id = ? AND criterion_key = ?
            """,
            (item["id"], criterion_key),
        ).fetchone()
        return _row(row) or {}

    def link_work_item_dependency(
        self, project_slug: str, work_item_key: str, dependency_key: str
    ) -> dict[str, Any]:
        if work_item_key == dependency_key:
            raise ValueError("a work item cannot depend on itself")
        project = self._project(project_slug)
        rows = self.connection.execute(
            "SELECT id, external_key FROM work_items WHERE project_id = ? AND external_key IN (?, ?)",
            (project["id"], work_item_key, dependency_key),
        ).fetchall()
        by_key = {row["external_key"]: row["id"] for row in rows}
        missing = {work_item_key, dependency_key} - set(by_key)
        if missing:
            raise ValueError(f"unknown work item: {sorted(missing)[0]}")
        self.connection.execute(
            """
            INSERT INTO work_item_dependencies(work_item_id, dependency_item_id, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(work_item_id, dependency_item_id) DO NOTHING
            """,
            (by_key[work_item_key], by_key[dependency_key], _now()),
        )
        self.connection.commit()
        return {"work_item_key": work_item_key, "dependency_key": dependency_key}

    def record_wbs_schedule_snapshot(
        self,
        project_slug: str,
        wbs_document_key: str,
        rows: list[dict[str, Any]],
        *,
        captured_at: str | None = None,
    ) -> list[dict[str, Any]]:
        if not rows:
            raise ValueError("WBS schedule snapshot requires at least one row")
        project = self._project(project_slug)
        document = self.connection.execute(
            """
            SELECT id, document_type FROM project_documents
            WHERE project_id = ? AND external_key = ?
            """,
            (project["id"], wbs_document_key),
        ).fetchone()
        if document is None:
            raise ValueError(f"unknown WBS document: {wbs_document_key}")
        if document["document_type"] != "wbs":
            raise ValueError(f"document is not a WBS: {wbs_document_key}")
        existing = self.connection.execute(
            """
            SELECT 1 FROM work_item_schedule_snapshots
            WHERE project_id = ? AND wbs_document_key = ? LIMIT 1
            """,
            (project["id"], wbs_document_key),
        ).fetchone()
        if existing is not None:
            raise ValueError(f"WBS document already has schedule rows: {wbs_document_key}")

        work_item_keys = [str(row.get("work_item_key", "")) for row in rows]
        display_ids = [str(row.get("display_id", "")) for row in rows]
        if len(set(work_item_keys)) != len(work_item_keys):
            raise ValueError("duplicate work item key in WBS schedule snapshot")
        if len(set(display_ids)) != len(display_ids):
            raise ValueError("duplicate display ID in WBS schedule snapshot")

        validated: list[dict[str, Any]] = []
        for row in rows:
            work_item_key = str(row.get("work_item_key", "")).strip()
            display_id = str(row.get("display_id", "")).strip()
            item_type = str(row.get("item_type", ""))
            wbs_status = str(row.get("wbs_status", ""))
            schedule_basis = str(row.get("schedule_basis", ""))
            if not work_item_key or not display_id:
                raise ValueError("work item key and display ID are required")
            if item_type not in WBS_ITEM_TYPES:
                raise ValueError(f"invalid WBS item type: {item_type}")
            if wbs_status not in WBS_STATUSES:
                raise ValueError(f"invalid WBS status: {wbs_status}")
            if schedule_basis not in SCHEDULE_BASES:
                raise ValueError(f"invalid schedule basis: {schedule_basis}")
            item = self.connection.execute(
                "SELECT id FROM work_items WHERE project_id = ? AND external_key = ?",
                (project["id"], work_item_key),
            ).fetchone()
            if item is None:
                raise ValueError(f"unknown work item: {work_item_key}")
            selected_estimate_key = row.get("selected_estimate_key")
            if selected_estimate_key is not None:
                estimate = self.connection.execute(
                    """
                    SELECT 1 FROM work_item_estimates
                    WHERE work_item_id = ? AND estimate_key = ?
                    """,
                    (item["id"], selected_estimate_key),
                ).fetchone()
                if estimate is None:
                    raise ValueError(
                        f"unknown estimate for {work_item_key}: {selected_estimate_key}"
                    )
            actual_effort = row.get("actual_effort")
            actual_effort_unit = row.get("actual_effort_unit")
            if (actual_effort is None) != (actual_effort_unit is None):
                raise ValueError("actual effort and unit must be supplied together")
            validated.append(
                {
                    **row,
                    "work_item_key": work_item_key,
                    "display_id": display_id,
                    "item_type": item_type,
                    "wbs_status": wbs_status,
                    "schedule_basis": schedule_basis,
                    "collaborators": list(row.get("collaborators") or []),
                }
            )

        timestamp = captured_at or _now()
        with self.connection:
            for row in validated:
                self.connection.execute(
                    """
                    INSERT INTO work_item_schedule_snapshots(
                        project_id, wbs_document_key, work_item_key, display_id,
                        item_type, owner, collaborators_json, wbs_status,
                        schedule_basis, baseline_start, baseline_end,
                        forecast_start, forecast_end, actual_start, actual_end,
                        selected_estimate_key, actual_effort, actual_effort_unit,
                        change_note, source_evidence_id, captured_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project["id"],
                        wbs_document_key,
                        row["work_item_key"],
                        row["display_id"],
                        row["item_type"],
                        row.get("owner"),
                        json.dumps(row["collaborators"], ensure_ascii=False),
                        row["wbs_status"],
                        row["schedule_basis"],
                        row.get("baseline_start"),
                        row.get("baseline_end"),
                        row.get("forecast_start"),
                        row.get("forecast_end"),
                        row.get("actual_start"),
                        row.get("actual_end"),
                        row.get("selected_estimate_key"),
                        row.get("actual_effort"),
                        row.get("actual_effort_unit"),
                        row.get("change_note"),
                        row.get("source_evidence_id"),
                        timestamp,
                    ),
                )
        stored = self.connection.execute(
            """
            SELECT * FROM work_item_schedule_snapshots
            WHERE project_id = ? AND wbs_document_key = ? ORDER BY display_id
            """,
            (project["id"], wbs_document_key),
        ).fetchall()
        return [self._wbs_schedule_dict(row) for row in stored]

    def record_policy_snapshot(
        self,
        project_slug: str,
        policy_document_key: str,
        rows: list[dict[str, Any]],
        *,
        captured_at: str | None = None,
    ) -> list[dict[str, Any]]:
        if not rows:
            raise ValueError("policy snapshot requires at least one row")
        project = self._project(project_slug)
        document = self.connection.execute(
            """
            SELECT id, document_type FROM project_documents
            WHERE project_id = ? AND external_key = ?
            """,
            (project["id"], policy_document_key),
        ).fetchone()
        if document is None:
            raise ValueError(f"unknown policy document: {policy_document_key}")
        if document["document_type"] != "policy":
            raise ValueError(f"document is not a policy: {policy_document_key}")
        existing = self.connection.execute(
            """
            SELECT 1 FROM policy_document_snapshots
            WHERE project_id = ? AND policy_document_key = ? LIMIT 1
            """,
            (project["id"], policy_document_key),
        ).fetchone()
        if existing is not None:
            raise ValueError(f"policy document already has policy rows: {policy_document_key}")

        keys = [str(row.get("policy_key", "")).strip() for row in rows]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate policy key in policy snapshot")

        validated: list[dict[str, Any]] = []
        for row in rows:
            policy_key = str(row.get("policy_key", "")).strip()
            area = str(row.get("area", "")).strip()
            title = str(row.get("title", "")).strip()
            body = str(row.get("body_markdown", "")).strip()
            state = str(row.get("policy_state", "")).strip()
            reviewed_at = str(row.get("reviewed_at", "")).strip()
            evidence_id = row.get("authority_evidence_id")
            if not policy_key or not area or not body or not reviewed_at:
                raise ValueError("policy key, area, body, and review date are required")
            if state not in POLICY_STATES:
                raise ValueError(f"invalid policy state: {state}")
            if state == "agreed" and not title:
                raise ValueError("agreed policy requires a title")
            if state in {"agreed", "not_applicable"} and evidence_id is None:
                raise ValueError(f"{state} policy requires authoritative evidence")
            if evidence_id is not None:
                evidence = self.connection.execute(
                    "SELECT 1 FROM evidence WHERE id = ? AND project_id = ?",
                    (evidence_id, project["id"]),
                ).fetchone()
                if evidence is None:
                    raise ValueError(f"unknown authoritative evidence: {evidence_id}")
            validated.append(
                {
                    **row,
                    "policy_key": policy_key,
                    "area": area,
                    "title": title,
                    "body_markdown": body,
                    "policy_state": state,
                    "reviewed_at": reviewed_at,
                }
            )

        timestamp = captured_at or _now()
        with self.connection:
            for row in validated:
                self.connection.execute(
                    """
                    INSERT INTO policy_document_snapshots(
                        project_id, policy_document_key, policy_key, area, title,
                        body_markdown, policy_state, effective_from, reviewed_at,
                        authority_evidence_id, captured_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project["id"],
                        policy_document_key,
                        row["policy_key"],
                        row["area"],
                        row["title"],
                        row["body_markdown"],
                        row["policy_state"],
                        row.get("effective_from"),
                        row["reviewed_at"],
                        row.get("authority_evidence_id"),
                        timestamp,
                    ),
                )
        stored = self.connection.execute(
            """
            SELECT * FROM policy_document_snapshots
            WHERE project_id = ? AND policy_document_key = ? ORDER BY area, policy_key
            """,
            (project["id"], policy_document_key),
        ).fetchall()
        return [dict(row) for row in stored]

    def record_architecture_snapshot(
        self,
        project_slug: str,
        version: str,
        summary: str,
        diagram_mermaid: str,
        details_markdown: str,
        *,
        source_refs: Iterable[str] = (),
        verification_status: str,
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        project = self._project(project_slug)
        captured = captured_at or _now()
        self.connection.execute(
            """
            INSERT INTO architecture_snapshots(
                project_id, version, summary, diagram_mermaid, details_markdown,
                source_refs, verification_status, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, version) DO UPDATE SET
                summary = excluded.summary,
                diagram_mermaid = excluded.diagram_mermaid,
                details_markdown = excluded.details_markdown,
                source_refs = excluded.source_refs,
                verification_status = excluded.verification_status,
                captured_at = excluded.captured_at
            """,
            (
                project["id"],
                version,
                summary,
                diagram_mermaid,
                details_markdown,
                json.dumps(list(source_refs), ensure_ascii=False),
                verification_status,
                captured,
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM architecture_snapshots WHERE project_id = ? AND version = ?",
            (project["id"], version),
        ).fetchone()
        result = _row(row) or {}
        result["source_refs"] = json.loads(result.get("source_refs", "[]"))
        return result

    @staticmethod
    def _work_item_dict(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        for field in ("acceptance_criteria", "assumptions", "exclusions"):
            result[field] = json.loads(result[field])
        return result

    def _resolve_work_item(self, project_slug: str, external_key: str) -> sqlite3.Row:
        project = self._project(project_slug)
        item = self.connection.execute(
            "SELECT * FROM work_items WHERE project_id = ? AND external_key = ?",
            (project["id"], external_key),
        ).fetchone()
        if item is None:
            raise ValueError(f"unknown work item: {external_key}")
        return item

    @staticmethod
    def _wbs_schedule_dict(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["collaborators"] = json.loads(item.pop("collaborators_json"))
        return item

    def register_repository(
        self,
        project_slug: str,
        remote_url: str,
        local_path: str,
        *,
        default_branch: str | None = None,
        head_sha: str | None = None,
        access_state: str = "available",
        synced_at: str | None = None,
    ) -> dict[str, Any]:
        project = self._project(project_slug)
        normalized = normalize_remote_url(remote_url)
        self.connection.execute(
            """
            INSERT INTO repositories(
                project_id, remote_url, normalized_remote, local_path,
                default_branch, head_sha, synced_at, access_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, normalized_remote) DO UPDATE SET
                remote_url = excluded.remote_url,
                local_path = excluded.local_path,
                default_branch = excluded.default_branch,
                head_sha = excluded.head_sha,
                synced_at = excluded.synced_at,
                access_state = excluded.access_state
            """,
            (
                project["id"],
                remote_url,
                normalized,
                local_path,
                default_branch,
                head_sha,
                synced_at or _now(),
                access_state,
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM repositories WHERE project_id = ? AND normalized_remote = ?",
            (project["id"], normalized),
        ).fetchone()
        return _row(row) or {}

    def record_commit(
        self,
        repository_id: int,
        sha: str,
        author_name: str | None,
        authored_at: str | None,
        subject: str,
        files: Iterable[dict[str, str]] = (),
    ) -> dict[str, Any]:
        self.connection.execute(
            """
            INSERT INTO commits(repository_id, sha, author_name, authored_at, subject)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(repository_id, sha) DO UPDATE SET
                author_name = excluded.author_name,
                authored_at = excluded.authored_at,
                subject = excluded.subject
            """,
            (repository_id, sha, author_name, authored_at, subject),
        )
        self.connection.execute(
            "DELETE FROM commit_files WHERE repository_id = ? AND commit_sha = ?",
            (repository_id, sha),
        )
        self.connection.executemany(
            "INSERT INTO commit_files(repository_id, commit_sha, path, status) VALUES (?, ?, ?, ?)",
            [
                (repository_id, sha, item["path"], item.get("status", "M"))
                for item in files
            ],
        )
        self.connection.commit()
        row = self.connection.execute(
            "SELECT * FROM commits WHERE repository_id = ? AND sha = ?",
            (repository_id, sha),
        ).fetchone()
        return _row(row) or {}

    def link_sources(
        self,
        project_slug: str,
        *,
        from_type: str,
        from_key: str,
        to_type: str,
        to_key: str,
        confidence: str,
        evidence_id: int | None = None,
    ) -> dict[str, Any]:
        if confidence not in CONFIDENCE_LEVELS:
            raise ValueError(f"invalid confidence: {confidence}")
        project = self._project(project_slug)
        self.connection.execute(
            """
            INSERT INTO source_links(
                project_id, from_type, from_key, to_type, to_key,
                confidence, evidence_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, from_type, from_key, to_type, to_key) DO UPDATE SET
                confidence = excluded.confidence,
                evidence_id = excluded.evidence_id
            """,
            (
                project["id"],
                from_type,
                from_key,
                to_type,
                to_key,
                confidence,
                evidence_id,
                _now(),
            ),
        )
        self.connection.commit()
        row = self.connection.execute(
            """
            SELECT * FROM source_links
            WHERE project_id = ? AND from_type = ? AND from_key = ?
              AND to_type = ? AND to_key = ?
            """,
            (project["id"], from_type, from_key, to_type, to_key),
        ).fetchone()
        return _row(row) or {}

    def search(
        self, query: str, *, project_slug: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        tokens = [token for token in query.split() if token]
        if not tokens:
            return []
        fts_query = " AND ".join(
            f'"{token.replace(chr(34), chr(34) * 2)}"*' for token in tokens
        )
        parameters: list[Any] = [fts_query]
        project_filter = ""
        if project_slug is not None:
            project_filter = " AND p.slug = ?"
            parameters.append(project_slug)
        parameters.append(limit)
        rows = self.connection.execute(
            f"""
            SELECT e.*, p.slug AS project_slug, bm25(evidence_fts) AS rank
            FROM evidence_fts
            JOIN evidence e ON e.id = CAST(evidence_fts.evidence_id AS INTEGER)
            JOIN projects p ON p.id = e.project_id
            WHERE evidence_fts MATCH ?{project_filter}
            ORDER BY rank
            LIMIT ?
            """,
            parameters,
        ).fetchall()
        return [dict(item) for item in rows]

    def project_context(self, project_slug: str) -> dict[str, Any]:
        project = self._project(project_slug)
        evidence = [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM evidence WHERE project_id = ? ORDER BY captured_at DESC",
                (project["id"],),
            ).fetchall()
        ]
        tasks = [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM tasks WHERE project_id = ? ORDER BY updated_at DESC",
                (project["id"],),
            ).fetchall()
        ]
        repositories: list[dict[str, Any]] = []
        for repository_row in self.connection.execute(
            "SELECT * FROM repositories WHERE project_id = ? ORDER BY normalized_remote",
            (project["id"],),
        ).fetchall():
            repository = dict(repository_row)
            commits: list[dict[str, Any]] = []
            for commit_row in self.connection.execute(
                "SELECT * FROM commits WHERE repository_id = ? ORDER BY authored_at DESC",
                (repository["id"],),
            ).fetchall():
                commit = dict(commit_row)
                commit["files"] = [
                    {"path": row["path"], "status": row["status"]}
                    for row in self.connection.execute(
                        """
                        SELECT path, status FROM commit_files
                        WHERE repository_id = ? AND commit_sha = ? ORDER BY path
                        """,
                        (repository["id"], commit["sha"]),
                    ).fetchall()
                ]
                commits.append(commit)
            repository["commits"] = commits
            repositories.append(repository)
        source_links = [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM source_links WHERE project_id = ? ORDER BY created_at DESC",
                (project["id"],),
            ).fetchall()
        ]
        documents = [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM project_documents WHERE project_id = ? ORDER BY captured_at DESC",
                (project["id"],),
            ).fetchall()
        ]
        work_items: list[dict[str, Any]] = []
        for item_row in self.connection.execute(
            "SELECT * FROM work_items WHERE project_id = ? ORDER BY updated_at DESC",
            (project["id"],),
        ).fetchall():
            item = self._work_item_dict(item_row)
            item["dependencies"] = [
                row["external_key"]
                for row in self.connection.execute(
                    """
                    SELECT dependency.external_key
                    FROM work_item_dependencies relation
                    JOIN work_items dependency ON dependency.id = relation.dependency_item_id
                    WHERE relation.work_item_id = ?
                    ORDER BY dependency.external_key
                    """,
                    (item["id"],),
                ).fetchall()
            ]
            item["events"] = [
                dict(row)
                for row in self.connection.execute(
                    """
                    SELECT * FROM work_item_events
                    WHERE work_item_id = ? ORDER BY occurred_at, id
                    """,
                    (item["id"],),
                ).fetchall()
            ]
            item["estimates"] = []
            for estimate_row in self.connection.execute(
                """
                SELECT * FROM work_item_estimates
                WHERE work_item_id = ? ORDER BY recorded_at, id
                """,
                (item["id"],),
            ).fetchall():
                estimate = dict(estimate_row)
                for field in ("assumptions", "exclusions", "dependencies", "workstreams"):
                    estimate[field] = json.loads(estimate[field])
                item["estimates"].append(estimate)
            item["acceptance_criteria_records"] = [
                dict(row)
                for row in self.connection.execute(
                    """
                    SELECT * FROM work_item_acceptance_criteria
                    WHERE work_item_id = ? ORDER BY updated_at, id
                    """,
                    (item["id"],),
                ).fetchall()
            ]
            work_items.append(item)
        architecture_snapshots: list[dict[str, Any]] = []
        for snapshot_row in self.connection.execute(
            """
            SELECT * FROM architecture_snapshots
            WHERE project_id = ? ORDER BY captured_at DESC
            """,
            (project["id"],),
        ).fetchall():
            snapshot = dict(snapshot_row)
            snapshot["source_refs"] = json.loads(snapshot["source_refs"])
            architecture_snapshots.append(snapshot)
        wbs_schedule_snapshots = [
            self._wbs_schedule_dict(row)
            for row in self.connection.execute(
                """
                SELECT schedule.*
                FROM work_item_schedule_snapshots schedule
                JOIN project_documents document
                  ON document.project_id = schedule.project_id
                 AND document.external_key = schedule.wbs_document_key
                WHERE schedule.project_id = ?
                ORDER BY document.captured_at DESC, schedule.display_id
                """,
                (project["id"],),
            ).fetchall()
        ]
        policy_snapshots = [
            dict(row)
            for row in self.connection.execute(
                """
                SELECT policy.*
                FROM policy_document_snapshots policy
                JOIN project_documents document
                  ON document.project_id = policy.project_id
                 AND document.external_key = policy.policy_document_key
                WHERE policy.project_id = ?
                ORDER BY document.captured_at DESC, policy.area, policy.policy_key
                """,
                (project["id"],),
            ).fetchall()
        ]
        return {
            "project": dict(project),
            "evidence": evidence,
            "tasks": tasks,
            "repositories": repositories,
            "source_links": source_links,
            "documents": documents,
            "work_items": work_items,
            "architecture_snapshots": architecture_snapshots,
            "wbs_schedule_snapshots": wbs_schedule_snapshots,
            "policy_snapshots": policy_snapshots,
        }
