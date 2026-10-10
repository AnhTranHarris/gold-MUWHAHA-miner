# GRID-0109 — Month-by-month weak-hour root-cause attack, grid-only

**2026-10-10 | Owner mandate:** attack each month's poor-performing hours more aggressively while preserving the daily discovery result. This is **stage-zero virtual grid research**, not a funded trading/entry/exit engine. **No session-specific rules, no Vertical Grid L1–L7, no Martingale, no unsealing August, no modification to immutable Dukascopy or R9 files.**

## Data and measurement boundary

The analysis reuses the previously source-reconciled GRID-0108 native Bid/Ask January–July full event arrays (`events_01.npz`…`events_07.npz`) and the complete 3,436 UTC-hour / 181 UTC-day audit CSV. Those arrays were generated from 57,527,562 chronological original XAUUSD Dukascopy ticks; this cycle **did not reread and newly replay all 57.5M source ticks**, but computed research diagnostics and candidate gates from the preexisting event tapes. The benchmark is the fixed creator-derived virtual price grid (gap=max($0.75,1.5×EWMA past observed spread), 7-second event cooldown) and frozen K5≥4 high-motion shadow tier.

The frozen hourly measure is a *relative movement-capacity score*: positive if the selected K4 event pool in the **same UTC hour** has a higher fraction of 120-second absolute future midpoint displacements exceeding 2× source event spread than all base-grid events in the hour. Hour eligibility: ≥20 baseline future-valid events; K4 support ≥5 future-valid events. **No profit, correct BUY/SELL, or trade fills are measured by this win label.**

## Per-month UTC-hour forensic audit

| Month | Baseline-eligible UTC hours | K4 supported | K4 increased capacity | K4 declined | K4 unsupported | Recurrent weakest UTC hours-of-day, diagnostic only |
|---|---:|---:|---:|---:|---:|---|
| January | 467 | 446 | 260 | 185 | 21 | 04, 10, 13, 16 |
| February | 452 | 443 | 292 | 151 | 9 | 08, 10, 04, 14 |
| March | 496 | 496 | 293 | 202 | 0 | 12, 15, 17, 01 |
| April | 470 | 455 | 291 | 162 | 15 | 04, 23, 22, 14 |
| May | 466 | 447 | 256 | 187 | 19 | 22, 06, 19, 11 |
| June | 489 | 474 | 294 | 179 | 15 | 02, 03, 05, 11 |
| July | 492 | 453 | 257 | 193 | 39 | 23, 22, 04, 07 |
| **Total** | **3,332** | **3,214** | **1,943** | **1,259** | **118** | — |

**Precision footnote:** K4 supported hours include an additional **12 ties** among the 3,214, so positive+negative+unsupported is not the full eligible count. Recurrent UTC-hour groups are **diagnostic only**—do not add time-of-day routing or secretly turn them into an L1 session filter.

Pooled persistent weak times: UTC 04 (75/145 fail to improve), 22 (38/75), 14 (70/150), 10 (68/150), 08 (67/149). Weak-hour identities shift between months. June and July retain severe exceptions despite their full-month/weekday success. July 22/23 UTC have unusually poor coverage, so any smaller filtered tier must be penalized for unsupported hours rather than claiming higher conditional win percentage.

## Critical novel forensic result — opportunity exists, but direction discovery is unsolved

A truly **retrospective, UNTRADABLE best-of-BUY-or-SELL oracle** asks whether, at the known price 120 seconds after each original virtual event, *either* correct executable quote-side trade direction would have yielded positive $0.01-lot/1oz markout after a $0.02 round-trip fee, if one could know the future. This is a **future-leaking bound used OFFLINE ONLY**, never a predictor or trading rule.

| Month | Grid raw events in weak UTC hours | Retrospective best-side positive fraction | Fixed creator-reversal average quote-side $ (fee included) | Fixed continuation average quote-side $ (fee included) |
|---|---:|---:|---:|---:|
| January | 23,732 | 79.1% | −0.757 | −0.858 |
| February | 19,068 | 79.7% | −1.032 | −1.059 |
| March | 33,453 | 83.8% | −0.750 | −0.919 |
| April | 18,134 | 77.0% | −0.783 | −0.685 |
| May | 21,994 | 76.8% | −0.636 | −0.628 |
| June | 21,942 | 78.4% | −0.644 | −0.625 |
| July | 17,933 | 71.7% | −0.724 | −0.642 |

This gives an investor-relevant diagnosis: a very large **upper bound on correctly predicted opportunity** exists even in the unproductive hours. It is *NOT achievable directional accuracy*. The actual simple creator contrarian or fixed continuation decisions remain negative after the native Dukascopy executable quotes. The hard missing component is **causal correct direction and decision timing**, not simply more virtual grid points. Source spreads are NOT uniform nor do the data include actual centralized gold order-book depth; source quoted sizes do not establish NYSE-style order-flow imbalance.

## Mechanism research and frozen chronological comparisons

### Proposal A: grid-native matured-outcome adaptive threshold

A non-clock rule compares only **prior grid-event outcomes already at least 130 seconds old**, from a trailing 30/60/120/240-minute window. It uses Beta-style shrinkage, then chooses a virtual grid capacity threshold from K5≥2…K5≥6, with optional no-expansion policy (threshold floor 4). All current outcome labels and same-hour future moves are *inaccessible to the decision*. This is an **exploratory virtual capacity rule**—not a funded trading strategy. Tested 144 variants on January–April development event tapes, with MAY–JUL chronological comparison fixed at the January–April selected setting. May–July had already been used in earlier research, so they are **NOT pristine holdouts**.

