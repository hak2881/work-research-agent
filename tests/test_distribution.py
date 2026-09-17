import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_distribution_installs_files_required_to_build_local_mcp() -> None:
    manifest = yaml.safe_load((ROOT / "distribution.yaml").read_text())
    owned = set(manifest["distribution_owned"])

    assert {"README.md", "pyproject.toml", "src/"}.issubset(owned)


def test_codex_plugin_exposes_skills_and_history_mcp() -> None:
    plugin_root = ROOT / "plugins" / "work-research-agent"
    manifest = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text())
    mcp = json.loads((plugin_root / ".mcp.json").read_text())

    assert manifest["name"] == "work-research-agent"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert "work_history" in mcp["mcpServers"]
    assert {
        path.parent.name for path in (plugin_root / "skills").glob("*/SKILL.md")
    } == {"work-history", "work-research"}

    for source in (ROOT / "skills").glob("**/*"):
        if source.is_file():
            relative = source.relative_to(ROOT / "skills")
            assert source.read_bytes() == (plugin_root / "skills" / relative).read_bytes()


def test_claude_plugin_uses_the_same_skills_and_mcp() -> None:
    plugin_root = ROOT / "plugins" / "work-research-agent"
    manifest = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text())
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

    assert manifest["name"] == "work-research-agent"
    assert marketplace["plugins"][0]["source"] == "./plugins/work-research-agent"
    assert (plugin_root / ".mcp.json").is_file()


def test_readme_documents_supported_host_runtimes() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "Codex와 Claude Code" in readme
    assert "해당 호스트의 모델과 토큰" in readme
    assert "docs/codex-installation.md" in readme


def test_work_history_prioritizes_completed_work_over_todos() -> None:
    skill = (ROOT / "skills" / "work-history" / "SKILL.md").read_text()

    assert "completed work" in skill
    assert "Do not infer a TODO" in skill
    assert "one-time bootstrap" in skill
    assert "Do not filter repositories by the person's ownership" in skill


def test_work_research_incrementally_persists_new_history() -> None:
    skill = (ROOT / "skills" / "work-research" / "SKILL.md").read_text()

    assert "Persist newly verified" in skill


def test_codex_docs_use_skill_invocation_syntax() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "$work-history 김병학" in readme
    assert "$work-research https://" in readme
