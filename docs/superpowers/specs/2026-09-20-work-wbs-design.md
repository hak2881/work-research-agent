# Work WBS Skill Design

## Objective

Add a `$work-wbs` skill that turns an approved or reviewable project plan into a versioned LUKUKU-standard work breakdown schedule. The skill uses verified project history and accepted planning records, preserves uncertainty, and creates an editable XLSX plus a shareable PDF from one canonical manifest.

The intended sequence is:

```text
$work-prd -> $dev-plan -> $work-wbs -> $dev-implement
```

`$work-wbs` schedules and presents work. It does not replace feasibility review, invent an engineering plan, approve implementation, or start development.

## Supported inputs

- `$work-wbs <PRD path or URL>`
- `$work-wbs <Slack permalink>`
- `$work-wbs <project>`
- `$work-wbs <work-item key>`
- `$work-wbs <existing WBS path or URL>` for a revision

The skill resolves the canonical project through `history_find_projects`, source links, customer identity, and document or work-item lineage. A project-only invocation loads project history first. When multiple independently releasable scopes or WBS lineages exist, the skill asks the user to choose one instead of merging them.

## Source authority and planning boundary

The WBS may use:

1. Explicit current PM or customer decisions.
2. The selected PRD and its requirement states.
3. Work items, dependencies, acceptance criteria, and estimate records produced or verified by `$dev-plan`.
4. Explicit progress, assignment, schedule, and completion evidence.

Stored history is a discovery and continuity layer. Mutable facts are reopened when they affect the current WBS. An old task, estimate, owner, date, or status is not current merely because it exists in the database.

Work items with `origin="proposed"`, proposed acceptance criteria, unaccepted estimates, or unresolved scope remain visibly proposed. A PRD does not authorize the skill to invent engineering tasks, owners, dates, or effort. If no matching development plan exists, the skill returns the missing planning inputs and routes the user to `$dev-plan`.

The skill may calculate a proposed forecast only when the user explicitly requests scheduling and supplies the required start anchor, working calendar, capacity, dependency, and ownership assumptions. Generated dates use a `proposed` schedule basis and never replace an agreed baseline without an authoritative decision.

## LUKUKU WBS standard

The plugin ships a reusable implementation of LUKUKU WBS Template v1.1. The original reference PDF is not required at runtime. The generated PDF preserves this information architecture:

1. Cover and document identity.
2. Contents.
3. Document version and change history.
4. Overall schedule summary and phase Gantt.
5. Monthly calendars.
6. Current-week and next-week schedules.
7. Milestones and application rules.
8. Detailed work schedule and effort.
9. Prerequisites, completion criteria, requirement links, result evidence, and change notes.

The PDF uses landscape A4. Page count is data-dependent: monthly calendars and detailed work tables add pages only when needed.

The standard keeps these concepts separate:

- Baseline dates: the agreed original schedule, immutable after approval.
- Forecast dates: the latest expected schedule for incomplete work.
- Actual dates: explicitly observed execution dates.
- Estimated effort and actual accumulated effort.
- Missing effort and a verified zero value.
- Tasks and zero-effort milestones.
- In-scope work and unapproved or deferred scope.
- Sharing and approval.

## Canonical manifest

Every artifact is rendered from a validated `wbs-manifest.json`. The manifest is the reproducible document input, not a new authority source. It contains:

- Template version and document version.
- Document number, status, as-of date, project, customer, PM, and bounded scope.
- Predecessor document key and change-history entries.
- Scope inclusions, exclusions, and unresolved additions.
- Work items and milestones.
- Dependencies and prerequisites.
- Requirement, acceptance, source, and result-evidence references.
- Schedule and effort summary rules.

Each line item contains:

- Stable `TASK-NNN` or `MS-NNN` display ID and the durable work-item key.
- Type, title, phase, workstream, owner, and collaborators.
- Origin and WBS status.
- Baseline, forecast, and actual start and end dates.
- Schedule basis: `confirmed | planned | proposed | unknown`.
- Selected estimate record, estimate range and unit, actual effort and unit.
- Prerequisite work-item keys and non-work prerequisites.
- Completion criteria and their approval states.
- Requirement references, result evidence, change reason, and next action.

