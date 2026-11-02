# H1V2 R10 — Full-source four-month order-path and extreme rejection audit

**Research date:** 2026-11-02. **Verdict: NEGATIVE.** No 80%-accurate volume-qualified BUY/SELL/WAIT signal. This is offline, deliberately in-sample research, not an MT5 EA or brokerage performance.

## Source, preservation and research premise

Frozen original R9 v2 code and exact H1V2 30-second entry/exit teacher preserved. R10 follows frozen R9 hyper-reject control `f559f9768331bfa520f090bde02dcd108d22b661` on a NEW branch. All four Dukascopy raw gzip hashes, original 15,401,392 H1V2 250ms labels and asof R8/R7 sources are pinned and checked against immutable original receipts. The 16 original/R10 unit tests pass.

R10 tests an **actually distinct** 48-dimensional event-ordinal path grammar: last 4/16/48 raw quotes, signed efficiency, extrema sequence, directional reversals, bid-only/ask-only quote leadership, joint revisions, spread widening, signed streak, burst and path age. Critically, these features read only past quote ordinals, not the final quote in a 250ms slot. These 48 are combined with 41 R8 asof hazard indicators and 12 R7 nested-HTF regime indicators in the direct student. Neither the full raw path nor competing-risk model is proved calibrated; quote-count based windows are not equivalent to full five-minute event graph.

## Complete-month training and replay

| Source month | Full 250ms decisions | R9 SYNTH minimum 80% | R10 first quota cutoff | R10 one-position entries | R10 strict correct | R10 modeled net | Previous R9 strict correct |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01 | 4,025,968 | 22,384 | 0.03 | 49,098 | 18.68% | $-30,776.47 | 20.29% |
| 02 | 3,112,593 | 26,819 | 0.01 | 29,152 | 22.63% | $-20,220.95 | 25.30% |
| 06 | 4,190,620 | 25,441 | 0.01 | 32,247 | 21.33% | $-15,239.87 | 22.41% |
| 07 | 4,072,211 | 19,506 | 0.03 | 26,881 | 16.12% | $-15,255.23 | 16.62% |

The single frozen **all-four-month** model was trained on 40,000 uniform chronological rows/month (160,000 rows TOTAL; 30 trees, 31 leaves, 101 asof features). This was chosen after two higher-capacity attempts timed out without a model; DO NOT call the attempted 180,000/month training completed. Each of the four complete monthly 250ms universes was scored and original R9 exact 30-second exits replayed for nine prespecified training-quantile cutoffs. First volume cutoff is earliest of increasing fraction thresholds meeting required trade count. All nine selected modeled-net values are negative across every month. R9 control had higher strict precision at the first volume cutoff for each month, so R10 is **not an improvement**.

## Full-population Bayesian/NP-style motif cohorts (deliberately overfit)

Five pre-defined competing-side cells trained on **ALL** quote decisions each month (not 15k/85k sample): legacy nested 1s/15s/5m/1h grid, 4/16/48 quote micro swings, quote-only liquidity revisions, trend-within-trend concordance, and the combined full motif. Each cohort calculates in-sample side good rates, Wilson 95% lower bound, mean modeled net and independent buy/sell. Apply min support 16/64/256, lower bound thresholds .20/.30/.50/.70/.80, either requiring or omitting a fitted positive mean return, 30 gates per family. All 20 grids times 30 gates = 600 full-month rank/admission/exact-single-position-replay experiments. Results uniformly fail the joint >80% strict direction-plus-return and >80%-SYNTH trade-count target.

| Month | Maximum 95%-Wilson BUY/SELL GOOD lower bound over 5 cell families with ≥16 observations | Cells with positive in-sample mean net / major constraint |
|---|---:|---|
| 01 | 46.71% (trend_within_trend) | All cohorts extremely sparse once net positivity and support gates both required |
| 02 | 40.79% (quote_liquidity) | All cohorts extremely sparse once net positivity and support gates both required |
| 06 | 41.30% (trend_within_trend) | All cohorts extremely sparse once net positivity and support gates both required |
| 07 | 52.74% (quote_liquidity) | All cohorts extremely sparse once net positivity and support gates both required |

A tiny-sample July quote-liquidity gate reached 70% empirically on **only 10 admitted nonoverlapping positions**, not 19,506 required. Tiny selected cohorts cannot be used to imply meaningful near-80% accuracy. The best supported Wilson lower bound never approached 80%.

## July-left-out diagnostic

July excluded from fitting: first volume-qualified fraction `0.03` selected 34,725 nonoverlapping positions, strict accuracy 15.27%, modeled net $-18,680.92. July was historically exposed during earlier research; this is a **left-month-out training diagnostic**, not blind OOS.

## Scientific audit and distinct follow-up mechanisms

1. Main finding: 48 more features including quote-ordinal extrema/order did **not** remove the side-identification deficit. Do not repeatedly train larger trees on these same 101 compressed features hoping overfit creates causal information.
2. First-passage survival must explicitly estimate **time-to-favorable, time-to-adverse, and neutral/no-pass** as competing absorbing events across 250ms/1s/3s/5s/15s/30s. Fit cause-specific calibrated hazards on exact quote risk sets; current collapsed 30s class loses time-order uncertainty. This is a **new hypothesis**, not performed here.
3. Next possible improvement requires full 5-minute quote-path structural representation (event-time self-attention/state-space with bounded past-only memory, peak/sweep/reclaim graph) and genuinely **fitted** multivariate Hawkes excitation/cross-mark lead/lag, not earlier six mark count or unfitted matrix. Measure ablations against frozen R9 and R10 full-month baselines.
4. Additional proposed context: completed M1/M5/M15/H1/H4 nested trend-within-trend, session transitions and quote arrival/granular liquidity-spread mechanics only as causally timed context. There are NO level-2 XAUUSD order book market-liquidity records in the current raw Dukascopy sources; do NOT fabricate depth or cross-market correlations.
5. High-selectivity Bayesian/Neyman–Pearson gate must be fitted from **negative** BAD+NEUTRAL distributions, calibrated with embargo, and conditioned on minimum sustainable source-exact trade volume and net costs. Fitted same-month cohort Wilson bounds may overstate transferable precision.
6. After a novel mechanism is trained, evaluate *every month* full quote population and one-open-position original-exit replay, plus held-out feed Coinexx or future month. No R9 SYNTH total is a proof of executable profits; nothing is qualified for MT5/live.

## Reproduction and recovery

Run scripts from R10 `src/` with original H1V2/R7/R8/R9 dependencies on PYTHONPATH. Verify original raw gzip hashes and original H1V2 oracle `.npz` receipts before building grammar. `r10_order_grammar.py --month XX` generates original 48 quote-ordinal matrix; `r10_full_cohort.py --month XX --grid NAME` exhaustively fits/tests one month and grid. `R10_SAMPLE_PER_MONTH=40000 R10_TREES=30 R10_LEAVES=31 r10_direct_student.py --fit --mode all4` regenerates frozen direct learner; `--month XX` scores/replays full month; repeat `--mode lomo07 --fit`, `--mode lomo07 --month 07`. All original scripts and source data are immutable and existing Drive artifacts are linked in the release. The R10 feature matrices total roughly 1.4GB and are **not** duplicated in the compact release; exact four SHA256 receipts enable reconstruction. Model text weights, all 20 cohort JSON, all direct five replay JSON and fit JSON, original forensic audit and sources/tests are saved.

**Status remains SOURCE-EXACT HINDSIGHT RESEARCH NEGATIVE / FORESIGHT UNQUALIFIED.**
