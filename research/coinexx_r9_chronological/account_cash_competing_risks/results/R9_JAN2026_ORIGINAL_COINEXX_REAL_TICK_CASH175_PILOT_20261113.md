# R9 v1.94 — Coinexx January 2026 account-currency first-cause pilot

**Status: retrospective REAL QUOTE SOURCE-ORDINAL shadow pilot, not a new on-policy R9 v1.94 profit result. No MT5 source changes.**

## Immutable original evidence

- Original January Coinexx XAUUSD broker-export gzip, SHA256 **1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8**, contains **7,699,274** original source-ordered quote rows.
- Original frozen R9 January entry/exit ledger from existing nine-month candidate cache: **32,179** R9 positions; January candidate gzip SHA256 **718bda1cbc8e73b98569328de34b6d34d28883d60296344c7def43071499e1a9**.
- Programmatically verified ALL 32,179 original entry and exit source ordinals, entry/exit millisecond timestamps, exact BUY Ask/SELL Bid entry and BUY Bid/SELL Ask liquidation, and signed quote-price P&L against original raw Coinexx rows. Equal-ms source row order preserved. Source SHA256 matched immutable receipt. Data were read, not rebuilt or copied to Google Drive.
- First-cause research uses a 30s observation cutoff, a gap greater than 10s as right-censor and protective stop precedence on the stop execution ordinal. The actual original frozen stop/trailing/timeout lifecycle is the comparator; future ticks after its exit are NOT counted as realizable goals.

## EXPLICIT unverified account-money scenario

For illustration ONLY, let the account use USD, 0.01 lot, a broker-calibrated payoff coefficient K=1.00 account currency per +1.00 XAU price movement, roundtrip extra commissions/slippage C=0.20 account currency, and requested net target g=1.75 account currency. None of K, C, broker fills or account currency can be established from original Coinexx quote-only logs. Required favorable liquidation-side quote displacement is ceil((1.75+0.20)/1.00 *100) = **195 original XAU price cents**.

## Verified January source-path findings

| Measure | Result |
|---|---:|
| Frozen original R9 positions | **32,179** |
| Goal 1.75 reached before original R9 exit | **94** |
| Original R9 stop reached before 1.75 goal | **31,401** |
| Original R9 timeout before goal | **670** |
| Censored before first event owing to >10s quote gap | **14** |
| Goal-first fraction over all original R9 entries | **0.292116%** |
| Quote-gap censor fraction | 0.043507% |
| Goal-first mean and median time | 2.730s / 1.233s |
| Mean original XAU price return on executable Bid/Ask sides | **−0.18810777 XAU price dollars/trade**, before extra costs |
| Original scenario net cash per trade with K=1, C=0.20 | **−0.38810777 account currency** |
| Original scenario total cash with K=1, C=0.20 | **−12,488.92 account currency** |
| Original source R9 average hold | **5.821 seconds** |
| Original scenario aggregation by source-native clock-hour | **All 23 active clock-hour categories negative** |
| Matched uncensored hypothetical first-goal versus original exit mean cash delta | **−0.000327 account currency per position**, observational only |

The original exit ledger has 31,498 stop-coded exits and 681 timeout-coded exits. Those include profitable trailing stops, so STOP is an *exit reason*, not a loss flag. The 94 target-first and 14 censored cases redistribute these original classifications.

## Proper interpretation

1. With ORIGINAL R9 exit timing and trailing stop, a 1.75 account-currency goal is seldom crossed before exit in this illustrative fixed-cost/contract scenario. This points toward an economic entry/hold/exit problem rather than an automatic high-AUC profitability benefit.
2. Historical original-R9 mean quote-price return is negative BEFORE extra fees. Any fixed positive K conversion and nonnegative fixed C preserve the sign of average return. This conditional mathematical statement is independent of the illustrative K=1 choice.
3. Shadow early-goal cash estimates are NOT realized strategy improvements. Closing at first goal would change R9 rearming, trade occupancy, later entries, portfolio gross loss and potentially fill prices. The current first-cause pilot does not reexecute those counterfactual portfolios.
4. This pilot replays original frozen R9 source-ordinal positions independently on original January ticks. It does not claim to have run the branch's new Python CLI end-to-end or the v1.94 MT5 EA with its account governor.
5. Jan–Sep were researched previously: no pristine unseen OOS claim.

## Research implementation and next gate

This branch already contains the Python-only source-exact original R9 streaming observer (cash_risk_overlay.py), cause-specific Aalen–Johansen estimator with right-censoring (competing_hazards.py), chronological train/test CLI (cli.py), and small synthetic parity/test fixtures. GitHub CI tests verify the original baseline execution path is not altered by shadow observation.

Next: run the unchanged Python observer for existing months, train the nonparametric cause-specific hazard by earlier periods, score later Coinexx periods and compare actual original baseline payoff by time-of-entry hour. Then implement a SEPARATE on-policy simulator of alternative entry/hold/exit decisions, including reentry and loss governor; no promotion to R9 EA before a whole-portfolio net-cash and throughput improvement is verified.

**No new tick archive, retrained 155-feature model, MT5 code, or high-volume duplicate data was generated.** Source archives remain intact.
