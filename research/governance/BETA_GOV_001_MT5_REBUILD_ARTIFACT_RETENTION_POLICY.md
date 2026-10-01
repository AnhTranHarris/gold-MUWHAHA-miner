# BETA GOV-001 — MT5 Rebuild Artifact Retention and Reconstruction Policy

**Effective:** 2026-10-01  
**Branch:** `beta`  
**Status:** MANDATORY GOVERNANCE — applies to all future BETA research  
**Trigger:** BETA064 missing `beta064_multidesk_loop.py` recovery incident

## 1. Non-negotiable rule

No BETA research unit, checkpoint, candidate, or breakthrough may be called **VERIFIED_DURABLE**, frozen, promoted, or used as the parent of later research unless enough durable material exists to reconstruct its Python behavior and, if later approved by the owner, translate it faithfully into an MT5 EA.

A chat response, transient `/mnt/data` file, notebook state, temporary helper, or assistant memory is never authoritative storage.

**If a file influences a result, it must be durably preserved or deterministically regenerable from preserved source.**

## 2. Mandatory artifacts for every research unit

Every bounded research unit must preserve, as applicable:

1. **Source / helper code**
   - every experiment runner;
   - every helper imported by the runner;
   - cache builders;
   - feature builders;
   - candidate/event generators;
   - state machines;
   - routers;
   - schedulers;
   - label builders;
   - ownership/replay engines;
   - QA scripts;
   - conversion/export scripts;
   - model translation/export code.

2. **Exact configuration**
   - parameter values;
   - thresholds;
   - horizons/checkpoints;
   - seeds;
   - feature order;
   - model hyperparameters;
   - train/calibration/evaluation boundaries;
   - timezone/session definitions;
   - cost, spread, lot, risk and fill assumptions;
   - dependency/runtime versions when material.

3. **Input provenance**
   - input filenames/Drive IDs/repository paths;
   - source date ranges;
   - source SHA-256 when practical;
   - chronological/tie-break semantics;
   - exact preprocessing version;
   - sealed-data status.

4. **Intermediate surfaces required for reconstruction**
   - pre-ownership candidate/proposal ledger;
   - prediction/probability ledger;
   - selected/owned trade ledger;
   - specialist/session identifiers;
   - raw scores;
   - feature vectors or a deterministic means to reproduce them;
   - state-machine transition fields where they materially determine proposals.

5. **Models**
   - training code;
   - feature names and exact order;
   - model family and parameters;
   - fit/calibration boundaries;
   - random seed/determinism notes;
   - serialized model artifact when allowed;
   - deterministic text/tree/JSON export when practical;
   - SHA-256 for every model/export artifact;
   - exact inference contract.

6. **Results**
   - complete compact output;
   - month-by-month metrics;
   - failures/null results;
   - parameter-neighborhood or robustness outputs used in decisions;
   - QA results;
   - exact candidate counts and ownership counts where relevant.

7. **Reconstruction instructions**
   - exact entry point;
   - required files;
   - execution order;
   - expected fingerprints/counts;
   - known limitations;
   - supersession/rollback target.

## 3. GitHub + Google Drive storage contract

### GitHub is mandatory for reconstructible text/code

Small source-controlled artifacts must be committed to the `beta` branch before the unit is considered durable:

- Python/MQL5/source code;
- helper modules;
- manifests;
- JSON/YAML configuration;
- compact CSV result summaries;
- reconstruction specifications;
- model text/tree exports when reasonably sized;
- QA code and QA summaries;
- research records and supersession notes.

A transient helper that affects a result **must never exist only in chat or `/mnt/data`**.

### Drive is mandatory for large/binary evidence

Large or binary artifacts that do not belong in GitHub must be uploaded to the BETA_RESEARCH Drive surface and referenced by immutable identity in a GitHub manifest:

- large candidate/prediction/trade ledgers;
- pickle/parquet/large CSV/ZIP bundles;
- serialized model binaries;
- large diagnostic outputs;
- reproducibility archives.

The GitHub manifest must store at minimum:
- Drive file ID/name;
- byte size when available;
- SHA-256;
- role/purpose;
- producing code commit;
- input/source provenance.

Original large Dukascopy source data need not be duplicated when the canonical source file and SHA-256 are already durable and referenced.

## 4. Required research-unit manifest

Every future research unit must have a machine-readable manifest based on:

`research/artifacts/BETA_RESEARCH_UNIT_REBUILD_MANIFEST_TEMPLATE.json`

The manifest must explicitly state:

