"""Run and type-check this file outside the checkout against an installed wheel."""

import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

import mcp_capguard
from mcp_capguard import (
    CapabilityProfile,
    CapabilityViolation,
    __version__,
    assert_capability_boundary,
    get_exposed_tool_names,
)


class Server:
    async def list_tools(self) -> list[str]:
        return ["read", "export"]


def factory(settings: object) -> Server:
    return Server()


async def check_async_profile() -> None:
    names: set[str] = await get_exposed_tool_names(factory, None)
    assert names == {"read", "export"}
    profile = CapabilityProfile(
        name="allowlist",
        factory=factory,
        settings=None,
        must_expose=frozenset({"read"}),
        strict=True,
    )
    try:
        await profile.check()
    except CapabilityViolation as exc:
        undeclared: set[str] = exc.undeclared
        assert undeclared == {"export"}
    else:
        raise AssertionError("strict profile accepted an undeclared tool")


def main() -> None:
    assert __version__ == version("mcp-capguard")
    assert Path(mcp_capguard.__file__ or "").resolve().is_relative_to(Path(sys.prefix).resolve())
    # Existing open-world default accepts an undeclared tool.
    assert_capability_boundary({"read", "export"}, must_expose={"read"})
    try:
        assert_capability_boundary({"read", "export"}, must_expose={"read"}, strict=True)
    except CapabilityViolation as exc:
        assert exc.undeclared == {"export"}
        assert exc.missing == exc.forbidden == set()
    else:
        raise AssertionError("strict function accepted an undeclared tool")
    asyncio.run(check_async_profile())
    CapabilityProfile(
        name="default", factory=factory, settings=None, must_expose=frozenset({"read"})
    ).check_sync()


if __name__ == "__main__":
    main()
