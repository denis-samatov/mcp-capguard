"""Show a passing readonly profile and an intentionally leaked delete tool."""

from __future__ import annotations

import argparse

from mcp.server.mcpserver import MCPServer
from server import Settings, create_server

from mcp_capguard import CapabilityProfile, CapabilityViolation


def create_leaky_server(_settings: Settings) -> MCPServer:
    """Simulate a refactor that ignores the readonly setting."""
    return create_server(Settings(write_enabled=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--leak-delete", action="store_true", help="Intentionally expose delete in readonly mode."
    )
    args = parser.parse_args()
    profile = CapabilityProfile(
        name="readonly",
        factory=create_leaky_server if args.leak_delete else create_server,
        settings=Settings(write_enabled=False),
        must_expose=frozenset({"search", "get_document"}),
        must_not_expose=frozenset({"delete_document"}),
    )
    try:
        profile.check_sync()
    except CapabilityViolation as error:
        print(error)
        return 1
    print("PASS: readonly exposes search and get_document; delete_document is hidden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
