# Gold MUWHAHAHA Miner R9 — JAN 2026 causal-state reconstruction R02

**R02 decision: ALL THREE new specialist hypotheses FAILED acceptance. Research-only; no EA or approved risk-policy modifications.**

## Immutable source and validation

- Original MQL5 Git blob `7eecb5f1947017a01ce85b2520725de54749e523`; exact independently compiled R01 reference source retained. No modification to original EA `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`.
- Same original January Coinexx broker-export gzip `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`, 7,699,274 chronological Bid/Ask tick records, 413 adjacent equal-millisecond observations; no raw-data reindex or reconstruction.
- Original January R9 SYNTH 27,980 entries and 24,368 booked winners only retrospective comparator. The reference never enters the live router, profit-taking or R9 state machine; it is read exclusively by a separate observer at the source-ordered ticks.
- Replay source integrity SHA `348aad4437afcd19b7bee248640a8e265ce954aae413b8fc4f86cd2287eb4fed` exactly equals original R01 SHA `348aad4437afcd19b7bee248640a8e265ce954aae413b8fc4f86cd2287eb4fed` for all 32,179 generated positions, despite added R02 observation.
- Compiler `g++ -std=c++17 -O3 -Wall -Wextra -Werror -lz`, 4/4 source, parity, candidate and future suffix tests passed. Scans take about 2.2–2.5 seconds per entire month with approximately 2–3 MB peak process RSS, excluding network overhead.

## First round: full January source-causal gate state

Each of 27,980 historical original R9 entry seconds is an offline observational target; in 27,496 seconds at least one Coinexx quote existed (484 absent). At the FIRST observed quote of that historical second, the reconstructed original-source gates have the following PASS COUNTS (over 27,980, missing seconds fail observation; DO NOT label absent quotes as strategy rejects):

| Causal market/state component | Passing entries |
|---|---:|
| Quote exists in exact second | 27,496 |
| M5 ATR calculation ready | 27,423 |
| ATR passes source session threshold | 27,423 |
| Observed Ask-Bid spread <= source 25-cent limit | 25,674 |
| Original minute midpoint bracket touched in historical side | 18,080 |
| Original completed-10-S1 quality passes | 3,339 |
| Same-tick market signal all gates | 2,738 |
| Same-tick market and original recreated R9 inventory/rearm allows action | 591 |
| Some quote DURING second satisfies all original market-side gates | 2,914 |
| Some quote during second also satisfies independent inventory/rearm | 716 |

S1 component study at first quote: signed velocity >=15 cents 15,628/27,496 (56.84%); directional efficiency >=0.70 4,301 (15.64%); observed range >=50 cents 23,286 (84.69%); turns <=9 27,496 (100%). Median directional efficiency 0.367. Importantly, original R9 S1 is based on COMPLETED second bars: it is unchanged across ticks within the same source second, not a new price movement occurring later in that second. Session/ATR are not the limiting Jan source component at reference snapshots. 95% identical original entry seconds with original S1 + bracket is arithmetically excluded by the observed ~10.41% same-side signal coverage; this does NOT rule out a genuinely different market-structure strategy with different entry times.

No quote in exact original second is UNKNOWN, not inferred gate failure or a new broker fill. Original `entry_time_broker` has one-second precision, so observed market-side eligibility is a quote-time proxy, not source-identical executed trade history.

## Second round: economic exit failure and conditional recovery

Original R9 January synthetic BOOK has 8,205 second legs and 2,147 first-negative / final-cycle-positive recoveries, with 97.39% synthetic second-leg positive bookings. Original REAL quote-endpoint observational research finds 2,102 complete quote endpoints on the protected 2,147 recovered second legs, of which 1,413 (67.22%) have positive quote endpoint marks. Only 42 of the 2,147 have any same-second R9 market-side signal ALSO eligible under the independent REAL replay inventory/rearm state. These are fixed-interval quote references, not broker-realized recovered profit, and not a trade rule to mimic original second-leg timestamps.

