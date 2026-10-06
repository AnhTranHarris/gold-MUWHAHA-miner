# BUILD-02 Session + Timeframe Awareness — Refinement 001

**Unit:** `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_REFINEMENT_001`  
**Candidate:** `STMR_SLEEVE_PHASE_001`  
**Status:** **ACCEPTED AS STRONGER JANUARY SESSION/TIMEFRAME FLOOR**  
**Parent floor:** `STMR-001` (+$416.23 January net)  
**Cross-month status:** January research only; Jan–Jul validation remains required.

## Owner objective

Aggressively improve session awareness and timeframe awareness before moving to
the remaining whole-grid dimensions.

The objective is not to add more confirmation filters.  It is to make the grid
understand **who owns the market state at each horizon and how ownership changes
through the trading day**, while preserving bounded 0.01-lot scalping.

## Core architecture retained

Timeframes have different jobs:

- **H4** — slower environment;
- **H1** — structural trend ownership;
- **M15** — intraday phase;
- **M5** — ownership transfer / reclaim / rejection;
- **ordered ticks** — first-touch grid event and executable Bid/Ask fill.

There is no timeframe majority vote.

Session boundaries restart the local lattice and spatial memory.  London Open
and rollover remain observe-only in this child.

## High-impact mutation — semantic sleeve genealogy

The strongest mutation was not another indicator.

Instead of one first-touch memory for the whole session, each coherent
session/timeframe ownership state receives its own **semantic sleeve** and its
own first-touch cell genealogy.

That means the same price cell may become informationally new when the
ownership state genuinely changes, but it cannot be rearmed merely because a
timer elapsed.

This produced substantially more opportunity recovery without reintroducing
same-cell churn.

### Accepted sleeves

Asia:
- `ASIA_LOWER_TAKEOVER`
- `ASIA_M15_DIVERGE_M5_RECLAIM`

London:
- `LONDON_M5_TAKEOVER`
- `LONDON_M5_RECLAIM`

Overlap:
- `OVERLAP_LOWER_TAKEOVER`
- `OVERLAP_ALIGNED_COUNTERCROSS`

New York:
- `NY_LOWER_TRANSFER`
- `NY_LOWER_COUNTERCROSS`

Late New York:
- `LATE_ALIGNED_MOMENTUM`
- `LATE_MACRO_SPLIT_TRANSFER`
- `LATE_M5_REJECTION`
- `LATE_LOWER_TAKEOVER`

Every physical trade remains 0.01 lot; maximum concurrent grid-owned positions
remains three.

## Targeted session subphase mutation

Broad session labels were still too coarse for two sleeves.

The January diagnostics supported only two targeted gates:

- `ASIA_LOWER_TAKEOVER`: **23:00–00:00 UTC**
- `LONDON_M5_TAKEOVER`: **11:00–12:00 UTC**

These are sleeve-specific state priors, not a blanket “trade only at these
hours” filter.

All other accepted sleeves retain their broader session phase.

## Canonical January replay

Source SHA-256:

