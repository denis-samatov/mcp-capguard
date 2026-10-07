"""Capability policies against the real Yandex Workspace application factory."""

import os
from dataclasses import replace
from unittest.mock import patch

from yandex_workspace_mcp.config import Settings
from yandex_workspace_mcp.server import create_application

from mcp_capguard import CapabilityProfile

READ_TOOLS = frozenset({"search", "fetch", "disk_list", "wiki_get_page"})
WRITE_TOOLS = frozenset(
    {
        "disk_copy",
        "disk_create_folder",
        "disk_move",
        "disk_publish",
        "disk_rename",
        "disk_unpublish",
        "disk_upload",
        "wiki_add_comment",
        "wiki_add_grid_columns",
        "wiki_add_grid_rows",
        "wiki_append_page",
        "wiki_clone_page",
        "wiki_copy_grid",
        "wiki_create_grid",
        "wiki_create_page",
        "wiki_move_grid_column",
        "wiki_move_grid_row",
        "wiki_update_grid",
        "wiki_update_grid_cells",
        "wiki_update_page",
    }
)
DELETE_TOOLS = frozenset(
    {
        "disk_delete",
        "disk_restore_from_trash",
        "wiki_delete_grid",
        "wiki_delete_grid_columns",
        "wiki_delete_grid_rows",
        "wiki_delete_page",
        "wiki_recover_page",
    }
)


def capguard_profiles() -> list[CapabilityProfile]:
    # These are registration checks: no application lifespan or API client is opened.
    # Do not inherit credentials or permission flags from the operator's environment.
    with patch.dict(os.environ, {}, clear=True):
        readonly = Settings(_env_file=None, disk_allowed_roots=["/"], wiki_allowed_roots=["/"])
    editor = readonly.model_copy(update={"disk_write": True, "wiki_write": True})
    disabled = readonly.model_copy(
        update={"yandex_disk_enabled": False, "yandex_wiki_enabled": False}
    )
    return [
        CapabilityProfile(
            name="readonly",
            factory=create_application,
            settings=readonly,
            accessor=lambda app: app.mcp_server,
            must_expose=READ_TOOLS,
            must_not_expose=WRITE_TOOLS | DELETE_TOOLS,
        ),
        CapabilityProfile(
            name="editor-no-delete",
            factory=create_application,
            settings=editor,
            accessor=lambda app: app.mcp_server,
            must_expose=READ_TOOLS | WRITE_TOOLS,
            must_not_expose=DELETE_TOOLS,
        ),
        CapabilityProfile(
            name="services-disabled",
            factory=create_application,
            settings=disabled,
            accessor=lambda app: app.mcp_server,
            must_expose=frozenset({"search", "fetch"}),
            must_not_expose=(READ_TOOLS - {"search", "fetch"}) | WRITE_TOOLS | DELETE_TOOLS,
        ),
    ]


def leaking_profiles() -> list[CapabilityProfile]:
    """Deliberately misconfigure the real server while keeping the readonly policy."""
    readonly = capguard_profiles()[0]
    return [replace(readonly, settings=readonly.settings.model_copy(update={"wiki_write": True}))]
