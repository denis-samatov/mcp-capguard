# mcp-capguard

[![CI](https://github.com/denis-samatov/mcp-capguard/actions/workflows/ci.yml/badge.svg)](https://github.com/denis-samatov/mcp-capguard/actions/workflows/ci.yml)

**Assert that a configuration profile exposes exactly the MCP tools it
should — and none it shouldn't.** A pytest plugin for permission/capability
boundaries, not schema drift.

```python
def test_readonly_hides_destructive_tools(capguard_profile):
    capguard_profile.check_sync()
```

## The problem this solves

Any MCP server that gates tools behind settings — read-only vs. read-write,
authenticated vs. not, feature flags — can silently regress: a refactor adds
a new write tool, and it leaks into a profile that was supposed to stay
read-only. Nothing throws. The agent just gets a tool it shouldn't have.

capguard turns that into a CI failure, checked fresh on every run — no
prior snapshot required.

## Scope

capguard checks a declared tool policy against each configuration profile at
test time. It does not compare a server to a previous snapshot or check tool
schemas or behavior. The permission test follows the same pattern as
[`check_tool_matrix.py`](https://github.com/denis-samatov/yandex-workspace-mcp/blob/main/scripts/check_tool_matrix.py)
in `yandex-workspace-mcp`; this library makes that pattern reusable.

## How it works

capguard is **in-process only** in this release: it imports your server
factory and calls it directly with different settings objects, the same way
your own test suite would. No subprocess spawning, no stdio/HTTP transport
— just a function call per profile. Runtime depends on your server factory and
its tool-listing implementation.

Your server only needs to satisfy one contract:

```python
def factory(settings: Any) -> Any: ...  # returns a server with .list_tools()
```

`list_tools()` can be sync or async, and can return either plain strings or
tool objects with a `.name` attribute (like `mcp.types.Tool`). If your
factory returns a wrapper object (e.g. an `Application` whose real server
lives at `.mcp_server`), pass `accessor=lambda app: app.mcp_server` — explicit,
not guessed.

## Install from source

Clone the repository and install it in a virtual environment:

```bash
git clone https://github.com/denis-samatov/mcp-capguard.git
cd mcp-capguard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .
```

The optional FastMCP example needs the development dependencies:

```bash
python -m pip install -e '.[dev]'
```

## Quick start

`conftest.py` (or any module — point `capguard_profiles` at it):

```python
from mcp_capguard import CapabilityProfile
from myserver import create_app, Settings

def capguard_profiles() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly",
            factory=create_app,
            settings=Settings(write_enabled=False),
            must_expose=frozenset({"search", "get_document"}),
            must_not_expose=frozenset({"delete_document", "send_email"}),
        ),
        CapabilityProfile(
            name="editor",
            factory=create_app,
            settings=Settings(write_enabled=True, admin_enabled=False),
            must_expose=frozenset({"search", "get_document", "update_document"}),
            must_not_expose=frozenset({"delete_workspace"}),
        ),
    ]
```

`pytest.ini` (or the `[tool.pytest.ini_options]` table in `pyproject.toml`):

```ini
[pytest]
capguard_profiles = conftest:capguard_profiles
```

Any test file:

```python
def test_capability_boundary(capguard_profile):
    capguard_profile.check_sync()
```

Run `pytest` — one test is generated per profile, and a failure names the
specific profile and the specific tool that broke the policy.

A complete, runnable version of this against the real `mcp` SDK's
`MCPServer` lives in [`examples/fastmcp_example`](examples/fastmcp_example) —
including a server where a destructive tool is conditionally registered, so
you can see capguard catch the exact regression it's built for.

## CLI

For CI systems that don't run pytest directly:

```bash
capguard check --profiles conftest:capguard_profiles
```

## API reference

- **`CapabilityProfile(name, factory, settings, must_expose=frozenset(), must_not_expose=frozenset(), accessor=None)`**
  — a declarative profile. `.check()` (async) and `.check_sync()` run it.
- **`get_exposed_tool_names(factory, settings, *, accessor=None) -> set[str]`**
  — the low-level introspection primitive, usable directly without the
  profile/plugin machinery.
- **`assert_capability_boundary(exposed, *, must_expose=(), must_not_expose=(), profile_name=None)`**
  — the assertion primitive. Raises `CapabilityViolation` (an
  `AssertionError` subclass) carrying `.missing`, `.forbidden`, and
  `.exposed` as sets, so tooling can render its own report instead of
  parsing a message string.

## What this doesn't do (yet)

- **Black-box mode.** Testing a server you didn't write, over stdio/HTTP,
  the way `mcpward`/`covenant-mcp` do — deliberately out of scope for this
  release. It's a different mechanism (subprocess + protocol handshake per
  profile) and would dilute the one thing this tool does well.
- **Schema-drift detection.** Not the goal here — see the comparison table
  above.
- **YAML-driven settings construction.** Real `Settings` classes carry
  secrets and validators that don't round-trip through YAML safely; you
  construct them in Python, same as any other test fixture.


## License

MIT