`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Surface:

`DUKAS_COINEXX_LIKE_P75`

Execution:
- ordered ticks;
- BUY enters Ask / exits Bid;
- SELL enters Bid / exits Ask;
- $0.01 entry + $0.01 exit commission;
- completed bars only for H4/H1/M15/M5 state;
- no future-bar visibility;
- no Martingale;
- no loss-dependent sizing;
- no residual unpriced inventory.

### Aggregate

| Metric | STMR-001 parent | Refinement 001 |
|---|---:|---:|
| Net | +$416.23 | **+$877.78** |
| Trades | 867 | **1,518** |
| PF | 1.602 | **1.603** |
| Expected payoff | +$0.4801 | **+$0.5782** |
| Trades / active day | 43.35 | **75.90** |
| Max equity DD | $71.01 | **$61.22** |
| Max positions | 3 | 3 |
| Forced final exits | 0 | **0** |

Net improvement over the accepted parent:
**+$461.55 / +110.9%**

Trade count increased about **75.1%**, expected payoff increased about **20.4%**,
and max equity drawdown fell about **13.8%**.

### Internal January stability split

Discovery — Jan 5 through Jan 16:
- 380 trades;
- **+$110.87**;
- PF **1.347**;
- expected payoff +$0.292.

Validation — Jan 17 onward:
- 1,138 trades;
- **+$766.91**;
- PF **1.675**;
- expected payoff +$0.674.

Both halves are positive, but this remains an **internal January stability
diagnostic**, not external OOS proof.

## Risk and small-account diagnostic

- max balance drawdown: **$55.88**
- max equity drawdown: **$61.22**
- minimum equity delta from initial balance: **-$8.94**
- maximum total grid-owned lots: **0.03**
- average hold: **37.7 sec**
- maximum hold: **303.8 sec**
- skipped opportunities at 3-position cap: **565**
- TP exits: **539**
- SL exits: **915**
- age exits: **64**
- forced final liquidation: **0**

Theoretical minimum equity from the same path:

- $100 start -> **$91.06**
- $200 start -> **$191.06**
- $300 start -> **$291.06**

All three remain positive before broker-specific margin modeling.

## R9 January context

R9 REAL January:
- -$6,651.62
- 31,915 trades

R9 SYNTH January:
- +$41,520.82
- 27,980 trades

Refinement 001:
- +$877.78
- 1,518 trades

For human orientation only:
- R9 SYNTH January net attainment: **~2.11%**
- January REAL→SYNTH net-gap closure: **~15.63%**

The owner explicitly suspended the 30% milestone as a hard gate for this
dimension, so this build is judged on structural improvement first.

The remaining major weakness is **throughput**.  The grid is now economically
positive and bounded on January, but ~75.9 trades/active day is still far below
R9 SYNTH's roughly 1,300+ trades/day.

## Mutation campaign — what failed and what survived

Rejected because they reduced economics or destabilized the January split:
- simple relay-freshness gates;
- generic session-age filters;
- freshness + age combination;
- timer-only M5 rearm;
- M15+M5 timer/state rearm;
- global M1 confirmation;
- M1 “freshness” gating;
- state-episode micro-lattice resets.

The state-episode micro-lattice was particularly instructive: it could raise
full-January net materially, but discovery PF collapsed near 1.0.  It was
therefore rejected as unstable opportunity inflation.

Retained:
- session-morphed TP/SL horizons;
- role-separated temporal relay semantics;
- semantic sleeve-local first-touch genealogy;
- targeted subphase priors only where both January halves provided support.

## Concentration warning

The two overlap sleeves are weak in discovery and strong in validation,
especially `OVERLAP_LOWER_TAKEOVER`.

That is not grounds to delete them after seeing validation, because the
aggregate frozen child is positive in both halves and the objective is maximum
robust system performance.  It **is** a mandatory cross-month warning.

Do not tune overlap thresholds against January validation.

## M1 finding

M1 is not promoted as a global confirmation layer.

Some small state families suggest M1 may later have selective value, but the
sample is not large enough to justify another rule.  The accepted ownership
chain remains:

`H4 -> H1 -> M15 -> M5 -> ordered tick`

## Durability

System integration:
`research/delta_a_alpha/experiments/grid_system_session_timeframe.py`

Canonical result:
`research/delta_a_alpha/artifacts/DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_REFINEMENT_001_JANUARY.json`

Source hunt:
`research/delta_a_alpha/research/DAA_GRID_SESSION_TIMEFRAME_SOURCE_HUNT_003.md`

Parent report:
`research/delta_a_alpha/grid/DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_AWARENESS_REPORT.md`

Verified local portable replay helper SHA-256:
`943b62c4be0e84185ad9c61577d4d3dd14ce51b2cafcfb7829c47a2910ff0216`

Verified local result SHA-256:
`10994339fbe82d7dfa0907f06d643f07c09d4ad389dd4d64271431da93de5149`

## Scientific decision

**ACCEPT `STMR_SLEEVE_PHASE_001` as the stronger January session/timeframe
floor, superseding STMR-001 economically while preserving STMR-001 as its
historical parent.**

This is not Jan–Jul promotion and not MT5 authorization.

The next system dimension must build vertically on this floor; it may not
silently revert to the older +$416.23 session/timeframe behavior.
