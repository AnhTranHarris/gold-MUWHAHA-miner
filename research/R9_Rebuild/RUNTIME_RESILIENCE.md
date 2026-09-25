# R9 Rebuild Runtime Resilience

Status: research-infrastructure policy only. This file does **not** change trading logic.

## Failure mode this prevents

Chat/container runtimes are ephemeral. A detached Python process, nohup/tmux process, or sub-agent inside a Chat runtime is not durable evidence that a research job will continue after the runtime is replaced. The September 25, 2026 incident left the GitHub source and Drive research ledger intact but lost the local `/mnt/data/r9_research_v2` event checkpoints and the live worker.

## Mandatory job contract

Every expensive R9 research job must use:

1. A deterministic job ID.
2. Git commit SHA + script path + parameters.
3. Source file identity/hashes.
4. Bounded unit of work (normally one month or one specialist/target block).
5. Live PID/command verification before claiming RUNNING.
6. Heartbeat/progress log while the worker is alive.
7. Atomic checkpoint writes: temporary file -> fsync/close -> SHA-256 -> rename.
8. A DONE manifest containing output hash, row/trade count, metrics, completion timestamp, and source/code identity.
9. Immediate update of the Google Drive research ledger after each completed unit.
10. Durable upload/commit of any artifact whose loss would force expensive recomputation, when practical.

## Status vocabulary

- PLANNED
- STARTED
- RUNNING_VERIFIED
- COMPLETED_LOCAL
- VERIFIED_DURABLE
- FAILED_RECOVERABLE
- REJECTED

No research result exists scientifically until VERIFIED_DURABLE.

## Timeout / reset recovery order

1. Inspect process table.
2. Inspect job-state / heartbeat.
3. Inspect progress logs.
4. Inspect newest output and DONE manifests.
5. Compare against Google Drive research ledger.
6. Compare source/commit against GitHub.
7. Resume only from the last verified checkpoint.
8. Never blindly restart Jan-Jul.

## Ordinary Chat versus durable execution

Ordinary Chat/container execution must be treated as bounded and ephemeral. If a computation is expected to exceed a safe active execution window, do not rely on a detached background process. Use a durable execution venue instead, such as an explicitly supported ChatGPT Work task where appropriate, or a secured external/local runner.

GitHub Actions can persist workflow artifacts and provides explicit timeout controls. For CPU/data-heavy tick research, a self-hosted runner may be appropriate if the user controls the machine and the repository/workflow is secured. Do not expose a self-hosted runner to untrusted public-fork workflows.

## R9-specific restart invariant

August remains sealed. The active authority remains original R9 REAL/SYNTH, certified R9 source, ordered Dukascopy Jan-Jul ticks, the live Drive research ledger, and Project sources. Runtime failure must never be converted into a strategy conclusion.
