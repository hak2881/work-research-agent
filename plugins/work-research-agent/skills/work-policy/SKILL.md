---
name: work-policy
description: Use when a PM needs to create or revise a project policy Markdown document from customer-agreed Slack history, approved documents, or an existing policy file.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Work Policy

Create the current customer-agreed policy document without turning discussion, implementation, or silence into policy.

Accepted inputs:

- `$work-policy <Slack permalink>`
- `$work-policy <project>`
- `$work-policy <project> <policy area>`
- `$work-policy <existing policy.md path or URL>`

Read [references/source-resolution.md](references/source-resolution.md) before deciding whether a statement is policy. Read [references/policy-contract.md](references/policy-contract.md) before editing the bundled [LUKUKU policy template v1.0](references/lukuku-policy-template-v1.0.md).

## Workflow

1. Resolve one canonical project, customer, primary repository, policy lineage, and predecessor through `history_find_projects`, repository mappings, document records, and explicit source links. Do not merge policies from similarly named projects or customers.
2. Load `history_project_context`, including `policy_snapshots`, then read the complete supplied source and every material linked approval. For a project invocation, search all accessible project-relevant history; for a Slack invocation, revise only affected policies and preserve unrelated current policy text.
3. Build a policy ledger with statement, area, authority, source location, agreement time, effective date when explicit, predecessor policy key, and status. Apply `source-resolution.md`. Do not infer policy from current code, Shopify configuration, an internal proposal, historical implementation, customer silence, or an unanswered question.
4. Compare the newest authoritative agreement with the explicit predecessor. If sources conflict and the later customer decision is unclear, leave the current policy unchanged and return the exact decision needed.
5. Copy the bundled reference and materialize all eight standard areas in order. Include only current agreed policies. Use `현재 확정된 정책 없음` only after that area was actually reviewed, and `적용 대상 아님` only when an authoritative source excludes it. Remove authoring comments, examples, and placeholders.
6. Start a new lineage at `v0.1`. Increment a draft or reviewed version only after comparing the explicit predecessor. Never overwrite the immutable archive version. Do not use `v1.0` merely because sources are agreed; it also requires explicit review of the compiled document.
7. Write the immutable file below `~/.local/share/work-research-agent/policy/<project-slug>/<document-key>/<version>/policy.md`. Sanitize path segments and confirm the resolved path stays below the policy root. When one primary repository is unambiguous and local work is preserved, also update `docs/policy.md`; otherwise return the archive and ask which repository owns the canonical file. Never commit or push.
8. Validate the completed file with `python3 <skill-dir>/scripts/validate_policy.py <policy.md>`. Do not store or report an invalid document.
9. Record the file with `history_record_document` using `document_type=policy`, its immutable archive URI, version, and SHA-256. Atomically record all area and policy rows with `history_record_policy_snapshot`. Link each agreed or not-applicable policy key to authoritative evidence with `history_link_sources`.
10. Return the archive and canonical paths, version, changed policies, excluded candidates with reasons, evidence coverage, and PM decisions needed. Never post to Slack automatically.

## Boundaries

Do not create requirements, TODOs, work items, estimates, schedules, branches, product-code changes, commits, pull requests, Shopify changes, or AWS changes. A policy document records an agreement; it does not authorize implementation.

Current code or platform behavior may reveal a mismatch with policy. Report the mismatch separately and route requested product work to `$work-prd` or `$dev-plan`; do not rewrite policy to match the implementation.

