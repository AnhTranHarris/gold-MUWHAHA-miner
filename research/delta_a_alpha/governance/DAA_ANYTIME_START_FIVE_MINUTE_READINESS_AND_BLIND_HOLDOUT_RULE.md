# Delta-A-alpha — Owner Governing Rule: Anytime Start, Five-Minute Readiness, Seven-Month Development and Sealed Blind Holdouts

**Authority:** owner directive, 2026-10-08. **Status:** mandatory for Delta-A-alpha V1 engineering, Jan–Jul research, V2+ adaptations, Python tests, MT5 EA and capital-ladder qualification.
**Supersedes:** any experimental workflow implying that a deployed EA must wait hours, days or weeks to generate first trades, or that isolated indicator performance is a sufficient assessment.
**Preserves:** frozen V1 eight-layer order, January–April completed research, rollback branches, current May cursor (owner-paused), and read-only main `delta`.

## G1 — Mission and unified product

Delta-A-alpha is a single, commercially oriented, self-adjusting **XAUUSD MT5 Expert Advisor**. It must use **the complete Vertical Grid System V1** to harvest justified trading opportunities and manage physical risk. Every adaptive module must cooperate with, not replace, the permanent L0–L8 responsibilities:
```
L0  ordered actual executable Bid/Ask ticks / first-touch chronology
L1  session-specific grid geometry
L2  completed H4/H1/M15/M5 environment, location, phase, transfer
    + research candidate: completed-M5 Opportunity Supply Observer
L3  London/overlap/New York hourly high-volume harvesting
L4  separately parameterized Asia geometry
L5  Watchdog earned scout/renewal and campaign control
L6  structural trend-within-trend native routing
L7  bounded wrong-direction recovery
L8  global physical capacity, full-equity heat, margin and survivability governor
```
Adaptation may adjust any layer's market-state-dependent, causal **settings** (geometry, target/stop/lifecycle, participation intensity, source slot priority, renewal depth and capacity), but may not bypass its responsibilities, use the calendar month to choose a rulebook, change the fixed **0.01 lot** during V1 testing, deploy Martingale/DCA rescue, or promote results selected from a holdout.

## G2 — Research/validation partition and future-data embargo

1. **January 1–July 31, 2026:** development evidence, calibration, causal rolling-learning design, per-layer monthly discovery, integration, regression and daily/weekly/monthly evaluation. Each month adds transferable market-state behavior; no month-number rules.
2. **August 1–31, 2026: SEALED true blind holdout.** Do not inspect its price outcomes, derived features, outcomes, model scores or capital curves during strategy design. Previous possession of raw bytes is not permission to unseal. Owner-directed explicit release is required after freezing candidate rules, coefficients, source code, risk caps and execution simulator.
3. **September 1–30, 2026: RESERVED second true blind holdout**, to be used only after the owner supplies/authorizes the relevant real MT5 test data. Do not claim September's data have been obtained or validated. Do not tune August failures into September without separately declaring the changed validation status and obtaining approval.
4. A truly blind evaluation must use one immutable code/configuration snapshot, exact source hashes and a documented predeclared acceptance scorecard. No inspection-driven threshold changes within the scored holdout.
5. If simulating an earlier **historical** deployment date (e.g., February 1), the model can use only market data, previously completed bars and training labels genuinely available **before that simulated T0**. Later Jan–Jul discoveries may inform present-day development, but cannot be retroactively inserted into a supposedly blind early-2026 as-of test.

## G3 — Arbitrary deployment and five-minute startup service level

The EA shall be able to start on **any calendar date, at any wall-clock time** and automatically identify whether XAUUSD is currently tradable. It shall support mid-session restarts, account restarts, new broker terminal sessions and clock/DST transitions.

**Operational SLA, provided valid broker connectivity, live quotes, usable prior historical prices, margin capacity and an open market:**
- By **T0 + 300 seconds** (and ideally at first actionable quote), fully initialize the eight-layer decision pipeline and **be able to submit a qualified 0.01-lot scout/order**. Do not require a new full M5/H1/H4 bar after T0 if already-completed, pre-T0 history supplies the state.
- On first live tick, register executable Bid/Ask, active session/DST, portfolio state and protective risk. Run in a preseeded **trade-capable mode** immediately as soon as required state is valid.
- The first viable signal can be proposed in the first seconds. **Never require an online learning warmup, 16/32/128 closed winners, completion of a new monthly training block, or earning Watchdog renewal credit before initial scout eligibility.** Renewal children may still require actually funded, already closed predecessor evidence.
- An order need not be **forced** within five minutes when price provides no qualifying edge, market is closed, spread is unsafe, account funds/margin are insufficient or historical/quote data are invalid. Record the reason explicitly; never invent a fill or claim guaranteed immediate profit.
- If deployed while XAUUSD is closed, measure the five-minute trade-readiness deadline from the first **tradable live quote** after reopen, not the time the market is closed. Nontrading / missing-history status is not a valid success.

