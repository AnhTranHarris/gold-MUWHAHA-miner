# Gold MUWHAHAHA Miner — Winner-first micro180 trade forensics

**Source:** Original SHA-pinned Coinexx Jan–Sep 2026, **existing** V12 exact-ordinal derived trade ledgers, with V13's separately computed causal quote-time price-location summary. No Coinexx tick files were modified, recompressed, reconstructed, or reexported. No MT5 order code or EA settings were changed.

## Primary object of study: the *128,203 profitable trades*

From 338,064 original completed V9/V12 simulated trade lifecycles, exactly **128,203** finished with positive modeled net under the original research assumption (one cash unit per $1/oz price change and $0.20 additional round-trip cost, with executable Bid/Ask entry/exit). **These winners contributed +$30,101.43 in positive modeled outcomes.** This is *positive trade-cohort proceeds*, **not** a profitable complete strategy or a broker-confirmed return. The goal is to reconstruct the causal mechanism of these winning events without selecting future outcomes at entry time.

- **127,247 cash-harvest winners (99.25% of winners)**, averaging **+$0.22968** modeled cash per winner.
- **313 preferred-cash-cap winners**, averaging **+$2.62160**.
- **451 positive timeouts** and **192 positive stale-quote exits**; neither is a proposed new entry mechanism.
- Mean winner **+$0.23480**; median winner approximately **+$0.17**; 90th-percentile winner approximately **+$0.43**. These figures quantify what the frozen simulator *did* win, not what a new lattice can guarantee.

### The two historical profitable lifecycles

| Source-exact actual-hold property | Clean impulse winners | Recovery winners |
|---|---:|---:|
| Profitable trades | **83,120** | **45,083** |
| Share of all winners | **64.83%** | **35.17%** |
| Definition | Never reached a 10-cent adverse drift from entry liquidation quote before original exit | Did touch or cross that adverse 10-cent threshold, then finished positive |
| Median original hold | **2,503 ms** | **7,015 ms** |
| Median time to 10-cent favorable drift | **524 ms** | **1,846 ms** |
| First +10c favorable within 1 second | **68.04%** | **32.66%** |
| First original-ordinal +50c favorable move before original exit | 78,231 | 42,442 |
| Median time to first observed +50c move (those reaching it) | **2,474 ms** | **6,867 ms** |
| Average original modeled net per winning trade | **+$0.23897** | **+$0.22709** |

**Especially important:** among the 45,083 winners that recovered from a 10-cent adverse move, **31,116 experienced their adverse 10-cent move *before* their first favorable 10-cent move**, in exact quote ordinal order; another **13,967 had favorable 10 cents first, then drew down and recovered**. A generic 'exit the moment price goes 10 cents against entry' rule would destroy observed successful recovery trades. The real research task is to detect a *failed* recovery quickly **without widening an existing protective stop**.

The profitable lifecycle classes above are **known only after a trade has developed**. A model cannot use them as entry-time filters. This audit explicitly separates as-of-entry variables from later path labels in the accompanying CSV.

### Monthly winning trades, not a negative-strategy league table

| 2026 | Positive completed trades | Clean impulse winners | Recovery winners | Positive cohort proceeds (modeled) |
|---|---:|---:|---:|---:|
| Jan | 13,374 | 8,841 | 4,533 | +$2,965.55 |
| Feb | 17,616 | 12,591 | 5,025 | +$5,711.16 |
| Mar | 21,742 | 15,534 | 6,208 | +$6,060.40 |
| Apr | 14,134 | 8,958 | 5,176 | +$3,142.75 |
| May | 10,912 | 6,383 | 4,529 | +$2,252.19 |
| Jun | 13,744 | 8,425 | 5,319 | +$2,803.24 |
| Jul | 12,301 | 7,517 | 4,784 | +$2,357.25 |
| Aug | 11,965 | 7,348 | 4,617 | +$2,389.15 |
| Sep | 12,415 | 7,523 | 4,892 | +$2,419.74 |
| **Total** | **128,203** | **83,120** | **45,083** | **+$30,101.43** |

**Regime implication:** the recovery share of monthly winners changes across the year. For example, it is 28.5% in February and 41.5% in May. The choice of clean-continuation versus recovery specialist should therefore depend on *as-of-time observed market regime*, not on a fixed universal hold time selected from hindsight.

## What was observable BEFORE profitable trades?

These are **as-of-entry causal descriptors**, not future labels. Compared against all corresponding original entries:

- **Directional 1-second midquote movement ≥50 cents before entry:** 21,505 winners among 53,541 entries, **40.16% conditional win rate**. The whole-population original V9 baseline is 37.92%.
- **Entry spread ≤19 cents:** 44,248 winners among 113,026 entries, **39.15% conditional win rate**. This absolute spread criterion was heavily concentrated in Jan–Apr and is therefore **not a fixed setting to deploy**; the proposed lattice must use local session-relative spread and explicit executable cost.
- **Both conditions:** 7,625 winners among 18,258 entries, **41.76% conditional win rate**; on later Jul–Sep data, 350 winners among 847 entries, **41.32%**. This is promising as a *feature combination to explain*, but the sample's absolute-spread distribution shifts substantially between months, and these are original V9 trades rather than a new on-policy policy.
- Pre-entry old V9 EMA directional bias and breakout quant score do **not** sharply separate clean winners from recovery winners: both winning classes have approximately 20-cent mean spread, five prior-second quotes median, and 16–17 cents median signed preceding 1-second movement. **We need differentiated structural-location and micro-path context, not more indicator votes.**

