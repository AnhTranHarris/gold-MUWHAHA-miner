# R9 GAMMA-02 — Timeout Recovery Checkpoint — 2026-10-07 03:40Z

**Branch:** `carson/r9-gamma-02-velocity-geometry-research`

**Parent frozen savepoint:** `carson/r9-gamma-01-stmr-clockfix` @ `74dcc6b92d12705fe45f55e0c252e0e5fb04781c`

**Recovery reason:** ChatGPT message-delivery timeout during January velocity/geometry mutation loop. Runtime inspection found all completed `gamma02_*` helpers/results intact and no surviving research worker process. This checkpoint is authoritative for restart; do not restart completed sweeps.

## Scientific floor / owner target

- Validated parent remains STMR ClockFix; do not overwrite it.
- R9 SYNTH Jan–Jul remains the hard north-star: +$309,122.85 net, PF 20.036, +$1.409319 expectancy/trade, 219,342 trades, 87.14% wins, ~16 s average hold.
- January discovery is allowed to mutate aggressively, but August remains SEALED.
- No MQL5 implementation until owner authorizes after Python evidence.

## Completed January work recovered

### 1. Dense HTF-directed micro-lattice — REJECTED as a broad frequency engine

Broad nested-lattice variants produced thousands of trades but remained negative. Best stage-1 example:
- 4,784 trades
- -$318.60 net
- PF 0.8943
- expectancy -$0.0666/trade

Recross stage-2/stage-3 remained negative. This is evidence that simply increasing crossings under HTF direction does not create enough directional edge.

### 2. Exact funded STMR root-event ledger — IMPORTANT POSITIVE DIAGNOSTIC

Recovered root count: **1,268** January events.

Forward executable directional markout across all roots:
- 0.25 s: -$27.54 aggregate, PF 0.937
- 0.5 s: +$150.25, PF 1.310
- 1 s: +$303.06, PF 1.472
- 2 s: +$460.14, PF 1.420
- 5 s: +$497.34, PF 1.284
- 10 s: +$1,016.35, PF 1.425
- 30 s: +$936.91, PF 1.276
- 60 s: +$3,090.41, PF 1.745

Interpretation: the funded STMR root events contain real directional information after roughly 0.5 s, but the edge is highly sleeve/lifecycle dependent. This supports using geometry for **harvest/recycling around qualified roots**, not indiscriminate micro-lattice entry proliferation.

### 3. Root-only lifecycle sweep — POSITIVE

Best recovered single-entry root lifecycle:
- TP 4.00 / SL 1.50 / max hold 300 s
- 407 trades
- +$234.59 net
- PF 1.4927
- expectancy +$0.5764
- DD ~$35.69

### 4. Root-neighborhood / repeated opportunity locator — POSITIVE but not yet velocity breakthrough

Best recovered neighborhood candidate:
- 15 s campaign window
- 0.15 price step
- TP 4.00 / SL 1.50 / max hold 300 s
- up to 8 candidate events
- 518 trades
- +$276.64 net
- PF 1.4061
- expectancy +$0.5341

It did not yet produce the required R9-class trade density.

### 5. Speed/lifecycle sweep — POSITIVE frontier, still modest density

Best broad speed/lifecycle recovered:
- 577 trades
- +$248.44 net
- PF 1.3611
- expectancy +$0.4306
- TP 4.00 / SL 1.50 / hold 60 s / micro-step 0.15

### 6. TP-recycle campaign architecture — ACTIVE promising family

Semantics:
- exact funded STMR root starts a directional campaign;
- one live position at a time;
- a TP may causally re-arm another same-direction harvest while campaign/state remains valid;
- no leverage cloning;
- live HTF/session state is rechecked;
- campaign can be extended by same semantic root;
- SL/time exit normally terminates the campaign.

The first generic TP-recycle search was too large for one bounded call, so it was split by sleeve.

### 7. OVERLAP sleeve wide-stop recycle — COMPLETED and POSITIVE

`OVERLAP_LOWER_TAKEOVER` (sleeve 4) wide sweep completed: 720 variants.

Best net candidate recovered:
- TP 1.50
- catastrophic SL 8.00
- hold 5 s
- max 12 harvests/campaign
- 239 trades from 355 root events
- +$182.04 net
- PF 1.5814
- expectancy +$0.7617/trade
- win rate 74.48%
- DD ~$70.61

