"""Core capability-boundary primitives: extract exposed tool names from a
server built in-process, and assert they satisfy a profile's expectations.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable
from typing import Any

from mcp_capguard.exceptions import CapabilityViolation


def _tool_name(tool: Any) -> str:
    if isinstance(tool, str):
        return tool
    name = getattr(tool, "name", None)
    if isinstance(name, str):
        return name
    raise TypeError(
        f"Cannot determine a tool name from {tool!r}. "
        "Expected a str or an object with a string `.name` attribute."
    )


def _normalize_tool_names(tools: Iterable[Any]) -> set[str]:
    return {_tool_name(tool) for tool in tools}


async def get_exposed_tool_names(
    factory: Callable[[Any], Any],
    settings: Any,
    *,
    accessor: Callable[[Any], Any] | None = None,
) -> set[str]:
    """Build a server with ``factory(settings)``, optionally unwrap it with
    ``accessor`` (for wrapper objects like ``Application.mcp_server``), then
    call its ``list_tools()`` — sync or async — and return the exposed tool
    names as a set of strings.

    Raises ``TypeError`` if the resulting object has no ``list_tools``
    method, naming the object so the mistake (usually a missing
    ``accessor=``) is obvious.
    """
    server = factory(settings)
    if inspect.isawaitable(server):
        server = await server
    if accessor is not None:
        server = accessor(server)

    list_tools = getattr(server, "list_tools", None)
    if list_tools is None:
        raise TypeError(
            f"{server!r} has no `list_tools` method. "
            "Pass `accessor=` to unwrap it from whatever `factory` returned."
        )

    result = list_tools()
    if inspect.isawaitable(result):
        result = await result

    return _normalize_tool_names(result)


def assert_capability_boundary(
    exposed: Iterable[Any],
    *,
    must_expose: Iterable[str] = (),
    must_not_expose: Iterable[str] = (),
    profile_name: str | None = None,
) -> None:
    """Assert that ``exposed`` satisfies the capability boundary: every tool
    in ``must_expose`` is present, and no tool in ``must_not_expose`` is
    present.

    ``exposed`` may be plain strings or tool-like objects with a ``.name``
    attribute (e.g. ``mcp.types.Tool``).

    Raises ``CapabilityViolation`` (an ``AssertionError`` subclass) carrying
    the specific missing and forbidden tool names on failure.
    """
    exposed_names = _normalize_tool_names(exposed)
    must_expose_set = set(must_expose)
    must_not_expose_set = set(must_not_expose)

    missing = must_expose_set - exposed_names
    forbidden = must_not_expose_set & exposed_names

    if missing or forbidden:
        raise CapabilityViolation(
            profile_name=profile_name,
            missing=missing,
            forbidden=forbidden,
            exposed=exposed_names,
        )
