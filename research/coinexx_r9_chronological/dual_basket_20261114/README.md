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


## 2026-11-14 owner request: Train the **NEW entry** on January–September

**Training research source:** `train_jan_sep.py` (separate branch `carson/r9-v194-dual-entry-training-jan-sep-20261114`).

**Original source RECEIPT HAS BEEN FOUND:** primary Drive `gold_mt5_tick_all/R9_Path_Signatures_Derived_Cache_2026_Jan_Sep/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip`, file ID `1Kkdrh-IYrTmjNS2tpBgJDq9SKrfeFewa` (~41 MB), source receipts and original candidate closes. The original nine month Coinexx `XAUUSD_MT5_BROKER_2026_01..09_ticks_ALL.csv.gz` are present in the existing Drive parent. Neither needs to be reconstructed, published in GitHub, nor copied into a new Drive folder. Existing M60 first-passage/155/237-feature archives remain *original R9* features and DO NOT authorize new-dual-entry labels.

**Exact chronological method:**

1. **Pass 1 January–September:** Source SHA-256 + row counts + original R9 frozen entry/exit parity are verified for each month. On the **same original tick** the new dual-basket `$0.10` net cash-harvest arm executes independently. Only its **actual completed entry ordinals**, source-time snapshots and eventual actual modeled liquidation net become supervised examples. This is not a random sampling of windows, not old M60 labels, not a 5s faked-OHLC future.
2. **Fit January–June:** exactly 14 features recorded **before opening each position**: side, directional basket displacement for 5s and 15s, completed breakout excess for 15s and 30s, spread, lane agreement, basket clock offsets, completed M5 ATR, recent completed-quote midpoint range and directional impulse, and source-native daily sine/cosine. Causal first-quote and one-second-close policies remain intact. Purge entries within 120 seconds of July boundary. Reconstructible, fixed modest hist-gradient-boosting regression is trained on *clipped* after-cost account-cash trade labels; **raw loss tails** are retained for evaluation. No 155-model scores are imputed.
3. **July admission choice:** restrict to just four *predeclared training-score quantile* reject budgets: 0%, 1%, 3%, 5%. Require 95%+ offline retention and positive offline net before any model gate is selected. **Zero-rejection fallback** is preferred over a negative or unstable result. No broad parameter sweep.
4. **August no-retune veto:** if the chosen gate fails 95% retention or positive net in August, disable it. August doesn't set new thresholds.
5. **September frozen:** record the already-frozen January–June model's September diagnostics without changing weights or threshold. All nine months have been previously exposed to other project research, so *September is retrospective development evaluation*, **not pristine prospective OOS**.
6. **Pass 2 full chronological on-policy replay:** the frozen selector starts only in July; before July it acts as the **ungated new-entry control**. Rejection is evaluated at the precise time of candidate entry. It leaves the existing basket active; any subsequent position, stop, exit, rearm, loss, cash/hour or trade count is recomputed from source quotes, **not posthoc deleted from a trade ledger**. The runner separately assesses $0.10 immediate harvest and stop-protected $1.75 stretch. July/Aug/September comparisons include original v1.90 R9, new ungated basket, and gated new basket.
7. **Full January–September fit after the frozen September evaluation:** default writes a second small `*.jansep_INSAMPLE_ONLY.joblib`. This **is an in-sample model only**, not approved by the earlier September validation. The fixed Jan–June/frozen model is saved separately, with hashes, for audit. The all-month model needs genuinely unseen later dates before claiming future performance.

**Required original inputs** must already be accessible on a computation host, e.g. a local Windows research PC with existing synced files. In this chat, Drive metadata and GitHub source are accessible, **but the 72,129,347 raw Coinexx quote rows are not mounted to the execution runtime**. Do not state that real nine-month model training ran merely because the pipeline and its synthetic CI tests pass.

```bash
python research/coinexx_r9_chronological/dual_basket_20261114/train_jan_sep.py \
  --data /existing/path/to/original/coinexx/months \
  --receipt /existing/path/to/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip \
  --output /small/reports/R9_DUAL_JANSEP_TRAIN_REPORT.json
```

**No source archive download, source duplication, feature archive, per-day optimization result, MQL5 file edit, or production EA modification** is made by this script. It writes only one compact JSON report and two small fitted model files; it reads the nine pre-existing gzip files sequentially in two passes. Dependencies for actual training are Python 3.11, numpy, scikit-learn and joblib (installed on the computation host); GitHub Actions runs synthetic zero-data invariants only.

**Hard release gate:** exact nine-month parity plus positive after-cost cash/hour, 95%+ **actual on-policy** trade retention, gross realized loss, tail CVaR, simulated account peak/drawdown and post-September genuine forward validation under real Coinexx contract economics. Quote-only simulation lacks MT5 OnTick coalescing, slippage, server-side stop/freeze and deal-confirmation; see [MetaQuotes OnTick](https://www.mql5.com/en/docs/event_handlers/ontick). More model AUC alone cannot authorize live trading.
