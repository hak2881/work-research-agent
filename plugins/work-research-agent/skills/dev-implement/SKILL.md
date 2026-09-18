---
name: dev-implement
description: Use when a developer must implement one ready, evidence-backed work item while rechecking PRD, Slack, architecture, Git history, accepted criteria, and project history; starts backend work with b-start and stops before PR completion or deployment.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Dev Implement

Treat the content after `$dev-implement` as a project and work-item key. Implement only that accepted scope, preserve all decisions and verification in `work_history`, and stop before end, merge, or deploy workflows.

Read [references/implementation-contract.md](references/implementation-contract.md) before changing code.

## Revalidate the work item

1. Resolve the project and load the work item, document versions, events, dependencies, estimates, accepted acceptance criteria, architecture snapshots, repositories, and linked evidence from `history_project_context`.
2. Require state `ready`, completed prerequisites, and accepted acceptance criteria that are observable enough to determine success without inventing product policy. For retry work, retryable failure classes, duplicate-side-effect or idempotency behavior, bounded exhaustion, and terminal failure handling must each be accepted or explicitly excluded before implementation. Proposed criteria and a prior `ready` state are not approval of newly changed scope. If these conditions fail, record a blocker and return to `$dev-plan <work-item key>`.
3. Refresh every material source. Read the current PRD/WBS version and complete relevant Slack threads. Search after explicit per-source coverage checkpoints; without a checkpoint, search all accessible project-relevant history and record the checked-through range.
4. For every affected repository, verify its normalized remote, run `git fetch --prune`, and record the fetched default-branch SHA, current repository@SHA, branch/upstream, dirty state, and observation time. Use CodeGraph first to trace the affected path and impact when available.
5. Compare current sources and code with the accepted plan. A superseding requirement, conflicting architecture, missing access, or ambiguous SQS/EventBridge-like choice blocks implementation. Record the evidence and state transition instead of choosing an interpretation.

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

## Stop boundary

Transition the work item to `verification_pending` when the code and local verification are complete. This skill does not mark it `completed`; completion belongs to later review, merge, deployment, or acceptance evidence defined by the item.

Never invoke `$b-end`. Never invoke `$b-deploy`. Do not create or merge a PR, push, deploy, mutate AWS or Shopify, or claim production behavior. Return the Korean implementation report defined by the contract, including the exact remaining evidence needed for completion.
