"""``capguard`` CLI: run capability-boundary checks outside pytest, for CI
systems that don't run pytest directly.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import os
import sys
from collections.abc import Sequence

from mcp_capguard.exceptions import CapabilityViolation
from mcp_capguard.profiles import CapabilityProfile


def _load_profiles(target: str) -> list[CapabilityProfile]:
    module_path, _, attr = target.partition(":")
    if not attr:
        raise SystemExit(f"--profiles must be 'module:function', got {target!r}")

    # Console-script entry points don't get the current directory on
    # sys.path the way `python -m` / pytest do — add it so `--profiles
    # conftest:capguard_profiles` works when run from a project directory.
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    module = importlib.import_module(module_path)
    loader = getattr(module, attr)
    return list(loader())


async def _run(profiles: Sequence[CapabilityProfile]) -> int:
    exit_code = 0
    for profile in profiles:
        try:
            await profile.check()
        except CapabilityViolation as violation:
            exit_code = 1
            print(profile.name)
            for tool in sorted(violation.missing):
                print(f"  ✗ {tool} expected but not exposed")
            for tool in sorted(violation.forbidden):
                print(f"  ✗ {tool} unexpectedly exposed")
            print()
            print("SECURITY REGRESSION")
            for tool in sorted(violation.forbidden):
                print(f"  {profile.name} → {tool}")
        else:
            print(profile.name)
            print(f"  ✓ {len(profile.must_expose)} expected tool(s) exposed")
            print(f"  ✓ {len(profile.must_not_expose)} destructive tool(s) hidden")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capguard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Run capability boundary checks.")
    check_parser.add_argument(
        "--profiles",
        required=True,
        help=(
            "Import path (module:function) to a zero-arg callable "
            "returning a list[CapabilityProfile]."
        ),
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        profiles = _load_profiles(args.profiles)
        return asyncio.run(_run(profiles))
    return 1


if __name__ == "__main__":
    sys.exit(main())
