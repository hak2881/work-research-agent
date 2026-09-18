---
name: dev-plan
description: Use when a developer must turn a PM request, PRD, WBS, Slack thread, or project document into an evidence-backed feasibility review, effort range, dependencies, acceptance criteria, and durable work items before implementation.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Dev Plan

Treat the content after `$dev-plan` as planning input, not permission to implement it. Produce an evidence-backed development plan and persist its sources and work items through `work_history`.

Read [references/planning-contract.md](references/planning-contract.md) before reporting.

## Establish the source and project

1. Read the complete supplied PRD, WBS, Slack thread, or document. Use the host's document, spreadsheet, Drive, or Slack capability appropriate to the source; do not plan from a search snippet.
2. Resolve the project through `history_find_projects`, source links, repositories, customer identity, and project history. Ask when multiple candidates would change the plan. Create a project only when the source explicitly establishes a new project identity.
3. Record each source with `history_record_document`, including a stable URI, source type, version, content hash, and capture time. Record explicit requirements, decisions, supplied estimates, and unresolved statements as evidence with their provenance.
4. Load `history_project_context`, then refresh material Slack decisions from each source's explicit coverage checkpoint. When a channel or source has no checkpoint, search all accessible project-relevant Slack history for that source. A stored message is not proof that later replies or channel history were checked. Read complete relevant threads and persist separate channel/source coverage evidence with the searched range and checked-through time. Treat an older Slack architecture decision and an unverified code hypothesis as a conflict to resolve, not a choice.
5. For every repository that can change feasibility or effort, verify the normalized remote, run `git fetch --prune`, and record the fetched default-branch SHA, inspected working-tree SHA, dirty state, and observation time. Do not reset, merge, rebase, clean, or treat an old local checkout as current. Inspect architecture-dependent behavior at the current repository@SHA and use CodeGraph first when available.

## Build the work plan

- Separate source statements from engineering interpretation. An actionable item stated by the source uses `origin="explicit"`. A useful decomposition invented during planning uses `origin="proposed"`, remains `planned`, and is labeled for PM or developer acceptance. Never turn a suggestion, discussion, or inferred concern into an accepted TODO.
- Set `ready` only when the scope, dependencies, acceptance criteria, and authority to start are explicit. The existence of a PRD or WBS does not mean work has started.
- Write observable acceptance criteria through `history_upsert_acceptance_criterion`. A criterion stated in an authoritative source is `origin="explicit"`; an engineering criterion added to make the work testable is `origin="proposed"` and `status="proposed"` until accepted. Do not mix both into an unlabeled list. For retries and asynchronous work, consider idempotency, bounded attempts, terminal failure handling, replay, observability, and controlled failure tests only when relevant; do not silently expand the requested product scope.
- Link directed prerequisites with `history_link_work_item_dependency`. A blocked architectural decision is a blocker, not an implicit dependency with a guessed resolution.
- Compare the request with current behavior, existing integrations, data ownership, security boundaries, AWS or Shopify constraints, and earlier decisions. Report feasibility as feasible, feasible with conditions, not currently feasible, or unverified.

## Estimate without false precision

- Preserve a PM or WBS estimate as supplied evidence and a separate `history_record_work_item_estimate` record with `estimate_basis="source"`. It is not an engineering commitment.
- Use a different estimate key and `estimate_basis="engineering"` for a newly derived range. Persist its minimum, maximum, unit, confidence, assumptions, exclusions, dependencies, inspected repository SHA, and included workstreams in that estimate record.
- When both estimates exist, store and show both as separate estimate records. Do not overwrite the supplied estimate with the engineering range or present two days and sixteen hours as independent confirmation.
- If unresolved architecture, scope, access, or policy would materially change the range, report the engineering estimate as `미산정` and name the decision required. Filling the report is never a reason to invent a range.
- Do not calculate project progress unless an authoritative denominator exists in an accepted PRD, milestone, or WBS. Proposed decomposition is not an authoritative denominator. Report uncertain and superseded items separately.

## Persist and stop

Use `history_upsert_work_item` for each persisted item and retain exact source evidence or links. Use `history_record_work_item_event` for acceptance, supersession, blockers, or later planning decisions. Mark replaced items `superseded`; do not delete their history.

Do not edit product code, create a development branch, invoke `$b-start`, operate Shopify, mutate AWS, merge, or deploy. Recommend `$dev-implement <work-item key>` only for items that are actually ready. If critical information is absent, return the smallest set of questions that changes feasibility, architecture, scope, or effort.
