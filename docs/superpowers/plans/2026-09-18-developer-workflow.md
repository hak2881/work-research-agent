# Developer Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `$dev-plan`, `$dev-implement`, and `$dev-context` with durable planning, implementation, and architecture history.

**Architecture:** Extend the existing SQLite/MCP store with additive tables and focused tools, then add three packaged skills that consume the same project context. Keep PM commands compatible and make every developer conclusion traceable to documents, Slack, Git, code, or cloud observations.

**Tech Stack:** Python 3.11, SQLite, MCPServer, pytest, Codex and Claude plugin skill manifests.

**Spec:** `docs/superpowers/specs/2026-09-18-developer-workflow.md`

## Global Constraints

- Skill names are exactly `dev-plan`, `dev-implement`, and `dev-context`.
- Backend implementation invokes `$b-start` only; it never invokes `$b-end` or `$b-deploy`.
- Work-item history is append-only and completion requires acceptance evidence.
- AWS and architecture claims require repository@SHA or account/region/time evidence.
- Existing PM commands and stored data remain compatible.

---

### Task 1: Developer history model

**Files:**
- Modify: `src/work_research_history/store.py`
- Modify: `src/work_research_history/server.py`
- Modify: `tests/test_store.py`
- Modify: `tests/test_server.py`

**Interfaces:**
- Produces: `record_document`, `upsert_work_item`, `record_work_item_event`, `link_work_item_dependency`, and `record_architecture_snapshot` store methods and matching `history_*` MCP tools.
- Produces: `project_context()` keys `documents`, `work_items`, and `architecture_snapshots`.

- [ ] Add failing store tests for document idempotency, work-item state events, dependency links, architecture snapshots, and extended project context.
- [ ] Run the focused store tests and confirm failure because the APIs do not exist.
- [ ] Add the five additive tables and minimal store methods.
- [ ] Run focused tests and confirm they pass.
- [ ] Add failing MCP discovery and call tests for the new tools.
- [ ] Run the focused MCP test and confirm failure because tools are absent.
- [ ] Register the tools and confirm store, MCP, and existing tests pass.
- [ ] Commit the developer history model.

### Task 2: PRD and WBS planning skill

**Files:**
- Create: `skills/dev-plan/SKILL.md`
- Create: `skills/dev-plan/references/planning-contract.md`
- Modify: `tests/test_distribution.py`
- Modify: `scripts/validate_distribution.py`

**Interfaces:**
- Consumes: project resolution, document, work-item, dependency, event, evidence, and project-context MCP tools.
- Produces: sourced work items with ranges, assumptions, acceptance criteria, blockers, and dependency order.

- [ ] Run a no-skill baseline scenario and record whether requirements, estimates, and source boundaries are invented or lost.
- [ ] Add a failing distribution behavior test for explicit versus proposed items, ranged estimates, authoritative progress, and no code edits.
- [ ] Run the focused test and confirm it fails because `dev-plan` is absent.
- [ ] Write the minimal skill and planning report contract that close observed baseline failures.
- [ ] Package the skill and run quick validation, behavior tests, and distribution validation.
- [ ] Run the same scenario with the skill and close demonstrated loopholes.
- [ ] Commit the verified planning skill.

### Task 3: History-safe implementation skill

**Files:**
- Create: `skills/dev-implement/SKILL.md`
- Create: `skills/dev-implement/references/implementation-contract.md`
- Modify: `tests/test_distribution.py`
- Modify: `scripts/validate_distribution.py`

**Interfaces:**
- Consumes: a ready work item, project history, architecture snapshots, repositories, and work-item events.
- Produces: `$b-start` handoff, code and test evidence, state transitions, and a `verification_pending` or blocked result.

- [ ] Run a no-skill pressure scenario that tempts coding from stale or contradictory requirements and premature completion.
- [ ] Add a failing behavior test for `$b-start`, history checks, acceptance checks, event persistence, and prohibitions on `$b-end` and `$b-deploy`.
- [ ] Run the focused test and confirm it fails because `dev-implement` is absent.
- [ ] Write the minimal skill and implementation report contract.
- [ ] Package and validate the skill, then rerun the pressure scenario.
- [ ] Close demonstrated loopholes and rerun all tests.
- [ ] Commit the verified implementation skill.

### Task 4: Developer context and architecture skill

**Files:**
- Create: `skills/dev-context/SKILL.md`
- Create: `skills/dev-context/references/context-contract.md`
- Modify: `tests/test_distribution.py`
- Modify: `scripts/validate_distribution.py`

**Interfaces:**
- Consumes: repositories, work items, events, prior snapshots, CodeGraph, IaC, deployment config, and optional read-only AWS observations.
- Produces: versioned Mermaid and Markdown architecture snapshots plus evidence-backed developer progress.

- [ ] Run a no-skill scenario with incomplete IaC and misleading AWS names and record unsupported inferences.
- [ ] Add a failing behavior test for repository@SHA, AWS account/region/time, Mermaid, unknowns, authoritative progress, and next-ready work.
- [ ] Run the focused test and confirm it fails because `dev-context` is absent.
- [ ] Write and package the minimal architecture skill and report contract.
- [ ] Rerun the scenario and close demonstrated inference and coverage loopholes.
- [ ] Run quick validation, distribution validation, and all tests.
- [ ] Commit the verified architecture skill.

### Task 5: Release and installation

**Files:**
- Modify: `README.md`
- Modify: `docs/codex-installation.md`
- Modify: `docs/claude-code-installation.md`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `distribution.yaml`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `plugins/work-research-agent/.claude-plugin/plugin.json`
- Modify: `plugins/work-research-agent/.codex-plugin/plugin.json`
- Modify: `plugins/work-research-agent/.mcp.json`

**Interfaces:**
- Consumes: all three verified skills and new MCP tools.
- Produces: one installable Codex and Claude release with matching skill copies and pinned MCP tag.

- [ ] Update usage documentation and bump the minor plugin version.
- [ ] Copy canonical skill files into the packaged plugin and run byte-for-byte distribution checks.
- [ ] Run pytest, distribution validation, Codex plugin validation, skill quick validation, Claude strict validation, and `git diff --check`.
- [ ] Tag and push the release after all checks pass.
- [ ] Upgrade the local Codex and Claude plugins and verify the new version, seven skills, and `work_history` MCP.