Display IDs are unique within one WBS lineage. Durable work-item keys remain the database identity and are never inferred solely from a display ID.

## Status rules

The WBS display statuses are:

- `예정`
- `진행 중`
- `확인 대기`
- `완료`
- `보류`

They are derived only from explicit work-item state and event evidence. `확인 대기` means external confirmation or verification is pending. `보류` requires an explicit deferral or hold; it is not a generic label for every blocker. Cancelled and superseded items do not appear as active schedule rows and remain available through document history.

An item is not shown as completed unless the completion and result evidence satisfy its accepted criteria. A merged commit or elapsed end date alone does not prove completion.

## Missing and uncertain values

The skill never fills unknown owners, dates, effort, status, or result evidence to complete the layout.

- Unknown values display as `미입력` or `미정`, according to the standard field meaning.
- A verified `0 MH` remains distinct from missing effort.
- Unscheduled work remains in the detailed WBS and in the attention list.
- Unscheduled work is omitted from Gantt and calendar placement with a visible exclusion note.
- Unapproved additions remain separate from the accepted baseline and are excluded from confirmed totals.
- Estimate ranges remain ranges. They are not collapsed into a single value.
- Different units are never summed without an explicit conversion rule.

## Outputs

The output root is:

```text
~/.local/share/work-research-agent/wbs/<project-slug>/<document-number>/<version>/
```

The project slug, document number, and version are sanitized to letters, numbers, `_`, `-`, and `.` as appropriate. Every resolved output path must remain inside the WBS root. Existing files are not overwritten.

The output directory contains:

```text
<project>-wbs.xlsx
<project>-wbs.pdf
wbs-manifest.json
```

The XLSX is the editable project artifact and contains:

- `기본정보`: document identity, scope, application and calculation rules.
- `WBS`: work items, milestones, assignments, three date sets, effort, state, prerequisites, completion, and evidence.
- `문서이력`: version changes, reasons, affected IDs, author, confirmation status, and source.

The PDF is rendered from the same manifest through bundled landscape HTML/CSS assets and a deterministic renderer. HTML is an internal rendering intermediate, not the primary PM artifact.

## Database additions

Reuse the existing project, document, evidence, source-link, work-item, dependency, estimate, acceptance, and event tables.

Add one versioned schedule table:

```text
work_item_schedule_snapshots
- id
- project_id
- wbs_document_key
- work_item_key
- display_id
- item_type
- owner
- collaborators_json
- wbs_status
- schedule_basis
- baseline_start
- baseline_end
- forecast_start
- forecast_end
- actual_start
- actual_end
- selected_estimate_key
- actual_effort
- actual_effort_unit
- change_note
- source_evidence_id
- captured_at
- UNIQUE(project_id, wbs_document_key, work_item_key)
```

Each WBS document version writes a new set of schedule snapshot rows. Updating a forecast creates a new WBS version and does not alter the earlier baseline snapshot. The WBS document itself is recorded through `history_record_document`, and source links connect the document and line items to PRD requirements, Slack decisions, work items, estimates, acceptance criteria, and evidence.

Add MCP tools for writing and reading a WBS schedule snapshot. The read path becomes part of `history_project_context` so `$work-status`, later `$work-wbs` revisions, and developer skills can compare the current plan with prior versions.

## Workflow

