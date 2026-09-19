---
name: dev-implement
description: Use when a developer must implement one ready, evidence-backed work item from a work-item key or Slack permalink while rechecking PRD, Slack, architecture, Git history, accepted criteria, and project history; starts backend work with b-start and stops before PR completion or deployment.
metadata:
  version: 0.2.0
  author: hak2881
license: MIT
---

# Dev Implement

Treat the content after `$dev-implement` as a work-item key or Slack permalink. Implement only one resolved and accepted scope, preserve all decisions and verification in `work_history`, and stop before end, merge, or deploy workflows.

Read [references/implementation-contract.md](references/implementation-contract.md) and the shared [../dev-plan/references/report-quality.md](../dev-plan/references/report-quality.md) before changing code or reporting results.

## Resolve a Slack request

When the input is a Slack permalink:

1. Parse its workspace, channel, message timestamp, and thread timestamp. Fetch the root and every reply, preserving authors, timestamps, permalinks, edits, and reply order. If the connected account cannot read the message or complete thread, block instead of planning from a snippet.
2. Resolve the project from the thread's customer/store identity, channel context, repository or PR links, participants, and existing project source links. A shared keyword is not enough.
3. Find work items connected to the root, replies, or thread through exact evidence URIs and `source_links`. Corroborate title similarity with source identity and accepted document versions; never select an item from semantic similarity alone.
4. Continue directly only when the thread resolves to exactly one `ready` work item. When multiple material candidates remain, return the candidates and ask which scope applies without editing code.
5. Before creating a work item, audit every same-project work item and current open PR for overlapping outcome, affected system or repository, acceptance criteria, and source versions. If a material candidate lacks an exact source link, do not auto-create or auto-link. Resolve it from evidence or ask the user to choose whether to reuse and link it, supersede or replace it with an event, or create a distinct item with an explicit non-overlap reason.
6. When no exact or overlapping work item exists, read the bundled planning workflow at [../dev-plan/SKILL.md](../dev-plan/SKILL.md) and its contract, then perform that planning workflow in the same invocation. Persist the Slack source, requirements, estimates, dependencies, acceptance criteria, and created work items. A new item becomes `ready` only when the thread or another authoritative source explicitly establishes the full scope, observable accepted criteria, resolved dependencies, and authority to start; otherwise return the plan or required questions and stop.
7. After planning or overlap resolution, continue only if it produced exactly one `ready` work item for this thread. Link the thread root and material replies to that item with `history_link_sources` so a repeated invocation resolves the same scope without duplicating it.

Do not post, reply, react, or change anything in Slack. The thread is an input and evidence source only.

## Revalidate the work item

1. Resolve the project and load the work item, document versions, current policy snapshots, events, dependencies, estimates, accepted acceptance criteria, architecture snapshots, repositories, and linked evidence from `history_project_context`.
2. Require state `ready`, completed prerequisites, and accepted acceptance criteria that are observable enough to determine success without inventing product policy. For retry work, retryable failure classes, duplicate-side-effect or idempotency behavior, bounded exhaustion, and terminal failure handling must each be accepted or explicitly excluded before implementation. Proposed criteria and a prior `ready` state are not approval of newly changed scope. If these conditions fail, record a blocker and return to `$dev-plan <work-item key>`.
3. Refresh every material source. Read the current PRD/WBS version and complete relevant Slack threads. Search after explicit per-source coverage checkpoints; without a checkpoint, search all accessible project-relevant history and record the checked-through range.
4. For every affected repository, verify its normalized remote, run `git fetch --prune`, and record the fetched default-branch SHA, current repository@SHA, branch/upstream, dirty state, and observation time. Use CodeGraph first to trace the affected path and impact when available.
5. Compare current sources, agreed policy, and code with the accepted plan. A superseding requirement, policy conflict, conflicting architecture, missing access, or ambiguous SQS/EventBridge-like choice blocks implementation. Record the evidence and state transition instead of choosing an interpretation.

Treat a planning HTML report as a derived navigation artifact, not an authoritative source. Use it to locate decisions and evidence, then recheck the accepted original document versions, Slack decisions, criteria, and current code before editing. If the report conflicts with an original source or omits a decision that changes implementation, return to `$dev-plan` instead of silently following the report.

## Start safely

- Determine the affected repository and workstream from evidence. For backend work, Invoke `$b-start` only after the preflight above succeeds. If `$b-start` is unavailable, stop before editing.
- Do not run `$b-start` in a checkout containing unrelated dirty work. Trace every pre-existing dirty path and hunk to this work item through a recorded work-item event, session, commit, or source. File proximity is not evidence of ownership. If any hunk is ambiguous, block or use a verified clean isolated worktree without carrying that hunk forward. Preserve the original checkout; never reset, clean, stash, overwrite, or combine unrelated dirty work to make the preflight pass.
- After `$b-start`, record an `implementation_started` event with the work-item key, branch, starting SHA, accepted document versions, and architecture snapshot. Transition to `in_progress` only at this point.
- If the selected workstream is not backend, do not substitute `$f-start` or another lifecycle skill without an explicit project rule. Report the missing start workflow before editing.

## Implement against the accepted contract

1. Write a focused test that fails for the missing accepted behavior and observe the expected failure before product code. Existing green tests are only the pre-change baseline.
2. Make the smallest code change that satisfies the accepted criteria and current architecture. Do not implement proposed criteria, adjacent cleanup, speculative infrastructure, or unrelated refactors.
3. Run the focused test, affected tests selected from CodeGraph or actual dependencies, and meaningful integration or failure-path checks. Record expected and observed results at the exact SHA.
4. Inspect the final diff against the PRD, later Slack decisions, architecture snapshot, accepted criteria, and exclusions. Run an independent contradiction check: no criterion may be credited from a commit message, passing test, or code presence alone when it requires runtime or production evidence.
5. Persist decisions, implementation events, commit/file metadata, test evidence, discovered blockers, and criterion verification through `work_history`. A persistence failure must be reported; it is not a reason to repeat a code mutation.

## Report proportionally

Use the shared report-quality standard for the final implementation result. Keep the normal result inline and concise. Create a self-contained HTML report under the same safe reports directory only when a multi-component flow, data mapping, migration, decision matrix, or substantial criterion evidence cannot remain clear inline. Do not create HTML because many files changed or because the task took a long time. When HTML is justified, put the decision and implementation status in the session, place the complete implementation contract in the HTML, apply the dev-plan HTML safety and visual-verification rules, and record the route trigger. Persist the generated report URI, content hash, checked time, work-item key, and final repository SHA as a derived artifact linked to the implementation event; the original sources and accepted criteria remain authoritative. If artifact creation, persistence, or visual verification fails, report the failure and provide the complete result inline.

## Stop boundary

Transition the work item to `verification_pending` when the code and local verification are complete. This skill does not mark it `completed`; completion belongs to later review, merge, deployment, or acceptance evidence defined by the item.

Never invoke `$b-end`. Never invoke `$b-deploy`. Do not create or merge a PR, push, deploy, mutate AWS or Shopify, or claim production behavior. Return the Korean implementation report defined by the contract, including the exact remaining evidence needed for completion.
