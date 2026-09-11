from __future__ import annotations

from mcp_capguard import CapabilityProfile


class _Server:
    def list_tools(self) -> list[str]:
        return ["search", "delete"]


def load() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly",
            factory=lambda _settings: _Server(),
            settings=None,
            must_not_expose=frozenset({"delete"}),
        )
    ]
