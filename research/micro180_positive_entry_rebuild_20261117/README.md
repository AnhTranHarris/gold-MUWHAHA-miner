# MICRO180-RB1 — NEW entry-only causal reconstruction (January-first, month-append)

**Not a V28 parameter update. Not an exit/holding or live order engine.** New, independent research implementation. The original V28 SHA/weights and every source R9 trade remain unchanged. Developed in the owner's requested entry-only mode.

## Objective and immutable data contract

Reference: updated **R9 SYNTH positive-winning-leg / Coinexx REAL TickLogger** merge, **236,079 positive individual trade legs, +$379,057.59 original synthetic net of those legs** across January–September 2026. No target records are rejected for family, profitability, or quote divergence. Those positive individual legs include winners in some net-nonpositive *complete* cycles; strict positive complete-cycle accounting is a separately preserved denominator. The original $379,057.59 is not Coinexx executable profit.

**Train** a new entry pattern/direction/phase model by reverse engineering real quote market state at each exact original R9 SYNTH teacher whole-second and preserve family target labels for offline learning. **Evaluate** independent entry intentions against **same source-minute + original R9 leg + BUY/SELL + teacher second** and ±2-second proximity. No hold/exit, alternative trade P&L, realized-profit optimization, missing-opportunity penalty, or losing-trade classifier is in scope. The algorithm cannot use exact teacher timestamps while deciding when to issue an entry. Labels are only offline teacher exemplars and post-replay scoring.

Taxonomy: **23 mutually exclusive atomic family target labels**, plus 4 overlapping A/B/C/D reporting parent summaries (27 reporting rows; not 27 disjoint patterns). Seven role heads A1, B1, B2, C2, D1, N1, N2; entry-side and 6 observable regime states derived from **as-of** quote features, not future R9 cycle classification. B2/N2 conditional second-entry policies and C2 recovery shadow mechanism have `conditional_on_flat`, never assume a real exit or fill.

## V28 lineage explicitly re-examined, but not reused as coefficients

Reviewed the V3 asymmetric BUY/SELL code and charters; V5 ordered 250ms path, M1 indicator proxies; V6 past-only kernels; V7 setup-conditioned kernels; V8 same-ms/quote freshness parity repairs; V9 four-lane OR design; V10 frozen R9 versus real quote control; V11 independent dual-basket and new-minute anchoring; V12 teacher clock, reference timing and positive-entry two-head approach; V28 frozen July-trained C++ 38-slot/25-score, eight-head prototype/phase/hazard model. Never import those V28 fitted weights: the original V28 Jan–Jul reference had a materially smaller/different supervision population. Core reusable **mechanism ideas**, not fitted coefficients, are reengineered as new code here.

## New architecture (C++ accelerated, Python entry policy)

`src/causal_quote_engine.cpp` reads **original** per-day `R9_REAL_YYYY-MM-DD_ticks.csv.gz` data directly with zlib, traverses every REAL row in exact source order including same-ms duplicates, and constructs source-second snapshots. No separate quote library, M1 bars file, raw ticks file, synthetic entry stream or logger R9 event fields is generated. Features derive from observed bid/ask and **completed** prior seconds/minutes:

- 180s/300s/60s/15s/5s returns; signed efficiency; 5s/15s baskets, minute-seed displacement; four 5/15 × 15/30 historical executable-side breakout opportunities
- M1/M5 ATR proxy based on completed M1 bars and complete 5-minute groups; completed M1 Wilder +DI/−DI/ADX14 and EMA3/8/21
- quote-count-weighted VWAP **proxy**, not traded-volume VWAP; quote-update intensity (not volume), spread shock, short and long realized quote RMS, microstructure time, channel/regime, contraction, current completed-second S1 proxy
- all values use observed historical Bid/Ask; no source `event`, R9 gate, `s1`, source `atr`, synthetic teacher exit/profit or volume_real fields.

**Source event clock:** `target_teacher_sec = (equote_ms - elag_ms - 1000)/1000` must exactly reconcile to original `entry_time_broker` UTC second. This is the **original R9 SYNTH second**, *not* the next-full-second mapped Coinexx quote. The engine samples on the first actual REAL quote in that second, using only causal quote history. At cold starts, quality windows are unavailable and original targets remain in the denominators rather than acquiring fabricated features. The original next-second mapped price is stored only in the immutable offline targets.

