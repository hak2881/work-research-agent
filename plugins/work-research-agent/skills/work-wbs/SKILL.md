---
name: work-wbs
description: Use when a PM needs to create or revise a LUKUKU-standard project WBS, schedule, milestone plan, or XLSX/PDF delivery plan from verified PRD and development-plan history.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Work WBS

Create a versioned project schedule from verified plan records. The WBS presents agreed and unresolved work; it does not invent a development plan or authorize implementation.

Accepted inputs:

- `$work-wbs <PRD path or URL>`
- `$work-wbs <Slack permalink>`
- `$work-wbs <project>`
- `$work-wbs <work-item key>`
- `$work-wbs <existing WBS path or URL>`

Read [references/source-resolution.md](references/source-resolution.md) before selecting work and [references/wbs-contract.md](references/wbs-contract.md) before building the manifest.

## Workflow

1. Resolve the canonical project, bounded scope, WBS lineage, and predecessor through `history_find_projects`, document records, source links, customer identity, and work-item keys. For a project-only input, load `history_project_context` before asking the user to choose among independent active scopes.
2. Read the complete supplied source. Load the selected PRD, work items, dependencies, estimates, acceptance criteria, previous WBS versions, schedule snapshots, and progress events through `history_project_context`.
3. Refresh every mutable source that can change the current assignment, dates, status, actual effort, or completion result. History locates evidence; current primary evidence establishes current facts.
4. Require a matching development plan. When actionable work, dependencies, acceptance criteria, or engineering estimates have not been reviewed, return the missing inputs and route to `$dev-plan <source>`. Do not silently perform an abbreviated developer plan inside this skill.
5. Build a scheduling ledger that labels each value as explicit, verified, proposed, unresolved, or superseded. Never infer an owner, date, effort, status, result, or approval merely to complete the layout.
6. Use accepted baseline dates without changing them. Put later expected dates in forecast fields and directly observed execution dates in actual fields. Calculate proposed forecast dates only when the user explicitly requests scheduling and supplies the start anchor, working calendar, capacity, ownership, and dependency assumptions.
7. Build `wbs-manifest.json` according to `wbs-contract.md`. Unknown scheduled values remain `미정` or `미입력`; verified zero effort remains numeric zero. Unscheduled items stay in the detailed WBS and attention list but are not placed on calendars or the Gantt.
8. Resolve a safe versioned directory below `~/.local/share/work-research-agent/wbs/<project-slug>/<document-number>/<version>/`. Sanitize path segments and verify the resolved directory remains inside the WBS root. Never overwrite an existing version.
9. Validate the manifest with `python3 <skill-dir>/scripts/validate_wbs.py <manifest>`. Do not persist or render an invalid manifest.
10. Record the validated WBS with `history_record_document`, then atomically record its line items with `history_record_wbs_schedule_snapshot`. Namespace source links with the WBS document external key and durable work-item key, rather than the display-only `TASK-NNN` or `MS-NNN` ID.
11. Render with `uv run --no-project --with 'openpyxl>=3.1,<4' python <skill-dir>/scripts/render_wbs.py <manifest> <output-directory>`. This creates the editable XLSX and shareable PDF from the same manifest.
12. Cross-check manifest, XLSX, and PDF item IDs, counts, dates, states, and effort summaries. Render the PDF pages to images and inspect Korean text, calendars, Gantt placement, detailed tables, headers, footers, blank pages, and clipping. Revise and rerender until every PDF page passes.
13. Return PM review text, clickable XLSX and PDF paths, the as-of date, bounded scope, source coverage, attention items, unresolved decisions, and document status. Never post the files or message externally.

If persistence succeeds but artifact generation fails, record the exact artifact failure as evidence and return the validated manifest plus failure reason. Do not claim that an XLSX or PDF was created.

## Boundaries

A WBS row, date, or generated file is not approval to begin development. Do not edit product code, create a development branch, invoke `$dev-implement`, operate Shopify, mutate AWS, merge, deploy, or post to Slack.

Keep source estimates and engineering estimates distinct. Do not convert units without an explicit conversion rule, use actual effort as a progress percentage, or treat effort overrun as additional billing.

Cancelled and superseded work remains in history and is excluded from the active schedule unless the user explicitly requests a historical comparison.
