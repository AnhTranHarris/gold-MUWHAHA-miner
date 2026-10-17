# R14 causal executable-price-acquisition research lock
Date: 2026-10-17. Research-only. No investor pass; no MT5 live deployment.

## Executable mechanisms and original evidence
Causal price-improvement source and unit regressions:
`htf_ticklab/price_acquisition_r14.py`, `tests/test_price_acquisition_r14.py`.
Separate full-original-tick Numba research, scripts, source prerequisites, full funded
results and reconciled ledgers (85 ZIP members):
https://drive.google.com/file/d/1SexS1DssP7pgiizrcCrKvjVK8Qu1zJWF/view

ZIP bytes **303521**, SHA-256 `7302b9334551194786c9a7a4429407fe6b46b354a128de50c21098993a42dbaf`.
R12 verified parent `fd1aa7182b3319a9dfbba9428167c1479b4602f8`.

Results: 896 whole-account strategy-family evaluations; 240 exploratory
two-stage acquired-price configurations; 72 latency-corrected funded account
scenarios (0/250/1000ms, $100/$200, two independent brokers, Jan and Feb four-day
exposed samples), 48 matched candidate vs same-tape R12 control comparisons;
168 additional dual-path continuation versus pullback tests; chronological
Jan-trained / Feb-frozen hourly-router experiment. New acquisition entry
improves after-cost net in 24/24 matched accounts for both 15-cent and 30-cent
settings. 30-cent also reduces marked DD in 24/24, but trade-count retention
can fall below 10%, so **this is NOT an acceptable full investor system**.
Neither candidate met jointly required positive returns, trade frequency and
small-account robustness. No truly blind month has been opened in this cycle.

R9 reference is a SYNTH comparator, not a presumed executable edge.
Original Coinexx UTC source offset Jan/Feb -120 minutes, Dukascopy UTC unchanged.
Unaltered original gzip SHA pins are in the research ZIP. No third-party prices.
All original source replays use actual bid/ask first later quote; modeled slippage
and commissions and illustrative risk caps are not investor-approved. New GitHub
source is a tested acquisition interface, NOT yet fully parity-scored through the
production `htf_ticklab.cli` nor a verified MQL5 release.

## Next engineering checkpoint
Build a **single funded arbiter** that lets price-improvement, fast continuation
and sweep/reversal experts bid jointly by conditional after-cost first-passage
probability, funding and broker latency. Prior-trade evidence must mature
before live decision time. Validate exact Python CLI S/S' parity on approved
source tick tapes, then freeze configuration before touching the next unopened
month. Metrics: net, gross losses, PF, win rate, 710–2127/day aspiration,
positive hours/days/weeks/months and marked equity/DD survival at $100/$200.
No zero-trade strategy may pass investor throughput scoring.
