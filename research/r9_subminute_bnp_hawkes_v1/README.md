# Gold MUWHAHA Miner — Bayesian / Neyman–Pearson / Hawkes entry v1

**Status: source implementation and shadow features only; untrained, uncalibrated, not MT5-compiled, not safe to deploy.** The existing R9 holding/trailing/time-exit logic is retained in the separate EA clone. Original R9 is unmodified.

## Design purpose

Replace the misleadingly profitable synthetic M1 bracket + S1 gate with a **causal, event-time, 8-level entry engine**. An entry is allowed only if a frozen score ranks it above an independent held-out Neyman–Pearson rejection threshold and the MT5 settings explicitly authorize trading. No 1m/15m/H1/H4 geometry or look-ahead confirmed pivots.

Real tick → completed `250ms`, `500ms`, `1s`, `5s`, `15s`, `30s`, `45s` quote bars. Each bar contains only arrived quotes and no interpolation. The running current interval is never used for historical features; the **current quote** can be used for event-time Hawkes intensity, side selection and executable spread. Every gap >15s invalidates all rings and intensities. Candidate evaluation is at most once per 500ms time slot; no modeled ticks are manufactured.

## Feature model

A bivariate exponential Hawkes **candidate specification** measures up- and down-quote-event intensities, using fixed stable kernel `(alpha_same=0.7, alpha_cross=0.2, beta=4.0 s−1, baseline=0.5)`. Its coefficients are currently **design priors, not fitted/validated Hawkes parameters**. It is not a magic predictor of news or future prices.

For each completed clock, the engine calculates completed-bar ATR(14) and ATR acceleration versus earlier realized ranges, signed RSI(14), Bollinger z/dislocation using trailing 20 completed closes, price position within trailing 34-bar high-low range (a **causal Fibonacci location proxy**, NOT a later-confirmed swing), momentum/path efficiency, and **quote-update-weighted average price (QWAP)**. QWAP is *not* true transaction-volume VWAP: Coinexx and Dukascopy quote feeds do not supply a consolidated gold trade tape. The feature names and mathematics are version locked.

Eleven bounded signed features feed five immutable bins. Bayesian Dirichlet-smoothed class-conditionals form a tempered log-likelihood-ratio ranking score. Until supervised fitting, these are **not probabilities**. Later, an independently held-out negative class produces a Neyman–Pearson order-statistic threshold with target false acceptance bound alpha and violation tolerance delta, subject to exchangeability assumptions that are doubtful for market quotes. This must be checked in chronological OOS and across brokers; no formal guarantee is claimed for dependent market events.

## Critical operation gates

- `InpUseBNPHawkes=true` uses the new entry path rather than R9 bracket/S1. The original R9 file is not edited.
- `InpBNPShadowOnly=true` and `InpBNPAllowOrders=false` by default. **No orders** are permitted.
- With no frozen policy file, model loading fails closed. To trade, code requires an explicit frozen and real-validated model plus intentional input changes. No such model is bundled.
- `OpenTrade`, `ManagePosition`, trailing SL, stop placement, 30-second timeout and position reconciliation use the inherited R9 implementation. Known R9 gap/stop-loss/cycle risks remain **unfixed** and cannot be considered live safe.
- Multi-clock Python and MQL5 formulas are intended to match. They have **not** yet passed a binary MQL5 compile or cross-language feature-stream parity. Passing Python unit tests does not establish MQL5 production suitability.
- The reference source SHA is GitHub commit `8729a6345655a7b4ea31facc81982004ee2b8921`; original EA blob SHA `7eecb5f1947017a01ce85b2520725de54749e523`.

## Teacher training — intentionally NOT performed

The historical MT5 generated-tick SYNTH teacher trades are retained only as a **weak privileged training signal / proposed ranking target**, never a substitute for real-tick survivability labels. Training will use a chronological separation: features at t, labels only when the teacher/realized R9 path has completed after t, fit window earlier than independent calibration window, embargo around split boundaries, and untouched later real-tick Coinexx/Dukascopy evaluation. There must be no mapping of a synthetic path's future high/low to an earlier quote feature and no teacher-provided exit facts used at entry inference.

Before any actual model approval, define a label capturing survival of the **unchanged R9 SL/trailing/30s exit** after spread and stop execution, and compare SYNTH teacher ranking against real quote path outcomes. An action that only imitates teacher success but loses on Coinexx real ticks is rejected. Additional sample-selection bias, overlapping horizon and account-capital sensitivity must be documented.

## Run causal shadow research

```bash
python -m unittest discover -v -s tests
python src/entry_model.py --ticks /path/to/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz --source coinexx --out results/coinexx_jan --limit 250000
python src/entry_model.py --ticks /path/to/XAUUSD_DUKAS_2026_01_ticks.csv.gz --source dukascopy --out results/dukascopy_jan --limit 250000
```

`shadow_candidates.csv` contains **features and candidate intentions, not executed trades**. `summary.json` contains the source hash and row counts. Outputs should be reproducible from the pinned, source-native tick sequence. Never use these outputs as a P&L report.

## Technical reference

- MetaQuotes MqlTick `time_msc` and quote flags: https://www.mql5.com/en/docs/constants/structures/mqltick
- MetaQuotes `OnTick` queue can coalesce events: https://www.mql5.com/en/docs/event_handlers/ontick
- MetaQuotes `CopyTicks` for sequence fidelity: https://www.mql5.com/en/docs/series/copyticks
- Real vs synthetic MT5 tick divergence: https://www.mql5.com/en/articles/2612
- X-DataInitiative's Hawkes implementation and exponential-kernel definitions: https://github.com/X-DataInitiative/tick/tree/master/tick/hawkes
- Neyman–Pearson umbrella classification, Tong et al., Science Advances 2018: https://pmc.ncbi.nlm.nih.gov/articles/PMC5804623/

## Next chronological gate

**Next = source exact MQL5 compile + January Coinexx/Dukascopy feature parity**; only after that, create teacher-aligned labels and fit a model on a declared historical development window, calibrate NP on untouched later data, then score later months and second broker without changing inputs. Holding and exit redesign is explicitly out of scope for this commit.