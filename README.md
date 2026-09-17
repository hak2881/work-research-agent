# Work Research Agent

`work-research-agent` is a public [Hermes Agent](https://github.com/NousResearch/hermes-agent) profile distribution for investigating customer requests before a PM answers them.

Give it a Slack thread link and it reconstructs the related project history, checks Git and current code, verifies Shopify capabilities or app flows when relevant, and returns a Korean PM response draft with evidence. It does not post the draft to Slack by default.

## What is included

- `/work-history <person-or-project>` builds a local evidence history from accessible Slack threads and Git repositories.
- `/work-research <slack-link>` checks one request against that history and fresh code, Shopify, documentation, and browser evidence.
- A local SQLite + FTS5 MCP server stores normalized projects, evidence, TODOs, repositories, commits, and source relationships.
- `SOUL.md` enforces evidence labels, contradiction checks, exact Git SHAs, and read-only defaults.

The profile contains workflows and local storage. Slack, Git hosting, Shopify Admin, and browser access come from tools or MCP connections configured on the installer's machine.

## Install

Requirements:

- Hermes Agent `0.12.0` or later
- Python 3.11 or later
- [`uv`](https://docs.astral.sh/uv/)
- Git and, for GitHub discovery, an authenticated `gh` CLI
- a Slack connection that can read the channels being researched
- browser automation and Shopify access for Shopify-specific verification

```bash
mkdir -p ~/projects
hermes profile install github.com/hak2881/work-research-agent --alias
work-research-agent chat
```

If the alias is omitted, run `hermes -p work-research-agent chat`.

Hermes currently reads MCP servers from `config.yaml`; this distribution also ships the documented `mcp.json` representation so it remains compatible when Hermes resolves that format mismatch. The definitions are intentionally identical.

## Use

Build or refresh history first:

```text
/work-history 김병학
```

Then research a request:

```text
/work-research https://your-workspace.slack.com/archives/C01234567/p1234567890
```

The response ends with:

```text
1. 답변 복사
2. <부분> 재검수
3. 전체 독립 재검수
```

Option `1` copies only when the active Hermes surface provides clipboard tooling. Otherwise the agent returns a clean copy block. No option posts to Slack unless you explicitly request posting in the active conversation.

## Local data

The installed profile stores its database at:

```text
$HERMES_HOME/local/work-history.sqlite3
```

For the default profile name this normally resolves under:

```text
~/.hermes/profiles/work-research-agent/local/work-history.sqlite3
```

Git checkouts default to:

```text
~/projects/lukuku/<project>/<repository>
```

Repository blobs stay in Git. SQLite stores provenance, excerpts, task state, repository metadata, commit metadata, changed paths, and links between sources. Credentials, browser cookies, Slack tokens, Shopify tokens, and customer databases are never part of this repository.

See [the schema](docs/schema.md) and [the design](docs/superpowers/specs/2026-09-17-work-research-agent-design.md) for the evidence model.

## Development

```bash
uv sync --dev
uv run pytest -q
uv run python scripts/validate_distribution.py
uv build
```

Run the MCP server directly:

```bash
WORK_RESEARCH_DB=/tmp/work-history.sqlite3 uv run work-research-history
```

## Limits of the initial release

- The agent can only search Slack channels visible to its connected account.
- Provider-specific Slack and Shopify credentials must be configured locally.
- A Git commit proves a change exists in history; deployment and production behavior require separate evidence.
- Ambiguous project-to-repository mappings remain labeled for review instead of being guessed.

## License

MIT

