---
name: work-history
description: Run a one-time bootstrap of evidence-backed completed work and decisions from all accessible Slack and Git history for a person.
metadata:
  version: 0.2.3
  author: hak2881
license: MIT
---

# Work History

Treat `$work-history <person>` as a one-time bootstrap that creates the initial local history database. Search the full accessible past for that person and build durable project timelines of completed work. Capture what was requested, decided, implemented, changed, verified, and delivered. Store facts through the `work_history` MCP tools; do not treat conversational memory as the business source of truth. TODO tracking is secondary.

Read [references/evidence-model.md](references/evidence-model.md) before writing records. Read [references/git-sync.md](references/git-sync.md) when repositories must be discovered or synchronized.

## Workflow

1. Resolve the Slack identity. Record candidate IDs and the evidence for the selected identity. If multiple candidates would materially change coverage, ask the user.
2. Search all channels accessible to the connected account for authored messages, mentions, replies, linked threads, and project references. Access coverage is limited to what that account can read; report inaccessible channels.
3. Fetch complete threads, preserving permalink, channel, author, timestamp, and reply relationships. Do not summarize from search snippets alone.
4. Resolve projects from explicit customer names, channel purpose, repository/PR links, Shopify store references, and existing project mappings. Mark uncertain mappings `inferred` or `unresolved`.
5. Reconstruct completed work as dated evidence: request, decision, implementation, verification, delivery, cancellation, or replacement. Link each event to its Slack message, PR, commit, document, or other source.
6. For every resolved project, discover and synchronize that project's repositories according to [references/git-sync.md](references/git-sync.md). Do not filter repositories by the person's ownership, Git account, or commit authorship. Record the remote, local path, default branch, fetched SHA, sync time, and access failures.
7. Index commit metadata and changed paths. Link Slack items to Git only when a PR/commit is explicit or author, time, branch, issue key, and content provide enough corroboration. A commit never proves deployment or acceptance.
8. Record an open item only when the source explicitly assigns, requests, or leaves work unresolved. Do not infer a TODO from discussion, an idea, or a code commit. Preserve resolved items as history instead of treating the TODO list as the main output.
9. Return a work-history report per project: chronological completed work, decisions and implementation evidence, channels and time range searched, repositories cloned/synced/inaccessible, optional open items, and unresolved mappings.

## Repository layout

Default to `${HOME}/projects/lukuku/<project-slug>/<repository-name>`. Reuse a verified existing checkout when its normalized remote matches. Never create two checkouts for the same project and remote.

## Completion rule

Call the history ready only when each known project has source coverage recorded and every inaccessible or ambiguous source appears in the report. Ready means sufficient provenance for research; it does not mean every historical message is accessible.

After this bootstrap, normal updates belong to `$work-research`: each investigation stores newly verified relevant evidence. Do not tell the user to rerun `$work-history` routinely. If the user explicitly reruns it, backfill missing coverage without duplicating existing evidence.
