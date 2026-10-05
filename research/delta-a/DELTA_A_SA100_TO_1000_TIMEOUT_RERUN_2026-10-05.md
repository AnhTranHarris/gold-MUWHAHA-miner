# DELTA-A — $100->$1,000 timeout recovery / January rerun — 2026-10-05

**Status:** COMPLETE RESEARCH HANDOFF / EXPERIMENTAL / NOT A MILESTONE / AUGUST SEALED / NOT MT5 AUTHORIZED

## Timeout forensic decision

The durable helper ledger showed that the last helper marked COMPLETE before the delivery timeout was `sa100_r2_port_month.py`, a completed failed candidate. The following `sa100_build_core_stop_variants.py` state was explicitly `INCOMPLETE_ANALYSIS_DO_NOT_RESUME`.

Per owner instruction, the incomplete helper was **not resumed**. The stop-variant work was rebuilt from scratch beginning with January.

Unverified scratch artifacts from the timed-out workspace are quarantined and must not be used as evidence:
- `DELTA_A_R2_EVENT_SHOCK_FEATURES.csv`
- `DELTA_A_SHOCK_GUARD_SIGNAL_SCREEN04.csv`
- `DELTA_A_SHOCK_GUARD_CAPITAL_NARROW04.csv`

## Rerun 01 — exact January stop variants

Recovered exact R2 January event ledger:
- rows: **39,253**
- SHA-256: `00343daacb5aed5ac8c2fb45b2cee87f36e8347aa0bcd56f6c7d3e43d5500eef`
- frozen aggregate: **+$12,239.46**

The raw-tick/P75 no-stop rerun matched **all 39,253 rows exactly to floating-point precision** and reproduced +$12,239.46.

Preregistered hard-stop results:
- $3: +$5,820.24
- $5: +$8,495.51
- $7.50: +$9,538.68
- $10: +$9,950.98
- $15: **+$12,468.31**

Conclusion: ordinary tightening below $15 sacrifices too much expectancy. $15 slightly improves January net but does not solve seed-capital tail risk.

## Rerun 02 — $100->$1,000 ordinary capital screen

216 January stop/slot/session configurations were rerun.

A few achieved 100% **realized-balance** survival, but the least-bad 100%-survival configuration still had about **69.23%** of rolling starts below $60 and a worst realized balance near **$1.94**.

Conclusion: plain stop/slot/session tuning is structurally insufficient.

## Recovery directional screen

At exact adverse trigger times, the remaining raw-tick path was tested as:
- counter switch,
- counter overlay,
- one fixed same-side add,
- delayed same-side entry,
- delayed counter entry.

Best event-level counter overlay:
- adverse trigger: $10
- counter horizon: 30 s
- net: **+$14,574.76**
- PF: **1.07375**

Best one-slot counter switch:
- adverse trigger: $7.50
- counter horizon: 30 s
- net: **+$11,687.24**
- PF: **1.07157**
- worst combined episode improved from about -$321.82 baseline to about -$81.41.

However, the counter-switch capital replay failed because it realizes the primary loss before the counter can recover it. Switch-as-rescue is rejected for $100 seed capital.

## Leading architecture — temporary counter overlay

Leading January lane:
- fixed 0.01 lot;
- SAFE primary episode ladder: 1 slot below $250, 2 below $500, 3 below $750, 4 below $1,000;
- while realized balance < $200, admit new primary episodes only during London/NY overlap;
- if an admitted primary reaches **-$7.50**, open one equal **0.01 opposite-direction counter overlay**;
- keep the original primary open;
- counter overlay lifecycle: **30 seconds**;
- no real architecture handoff before **$1,000**.

Closed-balance rolling-start result:
- 26/26 realized-balance survivors;
- below $60: ~23.08%;
- below $30: ~3.85%;
- worst realized balance: **$17.68**;
- for the 14 starts with at least 15 calendar days of January runway: **14/14 reached $1,000**.

## Exact tick floating-equity / margin sensitivity

The leading lane was then replayed tick-by-tick using raw January Dukascopy ticks and P75 research quotes.

Conservative margin sensitivity:
- 1:500;
- 0.01 XAUUSD treated as 1 oz notional;
- full margin charged to every position, including opposite hedge legs;
- this is deliberately conservative and is **not** a substitute for broker-native MT5 margin/stop-out semantics.

Results across 26 rolling starts:
- equity stayed above zero: **26/26**;
- margin level stayed above 100%: **26/26**;
- margin level stayed above 50%: **26/26**;
- worst minimum tick equity: **$12.49**;
- worst minimum free margin: **$1.49**;
- worst margin level: **109.30%**;
- maximum physical positions: **8**;
- starts reaching $1,000 before January end: **24/26** (the two misses had only ~12 and ~2 calendar days of usable January runway);
- median successful time to $1,000: **~15.57 days**;
- below $60 tick equity: **~26.92%**;
- below $30 tick equity: **~15.38%**.

Interpretation: this is the first micro-capital architecture in the restarted work that survives every January rolling start under the current tick-equity/full-margin sensitivity, but it is **not promotable** because the equity/free-margin tail remains too close to the cliff.

## Rejected seed refinement

A stricter low-balance filter using London/NY overlap + CONT ownership + $2.375 source-gap was tested. Although that subset has high average January expectancy, using it as the seed gate starved the account and worsened rolling-start survival.

Retain the broad overlap-only gate below $200 for now.

## Next unit

`SA100_JAN_OVERLAY_TAIL_FLOOR_RESEARCH03`

Goal: raise the worst equity/free-margin floor materially while preserving the current $1,000 velocity. Candidate causal mechanisms:
- volatility-normalized adverse trigger rather than fixed $7.50;
- account-equity/free-margin-aware overlay admission;
- regime-specific overlay duration;
- event/news proximity state;
- capital-floor rescue mode that does not freeze trading;
- recovery-slot reservation and physical-position cap;
- causal session/regime features rather than month-coded tuning.

August remains SEALED. Production MQL5 remains unauthorized.
