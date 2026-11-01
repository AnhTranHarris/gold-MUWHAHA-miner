# R9 v2 high-volume event-stream repair — source-exact additive implementation

**Git lineage:** `carson/r9-v2-frozen-four-month-baseline-20261101` → `carson/r9-v2-high-volume-event-stream-repair-20261101`.

## Binding owner acceptance gate (not a result claim)

The R9 SYNTH completed-position counts, extracted directly from the entire SYNTH report and grouped by their recorded native entry month, are **Jan 27,980; Feb 33,523; June 31,801; July 24,382**, total 117,686. The v2 repair must achieve **at least 85% per month** on independently replayed, completed, sequential, **nonoverlapping**, real-tick actions. Targets are Jan 23,783; Feb 28,495; June 27,031; July 20,725; aggregate 100,034. Never project from sampled UTC windows, count proposals as trades, or use the synthetic teacher to trigger runtime decisions.

## Fixed source faults

- Discard the earlier *bounded* research collection as any proxy for capacity. Its four 9-minute UTC windows and 100-decision caps were never an evaluation of monthly throughput.
- Never build tens of thousands of overlapping hypothetical `ActivePath` objects. One executable position per broker symbol, bid/ask chronological exit on the same stream, re-evaluate at the next completed 250-ms microclock.
- Price/event history is **incremental**: each of nine horizon windows uses amortized O(1) updated rolling sums, squares, path movement and max/min monotone queues; completed-minute HTF context is retained independently; event-type Hawkes excitation is a marked **250ms-bucket approximation**, explicitly distinct from the original per-tick Hawkes process. No 4h x 250ms rescans, 10-second decision scheduler, frozen hour/4h veto, or arbitrary max trades/day.
- Fix the original v2 `ActivePath.update` error where later ticks sharing the entry millisecond were silently skipped; exact chronological row order and original timestamps are preserved without fabricated time increments.
- Write real completed trades immediately to gzip CSV; keep only summary counters and one active trade in RAM.
- Preserve the original v2 files and the exact R9 source in their prior GitHub branches; all modifications are additive. The research-only `HighVolumeStream` entry scorer is not an authorized replacement for a trained Bayes/NP policy.

## Validation boundaries

`high_volume_stream.py` is an **experimental throughput lane** with competing continuation and reversal experts using observed bid/ask event counts, multiscale Hawkes excitation, subminute realized movement, completed-minute 15m/1h/4h context and spread-aware eligibility. The Bayesian v2 model and its Neyman–Pearson safety criterion are not present in this experimental scorer, and it must **not** be presented as an approved BNP/NP strategy or as a profitable result. There is no teacher runtime input and no historical hindsight feature in the scorer. The policy uses `min_evidence=.18`, `max_spread=1.5`, unchanged R9 stop/trailing/timeouts and the source-v2 `$0.02` roundtrip fee.

`volume_contract.py` fails closed on missing months; evaluates exact month-specific completed trade counts, not candidates; records economic outcomes as independent acceptance criteria. **High-frequency trade count alone never approves the strategy.** No live order integration, MT5 compilation, leverage optimization, or model promotion is performed.

## Commands

```bash
python -m pytest -q tests/test_high_volume.py
python src/high_volume_stream.py --source coinexx --ticks /mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz --out results/coinexx_01_full
python src/high_volume_stream.py --source dukascopy --ticks /mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv.gz --out results/dukascopy_01_full
python src/volume_contract.py --results results --teacher /mnt/data/r9_four_month_dev/results/synth_teacher_minutes.csv --out results/volume_contract.json
```

The last step must return `all_sources_months_pass_volume` **true** and each month status `VOLUME_PASS` to meet the user's volume criterion, but *still* requires independently profitable, calibrated evidence. Never claim the experimental lane proves this is achievable profitably at the same time.

## Frozen eight-source run and acceptance outcome

`results/REPAIR_FULL_MONTH_VERIFICATION.json` and `results/volume_contract.json` carry all eight native-month full-stream numbers. Every source-month exceeds the user’s 85% R9 SYNTH trade-count floor. The new experimental entry policy **fails** the independent profitability criterion on every source-month and **MUST NOT BE PROMOTED** as a trading EA. The per-trade `results/{source}_{month}_full/trades.csv.gz` ledgers have been independently checked for count, true executable-side net calculation, chronological ordering and zero concurrent positions. Their exact compressed bytes, every module, and the original v2 sources are stored in the companion Drive recovery ZIP.

The experimental policy is deliberately not misrepresented as a fitted Bayesian/NP system. It repairs the executable real-tick evaluation capacity, which may be used for new trained risk-aware entry decisions without rebuilding the causal engine. No volume target was fed to runtime entries.
