# Git discovery and synchronization

## Discovery order

1. Explicit repository, PR, branch, or commit URLs in Slack threads.
2. Existing project mappings in the history database.
3. Existing local Git remotes under the workspace root.
4. Repositories accessible to the connected Git-hosting identity whose organization, name, description, topics, or linked documentation identify the project.

Repository scope follows the resolved project, not the searched person. Do not restrict discovery to repositories owned by the person or containing their commits. The person's commits help connect work to a repository after the project repository set is found. Do not assign every repository owned by an account to every customer. Record ambiguous candidates for review.

## Clone and update rules

- Clone into `${HOME}/projects/lukuku/<project-slug>/<repository-name>`.
- Keep complete commit history. Prefer `git clone --filter=blob:none`; never use `--depth`.
- Normalize and compare remote URLs before cloning to prevent duplicates.
- When a checkout exists, run read-only inspection first.
- Fetch remote refs with pruning. Do not reset, clean, checkout, merge, rebase, stash, or delete anything.
- A dirty worktree may be fetched but never otherwise changed.
- Use the configured Git/`gh` credentials. Never copy credentials into the history database.
- Report private or missing repositories as inaccessible with the attempted source URI and error category.

## History indexing

Record repository ID, remote URL, local path, default branch, fetched SHA/time, commit SHA, author, authored time, subject, and changed paths. Store blobs in Git, not SQLite. When analyzing current behavior, record the exact checked SHA and whether the working tree was dirty.