**Training-only optimization:** C++ `--only-seconds` selects only target teacher seconds **for small positive snapshot export**. Inference never supplies that flag or any target list, and streams independent seconds through the frozen model. This avoids redundant multi-GB derived caches and preserves source tick archives.

`src/positive_entry_model.py` trains deterministic, positive-only KMeans manifold prototypes separately by available **atomic family + side** on 41 chronological market features, learned event-second clock, hourly conditional intensity and six observable regimes. Small family/side cells remain unpopulated until sufficient positives exist, instead of inventing samples. Scoring independently evaluates both directions on each real second, maximizes a causal family-conditioned score, emits first-leg and flat-conditional second-leg **shadow entry intentions**. Original teacher labels/times are not supplied to `replay`.

`src/forward_month.py` scores a **previously frozen** model on the later month before its targets can be fitted. `src/append_month.py` then creates an append-only merged policy with **per-month independent feature scaling and centers**, checks the forward receipt SHA, chronology and leakage flags. No previous month weights are averaged away.

## Local run (read-only original sources already present)

```sh
# Compile C++ accelerator (only C++17 and zlib; never builds a tick warehouse)
g++ -std=c++17 -O3 -Wall -Wextra -Werror src/causal_quote_engine.cpp -lz -o src/causal_quote_engine
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v

# January partial developmental training → later JANUARY teacher-entry test
python src/positive_entry_model.py --month 2026-01 --train-days 5 --eval-days 2 --outdir results/jan_probe
# Freeze entire January after its developmental tests
python src/positive_entry_model.py --month 2026-01 --train-days 21 --eval-days 0 --outdir results/jan_frozen
# January-only model on later February, BEFORE any Feb fitting
python src/forward_month.py --model results/jan_frozen/micro180_rb1_2026-01_positive_model.json --month 2026-02 --days 2 --outdir results/feb_forward
# Then freeze February independently; append after source/forward receipt verification
python src/positive_entry_model.py --month 2026-02 --train-days 20 --eval-days 0 --outdir results/feb_frozen
python src/append_month.py --prior results/jan_frozen/micro180_rb1_2026-01_positive_model.json --new results/feb_frozen/micro180_rb1_2026-02_positive_model.json --forward results/feb_forward/micro180_rb1_frozen_forward_2026-02.json --out results/merged/micro180_rb1_JanFeb.json
# Next: freeze prior JanFeb against March, only then train March and append.
```

No source or weights from V28 `MICRO180_Jan_through_07_merged_weights.tsv` are loaded. All inputs are **original local** daily Coinexx data and nine MT5_EXPAND target ZIPs; no regenerated source. This is **not** a native MQL5 implementation yet, and Python/MQL5 parity is not claimed. `OnTick` may coalesce source events; a later native research adapter must use audited `CopyTicks` catch-up and a one-to-one feature-trace parity check. Keep all order execution disabled until explicitly authorized.

## Current measured developer checkpoints (not deployed)

- January training first five days: 5,115 positive targets, 4,900 usable as-of snapshots. Jan 9 and 12 frozen within-month evaluation: **189/1,963 = 9.63%** correct minute/leg/side within ±2 seconds; **39** exact teacher-second matches. Neither benchmark uses R9 exits.
- January complete: **7,699,274** original tick rows processed once, **23,485 / 24,368** targets have valid causal snapshots; 42 populated atomic-family/side models with 41 features. This is **in-sample model freeze**, not an independent January score.
- January-frozen → Feb 2–3: **1,108,092** real ticks; **757/4,020 = 18.83%** positive R9 entry targets matched within ±2s, 105 exact seconds.
- February complete: **7,102,818** original real ticks processed once, **28,257 / 29,600** targets have valid feature snapshots; 44 populated independent atomic/side specialists.
- Append-only Jan+Feb = 86 independently trained family-side profiles, with exact source and forward-receipt hashes.
- JanFeb-frozen → March 2: **291/1,828 = 15.92%** matching positive R9 targets within ±2s; **53** exact seconds. March has NOT been used to re-fit that frozen JanFeb model.

These concordance numbers are **not yet satisfactory**; preserving real measurement rather than silently injecting the teacher schedule is mandatory. Native MQL5 implementation and all nine month appends remain subsequent build stages.
