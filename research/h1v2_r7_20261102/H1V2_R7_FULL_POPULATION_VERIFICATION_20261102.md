# H1V2 R7 source-exact full population nested geometry and hourly grid — 2026-11-02

**Research status: FOUR MONTHS FULL COHORT COMPLETE, ZERO 80%-QUALIFIED MODEL; original v2 engine unchanged.**

## Source lineage and exact audit
Original repaired R9 V2 source audit `R9_V2_ENTRY_ASYMMETRY_SOURCE_AUDIT_20261102.md` read directly. Original XAUUSD H1V2 Jan/Feb/Jun/Jul tick source SHA-256 hashes and every original 250ms candidate label `.npz` SHA-256 verified independently before training. Repaired R9 engine and archived v2 files untouched; R7 branch from R6 `265aae380b2ddde2c3db0fa97b06a2a0aca722d6`. Do not reuse original corrupted 250ms SELL teacher. Actual original H1V2 R9 quote-ordinal 30s BUY/SELL exit data and $0.02 model research fee retained unchanged.

## New mechanism and experiment
A genuinely *past-only* multilevel nested price-path regime built from raw Dukascopy bid/ask quotes at 1s, 15s, 5m and 1h; standardized signed trend at those four horizons, spread, quote arrivals in previous 1s, path efficiency in previous 15s, and UTC 6-hour session. Fixed boundaries, no future-labeled as-of feature. Initial coarse grid 19,440 theoretical states; 24-UTC-hour fine grid 116,640 states. The second grid reuses source-exact first-stage states and original historical timestamps, not new/future quote paths.

For every eligible first-observed 250ms candidate (not 15k samples), independent BUY/SELL correct/neutral/wrong original labels trained via aggregated Bayesian-smoothed posterior per grid cell with explicit WAIT and side preference. Four-month resubstitution deliberately leaks train label into test; separate LOMO excludes evaluated entire month when fitting cell rates. Ranked cell admissions applied to original exact BUY/SELL exit rows, **one position max**, next entry ordinal strictly greater than previous exit ordinal. All losing trades still executed; no cherry-picking future-confirmed wins. Original teacher has a small number of month-tail no-future-quote -1/NaN exits; R7 research replay counts these as unscorable, NEVER profits or losses, rather than contaminating trading economics. Missing exit events are documented; do not silently count them as protected live WAIT.

## Entire population reconciliation

| Month | All original 250ms eligible events | Strict BUY good | Strict SELL good | Nonempty 6h-grid cells | Nonempty 24h-grid cells |
|---|---:|---:|---:|---:|---:|
| 01 | 4,025,968 | 543,585 | 528,773 | 11,955 | 51,558 |
| 02 | 3,112,593 | 451,069 | 443,399 | 12,766 | 55,468 |
| 06 | 4,190,620 | 586,440 | 597,071 | 11,004 | 45,833 |
| 07 | 4,072,211 | 438,341 | 445,229 | 10,627 | 41,723 |
| **Total** | **15,401,392** | **2,019,435** | **2,014,472** | — | — |

## Full-month R9 one-position replay: strict +$0.10 first-pass and source-exact net positive

Using only the **top 0.01% ranked train events**, with original model exits for ALL selected signals:

| Month | Coarse 6h all-four IN-SAMPLE replay precision | Finer 24h all-four IN-SAMPLE precision | Finer 24h LOMO held-out precision | Fine in-sample trades | Fine in-sample net ($0.02 fee) |
|---|---:|---:|---:|---:|---:|
| 01 | 23.75% | 41.13% | 7.59% | 124 | -41.640 |
| 02 | 28.42% | 46.43% | 16.15% | 364 | -163.676 |
| 06 | 29.93% | 37.09% | 15.34% | 151 | -49.553 |
| 07 | 25.00% | 36.00% | 12.50% | 50 | -18.000 |

All the above fine all-four resubstitution model-net values are negative even with optimistic Dukascopy quote execution and $0.02 flat fee; **not viable**. Every month individually fails strict correctness >=80% and minimum high-volume count. Other recorded admission rates 0.1% and 1%, and 30-record vs 10-record threshold and four additional leave-one-month-out experiments, also failed. Coarse model admitted no groups with smoothed probability >=0.50 given >=30 training examples; no 80%-eligible regime.

The fine in-sample improvement is clearly **memorization/resubstitution** of session-specific target distributions, not stable leading indicators: the fine 24-hour LOMO result is generally worse than the coarse all-four self-fit, particularly January and July. Multiple-hypothesis exploration is not independent evidence. Wilson lower bounds based on overlapping candidate events are not valid i.i.d. statistical certification. Nor does this account for Coinexx execution, slippage, latency, margin, dollar-volume conversion, or real-time fill feasibility. Do not compare Dukascopy modeled PnL directly to MT5 SYNTH broker profit.

## Anti-hallucination / future research
- Original H1V2 future-privileged oracle selects 513,262 sure-good hypothetical events, but R7 could not isolate 80% precision using only as-of nested trends + arrival + spread + session. This falsifies **these two fixed grids**, not all possible complex mechanisms.
- The bigger deficit is **opportunity/time detection**: most eligible candidate market instants are not strong first-30-second winners. Prior R6 60k deliberate high-capacity four-month resubstitution got 150/150 per month on top 1% of sampled training points, but R7 demonstrates that this DOES NOT carry to exhaustive full-month on-policy entry selection.
- Avoid repeating R3 112 weak basic grids, R4 old mark classifiers, R5 fitted six-mark count model, R6 quote arrival survival. A next distinct hypothesis is a **competing-risk instantaneous crossing hazard** with explicitly separate favorable vs adverse first-passage *event-time* targets, quote-ordinal survival exposure and dynamic risk-gated action timing. Train on independent side labels, embargo overlapping 30s windows when measuring confidence, and require one-position quote-side execution.
- No 80%-approved foresight, no promotional MT5 EA code, no live-trading approval.

## Verification and preservation
- six new R7 unit tests passed; feature-horizon future-path and same-ms later-quote mutation invariance. Full 4-month source hash and exact candidate ordinal reconciliation passes.
- Both 6h and 24h grids computed from ALL 15,401,392 250ms rows, every month; each stored compressed per-month full-length regime+tick-index+timestamp (6h) and fine regime+tick-index (24h), independent 2-side class histograms and receipts with SHA-256.
- Replay validates `executed_count = correct + neutral + wrong` and `candidate_count = correct + neutral + wrong`, skips only the original unscorable source-boundary -1/NaN action exits.
- Source and fast exact results in R7 self-contained recovery, original large H1V2 teacher arrays/raw source referenced by hashes and existing primary Drive source. No re-creation of 32 million ticks, no changes to broker execution system.
