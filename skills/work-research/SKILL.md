---
name: work-research
description: Investigate a Slack customer request against project history, Git, code, Shopify, and browser evidence, then draft a PM answer without posting it.
metadata:
  version: 0.1.2
  author: hak2881
  hermes:
    tags: [slack, shopify, code, fact-check, pm]
    platforms: [macos, linux]
license: MIT
---

# Work Research

Use the Slack permalink supplied after `/work-research` as the primary request. Produce a reviewable answer draft; never post it automatically.

Read [references/research-routing.md](references/research-routing.md) for source selection and [references/response-contract.md](references/response-contract.md) before answering.

## Workflow

1. Parse the workspace, channel, message timestamp, and thread timestamp from the permalink. Fetch the root and every reply. If the connected account cannot read it, report the exact access failure rather than guessing.
2. Identify the request, requested outcome, requester, customer, project, time constraints, and open questions. Separate quoted requirements from interpretation.
3. Query the `work_history` MCP for project context and related evidence. Validate that retrieved history is truly related using project identity, participants, linked sources, time, and subject. Exclude keyword-only matches.
4. If history coverage is missing, perform the smallest necessary `/work-history` style backfill for the resolved project before continuing.
5. Route each claim using [references/research-routing.md](references/research-routing.md). Inspect fresh sources for facts that may have changed.
6. Build a claim ledger. For each material sentence in the proposed answer, record supporting evidence, verification level, confidence, and conflicts.
7. Draft the response using [references/response-contract.md](references/response-contract.md). Include repository and SHA for code conclusions and observation time for browser/Admin conclusions.
8. Run a contradiction check: compare the draft against the original request, later thread replies, stored decisions, current code, and fresh platform evidence.
9. Return the draft and actions `1`, `2 <part>`, and `3`. Do not execute clipboard or external-post actions unless the host supports them and the user selects one.

## Re-review behavior

- `1`: copy only the PM response body when clipboard tooling is available; otherwise return a clean copy block.
- `2 <part>`: discard conclusions for the named part, collect fresh evidence for that part, and revise affected claims.
- `3`: independently repeat project resolution, history selection, source collection, and contradiction checking. Do not reuse confidence judgments from the first pass.
