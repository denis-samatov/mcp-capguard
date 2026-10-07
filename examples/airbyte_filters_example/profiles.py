"""Exercise Airbyte's real tool filters on three local annotated stub tools."""

import os
from dataclasses import dataclass, replace
from unittest.mock import patch

from mcp_capguard import CapabilityProfile


@dataclass(frozen=True)
class Settings:
    read_only: bool = True
    no_destructive: bool = False
    excluded_tools: tuple[str, ...] = ()


class ClientVisibleTools:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def list_tools(self) -> list[str]:
        environment = {
            "MCP_READONLY_MODE": "1" if self.settings.read_only else "0",
            "MCP_NO_DESTRUCTIVE_TOOLS": "1" if self.settings.no_destructive else "0",
            "MCP_EXCLUDE_TOOLS": ",".join(self.settings.excluded_tools),
            "FASTMCP_CHECK_FOR_UPDATES": "off",
            "DO_NOT_TRACK": "1",
        }
        with patch.dict(os.environ, environment, clear=True):
            from fastmcp import Client
            from fastmcp_extensions import mcp_server
            from mcp.types import ToolAnnotations

            server = mcp_server(
                "capguard-filter-example",
                include_standard_tool_filters=True,
                telemetry=False,
            )

            @server.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False))
            def list_items() -> list[str]:
                raise AssertionError("Tool invocation is outside this example")

            @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False))
            def create_item() -> str:
                raise AssertionError("Tool invocation is outside this example")

            @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True))
            def delete_item() -> str:
                raise AssertionError("Tool invocation is outside this example")

            async with Client(server) as client:
                return [tool.name for tool in await client.list_tools()]


def capguard_profiles() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly",
            factory=ClientVisibleTools,
            settings=Settings(),
            must_expose=frozenset({"list_items"}),
            must_not_expose=frozenset({"create_item", "delete_item"}),
        ),
        CapabilityProfile(
            name="no-destructive",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False, no_destructive=True),
            must_expose=frozenset({"list_items", "create_item"}),
            must_not_expose=frozenset({"delete_item"}),
        ),
        CapabilityProfile(
            name="explicit-exclusion",
            factory=ClientVisibleTools,
            settings=Settings(read_only=False, excluded_tools=("create_item", "delete_item")),
            must_expose=frozenset({"list_items"}),
            must_not_expose=frozenset({"create_item", "delete_item"}),
        ),
    ]


def leaking_profiles() -> list[CapabilityProfile]:
    """Turn off the real filter while retaining the readonly declared policy."""
    return [replace(capguard_profiles()[0], settings=Settings(read_only=False))]
