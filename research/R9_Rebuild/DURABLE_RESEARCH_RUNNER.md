# R9 Durable Research Runner

This runner removes heavyweight Python ownership from an ordinary ChatGPT turn.

## Failure model

ChatGPT Chat may disconnect, hit a tool/stream timeout, or lose an ephemeral container. None of those events should terminate a raw-tick backtest. A Windows Scheduled Task owns the daemon; the daemon pulls immutable job specs from the dedicated GitHub branch, runs exactly one allowlisted Python script per job, writes a local checkpoint/heartbeat/manifest, and commits small result manifests back to GitHub.

## One-time install

From a local clone of this repository on Windows:

```powershell
git fetch origin
git checkout carson/r9-durable-runner
git pull
powershell -ExecutionPolicy Bypass -File .\research\R9_Rebuild\install_r9_durable_daemon.ps1 -RepoRoot (Get-Location).Path
```

The scheduled task is `R9-Durable-Research`. It starts at logon, restarts on failure, and ignores duplicate task launches.

## Job contract

Place an immutable JSON spec in `research/R9_Rebuild/jobs/pending/`. Only `.py` scripts under `research/R9_Rebuild/` may execute. Arbitrary shell commands are intentionally forbidden.

Example:

```json
{
  "job_id": "C12_JAN_EXAMPLE",
  "script": "research/R9_Rebuild/example_screen.py",
  "args": ["--month", "1"],
  "artifact_globs": ["research/R9_Rebuild/out/C12_JAN_EXAMPLE*.json"],
  "publish_files": ["research/R9_Rebuild/out/C12_JAN_EXAMPLE_summary.json"],
  "publish_max_mb": 20
}
```

## Completion states

- `STARTED`: supervisor created the manifest.
- `RUNNING_VERIFIED`: child PID exists and heartbeat updates.
- `COMPLETED_LOCAL`: child exited 0; output/log hashes were written atomically.
- `FAILED_RECOVERABLE`: child exited non-zero; log and manifest remain.
- `VERIFIED_DURABLE`: ChatGPT Work/Chat reconciles the GitHub result plus Drive/Library ledger.

The daemon does not rerun a job that already has a `COMPLETED_LOCAL` manifest unless the job ID changes. Small results in `jobs/results/<JOB_ID>/` are committed and pushed back to the dedicated branch.

## Why this fixes the recurring failure

- Windows Task Scheduler—not the chat—owns process lifetime.
- Task Scheduler restarts the daemon after failure.
- The wrapper writes its own heartbeat and final manifest.
- Small results/logs are pushed to GitHub independent of ChatGPT's temporary filesystem.
- A chat timeout only delays analysis; it does not kill computation.
- The dedicated branch prevents unrelated repo changes from becoming job instructions.
- Heavy raw-tick months remain sequential; lightweight post-processing may be parallelized safely after durable corpora exist.

For long ChatGPT-side orchestration, use ChatGPT Work. OpenAI documents that Work's cloud browser can continue after the user leaves the conversation, but Work is not treated as infallible; this daemon remains the compute owner.
