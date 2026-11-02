# H1V2 — Four-Month R9 v2 Asymmetric Hindsight Teacher (November 2, 2026)

## Status: completed offline oracle, **not** a trained profitable foresight strategy

Source-exact parent branch: `carson/r9-v2-source-audit-repairs-independent-20261102`, `997dfdbd06157faa426c143874ad84277971570e`. **Do not modify archived original R9 exit or live model.** Original source / repair ZIPs are independent and preserved.

## Historical experimental target

Strict per-month minimum **ceil(80% x original R9 SYNTH trade count)**: Jan 22,384; Feb 26,819; Jun 25,441; Jul 19,506; 94,150 aggregate. This is **an entry-count comparator**, not an expected profitability requirement. Separately require at least 80% selected outcomes correct for any candidate foresight model. Oracle always selects only known successes; its perfect in-sample labeling has no predictive meaning.

**H1V2 qualifying entry:** a BUY or SELL entered on an actually observed, first-in-250ms-slot Dukascopy quote, quoted spread <=1.50, after 300s quote warmup; BID/ASK executable economics, original R9 initial stop ±$0.30, +$0.10 gross trailing activation and trailing distance $0.03, close at original stop or first observed quote at/after 30s. A **qualifying** hindsight action first achieves net +$0.10 after $0.02 flat research fee before the liquidation quote moves -$0.10 against entry, all within 30s, and completes with net >0 within the same 30-second bound. If a quote drought forces a later close, it does not qualify.

**Critical causal fix:** do NOT choose the *last* quote in a 250ms bin; knowing which quote was last requires a future quote. Choose first **observed** quote in each occupied bin. Preserve original event ordering and keep first-pass labels in separate oracle-only matrices.

**Optimization:** deterministic DP maximizing number of nonoverlapping qualifying R9 exact-tick exits (then modeled net as a tie-break). It is allowed privileged future labels: hindsight teacher only. It cannot become a deployed policy or performance forecast. 80% volume-equivalent success is a historical supply condition, not demonstrated edge.

## Reproducible source inputs

Full raw Dukascopy archives in PRIMARY Google Drive folder: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV.

| Month | Immutable raw source SHA-256 |
| --- | --- |
| January | d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5 |
| February | ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d |
| June | 34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2 |
| July | e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7 |

Note: Verify raw SHA strings against `src/h1v2_freeze.py` and the actual `H1V2_FOUR_MONTH_SOURCE_EXACT_REPORT.json` (the authoritative machine record); never rekey them from narrative text. Do not infer Coinexx performance from Dukascopy.

## Executable workflow

```bash
python -m pip install numpy pandas numba pytest lightgbm scikit-learn
PYTHONPATH=src pytest -q tests/test_h1v2_teacher.py tests/test_h1v2_geometry.py
for mon in 01 02 06 07; do
  PYTHONPATH=src python src/h1v2_teacher.py --month "$mon" --raw-root /path/to/raw --output /path/to/results
done
PYTHONPATH=src python src/h1v2_freeze.py
for mon in 01 02 06 07; do
  PYTHONPATH=src python src/h1v2_geometry_atlas.py --month "$mon" --raw-root /path/to/raw --results /path/to/results --sample-size 15000
done
PYTHONPATH=src python src/h1v2_geometry_probe.py
```

`h1v2_freeze.py` is pinned by default to `/mnt/data`; import its `freeze(root,raw_root)` to use different source paths. The original R9 Python `ActivePath` parity checker requires restoration of its source-exact ZIP into the documented subdirectory, and will fail if it is absent. `src/h1v2_geometry.py` features are vectorized purely as-of and correspond to the original repaired 99-dimensional ordered-quote geometry, not 1-minute-candle transforms.

## Four-month oracle results (Dukascopy; ideal execution; strictly research)

Original raw ticks: 32,290,648; causally eligible 250ms decision events 15,401,392. Maximum-count nonoverlap **oracle**: Jan 137,402; Feb 125,472; Jun 149,273; Jul 101,115; combined **513,262** potential hindsight-selected wins, 436.13% of SYNTH reference count. All four clear the 80%-of-SYNTH count floor. These are **hypothetical hindsight opportunities**, with perfect-selection privilege by definition, and cannot be represented as model precision, actual trades, actual dollar profit or margin-safe trading. Source transactions cost original $0.02 research fee and Dukascopy bid/ask spread, but omit Coinexx conditions, latency, slippage and account survivability.

## Actual subminute geometry forecast diagnostic (separate experiment)

A natural 15,000-uniform-quote-per-month sample (60,000 total) was featurized using 99 raw-ordered quote path features + spread. A predeclared fixed 3-class LightGBM fitted January + February; cutoff calibrated only in June; July untouched. Both a slow-5m control and all-horizons model returned **zero qualifying actions** under an ≥80% 95% Wilson confidence-interval lower bound (z=1.96, ≥150 calibration samples). Full geometry improves some *June* top-ranked rates but not reliable July directional precision. The causal pilot did NOT validate an 80% foresight edge. It uses a sampled candidate population, not exhaustive on-policy replay. See results JSON.

## Recovery and next scientific step

- Full exhaustive teacher `.npz` outputs are large, re-creatable from pinned raw files and this source. SHA-256 hashes are in each month's receipt.
- Compact `*_selected_exact_trace.npz` files are persisted with executable entry/exit quote ordinals, timestamps, bid/ask, first favorable elapsed, net and side.
- Do not rename, overwrite, delete or merge the original v2 trained artifacts or source-exact tick engine.
- Next research must establish a *causal, chronologically evaluated* selective BUY/SELL/WAIT policy before any 80% correctness or trading-volume claim can be promoted.
