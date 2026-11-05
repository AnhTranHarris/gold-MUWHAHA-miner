# XAUUSD H1V2 R26 — frozen 2026-11-04 two-feed full-month source research

## Exact source and baseline

Base GitHub SHA `f439e870cc7f1abaeb47aa2172140c424e31c05f`, branch `carson/h1v2-r26-broker-asymmetric-opportunity-hazard-20261104`. The original R9 EA, repaired R9 v2, hindsight teacher, R11–R24, R23H7 and three R25 branches are untouched. The authoritative original R9 SYNTH source-corrected UTC volume references are Jan 27,980 / Feb 33,523 / June 31,758 / July 24,324 for EACH source separately, in 120 days, 2,880 hours and 11,520 fifteen-minute quarters (1,917 original reference-active hours, 7,521 original reference-active quarters). Do not pool executions across feeds to pass quota. Inputs: original Dukascopy source and Coinexx-linked MT5 historical Bid/Ask quote exports; latter is NOT independently confirmed dealer acknowledgments. Eight original gzip source byte hashes remain pinned in `src/source.py`.

## Six distinct frozen as-of hypotheses

C1 Ridge continuation 0.5/2/6/15s price and Bid/Ask directional convexity with source cost-scaled gate (H8).
C2 Convexity pivot fade after 15/60s excursion and 2s reversal (H16).
C3 Spread recovery with earlier 2/6s observed quote spread contraction (H12 Coinexx, H16.8 Dukascopy).
C4 15/60s trend pullback and 0.5s reclaim (H25 Coinexx, H35 Dukascopy).
C5 Heterogeneous as-of router choosing strongest of C1–C4, source normalized, same 12s horizon.
C6 High-throughput independent source quote sign diagnostic with 12s horizon; **not an economic or causal edge claim**.

On each candidate the source decision is exactly the first actually observed quote of an occupied second, with >=300s fresh source after a >15s gap, nonnegative current spread<=4000 raw, exact 100ms delayed actual first quote <=1000ms late. The BUY market quote is ASK and SELL is BID, closure uses BID/ASK respectively and a 20raw quoted-price fee. STOP is adverse distance from initial liquidation price, not from synthetic midpoint. All six have distinct source-conditioned target/stop and H. The first actual quote at or before H crossing TP/STOP is TARGET/STOP; first quote after H is TIMEOUT, even if quote crossed target meanwhile; first >15s gap is UNKNOWN CENSORED, with **no** assumed known net. One-position state persists across hour/quarter/day boundaries; R9 trade targets appear only in analysis after each output trade is frozen. No external news feed or broker/prop permission is imputed, and no model training/OOS certification is claimed.

## Recorded engineering correction

Quarantined V0 had an event-ordering defect checking target and stop BEFORE the declared H cutoff. The independent original quote trace verifier rejected V0. The entire original V0 all48 lossless output and source/testing code is preserved byte-exact in a distinct MT5_EXPAND ZIP: `R26_V0_QUARANTINE_HORIZON_DEFECT_ORIGINAL_ALL48_SOURCE_BYTES_20261104.zip` SHA `4c374e1023eabfd1bd55a0a9ac92c1a567254c1160540b25bd24a57c18b43044`. The F02 corrected engine and two additional regression fixtures are in this version. Tests 11/11 PASS, after correction every source month independently passed `r26_verify.py`, all 48 corrected source outputs were verified against original source ordinal/UTC time, fill delay, STOP/TP-H timing, nonoverlap, actual price net, original quota and source ZIP SHA.

## Source-exact outputs and code integrity

Each of 8 source-month archives contains 6 full policy cases; each policy case has complete original 15-minute/UTC hourly/daily CSV INCLUDING reference-zero periods, exact complete accepted/unfilled original source ordinal trade arrays in NPZ, and an explicit full SHA256 receipt. The index `R26_CERTIFIED_ALL_48_SOURCE_MONTH_POLICY_COMPLETE_RECONCILIATION.csv` contains all 48 cases with source identifier, source SHA, original R9 benchmark, exact net, actual fills, exact classes, accuracy, full quarter/hour/day denominators, volume, precision and joint passes. No months or failure cases are omitted. Eight raw monthly tick gzip bytes are kept at PRIMARY original Drive, not redundantly copied into this research archive.

## Final research status — negative

All 48 corrected source-month×policy cases retain **0 original reference-active hours satisfying simultaneously >=80% strict target-first accuracy and original R9 SYNTH hourly completed trade count**, across both feeds and Jan/Feb/Jun/Jul 2026. All 48 models have negative known quote-price-net sums. C6 reached all 1,917 reference-active hourly volume quotas on EACH source, without any joint precision+volume success; this falsifies pure quote-frequency increase as a sufficient repair. Other expert policies sacrificed volume without overcoming hourly accuracy. Some isolated quarter joint passes occurred, which are retained in exact period CSV; they do NOT form a high-performing global strategy. None is acceptable for funded/live MT5 execution or an H1V2 causal predictor promotion.

The four research months have been seen by earlier work; do not call them blind OOS. Actual account dollars depend on contract-size, lot, commission, market impact, broker dealer slippage and margin, not modeled. Medium/high official news vintage and broker permissions remain UNKNOWN. MQL5 live EA files remain unmodified. Follow-up must use a genuinely new conditional *competing event* model and offline outcome-history/causal training separation, not threshold fitting on these same failing 48 cases.
