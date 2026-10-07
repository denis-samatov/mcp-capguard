# MCP Atlassian pilot

This checks the real
[`sooperset/mcp-atlassian`](https://github.com/sooperset/mcp-atlassian/tree/0a5d2427144d72f5aade07d4fabd385421cec401)
server at a pinned commit with FastMCP 3.4.8 and MCP SDK 1.30.0.
Use a **separate Python 3.12 environment**: the capguard development extra and
Yandex pilot use SDK 2.x, which is incompatible with this upstream server.

From the capguard repository root (Linux/macOS, with `uv` installed):

```bash
uv venv --python 3.12 .venv-atlassian
uv pip install --python .venv-atlassian/bin/python -e . -r examples/mcp_atlassian_pilot/requirements.txt
cd examples/mcp_atlassian_pilot
../../.venv-atlassian/bin/python -m pytest -q
../../.venv-atlassian/bin/capguard check --profiles profiles:capguard_profiles
```

## Check the client-visible boundary

Calling upstream's `main_mcp.list_tools()` directly returns its internal registry
(98 tools at this commit), before request-time filtering. The adapter's
`list_tools()` opens an **in-memory FastMCP Client**, enters the real server
lifespan, and requests `tools/list`. That tests the list a client actually sees.
It adds no HTTP listener or subprocess and requires no capguard core changes.

| Profile | Observed tools | Declared boundary |
| --- | ---: | --- |
| readonly, all toolsets | 58 | Required Jira/Confluence reads; four declared writes absent |
| readwrite, all toolsets | 98 | Required read and write tools available |
| two-tool-allowlist | 2 | `jira_get_issue` and `confluence_get_page`; declared other tools absent |

Counts are observations, not assertions. These sample policies check only the
named requirements and prohibitions; they do not prove every undeclared tool is
safe or that the allowlist has no other tools.

The negative control turns off upstream's actual readonly setting while retaining
the readonly policy:

```bash
../../.venv-atlassian/bin/capguard check --profiles profiles:leaking_profiles
```

It must exit **1**, naming `jira_create_issue`, `confluence_delete_page`, and the
other declared forbidden tools. The fourth pytest test verifies this intentional
violation; pytest itself exits 0.

Run in a fresh, dedicated process, serially. The upstream server is a module-level
singleton; the adapter imports it inside a temporary, isolated environment and
restores environment variables after the client closes. Do not reuse this adapter
concurrently with another server or after importing a differently configured
`main_mcp` in the same process.

Only placeholder credentials are supplied. No Jira/Confluence tools are called.
The pytest configuration blocks TCP sockets, including outbound API requests.
This tests tool exposure, not tool execution or runtime authorization. The pilot
is maintained here; it does not imply endorsement or adoption by upstream.
