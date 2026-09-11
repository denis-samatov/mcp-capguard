from mcp_capguard import CapabilityProfile

from server import Settings, create_server


def capguard_profiles() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly",
            factory=create_server,
            settings=Settings(write_enabled=False),
            must_expose=frozenset({"search", "get_document"}),
            must_not_expose=frozenset({"delete_document"}),
        ),
        CapabilityProfile(
            name="editor",
            factory=create_server,
            settings=Settings(write_enabled=True),
            must_expose=frozenset({"search", "get_document", "delete_document"}),
        ),
    ]
