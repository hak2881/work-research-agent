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

    @server.tool(name="history_record_document")
    async def record_document(
        project_slug: str,
        external_key: str,
        source_uri: str,
        document_type: str,
        title: str,
        content_hash: str,
        version: str | None = None,
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        """Record the identity and version of a PRD, WBS, or other project source."""
        return store.record_document(
            project_slug,
            external_key,
            source_uri,
            document_type,
            title,
            version=version,
            content_hash=content_hash,
            captured_at=captured_at,
        )

    @server.tool(name="history_upsert_work_item")
    async def upsert_work_item(
        project_slug: str,
        external_key: str,
        title: str,
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
        acceptance_criteria: list[str] | None = None,
        assumptions: list[str] | None = None,
        exclusions: list[str] | None = None,
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        """Create or update a sourced developer work item and its current state."""
        return store.upsert_work_item(
            project_slug,
            external_key,
            title,
            state=state,
            parent_key=parent_key,
            description=description,
            workstream=workstream,
            priority=priority,
            estimate_min=estimate_min,
            estimate_max=estimate_max,
            estimate_unit=estimate_unit,
            estimate_confidence=estimate_confidence,
            origin=origin,
            estimate_basis=estimate_basis,
            acceptance_criteria=acceptance_criteria or [],
            assumptions=assumptions or [],
            exclusions=exclusions or [],
            source_evidence_id=source_evidence_id,
        )

    @server.tool(name="history_record_work_item_event")
    async def record_work_item_event(
        project_slug: str,
        external_key: str,
        event_type: str,
        note: str,
        state: str | None = None,
        source_evidence_id: int | None = None,
        repository_sha: str | None = None,
        occurred_at: str | None = None,
    ) -> dict[str, Any]:
        """Append a decision, state transition, implementation, or verification event."""
        return store.record_work_item_event(
            project_slug,
            external_key,
            event_type,
            note,
            state=state,
            source_evidence_id=source_evidence_id,
            repository_sha=repository_sha,
            occurred_at=occurred_at,
        )

    @server.tool(name="history_record_work_item_estimate")
    async def record_work_item_estimate(
        project_slug: str,
        external_key: str,
        estimate_key: str,
        basis: str,
        estimate_min: float,
        estimate_max: float,
        unit: str,
        confidence: str,
        assumptions: list[str] | None = None,
        exclusions: list[str] | None = None,
        dependencies: list[str] | None = None,
        workstreams: list[str] | None = None,
        repository_sha: str | None = None,
        source_evidence_id: int | None = None,
        recorded_at: str | None = None,
    ) -> dict[str, Any]:
        """Record a versioned source or engineering estimate without overwriting another."""
        return store.record_work_item_estimate(
            project_slug,
            external_key,
            estimate_key,
            basis,
            estimate_min,
            estimate_max,
            unit,
            confidence=confidence,
            assumptions=assumptions or [],
            exclusions=exclusions or [],
            dependencies=dependencies or [],
            workstreams=workstreams or [],
            repository_sha=repository_sha,
            source_evidence_id=source_evidence_id,
            recorded_at=recorded_at,
        )

    @server.tool(name="history_upsert_acceptance_criterion")
    async def upsert_acceptance_criterion(
        project_slug: str,
        external_key: str,
        criterion_key: str,
        criterion: str,
        origin: str,
        status: str,
        source_evidence_id: int | None = None,
    ) -> dict[str, Any]:
        """Store an explicit or proposed acceptance criterion and its approval state."""
        return store.upsert_acceptance_criterion(
            project_slug,
            external_key,
            criterion_key,
            criterion,
            origin=origin,
            status=status,
            source_evidence_id=source_evidence_id,
        )

    @server.tool(name="history_link_work_item_dependency")
    async def link_work_item_dependency(
        project_slug: str, work_item_key: str, dependency_key: str
    ) -> dict[str, Any]:
        """Link a work item to another item that must be completed first."""
        return store.link_work_item_dependency(
            project_slug, work_item_key, dependency_key
        )

    @server.tool(name="history_record_architecture_snapshot")
    async def record_architecture_snapshot(
        project_slug: str,
        version: str,
        summary: str,
        diagram_mermaid: str,
        details_markdown: str,
        verification_status: str,
        source_refs: list[str] | None = None,
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        """Record a versioned, evidence-backed technical architecture snapshot."""
        return store.record_architecture_snapshot(
            project_slug,
            version,
            summary,
            diagram_mermaid,
            details_markdown,
            source_refs=source_refs or [],
            verification_status=verification_status,
            captured_at=captured_at,
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
