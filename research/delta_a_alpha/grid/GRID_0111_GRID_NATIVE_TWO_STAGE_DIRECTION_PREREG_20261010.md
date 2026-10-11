# GRID0111 PRE-REGISTRATION — grid-native two-stage quote-side direction research
Date: 2026-10-10. Branch: delta-A-alpha. Immediate parent HEAD before registration: 3073fd6682595e1262141fc52a8672d38faa594f. Scientific parent: J0109/GRID0109; J0110 handoff only. Status PRE-REGISTERED hypothesis only; no trading enabled.

## Source and baseline
Original GRID0108 reproduce_from_original_quotes.py, clean_grid_0104_ancestor/grid_event_research.py + grid_event_economic_geometry.py, and GRID0109 scripts. GRID0109 ZIP sha256 5c00ef0f7a49864a9d92355a1a740e99982447b0b4a693b37f6cfcc3978723da; GRID0108 ZIP sha256 dc03dac3995e7db9a2c1a29a05f068dc8e1be7b554ca3d6337cdeb305b050c88. Original raw Jan–Jul readonly; August SEALED. Virtual gap G=max($0.75,1.5x past/current observed quote EWMA spread alpha .001), 7s cooldown; event sign +1 is downward crossing/creator reversal BUY; -1 is upward crossing/creator reversal SELL. K5 = abs(mid at T0 - last observed mid by T0-300s)/max(current spread,$0.10). K2 broad >=2, K4 nested >=4. No calendar-hour, session, or month feature in decisions.

## Question and predeclared hypotheses
Can a grid-native T1 sign election on later observed real Bid/Ask improve after-cost SIGNED forward markout and preserve daily/hourly opportunity density without changing T0 grid? H0 none of these methods produces consistent positive after Bid/Ask + $0.02 fixed roundtrip hypothetical fee markout at 30/120/600s across chronological months.

T0 yields one virtual opportunity ID and TWO uncommitted sign alternatives. T1 is a genuinely later tick, never T0, never selected with future markout. Primary scan deadline (0,15s]. Tests:
A. CONT-ESCAPE: first subsequent mid travel in direction of T0 crossing at least f*G, select continuation opposite of creator sign; primary f=.40, sensitivity f=.20/.65.
B. RECLAIM: first subsequent mid travel against T0 crossing at least f*G, select creator reversal sign; f as above.
C. FIRST-RESPONSE RACE: whichever A or B quote trigger happens first selects the sign; deduplicate simultaneous T1 quote collisions by retaining earlier parent T0 ID only, no hindsight.
D. FAILED-ESCAPE-RECLAIM: after source tick satisfies A with .20*G, later source tick crosses beyond T0 mid by .20*G against T0 crossing inside 30s; select creator sign at that later tick. D screen on K2 first.
E. DELAYED-T1 DRIFT control: T1 first observed tick at/after 250ms or 1000ms from T0, elect observed sign of drift vs T0, abstain if zero; not T0 pricing.
Source tick quote is entry Ask for BUY and entry Bid for SELL. Future first quote >=T1+30/120/600s, reject >=10s late. Liquidate hypothetical BUY at future Bid, SELL at future Ask, charge $0.02 roundtrip only once. Source spread already included, never double count. Additional $0.10/$0.25 roundtrip slippage and 250/1000ms signal-to-pricing latency are declared sensitivity, not primary results. Markouts are NOT actual fills, trade PL, MT5 certification, or portfolio balance.

First-passage: only OFFLINE after T1, first future source-quote-side crossing to >=+$1 (after fee) favorable versus <=-$1 adverse within 120s, with absolute order determined by ordered ticks. It never changes T1 choice; no midpoint/OHLC path fills.

## Windows, scoreboards, decision standard
Jan–Apr exploratory development, May–Jul later chronological diagnostic only; all seven already previously inspected, no pristine holdout. August SEALED. Show per month, day and actual UTC-hour quote-side mean, positive-rate, worst observations, unsupported hours, quote-valid counts, raw K2 and K4 and T1 counts, and ratio against original R9 daily reference (T1 raw candidates must NEVER count as qualified fills). Complete comparison against frozen 3332 baseline eligible weekday UTC hours; no weak UTC-hour routing. Record all variants/multiplicity, failures and parameter neighborhood, no retuning May–Jul as blind.

Promote NOTHING without robust positive signed after-cost expectancy across months, participation/cost resistance and ultimately untouched independent data. Frozen GRID0104+K2/K4 retained. No sessions/HTF/Vertical L1-L7 orders, no Martingale, no increasing lot, no source modifications, trading_enabled=false; later fully integrated system and MT5 real ticks require separate authorization/certification.