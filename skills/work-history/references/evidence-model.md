# Evidence model

## Verification levels

- `slack`: complete Slack thread or message metadata was inspected.
- `official-docs`: current first-party documentation was inspected.
- `admin`: the connected Shopify Admin surface or Admin GraphQL response was inspected.
- `code`: current code at a recorded repository SHA was inspected.
- `execution`: behavior was reproduced in a controlled execution or browser session.
- `production`: behavior was observed in the actual production environment.

## Relationship confidence

- `explicit`: the source directly identifies the relationship, such as a Slack message linking a PR.
- `verified`: multiple independent attributes agree and no contradictory evidence was found.
- `inferred`: plausible from partial evidence and must be labeled as inference.
- `unresolved`: candidates remain and choosing one could change the result.

## Required provenance

Every evidence record needs a project, source type, stable URI or local identifier, title or concise claim, captured time, verification level, confidence, and optional excerpt. Store only the smallest excerpt needed for retrieval; keep the original source authoritative.

TODOs are stateful records. Store the current state plus the evidence that caused each change. Never interpret a code commit alone as `done`.

