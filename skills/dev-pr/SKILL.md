---
name: dev-pr
description: Use when a developer wants to push the just-finished verified branch and create one evidence-backed pull request, with or without a work-item key or Slack permalink, while determining the correct base from project history and never merging or deploying.
metadata:
  version: 0.1.0
  author: hak2881
license: MIT
---

# Dev PR

Create or reuse exactly one pull request for already implemented and verified work. The `$dev-pr` invocation authorizes the required normal branch push and PR creation for the resolved repository, head, and base. It does not authorize code changes, commits, force pushes, merges, promotion PRs, deployment, or branch cleanup.

Read [references/pr-contract.md](references/pr-contract.md) before pushing.

## Resolve the work without guessing

When invoked without an argument, scope discovery to the current Git root first. Match its normalized remote, current branch, HEAD, commits, current-session file operations, and recent implementation or verification events to exactly one corroborated work item. A recent timestamp alone is not a match. If the current directory is not inside a Git repository, use repositories actually touched in the current session as candidates and continue only when the same evidence resolves exactly one repository and work item.

Do not scan or stage a dirty sibling repository. If no candidate or multiple candidates remain, return their repository, branch, SHA, and work-item keys and stop before any push.

When given a work-item key, resolve its linked repository and verified branch from `history_project_context`. When given a Slack permalink, follow only the project and work-item resolution rules in [../dev-implement/SKILL.md](../dev-implement/SKILL.md); do not plan or implement new work from this skill. Continue only when the link resolves to one existing `verification_pending` item and its current branch.

Require the resolved item to be `verification_pending` for every input mode. An `in_progress`, `ready`, blocked, completed, cancelled, superseded, or unknown item must not be pushed or opened as a PR by this workflow.

## Verify the exact PR contents

1. Verify the selected remote, Git-host repository, current branch/upstream, HEAD, dirty state, and fetch time. Run `git fetch --all --prune` without checkout, reset, clean, rebase, merge, or stash.
2. Require a non-base feature branch and a clean worktree, including untracked files. This skill never edits code or creates a commit. If work remains uncommitted, return to `$dev-implement`.
3. Confirm HEAD equals the verified SHA recorded for the work item. If HEAD or its commit set changed afterward, inspect the new diff and rerun the affected checks before creating the PR; record the new results. Never copy a stale test result into the PR body.
4. Determine the base from an explicit delivery rule in repository instructions, an accepted project decision, or corroborated project PR history. Backend-to-`main` and frontend-to-`staging` are valid only when that repository's rule is evidenced. The remote default branch, repository name, ancestry, or a sibling repository rule alone is insufficient. Stop on missing or conflicting evidence.
5. Review the exact `base...HEAD` commits and diff. Ensure every change belongs to the resolved work item, accepted criteria, or required tests. Block on unrelated commits, secrets, generated debris, unexplained migrations, or a diff that does not match the history.
6. Verify the recorded test commands and results against this HEAD. Disclose migrations, configuration, review requirements, and deployment or production checks that remain after the PR.

## Avoid duplicate pull requests

Enumerate existing pull requests from the Git host for the exact repository and head branch, then compare base, work-item key, and commit SHAs.

- If an open PR already covers the same head and base, do not create or edit another PR. Record and return it as `pr_reused`.
- If an open PR uses a different base or scope, stop and report the conflict.
- If a closed or merged PR already contains the same branch or commits, stop and resolve whether new commits or a new branch are required. Do not recreate it blindly.

## Push and create only the PR

1. Push the reviewed current branch to its verified remote with a normal upstream push. Re-read the remote head and require it to equal local HEAD. Record the successful push and exact remote SHA with `history_record_work_item_event` before PR creation. Never force-push, rename the branch, delete a branch, or substitute a remote after a failed push.
2. Write the PR title and body from the actual diff, accepted work-item scope, and observed validation. Match the repository's recent PR language and format when available. Lead with the concrete problem and resulting behavior; include the work-item or Slack source, changed components, exact tests, risks or gaps, and remaining merge/deploy evidence. Do not expose secrets, internal DB mechanics, or unsupported claims.
3. Write the body to a temporary file and use the Git host CLI with `--body-file` to create one review-ready PR for the verified head and base. Do not create a draft unless the user explicitly requested a draft.
4. Re-read the created PR and verify repository, head SHA, base branch, title, body, URL, number, and state.

If PR creation times out or returns an uncertain error after the push, enumerate the Git host again for the exact repository, head, and base before doing anything else. If the PR exists, verify and record it as created. If existence remains unresolved, record a `pr_create_uncertain` event with the pushed SHA and observed error, then stop. Do not retry PR creation until a fresh host lookup has resolved the prior attempt; persistence failure is also not a reason to repeat the create call.

## Persist and stop

Record `pr_created` or `pr_reused` with `history_record_work_item_event`, including repository, head SHA, base, PR URL/number/state, test evidence, and checked time. Use `history_link_sources` to link the work item, PR, commits, and Slack source when present. Keep the work item `verification_pending`; a PR is not completion, merge, deployment, or acceptance.

Never invoke `$b-end`. Never invoke `$f-end`. Never invoke `$b-deploy`. Do not merge, approve, enable auto-merge, create a staging-to-main promotion PR, deploy, switch to or pull a base branch, or delete local or remote branches.
