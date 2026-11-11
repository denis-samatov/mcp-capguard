# Catch an accidentally exposed MCP tool in one minute

A read-only configuration can regress when a refactor registers a write tool. mcp-capguard checks a declared tool exposure policy and makes that mismatch fail a test or CLI check.

## Reproduce the demonstration

The following source revision was checked on 11 November 2026 with Python 3.12.14, MCP 2.3.0 and pytest 9.2.0:

```bash
git clone https://github.com/denis-samatov/mcp-capguard.git
cd mcp-capguard
git checkout ad2e4b48895830e43633622bdc5da9eace738966
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python examples/fastmcp_example/demo.py
python examples/fastmcp_example/demo.py --leak-delete
```

Observed normal output (exit 0):

```text
PASS: readonly exposes search and get_document; delete_document is hidden.
```

Observed intentional regression (exit 1):

```text
capability boundary violated (readonly)
  ✗ delete_document unexpectedly exposed
```

The second command is expected to fail: that is the demonstration's successful negative control. No API keys or running remote server are required.

`pytest -q` at this revision: **32 passed**, with three pytest-asyncio fixture-loop configuration deprecation warnings in the plugin tests.

## A 60-second presentation

- 0–15 seconds: show the readonly policy and explain which tools it requires and prohibits.
- 15–30 seconds: run the normal demo and show exit 0.
- 30–45 seconds: run with `--leak-delete`; show the specific offending tool and exit 1.
- 45–60 seconds: explain that the same assertion can run in CI and invite maintainers to reproduce it on their server.

## Scope and versions

This checks exposed tool names, not execution-time authorization or tool behavior. Default policies only check explicitly required and prohibited names. Source version 0.2.0rc1 additionally offers strict allowlist checking; the published v0.1.2 wheel does not have that API. This walkthrough uses the pinned source revision, not a claim that a new release has been published.

Existing upstream compatibility examples are not evidence of upstream adoption. For an independent reproduction, report your revisions, command, result and sanitized output using the [compatibility report](https://github.com/denis-samatov/mcp-capguard/issues/new?template=compatibility-report.yml).
