# Work Research Agent Design

## Purpose

Build a shareable agent profile that turns a Slack request link into an evidence-backed PM response draft. The agent must recover what was requested, decided, implemented, verified, and delivered, inspect relevant Git history and current code, and verify Shopify claims with official sources or browser evidence before drafting an answer. It never posts to Slack by default.

## User workflows

### `/work-history <person>`

Run a one-time bootstrap of the local evidence store for a person such as `김병학`. Later `/work-research` runs append newly verified evidence incrementally.

1. Resolve the Slack identity and record the resolution evidence.
2. Search every channel accessible to the connected Slack account.
3. Read complete threads and reconstruct each project's completed work and decisions. Track open items only when they are explicit.
4. Discover repositories from explicit Slack links, project mappings, existing local remotes, and accessible Git hosting metadata.
5. Clone missing repositories under `<workspace-root>/lukuku/<project>/<repository>` with full commit history. Partial clone with `--filter=blob:none` is allowed; shallow clone is not.
6. For existing repositories, fetch and prune without resetting, checking out, cleaning, or modifying a dirty worktree.
7. Index repository metadata, commits, changed files, and explicit or inferred Slack-to-Git links.
8. Report completed work, coverage, inaccessible sources, ambiguous mappings, and explicit unresolved items.

### `/work-research <slack-link>`

1. Parse the Slack permalink and read the complete thread.
2. Resolve the customer, project, repository, Shopify store, and prior work using stored mappings and fresh source checks.
3. Reject unrelated history. Mark relationships as `explicit`, `verified`, `inferred`, or `unresolved`.
4. Route verification according to the claim:
   - current behavior: local code plus Git history;
   - Shopify Admin capability: Admin GraphQL and official Shopify documentation;
   - Shopify app suitability: current app listing/docs and Playwright verification;
   - Shopify Function feasibility: Function API and platform constraints;
   - prior agreement or requested behavior: complete Slack thread and linked evidence.
5. Produce a PM draft with claims, evidence, confidence, remaining questions, and the exact repository SHA checked.
6. Do not post externally. Present actions: `1` copy answer, `2 <part>` targeted re-review, `3` independent full re-review.

## Architecture

The repository is a Hermes Profile Distribution. `SOUL.md` defines the agent's operating rules, while `skills/work-history` and `skills/work-research` define the two explicit slash-command workflows.

A local stdio MCP server owns a SQLite database. Evidence is the primary timeline of sourced work; optional task records are limited to explicitly assigned or unresolved items. The database also stores normalized projects, repositories, commits, and source links. Raw repository contents remain in Git checkouts; the database stores paths, SHAs, metadata, excerpts, and provenance. SQLite FTS5 supplies local text search.

External systems remain separate connectors. Slack, GitHub/Git, Shopify, browser automation, and code analysis provide evidence; the local MCP records and retrieves it. Credentials and customer data are never distributed in this public repository.

## Evidence contract

Every material claim must identify its source type, source URI, capture time, and verification level. A commit is evidence that code changed, not proof that a customer request is complete. Current behavior must be checked at a recorded SHA. Conflicting evidence is returned rather than silently reconciled.

Verification levels are `slack`, `official-docs`, `admin`, `code`, `execution`, and `production`. Relationship confidence is `explicit`, `verified`, `inferred`, or `unresolved`.

## Safety and boundaries

- Read-only by default for Slack, Shopify, and production systems.
- Never send Slack messages or mutate Shopify without an explicit request in the active conversation.
- Never reset, clean, delete, or switch branches in discovered repositories.
- Never store API keys, cookies, OAuth tokens, or Git credentials in SQLite.
- Ask the user only when ambiguity can materially change the answer; otherwise continue and label uncertainty.
- Treat private customer data as local runtime data excluded from Git.

## Initial release scope

The first release includes the Hermes distribution, both skills, a tested SQLite repository, MCP tools for storing and querying evidence, schema documentation, and installation instructions. Automated Slack crawling, Git hosting enumeration, and Shopify browser automation are orchestrated by the skills through the host's connected tools; provider-specific credentials and clients are not embedded in the MCP.

## Acceptance criteria

- The public repository installs as a Hermes profile distribution.
- Both skills are discoverable as `/work-history` and `/work-research`.
- The local database can upsert projects, record completed-work evidence and optional explicit open items, register repositories and commits, create source links, search evidence, and return a project context bundle.
- Re-running an upsert does not create duplicate logical records.
- Search results expose provenance and confidence.
- The repository contains no runtime database, credentials, sessions, or customer history.
- Automated tests pass on Python 3.11 and later.