Developed choice: past 30 min, Beta prior=10, tier penalty 0.006 for each higher K step, 30 prior outcome-observation warmup, expansion disabled (never a tier below K4). Scores for candidates with <10 observations are not allowed to drive tier selection.

| Month grouping | Frozen K4 improved eligible hours | Adaptive rule improved eligible hours | Eligible hours | Fixed K4 positive days | Adaptive positive days |
|---|---:|---:|---:|---:|---:|
| January–April (development) | 1,136 | 1,151 | 1,885 | 84/84 | 84/84 |
| May–July (chronological re-analysis) | 807 | 810 | 1,447 | 66/66 | 66/66 |
| All months | 1,943 | 1,961 | 3,332 | 150/150 | 150/150 |

The adaptive rule reduced original K4 candidate volume by about 5% while preserving seven-month *daily unsigned uplift*. **Only +3 additional improved hours on the later months after 144 in-sample hypotheses is far too small and post-selection to justify promotion as a real hourly breakthrough.** Preserve as quarantined research, not the canonical grid.

### Proposal B: nonlinear as-of capacity ranking

Trained three modest LightGBM nonlinear magnitude classifiers on original January–March event features; used April to choose between 15 model/threshold combinations, and compared unchanged models to later May–July tapes. Features include only causal recent price changes, spread/gap, grid rung-event flow, bid/ask event sign, and prior quote history—**no session identifiers**. The classifiers improved future-movement precision among their surviving subset but generally removed too many supported hours. They did **not** beat the simple existing K4 hourly-coverage scoreboard in April. No model promoted. This is also not a predictor of BUY/SELL sign.

## Research decision — protect actual working edge

**RETAIN** existing grid origin plus broad K5≥2 and high-movement K5≥4 tiers. Retain complete forensic UTC-hour failure ledger and retrospective best-direction diagnostics as **research tools only**. Do **not** promote an hourly rule on evidence of +3 later historical improvement; do not turn weak UTC-hour bins into forbidden prematurity/session-specific execution conditions; do not increase lot sizing, margin use or exposure.

Next quantitatively constructive experiments at the GRID-only stage, BEFORE L1 sessions:

- **Two-stage causal direction election** as a *new entry decision at later quote*, not hindsight at original crossing: for an initial grid event generate both reversal and continuation virtual pathways; require a subsequent executable side-specific price test, market-order quote age bound, and explicit local protective wrong-way invalidation. Measure its own event-time and price, rather than evaluating it at the initial crossing's future price.
- **First-passage cost/range competition**: on a completed quote path, compare exact temporal ordering of "+current spread+fee+slippage reserve" favorable barrier and wrong-direction barrier. No midpoint synthetic fill or OHLC ordering shortcuts.
- **Grid-state/exhaustion pressure**: virtual consecutive rung travel, unique-cell first touch and expired attempted reversals as as-of features. Never create an averaging-down position or use doubled lots to manufacture recovered wins.
- **Depth-data feasibility check**: quote ask_volume/bid_volume in raw Dukascopy feed is not a central-order-book queue; do not import real order-flow-imbalance equations as if full market-by-order depth existed.

Evaluate by **month + actual UTC hour**: K2/K4 source candidate counts, sign-specific AFTER-real-Bid/Ask 30/120/600s markout, fixed-dollar absolute movement, signed positive hours, worst-hour and quiet-hour coverage, serial event overlap, and (only after the fully integrated L0–L7 order lifecycle exists) account P/L/heat/DD/capital risk. The $100k initial account is a future research simulation preference, not a current trade input. August remains sealed.

## Research basis & reproduction

- Previous frozen evidence: [GRID0108 seven-month report](../grid/GRID_0108_SEVEN_MONTH_HOURLY_AND_DAILY_RESEARCH_REPORT.md) and its [complete source and daily/hourly tapes](https://drive.google.com/file/d/1TeMWzdLV3KQTeMSNOJCBMh-HrlmwyyCW/view).
- Peer-reviewed microstructure inspiration: Cont/Kukanov/Stoikov, *Price Impact of Order Book Events*, [arxiv 1011.6402](https://arxiv.org/abs/1011.6402). That empirical result requires order book depth NOT present in the current Dukascopy quote fields; only generic causal logic is transferable.
- Independent empirical pricing caveat: Hasbrouck, [Dynamics of Discrete Bid and Ask Quotes](https://doi.org/10.1111/0022-1082.00183); volatile quoted costs can persist, not just vary with time of day.
- Backtest design: [event-label overlap / purged time-series CV](https://javiermeseguer.me/projects/financial-ml/), including independent untouched tests and multiple hypothesis penalties.
- Current reusable scripts: `hourly_forensics.py`, `poor_hour_oracle_decomposition.py`, `quote_direction_ceiling.py`, `learn_intrinsic_capacity.py`, `causal_grid_hour_router.py`, `test_grid0109.py`; includes extracted monthly/hourly CSVs, ML model snapshots, complete results JSON, and seven deterministic local tests. Ancestry: original zipped GRID0108 seven-month source package. No change to original raw quote R9 data.
