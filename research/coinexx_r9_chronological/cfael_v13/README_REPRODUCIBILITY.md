# V13 Causal Fibonacci–Anchor Execution Lattice — reproducible Python-only research

This package contains the **exact local research scripts** and small machine-readable research outputs from the 2026-11-15 XAUUSD Coinexx study. It does **not** contain broker tick archives, full per-entry feature snapshots, historic trade exports, trained models, MT5 EAs, or real broker fills.

## Source inputs

Required pre-existing monthly files `XAUUSD_MT5_BROKER_2026_MM_ticks_ALL.csv.gz` for months 01–09 under a directory chosen by `COINEXX_DATA_ROOT`. Required **frozen V12** Python source under `R9_V12_SOURCE_ROOT`, and pre-existing V12 derived event ledgers in `${COINEXX_DATA_ROOT}/r9_micro180_v12_results`. All nine files are SHA-256 verified against `micro180_exactms_v12.SHA_2026` at execution. The no-lookahead signal cohort is **V9's prior position-limited entry list**, not all signals a newly deployed lattice would generate.

Run (using an isolated Python environment with numpy, pandas, scikit-learn, scipy and joblib):

```bash
export COINEXX_DATA_ROOT=/path/to/existing/quote_and_v12_event_files
export R9_V12_SOURCE_ROOT=/path/to/frozen/r9_v12_recovered_source
export CFAEL_V13_OUTPUT=/path/to/local/small_results
python -m unittest discover -s . -p test_research.py -v
python map_features.py 01 02 03 04 05 06 07 08 09
python aggregate_profit_geometry.py
python model_profit_map.py
python confirm_9m.py 01 02 03 04 05 06 07 08 09
python summarize_results.py
```

These commands re-read the **existing** original source files to construct *ephemeral in-memory* quote arrays. The optional intermediate nine-month per-entry feature CSVs occupy ~50 MB compressed; after confirming `V13_*RESULT.json`, they can be discarded. Do not upload them to GitHub/Drive. No huge reconstructed tick/second libraries are produced. Avoid running months simultaneously on machines with limited memory.

The historical trade model uses observed quote-side BUY-Ask/SELL-Bid entry, opposite quote liquidation, 0.20 additional cash cost on k=1 exposure, a one-position capacity rule, a maximum four **actual** entries per minute, a 1.5s cooldown and a 250ms+2 source quote rebounce after an observed pullback. At the entry decision, EMA uses **completed** M1 only, SMA uses **completed** M5 only, and pivots must have two fully closed right bars and their delayed first-eligible time.

## Audit hierarchy

- `research.py`: causal bars/pivots/time-weighted price and original signal cohort market-side fill/exit experiments
- `map_features.py`: causal as-of-entry price location features, including actual V9 outcomes as offline-only training labels
- `aggregate_profit_geometry.py`: where winners and losers actually occurred; does not use later observations as entry inputs
- `model_profit_map.py`: single limited-complexity chronological train/calibration/later comparison; never an execution model
- `confirm_9m.py`, `summarize_results.py`: five predefined lattice/control variants across nine full original-month sources, compact aggregates only
- `test_research.py`: source-order, equal-ms, Bid/Ask, and quote-duration causality contracts
- `V13_EXECUTIVE_RESEARCH_REPORT_20261115.md`: scope, results, caveats and next necessary evidence

## Nonnegotiable limitations

1. This is a **V9 historical signal-cohort counterfactual**, NOT the fully closed-loop on-policy performance of a modified EA, since changing trades changes subsequent rearm and opportunity availability.
2. The market quote-side experiment is already generous relative to an unknown Coinexx broker latency/slippage/rejection distribution. It does not simulate passive maker limit-order fill or real traded volume.
3. All nine months have been reused for project research. The later chronological evaluation is **not untouched OOS**.
4. Although the scripts demonstrate causal geometry and execution mechanics, **none of the studied parameter combinations passed net-profit and majority-win gates**. Do not use the default constants as recommended live MT5 settings.
5. Preserve V12 original source and EA. No MT5 EA or native trading branch modification is included in this package.

## Follow-up independent signal-generation pilot (Jan, May, September only)

The additional `independent_pilot.py` is **not** based on historical V9 signal timestamps: it generates fresh M15 EMA20/M5 SMA20/M1-reclaim events on existing Coinexx quotes, with closed bar availability, delayed next-source-quote execution, six explicitly enumerated directional/rejection/Fibonacci-anchor controls, source-order Bid/Ask stop/target outcomes, strict one-position capacity, and quote-gap marking. The pilot did **not** find positive net results across the three development months; therefore it was not mechanically expanded to all nine months or tuned until something looked profitable.

```bash
COINEXX_DATA_ROOT=/path/to/existing/quotes \
R9_V12_SOURCE_ROOT=/path/to/frozen/v12/recovered/source \
PYTHONPATH=/path/to/CFAEL_V13 \
python independent_pilot.py 01 05 09
```

The pilot uses a fixed illustrative 100c stop, $2 net cash target, 10-minute maximum holding window, k=1 and an added $0.20 transaction cost (separate from quote Bid/Ask spread). It does **not** have historical broker order acknowledgments, variable slippage/commission or a live equity governor, and its results must not be described as executable profitability.

Other supporting outputs: `V13_INDEPENDENT_CLOSED_LOOP_DEVELOPMENT_RESULTS.json`, `independent_pilot_01.json`, `independent_pilot_05.json`, `independent_pilot_09.json`, `test_independent_pilot.py`, and `V13_PROFIT_FIRST_COMBINED_REPORT_20261115.md`.
