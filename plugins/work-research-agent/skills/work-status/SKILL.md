---
name: work-status
description: Report an evidence-backed project's current progress from local history plus targeted fresh Slack and Git checks, without implementing changes.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Work Status

Treat the content after `$work-status` as a project name or alias. Produce a current, evidence-backed status report. This is a read-only status workflow: do not edit code, operate Shopify, post messages, or execute proposed work.

Read [references/status-contract.md](references/status-contract.md) before reporting.

## Resolve the project

1. Call `history_find_projects` with the supplied project name or customer alias. Use `history_search` only to corroborate aliases, Slack references, and repository mappings that are not present in the project identity fields.
2. Select a project only when identity is explicit or corroborated by project participants, Slack channel context, repository links, customer/store identity, or existing source links. Exclude keyword-only matches. If multiple candidates could materially change the report, ask the user to choose.
3. If no project matches, return a blocked report with the searched name and available gap. Do not create a project, choose a keyword-only candidate, or guess a slug during status lookup.
4. Load the complete project context: evidence, explicit open items, repositories, commits, and source links. Record the last stored evidence time, explicit Slack coverage checkpoints per channel/source, and repository sync times separately. A stored Slack message is context, not proof that earlier channel history was searched completely.

## Refresh only what can change the status

1. Search each accessible relevant Slack source after its own explicit recorded coverage checkpoint. Never infer coverage from the newest stored Slack evidence. A newer Git, code, document, or browser observation must never advance a Slack checkpoint. When a Slack source has no explicit checkpoint, search the available project-relevant history and disclose the covered range. Read complete relevant threads rather than snippets. Capture later decisions, completion reports, cancellations, blockers, assignments, and customer acceptance.
2. For every mapped repository, verify its normalized remote and local path. Fetch remote refs with pruning without checking out, resetting, cleaning, merging, rebasing, or modifying a dirty worktree.
3. Record the working-tree HEAD, fetched default-branch SHA, dirty state, and observation time. Do not treat a local dirty checkout as deployed or shared state.
4. Inspect current code only when a status claim depends on implemented behavior. Use CodeGraph first when `.codegraph/` exists; initialize it for a Git repository without `.codegraph/` when the host instructions require that. Record the exact repository and SHA inspected.
5. Persist newly verified Slack, Git, code, decision, completion, blocker, and explicit open-item evidence through `work_history`. After each Slack source search, record separate coverage evidence containing the source/channel and checked-through range; do not represent an individual message as coverage. Do not duplicate existing evidence. Evidence-only writes to the local history DB are the sole allowed DB mutation in this read-only workflow. Git fetch may update repository metadata and objects, but must not change the working tree or operational state.

## Classify progress

- **Completed:** Require direct delivery, acceptance, deployment/production observation, or corroborated completion evidence appropriate to the request. A commit or merged PR alone proves a code change, not customer acceptance or production completion.
- **In progress:** Require an explicit active assignment, pending review, active branch/PR status with corroborated ownership and recency, or another sourced indication that work remains active. A recent commit or local dirty tree alone is `Unknown`, not in progress.
- **Blocked or needs confirmation:** Include unresolved decisions, missing access, failed verification, dependency waits, conflicting evidence, or developer/customer confirmation that changes the next action.
- **Unknown:** Use when no current source establishes the state. Do not silently infer a state from age, silence, branch names, or absent commits.

Do not invent a completion percentage. Show a ratio only when an authoritative PRD, milestone, or checklist provides both the full denominator and item states; label missing or disputed items. Never convert the count of Slack messages, commits, or repositories into progress.

## Boundaries and handoff

Return the Korean report defined in the status contract with source links, repository@SHA, observation times, and coverage gaps. Keep facts separate from inference.

If implementation or an external operational change is the next step, propose `$work-act` with the exact scoped item but do not invoke or execute it. If a customer-facing answer needs research, propose `$work-research <Slack link>`. Do not post the status report externally.
