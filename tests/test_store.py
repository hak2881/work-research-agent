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

