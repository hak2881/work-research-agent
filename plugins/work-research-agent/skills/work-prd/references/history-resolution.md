# History resolution for PRDs

Use history to find the right sources and decisions, not to fill empty PRD fields by similarity.

## Authority and relevance

Evaluate each candidate claim by all of these dimensions:

1. Project identity: same customer, service, store, repository group, or explicitly linked project.
2. Scope identity: same feature, release, workflow, users, market, and operating condition.
3. Authority: an explicit customer or PM decision outranks discussion, suggestion, and implementation inference.
4. Time: a later decision can replace an earlier one only when it addresses the same scope.
5. Verification: current primary sources outrank stored summaries when the underlying fact can change.

Use an approved current PRD, explicit current Slack decision, or authoritative policy as a requirement source. Use current code, Admin, production, and browser observations to describe the as-is state or a constraint.

Current code proves current behavior; it does not prove requested future behavior. A commit proves a code change, not customer acceptance, deployment, or continuing product intent. Completed historical work does not become a requirement merely because it is related.

## Claim status

- `확정`: the current authoritative source explicitly defines the requirement, boundary, or acceptance result.
- `확인 필요`: the source mentions the need but leaves a decision-changing condition, actor, target, result, or boundary unresolved.
- `보류`: an authoritative source explicitly defers the item or excludes it from the current decision.

An agent proposal remains `확인 필요` and must be labeled as a proposal. Never promote it to `확정` to make the PRD look complete.

## Conflicts and supersession

When two sources conflict, preserve both in the internal ledger. Use a later source only when its authority and scope show that it superseded the earlier decision. Otherwise place the conflict in section 7.2 with the affected FR IDs, decision owner, and effect of leaving it unresolved.

Do not silently combine alternatives. Do not treat keyword-only matches, a similar past customer request, or a nearby code path as proof that histories belong to the same requirement.

## Scope selection

A Slack thread or bounded source document normally establishes the initial scope. A project-only invocation must identify a coherent requested outcome from history. If several unrelated or independently releasable outcomes remain, ask which one to document.

Record related but excluded history in section 3.2 only when it clarifies a real boundary. Omit unrelated history entirely.

## Freshness

Recheck mutable facts when they can change the PRD:

- Slack: full relevant thread and later explicit project decisions.
- Documents: current version, content hash, and approval state.
- Git: current remote default-branch SHA when current behavior or a technical constraint matters.
- Shopify, Admin, browser, AWS, or another platform: current state and observation time when the requirement depends on it.

If access is missing, state the exact missing evidence and use `확인 필요`; do not reconstruct the answer from older summaries.
