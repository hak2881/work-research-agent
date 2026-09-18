# Developer Workflow Design

## Purpose

Add a developer-facing workflow to Work Research Agent without changing the existing PM-facing commands. The workflow converts sourced PRD or WBS material into durable work items, implements one ready item with history checks, and maintains an evidence-backed technical architecture and delivery view.

## Commands

- `$dev-plan <PRD, WBS, Slack link, or document>` analyzes requirements, feasibility, effort, dependencies, acceptance criteria, and unresolved questions. It writes sourced planning records but does not edit product code.
- `$dev-implement <work-item key or Slack permalink>` resolves or plans exactly one approved ready item and implements it. For backend work it invokes `$b-start`; it never invokes `$b-end` or `$b-deploy`, merges, or deploys.
- `$dev-context <project>` maps the code, runtime, data, integration, AWS, and delivery architecture and reports developer-oriented progress and the next ready work. It does not edit product code or cloud resources.
- `$dev-pr [work-item key or Slack permalink]` resolves the just-finished verified work when omitted, determines the evidenced base branch, and performs only the required normal push and pull-request creation.

## Evidence and state rules

Project identity must be corroborated before records are written. Documents are recorded by source URI, version, and content hash. A requirement becomes a work item only when it is explicit in a source or clearly labeled as a proposed engineering decomposition. Missing decisions remain questions or blockers.

Work-item states are `planned`, `ready`, `in_progress`, `verification_pending`, `completed`, `blocked`, `cancelled`, and `superseded`. State transitions are append-only events. Updating a current row must not erase its event history. Code completion alone reaches at most `verification_pending`; `completed` requires the relevant acceptance evidence.

Effort uses a minimum and maximum with a unit, confidence, assumptions, exclusions, and dependencies. A single exact estimate is allowed only when its source explicitly fixes it. Project progress is shown only against an authoritative WBS or accepted work-item scope; message, commit, or repository counts are not progress.

## Architecture rules

Architecture conclusions cite repository and SHA or a cloud observation with account, region, and checked time. CodeGraph is used first for current code relationships when available. AWS resources are confirmed from IaC, deployment configuration, or read-only AWS inspection; names and conventions alone are not proof.

The architecture snapshot stores a summary, Mermaid source, detailed Markdown, source references, verification status, and capture time. It covers repository boundaries, request and data flows, persistent stores, queues, caches, scheduled work, Shopify surfaces, external integrations, CI/CD, runtime topology, AWS networking and resources, IAM relationships, logging, monitoring, unknowns, and affected work items as applicable.

## Persistence model

Keep existing projects, evidence, tasks, repositories, commits, and source links compatible. Add:

- `project_documents` for source identity, type, version, and content hash.
- `work_items` for the current planning state, plus versioned estimate and sourced acceptance-criterion records.
- `work_item_dependencies` for directed prerequisites.
- `work_item_events` for append-only state, decision, implementation, verification, and blocker history.
- `architecture_snapshots` for versioned technical baselines and Mermaid diagrams.

`history_project_context` returns the new records alongside the existing data. MCP tools create or update each record without requiring direct SQLite access from skills.

## Output boundaries

All four skills report in Korean unless requested otherwise and disclose inaccessible sources. `dev-plan` produces a feasibility and estimation report plus the exact work items written. `dev-implement` reports code changes, tests, acceptance checks, history consistency, and DB persistence. `dev-context` produces Mermaid diagrams, AWS and repository evidence, developer progress, risks, unknowns, and recommended next ready work. `dev-pr` pushes the verified branch and creates or reuses one PR without merging or deploying.
