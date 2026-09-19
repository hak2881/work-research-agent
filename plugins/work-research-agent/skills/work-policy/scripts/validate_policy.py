#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    ("1", "회원"),
    ("2", "상품"),
    ("3", "주문"),
    ("4", "클레임"),
    ("5", "CRM"),
    ("6", "물류"),
    ("7", "판매 채널"),
    ("8", "정산 및 회계"),
]
INFO_FIELDS = [
    "프로젝트명",
    "대상 스토어·서비스",
    "국가",
    "통화",
    "시간대",
    "판매 채널",
    "문서 담당자",
    "버전",
    "최종 수정일",
]
DATE_PATTERN = r"\d{4}-\d{2}-\d{2}"


def _section_body(text: str, number: str, title: str) -> str:
    match = re.search(
        rf"^## {number}\. {re.escape(title)}\s*$\n(.*?)(?=^## \d+\. |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError("required policy sections are missing or out of order")
    return match.group(1).strip()


def validate_policy(text: str, *, allow_template: bool = False) -> None:
    if not re.search(r"^# .+ 정책 문서\s*$", text, flags=re.MULTILINE):
        raise ValueError("policy title is missing")
    headings = re.findall(r"^## ([1-8])\. (.+?)\s*$", text, flags=re.MULTILINE)
    if headings != REQUIRED_SECTIONS:
        raise ValueError("required policy sections are missing or out of order")
    for field in INFO_FIELDS:
        if not re.search(rf"^\| {re.escape(field)} \| .+ \|\s*$", text, flags=re.MULTILINE):
            raise ValueError(f"document information is missing: {field}")
    if allow_template:
        return
    if re.search(r"\{[^{}]+\}|YYYY-MM-DD|<!--", text):
        raise ValueError("unresolved template content remains")
    version = re.search(r"^\| 버전 \| (v\d+\.\d+) \|\s*$", text, flags=re.MULTILINE)
    if version is None:
        raise ValueError("document version must use vN.N")
    modified = re.search(rf"^\| 최종 수정일 \| ({DATE_PATTERN}) \|\s*$", text, flags=re.MULTILINE)
    if modified is None:
        raise ValueError("final modified date is invalid")
    for number, title in REQUIRED_SECTIONS:
        body = _section_body(text, number, title)
        review = re.search(rf"^최종 검토일: ({DATE_PATTERN})\s*$", body, flags=re.MULTILINE)
        if review is None:
            raise ValueError(f"section {number} review date is invalid")
        content = body[review.end():].strip()
        if content in {"현재 확정된 정책 없음", "적용 대상 아님"}:
            continue
        if not re.search(r"^### .+\s*$\n\s*\S", content, flags=re.MULTILINE):
            raise ValueError(f"section {number} policy content is invalid")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a completed LUKUKU policy Markdown file")
    parser.add_argument("policy", type=Path)
    parser.add_argument("--allow-template", action="store_true")
    args = parser.parse_args()
    try:
        validate_policy(args.policy.read_text(encoding="utf-8"), allow_template=args.allow_template)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("Policy Markdown validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
