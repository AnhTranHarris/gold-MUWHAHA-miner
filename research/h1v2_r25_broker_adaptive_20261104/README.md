# H1V2 R25 — broker-adaptive multi-horizon, source-exact research

**Status: research-only. No H1V2/R9 EA change. No causal policy meeting 80% and original R9 count has been demonstrated.**

Frozen Git parent: `f439e870cc7f1abaeb47aa2172140c424e31c05f`. New branch `carson/h1v2-r25-broker-adaptive-multicycle-20261104`. The repository preserves original H1V2, R9, R11–R24 and lateral R23H7 mechanisms unchanged.

R25 uses original R24 source first observed 1s signal grid, 300s fresh post-gap lookback, +100ms first actual observed source quote fill, 15s quote gap censorship, original R24 Bid/Ask first-passage segment trees, full historical source-ordinal identity, and original R23H7 64-quote grammar. New R25 adds exponentially decayed observed bid/ask quote mark intensity at 250/2000/15000ms. These are Level I quote updates, not verified order-book imbalance or signed trade prints.

Each signal is paired with six actions, BUY/SELL each H15 SPREAD_RECLAIM, H30 CROSS_SCALE and H60 REGIME_RUNNER. Target and adverse barriers are spread- and past-volatility conditioned at signal, converted into liquidating Bid/Ask quote barriers only after the actual source quote fill. Future labels, first passage and quote exit ordinals are used exclusively for offline supervised training and labels, never causal action inputs.

Runs per named source month: in-sample first 12 UTC hours of a single day for training, with 61-second purge before test; the last 12 UTC hours are a source-chronological pilot evaluation. Original R9 quarter/hour references are joined **only after actions**. Policies: `C0_VOLUME_FIRST`, `C1_EV_GE_ZERO`, `C2_EV_GE_75RAW`, `C3_EV_AND_PTP_GE_080`, `C4_VOLUME_SOFT_300RAW`. An independent future-selected interval-ceiling uses all six actions and exact first quote exits; it is not a causal strategy.

Month/day pilots: 2026-01-06, 2026-02-10, 2026-06-09, 2026-07-09, each performed for DUKASCOPY_RAW and MT5_BROKER_EXPORT. The latter is Coinexx-linked historical MT5 exported Bid/Ask quote data, **not dealer fill proof**. The 8 verified raw gzip source SHA256 values are recorded in `artifacts/raw_source_sha256.json`, with original source event calendar ZIPs recovered from Google Drive. Historical broker timestamp offsets and June MT5 July-tail source halo use the original R24 frozen source contract. Authenticated source raw bytes and original R23 month selection archives are required to rerun.

### Commands on source-equipped research machine

```bash
# exact frozen modules must be available through the original repository ancestor
PYTHONPATH=research/h1v2_r25_broker_adaptive_20261104/src pytest -q research/h1v2_r25_broker_adaptive_20261104/tests
PYTHONPATH=/mnt/data/h1v2_r25/source python /mnt/data/h1v2_r25/source/r25_run_day.py --source DUKASCOPY_RAW --month 07 --day 9
PYTHONPATH=/mnt/data/h1v2_r25/source python /mnt/data/h1v2_r25/source/r25_run_day.py --source MT5_BROKER_EXPORT --month 07 --day 9
PYTHONPATH=/mnt/data/h1v2_r25/source python /mnt/data/h1v2_r25/source/r25_fullcalendar_quote_census.py --source DUKASCOPY_RAW --month 07
```

The 8 test days produce per-source pilot full 96-quarter/24-hour receipts and individual source quote trade ordinal traces. The full raw quote census (separate) emits all 2026 Jan, Feb, Jun, July 11,520 quarters, 2,880 UTC hours, 120 days for each broker source, including reference-zero periods. **The census is quote admission opportunity, not simulated correct trades or profit.**

### Guardrails and negative results

The pilot models achieve source R9 volume in many observed active quarters/hours but have low target-first correctness. No named pilot achieves the original 80%-AND-volume joint condition. Positive modeled expected-value filters often select none; a zero-trade cohort is a failure, not a success. The hindsight union finds more successes than the causal model but future side selection cannot be implemented at run time. Changing the original fixed 30-sec H1V2 exit contract or adding more broker risk are scientific contract changes and must be separately approved. Never infer live account P&L by multiplying summed quote-price raw returns: lot, margin, swap, slippage, commission and actual dealer fill unverified. No historical news/prop calendar permission certified.

### Source preservation

The Drive ledger and code artifact ZIP with SHA256 receipts are stored in MT5_EXPAND `https://drive.google.com/drive/folders/1Sa1le7ZzlEV952he8ZSwu6kEqapfLkhy`. Previous full 11-volume audit stays in `https://drive.google.com/drive/folders/1IatRLkza1QwOhwK4RLYtlpsAwAwLFna8`. Record failed partial results and source errors append-only. Proceed only with independent exact source month/day/hour/15min replay and frozen experimental geometry before claiming improvements.
