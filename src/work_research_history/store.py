from __future__ import annotations

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
        return {
            "project": dict(project),
            "evidence": evidence,
            "tasks": tasks,
            "repositories": repositories,
            "source_links": source_links,
        }