Using the already completed V13 causal geometry map (not rerunning 72 million ticks):

- **8,808 winners / 20,915 entries (42.11%)** occurred at **≥$1.50/oz *against* the entry direction relative to the preceding 180-second quote-duration-weighted midprice**. This is a distinct *discounted price location* cohort worthy of reverse engineering; it is not actual traded-volume VWAP and does not establish fillable limit orders.
- **65,935 winners** occurred near the last 20% of the directional 180-second price range, but the total population in that position was 176,963 entries, giving only **37.26%** conditional winners. Raw winner *counts* there are largely explained by the overwhelming number of V9 breakout entries there. Do not use this concentration as proof that breakout chasing is superior.
- Near the earliest 20% of the directional range, **3,426 / 8,545 (40.09%)** were positive; fewer winner events but modestly higher conditional winning rate. Any Fib/anchor rail must be tested against **all eligible opportunities**, not merely those that ultimately won.

## A timed observation that can be used prospectively, after a trade enters

Among V9 positions still alive at the stated landmark (never retconning an entry decision):

| Original-price-path state observed by landmark | Trade age | Survivor cohort | Ultimately positive under original V9 |
|---|---:|---:|---:|
| +10c favorable, *no* −10c adverse yet | **250 ms** | 44,075 | **24,972 (56.66%)** |
| −10c adverse, *no* +10c favorable yet | 250 ms | 32,821 | 7,698 (23.45%) |
| +10c favorable, no adverse | **1,000 ms** | 79,763 | **43,347 (54.34%)** |
| −10c adverse, no favorable | 1,000 ms | 63,180 | 15,648 (24.77%) |

This is the strongest *positive-path timing distinction* found by the current source-exact analysis. Note that the 250ms and 1s survivors are different selected cohorts: these are descriptive **landmark associations, not counterfactual profits from an exit rule**. Many winners also recover after adverse-first behavior, so one state cannot replace the other. The observer must use original quote ordinal, not an OHLC bar, and must abstain when quotes are missing or spread spikes.

## Profit-first redesign: two causal lattice specialists, not an expanding grid

**Specialist C — clean impulse continuation.** Freeze M15/H1 regime and a confirmed M5 Fib rail / quote-duration anchor using only completed evidence. Seek cost-covered executable price location and observed 250ms entry-side reclaim. Test quote-side directional +10c continuation and adverse-risk *before* submitting a hypothetical market-side entry on the **next observed quote**. The historical clean-winner median 524ms to +10c and ~2.47s to first +50c are diagnostic priors, **not validated optimal entry-delay or target settings**.

**Specialist R — sweep, reject, recover.** Detect a causal sweep of a confirmed support/resistance/Fib/anchor zone; require an observed quote-side reclaim **before** taking a new position, rather than buying additional lots while price falls. The 31,116 historical adverse-first eventual winners motivate studying this specialist, but their recovery occurred *after* a different original entry and cannot be assumed repeatable from a shifted entry. Use frozen zone invalidation strictly on the correct side; no martingale, averaging down, or protective-stop widening. A longer but bounded management window is a *research variable* because historical recovery winners held a median of ~7.02s.

**Unified exit controller.** Keep unchanged broker protective stops. In shadow research, distinguish (a) adverse quote state with no confirmed reclaim; (b) favorable quote state whose prospective next rail has enough room **after spread+fee+slippage reserve**; (c) a confirmed sweep/reclaim. Record first available quote-side executable exit and original-order source ordinal. Do not mark a post-exit hypothetical quote as achieved cash. The objective is to improve both *net gain per win* and *size/timing of actual adverse exits*, since high winner counts alone do not guarantee net expectancy.

**First focused falsification:** no more than two mechanisms (C and R), with one existing equal-spaced anchor-grid control. Build a new on-policy Python simulation that creates fresh candidate signals and re-arms independently; choose fixed settings from early development chronology, freeze them, check later periods without retuning. Measure all trades, positive completed share, net after Bid/Ask and stress costs, cash capture, occupancy, tail drawdown and monthly consistency. January–September remains historically reused development data, **not untouched OOS**. Only a successful complete on-policy study should inform MT5 parameter settings.

## Preservation and reproducibility

- Winner-only derived ledger: `V14_128203_POSITIVE_MICRO180_TRADES_only.csv.gz`. It contains **128,203 original winning trade rows** with exact entry/exit ordinals, quote-side prices, as-of-entry evidence, and clearly labelled after-entry path annotations. It contains **no original tick stream**.
- Audit computation script: `reverse_engineer_positive_trades.py`, which reads nine existing V12 derived ledgers, independently reconciles original entry/exit and winner/cash totals, and produces the winner-only ledger and statistical JSON.
- Full machine-readable statistics: `V14_WINNER_FIRST_NINE_MONTH_ANALYSIS.json` with monthly cohorts, entry descriptors, temporal split probe and 250ms/1s landmark evidence, plus source-file hashes.
- No MT5 EA edited, no new live/demo order path, no quote archive duplicated. No claim that a majority-winning *system* is already proven; the evidence above describes **why historical winning trades won** and **where new specialists must acquire causal evidence**.