# WBS source resolution

Use history to locate the plan and its evidence. Use current primary evidence for facts that can change.

## Authority

For product scope, prefer an approved current PRD or explicit current PM or customer decision. For engineering work, use reviewed work items, accepted criteria, explicit dependencies, and separately identified source or engineering estimates. For current progress, use explicit work-item events, review results, deployment or acceptance evidence, and verified work logs.

A commit proves a code change. It does not prove completion, deployment, customer acceptance, actual effort, or the correct WBS status. An elapsed forecast date does not prove that work started or finished.

## Identity and lineage

Require the same project, bounded outcome, requirement set, work-item group, and WBS document lineage. Similar titles and keyword matches do not join independent scopes.

Choose a predecessor through an explicit WBS document link, matching document number, or unambiguous bounded scope. Do not choose the highest project-wide version. A new scope receives a new document number and starts a new lineage.

## Freshness and supersession

Reopen relevant Slack threads, source documents, work-item events, estimates, and result evidence when they can change the WBS. A later source supersedes an earlier value only when it addresses the same field and scope with equal or greater authority.

Preserve conflicting evidence in the ledger. Put a decision-changing conflict in the attention and unresolved sections rather than silently choosing one. Exclude cancelled and superseded work from the active schedule while retaining its historical records.

## Missing plan

The skill requires reviewed work items, dependencies, acceptance criteria, and any effort that the WBS will display. If they do not exist, return:

- The bounded scope that was found.
- The exact planning records that are absent.
- The source that should be passed to `$dev-plan`.
- Any WBS fields that can already be confirmed without creating an artifact.

Do not create proposed developer tasks solely to make the WBS render.
