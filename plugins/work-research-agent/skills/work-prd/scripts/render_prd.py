#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path


REQUIRED_SECTIONS = {
    str(number): title
    for number, title in enumerate(
        (
            "문서 정보",
            "배경과 목표",
            "포함·제외 범위",
            "사용자와 주요 업무 흐름",
            "기능 요구사항",
            "품질·제약 조건",
            "선행 조건·미확정 사항",
            "전체 인수 기준·관련 문서",
        ),
        start=1,
    )
}

REQUIRED_FIELDS = {
    "project",
    "customer",
    "author",
    "version",
    "date",
    "status",
    "scope",
    "document-number",
}
REQUIRED_ROW_GROUPS = (
    "change-history",
    "goals",
    "in-scope",
    "roles",
    "flows",
    "functional-requirements",
    "acceptance",
    "related-documents",
)
REQUIRED_ROW_COLUMNS = {
    "change-history": 4,
    "goals": 3,
    "in-scope": 2,
    "roles": 3,
    "flows": 4,
    "functional-requirements": 5,
    "acceptance": 3,
    "related-documents": 4,
}
BLOCKED_TAGS = {"embed", "iframe", "object", "script"}


class PRDContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fields: dict[str, str] = {}
        self.rows: dict[str, list[list[str]]] = {}
        self._field_name: str | None = None
        self._field_tag: str | None = None
        self._field_text: list[str] = []
        self._row_group: str | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.unsafe_reason: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag.lower() in BLOCKED_TAGS:
            self.unsafe_reason = f"blocked HTML tag: {tag}"
        for name, value in attrs:
            lowered_name = name.lower()
            lowered_value = (value or "").strip().lower()
            if lowered_name.startswith("on"):
                self.unsafe_reason = f"blocked HTML event attribute: {name}"
            if lowered_name in {"href", "src", "xlink:href"} and lowered_value.startswith(
                ("data:", "javascript:", "vbscript:")
            ):
                self.unsafe_reason = f"blocked active URL in attribute: {name}"
            if tag.lower() in {"audio", "img", "source", "video"} and lowered_name == "src":
                if "://" in lowered_value or lowered_value.startswith("//"):
                    self.unsafe_reason = f"blocked remote media source: {value}"
        field_name = attributes.get("data-prd-field")
        if field_name:
            self._field_name = field_name
            self._field_tag = tag
            self._field_text = []
        row_group = attributes.get("data-prd-rows")
        if tag == "tbody" and row_group:
            self._row_group = row_group
            self.rows.setdefault(row_group, [])
        elif tag == "tr" and self._row_group:
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._field_name is not None:
            self._field_text.append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._field_name is not None and tag == self._field_tag:
            self.fields[self._field_name] = " ".join(self._field_text).strip()
            self._field_name = None
            self._field_tag = None
            self._field_text = []
        if tag == "td" and self._cell is not None and self._row is not None:
            self._row.append(" ".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None and self._row_group is not None:
            self.rows[self._row_group].append(self._row)
            self._row = None
        elif tag == "tbody":
            self._row_group = None


def validate_required_content(text: str) -> None:
    parser = PRDContentParser()
    parser.feed(text)
    if parser.unsafe_reason:
        raise ValueError(parser.unsafe_reason)
    for field in sorted(REQUIRED_FIELDS):
        if not parser.fields.get(field, "").strip():
            raise ValueError(f"required PRD field is empty: {field}")
    for row_group in REQUIRED_ROW_GROUPS:
        if not parser.rows.get(row_group):
            raise ValueError(f"{row_group} requires at least one row")
        minimum_columns = REQUIRED_ROW_COLUMNS[row_group]
        for row in parser.rows[row_group]:
            if len(row) < minimum_columns or any(not value for value in row[:minimum_columns]):
                raise ValueError(f"{row_group} contains an incomplete row")
    for row in parser.rows["functional-requirements"]:
        if not re.fullmatch(r"FR-\d{3}", row[0]):
            raise ValueError(f"invalid functional requirement ID: {row[0]}")
        if row[3] not in {"확정", "확인 필요", "보류"}:
            raise ValueError(f"invalid functional requirement state: {row[3]}")
        if not row[4]:
            raise ValueError(f"functional requirement completion criterion is empty: {row[0]}")


def validate_prd_html(path: Path, *, allow_placeholders: bool = False) -> None:
    if not path.is_file():
        raise ValueError(f"PRD HTML not found: {path}")
    text = path.read_text(encoding="utf-8")
    if '<html lang="ko"' not in text:
        raise ValueError("PRD HTML must declare lang=ko")
    section_positions: list[int] = []
    for section_id, title in REQUIRED_SECTIONS.items():
        marker = f'data-prd-section="{section_id}"'
        if text.count(marker) != 1:
            raise ValueError(f"PRD section {section_id} marker must appear exactly once")
        section_positions.append(text.index(marker))
        if title not in text:
            raise ValueError(f"PRD section {section_id} title is missing: {title}")
    if section_positions != sorted(section_positions):
        raise ValueError("PRD sections must appear in order from 1 through 8")
    if "LUKUKU-PRD-TEMPLATE-04" not in text:
        raise ValueError("LUKUKU template identifier is missing")
    if "<script" in text.lower():
        raise ValueError("PRD HTML must not contain scripts")
    if not allow_placeholders and re.search(r"\{\{[^{}]+\}\}", text):
        raise ValueError("PRD HTML contains unresolved template placeholders")
    stylesheet_matches = re.findall(
        r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
        text,
        flags=re.IGNORECASE,
    )
    if len(stylesheet_matches) != 1:
        raise ValueError("PRD HTML must link exactly one stylesheet")
    stylesheet_ref = stylesheet_matches[0]
    if "://" in stylesheet_ref or stylesheet_ref.startswith("//"):
        raise ValueError("PRD stylesheet must be a local file")
    if not (path.parent / stylesheet_ref).is_file():
        raise ValueError(f"PRD stylesheet not found: {stylesheet_ref}")
    if not allow_placeholders:
        validate_required_content(text)


def find_browser() -> str | None:
    configured = os.environ.get("WORK_PRD_BROWSER")
    candidates = [
        configured,
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    validate_prd_html(html_path)
    if pdf_path.exists():
        raise ValueError(f"refusing to overwrite existing PDF: {pdf_path}")
    browser = find_browser()
    if browser is None:
        raise RuntimeError(
            "Chrome or Chromium was not found. Keep the validated HTML or set "
            "WORK_PRD_BROWSER to a browser executable before rendering the PDF."
        )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="work-prd-chrome-") as profile:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--allow-file-access-from-files",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        with tempfile.TemporaryFile(mode="w+") as browser_log:
            process = subprocess.Popen(
                command,
                stdout=browser_log,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            deadline = time.monotonic() + 30
            previous_size = -1
            stable_checks = 0
            while time.monotonic() < deadline:
                if pdf_path.is_file():
                    current_size = pdf_path.stat().st_size
                    stable_checks = stable_checks + 1 if current_size == previous_size else 0
                    previous_size = current_size
                    if current_size > 0 and stable_checks >= 2:
                        break
                if process.poll() is not None:
                    break
                time.sleep(0.1)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=3)
            browser_log.seek(0)
            detail = browser_log.read().strip()
    if not pdf_path.is_file():
        pdf_path.unlink(missing_ok=True)
        detail = detail or "no PDF was produced before the 30-second timeout"
        raise RuntimeError(f"Chrome PDF rendering failed: {detail}")
    if not pdf_path.read_bytes().startswith(b"%PDF"):
        pdf_path.unlink(missing_ok=True)
        raise RuntimeError("Chrome output is not a PDF")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render a LUKUKU PRD HTML file")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="validate the bundled blank template; never use for a completed PRD",
    )
    parser.add_argument("html", type=Path)
    parser.add_argument("pdf", type=Path, nargs="?")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.allow_placeholders and not args.validate_only:
            raise ValueError("--allow-placeholders can only be used with --validate-only")
        validate_prd_html(args.html, allow_placeholders=args.allow_placeholders)
        if args.validate_only:
            print("PRD HTML validation passed")
            return 0
        if args.pdf is None:
            raise ValueError("PDF output path is required unless --validate-only is used")
        render_pdf(args.html, args.pdf)
    except (OSError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"PRD PDF created: {args.pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
