# SPDX-License-Identifier: MIT
# MIT License
#
# Copyright (c) 2026 Denis Samatov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Reproduce a read-only MCP tool exposure regression for Agent Research Commons.

With Python 3.10+ and Git, install the pinned mcp-capguard source and run:

    python -m pip install "mcp-capguard @ git+https://github.com/denis-samatov/mcp-capguard.git@411f74939947419c089eeb7ab71bfc3a4f7985b5"
    python arc_capguard_example.py

The six checks compare three synthetic tool catalogs with a read-only
exposure policy in default and strict modes. The catalogs model the names
returned by tools/list. The checks do not connect to an MCP server, invoke
tools, or test tool invocation authorization end to end. The script exits
with status zero only if all six checks produce the expected outcome.
"""

from mcp_capguard import CapabilityViolation, assert_capability_boundary

REQUIRED = frozenset({"search", "get_document"})
FORBIDDEN = frozenset({"delete_document"})


def main() -> None:
    cases = (
        ("baseline", REQUIRED, "accepted", "accepted"),
        (
            "delete leak",
            REQUIRED | {"delete_document"},
            "forbidden: delete_document",
            "forbidden: delete_document",
        ),
        (
            "new share tool",
            REQUIRED | {"share_document"},
            "accepted",
            "undeclared: share_document",
        ),
    )
    for label, exposed, expected_default, expected_strict in cases:
        for strict, expected in ((False, expected_default), (True, expected_strict)):
            try:
                assert_capability_boundary(
                    exposed,
                    must_expose=REQUIRED,
                    must_not_expose=FORBIDDEN,
                    profile_name="readonly",
                    strict=strict,
                )
            except CapabilityViolation as error:
                actual = ", ".join(
                    f"{kind}: {tool}"
                    for kind, names in (
                        ("missing", error.missing),
                        ("forbidden", error.forbidden),
                        ("undeclared", error.undeclared),
                    )
                    for tool in sorted(names)
                )
            else:
                actual = "accepted"

            if actual != expected:
                raise AssertionError(f"{label}, {strict=}: expected {expected!r}, got {actual!r}")
            print(f"{label}, {strict=}: {actual}")


if __name__ == "__main__":
    main()
