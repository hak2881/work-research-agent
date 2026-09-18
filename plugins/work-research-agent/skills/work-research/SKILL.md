---
name: work-research
description: Investigate a Slack customer request against project history, Git, code, Shopify, and browser evidence, then draft a PM answer without posting it.
metadata:
  version: 0.4.1
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
5. Route each claim using [references/research-routing.md](references/research-routing.md). Inspect fresh sources for facts that may have changed. When an existing linked attachment, document, export, archive, or other file is already available through the current access and is needed to understand or verify the request, download it without asking for separate confirmation and inspect it according to the routing rules.
6. Build a claim ledger. For each material sentence in the proposed answer, record supporting evidence, verification level, confidence, and conflicts. Also separate the observed symptom, immediate cause, root cause, recurrence evidence, blast radius, and unresolved assumptions.
7. Treat a root cause as established only when it was directly reproduced or traced end-to-end through current code, data, configuration, or runtime evidence. A similar historical symptom is not root-cause evidence for the current request. Static proximity, shared keywords, and an older fix may guide investigation but cannot justify a causal claim or a broader change.
8. Decide whether code changes or developer confirmation are required, then draft the selected mode from [references/response-contract.md](references/response-contract.md). Include repository and SHA for code conclusions and observation time for browser/Admin conclusions.
9. Run a contradiction check: compare each draft against the original request, later thread replies, stored decisions, current code, and fresh platform evidence. In mode 1, verify that the two answers represent genuinely different evidence-backed scopes; do not manufacture a structural alternative.
10. Persist newly verified request, decision, implementation, verification, delivery, source-link, and explicit open-item evidence so the local history grows incrementally.
11. Return the draft and the word-based actions defined by the response contract. Do not execute clipboard or external-post actions unless the host supports them and the user selects one.

## Execution handoff

When the user wants to carry out a researched app setup or operational task, offer a `$work-act` handoff containing the requested outcome, project/store and target URLs, verified findings and observation times, unresolved developer checks, suggested configuration, acceptance checks, and anticipated live effects. Do not execute it from this research skill or treat the handoff as approval. `work-act` must revalidate current state and obtain final confirmation immediately before live or operationally consequential actions.

## Follow-up behavior

- `복사 A` or `복사 B`: in mode 1, copy only the selected PM response body when clipboard tooling is available; otherwise return a clean copy block.
- `답변 복사`: in mode 2, copy only the PM response body.
- `재검수 <부분>`: discard conclusions for the named part, collect fresh evidence for that part, and revise affected claims.
- `전체 재검수`: independently repeat project resolution, history selection, source collection, cause classification, and contradiction checking. Do not reuse confidence judgments from the first pass.
