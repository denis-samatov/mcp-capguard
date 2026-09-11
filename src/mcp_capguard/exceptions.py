"""Exceptions raised by mcp_capguard."""

from __future__ import annotations


class CapabilityViolation(AssertionError):
    """Raised when a server's exposed tools violate a capability boundary.

    Carries the specific missing and forbidden tool names as structured
    fields so both pytest output and the CLI report can render from the
    same data, instead of re-parsing a formatted message.
    """

    def __init__(
        self,
        *,
        missing: set[str],
        forbidden: set[str],
        exposed: set[str],
        profile_name: str | None = None,
    ) -> None:
        self.profile_name = profile_name
        self.missing = missing
        self.forbidden = forbidden
        self.exposed = exposed
        super().__init__(self._render())

    def _render(self) -> str:
        suffix = f" ({self.profile_name})" if self.profile_name else ""
        lines = [f"capability boundary violated{suffix}"]
        for tool in sorted(self.missing):
            lines.append(f"  ✗ {tool} expected but not exposed")
        for tool in sorted(self.forbidden):
            lines.append(f"  ✗ {tool} unexpectedly exposed")
        return "\n".join(lines)
