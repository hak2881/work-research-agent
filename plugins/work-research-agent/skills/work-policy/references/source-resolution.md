# Policy source resolution

## Authority

Use a statement as policy only when its meaning and current applicability are supported by one of these sources:

1. A direct customer approval or decision in a complete Slack thread.
2. A customer-provided final policy document.
3. The current reviewed policy document when no later authoritative source supersedes it.
4. A PM record that cites the exact underlying customer agreement.

Customer silence is not agreement. A question, suggestion, acknowledgement, internal PM interpretation, developer recommendation, code path, Shopify setting, test result, or historical implementation does not establish policy.

## Conflicts

- Prefer a later explicit customer decision only when it addresses the same policy and clearly replaces the earlier one.
- Do not use timestamps alone to resolve statements with different scope, country, channel, customer type, or effective period.
- When the current decision cannot be distinguished, preserve the existing policy and return the conflict for PM confirmation.
- Current code and platform state may prove compliance or mismatch, but neither may rewrite the agreed policy.

## Coverage

Record the channels, threads, documents, versions, and checked-through times used for each changed area. Missing access makes that area partially verified. Do not write `현재 확정된 정책 없음` when the relevant source range was not actually reviewed.

