# R9 Device-Independent Cloud Mode

The research workflow must not depend on the user's current device, browser, Android app, desktop app, or personal PC being online.

## Canonical device-independent layers

1. **Private source archive — Google Drive**
   - Original Jan-Jul Dukascopy gzip files remain private.
   - Do not change sharing permissions merely to enable compute.

2. **Cloud execution corpus — ChatGPT Library**
   - Canonical path: `/R9_Cloud_Corpus/Dukascopy_2026/`
   - Contains Jan-Jul raw XAUUSD Dukascopy monthly gzip files.
   - Corpus size at certification: 430,595,185 bytes.
   - A private Library manifest records source identity, exact size and SHA-256 for every month.
   - A Work/Chat cloud runtime rehydrates only the month(s) required for the current bounded job.

3. **Long-running controller — ChatGPT Work Cloud**
   - Preferred when research must continue after the user leaves, changes device, closes the browser, or turns off a device.
   - Work owns orchestration; it does not replace scientific checkpoints.
   - Each bounded compute stage still follows preflight -> compute -> validate -> local commit -> durable sync.

4. **Code / CI / attempt history — GitHub**
   - Branch: `carson/r9-durable-runner`.
   - GitHub-hosted Actions independently self-test runner reliability.
   - GitHub-hosted heavy research may be used only when required private inputs are securely available to that runner.
   - Never make the raw Drive corpus public to simplify Actions.

5. **Scientific authority — Google Drive research ledger + Library artifacts**
   - A result is scientifically durable only after its metrics, hashes and next-task state are reconciled into the ledger and its required artifacts exist outside the ephemeral runtime.

6. **Optional accelerator — personal Windows PC**
   - The Windows daemon/watchdog remains supported.
   - It is no longer a prerequisite.
   - If the PC is offline, research proceeds through Work/Library cloud mode.
   - When the PC is online, it may accelerate bounded raw-tick jobs using the same job contract.

## Cloud rehydration rule

Before a cloud job:
- read the current Drive research ledger;
- read the Library corpus manifest;
- materialize only the required month(s) from Library;
- verify file size and SHA-256 against the manifest;
- execute one bounded heavyweight unit;
- persist outputs immediately to Library and ledger;
- remove or ignore local cache after durable sync.

A cloud runtime path such as `/mnt/data` is cache only. It is never a source of truth.

## Device-switch behavior

Switching between Android browser, Android ChatGPT app, desktop web, or another supported device must not change research state. The active device only sends instructions and reviews results. Inputs, outputs and status live in Drive/Library/GitHub/Work rather than the device.

## Failure containment

If Chat ends:
- Work may continue its delegated cloud task.
- Any already-durable artifacts remain available to the next chat.

If a cloud compute container disappears:
- rehydrate the last required inputs from Library;
- resume from the latest VERIFIED_DURABLE stage;
- never rerun earlier stages blindly.

If Work pauses for user input:
- completed stage artifacts remain durable;
- resume from the same checkpoint on any supported device.

If GitHub is unavailable:
- Drive/Library preserve data and scientific status;
- GitHub synchronization resumes later.

If the PC is unavailable:
- no action is required; use Work + Library cloud mode.

## Verification completed

January was streamed from private Drive to Library, re-materialized into a fresh cloud path, and reproduced the canonical SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
at exactly 68,690,420 bytes.

This proves the cloud corpus is reusable independently of the personal PC.
