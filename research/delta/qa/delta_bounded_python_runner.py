"""Crash-contained runner for DELTA bounded Python research jobs.

Creates an isolated Numba cache for every invocation and applies a hard subprocess
wall-clock timeout. Scientific producers remain responsible for atomic result writes.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("command", nargs=argparse.REMAINDER)
    ns = ap.parse_args()
    cmd = list(ns.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        ap.error("a command is required after --")
    if ns.timeout <= 0:
        ap.error("--timeout must be > 0")

    with tempfile.TemporaryDirectory(prefix="delta_numba_cache_", ignore_cleanup_errors=True) as cache_dir:
        env = os.environ.copy()
        env["NUMBA_CACHE_DIR"] = cache_dir
        env["PYTHONFAULTHANDLER"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        try:
            cp = subprocess.run(cmd, env=env, timeout=ns.timeout, check=False)
        except subprocess.TimeoutExpired:
            print(
                f"DELTA_BOUNDED_RUNNER_TIMEOUT seconds={ns.timeout:g} command={cmd!r}",
                file=sys.stderr,
            )
            return 124
        return int(cp.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
