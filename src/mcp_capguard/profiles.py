"""Declarative capability profiles: one named configuration under test, with
the tool-surface boundary it must satisfy.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CapabilityProfile:
    """One named configuration under test.

    Build the server with ``factory(settings)`` (optionally unwrapped with
    ``accessor``), then assert the resulting tool surface exposes every tool
    in ``must_expose`` and none in ``must_not_expose``.
    """

    name: str
    factory: Callable[[Any], Any]
    settings: Any
    must_expose: frozenset[str] = field(default_factory=frozenset)
    must_not_expose: frozenset[str] = field(default_factory=frozenset)
    accessor: Callable[[Any], Any] | None = None

    async def check(self) -> None:
        """Run the boundary check. Raises ``CapabilityViolation`` on
        failure."""
        from mcp_capguard.core import assert_capability_boundary, get_exposed_tool_names

        exposed = await get_exposed_tool_names(self.factory, self.settings, accessor=self.accessor)
        assert_capability_boundary(
            exposed,
            must_expose=self.must_expose,
            must_not_expose=self.must_not_expose,
            profile_name=self.name,
        )

    def check_sync(self) -> None:
        """Synchronous convenience wrapper around ``check()``, for test
        functions that don't want a dependency on pytest-asyncio."""
        asyncio.run(self.check())
