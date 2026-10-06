# Delta-A-alpha Source Registry

## Parent scientific state

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Parent branch: `delta`
- Parent commit: `ac91fc43389a34f8ba380b58143f8e185589b106`
- Parent mode: **READ ONLY**
- Canonical Stage-A January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Default research surface: `DUKAS_COINEXX_LIKE_P75`
- August 2026: **SEALED**

## GRID-001 exact creator authority

Video:
`https://www.youtube.com/watch?v=4WQEoQxsJMc`

Exact tutorial-code repository:
`MegaJoctan/omegafx-youtube-shared-files`

Inspected commit:
`fc232fb4ffa9ed854d8c398e6e7a6de28c5dc51f`

Authoritative tutorial files:
- `Python Grid Bot/grid_bot.py` — blob `1d5efa140b363941e7360bd0ae85ac7e04d0ecaa`
- `Python Grid Bot/grid_bot_backtest.py` — blob `3d4f66a2e57397c15876df795a629488b6278a7c`
- `Python Grid Bot/grid_bot_optimization.py` — blob `fd69caaa878643fcbe26070ae120e213d67b44ff`

Framework/API repository:
`MegaJoctan/StrategyTester5`

Inspected framework commit:
`45e2a23d11716f204cf66f9695124980aceae1bc`

The user-supplied transcript remains explanatory evidence; exact shared-files source governs the tutorial implementation when they differ.

Confirmed source mechanics:
- H1 timeframe;
- default 48-bar rolling high/low;
- fixed grid-gap parameter;
- current Ask used for both signal comparisons;
- BUY fills at Ask, SELL fills at Bid;
- latest still-open same-side entry becomes the next anchor;
- one-grid-gap TP;
- no intrinsic stop in live source;
- backtest adds maximum positions per direction;
- backtest/optimization introduces loss-dependent lot multiplication;
- optimizer searches gap/window/max orders for net profit;
- source tester uses 1-minute-OHLC modelling.

Delta-A-alpha rejects:
- loss-dependent sizing;
- Martingale;
- no-stop promotion;
- optimistic OHLC path inference.

No LICENSE was found in the inspected shared-files repository. Use for inspection and clean-room reconstruction, not substantial source copying.

## Canonical R9 benchmark

SYNTH MT5 report:
- file: `ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx`
- SHA-256: `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`

REAL MT5 report:
- file: `ReportTester-871471_jan2026_jul2026_R9_ticklog_real(4).xlsx`
- SHA-256: `19d5ffd785beaae2a9d0baa5efb50efcd36a7db635c7ef82957be442429c1064`

Canonical ledger:
`research/delta_a_alpha/benchmarks/R9_REAL_SYNTH_JAN_JUL_2026.json`

Extractor:
`research/delta_a_alpha/helpers/mt5_report_benchmark_extract.py`

The uploaded (3)/(4) report copies were byte-identical.

## Whole-system public GitHub mechanism sources

### bnzr-team/grinder

Inspected commit:
`f216435c9549795edd12886d755f114b42b819fc`

Verified mechanisms:
- volatility/NATR-driven step;
- min/max clamps;
- step hysteresis and cooldown;
- regime-specific grid semantics;
- finite width/level clamps;
- asymmetric trend geometry;
- toxicity/thin-book/pause/reduce-only states;
- drawdown-budget hooks;
- deterministic replay architecture.

Relevant blobs:
- `src/grinder/policies/grid/adaptive.py` — `c8eaa94d0fe1aa51c104530e449b1657fc153765`
- `src/grinder/risk/adaptive_step.py` — `a4cd0f90de9ba5e6483a6c46b455fa02059c03c7`

No top-level license found at inspected commit. Clean-room concepts only.

### aycfundteam/ayc-bybit-competition-2026

Relevant blob:
`strategy/atr_grid_strategy.py` — `df5d865c2b756512d108acaab0f91d757f11832a`

