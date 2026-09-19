# Work Policy Design

## Goal

Add `$work-policy` to create and revise a project `policy.md` from customer-agreed evidence while preserving every document version and policy entry in local history.

## Decisions

- Bundle the supplied LUKUKU policy Markdown v1.0 under `skills/work-policy/references/`; new users do not need the Downloads file.
- Produce Markdown only. Do not add HTML or PDF rendering.
- Include only current policies backed by explicit customer agreement or an already approved policy document. Questions, proposals, current code behavior, silence, schedules, estimates, and TODOs are not policy.
- Store an immutable versioned copy below `~/.local/share/work-research-agent/policy/<project>/<document-key>/<version>/policy.md`.
- Update `<primary-repository>/docs/policy.md` only when one primary repository is unambiguous and the working tree can be preserved. Never commit, push, or post externally.
- Record the document through `history_record_document`, each policy version through an atomic `history_record_policy_snapshot`, and each policy-to-source relationship through `history_link_sources`.
- Keep the standard eight areas in order. Additional areas may follow as section 9 and above.
- Preserve unchanged current policies verbatim during a scoped revision. Ambiguous conflicts block the affected policy update.

## History model

Each policy snapshot row belongs to one `project_documents` record whose `document_type` is `policy`. A stable internal policy key connects the same policy across document versions. Rows record area, title, body, state, effective date, review date, and authoritative evidence. Document versions are immutable once policy rows exist.

Policy states are `agreed`, `no_confirmed_policy`, and `not_applicable`. An agreed policy and an explicit not-applicable decision require authoritative evidence. `no_confirmed_policy` means the area was reviewed and no agreed policy was found; it is not a claim that no future policy exists.

## Standard and validation

The bundled reference remains an authoring template. A completed policy document must contain document information, change history, all eight required areas in order, a real review date for every area, and no placeholder tokens or authoring comments. Each area contains agreed `###` policy entries, `현재 확정된 정책 없음`, or `적용 대상 아님`.

## Integration boundary

`work-research`, `work-prd`, `dev-plan`, and `dev-implement` consult the newest policy snapshot when policy affects an answer or implementation. They still reopen the authoritative source when a new request may change policy. `$work-policy` does not create requirements, work items, estimates, code changes, commits, or Slack replies.

