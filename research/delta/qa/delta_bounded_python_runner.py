"""Crash-contained runner for DELTA bounded Python research jobs.

Each invocation uses an isolated Numba cache, enables faulthandler/unbuffered output,
starts the producer in its own process group/session, and applies a hard wall-clock
timeout. On timeout or interruption, the runner terminates the entire child group.

Linux adds a PR_SET_PDEATHSIG trampoline: if an outer transport/tool kills this
runner before its own cleanup executes, the kernel delivers SIGTERM to the producer
when the runner dies. This prevents orphaned research processes after message/tool
delivery timeouts.

Scientific producers remain responsible for atomic result writes.
"""
from __future__ import annotations

import argparse
import ctypes
import os
import signal
import subprocess
import sys
import tempfile
import time

_ACTIVE: subprocess.Popen[bytes] | None = None


def _linux_parent_death_exec(expected_parent: int, cmd: list[str]) -> int:
    """Set Linux parent-death SIGTERM, verify parent identity, then exec producer."""
    if not cmd:
        return 2
    if not sys.platform.startswith("linux"):
        os.execvpe(cmd[0], cmd, os.environ)
        return 127

    libc = ctypes.CDLL(None, use_errno=True)
    PR_SET_PDEATHSIG = 1
    if libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0) != 0:
        err = ctypes.get_errno()
        print(f"DELTA_PDEATHSIG_FAIL errno={err}", file=sys.stderr)
        return 125

    # Race guard: parent could die between fork/exec and prctl().
    if os.getppid() != expected_parent:
        print(
            f"DELTA_PDEATHSIG_PARENT_GONE expected={expected_parent} actual={os.getppid()}",
            file=sys.stderr,
        )
        return 125

    os.execvpe(cmd[0], cmd, os.environ)
    return 127


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

    proc.kill()
    proc.wait()


def _parent_signal(signum, _frame) -> None:
    """Cleanup child group when the runner itself receives a catchable termination."""
    global _ACTIVE
    proc = _ACTIVE
    if proc is not None:
        try:
            terminate_process_tree(proc, 2.0)
        except Exception as exc:
            print(
                f"DELTA_BOUNDED_RUNNER_SIGNAL_CLEANUP_FAIL signal={signum} error={exc!r}",
                file=sys.stderr,
            )
    raise SystemExit(128 + int(signum))


def main() -> int:
    # Hidden trampoline mode. Keep it before argparse for the normal public CLI.
    if len(sys.argv) >= 4 and sys.argv[1] == "--_pdeath_exec":
        expected = int(sys.argv[2])
        rest = sys.argv[3:]
        if rest and rest[0] == "--":
            rest = rest[1:]
        return _linux_parent_death_exec(expected, rest)

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

        launch_cmd = cmd
        kwargs: dict[str, object] = {"env": env}
        if os.name == "posix":
            kwargs["start_new_session"] = True
            if sys.platform.startswith("linux"):
                launch_cmd = [
                    sys.executable,
                    os.path.abspath(__file__),
                    "--_pdeath_exec",
                    str(os.getpid()),
                    "--",
                    *cmd,
                ]
        elif os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, _parent_signal)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, _parent_signal)

        started = time.monotonic()
        global _ACTIVE
        proc = subprocess.Popen(launch_cmd, **kwargs)
        _ACTIVE = proc
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
        finally:
            _ACTIVE = None

        elapsed = time.monotonic() - started
        print(
            "DELTA_BOUNDED_RUNNER_EXIT "
            f"returncode={rc} elapsed={elapsed:.3f} command={cmd!r}",
            file=sys.stderr,
        )
        return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
