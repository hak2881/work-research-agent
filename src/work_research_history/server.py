from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from .store import HistoryStore


def default_database_path() -> Path:
    configured = os.environ.get("WORK_RESEARCH_DB")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".local" / "share" / "work-research-agent" / "history.sqlite3"


def create_server(database_path: str | Path | None = None) -> MCPServer:
    store = HistoryStore(database_path or default_database_path())
    server = MCPServer("work-research-history")

    @server.tool(name="history_upsert_project")
    async def upsert_project(slug: str, name: str, customer: str | None = None) -> dict[str, Any]:
        """Create or update a project identity used to group evidence."""
        return store.upsert_project(slug, name, customer)

    @server.tool(name="history_record_evidence")
    async def record_evidence(
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
        """Record a sourced claim with verification and relationship confidence."""
        return store.record_evidence(
            project_slug=project_slug,
            source_type=source_type,
            source_uri=source_uri,
            title=title,
            claim=claim,
            excerpt=excerpt,
            verification_level=verification_level,
            confidence=confidence,
            captured_at=captured_at,
        )

    @server.tool(name="history_upsert_task")
    async def upsert_task(
        project_slug: str,
        external_key: str,
        title: str,
        state: str,
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        """Store an explicitly assigned or unresolved project item."""
        return store.upsert_task(
            project_slug,
            external_key,
            title,
            state,
            source_evidence_id,
        )

    @server.tool(name="history_register_repository")
    async def register_repository(
        project_slug: str,
        remote_url: str,
        local_path: str,
        default_branch: str | None = None,
        head_sha: str | None = None,
        access_state: str = "available",
        synced_at: str | None = None,
    ) -> dict[str, Any]:
        """Register a discovered Git repository and its latest sync state."""
        return store.register_repository(
            project_slug,
            remote_url,
            local_path,
            default_branch=default_branch,
            head_sha=head_sha,
            access_state=access_state,
            synced_at=synced_at,
        )

    @server.tool(name="history_record_commit")
    async def record_commit(
        repository_id: int,
        sha: str,
        subject: str,
        author_name: str | None = None,
        authored_at: str | None = None,
        files: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Record commit metadata and changed paths without copying Git blobs."""
        return store.record_commit(
            repository_id,
            sha,
            author_name,
            authored_at,
            subject,
            files or [],
        )

    @server.tool(name="history_link_sources")
    async def link_sources(
        project_slug: str,
        from_type: str,
        from_key: str,
        to_type: str,
        to_key: str,
        confidence: str,
        evidence_id: int | None = None,
    ) -> dict[str, Any]:
        """Link Slack, task, repository, commit, document, or browser evidence."""
        return store.link_sources(
            project_slug,
            from_type=from_type,
            from_key=from_key,
            to_type=to_type,
            to_key=to_key,
            confidence=confidence,
            evidence_id=evidence_id,
        )

    @server.tool(name="history_search")
    async def search_history(
        query: str, project_slug: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search evidence text and return provenance with each result."""
        return store.search(query, project_slug=project_slug, limit=limit)

    @server.tool(name="history_find_projects")
    async def find_projects(query: str, limit: int = 20) -> list[dict[str, Any]]:
        """Resolve a project by slug, name, or customer and return coverage counts."""
        return store.find_projects(query, limit=limit)

    @server.tool(name="history_project_context")
    async def project_context(project_slug: str) -> dict[str, Any]:
        """Return work evidence, optional open items, repositories, commits, and links."""
        return store.project_context(project_slug)

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