1. Resolve the project, bounded scope, and WBS lineage.
2. Read the complete input and record its version and content hash.
3. Load project context and locate the selected PRD, work items, dependencies, estimates, acceptance criteria, prior WBS versions, and progress events.
4. Refresh material mutable sources. Record the checked time and exact source version.
5. Verify that a matching development plan exists. If it does not, return the smallest missing-input list and `$dev-plan` handoff.
6. Build a claim and scheduling ledger that distinguishes explicit, verified, proposed, unresolved, and superseded values.
7. Select the baseline, forecast, and actual values without overwriting one category with another.
8. Build and validate the canonical manifest.
9. Persist the document record and versioned schedule snapshot.
10. Generate XLSX and PDF from the same manifest.
11. Cross-check XLSX, PDF, and manifest counts, totals, IDs, dates, and states.
12. Visually inspect every PDF page. Revise and rerender until all pages pass.
13. Return a PM review summary, clickable XLSX and PDF paths, source coverage, attention items, unresolved decisions, document status, and next step. Never post externally.

Persistence happens only after the complete manifest validates. If artifact generation fails after persistence, record the artifact failure as an event or evidence and return the manifest plus exact failure instead of claiming that the WBS was produced.

## Validation contract

The manifest and renderer reject:

- Duplicate display IDs or durable work-item keys.
- Missing referenced prerequisites.
- Self-dependencies or dependency cycles.
- End dates earlier than start dates.
- Actual dates or effort without an explicit source.
- `완료` without accepted completion criteria and result evidence.
- Milestones included in task-count or effort totals.
- Missing effort treated as zero.
- Incompatible effort units summed together.
- Unapproved additions included in confirmed scope or totals.
- Proposed dates presented as baseline or confirmed dates.
- Calendared work with unknown dates.
- Unsafe HTML, remote rendering assets, unresolved placeholders, or output path traversal.
- XLSX, manifest, and PDF summary values that do not match.

Overdue and dependency-risk indicators are derived warnings, not state changes. They do not rewrite source dates or statuses.

## Versioning

- A generated internal draft starts at `v0.1` with document status `초안`.
- The first explicitly approved sharing version is `v1.0`.
- Later shared revisions increment `v1.1`, `v1.2`, and so on.
- Template version `1.1` remains separate from the project document version.
- A new bounded scope receives a new document number and lineage.
- Every revision names its predecessor, affected IDs, change reason, author, and confirmation source.

Silence, file generation, or prior implementation does not approve a WBS.

## Integration with other skills

- `$work-prd` defines the requested product scope.
- `$dev-plan` verifies feasibility and creates sourced or proposed work items, dependencies, estimates, and acceptance criteria.
- `$work-wbs` creates and revises a schedule snapshot from those records.
- `$work-status` may compare later evidence with the newest WBS snapshot but does not silently rewrite it.
- `$dev-implement` still requires a ready work item and accepted criteria. A WBS row or schedule date is not implementation approval.

## Packaging

Add the skill to both source and packaged plugin trees. Bundle:

```text
skills/work-wbs/
|- SKILL.md
|- references/
|  |- wbs-contract.md
|  `- source-resolution.md
|- assets/
|  |- lukuku-wbs-template.html
|  `- lukuku-wbs-template.css
`- scripts/
   |- validate_wbs.py
   `- render_wbs.py
```

The renderer produces the PDF and XLSX from the manifest. Validation logic remains separate enough to test without Chrome.

## Test strategy

- Store tests for schedule snapshots, multiple WBS versions, lineage, and project-context retrieval.
- MCP tests for schedule snapshot read and write tools.
- Manifest tests for date ordering, dependency cycles, missing versus zero effort, range totals, milestone exclusion, and proposed schedule handling.
- XLSX tests for required sheets, rows, formulas or values, and document history.
- PDF renderer tests for section order, local assets, placeholder removal, and summary consistency.
- A representative fixture that renders monthly calendars, two weekly views, milestones, multi-page detail tables, and unscheduled work.
- Visual inspection of every rendered PDF page for Korean text, table overflow, calendar placement, Gantt clipping, and headers and footers.
- Distribution tests proving source and packaged skills match and new users receive every template and script.

## Non-goals

- Resource-capacity optimization.
- Timesheet collection.
- Billing or additional-charge calculation.
- Automatic Slack posting.
- Automatic implementation start, branch creation, deployment, or production mutation.
- Treating a schedule date as product, engineering, or deployment approval.
