# DAA April Auction Awareness — exploratory checkpoint 2026-10-08

**Research-only branch. No accepted V1 modification. No EA change. May 137 remains paused by owner.**

Authoritative detailed research and exact replay scripts/results/checksum/tar available in ChatGPT Library:
`/xauusd-trading-bot/delta-A-alpha/monthly/april_2026/vertical-grid-136/auction-awareness-20261008/`

The source artifacts are:
- `DAA_APRIL_AUCTION_AWARENESS_20261008.md`
- `april_awareness_replay_v01.py`, `april_runner_extension_v01.py`, `april_capital_equity_v01.py`
- `APRIL_AUCTION_AWARENESS_CYCLE_001.json`, `APRIL_RUNNER_EXTENSION_CYCLE_002.json`, `APRIL_CAPITAL_EQUITY_CYCLE_003.json`
- `SHA256SUMS.txt` and `DAA_APRIL_AUCTION_AWARENESS_CYCLES_001_003_20261008.tar.gz` (SHA256 `fbb027beeb174695b0f3cac722ace8c561d04b801886748e444fea4dcee7d536`).

## Experimental findings (not broker-certified)

April-136 **April-selected** archived event sources; fixed 0.01 lots, normalized $0.20 quote spread, $0.02 trade cost, 11,094,790 chronological tick cache, prior completed M1 / H4 / H1 / M15 / M5 features. The new acceptance gate does not use calendar month/date/hour as a signal. The V1 source event generators are still session aware.

- Cycle 001: Frozen inherited 4-fast-win renewal rule with **global cap256**: **+$43,924.76 / 12,284 trades / gross loss -$3,441.63 / PF 13.763**. Proposed auction awareness: **+$43,954.07 / 12,471 trades / gross loss -$3,581.35 / PF 13.273**. No viable incremental improvement; worse downside quality.
- Cycle 002: Eight causal exit-time H4/H1/M15/M5 runner-extension variants: all net-negative vs core **+$40,736.14**. Simple extension rejected.
- Cycle 003: full-tick floating-equity, strict cross-layer cap. At cap256 inherited **equity DD $2,879.08**, proposed auction **equity DD $2,915.32**, core-only **equity DD $1,792.16**. At global cap1 core net **+$849.70** (equity DD $21.59); global cap32 auction net **+$20,610.08** (equity DD $490.56). All root-quote realized P&L checks had zero price/P&L reconstruction error at logged precision.
- April-136 transition frontiers $67.5–71.3K remain **April-selected research**, with hundreds of simultaneous tickets and no cross-month deployment proof. January–March's >$170K exploratory profit at 0.01 lots has NOT been replicated in April with strict capacity controls.

**Falsification:** fixed gate filters, faster scouts, and passive runner extension do not solve the April opportunity/capacity economics under these test surfaces. Do not cherry-pick the slightly higher net.

## Next exploratory module, NOT yet implemented

**L0 tick-first-passage → L1 completed recent range/cost auction state → L2 H4/H1/M15/M5 structural opportunity → L3/L4 existing HIGHVOL/ASIA → L5 earned renewal scout → L6 independently originated native continuation → L7 conditional wrong-direction recovery → L8 strict global physical inventory / equity cap**.

Develop causal original Bid/Ask *new opportunity generation* via completed-price displacement/transition and bounded CUSUM plus first-passage net excursion. Do **not** simply re-filter April-selected events. Shadow counterfactual quote outcomes must be separately logged from funded realized wins. Test 1/4/16/32/64 cap, cumulative turnover/velocity, net, gross loss, equity DD, broker margin feasibility, and 0.01 lot fixed. Train on Jan–Mar; April is evaluation/diagnosis, not optimization authority. May remains paused until explicit owner instruction.

**Sources:** https://www.mql5.com/en/articles/21833, https://www.mql5.com/zh/articles/16213, https://www.mql5.com/ja/articles/16213, https://www.tradingview.com/script/NtSoWuHM-Adaptive-Fractal-Grid-Scalping-Strategy/, https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/risk-management/supported-models

**Branch starting point:** `delta-A-alpha` commit `277452e2a94943f21a7f3c52b7966e1781848c07`. Retain `CURRENT_INFLIGHT.json` as `IDLE_READY` with May as next scientific cursor; owner has paused that work.