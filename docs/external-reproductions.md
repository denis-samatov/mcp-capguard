# Three projects for independent reproduction

The next useful milestone is an MCP maintainer independently running a declared
tool policy and reporting the outcome. The examples below provide concrete,
credential-free starting points. Local compatibility checks are preparation for
that milestone, not evidence it has happened.

| Project | Why the tool-list boundary matters | Reproduction |
| --- | --- | --- |
| [MCP Atlassian](https://github.com/sooperset/mcp-atlassian) | Readonly and allowlist settings filter the client list at request time | [Real-server pilot](../examples/mcp_atlassian_pilot/README.md), three profiles and a real write-setting negative control |
| [Google Workspace MCP](https://github.com/taylorwilsdon/google_workspace_mcp) | Readonly, per-service permissions and explicit exclusions affect registered tools | [Gmail/Drive adapter](../examples/google_workspace_pilot/README.md), three profiles in fresh processes and a real write-setting negative control |
| [Airbyte FastMCP Extensions](https://github.com/airbytehq/fastmcp-extensions) | Annotation-based filters run through FastMCP middleware | [Library example](../examples/airbyte_filters_example/README.md), three profiles on local stub tools and a real filter-setting negative control |

The Airbyte row concerns a reusable library, not a production connector. The
Workspace row covers Gmail and Drive registration rather than the entire server
startup path. All policies declare particular required/forbidden names; new or
undeclared tools are not automatically prohibited. Execution authorization needs
its own tests.

## What to report

Use the [compatibility report](https://github.com/denis-samatov/mcp-capguard/issues/new?template=compatibility-report.yml)
for either a successful reproduction or a setup failure. Include upstream and
capguard revisions, Python/MCP-library versions, the exact command, and sanitized
output. Do not include credentials, account data or tool results.

A useful first result is: the passing CLI exits 0, the intentional violation exits
1, and pytest exercises both. If an author adopts a test in their own CI, link the
author's confirmation or their public change before recording external adoption.

These examples introduce no runtime dependency into any upstream project. A
maintainer can first try capguard in a development environment and decide whether
the assertion adds value alongside their existing tests.