Verified architecture:
- ATR-adaptive spacing;
- EMA trend context;
- ADX + ATR-ratio regime classification;
- stable/volatile trend and quiet/choppy sideways states;
- persistent grid state;
- maximum levels.

Production thresholds are intentionally hidden. Only disclosed architecture/formulas are eligible.

### vuyelwadr/pulsechainTraderUniversal

Inspected commit:
`a5383c6bb396ef30bf707cb67228b5118c68f3a1`

Verified mechanisms:
- ATR/volatility adaptive spacing and range;
- trend-aware asymmetric spacing;
- higher-timeframe regime anchor;
- recentering on meaningful drift;
- post-fill cooldown;
- finite active levels;
- fee/edge admission.

Relevant blob:
`strategies/grid_trading_strategy_v2.py` — `c1e81e48376928cac414f57795784e3104f470e6`

License not established in this audit. Clean-room concepts only.

### joshyattridge/smart-money-concepts

Inspected commit:
`1b62fd6c41e1f508e7ed76831a039fa4c82d42f6`

Relevant implementation:
`smartmoneyconcepts/smc.py` — blob `110759cc8e063773f4905d437f15932534e7f3b4`

License: MIT.

Potential structure primitives:
- swing highs/lows;
- BOS/CHoCH;
- liquidity levels/sweeps;
- previous highs/lows;
- sessions;
- retracement.

**Causality warning:** some public implementations use future-looking bars (for example future shifts or symmetric before/after swing windows). Delta-A-alpha must reconstruct these as delayed-confirmed/right-edge causal primitives before testing. Public labels are not execution-ready semantics.

### gammarinaldi/mql5

Relevant source:
`Grid_BB_RSI_News_EA/Grid_BB_RSI_News_EA.mq5` — blob `5f62fea67401bfb7f5f4471614b6c01494adfb95`

Useful concepts:
- trading-hour state;
- news-before/after windows;
- ATR distance option;
- maximum grid levels;
- drawdown circuit behavior.

The repository also contains Martingale-style multiplication. That component is prohibited.

### thales1020/QuantumTrader-MT5

Relevant example:
`docs/examples/news_filter.py` — blob `2031825c4e50deaaf7accaed562665953254ce27`

Useful only as an educational event-window/symbol-affect mapping example. It contains placeholder external-calendar integration and is not production authority.

### BlamzKunG/CFD-Trading-ML

Relevant XAUUSD experiment:
`projects/xauusd_trading_policy/scripts/run_exp75_cross_regime_adaptive_confluence.py` — blob `ff93f156cf60b6a1872ffb3196f3ec415f61d947`

Potential deterministic concepts:
- London/NY/transition session masks;
- volatility-conditioned horizons;
- multi-bar flow persistence;
- session-dependent action strictness.

Not eligible:
- opaque pretrained-model outputs;
- variable risk sizing;
- unverifiable ML authority.

## Research-source acceptance rules

A community mechanism may enter the testing queue only if:
1. logic is reconstructible;
2. causal timing can be specified;
3. execution semantics can be reproduced on ordered Bid/Ask ticks;
4. it does not require prohibited sizing;
5. licensing/provenance is recorded;
6. it addresses a defined whole-system role rather than becoming another stacked confirmation vote.

Public code is evidence of an implementable mechanism, not evidence of profitability.

## Active source-hunt artifact

Whole-system mechanism map:
`research/delta_a_alpha/research/DAA_GRID_COMMUNITY_SOURCE_HUNT_002_SYSTEM_LAYERS.md`

## Cleanup boundary

Out-of-order January-specific refinements were removed from active Delta-A-alpha at cleanup commit:
`1aa16d0f906e78b2757293a1e49cb3c3c6caa7e4`

Recovery-only branches:
- `delta-A-alpha-pre-system-cleanup-20261006`
- `delta-A-alpha-pre-system-cleanup-20261006-v2`

Those branches are forensic references only. A prior mechanism must be independently re-earned after its required whole-system parent layers exist.
