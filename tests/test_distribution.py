import json
import runpy
import shutil
from pathlib import Path

import pytest
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
    } == {
        "work-history",
        "work-research",
        "work-status",
        "work-act",
        "dev-plan",
        "dev-implement",
        "dev-context",
    }

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
    contract = (
        ROOT / "skills" / "work-research" / "references" / "response-contract.md"
    ).read_text()

    assert "Persist newly verified" in skill
    assert "개발자에게 요청할 내용" in contract
    assert "고객사에게 답변할 내용" in contract
    assert "developer review required" in contract


def test_codex_docs_use_skill_invocation_syntax() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "$work-history 김병학" in readme
    assert "$work-research https://" in readme
    assert "$work-status <프로젝트>" in readme


def test_work_status_reports_evidence_backed_current_state() -> None:
    skill_root = ROOT / "skills" / "work-status"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "status-contract.md").read_text()

    assert "Do not invent a completion percentage" in skill
    assert "last stored evidence" in skill
    assert "repository@SHA" in contract
    assert "완료된 작업" in contract
    assert "진행 중" in contract
    assert "차단·확인 필요" in contract
    assert "상태 미확인" in contract
    assert "Slack 이전 확인 지점" in contract
    assert "Evidence-only writes" in skill
    assert "$work-act" in contract


def test_dev_plan_separates_sourced_requirements_from_engineering_proposals() -> None:
    skill_root = ROOT / "skills" / "dev-plan"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "planning-contract.md").read_text()

    assert 'origin="proposed"' in skill
    assert 'estimate_basis="source"' in skill
    assert 'estimate_basis="engineering"' in skill
    assert "current repository@SHA" in skill
    assert "authoritative denominator" in skill
    assert "Do not edit product code" in skill
    assert "요구사항 충돌·질문" in contract
    assert "공수 범위와 근거" in contract


def test_dev_implement_revalidates_history_and_stops_before_end_or_deploy() -> None:
    skill_root = ROOT / "skills" / "dev-implement"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "implementation-contract.md").read_text()

    assert "Invoke `$b-start`" in skill
    assert "Never invoke `$b-end`" in skill
    assert "Never invoke `$b-deploy`" in skill
    assert "accepted acceptance criteria" in skill
    assert "current repository@SHA" in skill
    assert "unrelated dirty work" in skill
    assert "verification_pending" in skill
    assert "Slack permalink" in skill
    assert "root and every reply" in skill
    assert "exactly one `ready` work item" in skill
    assert "../dev-plan/SKILL.md" in skill
    assert "history_link_sources" in skill
    assert "Do not post" in skill
    assert "히스토리 일치 검수" in contract
    assert "완료 조건별 검수" in contract


def test_dev_context_separates_architecture_evidence_and_progress() -> None:
    skill_root = ROOT / "skills" / "dev-context"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "context-contract.md").read_text()

    assert "desired, configured, deployed, and live" in skill
    assert "AWS account, region, principal, and checked time" in skill
    assert "solid Mermaid" in skill
    assert "dashed" in skill
    assert "every mapped repository" in skill
    assert "authoritative denominator" in skill
    assert "accepted acceptance criteria" in skill
    assert "read-only" in skill
    assert "AWS·네트워크·IAM" in contract
    assert "다음 착수 가능 작업" in contract


@pytest.mark.parametrize("damage", ["missing", "changed", "extra"])
def test_distribution_validator_rejects_packaged_skill_drift(tmp_path: Path, damage: str) -> None:
    for directory in (".agents", ".claude-plugin", "plugins", "skills"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    for filename in ("distribution.yaml", "mcp.json", "config.yaml"):
        shutil.copy2(ROOT / filename, tmp_path / filename)

    packaged = tmp_path / "plugins/work-research-agent/skills/work-act"
    reference = packaged / "references/execution-contract.md"
    if damage == "missing":
        reference.unlink()
    elif damage == "changed":
        reference.write_text("Different execution contract\n")
    else:
        (packaged / "unexpected.md").write_text("Unpackaged source\n")

    validate = runpy.run_path(str(ROOT / "scripts/validate_distribution.py"))["main"]
    validate.__globals__["ROOT"] = tmp_path
    with pytest.raises(ValueError, match="(source and packaged|differs from source)"):
        validate()
