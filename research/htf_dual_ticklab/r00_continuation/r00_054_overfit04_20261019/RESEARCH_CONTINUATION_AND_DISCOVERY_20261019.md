# R00-054 OVERFIT04 — verified entry failure atlas (2026-10-19)

**Research-only continuation** from `carson/htf-r00-054-overfit03-failure-discovery-20261019`, parent HEAD `514d16ee60594b54b1634450ffc69544c742283b`. Original Jan-trained `lgb_oracle_weighted` R00-054 BUY/SELL decisions, timestamp generation, cached raw-source clocks and 30–32-second direction targets remain unchanged. NO held positions, exits, funded trades, P&L, or live MT5 EA deployment. No filter promoted.

## Accepted frozen baseline
Approved original source months: January, February, June, July 2026 only; both Coinexx and Dukascopy tick-level original separate replay environments, independent broker/months. Original model control JuneJuly: **1,231,388 signals, 548,099 correct, 530,177 opposite, 153,112 neutral/missing**; 44.5107% correct. Archived upstream stages are FILTER01/FAILURE02/OVERFIT03 — do not rerun/rebuild.

## Exact executed OVERFIT04 findings
Predeclared failure atlas: 15 causal masks across all eight broker-months. Activity/efficiency/spread thresholds derived from JAN broker-specific quantiles only; no JuneJuly-dependent mask calibration. Each original event timestamp, +30s target, original side and correctness label were checked against the original immutable event ledger. Resulting detailed evidence uploaded to MT5_EXPAND:
- [Source-month error atlas](https://drive.google.com/file/d/1yS5DF28wFSTDJ4zrbuCaPZAWh2S3RW6H/view) — **uploaded**, 16 conditions including control × eight broker-months.
- [Exact fitted-row 90% diagnostic](https://drive.google.com/file/d/1xeqDyDv7oz7gffOusNMp7ppHIJIZlDXl/view) — **uploaded**, independently recomputed original overfit model's fitted rows only.

**Deliberate OVERFIT03 training-sample positive filtering** (threshold P(correct)>=0.5): Original fitted rows from combined JuneJuly broker evaluations = **175,913** (one-seventh event subset). Retained **77,662**, of which **77,634 correct** and **28 incorrect**, ***99.9639% fitted-sample directional precision*** and ***99.3080% correct preservation among fitted rows***. This is memorization, never claim real filter or generalization. Only one-seventh of original stream: 77,634 correct supply falls below JuneJuly 90%-of-R9 aggregate reference of ~102,741 correct across both independently benchmarked brokers. It cannot meet R9 hourly/daily floors at that scope. Prior overfit03 February backward AUC 0.5062 Coinexx, 0.5049 Dukascopy, cross-broker JunJul AUC ~0.527–0.536; failed transfer.

**90% precision mathematics**: With exactly 95% of baseline good retained, 520,695 correct can be kept, 57,855 wrong permitted, requiring **625,434 / 683,289 = 91.53% wrong rejection**. With 100% of correct retained, need >=622,390 wrong rejected. Even a perfect *neutral-only* detector tops out at **50.831%** accuracy; even a perfect *opposite-only* detector tops out at **78.165%**. Therefore BOTH independent error classes require discovery, with joint mechanism/arbiter while preserving hourly correctly directed supply.

**Observed Feb/Jun/Jul (6 broker-months)**:
- High 10s quote-update rate (JAN q75 threshold): 435,366 signals, 211,112 correct = **48.49%**, neutral **5.28%**; lift in all six source months.
- Low quote rate (JAN q25): 513,735 signals, 207,902 correct = **40.47%**, neutral **20.33%**; worse in all six months.
- UTC 12–17 overlap: 425,603 signals, 200,269 correct = **47.06%**, positive deviation in all six.
- UTC 21–00 rollover: 147,691, 60,911 correct = **41.24%**, neutral **19.09%**; weaker in all six.
- Short adverse impulse with HTF body opposition unexpectedly showed **46.33%** correct in 178,230 source events, positive baseline deviation in all six. Do not veto mere countertrending structure.

These are highly overlapping original 5-second source events and **descriptive conditional associations only**. Quote updates are NOT traded volume/order flow.

## Full portable deliverable identity
`R00_054_OVERFIT04_EXECUTED_ATLAS_AND_OVERFIT90_DIAGNOSTICS_20261019.zip`, **7,164,635 bytes**, SHA-256 **`484b1134d6ae6c26dc8ebc162f61f2136710db5996bc65febba406ed040300fa`**, ZIP CRC PASS. Contains executable original Atlas04 Python helper, frozen plan, CSVs, exact trained-row replay output, complete receipts, next experiment design, member SHA256, and COMPLETE upstream FILTER01, FAILURE02 and OVERFIT03 original research ZIPs. Package available from the present ChatGPT conversation; **no binary ZIP copy verified on Google Drive yet**. The two research result CSVs have verified Drive IDs above. **Do not infer from these links that large archive has been uploaded.**

## Proposed new causal multi-facade discovery (NOT EXECUTED)
Predeclared `R00_054_FILTER05`: five independently resetting `ARM→CONFIRM→VETO/RELEASE→EXPIRE→COOLDOWN→REARM` specialists:
1. Actual ordered bid-only/ask-only/joint quote updates over last 16/32/64/128/256 observed quote events; stale-side age, persistence, spread elasticity (quote updates not centralized volume).
2. **Publication-safe** completed M1/M5/M15/H1 pivots and swing/sweep/reclaim/retest/failed-break/CHOCH phase; no repaint from unfinished bars.
3. Neutral/no-opportunity 30s quote-move hazard separately.
4. Opposite-side error hazard separate from neutral; discriminate real continuation vs momentary counter-move.
5. Session/regime broker-specific maturation specialist; previous signal labels only available after +32s, even for shadow-rejected candidates.

Cooperate via two-stage veto, measure every rejected **good** vs rejected **wrong**, and contribution of each specialist across UTC hour/day/week/month vs R9 original 90% correctly directed supply floors. Protection target >=95% good retained **per broker-month**, eventual >=90% precision without losing R9 throughput and >=25% relative uplift as ambition, NOT as achieved claim. JAN nested purged cross-fit meta labels; FEB select and freeze; exposed JUN/JUL historical transfer; **new truly blind month requires separate explicit source authorization**. Do not reoptimize on historical June/July.

## External reasoning clue provenance (NOT evidence of XAUUSD edge)
[Official MQL5 CopyTicks](https://www.mql5.com/en/docs/series/copyticks) · [MQL5 meta-labeling](https://www.mql5.com/en/articles/22274) · [MQL5 regime classification](https://www.mql5.com/en/articles/22940) · [TradingView repaint rules](https://www.tradingview.com/pine-script-docs/concepts/repainting/) · [ForexFactory gold HTF→LTF phase](https://www.forexfactory.com/thread/1397686-xauusd-timing-model) · [Reddit meta-label debate](https://www.reddit.com/r/algotrading/comments/1lnm48w/meta_labeling_for_algorithmic_trading_how_to/) · [Myfxbook dynamic XAUUSD sentiment](https://www.myfxbook.com/community/outlook/XAUUSD) is NOT a historical feature source.

All cumulative R00 governance laws, investor objective and the original four R9 reports remain binding in FULL original form; this receipt is a locator, not a replacement.
