# R9 Coinexx real-tick causal path-signature shadow research (Priority 1)

**Research only. No R9 MT5 EA mutation, no broker-fill parity or live permission.**

Original pinned environment: `research/coinexx_r9_chronological`, branch
`carson/coinexx-r9-chronological-backtest-v1-20261112` at
`de3e61702759af67f93eb12cff01084789357645`.

## Original data authority

The nine source monthly raw Coinexx XAUUSD gzip files are held in the user's
Google Drive under `Micro_account/gold_mt5_tick_all`, January–September 2026.
They must be mounted/downloaded as original `.csv.gz` files; DO NOT use M1
OHLC, a synthetic Strategy Tester report, model feature rows, or summary candles
in place of those inputs. The extractor reads **every original source tick**,
including same-millisecond events, and carries the unchanged R9 strategy state
across consecutive monthly file boundaries. The raw data are never written or
modified by this project. One source digest and row-count receipt is generated
per file.

Source fields are `time,time_msc,bid,ask,last,volume,volume_real,flags`.
Stop-level, fill/latency, slippage, dealer rejection, contract size and actual
commissions are **not certified**; generated outcomes are quote-path proxies.
Original R9 MQL5 source remains pinned as blob
`7eecb5f1947017a01ce85b2520725de54749e523`.

## Causal features

`signatures.py` implements streaming, *observed-only*, first- and second-order
Bid/Ask path signatures over trailing 500ms, 2s, 10s event-clock windows. For
consecutive quote increments `db_k`, `da_k`, the signed second-level area is

    2 A = sum_{i<j}(db_i * da_j - da_i * db_j).

The update is constant-time per event and its sliding-window removal uses the
exact ordered-pair inverse. Other causal covariates are Bid/Ask displacements,
quoted spread displacement, quote intensity, event-only side counts, quote
churn, net efficiency, direction-side alignment and frozen R9 gate diagnostics.
No future M1 candle, teacher label, or subsequent quote participates in the
as-of feature snapshot. Check unit tests for equal-millisecond event ordering,
area antisymmetry, window removal and long quote gaps.

## Immutable candidate labels

`extract.py` hooks the published source-exact R9 quotation replay without
modifying its open, hold, stop, trail or rearm decisions. At original R9 entry
it freezes a feature row; when that *same baseline trade* closes, it appends
its quote-side realized price movement to the row. Outputs are one atomic
compressed candidate ledger per month, keyed by original global source ordinal,
with original entry and exit millisecond timestamps. Monthly source ticks and
second-level sequence are never replaced by these candidate rows.

For supervised shadow classification, the target is positive liquidation-side
price movement exceeding a **modeled** 20-point (= $0.20 gold-price) buffer.
This is NOT certified net account P&L. Model validation has a hard minimum
60-second chronological purge and uses entire untouched later calendar months.

## Five explicit training passes

- P1: R9 contextual controls + ordered depth-2 path-area signature; Jan–Apr train, May evaluation.
- P2: full ordered-path geometry, normalization and churn; Jan–May train, June evaluation.
- P3: plus quote-side event response; Jan–Jun train, July evaluation.
- P4: nonlinear model plus full causal signature/event features; Jan–July train, August evaluation.
- P5: independently fitted nonlinear shadow, Jan–August train and **September final one-shot evaluation**.

Each pass scores all completed baseline events on its later evaluation month,
including losing events and zero-signal days where applicable; no future month
is allowed in its training features. The shadow's candidate selection threshold
is the **median of the earlier training score distribution**, fixed before the
next month's test. No sample from September is read before P5.

**Scientific scope:** scoring a subset of trades that the unchanged R9 baseline
would have taken does **not** equal a counterfactual on-policy EA replay. If
filtered, future opportunity and rearm states would change. No "shadow selected
P&L" metric can be promoted to executable trading profit absent a fresh fully
chronological single-position policy replay and broker-fill reconciliation.

## Reproduce

From `research/coinexx_r9_chronological/`:

```bash
export PYTHONPATH=src
python -m unittest discover -s shadow_path_signatures/tests -v
python shadow_path_signatures/extract.py --data-dir /PATH/TO/ALL_NINE_RAW_GZ --out-dir /LOCAL/OUTPUT
python shadow_path_signatures/train.py --input-dir /LOCAL/OUTPUT --output-dir /LOCAL/MODEL_OUTPUT
```

Training requires `numpy`, `pandas`, `scikit-learn`, `joblib`; source extraction
uses only the frozen R9 engine and standard library. Monthly row evidence,
model pickles and full per-day experiment receipts are local derived artifacts,
not substitutes for the nine original monthly gzip sources. Checkpoint and
progress files are local and not deployed.
