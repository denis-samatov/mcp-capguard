# Changelog

## 0.1.2

- Include the PEP 561 `py.typed` marker so consumer projects can type-check
  capguard imports. Verify an installed wheel from outside the source checkout.
- Align the public `__version__` with package metadata and check both in CI.
- Add reproducible, isolated pilots for pinned Yandex Workspace MCP and
  MCP Atlassian revisions, including real write-setting negative controls.
- Publish a practical article on client-visible tool-list boundaries and a
  compatibility report form for reproducible feedback.
- Document installation of the GitHub release wheel without cloning.

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
