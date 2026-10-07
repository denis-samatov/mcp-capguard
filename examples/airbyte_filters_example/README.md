# Airbyte FastMCP Extensions: client-visible filter contracts

This is a local example using the real filter implementation from
[Airbyte FastMCP Extensions](https://github.com/airbytehq/fastmcp-extensions/tree/b9d5754f2c36831055de373c1a77e15e306caf99).
It is a library example, not an Airbyte connector/server deployment pilot.

The adapter builds a new server with the library's standard filters and three
annotated stub tools: read, non-destructive write, and destructive write. Each
stub raises if invoked. An in-memory FastMCP Client lists tools through the real
middleware. Telemetry is disabled, and filter environment variables are isolated
for each sequential check. Pytest blocks TCP sockets.

## Reproduce

From the capguard repository root, use a separate Python 3.12 environment:

```bash
uv venv --python 3.12 .venv-airbyte-example
uv pip install --python .venv-airbyte-example/bin/python -e . -r examples/airbyte_filters_example/requirements.txt
cd examples/airbyte_filters_example
../../.venv-airbyte-example/bin/python -m pytest -v
../../.venv-airbyte-example/bin/capguard check --profiles profiles:capguard_profiles
../../.venv-airbyte-example/bin/capguard check --profiles profiles:leaking_profiles
```

The last command intentionally exits **1** and names `create_item` and
`delete_item`. Pytest should report **4 passed**: three policies plus the negative
control that disables the real filter while retaining the readonly policy.

| Profile | Required | Forbidden |
| --- | --- | --- |
| `readonly` | `list_items` | `create_item`, `delete_item` |
| `no-destructive` | `list_items`, `create_item` | `delete_item` |
| `explicit-exclusion` | `list_items` | `create_item`, `delete_item` |

Locally verified on Python 3.12.14, FastMCP 4.0.9 and MCP SDK 2.2.0. The requirements
pin upstream commit and the two MCP libraries; other transitive dependencies are
resolved on installation. Run these profiles serially because the filter
environment is process-wide.

Annotations are inputs to the upstream filters. A visibility assertion does not
prove that annotations correctly describe a tool's behavior or that runtime
authorization is enforced. No tool is called, and no external adoption is claimed.
