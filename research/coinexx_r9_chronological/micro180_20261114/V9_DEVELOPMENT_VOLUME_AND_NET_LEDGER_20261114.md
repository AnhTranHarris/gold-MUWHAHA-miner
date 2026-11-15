# Gold MUWHAHAHA Miner R9 Micro180 V9 — volume-retention / executable-price checkpoint

**Date:** 2026-11-14. **Status:** Research-only, economically negative, NOT MT5-compiled, no deployment authorization.

## Preserve existing work / rollback

- Branch source: `carson/r9-micro180-v8-measurement-parity-repair-20261114` (full exact V8 Python/MQL5 code and V8 negative-experiment ledger). New V9 research branch: `carson/r9-micro180-v9-volume-executable-or-20261114`.
- Never mutate production `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5` (historical blob `07222b1a3800c9cc826abe10a4ce6afbd97b0af5`), V8 MQL5, baseline files, original monthly Coinexx gz or Dukascopy, old high-AUC 155-feature model.
- Previous complete Jan–Sep 2026 comparisons: original R9 **303,934 trades / -$120,212.46** net; original 5/15×15/30 OR **419,389 / -$162,656.05**; selective Micro180 **61,258 / -$24,158.30**. All after illustrative extra $0.20/round trip and historical quote Bid/Ask spread, 0.01 lot assumed cash unit K=$1/XAUUSD $1.
- Prior V3 inverted SELL teacher; V4 direction-before-eligibility and feature collision; V5 250ms experiments and stop-high-watermark defect; V6 unconditional first-passage prior; V7 setup-conditioned cash kernel and held/harvest tests; V8 source-age and same-ms state repairs: inspected and not restarted. See original V7/V8 ledgers. These past attempts did not establish profitable high turnover.

## V9 experimental implementation (Python, non-production)

File `v9_volume_router.py` reuses existing R9 `DualBasketMixin`, `Micro180R9`, `RollingThreeMinute`, M1 Wilder/EMA/ATR, 250ms `MsQuarterPath`, on-policy cash and governor; no new market data format or data cache. `run_v9_volume.py` reads the original `.csv.gz` directly and can verify exact monthly compressed SHA before scanning a bounded prefix. `test_v9_volume_router.py` contains eight new deterministic contracts. Existing V8 suite remains unchanged.

1. **Four lane opportunity router:** independent elapsed-time-matured 5s and 15s source-quote candles, each allowed to authorize a 15s or 30s breakout, OR rather than all four or both horizons being required. Preserve one open position, four fills per source minute, 1.5s first-after-exit minimum plus new 5s OR new 15s basket. No artificial candle in empty seconds, no same-millisecond burst masquerading as a mature basket.
2. **Executable-side trigger:** BUY requires actual current **Bid** above prior completed Bid-second close maximum; SELL requires actual current **Ask** below prior completed Ask-second close minimum, with the existing 0.01 XAU price buffer and 0.10 price displacement (NOT $0.10 NET cash). Independent BUY/SELL evaluation and conflict refusal. Existing source-order S1 quality and R9 regime/session gate retained.
3. **Asymmetric causal quant diagnostic, SHADOW by default:** separate BUY/SELL weighted dimensions of 5s/15s/30s executable-direction efficiency, signed breakout normalized by past completed-second realized RMS, source-ordered actual 250ms path coherence/efficiency, past spread shock, completed M1 Wilder +DI/-DI and EMA slope. Quote-activity only, no trade print volume/DOM or seller/buyer aggressor. Scores are unfitted research indices, not probabilities, not profit predictions. No new hard indicator veto because past V7 positive-cash veto destroyed trade count without distinguishing profit.
4. **Cash holding/exits:** current inherited V8 default first observed **+$0.10 NET** request to close, preferred **+$1.75** cap, 30s maximum, original protective stop and first observed **-$2** loss emergency; optional shorter 250ms adverse path is OFF because it worsened September's controlled trial. No repeated commissions or unprotected speculative runner. Gains are computed BUY Ask-in/Bid-out, SELL Bid-in/Ask-out, with extra modeled $0.20 beyond observed spread.
5. **Governors:** frozen existing stricter 10% peak/equity, 4–12% daily gross budget and additional 25% start capital catastrophe threshold remain available; pilot economic comparison intentionally uses `governor=False` so not a live-account capacity report. Broker slippage and quote gaps can exceed intended $2 stop, observed below.

