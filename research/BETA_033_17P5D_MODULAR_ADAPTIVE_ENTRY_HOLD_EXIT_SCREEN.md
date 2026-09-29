# BETA033 — Investor-facing initial modular adaptive research screen
**Date:** 2026-09-29 | Independent BETA only | **NO PROMOTION** | August SEALED

## Results: no strategy cleared 10%

Tested **five distinct modular entry/hold/exit families** with **three bounded parameter configurations each** in a five-worker shared-tick parallel screen, using **4,205,709 original ordered XAUUSD Dukascopy Bid/Ask ticks** between 2026-01-01 00:00 UTC inclusive and 2026-01-18 12:00 UTC exclusive. There were **14,174** original source first-cycle opportunity origins. No synthetic quote path was generated. This 17.5-day historical sample has been repeatedly inspected before; it is discovery, not blind OOS.

**Common new realized-trade baseline:** 13,395 actual one-position closes, 2,478 winning, $-10,375.74 after modeled 0.01-lot Bid/Ask + $0.02 roundtrip, gross loss $-12,181.44, PF 0.1482, modeled max floating-equity drawdown $10,375.84. Baseline is the source-R9-like firstcycle detector with a 30-second expiry, $2/oz stop/$2/oz target, no trail; NOT source-equivalent to the original Coinexx EA and NOT a BETA015 funded replay.

| Adaptive specialist family | After-cost net USD | Relative loss reduction | Realized trades | Winning trades | Gross-loss improvement USD |
|---|---:|---:|---:|---:|---:|
| Fast Accept | -10,204.90 | +1.647% | 13,180 | 2,451 | +207.72 |
| Origin Retrace Continue | -9,833.39 | +5.227% | 12,785 | 2,382 | +615.04 |
| Sweep Context Counter Momentum | -10,020.96 | +3.419% | 12,945 | 2,397 | +436.51 |
| Regime Harvest | -10,337.69 | +0.367% | 13,591 | 2,280 | +492.44 |
| Early Failure | -10,408.88 | -0.319% | 14,084 | 481 | +1,301.24 |

**Best initial candidate:** ORIGIN_RETRACE_CONTINUE_LEVEL0 = $-9,833.39, $+542.35 vs baseline, **5.227%** reduction in realized loss, 2,382 winners vs 2,478 incumbent, 12,785 vs 13,395 closes; improved gross loss $+615.04. It improved each of the two initial blocks by $+285.65 and $+256.70, but **failed strictly >10%**, remained after-cost negative, and therefore did NOT advance Jan–Jul. No configuration achieved >20%.

## Honest technical interpretation

**Equal priority:** ENTRY/HOLD/EXIT received equal default research emphasis. Each specialist has independent `entry_specialist(...)` and `lifecycle_specialist(...)` rules, composed in a one-position `account_replay` using the current known regime, quote pressure, completed structural states, event age, and live observed Bid/Ask. A strategy can allocate more behavioral emphasis to exits when its entry rule is weak, without altering the externally applied full-system economic gate.

**An entry is not condemned by a short-term negative markout.** In the new scorecard, an accepted trade is profitable only when its actual closing Bid/Ask P&L **after spread and fees** is positive. Intratrade temporary MAE, floating drawdown, stop hits, quote gaps, and blocked follow-on opportunities are still recorded. The new baseline differs from previous BETA032 origin+15s markouts: these quantities are not interchangeable.

**No false level-retreat or sweep claims:** `ORIGIN_RETRACE_CONTINUE` waits for an actual origin-relative adverse $ move and rebreak. It does NOT confirm a literal retracement to the pivot price. `SWEEP_CONTEXT_COUNTER_MOMENTUM` uses a previously confirmed sweep context and waits for a fresh observed counter-direction extension; it does NOT independently establish an order-book liquidity sweep or subsequent reclaim. Historical Gamma profits and R9 OVERFIT oracle entries are not adopted.

**Ablation of best strategy:**

| Identical source evaluation | Realized after-cost net | Loss reduction | Winners | Closed trades |
|---|---:|---:|---:|---:|
| ORIGIN_RETRACE_CONTINUE_LEVEL0_entry_only | $-9,862.80 | +4.944% | 2,384 | 12,786 |
| ORIGIN_RETRACE_CONTINUE_LEVEL0_lifecycle_only | $-10,299.19 | +0.738% | 2,499 | 13,376 |
| ORIGIN_RETRACE_CONTINUE_LEVEL0 | $-9,833.39 | +5.227% | 2,382 | 12,785 |

**Modeling boundary:** quote gaps longer than 3 seconds are observed and recorded; there is NO fabricated gap liquidation, and orders close only on actual next Bid/Ask. The screen assumes zero slippage and an assumed contract/commission model. Broker stops, fills, latency and disconnections have not been independently reconciled. The market was closed during part of the 17.5-calendar-day screen; no empty ticks were generated. Position-level replay is **shadow**, with NO BETA015 daily/90k funded account gating. Completed monthly cache feature parity BETA005 remains incomplete. Full original Coinexx R9 REAL and R9 SYNTH unselected ticklog for the exact 17.5-day window is not present; matched teacher subsets must not be misreported as original full source recall.

**Validation:** direct full compressed original January source byte SHA, 4,205,709 ordered actual source ticks in the window, cached source-ordinal equality, direct quote-side stop/target/timeout and interim-adverse-recovery fixtures, one-position nonoverlap tests, full-score arithmetic and **225/225 independent QA assertions PASS**. Same-feed control/candidate chronological account comparison; no MQL5 compilation or demo/live claim.

## Go/no-go and next science

**GO: none.** Seven-month expansion is withheld until an initial specialist clears strictly >10% realized-after-cost improvement, with preserved absolute winners, adequate trade volume, and gross-loss / floating-DD safety. The optional aspirational step is >20%. After a valid January screen, freeze settings before the Jan–Jul historical diagnostic; April–July are not blind. If any candidate passes that research stage, BETA015 funded-account guard, feature parity and owner approval before MQL5 code are still required.

**Potential different mechanism, not just another threshold grid:** a closed-bar structural-owner transition graph with state-specific entry hazard, then stateful quote-flow proof, post-entry persistence hazard, explicit live event rearming and an integrated one-account policy. All new formulas need a reproducible independent Python/MQL5 translation contract, no causal-peeking or altered teacher timeline. Gold Hunter V8 remains secondary unverified genealogy only.

## Reproduce

- Original MONTHLY raw quote file must be independently available under `/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` and must match SHA-256 **`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`**; no original large raw market CSV.GZ is included in ZIP.
- Source event-cohort cache and completed-bar registry are in bundled reproducibility inputs; these are previous research caches not BETA005 17-layer parity-certified.

```bash
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=4 python BETA033_MODULAR_4PLUS1_ADAPTIVE_STAGE1.py
OPENBLAS_NUM_THREADS=1 python BETA033_INDEPENDENT_QA.py
```