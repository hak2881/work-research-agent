#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "template_version",
    "document",
    "scope",
    "change_history",
    "items",
    "sources",
    "rendering",
}
ITEM_TYPES = {"task", "milestone"}
WBS_STATUSES = {"예정", "진행 중", "확인 대기", "완료", "보류"}
SCHEDULE_BASES = {"confirmed", "planned", "proposed", "unknown"}
ORIGINS = {"explicit", "proposed"}
CRITERION_STATUSES = {"proposed", "accepted", "rejected", "verified"}


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"WBS manifest not found: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid WBS manifest JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("WBS manifest must be a JSON object")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value.strip()


def _parse_date(value: Any, label: str) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date") from exc


def _validate_dates(item: dict[str, Any], source_keys: set[str]) -> None:
    dates = item.get("dates")
    if not isinstance(dates, dict):
        raise ValueError(f"{item['display_id']} dates are required")
    for category in ("baseline", "forecast", "actual"):
        period = dates.get(category)
        if not isinstance(period, dict):
            raise ValueError(f"{item['display_id']} {category} dates are required")
        start = _parse_date(period.get("start"), f"{item['display_id']} {category} start")
        end = _parse_date(period.get("end"), f"{item['display_id']} {category} end")
        source_ref = period.get("source_ref")
        if start is not None and end is not None and end < start:
            raise ValueError(f"{item['display_id']} {category} ends before it starts")
        if (start is not None or end is not None) and source_ref not in source_keys:
            raise ValueError(f"{item['display_id']} {category} dates require a source")
        if source_ref is not None and source_ref not in source_keys:
            raise ValueError(f"{item['display_id']} references unknown source: {source_ref}")


def _validate_dependencies(items: list[dict[str, Any]]) -> None:
    keys = {item["work_item_key"] for item in items}
    graph: dict[str, list[str]] = {}
    for item in items:
        dependencies = item.get("dependencies") or []
        if not isinstance(dependencies, list):
            raise ValueError(f"{item['display_id']} dependencies must be a list")
        for dependency in dependencies:
            if dependency not in keys:
                raise ValueError(f"{item['display_id']} references unknown dependency: {dependency}")
            if dependency == item["work_item_key"]:
                raise ValueError(f"{item['display_id']} cannot depend on itself")
        graph[item["work_item_key"]] = dependencies

    colors: dict[str, int] = {key: 0 for key in graph}

    def visit(key: str) -> None:
        if colors[key] == 1:
            raise ValueError("dependency cycle detected")
        if colors[key] == 2:
            return
        colors[key] = 1
        for dependency in graph[key]:
            visit(dependency)
        colors[key] = 2

    for key in graph:
        visit(key)


