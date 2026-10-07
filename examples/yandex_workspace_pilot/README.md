# Yandex Workspace MCP pilot

This runs capguard against the real
[`yandex-workspace-mcp` application factory](https://github.com/denis-samatov/yandex-workspace-mcp/tree/9146882088ed8528e5d245337ea27d0c6d570c97),
using `accessor=lambda app: app.mcp_server`. The upstream commit and MCP SDK
version are pinned in `requirements.txt`. Python 3.12 is required for this pilot.

From the capguard repository root (Linux/macOS, with `uv` installed):

```bash
uv venv --python 3.12 .venv-yandex
uv pip install --python .venv-yandex/bin/python -e . -r examples/yandex_workspace_pilot/requirements.txt
cd examples/yandex_workspace_pilot
../../.venv-yandex/bin/python -m pytest -q
../../.venv-yandex/bin/capguard check --profiles profiles:capguard_profiles
```

The three profiles pass. At the pinned commit, the observed tool counts are:

| Profile | Observed tools | Declared boundary |
| --- | ---: | --- |
| readonly | 19 | Required read tools; declared write and delete tools absent |
| editor-no-delete | 39 | Required read/write tools; declared delete tools absent |
| services-disabled | 2 | `search` and `fetch` remain; declared service tools absent |

Counts are observations, not assertions. The policies assert names, and allow
undeclared tools. Review these lists whenever upstream adds a tool.

The negative control changes the actual server configuration to enable Wiki
writing while retaining the readonly policy:

```bash
../../.venv-yandex/bin/capguard check --profiles profiles:leaking_profiles
```

It must exit **1**, naming `wiki_create_page` and other forbidden write tools.
The fourth pytest test verifies this intentional violation; pytest itself exits 0.

No credentials are needed. Settings are built without environment overrides or
a dotenv file. This checks registration without opening the application lifespan
or calling any tool. The pytest configuration blocks TCP sockets. It does not
verify API access, runtime authorization, or resource path enforcement. This is
a compatibility pilot maintained here, not an upstream integration or adoption claim.
