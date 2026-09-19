---
name: work-research
description: Investigate a Slack customer request against project history, Git, code, Shopify, and browser evidence, then draft a PM answer without posting it.
metadata:
  version: 0.5.0
  author: hak2881
license: MIT
---

# Work Research

Use one of these input forms:

- `$work-research 1 <Slack permalink>`: compare a recurrence-prevention answer with a current-request answer.
- `$work-research 2 <Slack permalink>`: answer from the customer's stated request and expected outcome.
- `$work-research <Slack permalink>`: default to mode 2 for backward compatibility.

The leading mode number is input syntax, not a post-result action. Produce reviewable drafts and never post them automatically.

Read [references/research-routing.md](references/research-routing.md) for source selection and [references/response-contract.md](references/response-contract.md) before answering.

## Workflow

1. Parse the optional leading mode, then parse the workspace, channel, message timestamp, and thread timestamp from the permalink. Reject an unknown mode instead of treating it as part of the URL. Fetch the root and every reply. If the connected account cannot read it, report the exact access failure rather than guessing.
2. Identify the request, requested outcome, requester, customer, project, time constraints, and open questions. Separate quoted requirements from interpretation.
3. Query the `work_history` MCP for project context and related evidence. Validate that retrieved history is truly related using project identity, participants, linked sources, time, and subject. Exclude keyword-only matches.
4. If history coverage is missing, backfill only the resolved project and relevant time range. Do not initiate another person-wide bootstrap.
5. Before using code as evidence, refresh every repository that can change the answer. Match the normalized repository mapping to one live verified remote, resolve its remote default branch, run `git fetch --prune <verified-remote>`, and use that same remote-tracking ref for every later check. Record the current branch, HEAD, upstream, and dirty state. Pull only when the worktree is clean, checked out on that remote default branch with an upstream from the same verified remote, and the local HEAD is an ancestor of the fetched remote-default SHA with no local-only commits. In that case, disable repository hooks for the command, run `git pull --ff-only`, verify that HEAD exactly equals the fetched remote-default SHA, and record that the ordinary checkout was updated. Otherwise leave the checkout untouched and inspect the exact fetched SHA in a detached temporary worktree at a unique temporary path. Verify the temporary worktree HEAD before inspection, then remove only that temporary worktree by its verified path, trying normal removal before a path-scoped forced removal when the created worktree is clean. Do not run global `git worktree prune`; if path-scoped cleanup fails, report the exact leftover path and registration without touching other worktrees. Never reset, clean, stash, merge, or rebase during research. Bind every code claim to the exact fetched SHA and record the verified remote, fetched default-branch SHA, inspected SHA, refresh method, and observation time.
6. Route each claim using [references/research-routing.md](references/research-routing.md). Inspect fresh sources for facts that may have changed. When an existing linked attachment, document, export, archive, or other file is already available through the current access and is needed to understand or verify the request, download it without asking for separate confirmation and inspect it according to the routing rules.
7. Build a claim ledger. For each material sentence in the proposed answer, record supporting evidence, verification level, confidence, and conflicts. Also separate the observed symptom, immediate cause, root cause, recurrence evidence, blast radius, and unresolved assumptions.
8. Treat a root cause as established only when it was directly reproduced or traced end-to-end through current code, data, configuration, or runtime evidence. A similar historical symptom is not root-cause evidence for the current request. Static proximity, shared keywords, and an older fix may guide investigation but cannot justify a causal claim or a broader change.
9. Decide whether code changes or developer confirmation are required, then draft the selected mode from [references/response-contract.md](references/response-contract.md). Include repository and SHA for code conclusions and observation time for browser/Admin conclusions.
10. Run a contradiction check: compare each draft against the original request, later thread replies, stored decisions, current code, and fresh platform evidence. In mode 1, verify that the two answers represent genuinely different evidence-backed scopes; do not manufacture a structural alternative.
11. Persist newly verified request, decision, implementation, verification, delivery, source-link, and explicit open-item evidence so the local history grows incrementally.
12. Return the draft and the word-based actions defined by the response contract. Do not execute clipboard or external-post actions unless the host supports them and the user selects one.

## Developer review and estimate boundary

When developer confirmation is required, provide one evidence-backed recommended approach rather than only forwarding the customer's question. Separate verified current behavior from the recommendation, explain why the approach is plausible, and ask the developer to verify implementation feasibility, affected areas, test conditions, and whether a better approach exists. The recommendation is not an approved design or permission to implement. When current evidence does not support a responsible candidate, set `권장 방안: 미정`, name the missing evidence or decision, and ask the developer to assess feasibility or propose a better approach without implying that an implementation is already possible.

Do not estimate effort in `$work-research`. Do not calculate, infer, validate, or repeat an estimate in hours, days, story points, cost, staffing, or delivery dates. When the request includes an estimate or schedule question, finish the factual research, state that development planning is required, and route the estimate request to `$dev-plan` with the same Slack link and verified context. Do not invoke `$dev-plan` automatically or promise a schedule in the customer-facing answer.

## Execution handoff

When the user wants to carry out a researched app setup or operational task, offer a `$work-act` handoff containing the requested outcome, project/store and target URLs, verified findings and observation times, unresolved developer checks, suggested configuration, acceptance checks, and anticipated live effects. Do not execute it from this research skill or treat the handoff as approval. `work-act` must revalidate current state and obtain final confirmation immediately before live or operationally consequential actions.

## Follow-up behavior

- `복사 A` or `복사 B`: in mode 1, copy only the selected PM response body when clipboard tooling is available; otherwise return a clean copy block.
- `답변 복사`: in mode 2, copy only the PM response body.
- `재검수 <부분>`: discard conclusions for the named part, collect fresh evidence for that part, and revise affected claims.
- `전체 재검수`: independently repeat project resolution, history selection, source collection, cause classification, and contradiction checking. Do not reuse confidence judgments from the first pass.
