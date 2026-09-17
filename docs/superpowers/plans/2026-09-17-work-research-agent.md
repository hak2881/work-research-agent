# Work Research Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Publish a Hermes profile distribution with evidence-backed work-history and work-research skills plus a local SQLite MCP server.

**Architecture:** Hermes owns orchestration and external tool use. A small Python package owns durable normalized evidence and exposes it through stdio MCP tools, keeping provider credentials and raw source data outside the public repository.

**Tech Stack:** Hermes Profile Distribution, agentskills.io `SKILL.md`, Python 3.11+, SQLite FTS5, MCP Python SDK 2.x, pytest, uv.

**Spec:** `docs/superpowers/specs/2026-09-17-work-research-agent-design.md`

## Global Constraints

- Slack, Shopify, and production access is read-only by default.
- Never mutate a discovered Git worktree.
- Do not commit credentials, runtime databases, sessions, or customer history.
- Material claims require provenance and a verification level.
- Keep provider-specific integrations outside the storage core.

---

### Task 1: Hermes distribution and skills

**Files:**
- Create: `distribution.yaml`
- Create: `SOUL.md`
- Create: `config.yaml`
- Create: `mcp.json`
- Create: `skills/work-history/SKILL.md`
- Create: `skills/work-research/SKILL.md`
- Create: `skills/*/references/*.md`

**Interfaces:**
- Consumes: Hermes profile-distribution and skill conventions.
- Produces: `/work-history` and `/work-research` workflows and the `work_history` MCP connection.

- [x] Write the distribution manifest, agent rules, MCP wiring, skills, and supporting references.
- [x] Validate YAML, JSON, skill frontmatter, referenced files, and forbidden runtime paths.
- [x] Commit the independently installable profile scaffold.

### Task 2: SQLite evidence repository

**Files:**
- Create: `pyproject.toml`
- Create: `src/work_research_history/store.py`
- Create: `tests/test_store.py`

**Interfaces:**
- Produces: `HistoryStore` methods `upsert_project`, `record_evidence`, `upsert_task`, `register_repository`, `record_commit`, `link_sources`, `search`, and `project_context`.

- [x] Write failing tests for idempotent project writes, evidence search with provenance, task state replacement, repository/commit recording, source links, and project context.
- [x] Run `uv run pytest tests/test_store.py -q` and confirm failure because the package is absent.
- [x] Implement the schema and minimal store methods.
- [x] Run the store tests and confirm they pass.
- [x] Commit the storage core.

### Task 3: MCP tools and public documentation

**Files:**
- Create: `src/work_research_history/server.py`
- Create: `tests/test_server.py`
- Create: `README.md`
- Create: `.gitignore`
- Create: `LICENSE`

**Interfaces:**
- Consumes: `HistoryStore`.
- Produces: stdio MCP tools mirroring the storage operations and public installation instructions.

- [x] Write a failing in-process MCP test that lists and calls representative tools.
- [x] Run the MCP test and confirm failure because the server is absent.
- [x] Implement the MCP wrapper using `MCPServer`.
- [x] Run all tests, package build, JSON/YAML parsing, skill validation, and secret scan.
- [x] Commit, tag `v0.1.0`, create `hak2881/work-research-agent` as public, and push `main` plus the tag.
