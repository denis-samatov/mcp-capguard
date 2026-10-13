from __future__ import annotations

from mcp_capguard import CapabilityProfile


class _Server:
    def list_tools(self) -> list[str]:
        return ["search", "export"]


def load() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly-strict",
            factory=lambda _settings: _Server(),
            settings=None,
            must_expose=frozenset({"search"}),
            must_not_expose=frozenset({"delete"}),
            strict=True,
        )
    ]


def load_passing() -> list[CapabilityProfile]:
    return [
        CapabilityProfile(
            name="readonly-strict",
            factory=lambda _settings: _Server(),
            settings=None,
            must_expose=frozenset({"search", "export"}),
            must_not_expose=frozenset({"delete"}),
            strict=True,
        )
    ]
