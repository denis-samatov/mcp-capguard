"""Inspect real Gmail/Drive tools in a fresh, credential-free process per profile."""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from mcp_capguard import CapabilityProfile

READ_TOOLS = frozenset(
    {"search_gmail_messages", "list_gmail_labels", "search_drive_files", "list_drive_items"}
)
WRITE_TOOLS = frozenset(
    {"send_gmail_message", "draft_gmail_message", "create_drive_folder", "create_drive_file"}
)


@dataclass(frozen=True)
class Settings:
    read_only: bool = True
    permissions: tuple[str, ...] = ()
    disabled_tools: tuple[str, ...] = ()


class ClientVisibleTools:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def list_tools(self) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="capguard-workspace-") as directory:
            environment = {
                "PATH": os.environ.get("PATH", os.defpath),
                "LANG": "C.UTF-8",
                "WORKSPACE_MCP_CREDENTIALS_DIR": directory,
                "MCP_ENABLE_OAUTH21": "false",
                "MCP_SINGLE_USER_MODE": "true",
                "PYTHON_DOTENV_DISABLED": "1",
                "FASTMCP_CHECK_FOR_UPDATES": "off",
                "DO_NOT_TRACK": "1",
            }
            result = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, str(Path(__file__).resolve()), json.dumps(asdict(self.settings))],
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        return json.loads(result.stdout)


def capguard_profiles() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="gmail-drive-readonly",
            factory=ClientVisibleTools,
            settings=Settings(),
            must_expose=READ_TOOLS,
            must_not_expose=WRITE_TOOLS,
        ),
        CapabilityProfile(
            name="organize-gmail-readonly-drive",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False, permissions=("gmail:organize", "drive:readonly")),
            must_expose=READ_TOOLS | {"modify_gmail_message_labels"},
            must_not_expose=WRITE_TOOLS,
        ),
        CapabilityProfile(
            name="full-with-send-blocked",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False, disabled_tools=("send_gmail_message",)),
            must_expose=READ_TOOLS | (WRITE_TOOLS - {"send_gmail_message"}),
            must_not_expose=frozenset({"send_gmail_message"}),
        ),
    ]


def leaking_profiles() -> list[CapabilityProfile]:
    """Disable the real readonly filter while keeping the readonly assertion."""
    return [replace(capguard_profiles()[0], settings=Settings(read_only=False))]


async def _list_in_worker(settings: Settings) -> list[str]:
    from importlib import import_module

    from auth.permissions import parse_permissions_arg, set_permissions
    from auth.scopes import set_enabled_tools, set_read_only
    from core.server import server
    from core.tool_registry import (
        filter_server_tools,
        set_disabled_tools,
        wrap_server_tool_method,
    )
    from core.tool_registry import (
        set_enabled_tools as set_enabled_tool_names,
    )
    from fastmcp import Client

    # Follow the Gmail/Drive registration and filtering sequence in main.main().
    set_enabled_tool_names(None)
    set_disabled_tools(set(settings.disabled_tools))
    set_enabled_tools(["gmail", "drive"])
    set_read_only(settings.read_only)
    set_permissions(
        parse_permissions_arg(list(settings.permissions)) if settings.permissions else None
    )
    wrap_server_tool_method(server)
    import_module("gmail.gmail_tools")
    import_module("gdrive.drive_tools")
    filter_server_tools(server)
    async with Client(server) as client:
        return [tool.name for tool in await client.list_tools()]


if __name__ == "__main__":
    from unittest.mock import patch

    payload = json.loads(sys.argv[1])
    settings = Settings(
        read_only=payload["read_only"],
        permissions=tuple(payload["permissions"]),
        disabled_tools=tuple(payload["disabled_tools"]),
    )
    # Block connections inside the subprocess too; pytest patches do not cross processes.
    with (
        patch("socket.socket.connect", side_effect=RuntimeError("Offline pilot: socket blocked")),
        patch(
            "socket.socket.connect_ex", side_effect=RuntimeError("Offline pilot: socket blocked")
        ),
    ):
        print(json.dumps(asyncio.run(_list_in_worker(settings))))