Alternative lower-DD/high-PF candidate:
- TP 2.00 / SL 3.00 / hold 15 s
- 208 trades
- +$178.14
- PF 1.6426
- expectancy +$0.8564
- DD ~$36.14

This is important because it shows **fast short-lived harvest geometry can preserve high win conversion around a strong HTF/session state**, but it is not yet enough trade volume by itself.

## Recovered root-event sleeve clue

Forward markout is strongly heterogeneous:
- sleeve 4 OVERLAP is strongly positive from 1 s onward and remains powerful at longer horizons;
- sleeve 9 LATE_MACRO_SPLIT_TRANSFER is weak at 1–10 s but becomes exceptionally persistent at 30–300 s;
- sleeve 2 LONDON has strong 1–3 s and 30–60 s behavior;
- sleeve 8 LATE_ALIGNED_MOMENTUM is weak short-horizon but improves materially at 120–300 s;
- sleeve 11 LATE_LOWER_TAKEOVER is useful around 2–10 s but degrades at 30 s+;
- sleeve 0 ASIA is modestly positive mainly from 2–10 s and later 120 s+.

This argues against one universal scalp lifecycle. GAMMA-02 should mutate **sleeve-specific velocity/lifecycle specialists** and later combine them causally.

## Runtime artifacts and SHA-256

- `gamma02_velocity_geometry_january.py` — `698d5da083efe3e111a32d3440410271cc2f0fb57121fd2827383bca2fed3b22`
- `gamma02_velocity_stage1.json` — `32f7a409408f614a5425aabccca7f4ad5ad289058ddd31d744c810b54a1fe521`
- `gamma02_velocity_stage2.json` — `8038771c0d9866c11a787fb7c3f64cf3a9cdbfbec607b08e7dfbfefde7f140f0`
- `gamma02_velocity_stage3.json` — `ceec917bc152b5b8f3b35d0180752e06cc05e0ef2c1b3d3ccdac299a0899ca49`
- `gamma02_root_burst_january.py` — `2caf2d68d66a90a6f3bc32e268143af3fb1c122ad3498681fc087aad7e2cdb05`
- `gamma02_root_lifecycle.json` — `12fda013721ae12652e975a196a3b1a8b6dd457a1f0b13dc006475826d918b3b`
- `gamma02_locate_best.json` — `905207f4f23aeb1b9ebc3faba6eb70a7f4a76e760dc4c45b7159658f1263ffd0`
- `gamma02_root_event_ledger.json` — `6921e683ae3a9727b0a1dfc77cdf2418b3c1824b06d9613cd48d2ec7aaaa9c8c`
- `gamma02_speed_lifecycle.json` — `148a9486ac0b533b20fcdaf2fb69f399bee8e6a6b443e55fcfbe85c4e9e516ac`
- `gamma02_tp_recycle.py` — `6f08882eb22a896526371d5fbd83c198e5302af1c7ec62143032f8d8e34b2e9b`
- `gamma02_tp_recycle_run.py` — `4b0b8fe73eea24d97180661014ac505d3ba6e45d0d2d89ca45d9830e8b87100e`
- `gamma02_recycle_widestop.py` — `abcb58ae2b61f90ae15b571517dcf4bcfe4b3f3f55c7a8a111f1ccbb226a60a0`
- `gamma02_recycle_wide_overlap.json` — `58bb80fc44cfb01830d1c253dd9bfcd01675b9bd9bff2192945f4ddabcef2b3e`

## Exact restart point after timeout

No active Python worker survived.

**COMPLETED:** wide-stop TP-recycle sweep for sleeve 4 / overlap.

**INCOMPLETE / NOT YET RUN:** equivalent bounded wide-stop recycle sweeps for:
1. sleeve 9 / `late9`
2. sleeve 2 / `london`
3. sleeve 0 / `asia`
4. sleeve 11 / `late11`

Resume these one sleeve at a time and checkpoint after each. Then construct a sleeve-specific lifecycle portfolio and test whether it can materially increase profitable trade density over the validated parent rather than merely replacing one low-frequency sleeve.

Do not rerun the completed broad lattice or overlap sweep unless a later engine change explicitly invalidates them.
