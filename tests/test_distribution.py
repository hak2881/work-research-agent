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
        "dev-pr",
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


def test_work_research_supports_comparison_and_request_focused_modes() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "`$work-research 1 <Slack permalink>`" in skill
    assert "`$work-research 2 <Slack permalink>`" in skill
    assert "default to mode 2" in skill
    assert "A similar historical symptom is not root-cause evidence" in skill
    assert "directly reproduced or traced end-to-end" in skill
    assert "A. 재발 방지 관점" in contract
    assert "B. 현재 요청 관점" in contract
    assert "요청 중심 답변" in contract
    assert "복사 A" in contract
    assert "전체 재검수" in contract
    for discouraged in (
        "해당 부분만",
        "요청 범위에 한정",
        "최소한으로 수정",
        "단순 수정",
    ):
        assert discouraged not in contract


def test_work_research_may_download_sources_needed_for_verification() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    routing = (skill_root / "references" / "research-routing.md").read_text()

    assert "download it without asking for separate confirmation" in skill
    assert "Slack attachment" in routing
    assert "sanitized source URL" in routing
    assert "content hash" in routing
    assert "already available through the current access" in routing
    assert "generate a new export" in routing
    assert "Do not execute, install, or upload" in routing


def test_work_research_checks_current_remote_default_branch_code() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    routing = (skill_root / "references" / "research-routing.md").read_text()

    assert "git fetch --prune <verified-remote>" in skill
    assert "git pull --ff-only" in skill
    assert "remote default branch" in skill
    assert "temporary worktree" in skill
    assert "local HEAD is an ancestor" in skill
    assert "HEAD exactly equals the fetched" in skill
    assert "unique temporary path" in skill
    assert "remove only that temporary worktree" in skill
    assert "Do not run global `git worktree prune`" in skill
    assert "Never reset, clean, stash, merge, or rebase" in skill
    assert "inspected SHA" in routing
    assert "CodeGraph index corresponds to the inspected SHA" in routing


def test_work_research_requests_developer_review_without_estimating_effort() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "Do not estimate effort" in skill
    assert "hours, days, story points, cost, staffing, or delivery dates" in skill
    assert "route the estimate request to `$dev-plan`" in skill
    assert "권장 방안" in contract
    assert "더 적합한 방안" in contract
    assert "구현 가능성" in contract
    assert "검수 부탁드립니다" in contract
    assert "candidate for developer review, not an approved design" in contract
    assert "권장 방안: 미정" in contract
    assert "Do not imply feasibility merely to fill the template" in contract


def test_work_research_output_is_customer_first_and_hides_routine_mechanics() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "Customer response comes first" in contract
    assert "핵심 판단" in contract
    assert "꼭 확인할 항목" in contract
    assert "확인 완료 (`verified`)" in contract
    assert "부분 확인 (`partially verified`)" in contract
    assert "확인 불가 (`blocked`)" in contract
    assert "Do not print an estimate section when no estimate was requested" in skill
    assert "routine Git transport" in skill
    assert "memory-file" in skill
    assert "answer-changing" in skill
    assert "Customer-facing text must not generalize" in contract
    assert "내부 이력 저장 실패" in contract
    assert "이력: 저장 완료" not in contract


def test_work_research_classifies_implementation_area_in_both_modes() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "프론트엔드 | 백엔드 | 공동 | 개발 불필요 | 미확인" in contract
    assert "Mode 1 must classify each option separately" in skill
    assert "Do not infer the area from the channel" in skill
    assert "Shopify Admin configuration" in skill
    assert "affected repositories and code paths" in skill
    assert contract.count("구현 영역") >= 3


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


def test_dev_plan_returns_a_pm_reply_and_uses_html_for_complex_reviews() -> None:
    skill_root = ROOT / "skills" / "dev-plan"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "planning-contract.md").read_text()

    assert "PM에게 전달할 내용" in contract
    assert "simple review" in skill
    assert "complex review" in skill
    assert "~/.local/share/work-research-agent/reports/" in skill
    assert "self-contained HTML" in skill
    assert "Do not create HTML merely because" in skill
    assert "Do not post the reply to Slack" in skill
    assert "route trigger" in skill
    assert "complete detailed plan in the HTML" in skill
    assert "resolved path remains inside" in skill
    assert "atomic write" in skill
    assert "private user-only permissions" in skill
    assert "allowlisted link schemes" in skill
    assert "escape untrusted source text" in skill
    assert "visually inspect" in skill
    assert "inline fallback" in skill
    assert "추가 없음" in contract


def test_dev_workflows_share_a_proportional_evidence_first_report_standard() -> None:
    plan_skill = (ROOT / "skills" / "dev-plan" / "SKILL.md").read_text()
    implement_skill = (ROOT / "skills" / "dev-implement" / "SKILL.md").read_text()
    quality = (
        ROOT / "skills" / "dev-plan" / "references" / "report-quality.md"
    ).read_text()
    implementation_contract = (
        ROOT
        / "skills"
        / "dev-implement"
        / "references"
        / "implementation-contract.md"
    ).read_text()

    assert "references/report-quality.md" in plan_skill
    assert "../dev-plan/references/report-quality.md" in implement_skill
    assert "decision before detail" in quality
    assert "facts, proposals, and unknowns" in quality
    assert "Do not copy the benchmark's section count" in quality
    assert "Every material statement" in quality
    assert "필수 | 조건부 | 파생" in quality
    assert "information density" in quality
    assert "preserve heading and table topology" in quality
    assert "stable row identifiers" in quality
    assert "rendered-view spot checks" in quality
    assert "OCR" in quality
    assert "visually verify" in quality
    assert "derived navigation artifact, not an authoritative source" in implement_skill
    assert "generated report URI, content hash, checked time" in implement_skill
    assert "final repository SHA" in implement_skill
    assert "HTML is exceptional" in implementation_contract


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


def test_dev_pr_creates_only_one_evidence_backed_pull_request() -> None:
    skill_root = ROOT / "skills" / "dev-pr"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "pr-contract.md").read_text()

    assert "When invoked without an argument" in skill
    assert "current Git root" in skill
    assert "exactly one corroborated work item" in skill
    assert "Require the resolved item to be `verification_pending`" in skill
    assert "verified SHA" in skill
    assert "explicit delivery rule" in skill
    assert "Enumerate existing pull requests" in skill
    assert "Never force-push" in skill
    assert "Never invoke `$b-end`" in skill
    assert "Never invoke `$f-end`" in skill
    assert "Never invoke `$b-deploy`" in skill
    assert "history_record_work_item_event" in skill
    assert "`pr_create_uncertain`" in skill
    assert "Do not retry PR creation" in skill
    assert "PR 생성 결과" in contract
    assert "병합·배포" in contract


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
