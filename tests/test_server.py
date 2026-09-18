from pathlib import Path

import pytest
from mcp import Client

from work_research_history.server import create_server


@pytest.mark.anyio
async def test_mcp_lists_and_calls_history_tools(tmp_path: Path) -> None:
    server = create_server(tmp_path / "history.sqlite3")

    async with Client(server) as client:
        listed = await client.list_tools()
        names = {tool.name for tool in listed.tools}
        created = await client.call_tool(
            "history_upsert_project",
            {"slug": "verish", "name": "Verish", "customer": "Verish"},
        )
        context = await client.call_tool(
            "history_project_context", {"project_slug": "verish"}
        )
        projects = await client.call_tool("history_find_projects", {"query": "Verish"})

    assert {
        "history_upsert_project",
        "history_record_evidence",
        "history_upsert_task",
        "history_register_repository",
        "history_record_commit",
        "history_link_sources",
        "history_search",
        "history_find_projects",
        "history_project_context",
    }.issubset(names)
    assert created.structured_content["slug"] == "verish"
    assert context.structured_content["project"]["name"] == "Verish"
    assert projects.structured_content["result"][0]["slug"] == "verish"
