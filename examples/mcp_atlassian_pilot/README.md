# MCP Atlassian pilot

The current **offline exposure-test profile** uses MCP Atlassian 0.23.1 and
`cryptography>=50.0.0`, captured with hashes in `requirements.lock`. This replaces
the previous Git snapshot that required `cryptography<47`; no incompatible
dependency override is used. The old constraint/advisory conflict is historical,
not an approval for live hosting. Certificates, OAuth credentials and real
Jira/Confluence tool calls remain outside these tests.

This checks the real
[`sooperset/mcp-atlassian`](https://pypi.org/project/mcp-atlassian/0.23.1/)
server at a pinned package version with the versions in `requirements.txt` (historical run: FastMCP 3.4.8 / MCP SDK 1.30.0).
Use a **separate Python 3.12 environment**: the capguard development extra and
Yandex pilot use SDK 2.x, which is incompatible with this upstream server.

From the capguard repository root (Linux/macOS, with `uv` installed):

```bash
uv venv --python 3.12 .venv-atlassian
uv pip install --python .venv-atlassian/bin/python --require-hashes -r examples/mcp_atlassian_pilot/requirements.lock
uv pip install --python .venv-atlassian/bin/python --no-deps -e .
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

## Dependency update

The requirements now select FastMCP 3.4.10 to address the upstream advisory range.
Earlier recorded results for 3.4.8 remain historical; installation and offline
compatibility must be rechecked for this revised environment. These tests do not
qualify OAuth credentials or live upstream services.

Local remediation check (2026-10-29): Python 3.12.14, FastMCP 3.4.10 / MCP SDK 1.30.0,
`python -m pytest -q`: 4 passed with TCP blocked by pytest-socket. This
checks tool exposure and negative controls, not live provider authorization.


Qualification update (2026-10-30): Python 3.12.14, MCP Atlassian 0.23.1,
FastMCP 3.4.10 / MCP 1.30.0 / cryptography 50.0.2: all four TCP-blocked
profile/negative-control tests passed. The same checks passed with a locally
built capguard wheel. Strict OSV audit of that installed environment reported
no known vulnerabilities; this is a versioned dependency observation, not a
cryptographic or live-service security certification.

Regenerate the Linux/Python 3.12 lock from the repository root with:

```sh
uv pip compile examples/mcp_atlassian_pilot/requirements.txt --python-version 3.12 \
  --python-platform x86_64-unknown-linux-gnu --generate-hashes \
  --output-file examples/mcp_atlassian_pilot/requirements.lock
```
