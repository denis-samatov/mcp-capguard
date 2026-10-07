# Check the MCP tool list a client actually sees

An MCP server can register 98 tools while exposing only 58 to a readonly client.
That is what we observed in the pinned MCP Atlassian pilot. A test against the
internal registry would check a different boundary from the one presented to
the client.

## Two real servers, two places to apply the policy

The [reproducible pilots](../README.md#pilots-with-real-servers) use actual upstream
code, pinned commits, synthetic settings, and no tool execution. They work with
the published capguard 0.1.1 runtime without core changes.

| Server | Upstream revision | Where the tool filter applies | Observed profiles |
| --- | --- | --- | --- |
| Yandex Workspace MCP | `9146882088ed8528e5d245337ea27d0c6d570c97` | Application factory registration | readonly 19, editor without deletion 39, services disabled 2 |
| MCP Atlassian | `0a5d2427144d72f5aade07d4fabd385421cec401` | Client `tools/list` request after server lifespan starts | readonly 58, readwrite 98, two-tool allowlist 2 |

These counts describe the pinned revisions. The policies assert explicitly
required and forbidden names, not counts or snapshots. An undeclared tool remains
allowed, so maintain the policy when adding tools.

### Registration-time filtering

Yandex's factory returns an application wrapper. Capguard can list the tools on
its MCP server using `accessor=lambda app: app.mcp_server`. No lifespan or API
client needs to be opened for this registration check.

The [Yandex policy](../examples/yandex_workspace_pilot/profiles.py) requires read
tools, prohibits the declared writes/deletions in readonly mode, and requires
writes while prohibiting deletions in editor mode. A third profile checks that
disabling both services removes the declared service tools.

### Request-time filtering

At the pinned Atlassian revision, `main_mcp.list_tools()` returns all 98 registered
tools. Readonly and allowlist settings are applied in the MCP request path.
The [adapter](../examples/mcp_atlassian_pilot/profiles.py) exposes its own async
`list_tools()` method, opens a real in-memory FastMCP Client, enters the real
server lifespan, and calls `client.list_tools()`.

This uses the normal MCP client/server request path without a network listener.
Capguard receives the client-visible names through its existing `list_tools()`
contract. The adapter requires a fresh, dedicated, serial process because the
upstream server is a singleton configured from process-wide environment variables.

## Prove the check can fail

A passing policy alone gives limited evidence. Both examples include a negative
control that changes actual upstream settings while retaining the readonly policy:

- Yandex: enable `wiki_write`; capguard names forbidden tools including
  `wiki_create_page` and `wiki_update_page`.
- Atlassian: turn off `READ_ONLY_MODE`; capguard names `jira_create_issue`,
  `jira_delete_issue`, `confluence_create_page`, and `confluence_delete_page`.

The CLI must exit 1 for these deliberately invalid configurations. The pytest
negative-control test expects `CapabilityViolation`, so its successful detection
is a passing test. This is an intentional configuration change, not a claim of
an upstream vulnerability.

## Reproduce or adapt it

1. Follow either the [Yandex instructions](../examples/yandex_workspace_pilot/README.md)
   or [Atlassian instructions](../examples/mcp_atlassian_pilot/README.md). Use separate
   Python 3.12 environments: these upstream servers require incompatible SDK majors.
2. Run pytest and the passing CLI profiles. Pytest blocks TCP sockets, including
   outbound API requests. No real credentials or tool invocation are needed.
3. Run the documented negative CLI control and check its exit code and named tools.
4. For your own server, identify where filtering actually happens, choose that
   public listing boundary, and declare required/forbidden names per configuration.

These checks do not verify tool execution, runtime authorization, API parity,
or that an undeclared tool is safe. Keep execution authorization tests alongside
the exposure policy.

The pilots are maintained by the capguard author. They establish reproducible
compatibility, not independent adoption or endorsement by upstream maintainers.
If you run one or integrate capguard into your own server, please
[share the result](https://github.com/denis-samatov/mcp-capguard/issues/new?template=compatibility-report.yml).
Successful reproductions and installation failures are both useful; include the
revision, command, outcome, and sanitized output.

## Sources

- [Yandex factory at the tested commit](https://github.com/denis-samatov/yandex-workspace-mcp/blob/9146882088ed8528e5d245337ea27d0c6d570c97/src/yandex_workspace_mcp/server.py)
- [Atlassian request filtering at the tested commit](https://github.com/sooperset/mcp-atlassian/blob/0a5d2427144d72f5aade07d4fabd385421cec401/src/mcp_atlassian/servers/main.py)
- [Pilot implementation and CI](https://github.com/denis-samatov/mcp-capguard/pull/4)
