# R9 v1.94 — owner-directed dual-basket entry and $0.10 / $1.75 cash exits

**2026-11-14 | Python research candidate only | NO production or live promotion.**

## Exact owner-approved change

- **Two parallel basket anchors:** first actually observed quote midpoint in each **5-second** and **15-second** wall-clock basket. Neither waits for a future candle close.
- **Two parallel causal breakout windows:** prior completed observed 1-second synchronized Bid/Ask CLOSE midpoints spanning **15 seconds** and **30 seconds**. The unfinished current second is excluded.
- **Four independent entry evidence lanes:** 5s/15s, 5s/30s, 15s/15s, 15s/30s. A BUY or SELL needs at least one complete lane (basket displacement plus breakout). Agreement from multiple lanes strengthens telemetry but never places multiple orders. Conflicting directions => **WAIT**. This OR design preserves high candidate throughput while avoiding an accidental 4-position multiplication. Its economics remain unvalidated.
- Pre-existing $0.10 **midquote price displacement** and $0.01 completed-close breakout buffer remain inherited from the previous experiment; these are NOT the $0.10 **net account-currency** cash objective.
- Retain existing causal S1 directional quality, completed M5 ATR/session/spread gate, R9 stop/trailing, 0.01-lot research comparator, account gross-loss safeguards, original **$2 intended per-position cash loss ceiling**, 10% peak-drawdown and 4%/12% daily gross-loss limits. An outer 25% capital emergency threshold does not relax any stricter limit.
- Maximum **four attempted successful entries per source-native minute**, or fewer if the inherited configuration permits fewer. Each 5s reset never resets this minute risk cap; opposite-side rearms are permitted only when the entry and exit remain in *both* the same 5s and 15s baskets.

## Owner cash-exit revision

- **Minimum target:** **+$0.10 modeled net account currency** per trade after quote-side spread and additional cost.
- **Preferred upper take-profit target:** **+$1.75 modeled net account currency**. Request a close at or above the observed executable mark. Realized cash can differ (or overshoot) due to delay or gaps.
- **Arm A: immediate minimum harvest.** First observable >=+$0.10 net requests a market close, preserving tighter protective stops. This can trade away potential larger wins.
- **Arm B: experimental protected stretch.** After the minimum is observed, only pursue $1.75 if an already-active stop protects the minimum or a *legal tighter* stop can first be installed. If neither is possible, request a minimum harvest. Never loosen original stops. This is a distinct research hypothesis, not a validated runner.
- Independent **original R9 30s stop/trail/exit** arm isolates entry changes from exit changes; the new experimental cash arms retain the separately reviewed 120s emergency quote-time backstop and the existing per-trade risk/timeout protections.
- **$0.10 is an objective, not a guaranteed positive floor.** Spreads, broker stops, losses and gaps can produce results below the requested cash target. K=1 and C=$0.20 are **illustrative**, not broker-verified `OrderCalcProfit` or fees.

## Preservation and deliberate limitations

1. Frozen compiled owner EA: original v1.94 MQ5 blob `07222b1a3800c9cc826abe10a4ce6afbd97b0af5`; original v1.90 rollback blob `7eecb5f1947017a01ce85b2520725de54749e523`. **Neither file was edited.**
2. Existing `quarter_basket_20261114` experiment and the January negative results stay immutable. That result found the 15s basket/30s breakout with original exit less negative than original R9, **not profitable**.
3. Source-only implementation: `dual_basket.py`; tests: `test_dual_basket.py`; one-pass runner: `run_dual_basket.py`. No alternate raw-tick engine, new tick cache, rebuilt month exports, or large artifacts.
4. All four entry lanes use **only original source-ordered Bid/Ask quote events** and the original completed-second builder. No future bars, market order volume, Level 2, VWAP or fabricated 155-feature score is used.
5. The original 155-feature model's candidate times do not transfer automatically to these NEW entry timestamps. No live-trained feature source or valid runner utility has been established for these trades.
6. This code is not an MQL5 EA; MetaEditor compile, account-currency K/fees validation, broker stops/freeze execution, terminal OnTick parity, time-offset checks and genuinely new future-period results are outstanding.

## Reuse original data (no duplication)

For a full *existing-source* month, after the original pinned receipt has been located:

```bash
python research/coinexx_r9_chronological/dual_basket_20261114/run_dual_basket.py \
  --data /path/to/existing/monthly/gzip \
  --receipt /path/to/existing/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip \
  --months 01 \
  --output /path/to/small/scorecard.json
```

The runner checks each original gzip SHA256 and **every original completed trade** against the frozen archive when evaluating a complete month; it streams input ONCE, sharing the source's causal market context across all strategy arms. `--governor` introduces a quote-only one-account governor comparator, **not** certified v1.94 MT5/account parity. Partial `--max-rows` samples are explicitly non-acceptance tests.

Before any EA integration, require positive net after-cost cash per active hour, sufficient trade retention, no worse total gross loss/drawdown/CVaR, feasible stops and model/source parity. January–September 2026 are research-exposed and are not pristine out-of-sample validation.

**Release rule:** test the entry-only arm first; do not re-engineer either Coinexx or Dukascopy datasets. No MQL5 trading changes before full same-baseline risk/performance certification.
