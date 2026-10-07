# Google Workspace MCP: Gmail/Drive tool policies

This adapter registers the real Gmail and Drive modules from
[Google Workspace MCP](https://github.com/taylorwilsdon/google_workspace_mcp/tree/8f4670ef8ad45f749660079da26eb8e394f6f9fa),
applies the upstream registration/filter sequence, and requests `tools/list`
through an in-memory FastMCP Client with the actual server lifespan.
It exercises a selected two-service configuration, not the complete CLI startup.

The upstream uses a mutable global server registry. Every profile runs in a fresh
Python process, an empty temporary working/credentials directory, and a minimal
environment with dotenv disabled. The worker blocks socket connections before
importing upstream modules. No Google credentials or live APIs are used, and no
tool is invoked.

## Reproduce

From the capguard repository root, use a separate Python 3.12 environment:

```bash
uv venv --python 3.12 .venv-workspace-pilot
uv pip install --python .venv-workspace-pilot/bin/python -e . -r examples/google_workspace_pilot/requirements.txt
cd examples/google_workspace_pilot
../../.venv-workspace-pilot/bin/python -m pytest -v
../../.venv-workspace-pilot/bin/capguard check --profiles profiles:capguard_profiles
../../.venv-workspace-pilot/bin/capguard check --profiles profiles:leaking_profiles
```

The last command intentionally exits **1** and names unexpected write tools.
Pytest should report **4 passed**: three policies plus that negative control.

| Profile | Declared requirement | Declared prohibition |
| --- | --- | --- |
| `gmail-drive-readonly` | Gmail/Drive search and listing | Gmail send/draft and Drive create |
| `organize-gmail-readonly-drive` | Those reads plus message label modification | The same send/draft/create names |
| `full-with-send-blocked` | Reads, drafts and Drive creation | `send_gmail_message` |

Locally verified on Python 3.11.16, FastMCP 4.0.10 and MCP SDK 2.2.0;
the three client lists contained 15, 18 and 30 tools respectively. The profile
declares only a subset of those names: undeclared tools remain permitted.
The requirements pin upstream commit and the two MCP libraries; other transitive
dependencies are resolved on installation, so report installed versions too.

This tests tool visibility, not OAuth consent, live API compatibility, or execution
authorization. The subprocess is an example-owned adapter, not a new capguard core
transport. Successful local runs do not establish independent upstream adoption.