R01 independent REAL replay 32,179 trades, 14,080 positive (43.76%), 17,950 negative, 149 flat; 31,498 stop closes and 681 timeouts, aggregate **−$6,053.12 one-ounce quote-dollar equivalents BEFORE fees**. Winners average +$0.2780/oz; losers average −$0.5553/oz, requiring ~66.6% winners to break even if payoff magnitudes were unchanged (even before additional costs). In the independent REAL replay 9,601 trades have a positive rearm count, 4,219 (43.94%) quoted positive. This is not the synthetic 97.39% recovery success.

## Third round: pre-registered autonomous specialists and exit logic

The source-only C++ prototype has four explicit modes: mode 0 preserves original R9 exact baseline; mode 1 **continuation**, requiring last completed M1 directional change >=$0.20/oz and completed 5-second directional movement >=$0.20/oz with efficiency >=0.55 at the minute bracket; mode 2 **failed-breakout reversal**, requiring a causally witnessed opposite bracket break followed by a return across minute midpoint plus completed 3-second confirmation; mode 3 **regime-routing hybrid**, choosing continuation if completed M1 displacement is strong, otherwise rejection, and rearming opposite ONLY after its own observed losing exit plus renewed confirmation. The new specialist exits use an initial 75-cent price stop relative to quote-side Bid/Ask, a $0.55/oz activation with $0.25/oz trailing offset, $0.75–$0.85/oz fixed target and a 30-second maximum hold. Not broker accepted fill/ticket/stops; no partial fills, slippage, commission, queue, spread recovery, broker margin, liquidations or financing modeled. All limits are candidate research assumptions, not validated optimizers or owner-approved risk settings.

| Mechanism | Trades | Positive REAL quotes | Entry+exit matches original ±2s | Pre-cost one-ounce quote P&L |
|---|---:|---:|---:|---:|
| R9 REAL baseline | 32,179 | 14,080 | 441 (1.58%) | −$6,053.12 |
| Structural continuation | 19,253 | 8,314 | 266 (0.95%) | −$3,879.05 |
| Failed-breakout reversal | 36,497 | 16,402 | 620 (2.22%) | −$6,861.78 |
| Hybrid + conditional recovery | 22,525 | 9,689 | 299 (1.07%) | −$4,577.29 |

**Acceptance: FAIL on ALL three independently generated new candidates, plus the baseline.** Baseline exceeds 27,980 count but not 24,368 profitable exits or 95% same-side one-to-one original entry/exit accuracy. Reversal exceeds 27,980 count but fails all others. Continuation and hybrid fail all count and alignment gates. Every candidate is quote-P&L negative before costs. There is no evidence of a deployable R9 successor from R02. The ±2 seconds joint match is an explicit earlier R01 measurement proxy; the owner has not defined a different exact unit for the 5% timing/price tolerance, so do not silently substitute an easier metric.

## Next scientific gate, not an R02 claim

The evidence strongly motivates a causal **opportunity universe** built from independent REAL-tick quote-ordinal events, completed MTF trend/structure, execution-side spread and first-passage outcome hazards. Use matched same minute/session/side/spread positive and negative controls, paired first-to-second recovery sequences and timed news only with provenance. Do not train on R9 original synthetic future outcomes or force original entry/exit seconds into the trading engine. Compare the opportunity universe's executable economic survival before optimization. Freeze February and future months for out-of-sample scientific testing; only promote a fully causal MQL5 port after January joint targets AND later holdouts pass. It is entirely possible that the current requested target combination is infeasible on source REAL ticks; no unsupported guarantee is made.

## Deliverables and preservation

`r9_r02_diagnostic.cpp`: source-exact fully independent R9 replay with observer; `r9_r02_routers.cpp`: candidate source; `verify_r02.py`: four scientific checks; `entry_state.csv.gz`: 27,980 concise observational causal state rows (not a trade signal dataset); `R02_RECEIPT.json`, `R02_EXPERIMENTS.csv`, original-source financial and research root cause report. No raw Coinexx data or duplicate entire merged datasets. Future modifications only on isolated branch and after scientific acceptance. The frozen original EA and July R8/S100 V2 account policies are not modified.
