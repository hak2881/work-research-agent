from pathlib import Path

from work_research_history.store import HistoryStore


def make_store(tmp_path: Path) -> HistoryStore:
    return HistoryStore(tmp_path / "history.sqlite3")


def test_project_upsert_is_idempotent(tmp_path: Path) -> None:
    store = make_store(tmp_path)

    first = store.upsert_project("verish", "Verish", customer="Verish")
    second = store.upsert_project("verish", "Verish Store", customer="Verish")

    assert first["id"] == second["id"]
    assert second["name"] == "Verish Store"
    assert store.project_context("verish")["project"]["slug"] == "verish"


def test_find_projects_resolves_name_customer_and_slug(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish Store", customer="베리시")
    store.upsert_project("jente", "Jente", customer="젠테")

    assert [item["slug"] for item in store.find_projects("베리시")] == ["verish"]
    assert [item["slug"] for item in store.find_projects("verish")] == ["verish"]


def test_evidence_search_returns_provenance(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")
    evidence = store.record_evidence(
        project_slug="verish",
        source_type="slack",
        source_uri="slack://C1/123.456",
        title="Gift option request",
        claim="선물 옵션을 상품 페이지에 추가해 달라는 요청",
        excerpt="고객이 선물 옵션을 선택할 수 있어야 합니다.",
        verification_level="slack",
        confidence="explicit",
        captured_at="2026-09-17T01:00:00Z",
    )

    results = store.search("선물 옵션", project_slug="verish")

    assert results[0]["id"] == evidence["id"]
    assert results[0]["source_uri"] == "slack://C1/123.456"
    assert results[0]["confidence"] == "explicit"


def test_task_upsert_replaces_current_state_without_duplication(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")

    created = store.upsert_task("verish", "slack:C1:123", "선물 옵션 검토", "open")
    updated = store.upsert_task("verish", "slack:C1:123", "선물 옵션 검토", "done")
    context = store.project_context("verish")

    assert created["id"] == updated["id"]
    assert updated["state"] == "done"
    assert len(context["tasks"]) == 1


def test_developer_plan_records_document_work_items_and_dependencies(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")

    first_document = store.record_document(
        "verish",
        "prd:checkout:v1",
        "file:///tmp/checkout-prd.md",
        "prd",
        "Checkout PRD",
        version="1",
        content_hash="sha256:abc",
        captured_at="2026-09-18T01:00:00Z",
    )
    same_document = store.record_document(
        "verish",
        "prd:checkout:v1",
        "file:///tmp/checkout-prd.md",
        "prd",
        "Checkout PRD",
        version="1",
        content_hash="sha256:abc",
        captured_at="2026-09-18T01:00:00Z",
    )
    store.upsert_work_item(
        "verish",
        "DEV-1",
        "Persist retry state",
        state="ready",
        workstream="backend",
        estimate_min=4,
        estimate_max=8,
        estimate_unit="hours",
        estimate_confidence="medium",
        origin="explicit",
        estimate_basis="engineering",
        acceptance_criteria=["A failed delivery is persisted"],
        assumptions=["Existing queue is reused"],
        exclusions=["No new AWS resource"],
    )
    store.upsert_work_item(
        "verish",
        "DEV-2",
        "Retry failed deliveries",
        state="planned",
        workstream="backend",
        estimate_min=8,
        estimate_max=12,
        estimate_unit="hours",
        estimate_confidence="low",
        origin="proposed",
        estimate_basis="source",
        acceptance_criteria=["Retries stop at the configured limit"],
    )
    dependency = store.link_work_item_dependency("verish", "DEV-2", "DEV-1")

    context = store.project_context("verish")

    assert first_document["id"] == same_document["id"]
    assert context["documents"][0]["content_hash"] == "sha256:abc"
    assert context["work_items"][0]["acceptance_criteria"] == [
        "Retries stop at the configured limit"
    ]
    assert context["work_items"][0]["dependencies"] == ["DEV-1"]
    assert context["work_items"][0]["origin"] == "proposed"
    assert context["work_items"][0]["estimate_basis"] == "source"
    assert dependency["dependency_key"] == "DEV-1"


def test_work_item_events_preserve_state_history(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")
    store.upsert_work_item("verish", "DEV-1", "Retry worker", state="ready")

    store.record_work_item_event(
        "verish",
        "DEV-1",
        "implementation_started",
        "Started from the accepted plan",
        state="in_progress",
        repository_sha="api@abc123",
        occurred_at="9999-01-01T02:00:00Z",
    )
    store.record_work_item_event(
        "verish",
        "DEV-1",
        "verification",
        "Unit and integration tests passed",
        state="verification_pending",
        repository_sha="api@def456",
        occurred_at="9999-01-01T03:00:00Z",
    )

    item = store.project_context("verish")["work_items"][0]

    assert item["state"] == "verification_pending"
    assert [event["to_state"] for event in item["events"]] == [
        "ready",
        "in_progress",
        "verification_pending",
    ]
    assert item["events"][-1]["repository_sha"] == "api@def456"


def test_work_item_keeps_multiple_estimates_and_sourced_acceptance_criteria(
    tmp_path: Path,
) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")
    store.upsert_work_item("verish", "DEV-1", "Retry worker", state="planned")

    store.record_work_item_estimate(
        "verish",
        "DEV-1",
        "wbs-v1",
        "source",
        2,
        2,
        "days",
        confidence="unverified",
    )
    store.record_work_item_estimate(
        "verish",
        "DEV-1",
        "engineering-api@abc123",
        "engineering",
        20,
        32,
        "hours",
        confidence="medium",
        assumptions=["Existing queue is reused"],
        exclusions=["No storefront changes"],
        dependencies=["Architecture decision ADR-12"],
        workstreams=["backend", "infrastructure"],
        repository_sha="api@abc123",
    )
    store.upsert_acceptance_criterion(
        "verish",
        "DEV-1",
        "prd-no-loss",
        "Failed webhooks are not lost",
        origin="explicit",
        status="accepted",
    )
    store.upsert_acceptance_criterion(
        "verish",
        "DEV-1",
        "eng-idempotency",
        "Duplicate delivery has no duplicate side effect",
        origin="proposed",
        status="proposed",
    )

    item = store.project_context("verish")["work_items"][0]

    assert [estimate["basis"] for estimate in item["estimates"]] == [
        "source",
        "engineering",
    ]
    assert item["estimates"][1]["assumptions"] == ["Existing queue is reused"]
    assert item["estimates"][1]["exclusions"] == ["No storefront changes"]
    assert item["estimates"][1]["dependencies"] == ["Architecture decision ADR-12"]
    assert item["estimates"][1]["workstreams"] == ["backend", "infrastructure"]
    assert item["estimates"][1]["repository_sha"] == "api@abc123"
    assert [criterion["origin"] for criterion in item["acceptance_criteria_records"]] == [
        "explicit",
        "proposed",
    ]
    assert item["acceptance_criteria_records"][1]["status"] == "proposed"


def test_architecture_snapshots_are_versioned_in_project_context(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")

    snapshot = store.record_architecture_snapshot(
        "verish",
        "2026-09-18-api@abc123",
        "Shopify webhook processing",
        "flowchart LR\nShopify --> API --> Queue --> Worker",
        "AWS account 123456789012, ap-northeast-2, checked 2026-09-18T04:00:00Z",
        source_refs=["api@abc123", "aws://123456789012/ap-northeast-2"],
        verification_status="partially_verified",
        captured_at="2026-09-18T04:00:00Z",
    )

    context = store.project_context("verish")

    assert context["architecture_snapshots"][0]["id"] == snapshot["id"]
    assert context["architecture_snapshots"][0]["source_refs"] == [
        "api@abc123",
        "aws://123456789012/ap-northeast-2",
    ]


def test_repository_and_commit_are_idempotent(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("jente", "Jente")
    repository = store.register_repository(
        "jente",
        "git@github.com:hak2881/storefront.git",
        "/tmp/lukuku/jente/storefront",
        default_branch="main",
        head_sha="abc123",
        access_state="available",
    )
    duplicate = store.register_repository(
        "jente",
        "https://github.com/hak2881/storefront.git",
        "/tmp/lukuku/jente/storefront",
        default_branch="main",
        head_sha="def456",
        access_state="available",
    )
    first_commit = store.record_commit(
        repository["id"],
        "c0ffee",
        "Kim",
        "2026-09-16T10:00:00Z",
        "Add gift option",
        [{"path": "app/gift.py", "status": "M"}],
    )
    second_commit = store.record_commit(
        repository["id"],
        "c0ffee",
        "Kim",
        "2026-09-16T10:00:00Z",
        "Add gift option",
        [{"path": "app/gift.py", "status": "M"}],
    )

    assert repository["id"] == duplicate["id"]
    assert duplicate["head_sha"] == "def456"
    assert first_commit["id"] == second_commit["id"]
    assert store.project_context("jente")["repositories"][0]["commits"][0]["files"] == [
        {"path": "app/gift.py", "status": "M"}
    ]


def test_source_links_appear_in_project_context(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")

    link = store.link_sources(
        "verish",
        from_type="slack",
        from_key="slack://C1/123.456",
        to_type="commit",
        to_key="c0ffee",
        confidence="verified",
    )
    duplicate = store.link_sources(
        "verish",
        from_type="slack",
        from_key="slack://C1/123.456",
        to_type="commit",
        to_key="c0ffee",
        confidence="verified",
    )

    assert link["id"] == duplicate["id"]
    assert store.project_context("verish")["source_links"][0]["confidence"] == "verified"


def test_rejects_unknown_verification_values(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.upsert_project("verish", "Verish")

    try:
        store.record_evidence(
            project_slug="verish",
            source_type="slack",
            source_uri="slack://C1/123",
            title="Invalid",
            claim="Invalid",
            verification_level="guess",
            confidence="explicit",
        )
    except ValueError as exc:
        assert "verification_level" in str(exc)
    else:
        raise AssertionError("invalid verification level was accepted")
