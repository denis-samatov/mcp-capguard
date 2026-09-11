"""mcp_capguard: assert that an MCP server's configuration profile exposes
exactly the tools it should, and none it shouldn't.

Not a schema-drift tool (see ``mcpward``/``covenant-mcp`` for that) — a
permission/capability boundary tester. No baseline snapshot required: it
checks the boundary against your declared policy, fresh, every run.
"""

from mcp_capguard.core import assert_capability_boundary, get_exposed_tool_names
from mcp_capguard.exceptions import CapabilityViolation
from mcp_capguard.profiles import CapabilityProfile

__all__ = [
    "CapabilityProfile",
    "CapabilityViolation",
    "assert_capability_boundary",
    "get_exposed_tool_names",
]

__version__ = "0.1.0"
