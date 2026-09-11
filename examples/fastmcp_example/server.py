"""A tiny example MCP server with a read/write permission flag — the kind of
server capguard is built for.

Two tools are always exposed; `delete_document` only exists when
`write_enabled=True`. That's the exact class of bug capguard catches: if a
refactor ever makes `delete_document` register regardless of the flag, the
`readonly` profile's `must_not_expose` check fails immediately.
"""

from __future__ import annotations

from dataclasses import dataclass

from mcp.server.mcpserver import MCPServer


@dataclass(frozen=True)
class Settings:
    write_enabled: bool = False


def create_server(settings: Settings) -> MCPServer:
    server = MCPServer("example-docs")

    @server.tool()
    def search(query: str) -> str:
        """Search documents."""
        return f"results for {query!r}"

    @server.tool()
    def get_document(doc_id: str) -> str:
        """Fetch a document by id."""
        return f"contents of {doc_id!r}"

    if settings.write_enabled:

        @server.tool()
        def delete_document(doc_id: str) -> str:
            """Permanently delete a document."""
            return f"deleted {doc_id!r}"

    return server
