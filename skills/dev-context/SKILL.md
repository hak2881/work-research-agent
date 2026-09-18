---
name: dev-context
description: Use when a developer needs an evidence-backed map of a project's current code, AWS, Shopify, data and runtime architecture, delivery progress, risks, and next ready work before starting development.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Dev Context

Treat the content after `$dev-context` as a project name or alias. Build a current technical context for development: architecture, infrastructure, repository and PR state, work progress, and the next item that is truly ready. This workflow is read-only except for evidence and snapshot records in the local history DB.

Read [references/context-contract.md](references/context-contract.md) before reporting.

## Resolve and refresh the project

1. Resolve the project with `history_find_projects` and corroborate it using customer, Slack, repository, store, and source links. Load documents, evidence, work items, events, dependencies, architecture snapshots, repositories, commits, and links through `history_project_context`.
2. Treat stored history as an index, not proof of current state. Refresh material Slack decisions from explicit per-source coverage checkpoints; without one, search all accessible project-relevant history and save the checked-through range.
3. Inspect every mapped repository. Verify its normalized remote, run `git fetch --prune`, and record the fetched default-branch SHA, inspected repository@SHA, branch/upstream, dirty state, observation time, role, and access failure. Do not omit a repository because its role is unclear.
4. Enumerate current open PRs from the Git host for every mapped remote. Record head/base SHA, state, reviews, CI, conflicts, merge evidence, deployment evidence, and checked time. If enumeration is unavailable, mark that repository's PR coverage unavailable and do not select a next-ready item while duplicate-work risk remains. An open or merged PR does not by itself prove deployment, acceptance, or completion.
5. Use CodeGraph first for current code relationships when available. Trace entrypoints, cross-repository calls, data ownership, queues/events, scheduled work, Shopify surfaces, external integrations, and failure paths. Cite the exact repository@SHA for each code conclusion.

## Separate architecture states

Keep desired, configured, deployed, and live architecture distinct:

- PRD and architecture notes show desired intent at their recorded version.
- Terraform, CDK, CloudFormation, application config, and environment-variable names show declared or configured references only.
- Deployment records show what a release mechanism reports as deployed.
- Read-only AWS, Shopify, and runtime observations show live state at an account, region/store, and checked time.

Partial IaC, old diagrams, naming conventions, local defaults, code presence, and environment resource names never prove a live resource or edge. Record conflicts and supersession instead of merging these states into one apparently current diagram. Never expose credentials, tokens, customer data, or secret values read from configuration.

## Verify AWS and Shopify

- When AWS access exists, identify the AWS account, region, principal, and checked time before inventory. Corroborate the observed account ID and each region against an authoritative project mapping, deployment configuration, or explicit source link before treating resources as this project's live state. Enumerate every project-configured or referenced region and relevant global service, or list it as unchecked. A precise observation from an unmatched active profile is unrelated or unverified evidence. Inspect only relevant resources and relationships: VPCs, subnets, route tables, NAT/Internet gateways, security groups, compute, load balancers, API gateways, Lambda/ECS/EKS/EC2, RDS/DynamoDB/ElastiCache, S3/CloudFront/Route 53, SQS/SNS/EventBridge, logs, alarms, and deployment surfaces as applicable.
- For IAM conclusions, inspect role trust, identity policies, resource policies, conditions, permission boundaries, cross-account assumptions, and disclose unknown SCP effects when relevant. An attached action policy alone does not prove effective access.
- When live access is unavailable, show configured or inferred resources with their evidence level. Do not invent account IDs, regions, CIDRs, routes, policies, or resource status.
- For Shopify, record the observed shop domain/store ID and app/client identity and match both to the resolved project before treating Admin state as current. A signed-in but unmatched store or app is unrelated or unverified evidence. Distinguish app code and configuration from current Admin registration, active webhook subscriptions, Function deployment, app embed/theme activation, and observed delivery or storefront behavior. Use read-only Admin, CLI, API, or browser evidence when accessible.

## Draw evidence-keyed diagrams

Produce the diagrams needed to explain the verified system, normally a system flow and an AWS/runtime deployment view. Use solid Mermaid nodes and edges only for verified relationships. Use a dashed edge and an explicit `inferred` or `unverified` label for a relationship supported only by partial evidence. Keep desired and current architecture in separate diagrams when both matter.

List a source reference for every material node and edge. A diagram with an inaccessible surface can still be useful, but its verification status must remain partial and the missing area must be visible.

## Determine progress and the next start

- Classify accepted work items as completed, in progress, verification pending, blocked, cancelled/superseded, or unknown from current events and fresh PR, merge, deployment, test, and acceptance evidence. A commit, PR, or message count is not progress.
- Calculate a ratio only for an accepted authoritative denominator in a versioned PRD, milestone, or WBS. If the WBS is incomplete, report its known subset and explicitly state that it is not whole-project progress. Exclude proposed decomposition from the denominator.
- Select a next start only when the item is `ready`, every dependency is completed, accepted acceptance criteria are observable, its sources and architecture are current, no active PR already implements it, and a safe mapped repository/start workflow exists. If no item qualifies, report `착수 가능 항목 없음` and the smallest evidence-backed unblock action. Do not invent priority.

## Persist and stop

Record newly verified repository, PR, Slack coverage, AWS, Shopify, conflict, and progress evidence. Save the technical baseline with `history_record_architecture_snapshot`, including version, Mermaid source, detailed Markdown, source references, verification status, and capture time. Record blockers or readiness changes as work-item events without deleting prior states.

Do not edit product code, start a branch, invoke `$b-start`, mutate AWS or Shopify, create or merge PRs, or deploy. Recommend `$dev-implement <work-item key>` only for the verified next-ready item.
