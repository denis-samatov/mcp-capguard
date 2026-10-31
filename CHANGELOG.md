# Changelog

## 0.2.0rc1 — unpublished release candidate (2026-10-31)

- Add an opt-in strict mode (`CapabilityProfile(strict=True)` /
  `assert_capability_boundary(..., strict=True)`) that treats `must_expose` as a
  closed allowlist and reports undeclared exposed tools separately. Default
  behavior is unchanged.
- Keep existing required/forbidden/profile APIs and CLI defaults compatible with
  the published GitHub 0.1.2 wheel. This candidate is not a PyPI publication.
- Verify an installed wheel with a strict external typed consumer and real
  default/strict boundary checks; document previous-wheel upgrade acceptance.
- Maintain the isolated Atlassian pilot on a compatible released upstream and
  complete audited hash profile; this checks exposure, not runtime authorization.

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
