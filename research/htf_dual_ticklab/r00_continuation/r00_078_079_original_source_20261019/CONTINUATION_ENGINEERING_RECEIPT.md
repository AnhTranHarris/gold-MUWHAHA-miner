# XAUUSD HTF — R00 original-source continuation, research-only (2026-10-19)

**Latest verified source-code ancestor**: `carson/htf-r00-077-direction-correction-20261019` GitHub SHA `a87dbdb8079263978a36c24db30596516c380667`. The original R00-077 portable archive and R00-065 original native-tick archive are preserved verbatim under `parents/`; all original research reports, investor and cumulative governor policies under `originals/` stay authoritative. This receipt does **not** replace or summarize those documents. No source permission, UTC correction, original event generator, backtest engine, MT5 EA or R9 baseline was changed.

## Original execution record

- **Sources:** exact SHA-registered Coinexx and Dukascopy Jan/Feb/Jun/Jul `.csv.gz` (eight genuine observed dealer bid/ask tapes, separately processed). Verified bytes and readback/source hashes under `features/*RECEIPT.json`; raw source bytes remain in canonical approved Drive folders and are not embedded into this archive. Original Coinexx wall-clock -120 minutes Jan/Feb, -180 minutes Jun/Jul; Dukascopy original UTC unchanged.
- **Event universe:** original R00-065 source quote indices/timestamps; February and June–July identity and exact 30-second labels verified against R00-077. **No signal skipped, inserted, resampled, retimed or renamed by outcome.**
- **Scoring:** first original quote at or after t+30, earlier than t+32 seconds, midpoint change above +$0.10 -> BUY, below -$0.10 -> SELL, otherwise neutral/missing wrong. This is a directional forecast diagnostic, NOT an executed/filled trade result or R9-style profitable-trade rate.
- **Training:** January only; February deterministic frozen candidate selection; June and July historically exposed (NOT genuinely blind). Seven new independent-feature LightGBM oracles in R00-078A, previous R00-077 winner + new oracle cooperative fusion in R00-078B, January-trained 5s/15s horizon oracles in R00-079. Horizon outcomes are January training labels and are **never** decision-time features.
- **Runtime/source:** `src/execute_r00_078.py`, `src/execute_r00_078b_fusion.py`, `src/execute_r00_079_horizon.py`, `src/native_phase_076d.py`, `src/ORIGINAL_067_reader.py`, `original_dependencies/causal_pivot_registry.py`, all frozen JSON plans, all model joblibs, all full 8 original-event features, June/July per-event policy decisions and R9 interval reference.

## Frozen policy comparisons: June+July, both independent brokers

| Policy | February frozen correct/373756 | June+July correct/814244 | June+July % | Preserved all events | Promotion |
|---|---:|---:|---:|---|---|
| Historical protected R00-077 `AGREE_005` | 175514 | 367343 | 45.114609% | Yes | **Retained as incumbent** |
| New R00-078A `FLIP_010` | 175473 | 367248 | 45.102942% | Yes | No |
| R00-078B `078_PRIO_STRONG` | 175599 | 367305 | 45.109942% | Yes | No; worse than incumbent on transfer |
| R00-079 February selected previous fusion `078_PRIO_STRONG` | 175599 | 367305 | 45.109942% | Yes | No |

**Unselected June/July hindsight candidates:** R00-078B UNION 367376/814244; R00-079 `077_PLUS_NEW_HORIZON` 367353/814244. These **must not** become February-frozen selected results. Every other attempted candidate is preserved in the per-policy ledgers and original per-event arrays.

## R9 SYNTH benchmark source-matched original UTC windows

Recovered R00-077 original benchmark ledger itself and audited all candidate policies against the identical original keys. **All** four scored selected policies have 1998/2006 hourly rows, 108/110 daily rows, 19/20 ISO weeks, and 5/6 UTC months meeting both 90%-of-R9 **emitted and correctly directed** signal-count floors. The failed rows are retained, including source-month boundary hours/days with no native quotes. This is NOT full 100% interval compliance and NOT a real executable R9 profit comparison.

Caveat: original R00-077 814244-event total includes source events outside its exact 2006 hourly R9 comparison key list; such events remain in the total score and were not discarded. An initial v0 independent audit script mistakenly coalesced duplicate reference keys across month boundaries; retained as `src/r9_volume_audit_initial_incorrect.py`, corrected and independently reconciled as `src/r9_volume_audit.py`. Corrected audit matches original reference hour/day totals; no forecast labels or raw quote-derived arrays were altered.

## Why this requires **non-microstep** next work

In the 814244 source events, 367207 initial baseline directions are correct; **356124 are opposite** at +30 seconds, and **90913 are neutral/missing**. With all events emitted and neutral always counted wrong, the best conceivable 30-second direction-only accuracy is 723331/814244 (88.83%). Achieving >=80% would require >=651396 correct, or **90.055% of all non-neutral** events—an exceptional requirement that further small ensemble corrections have not approached. New A/B/079 correction attempts gained about as many rescues as damage. No evidence yet establishes that the remaining direction information is available in retail-dealer quote data.

The strongest demonstrated **absolute correctly directed event count** elsewhere in the historical R00 lineage remains R00-054 548099/1231388, about 44.51% on a *different event population*. That is a distinct high-throughput research frontier, NOT a paired replacement for the R00-077 direction baseline, and still not a validated integrated EA.

### Next exact research action

Use frozen original `R00_080_NEXT_RESEARCH_DESIGN_NOT_EXECUTED.json` to develop genuinely orthogonal native quote-side event grammar, published HTF structural transition contests, first-passage race hazards, and a valid purged original-side conditional error corrector. **Recover exact missing R00-076D3 January protected OOF dependency, or explicitly version and test a replacement OOF procedure first**; do not fabricate this parent. Keep independent specialist lifecycle/expiry/reset states, broker-specific models and original event timestamps; compare complete cases across unchanged R9 UTC hour/day/week/month thresholds. Once meaningful signal research is achieved, execution/profit research is a separate later gate.

## Known continuation limitations

1. Original R00-076D3 full OOF/cache ancestor and R00-077 ~342MB original feature cache remain cloud-unverified from previous handoff; they were NOT silently recreated. This new experiment generated **new** 125-dimensional causal feature caches with distinct SHA, and is fully reproducible from its 8 verified registered source tapes + exact original code.
2. R00-079 multi-horizon package is research-only; no 80% result or guarantee of unknown future-month generalization.
3. No account capital, MT5 order execution, slippage, exits, stops or profit has been studied or certified in these cycles.
4. Community TradingView/MQL5 articles were used only as candidate mechanism inspiration; never as replacement tick data or as evidence of profitability.

## Source-preservation contract

All session-produced `.py`, `.json`, `.npz`, `.joblib`, `.csv`, `.log` and frozen plan files remain under this case root, with SHA-256 manifest. The eight large raw tick originals remain in the previously authorized Drive source folders. Verbatim governance/research predecessor copies are included, **not rewritten**, and the original R00-077 branch remains safe for rollback. Tests: `python -m pytest -q tests/test_preserved_research.py` (4 passed). Do not promote a result on the basis of this prose alone: use numeric matrices and saved event arrays.
