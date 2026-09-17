# Research routing

Choose sources by claim type and use the strongest available evidence.

| Claim | Required checks |
| --- | --- |
| What was requested or agreed | Complete Slack thread, linked messages/documents, later corrections |
| Whether current code supports it | Verified repository mapping, current checkout SHA, code path, Git history |
| Whether Shopify Admin supports it | Official Shopify documentation plus Admin GraphQL/schema or connected Admin observation |
| Whether a Shopify Function can implement it | Relevant Function API, target availability, input/output limits, deployment constraints, existing extensions |
| Which Shopify app fits | Current Shopify App Store listing, vendor docs, pricing/compatibility when relevant, Playwright inspection of the actual flow |
| Whether a UI flow works | Playwright reproduction with steps, observed result, timestamp, account/store context |
| Whether it is live | Production observation or deployment evidence; a merged commit is insufficient |

Use official documentation for platform capability. Use app/vendor sources for vendor-specific behavior and verify current UI claims with browser automation when access exists. If login, permissions, geography, plan, or test data prevents a check, state that limit.

For code, use CodeGraph before text search when the repository contains `.codegraph/`. If it is a Git repository without `.codegraph/` and the `codegraph` CLI is available, initialize it before code analysis. Confirm important paths directly in source and record the SHA.

