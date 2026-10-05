# DELTA-A — $100->$1,000 Survival / Velocity Research 02

**Status:** ACTIVE EXPERIMENTAL RESEARCH / NOT A MILESTONE / AUGUST SEALED / NOT MT5 AUTHORIZED

## Owner mandate — 2026-10-05

The physical micro-capital bridge is extended from the former $100->$500 target to **$100->$1,000**.

- No real architecture handoff before **$1,000**.
- $500 remains an intermediate capital state and preserved fallback reference, not the new handoff boundary.
- Fixed physical lot remains **0.01**.
- The design target for accounts below $1,000 is **100% rolling-start survival**. This is an engineering objective, not a claim; measured survival must be reported exactly.
- Longer-term architecture priority is survivability for accounts below **$50,000**, because deployment date/regime is unknowable.
- Velocity remains mandatory: survival cannot be achieved by starving the strategy of opportunities.
- R9 SYNTH remains the aspirational pattern: very low drawdown + 0.01 lot + high trade volume + high win count.

## Martingale / grid interpretation

Unbounded or exponential loss-driven sizing is not eligible for promotion.

The following are explicitly authorized as research hypotheses:
- fixed-size finite recovery grids;
- virtual-Martingale depth sensing with physical exposure delayed until confirmation;
- bounded same-direction averaging with a hard position/equity cap;
- opposite-direction counter-grid / loss-harvest specialists;
- basket recovery and reset;
- capital-ratchet / slot-compounding logic;
- volatility-normalized grid geometry;
- recovery specialists that attempt to monetize the market path causing a primary loss.

No candidate may hide a primary loss by relabeling accounting. Primary gross loss, recovery gross profit, and combined episode P&L must be reported separately.

## January raw-tick regime evidence

Source: raw ordered Dukascopy January file `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`.

Observed:
- ordered ticks: **9,135,062**
- active UTC dates represented: **26**
- daily true range minimum: **$27.135**
- daily true range median: **$79.983**
- daily true range maximum: **$769.110**
- max/min daily-range ratio: **28.34x**
- 60-minute rolling mean minute-range proxy: p10 **$1.294**, median **$2.182**, p90 **$5.704**, p99 **$16.051**
- 240-minute proxy: p10 **$1.435**, median **$2.237**, p90 **$5.195**, p99 **$16.686**
- daily mean native spread ranged from about **$0.579** to **$1.842**
- tick intensity ranged from about **121** to **624 ticks/minute** across active dates.

Session diagnostic from the same raw ticks:
- London/NY overlap: mean minute range ~**$4.567**, ~**476 ticks/min**
- London-only: ~**$2.395**, ~**235 ticks/min**
- NY-only: ~**$3.433**, ~**352 ticks/min**
- off-session: ~**$2.869**, ~**279 ticks/min**

Interpretation: a static micro-grid/stop/lifecycle policy is structurally exposed to large intra-month regime change. The seed architecture must classify and adapt to current state rather than use month identity.

## Active work unit

`SA100_JAN_SPEEDRUN_RESTART_02_1000_BRIDGE`

### Primary objective
Discover a January mechanic neighborhood that can carry $100 starts toward $1,000 with the smallest possible ruin/distress tail while preserving high opportunity throughput.

### Scorecard
Report at minimum:
- rolling-start reach-$1,000 rate;
- reach-$500 rate as an intermediate diagnostic;
- below-$80 / below-$60 / below-$30 incidence;
- account-death / infeasible-margin incidence;
- median, p75, p90 and worst successful days-to-$1,000;
- trade count / trades per active day;
- original-specialist gross profit/loss;
- recovery-specialist gross profit/loss;
- combined episode P&L;
- max physical concurrency;
- maximum floating DD and minimum equity;
- session and volatility-regime breakdown.

### Candidate families
1. Volatility-normalized micro-grid spacing.
2. Virtual-Martingale depth sensing, fixed 0.01 physical release.
3. Counter-grid / failed-thesis ownership transfer.
4. Finite same-side fixed-lot recovery basket.
5. Capital-floor ratchet with de-risk hysteresis after drawdown.
6. Profit-funded slot unlock and automatic slot relock after equity/balance deterioration.
7. Best-opportunity queue when scarce physical slots free.
8. Session-aware routing without hard session deletion unless evidence supports it.
9. Scheduled-news state machine: approaching -> restricted -> shock observation -> post-event classification -> normal.
10. Multi-horizon volatility state: seconds/minutes/session/recent-days/rolling multi-day.

## Anti-overfit rule

January may select the mechanic neighborhood, but later February-July work may not create month-specific settings. Later months may only motivate causal observable state variables (volatility, spread, tick intensity, session, event proximity, trajectory, balance/equity state). Re-run earlier months after each structural change.

August remains SEALED.

## Future MT5 implementation note

MetaTrader 5 exposes broker-aware margin calculation through `OrderCalcMargin`, symbol/account margin rules, and an economic-calendar API with event time/currency/importance metadata. These are future implementation surfaces only; production MQL5 remains unauthorized.

## Current conclusion

The first January regime audit supports the owner's concern: the micro-capital layer must be a **regime-adaptive survival/velocity governor**, not a smaller fixed copy of the large R9 Grid portfolio.
