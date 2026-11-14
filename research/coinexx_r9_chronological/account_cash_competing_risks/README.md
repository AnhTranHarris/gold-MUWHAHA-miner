# R9 v1.94 research: account-currency competing-risk utility (Python-only phase 1)

**Status:** SOURCE-EXACT RESEARCH ENGINE ADAPTER READY, SYNTHETIC TESTS PASSED. NO MODEL-DRIVEN MT5 CHANGE, NO FULL-MONTH COINEXX BACKTEST RUN IN THIS CHECKPOINT.

**Do not mutate production R9 v1.94**: preserved compiled source checkpoint https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/r9-v194-standalone-compile-repair-20261113 at commit 813baf96f2b381be5fc7896aac8b08a966114948. The Python branch forks the existing source-pinned Coinexx research branch b4ab1bfee01dda1d2c410a99c07a4dcc727c5590 and does NOT include changes to any Experts/*.mq5 or *.mqh. The v1.90 critical rollback 8729a6345655a7b4ea31facc81982004ee2b8921 remains untouched.

## Scope: answer the real cash question, not refit a favorable-barrier AUC
We want a model that improves *full-system net realized account cash per hour*, preserving as much R9 throughput as economically feasible under the gross-loss governor, with average holding <=30s. This first Python implementation measures whether a particular original R9 entry could attain a **net 1.75 units of account currency** before R9's own real-time protective stop or timeout. It uses only the ORIGINAL source-ordinal Coinexx Bid/Ask tick history and ORIGINAL unchanged Python R9 engine.

### Explicit required monetary assumptions
The Coinexx ticklogger does NOT contain actual fills, position sizes, commission, funding, account currency, rejected orders or margin. For BUY start at Ask, mark liquidation at future Bid; SELL start Bid, mark liquidation at future Ask. No free mid-price fills or double charging spread.

For a FIXED 0.01 lot, let:
- K = broker-calibrated account-currency profit for a +1.00 XAUUSD quoted-price movement *at that exact lot size* (do not assume USD account or fixed contract size).
- C = assumed total roundtrip account-currency cost not already represented by Bid/Ask: commissions, realized/assumed slippage, fees, swap if applicable.
- g = desired positive net account-currency profit (default 1.75, **not** automatically "USD" for non-USD account).
- DeltaP_min = ceil_in_cents((g+C)/K) is the minimum **liquidation-side** favorable quote improvement from actual Ask entry (BUY) or Bid entry (SELL).
- pi(t) = K * [BUY(Bid(t)-Ask(entry)) or SELL(Bid(entry)-Ask(t))] - C, with XAU movement measured in whole quoted-price dollars.

Example ONLY if a checked Coinexx/MT5 contract actually produces K=1.00 account currency per +1 XAUUSD for the configured 0.01 lot, and realistic total C=0.20: g=1.75 requires liquidation-side price improvement 1.95 XAU quoted dollars = 195 Coinexx integer cents. No such contract/cost is inferred from raw ticks. Confirm using real MT5 OrderCalcProfit, order fills and commission statements.

**No v1.93/v1.94 account governor claim:** Python baseline does not simulate actual account equity, order rejects, margin, cross-EA positions, 1-second timer or the governor. The governor remains a separate future capacity constraint.

## Competing events: observed first cause
For each original R9 position (no synthetic added orders), with a fixed 30s decision horizon:
1. GOAL_BEFORE_R9_EXIT: a *later* observed liquidation quote crosses the account-cash goal before R9 itself stops/times out. The observed favorable quote is shadow-only and does NOT close the original R9 in the research engine.
2. R9_STOP_BEFORE_GOAL: the original R9 initial or TRAILING protective stop closes before goal. This may be **a profitable trailing stop**; classify its economic payoff with its actual sign.
3. R9_TIMEOUT_BEFORE_GOAL: the original 30-second policy requests/closes on the next available observed quote before goal. Actual wallclock hold can exceed 30s; record true exit time separately.
4. CENSORED_QUOTE_GAP/CENSORED_SOURCE_END: quote gap above the predeclared 10s or insufficient source future. Do NOT manufacture an exit, target or zero return.

At the same source ordinal, if prior original stop is triggered, the protective exit has conservative precedence over target. Equal time_msc source ordinals stay in original arrival order. Any target first event is OBSERVATIONAL; if early close were actually executed, later R9 entries, rearming, portfolio exposure, governor and profits would change. Therefore early-target overlay PnL is **NOT a new system backtest**, and must not be presented as improved realized profits/hour.

### Cause-specific hazard and conditional cash utility
For side a, as-of context x, and causes j in {target, original stop, original timeout}:
- lambda_j(t|x) is the cause-specific conditional risk at t, counting only episodes still active and observed.
- S(t|x) is the probability no competing event has yet occurred.
- F_j(T|x) = integral_0^T S(u-|x) lambda_j(u|x) du.
- Our finite-sample estimator is a deterministic Aalen-Johansen risk-set product over source-order-observed event times, with explicit gap right-censoring.

A basic entry-time scenario utility is:
U(x) = sum_j F_j(30s|x) * E[net account cash | first cause j,x] - lambda_risk * CVaR_95(loss cash | observed x).

This is a *train-only retrospective conditional utility scenario*. Under non-independent censoring (e.g. quotes stop during unusual regimes), the estimator may be biased. Context groups with >10% censoring or fewer than 100 samples abstain by default; no zero-filled missing predictions. To model live account-aware hourly utility later, add projected governor cash budget consumption, execution refusal rate, opportunity cost, and occupancy-aware follow-up trades.

The estimator reports cumulative incidence at frozen horizons 1,3,5,10,15,20,30s, with source-native session and quote spread bands, or simpler predeclared groupings. These are NOT newly optimized thresholds. Tail cost CVaR and training cost scenarios are explicit.

## Existing original Coinexx backtester integration
Reuses WITHOUT MODIFICATION:
- research/coinexx_r9_chronological/src/coinexx_r9/ticks.py (supports broker-export and R9 TickLogger columns, preserves source-row ordinals and equal-ms order)
- research/coinexx_r9_chronological/src/coinexx_r9/r9_baseline.py (original v1.90 entry, stop, trailing, timeout and rearm)
- research/coinexx_r9_chronological/src/coinexx_r9/engine.py (same stream semantics)
- Existing frozen 155-feature score lineage from R9 v1.94 remains separate; THIS FIRST PASS does not re-train or gate with the old five-second ROC-AUC model. Later, compare exact model scores at the same ORIGINAL R9 source ordinal, not post-filter counterfactual entries that were never part of the original training universe.

Source market data: the original compressed XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz or original R9 TickLogger only; never Dukascopy. All prior January–September dates are already exposed to research and are not pristine future OOS.

## Run the existing Python backtester directly against ORIGINAL local Coinexx gzip

1. On your existing Windows research machine, check out this branch. No new data downloads needed if the Coinexx month files are already present on that machine.
2. Verify MT5 account currency and K via OrderCalcProfit at a FIXED 0.01 lot; provide empirically supported extra roundtrip cash cost C. This is external account calibration, **not a second historical market-data source**.
3. From the repository root, run below. The numbers K=1.00 and C=0.20 here are clearly a *demonstration scenario*, not claimed broker facts:

    python research/coinexx_r9_chronological/account_cash_competing_risks/src/cli.py replay --ticks "C:\Coinexx\XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz" --account-currency USD --cash-per-one-xau-dollar 1.0 --round-trip-cost-cash 0.20 --goal-net-cash 1.75

This by default emits only a compact JSON on standard output. NO gzip reconstruction, tick reexport, second-bar export, feature archive, new LightGBM training or large per-tick output is performed. Use --expected-source-sha256 with the original known SHA256 to refuse altered source; this performs one EXTRA compressed-file hash pass but never writes a copy.
Optional --max-ticks 100000 is only a source smoke test, always marks truncation and EOF censor; do not infer full-month economics from it.

When --episodes-out is specified, the CLI also writes a tiny PATH.csv.gz.receipt.json that pins account currency, the conversion rate K, all fees, original R9 config, truncated status and optional original SHA256s. Chronological fit-evaluate REFUSES missing receipts, truncated samples, mixed contract/lot/fee/currency scenarios or train/test timestamp overlap. Source hashes are reported as unverified unless the caller provides --expected-source-sha256; do not promote results from unverified raw sources.

For actual historical model calibration you MAY explicitly request one compact original-trade-only ledger using --episodes-out path.csv.gz. This writes one row per ORIGINAL completed R9 position, not one row per tick. Keep it local; do not upload 10GB dataset replicas. Only this optional little ledger is used to build cause hazards and test continuation.

4. Frozen chronological research fit/evaluate example (ONE comparison only, not broad retuning):

    python research/coinexx_r9_chronological/account_cash_competing_risks/src/cli.py fit-evaluate --train-episodes jan.csv.gz feb.csv.gz mar.csv.gz apr.csv.gz --test-episodes may.csv.gz --by session_spread --min-group-count 100 --max-censor-fraction 0.10 --cvar-penalty 0.25

The tool refuses overlapping input file paths or any training entry timestamp on/after the first test timestamp. These dates are **chronologically separated but previously research-exposed**; do not label as pristine OOS.
The full monthly and nine-month replay was NOT executed in the assistant's environment for this checkpoint; source tick archives remain in the owner's Drive/Windows research machine, and no raw duplication is required for implementation.

## Evaluation gates before predicting/authorizing entries
- BASELINE PARITY: exact original trade count, entry ordinals/quote sides, reason codes and observed source chronology match the original unmodified engine. Test class checks baseline trades/entries identical when overlay observer is attached.
- EVENT LABEL PARITY: manually inspect representative goal-first, profitable stop-first, losing stop-first, timeout, gap and equal-ms samples; never use a future quote in entry x.
- ACCOUNT MONEY PARITY: account currency and per-0.01-lot K from OrderCalcProfit, roundtrip fees; actual broker slippage and freeze constraints still not known from ticks.
- CAUSAL COMPETING RISK: train on earlier months, test later; compare incidence calibration, abstention, Brier score and expected net cash conditioned on ONLY as-of signals. Distinguish $ per trade from realized $ per entry-hour.
- WHOLE SYSTEM (NEXT): explicitly simulate hypothetical early closes and reruns of original R9 entry state, rearming, portfolio governor/transaction fees/execution. A target before original exit does not on its own prove more profit/hour.
- VOLUME & RISK: publish candidate counts, attempted/filled count assumptions, retained throughput, cash per hour per DATE/HOUR (not only aggregate 16h bucket), gross realized loss, adverse tail CVaR, average and tail hold, drawdown/capacity. Do not raise risk budget just to improve score.

## Tests
GitHub workflow: .github/workflows/r9_account_cash_competing_risks_ci.yml
Tests do not load/download real market data. They verify exact original R9 engine-trade path parity, no synthetic spread-free fills, 195c cash goal scenario, profitable trailing-stop classification, source ordinals including equal-ms, gap/EOF censor, Aalen-Johansen risk-set math, training-only tables, censor abstention and tail loss.
MQL5 EA source is NOT modified. MetaEditor is NOT involved in this research branch.

**Decision:** This is the correct minimal first competing-risk layer to connect a real model to economic outcomes; it is not yet a certified profitable R9 variant or the complete account governor simulator.
