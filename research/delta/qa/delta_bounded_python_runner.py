"""Crash-contained runner for DELTA bounded Python research jobs.

Each invocation uses an isolated Numba cache, enables faulthandler/unbuffered output,
starts the producer in its own process group/session, and applies a hard wall-clock
timeout. On timeout or interruption, the runner terminates the entire child group so
compiler/helper descendants cannot survive into the next bounded unit.

Scientific producers remain responsible for atomic result writes.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time


def terminate_process_tree(proc: subprocess.Popen[bytes], grace: float) -> None:
    """Best-effort terminate the producer and descendants, then escalate to kill."""
    if proc.poll() is not None:
        return

    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            proc.wait(timeout=grace)
            return
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
            proc.wait()
            return

    # Windows / non-POSIX fallback. CREATE_NEW_PROCESS_GROUP isolates the child group,
    # but Python's portable hard-stop primitive remains proc.kill().
    proc.kill()
    proc.wait()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--grace", type=float, default=5.0)
    ap.add_argument("command", nargs=argparse.REMAINDER)
    ns = ap.parse_args()

    cmd = list(ns.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        ap.error("a command is required after --")
    if ns.timeout <= 0:
        ap.error("--timeout must be > 0")
    if ns.grace < 0:
        ap.error("--grace must be >= 0")

    with tempfile.TemporaryDirectory(
        prefix="delta_numba_cache_", ignore_cleanup_errors=True
    ) as cache_dir:
        env = os.environ.copy()
        env["NUMBA_CACHE_DIR"] = cache_dir
        env["PYTHONFAULTHANDLER"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        kwargs: dict[str, object] = {"env": env}
        if os.name == "posix":
            kwargs["start_new_session"] = True
        elif os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        started = time.monotonic()
        proc = subprocess.Popen(cmd, **kwargs)
        try:
            rc = proc.wait(timeout=ns.timeout)
        except subprocess.TimeoutExpired:
            terminate_process_tree(proc, ns.grace)
            elapsed = time.monotonic() - started
            print(
                "DELTA_BOUNDED_RUNNER_TIMEOUT "
                f"seconds={ns.timeout:g} elapsed={elapsed:.3f} command={cmd!r}",
                file=sys.stderr,
            )
            return 124
        except KeyboardInterrupt:
            terminate_process_tree(proc, ns.grace)
            print(
                f"DELTA_BOUNDED_RUNNER_INTERRUPTED command={cmd!r}",
                file=sys.stderr,
            )
            return 130

        elapsed = time.monotonic() - started
        print(
            "DELTA_BOUNDED_RUNNER_EXIT "
            f"returncode={rc} elapsed={elapsed:.3f} command={cmd!r}",
            file=sys.stderr,
        )
        return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