- `python_rebuild_ready`
- `mt5_translation_ready`
- `missing_required_artifacts`
- `source_code`
- `helpers`
- `inputs`
- `intermediate_surfaces`
- `models`
- `outputs`
- `qa`
- `reconstruction`
- `supersedes`
- `rollback_target`

A research unit with `python_rebuild_ready=false` cannot be frozen or promoted.

`mt5_translation_ready=false` is allowed during ordinary research, but the exact blockers must be enumerated. A candidate cannot enter owner MT5-build review until `mt5_translation_ready=true`.

## 5. Pre-ownership candidate preservation rule

The BETA064 failure demonstrated that selected trades alone cannot recover a lost candidate generator because ownership, horizons and session routing censor the upstream event stream.

Therefore any Entry/Hold system that performs filtering, ranking, ownership or scheduling must preserve the **pre-ownership proposal surface** or a deterministic generator sufficient to reproduce it exactly.

For learned routers, preserve both:
- upstream proposal/candidate identity; and
- downstream prediction/score identity.

Candidate fingerprints should include, where applicable:

`time, source ordinal, side, specialist, session, raw_score, horizon, checkpoint, feature-version, proposal-id`.

## 6. State-machine preservation rule

Any finite-state, persistence, debounce, expiry, rearm, cooldown, trigger or latch behavior must be committed as executable source plus a compact transition specification.

Never leave these semantics only in prose.

For every material state machine preserve:
- state names;
- arming condition;
- transition condition;
- tick/bar timing convention;
- persistence counter/time;
- expiry;
- debounce/cooldown;
- reset conditions;
- rearm conditions;
- output event semantics.

## 7. Feature/cache preservation rule

A derived cache is durable only if either:

A. the exact cache is stored with hash and provenance; or  
B. its builder is durably committed and deterministic from durably identified source data.

The manifest must record:
- bucket timestamp convention, especially LEFT vs RIGHT edge;
- known-at time;
- missing-bucket handling;
- resampling rules;
- signed/side-relative feature semantics;
- numeric dtype/rounding when material;
- feature schema and order.

## 8. Model preservation rule

No learned checkpoint is durable without enough information to reproduce inference.

At minimum preserve:
- exact training population definition;
- exact feature order;
- target/label construction;
- model parameters;
- fit/calibration boundaries;
- model artifact/export hashes;
- probability/post-processing logic;
- gating thresholds;
- upstream candidate provenance.

A model binary without its candidate generator is **not** MT5-rebuild complete.

## 9. Atomic durability gate

Before moving to the next research unit, the active unit must pass this sequence:

1. Run completes.
2. Source/helpers/config are committed.
3. Required large artifacts are uploaded to Drive.
4. Hashes and Drive IDs are written into the manifest.
5. Compact results/QA are committed.
6. Reconstruction command/path is documented.
7. GitHub and Drive artifacts are read back/verified.
8. Manifest sets `python_rebuild_ready=true`.
9. `CURRENT_STATE.json` advances only after steps 1–8 succeed.

If a timeout occurs before step 9, resume the same unit from its first missing durability step. Do not start the next scientific unit.

## 10. MT5 build gate

Before the owner is asked to authorize an MQL5 build, the candidate must have a durable MT5 translation package containing:

- authoritative Python parent;
- full helper dependency list;
- exact candidate/event logic;
- exact feature equations and timing;
- state-machine semantics;
- model inference/export specification;
- BUY/SELL quote-side execution contract;
- fill/markout/fee assumptions;
- one-position/ownership rules;
- session/DST rules;
- risk rules;
- checkpoint hashes;
- Python parity fixtures with expected outputs.

MT5 work may still be scientifically rejected or withheld for other reasons, but it must never be blocked because a transient research helper or artifact was allowed to disappear.

## 11. Supersession and deletion

Do not silently delete or overwrite a helper that produced a durable result.

A replacement must:
- use a new commit/version;
- identify what it supersedes;
- preserve the old commit/path in provenance;
- update the active manifest;
- record the rollback target.

Git history is evidence, but the active state must point unambiguously to the authoritative version.

## 12. BETA064 postmortem rule

The BETA064 repair established the prohibited failure mode:

> A checkpoint was preserved while its transient upstream candidate generator and some intermediate proposal/prediction surfaces were not durably stored, making exact later MT5 parity impossible.

This condition must not recur.

From this policy forward, a checkpoint with missing upstream reconstruction artifacts is **INCOMPLETE**, regardless of how strong its reported metrics appear.

## 13. Owner-facing assurance

The project may still conclude that a strategy should not be encoded in MT5 because it fails causal, economic, robustness, risk, or owner-approval gates.

It must **not** conclude that an otherwise approved candidate cannot be encoded because the project failed to preserve its own source/helper/model/provenance artifacts.
