# R9 Router v2 — Frozen-default baseline collection (bounded diagnostic)

**Execution date:** 2026-11-01. **Status:** RESEARCH DIAGNOSTIC. No MT5 compile. No live authorization. Original v2 code frozen and never edited.

## Objective and boundary

The owner requested baseline entry performance for January, February, June, July 2026 on Coinexx and Dukascopy **with no optimization**. Eight full raw tick archives (all monthly rows) were verified, and the unchanged v2 tests passed 13/13. The original full-resolution `router_v2_dataset.py` collector was attempted on Coinexx January. It scaled poorly due to retaining every overlapping BUY/SELL candidate feature snapshot in memory and updating all hypothetical paths per quote. It reached ~1.45GB RSS with ~10% of gzip input consumed, and was deliberately stopped rather than continuing into container OOM. **No full-month performance claim is made.**

To obtain *some* controlled entry-performance evidence in the current runtime without changing feature functions or model parameters, the `bounded_trace_v2.py` diagnostic collector processes the entire monthly source file, keeps completed-minute geometry current on all ticks, and activates the exact frozen `RouterV2FeatureEngine` for four predeclared 9-minute UTC windows per predeclared research day, at 00:00/06:00/12:00/18:00 UTC. The first 5 minutes of each window are state warm-up. It emits at most 100 sequential 500ms candidate decision timestamps per window. Both BUY and SELL counterfactual paths are simulated with unchanged `ActivePath` (initial stop, trail, 30s timeout, bid/ask liquidation side, $0.02 fee). All labeled candidates are **hypothetical**, often overlapping, and do not represent actual trades.

`router_v2_train.py` is called unmodified with its **original defaults:** SYNTH teacher weight 0.10, NP alpha 0.10, utility minimum 0, original 5-bin Bayesian likelihood temperature 0.20, tail lambda 0.20, NP confidence delta 0.05. Its chronological fit/calibration/dev split remains unchanged. The dev selected ledger is **nonoverlapping per source**, using one active position at a time. All results are in USD per fixed 0.01 lot under the model's assumed quote-fill fee; no slippage, historical broker stop-level, or margin simulation is included.

The sample is **not representative of the entire month** and local 5-minute state is re-warmed each selected window (rather than maintained during omitted windows). The HTF minute context is retained on all source rows. The sampling grid, cap, and context restarts are declared here; do not compare these limited outcomes directly with MT5 full-month trade counts or extrapolate the trades to a full 30-day month.

## Fixed development dates

- Jan: fit 2026-01-06/12; NP cal 2026-01-20; dev 2026-01-27.
- Feb: fit 2026-02-03/10; NP cal 2026-02-19; dev 2026-02-26.
- June: fit 2026-06-02/09; NP cal 2026-06-18; dev 2026-06-25.
- July: fit 2026-07-02/09; NP cal 2026-07-16; dev 2026-07-28.

Not touched: March/April/May, August/September. These development dates have been previously exposed; development-check results are not pristine OOS.

## Reproduction

Pinned source: `carson/r9-probabilistic-entry-router-v2-20261101` at `35056fa38c11a7b2e9b9d6bab984af3368e905be` in `AnhTranHarris/gold-MUWHAHA-miner`. Data and weak teacher SHA-256 pins are in `results/source_hashes.json` in the original v2 branch, and output receipts carry input SHA-256.

```bash
python -m unittest discover -s ../r9_entry_router_v2/tests -v
for mm in 01 02 06 07; do
  for source in coinexx dukascopy; do
    python bounded_trace_v2.py --source "$source" --month "$mm" \
      --out bounded_collections
  done
done
python ../r9_entry_router_v2/src/router_v2_train.py \
  --data-dir bounded_collections --out results
python report_baseline.py
```

Note: helper script contains source-path default `/mnt/data` matching this container; adjust `--data-root` and original pinned source directory on another machine without modifying EA entry logic.

## Research integrity

- Synthetic teacher is used only as a weak training annotation on already favorable real-tick labels, never an inference feature.
- Each forecast feature is computed only from current/past quote data.
- First-passage outcomes use subsequent real ticks for *offline labels only*.
- Default Neyman–Pearson is trained on prior-day negative examples; the alpha value is not a live false-entry guarantee.
- The existing v2 cost assumption is $0.02/trade. A +$0.18/trade fee stress is shown separately and is NOT a substitute for exact broker commission verification.
- Full-month entry/trade performance is **UNMEASURED** by this bounded experiment. Do not call it an approved or optimized strategy.
