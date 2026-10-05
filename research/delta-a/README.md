# DELTA-A — R9 Grid Side Research

Status: **MAJOR RESEARCH MILESTONE — R9 GRID MILESTONE 01 / PRE-AUGUST**

This branch is an isolated side-research lineage derived from the DELTA evidence base. It must not modify or advance `delta/CURRENT_STATE.json`, DELTA promotion state, the DELTA workbook cursor, or any DELTA candidate.

## Current authoritative rollback target

- `research/delta-a/DELTA_A_R9_GRID_MILESTONE_01.md`
- `research/delta-a/DELTA_A_R9_GRID_MILESTONE_01.json`
- `research/delta-a/DELTA_A_R9_GRID_MATURE_FILTER_MANIFEST.json`
- `research/delta-a/DELTA_A_R9_GRID_MT5_BUILD_CANDIDATE.md`

The earlier R2 hard checkpoint remains preserved as historical provenance.

## Current architecture

The grid is no longer a conventional unlimited physical basket system. It is a causal high-frequency specialist substrate with:

- volatility-normalized virtual grid geometry,
- cold-start BOOTSTRAP routing,
- a calendar-blind maturity gate,
- a mature multi-specialist bank,
- source-specific bounded lifecycles,
- selective recovery handoff,
- deterministic event de-duplication,
- a portfolio-pressure wrapper.

### Cold-start -> mature transition

The system becomes mature-eligible only after:

- 25 active signal days, and
- 25,000 completed outcomes.

The actual switch waits for the next market inactivity gap of at least 24 hours. No month name is used in the rule.

A parity audit reconstructed all **186,901** pre-pressure Jan-Jul events exactly.

## Jan-Jul tick-level milestone

Research execution: native ordered Dukascopy signal ticks + frozen `DUKAS_COINEXX_LIKE_P75` comparison fills.

- trades: **186,569**
- winners: **113,958**
- win rate: **61.08%**
- net: **+$194,674.33**
- expected payoff: **+$1.0434/trade**
- PF: **1.2525**
- gross loss: **-$770,911.86**
- true max floating-equity DD: **$27,904.26**
- max simultaneous positions: **250**
- max absolute directional imbalance: **231**

All Jan-Jul months are positive in the accepted trade ledger.

## R9 SYNTH alignment

- trade count: **85.1%**
- winning-entry count: **59.6%**
- net profit: **63.0%**
- expected payoff: **74.0%**

The remaining large weakness is loss efficiency / PF, not signal frequency.

## MT5 status

This milestone is a **potential future MT5 EA build candidate**, not an authorized EA.

Before MQL5 production:

1. owner must explicitly authorize the build;
2. August holdout must be separately unsealed/validated;
3. physical-exposure scaling must be designed for the intended account size;
4. Coinexx `Every tick based on real ticks` parity must be run;
5. live-demo forward testing must pass before funded deployment.

The research account can reach 250 simultaneous 0.01-lot positions. That is not suitable for a $100-$500 account without a separate physical-exposure/margin adapter.

## Hard rules

- August 2026: **SEALED**
- Martingale: **FORBIDDEN**
- lookahead: **FORBIDDEN**
- main Delta promotion: **NONE**
- production MQL5 authorization: **NO**
- P75 synthesis inside live EA: **FORBIDDEN**

## Small-capital fallback milestone

The first preserved micro-capital fallback is **R9 Grid Small-Capital $500 Adapter V1**:

- fixed 0.01 lot,
- virtual full event engine,
- CORE_H4_M1800 physical bootstrap specialist,
- 1-to-5 balance-gated physical concurrency,
- scheduled-market-gap guard,
- Feb-Jul tick-level survival from $500.

See `DELTA_A_R9_GRID_SMALL500_FALLBACK_MILESTONE.md`. This fallback does not replace R9 Grid Milestone 01.
