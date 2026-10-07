# Changelog

## 0.1.1

- Add a runnable demo using the real Python MCP SDK: a valid readonly profile
  exits successfully, while an injected delete-tool exposure exits with an error.
- Exercise both documented demo commands in the test suite.
- Require Python MCP SDK v2 for the development extra and demo imports.
- Document installation directly from GitHub and commit pinning for CI.
- Clarify that only explicitly required or forbidden tools are checked;
  undeclared tools and runtime authorization are outside the check.

## 0.1.0

- Initial pytest plugin, CLI, and in-process capability profile API.
