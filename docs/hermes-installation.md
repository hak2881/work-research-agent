# Hermes Agent installation and setup

This guide installs Hermes Agent, the `work-research-agent` profile, its local SQLite MCP, and the browser engine needed for Shopify checks. Commands below target macOS and also apply to Linux or WSL unless noted.

## 1. Install Hermes Agent

Run the official CLI installer:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.zshrc
```

Use `source ~/.bashrc` when Bash is your shell. The installer places the command at `~/.local/bin/hermes` and keeps Hermes state under `~/.hermes/`.

Verify the installation:

```bash
command -v hermes
hermes --version
hermes doctor
```

If `doctor` reports an old configuration version, run:

```bash
hermes doctor --fix
```

On macOS, grant your terminal application Full Disk Access if Hermes needs to inspect repositories under protected folders:

```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
```

Restart the terminal after changing that setting.

## 2. Configure a model provider

Hermes needs a model before it can run a chat. Choose one route.

### Nous Portal

```bash
hermes setup --portal
```

This opens OAuth login and configures the model and Nous tool gateway. A Nous subscription is required.

### Existing provider or AWS Bedrock

```bash
hermes model
```

Choose the provider and model interactively. AWS Bedrock uses the standard AWS credential chain, such as an IAM role, `AWS_PROFILE`, AWS SSO, or `~/.aws/credentials`.

Confirm that a normal conversation works before adding the specialized profile:

```bash
hermes chat
```

## 3. Install Work Research Agent

```bash
mkdir -p ~/projects
hermes profile install github.com/hak2881/work-research-agent --alias --yes
```

This creates an isolated Hermes profile at:

```text
~/.hermes/profiles/work-research-agent/
```

The profile has its own configuration, skills, sessions, and local history database. Select its model separately:

```bash
work-research-agent model
```

If the alias is unavailable, use:

```bash
hermes -p work-research-agent model
```

## 4. Verify the profile and MCP

```bash
hermes profile info work-research-agent
hermes -p work-research-agent skills list
hermes -p work-research-agent mcp list
hermes -p work-research-agent mcp test work_history
```

Expected results:

- profile version and GitHub source are displayed;
- `work-history` and `work-research` are enabled;
- `work_history` is enabled;
- the MCP connection test succeeds and lists its tools.

Start the agent:

```bash
work-research-agent chat
```

Then build initial history:

```text
/work-history 김병학
```

## 5. Browser and Playwright verification

The official installer normally installs Chromium automatically. Check it with:

```bash
hermes doctor
```

If Playwright Chromium is missing:

```bash
cd ~/.hermes/hermes-agent
npx playwright install chromium
```

Shopify Admin and app verification still require an authorized browser session. Do not put Shopify cookies or tokens in this Git repository.

## 6. Connect Slack

Hermes can operate as a Slack bot through Socket Mode. Run:

```bash
hermes gateway setup
```

Select Slack and provide the Slack bot token (`xoxb-`), app-level token (`xapp-`), and allowed member IDs. Start it in the foreground while testing:

```bash
hermes gateway
```

Install the gateway as a user service after the test succeeds:

```bash
hermes gateway install
```

Slack access is limited to the channels and message history the installed Slack app can read. Invite the app to each required private channel and grant only the scopes needed for history and thread lookup. Never commit Slack tokens; Hermes stores local secrets in the profile `.env` files.

For research initiated from the terminal, a separate Slack MCP or connector may be used instead of the messaging gateway. Whichever connection is used must be able to open the supplied permalink and read its full thread.

## 7. Update

Update Hermes itself:

```bash
hermes update
```

Update this profile while preserving local sessions, memories, credentials, and history:

```bash
hermes profile update work-research-agent --yes
```

Re-run verification after an update:

```bash
hermes -p work-research-agent mcp test work_history
```

## Troubleshooting

### `hermes: command not found`

```bash
source ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### MCP says `Connection closed`

Inspect the profile log:

```bash
tail -100 ~/.hermes/profiles/work-research-agent/logs/mcp-stderr.log
```

Update the profile and retry:

```bash
hermes profile update work-research-agent --yes
hermes -p work-research-agent mcp test work_history
```

### The profile has no model

Named profiles do not automatically reuse another profile's model configuration. Run:

```bash
work-research-agent model
```

### Slack private channel cannot be read

Confirm that the Slack app is installed in the same workspace, invited to the private channel, and has the required history scopes. Reinstall the Slack app after changing OAuth scopes.

## Verified environment

This procedure was exercised on macOS ARM64 on 2026-09-17 with Hermes Agent `0.21.3`, Python `3.11.15`, SQLite `3.53.1`, and Playwright Chromium installed by the official installer.

