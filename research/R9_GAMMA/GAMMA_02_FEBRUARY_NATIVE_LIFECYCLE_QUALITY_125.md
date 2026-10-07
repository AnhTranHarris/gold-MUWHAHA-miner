# GAMMA-02 — February Native Lifecycle Quality 125

**Status:** MAJOR FEBRUARY DISCOVERY FRONTIER — COMPLETE  
**Parent:** GAMMA_02_FEBRUARY_NATIVE_STATE_DISCOVERY_124.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Breakthrough

The February-native state portfolio was refined with source-specific executable TP/SL/maximum-hold geometry.

Every cell was evaluated with first-passage TP/SL timing on ordered Bid/Ask ticks. The search grid was:
- TP: none / $2 / $4 / $6 / $8 / $12 / $20 / $40 / $80
- SL: none / same levels
- hold: 15 / 30 / 60 / 120 / 300 / 600 seconds

All 13 cells completed before the UI timeout.

### Integrated one-ledger results

| Mode | Net | Trades | PF | Win | Expectancy | Max open |
|---|---:|---:|---:|---:|---:|---:|
| Max-net | **+$71,149.91** | 12,543 | 3.143 | 65.69% | **+$5.672** | 342 |
| Quality | **+$67,260.48** | 11,421 | **3.372** | 67.96% | **+$5.889** | 342 |
| Strict quality | **+$59,294.35** | 9,985 | **3.672** | **69.69%** | **+$5.938** | 342 |

At cap 128:
- max-net: +$46,726.20 / 10,654 / PF 2.585
- quality: +$46,304.68 / 9,880 / PF 2.752
- strict-quality: +$40,071.12 / 8,568 / PF 2.954

The prior fixed-horizon February-native parent was +$40,163.27 / 12,543 / PF 2.30.

## Important cell-level discoveries

- 15 UTC H4/H1 short, M15 long, M5 short: TP $40 / no normal SL / 600s -> **+$12,639.84 / 706 / PF 12.80 / 82.6% wins**.
- 13 UTC H4/H1 short, M15/M5 long: TP $40 / SL $20 / 600s -> **+$13,137.49 / 1,062 / PF 3.08**.
- 14 UTC same pullback family: quality route TP $20 / 600s -> **+$8,827.56 / PF 2.50**.
- 17 UTC short reclaim: TP $40 / 600s -> **PF 6.39**.
- 17 UTC long reclaim: TP $8 / 600s -> **PF 64.95 / 93.0% wins**.

## Interpretation

February is not a failed January transfer. It contains a different medium-duration continuation architecture.

The correct repair was:
1. remove warmup leakage;
2. discover February-native legal state cells;
3. assign lifecycle by state rather than inheriting January's fast-quantum geometry.

This moves February from the clean inherited-family ceiling of roughly +$8-9K to **+$59K-$71K discovery economics**, depending on quality target.

The remaining gap to R9-SYNTH is now mostly PF/win-rate and chronological density/heat efficiency, not monthly dollar capture.

## Exact helper authority

- lifecycle search helper SHA-256: `bd54fa83575ebd0727f21cafbecbc784a533c4a67228b525149f98acc7ef8a00`
- lifecycle portfolio helper SHA-256: `d492df90dc87f1c8bc8237ebe86a278542dbefcc8623fc95dba9d8c7e22a6402`
- full lifecycle result SHA-256: `7354d14ac5087df911747fa8a9bc00514cf4bdcc9f771a8658efc66f4bf82963`
- full portfolio result SHA-256: `22ff23027b0e1a3392c251aef6b7c2bfd3623438c292482a48602beb5c8b56a8`

GitHub helpers:
- `research/R9_GAMMA/helpers/gamma02_feb_lifecycle_quality_125.py`
- `research/R9_GAMMA/helpers/gamma02_feb_lifecycle_portfolio_125.py`

## Next

`GAMMA_02_FEBRUARY_NATIVE_CONVICTION_ROUTING_126`

Use causal displacement/subphase/state-age features to raise PF/win rate while preserving the new February profit frontier. Then backcast unchanged rules to January and forward-test March before any deployable meta-router promotion.