**Two separately evaluated acceptance metrics:** `time_to_first_order_eligible_ms <= 300000` in all valid test cases; and actual `time_to_first_funded_trade_ms`, with first-trade-within-5-min frequency and no-trade reason distribution reported explicitly. **A qualified first fill or profit within five minutes is an optimization objective, not an unconditional promise.**

## G4 — Prior-history bootstrap and continuous learning

- Load only **pre-T0 broker historical ticks/bars**, model assets trained as of T0, last known trade/campaign state and account/position inventory. Reconstruct completed H4/H1/M15/M5 structure and session/phase geometries from history; missing state must remain explicitly unknown rather than look ahead.
- Ship a prequalified, reconstructible **cold-start rule base** that operates without local trade history. Independently operated first-parent/scout, high-volume and Asia candidate-generation routes must be eligible immediately after initialization and checks; learning upgrades but does not gate initial participation.
- Add rolling, entry-known adaptation after each newly completed bar, funded closed trade and independently matured label. Use only lagged observations and strict event-time ordering; shadow outcomes are not funded evidence.
- Preserve and restore state checkpoints across crashes/reboots. During restart, reconcile open positions, active campaign genealogy and risk with MT5 before adding orders; no duplicate re-entry from the same quote/event.

## G5 — High-performance acceptance and required scorecards

Assess *the entire funded portfolio*, never isolated indicators. For each month Jan–Jul and then frozen blind August/September, provide day/week/month/cumulative:
- net and gross profit; **gross loss**; profit factor; win rate; expected payoff/expectancy; funded trade count and velocity; qualifying active days and weeks;
- full-tick **floating equity drawdown** and closed balance drawdown; risk-adjusted opportunity capture; maximum simultaneously open positions, aggregate lots, actual spread, commission, execution slippage assumptions, free margin, used margin, liquidation avoidance;
- diagnostic attribution and participation denials for each layer L0–L8 and active market state, including missed favorable events / forecaster false vetoes;
- startup `T0`, pre-T0 history loaded, first valid quote, first eligible signal, first proposed order, first funded fill, first closed trade and five-minute readiness reason codes.

Benchmark against canonical R9 SYNTH and R9 REAL as **comparators**, not financial oracle or guaranteed result; historical optimized Jan/Feb/Mar frontiers do not prove forward profitability.

## G6 — Capital survivability ladder

Use the fixed **0.01-lot** initial research rule and require stepwise exact-tick, broker-relevant margin/stopout qualification at **$100,000 → $1,000 → $500 → $300 → $100 starting balance**. Each tier has its own global physical inventory, per-campaign cap, max adverse excursion and reduce-only circuit breakers; never silently assume the $100K concurrency fits $100. If minimum executable margin for even one 0.01-lot XAUUSD order exceeds available free margin, report this as a funding infeasibility, not an EA trade-generation failure and never bypass broker limits.

## G7 — Enforced experimental protocol and preservation

1. Preserve complete, accepted Jan–Jul discoveries and regression requirements with source hashes and per-layer lineage; do not reconstruct completed research from chat.
2. Implement and regression-test the **complete** V1 L0–L8 causal state machine in Python, then MQL5 parity; not a reduced single-filter replacement.
3. Compare same-data, same-clock and same-portfolio-cap controls to each new awareness mechanism, including all forgone trades, realistic raw executable Bid/Ask, costs and first-touch protective exits.
4. Verify cold starts at diverse **previously unseen timestamps**, including Asia, London, overlap, New York, turnover, rollovers, weekends and market reopening; distinguish market closure from eligible trading failures. Test startup at varying account balances and with inherited open positions.
5. Persist crash-safe small atomic artifacts/QA and a deterministic event/restart journal. Never claim a running or future asynchronous experiment without actual execution. On a timeout resume the smallest missing checkpoint.
6. Approval to enable a candidate add-on's physical order effect requires integrated, causal financial evidence and explicit owner promotion. **An observe-only L2 awareness observer is not proof that the EA's trade economics hold up.**

## Binding pass/fail gates

- **FAIL** if the EA needs hours/days/weeks of post-start rolling history before the initial eligible order.
- **FAIL** if a valid active-market start cannot reach order-ready status within 300 seconds for reasons attributable to the software (rather than price opportunity, market closure or broker limitations).
- **FAIL** if month/date identity, future bars, hindsight outcomes or data from a sealed holdout steer entries.
- **FAIL** if gross loss, portfolio floating-equity drawdown, actual spread or margin accounting are omitted from reported financial claims.
- **FAIL** if a new V1 module disables the pre-existing profitable route without attribution and regression review, or if the entire V1 system is replaced by one indicator.
- **PASS candidate** only when full L0–L8 execution semantics, immediate startup readiness, risk constraints and integrated month-by-month metrics have been audited. High profits are a research goal, **never promised returns**.

**Owner context:** this governs all subsequent January–July development and final MT5 deployment design; August and September remain embargoed blind test sets. No research cursor/production algorithm changes are authorized by this documentation alone.
