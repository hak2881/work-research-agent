# Work Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `$work-policy` with the LUKUKU Markdown standard, strict validation, and versioned policy history.

**Architecture:** The skill resolves customer-agreed evidence and materializes the bundled Markdown reference. The existing document registry stores each file version, while a new immutable policy snapshot table stores searchable policy entries and their authority evidence.

**Tech Stack:** Python 3.11+, SQLite, MCP, Markdown, pytest

**Spec:** `docs/superpowers/specs/2026-09-20-work-policy-design.md`

## Global Constraints

- The standard template lives under `skills/work-policy/references/`.
- Markdown is the only policy artifact.
- No policy is inferred from code, silence, proposals, estimates, schedules, or TODOs.
- No automatic commit, push, implementation, or external posting.

---

### Task 1: Policy snapshot storage

**Files:**
- Modify: `src/work_research_history/store.py`
- Modify: `src/work_research_history/server.py`
- Test: `tests/test_store.py`
- Test: `tests/test_server.py`

- [ ] Add failing tests for versioned, atomic, immutable policy snapshots and MCP exposure.
- [ ] Add the policy snapshot schema, validation, persistence method, project context result, and MCP tool.
- [ ] Run the focused store and server tests.

### Task 2: Standard reference and validator

**Files:**
- Create: `skills/work-policy/SKILL.md`
- Create: `skills/work-policy/references/lukuku-policy-template-v1.0.md`
- Create: `skills/work-policy/references/policy-contract.md`
- Create: `skills/work-policy/references/source-resolution.md`
- Create: `skills/work-policy/scripts/validate_policy.py`
- Create: `tests/fixtures/policy/sample-policy.md`
- Create: `tests/test_policy_validator.py`

- [ ] Add failing tests for the eight areas, placeholders, comments, dates, and section contents.
- [ ] Copy the supplied standard into references and implement the minimal validator.
- [ ] Write the skill workflow and policy/source contracts.
- [ ] Validate the source skill.

### Task 3: Workflow and distribution integration

**Files:**
- Modify: relevant existing skills, `README.md`, installation docs, manifests, `distribution.yaml`, and `scripts/validate_distribution.py`
- Mirror: `plugins/work-research-agent/skills/`
- Test: `tests/test_distribution.py`

- [ ] Add failing distribution assertions for `$work-policy` and its bundled reference.
- [ ] Teach relevant workflows to consult current policy snapshots.
- [ ] Package the new skill, bump the minor version to `0.10.0`, and update usage docs.
- [ ] Run all tests and both plugin validators; verify source/package equality and a clean diff check.

