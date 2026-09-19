import json
import re
import runpy
import shutil
import subprocess
import sys
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
        "work-prd",
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


def test_work_prd_uses_bounded_history_without_inventing_requirements() -> None:
    skill_root = ROOT / "skills" / "work-prd"
    skill = (skill_root / "SKILL.md").read_text()
    history_rules = (skill_root / "references" / "history-resolution.md").read_text()
    contract = (skill_root / "references" / "prd-contract.md").read_text()

    assert "$work-prd <Slack permalink>" in skill
    assert "$work-prd <project>" in skill
    assert "$work-prd <project> <scope>" in skill
    assert "history_project_context" in skill
    assert "history_record_document" in skill
    assert "Do not create work items" in skill
    assert "load project history before asking the user to choose" in skill
    assert "<document-external-key>#FR-NNN" in skill
    assert "Escape source text as HTML" in skill
    assert "every page passes" in skill
    assert "superseded" in history_rules
    assert "Current code proves current behavior" in history_rules
    assert "proposed completion criterion" in contract
    assert "[제안·확인 필요]" in contract
    assert "explicit version lineage" in contract
    assert "확정 | 확인 필요 | 보류" in contract
    assert "$dev-plan" in contract


def test_work_prd_ships_the_lukuku_standard_template_and_renderer(tmp_path: Path) -> None:
    skill_root = ROOT / "skills" / "work-prd"
    template = skill_root / "assets" / "lukuku-prd-template.html"
    stylesheet = skill_root / "assets" / "lukuku-prd-template.css"
    renderer = skill_root / "scripts" / "render_prd.py"

    assert template.is_file()
    assert stylesheet.is_file()
    assert renderer.is_file()
    html = template.read_text()
    for section in (
        "문서 정보",
        "배경과 목표",
        "포함·제외 범위",
        "사용자와 주요 업무 흐름",
        "기능 요구사항",
        "품질·제약 조건",
        "선행 조건·미확정 사항",
        "전체 인수 기준·관련 문서",
    ):
        assert section in html

    result = subprocess.run(
        [
            sys.executable,
            str(renderer),
            "--allow-placeholders",
            "--validate-only",
            str(template),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PRD HTML validation passed" in result.stdout

    unresolved = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(template)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert unresolved.returncode == 1
    assert "unresolved template placeholders" in unresolved.stderr

    invalid_order = tmp_path / "invalid-order.html"
    html = template.read_text()
    html = html.replace('data-prd-section="1"', 'data-prd-section="swap"')
    html = html.replace('data-prd-section="2"', 'data-prd-section="1"')
    html = html.replace('data-prd-section="swap"', 'data-prd-section="2"')
    invalid_order.write_text(html)
    shutil.copy2(stylesheet, tmp_path / stylesheet.name)
    wrong_order = subprocess.run(
        [
            sys.executable,
            str(renderer),
            "--allow-placeholders",
            "--validate-only",
            str(invalid_order),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert wrong_order.returncode == 1
    assert "sections must appear in order" in wrong_order.stderr

    blank_field = tmp_path / "blank-field.html"
    blank_html = template.read_text().replace("{{PROJECT_NAME}}", "")
    blank_html = re.sub(r"\{\{[^{}]+\}\}", "값", blank_html)
    blank_field.write_text(blank_html)
    blank_result = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(blank_field)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert blank_result.returncode == 1
    assert "required PRD field is empty" in blank_result.stderr

    materialized = template.read_text()
    row_values = {
        "GOAL_ROWS": "<tr><td>목표</td><td>결과</td><td>확인</td></tr>",
        "IN_SCOPE_ROWS": "<tr><td>범위</td><td>내용</td></tr>",
        "OUT_OF_SCOPE_ROWS": "<tr><td>제외</td><td>사유</td></tr>",
        "ROLE_ROWS": "<tr><td>역할</td><td>목적</td><td>업무</td></tr>",
        "FLOW_ROWS": "<tr><td>1</td><td>사용자</td><td>동작</td><td>결과</td></tr>",
        "FUNCTIONAL_REQUIREMENT_ROWS": (
            "<tr><td>FR-001</td><td>요구사항</td><td>필수</td>"
            "<td>확정</td><td>완료 기준</td></tr>"
        ),
        "TECHNICAL_CONTEXT_ROWS": "<tr><td>대상</td><td>현황</td><td>근거</td></tr>",
        "QUALITY_ROWS": "<tr><td>NFR-001</td><td>품질</td><td>기준</td><td>근거</td></tr>",
        "CONSTRAINT_ROWS": "<tr><td>제약</td><td>영향</td><td>상태</td></tr>",
        "PREREQUISITE_ROWS": "<tr><td>준비</td><td>담당</td><td>시점</td><td>영향</td></tr>",
        "OPEN_QUESTION_ROWS": "<tr><td>질문</td><td>FR-001</td><td>담당</td><td>미정</td></tr>",
        "ACCEPTANCE_ROWS": "<tr><td>대상</td><td>기준</td><td>근거</td></tr>",
        "RELATED_DOCUMENT_ROWS": "<tr><td>문서</td><td>v1</td><td>위치</td><td>FR-001</td></tr>",
    }
    for placeholder, value in row_values.items():
        materialized = materialized.replace(f"{{{{{placeholder}}}}}", value)
    materialized = re.sub(r"\{\{[^{}]+\}\}", "값", materialized)

    complete = tmp_path / "complete.html"
    complete.write_text(materialized)
    complete_result = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(complete)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert complete_result.returncode == 0, complete_result.stderr

    missing_rows = tmp_path / "missing-rows.html"
    missing_rows.write_text(
        materialized.replace(row_values["FUNCTIONAL_REQUIREMENT_ROWS"], "")
    )
    missing_rows_result = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(missing_rows)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_rows_result.returncode == 1
    assert "functional-requirements requires at least one row" in missing_rows_result.stderr

    incomplete_fr = tmp_path / "incomplete-fr.html"
    incomplete_fr.write_text(materialized.replace("<td>요구사항</td>", "<td></td>"))
    incomplete_result = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(incomplete_fr)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert incomplete_result.returncode == 1
    assert "functional-requirements contains an incomplete row" in incomplete_result.stderr

    unsafe_html = tmp_path / "unsafe.html"
    unsafe_html.write_text(materialized.replace("<td>목표</td>", '<td><img src="https://example.com/a.png"></td>'))
    unsafe_result = subprocess.run(
        [sys.executable, str(renderer), "--validate-only", str(unsafe_html)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert unsafe_result.returncode == 1
    assert "blocked remote media source" in unsafe_result.stderr


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
    assert "적절한 작업 방안을 검토 부탁드립니다" in contract
    assert "not an implementation specification" in contract
    assert "권장 방안: 미정" in contract
    assert "Do not imply feasibility merely to fill the template" in contract


def test_work_research_keeps_pm_and_developer_messages_non_committal() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "brief sendable handoff, not a technical design" in skill
    assert "Do not include file names, line numbers, code-level steps" in skill
    assert "Do not tell the customer how the feature will be implemented" in skill
    assert "가능할 것으로 보입니다" in contract
    assert "가능 여부를 검토한 뒤 안내드리겠습니다" in contract
    assert "Never promise implementation" in contract
    assert "꼭 확인할 항목:" not in contract


def test_work_research_output_is_customer_first_and_hides_routine_mechanics() -> None:
    skill_root = ROOT / "skills" / "work-research"
    skill = (skill_root / "SKILL.md").read_text()
    contract = (skill_root / "references" / "response-contract.md").read_text()

    assert "Customer response comes first" in contract
    assert "핵심 판단" in contract
    assert "개발자에게 요청할 내용" in contract
    assert "short handoff, not an implementation specification" in contract
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