def validate_manifest(manifest: dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL - set(manifest)
    if missing:
        raise ValueError(f"missing WBS manifest field: {sorted(missing)[0]}")
    if manifest["template_version"] != "1.1":
        raise ValueError("unsupported WBS template version")
    document = manifest.get("document")
    if not isinstance(document, dict):
        raise ValueError("document must be an object")
    for field in (
        "number",
        "version",
        "status",
        "as_of_date",
        "project",
        "project_slug",
        "customer",
        "pm",
        "author",
    ):
        _require_text(document.get(field), f"document.{field}")
    _parse_date(document["as_of_date"], "document.as_of_date")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources require at least one entry")
    source_keys: set[str] = set()
    for source in sources:
        key = _require_text(source.get("key"), "source key")
        if key in source_keys:
            raise ValueError(f"duplicate source key: {key}")
        source_keys.add(key)
        for field in ("type", "uri", "version", "checked_at"):
            _require_text(source.get(field), f"source {key} {field}")

    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("items require at least one entry")
    work_item_keys: set[str] = set()
    display_ids: set[str] = set()
    for item in items:
        work_item_key = _require_text(item.get("work_item_key"), "work item key")
        display_id = _require_text(item.get("display_id"), "display ID")
        if work_item_key in work_item_keys:
            raise ValueError(f"duplicate work item key: {work_item_key}")
        if display_id in display_ids:
            raise ValueError(f"duplicate display ID: {display_id}")
        work_item_keys.add(work_item_key)
        display_ids.add(display_id)
        for field in ("title", "phase", "workstream"):
            _require_text(item.get(field), f"{display_id} {field}")
        if item.get("item_type") not in ITEM_TYPES:
            raise ValueError(f"invalid item type: {item.get('item_type')}")
        if item.get("wbs_status") not in WBS_STATUSES:
            raise ValueError(f"invalid WBS status: {item.get('wbs_status')}")
        if item.get("schedule_basis") not in SCHEDULE_BASES:
            raise ValueError(f"invalid schedule basis: {item.get('schedule_basis')}")
        if item.get("origin") not in ORIGINS:
            raise ValueError(f"invalid origin: {item.get('origin')}")
        if not isinstance(item.get("confirmed_scope"), bool):
            raise ValueError(f"{display_id} confirmed_scope must be boolean")
        _validate_dates(item, source_keys)

        estimate = item.get("estimate")
        if estimate is not None:
            minimum = estimate.get("min")
            maximum = estimate.get("max")
            if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)):
                raise ValueError(f"{display_id} estimate range must be numeric")
            if minimum < 0 or maximum < minimum:
                raise ValueError(f"{display_id} estimate range is invalid")
            _require_text(estimate.get("unit"), f"{display_id} estimate unit")
            if estimate.get("source_ref") not in source_keys:
                raise ValueError(f"{display_id} estimate requires a source")
            if item["item_type"] == "milestone" and (minimum != 0 or maximum != 0):
                raise ValueError(f"{display_id} milestone effort must be zero")
        elif item["item_type"] == "milestone":
            raise ValueError(f"{display_id} milestone effort must be zero")

        actual_effort = item.get("actual_effort")
        if actual_effort is not None:
            if not isinstance(actual_effort.get("value"), (int, float)):
                raise ValueError(f"{display_id} actual effort must be numeric")
            if actual_effort["value"] < 0:
                raise ValueError(f"{display_id} actual effort cannot be negative")
            _require_text(actual_effort.get("unit"), f"{display_id} actual effort unit")
            if actual_effort.get("source_ref") not in source_keys:
                raise ValueError(f"{display_id} actual effort requires a source")

        criteria = item.get("completion_criteria")
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f"{display_id} requires completion criteria")
        for criterion in criteria:
            _require_text(criterion.get("key"), f"{display_id} criterion key")
            _require_text(criterion.get("text"), f"{display_id} criterion text")
            if criterion.get("origin") not in ORIGINS:
                raise ValueError(f"{display_id} criterion origin is invalid")
            if criterion.get("status") not in CRITERION_STATUSES:
                raise ValueError(f"{display_id} criterion status is invalid")

        result_evidence = item.get("result_evidence") or []
        for source_ref in result_evidence:
            if source_ref not in source_keys:
                raise ValueError(f"{display_id} references unknown result evidence: {source_ref}")
        if item["wbs_status"] == "완료":
            if not result_evidence:
                raise ValueError(f"{display_id} completed item requires result evidence")
            if not any(c["status"] in {"accepted", "verified"} for c in criteria):
                raise ValueError(f"{display_id} completed item requires accepted criteria")
        if item["schedule_basis"] == "proposed" and item["confirmed_scope"]:
            raise ValueError(f"{display_id} proposed schedule cannot be confirmed scope")

    _validate_dependencies(items)

    for change in manifest.get("change_history") or []:
        if change.get("source_ref") not in source_keys:
            raise ValueError("change history requires a valid source")


def summarize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    validate_manifest(manifest)
    confirmed = [item for item in manifest["items"] if item["confirmed_scope"]]
    tasks = [item for item in confirmed if item["item_type"] == "task"]
    milestones = [item for item in confirmed if item["item_type"] == "milestone"]
    estimated: dict[str, dict[str, float]] = defaultdict(lambda: {"min": 0, "max": 0})
    actual: dict[str, float] = defaultdict(float)
    missing_estimate = 0
    missing_actual = 0
    for item in tasks:
        estimate = item.get("estimate")
        if estimate is None:
            missing_estimate += 1
        else:
            estimated[estimate["unit"]]["min"] += estimate["min"]
            estimated[estimate["unit"]]["max"] += estimate["max"]
        actual_effort = item.get("actual_effort")
        if actual_effort is None:
            missing_actual += 1
        else:
            actual[actual_effort["unit"]] += actual_effort["value"]

    unscheduled = []
    for item in manifest["items"]:
        periods = item["dates"]
        if not any(
            periods[name].get("start") or periods[name].get("end")
            for name in ("baseline", "forecast", "actual")
        ):
            unscheduled.append(item["display_id"])
    return {
        "task_count": len(tasks),
        "milestone_count": len(milestones),
        "status_counts": dict(Counter(item["wbs_status"] for item in confirmed)),
        "estimated_effort": dict(estimated),
        "actual_effort": dict(actual),
        "missing_estimate_count": missing_estimate,
        "missing_actual_count": missing_actual,
        "unresolved_count": sum(not item["confirmed_scope"] for item in manifest["items"]),
        "unscheduled_ids": sorted(unscheduled),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a LUKUKU WBS manifest")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        validate_manifest(load_manifest(args.manifest))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("WBS manifest validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
