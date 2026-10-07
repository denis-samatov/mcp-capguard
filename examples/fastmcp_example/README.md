# Catch a readonly regression

This example uses the real Python MCP SDK in-process. It needs no credentials,
network connection, or running MCP client. The tools return illustrative strings;
the demo never calls them or deletes documents.

From the repository root:

```bash
python -m pip install -e '.[dev]'
python examples/fastmcp_example/demo.py
```

Expected output, exit code `0`:

```text
PASS: readonly exposes search and get_document; delete_document is hidden.
```

Now simulate a factory that ignores `write_enabled=False`:

```bash
python examples/fastmcp_example/demo.py --leak-delete
```

Expected output, exit code `1`:

```text
capability boundary violated (readonly)
  ✗ delete_document unexpectedly exposed
```

The nonzero exit code is intentional: CI can reject the change. The policy and
settings remain the same; only the server factory changes. See `create_leaky_server`
in [demo.py](demo.py) for the injected mistake.

For the pytest integration, run `python -m pytest -v examples/fastmcp_example`
from the repository root. The existing profiles check readonly and editor modes.

capguard checks the required and forbidden tool names you declare. Undeclared
tools are not rejected automatically, and a tool-list check does not validate
runtime authorization or tool execution.
