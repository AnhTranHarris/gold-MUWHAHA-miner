# Owner-amended V1 Vertical Grid System — 2026-10-10
**Authority: exact new owner instruction, binding alongside the frozen original whitepaper. The source whitepaper remains physically unchanged.**

## OWNER INSTRUCTION — VERBATIM, NOT A SUMMARY
okay good, first is house keeping we have to get rid of jan and feb data, since the engine was made badly the results for jan and feb have been containmentatied and cannot be used, those data sets and mechinsmns, logic, etc, etc must be deleted to ensure a clean enviroement moving farwrad. r9 syth, and dukascopy must not be touch

okay now the fix, sessison aware mean that the ssasion layer has 2 clocks a UTC clock , and a session clock for sydney, tokyo, london, and ny. so that the system is aware what trading session it is in
the multi-timeframe, must be optimize per session and session overlap to provide the best possible seprate strutcul roles for the best possible oppotunies per session and session overlap

the hourly high volume haversting micro grid system looks for the highest amount of trade liquidity which has been generally the session overlap of london, and ny. to allow for the best possible opportunites to captilize on trades and oppotunites. the sydney, asia overlap will need to have a different kind of micro grid system gemoentry to take advantge of opportunies, and trades.

watchdog is a regime renewal, regime aware layer that helps determine market conditions for the session the system is in.

the trend within trend should allow for acelerated winning opputunites once a trend is found

wrong direction layer is a hyper recovery layer to help correct trades going in the wrong direction to help lower gross loss, and lower max drawdown, and hopefull turn a losing trade into a winning trade by having it go in the right direction.

the porfolito heat / capital govener forces trades to be the lowest lot possible, generally it is .01 lot for gold, trailing stop loss to help lower risk, lower drawdown, lower gross loss.  a trailing stop loss must allow a trade to breathe, and be a warning system for recovery layer to help correct.

The system is aware of major calendar events from usa, euro, asia, austrila such as holidays and weekends so that it does not confuse a closed market for miss oppotunties.

The system must be able to work together to provide the best possible trade with the best possible chance for high profits, low gross loss, low max drawdown, trade volume is to not exceed R9 syth monthly average trade volume by no more than 75%, a high profit factor (PF), and a high trade accuracy, and high trade survivability perferredably an account using only 100 to 300 dollars as it starting captial.  while maintaining a high degree of trade velocity to ensure hourly and daily profits.

## Implementable owner-approved contract (interpretive implementation contract, subordinate to verbatim owner instruction)
**Scope / cleanup:** The previous Jan/Feb V1-derived strategies, configs, metrics, cached funded ledgers, and implementation branches are INVALID AND NOT REUSABLE. The GitHub active branch removes the Jan/Feb derived directories, identified dependent J0053–J0096 funded/journal artifacts, and generated outputs. The original Jan/Feb Dukascopy ticks are RAW INPUTS, protected, and must never be deleted or altered; the R9 SYNTH and R9 REAL tester benchmarks and reports are protected and must never be deleted or altered. Original whitepaper and this governance remain active. Old Git commits are Git provenance only, not a license to revive a model. March/April derived research files are not certified as transferable after deleting their Jan/Feb ancestors; they remain NON-AUTHORITATIVE historical references until independently rebuilt and approved from the clean V1.

**L0**: ordered executable Bid/Ask tick root, zero future state. Maintain one canonical UTC timestamp.

**L1 — two views of time**: UTC master clock plus a local session-clock view for **Sydney, Tokyo, London, New York**, using DST-aware IANA time zones where applicable: Australia/Sydney, Asia/Tokyo, Europe/London, America/New_York. Track session OPEN/CLOSED/OVERLAP and broker tradability as event-time causal state; overlap is calculated from actual active intervals, never inferred from a fixed UTC month offset. Use regional holiday and weekend knowledge (USA, Europe, Asia, Australia) as context, not a substitute for executable broker market status. Do not mark a closed market as a missed trade.

**L2**: completed, role-separated H4 environment, H1 structural location, M15 phase, M5 transfer and tick entry/microstructure, each independently qualified by causal session and overlap, no universal cross-session indicator vote, no use of unfinished bars. Per-session research may optimize parameters, but active selection is ONLY by observed conditions, never a trading-month label.

**L3**: liquidity-seeking session-aware microgrid. London–NY overlap and other liquid hour/subphase regimes may deploy denser causally qualified harvesting; Sydney/Tokyo/Asia overlap uses a separate geometry/cadence/lifecycle appropriate to measured local opportunity. No forced trading or assumption that highest liquidity always gives highest net profitability.

**L4**: Watchdog is the session-conditioned market-regime observer and *earned* campaign renewal owner, with realized evidence, state transitions, capacity accounting and relock. It is not an isolated standalone profit stream.

**L5**: trend-within-trend specialist routing, enabling accelerated continuation entries where observed higher-timeframe trend and lower-timeframe opportunity align. Still tick/entry-known and globally funded.

**L6**: bounded, causally identified wrong-direction recovery. Receive trailing-stop/quality-warning state and observed directional failure from L7/lifecycle; may propose timely corrective trades using state-confirmed direction, NEVER Martingale, increasing size after loss, unbounded DCA or hindsight reversal. Higher profitability and conversion of losses into wins are explicit research goals, not guarantees.

**L7**: one shared broker-aware balance/equity/margin/exposure/collision governor; base research ticket fixed 0.01 lot XAUUSD (subject to broker minimum lot and margin feasibility); no auto escalation or loss-dependent sizing. Volatility/structure-informed trailing stops must allow position breathing, reduce preventable stop-outs, and issue graded warnings to L6. Keep hard protective stops, drawdown control, physical slot budgets and broker order-rate safeguards. Use no-lookahead current Bid/Ask tick marks.

**Calendar awareness**: planned economic calendar events, regional bank/market holidays, weekends and brokerage halts are causal timing inputs; planned high-impact releases may affect liquidity/spread/eligibility. Calendar features may NOT retrospectively define profitable periods or override actual executable quote events.

**Whole portfolio performance**: jointly maximize net profit, high win accuracy, profit factor, survivability, low gross loss, low balance/equity drawdown, and meaningful hourly/daily trade opportunity velocity. Never force hourly or daily profit without observed qualifying opportunity. Trade-count hard-ceiling research target: **monthly total <= 1.75 × R9 SYNTH mean monthly completed trades** for the benchmark months selected and frozen BEFORE optimization; use the original untouched R9 SYNTH benchmark data as source. Always distinguish trades, lots and turnover; count completed trades consistently. Evaluate for starting account budgets $100/$200/$300 using actual lot margin/cost realities; do not promise 0.01 lot feasibility at these balances absent broker terms.

**Architecture & phase rule**: only ONE clean engine under `research/delta_a_alpha/implementation/`, in strict L0→L7 spine; no imported retired Jan/Feb source code, no proposed historical Jan/Feb profitability as current, no independent sliced specialist branches recombined after the fact. Every future new chat first reads FULL governing conversation and original owner whitepaper, then this verbatim addendum; recurring five-owner-prompt reread remains binding.
