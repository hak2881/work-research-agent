from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "work-policy" / "scripts" / "validate_policy.py"
TEMPLATE = ROOT / "skills" / "work-policy" / "references" / "lukuku-policy-template-v1.0.md"
FIXTURE = ROOT / "tests" / "fixtures" / "policy" / "sample-policy.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("work_policy_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_completed_policy_document_is_valid() -> None:
    load_validator().validate_policy(FIXTURE.read_text())


@pytest.mark.parametrize(
    ("replace", "message"),
    [
        (("## 2. 상품", "## 9. 상품"), "required policy sections"),
        (("2026-09-20", "YYYY-MM-DD"), "unresolved template content"),
        (("최종 검토일: 2026-09-20", "최종 검토일: 미정"), "review date"),
        (("현재 확정된 정책 없음", "검토 예정"), "policy content"),
    ],
)
def test_invalid_policy_document_is_rejected(replace: tuple[str, str], message: str) -> None:
    text = FIXTURE.read_text().replace(*replace, 1)
    with pytest.raises(ValueError, match=message):
        load_validator().validate_policy(text)


def test_reference_template_is_bundled_and_valid_as_template() -> None:
    validator = load_validator()
    text = TEMPLATE.read_text()

    assert "# {프로젝트명} 정책 문서" in text
    assert "## 8. 정산 및 회계" in text
    validator.validate_policy(text, allow_template=True)


def test_validator_cli_accepts_completed_markdown() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURE)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Policy Markdown validation passed" in result.stdout
