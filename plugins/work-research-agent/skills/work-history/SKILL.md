---
name: work-history
description: Build or refresh evidence-backed Slack and Git history for a person or project before customer-request research.
metadata:
  version: 0.2.0
  author: hak2881
license: MIT
---

# Work History

Build durable project history for the person or project named after `/work-history`. Store facts through the `work_history` MCP tools; do not treat conversational memory as the business source of truth.

Read [references/evidence-model.md](references/evidence-model.md) before writing records. Read [references/git-sync.md](references/git-sync.md) when repositories must be discovered or synchronized.

## Workflow

1. Resolve the Slack identity. Record candidate IDs and the evidence for the selected identity. If multiple candidates would materially change coverage, ask the user.
2. Search all channels accessible to the connected account for authored messages, mentions, replies, linked threads, and project references. Access coverage is limited to what that account can read; report inaccessible channels.
3. Fetch complete threads, preserving permalink, channel, author, timestamp, and reply relationships. Do not summarize from search snippets alone.
4. Resolve projects from explicit customer names, channel purpose, repository/PR links, Shopify store references, and existing project mappings. Mark uncertain mappings `inferred` or `unresolved`.
5. Extract decisions, requirements, questions, and TODO state events. Preserve later cancellations and replacements rather than deleting old events.
6. Discover and synchronize repositories according to [references/git-sync.md](references/git-sync.md). Record the remote, local path, default branch, fetched SHA, sync time, and access failures.
7. Index commit metadata and changed paths. Link Slack items to Git only when a PR/commit is explicit or author, time, branch, issue key, and content provide enough corroboration. A commit never proves deployment or acceptance.
8. Reconcile the current TODO state from ordered events. Leave conflicting states visible.
9. Return a coverage report per project: channels and time range searched, threads read, repositories cloned/synced/inaccessible, explicit and inferred links, TODO counts, and unresolved mappings.

## Repository layout

Default to `${HOME}/projects/lukuku/<project-slug>/<repository-name>`. Reuse a verified existing checkout when its normalized remote matches. Never create two checkouts for the same project and remote.

## Completion rule

Call the history ready only when each known project has source coverage recorded and every inaccessible or ambiguous source appears in the report. Ready means sufficient provenance for research; it does not mean every historical message is accessible.