## Evidence: original nine 200,000-row prefixes, not nine complete months

All nine original monthly compressed files read **read-only**, SHA256 confirmed against frozen source receipt, each original first 200,000 source ordinals (1.8 million quotes total). Sample windows are *different chronological durations* per month and already exposed research IS. Original R9 and V9 processed identical quote sequences; `ResearchCash` K=1/C=0.20, original Bid/Ask, no slippage or MT5 fills, governor OFF. No source copies, tick cache, model training, or inferred traded volume.

| Month | Original R9 completed trades | Original R9 NET | V9 completed trades | V9 NET | V9 first-available loss ≤ -$2 |
|---|---:|---:|---:|---:|---:|
| Jan | 938 | -$343.74 | 905 | -$335.31 | 0 |
| Feb | 360 | -$131.64 | 466 | -$183.20 | 7 |
| Mar | 823 | -$336.62 | 1,047 | -$452.18 | 2 |
| Apr | 941 | -$351.92 | 1,186 | -$441.46 | 3 |
| May | 970 | -$397.96 | 988 | -$392.89 | 0 |
| Jun | 736 | -$331.02 | 713 | -$328.65 | 0 |
| Jul | 918 | -$354.16 | 963 | -$388.91 | 0 |
| Aug | 872 | -$356.11 | 870 | -$357.81 | 0 |
| Sep | 835 | -$343.98 | 900 | -$368.52 | 0 |
| **TOTAL** | **7,393** | **-$2,947.15** | **8,038** | **-$3,248.93** | **12** |

V9 produces **645 more completed trades (+8.72%)** than original R9 in these nine *limited prefixes*, but net is **$301.78 worse**, 0/9 positive month prefixes. Not a profit breakthrough, not valid to extrapolate trade count to a full 72,129,347-quote/9-month result. Of the 8,038 trades, **12 first-available quote exits have realized modeled cash losses ≤ -$2**: strict $2 cannot be guaranteed by any reactive stop under gaps. Count may reduce under governor ON, actual fill/commissions, MQL5 `OnTick` coalescence, native indicator gate and sample chronology.

### Additional bounded Jan/Sep arms already tested
- Jan first 200k: frozen dual OR/old exit 1,239/-$452.02; V9 first +$0.10 905/-$335.31; V9 250ms adverse 937/-$338.29; reverse-all-side 913/-$391.69.
- Sep first 200k: frozen dual OR/old exit 1,162/-$475.60; V9 first +$0.10 900/-$368.52; V9 early adverse 926/-$390.05; reverse-all-side 943/-$367.01.
- Reversing all sides loses on both Jan/Sep; early adverse net worsens both. Both remain *diagnostic*, not an approved optimized rule. V7 matched-history predictive cash kernel also failed to discriminate winning versus losing candidates, per prior ledger. Do not run the same variants again without a new explanation or independent evidence.

## Acceptance / release blockers

**FAIL** joint gate: >=303,934 completed trades on FULL comparable January–September original source and **positive after-cost NET**; broader month-to-month consistency and independent later OOS still untested. **FAIL** economic profitability on nine prefixes. Production unchanged, no demo/live orders authorized.

Before any promotion, measure per-side net/gross loss/first-passage and abnormal 12 gap overrun cases; design a non-peeking *joint entry-and-hold action* only when it improves risk-adjusted positive expectancy and preserves volume rather than cherry-picking exposed months. Existing native V8/MQL5 includes bounded 180s source history, M1 `iADXWilder`, EMA20 and M1/M5 `iATR`, with honest quote-only activity fallback, but **native V9 parity and MetaEditor zero-error compile are NOT established**. Original R9 Python session-adjusted M5 ATR and MQL5 flat 1.75 filter, synthetic vs native indicator seed, and exact-ms `CopyTicks` catchup/events remain parity blockers. No ability to guarantee $0.10 minimum realized cash, $1.75 hard realized maximum, $2 realized loss limit, or 25% account loss under real gaps/latency.

**Do not relabel a negative NET trade as positive; do not loosen stops, remove commission or replace Bid/Ask with midpoint to manufacture a profit claim.**
