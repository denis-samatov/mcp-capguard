"""Minimal fake MCP-like servers for testing ``get_exposed_tool_names``'s
duck-typing, without depending on the real ``mcp`` package in the core test
suite.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FakeTool:
    name: str


class SyncStringServer:
    """``list_tools()`` is sync and returns plain strings."""

    def __init__(self, tools: list[str]) -> None:
        self._tools = tools

    def list_tools(self) -> list[str]:
        return self._tools


class AsyncToolObjectServer:
    """``list_tools()`` is async and returns Tool-like objects with
    ``.name`` — mirrors the real ``mcp`` SDK's shape."""

    def __init__(self, tools: list[str]) -> None:
        self._tools = [FakeTool(name=name) for name in tools]

    async def list_tools(self) -> list[FakeTool]:
        return self._tools


class WrappedServer:
    """Simulates an ``Application``-style wrapper (e.g.
    ``yandex-workspace-mcp``): the real server sits behind a ``.mcp_server``
    attribute, requiring an explicit ``accessor=``."""

    def __init__(self, tools: list[str]) -> None:
        self.mcp_server = AsyncToolObjectServer(tools)
