"""mcp_capguard: check required and forbidden tools for a configuration profile.

Use opt-in strict mode to reject every undeclared tool as well.

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

__version__ = "0.2.0rc1"
