# H1V2 R3 — Source-Exact Multigrid, Session, Trend, Regime, Horizon and High-Skew Research

**2026-11-02. Scientific status:** Deliberate Jan/Feb/Jun/Jul **in-sample overfit** and explicit falsification. **No executable directional policy qualifies, no original trading engine modified, and no profitability claim.**

## Source and immutable scope

- User-authorized H1V2 hindsight research; do not replace, merge into, or retrain the original v2 execution policy from this archive.
- Exact parent R2 GitHub branch `carson/h1v2-is-overfit-skew-r2-20261102` at `0a6f860bf2b3e265922af55bd2547e4970037101`. Original H1V2 baseline `edce573d9c53b743dc5de1b0d741c81370af52c1`; repaired v2 baseline `997dfdbd06157faa426c143874ad84277971570e`.
- Preserve full existing R9 `ActivePath`, H1V2 tick-ordinal teacher/labels, and Dukascopy source hashes from original v2 full audit. Only add isolated R3 scripts and derived, replayable data.
- Source R2 complete recovery (authoritative): https://drive.google.com/file/d/11vsLhtdkDUfdEF34Q7zPYqpIJibu-aPV/view (SHA256 `4105f83b7562c36cf9eab94c190bf99ea7b191ee9de713a25daf460e7e7f692e`). Base H1V2 complete dependency kit: https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view (SHA256 `9a79d633c72be310737aee06627e5e8ee9df9ae0fea2658f5a159ad9328a2e61`). Four original raw Dukascopy sources Jan/Feb/Jun/Jul: https://drive.google.com/drive/folders/1lSCfO_awUKkbR4I6xDTy9orjIl0SrgIV .
- R2 independent-side labels (not features), 60,000 as-of quote states / 120,000 BUY+SELL action rows: WRONG 99,341; NEUTRAL 4,898; WEAK_GOOD 12,517; STRONG_GOOD 3,244. Reverified R2 frozen data SHA256 for months January, February, June, July in R3 JSON `source_sha256` and ZIP manifest.
- Strong-good teacher is the ORIGINAL exact bid/ask first favorable >= $0.10 before adverse -$0.10, <= 3s, R9 exit net >= $0.10, opening spread <= $1.00, on the original 250ms first-observed-quote candidate population. Original first-hit and exit paths were NOT recomputed or modified in this R3 (source-exact R2 data reused).

## Experiment design: hypothesis -> high-capacity fit -> adversarial self-exclusion -> month-out falsification

1. **G1–G8:** Probe interlocked session, slow/fast terminal range-position, extrema order, relative volatility, one-sided quote revisions, quote-side leads/lags, day-of-week and 250ms/1s/5s/15s/30s/60s/300s feature grids. These are as-of aggregates, not actual start-to-end signed trends.
2. **G9–G14 (new and independently derived from four ORIGINAL raw gzip files):** Actual first-to-current midpoint displacement (context **only**, never for execution), absolute displacement and **raw quote-arrival intensity** at 250ms, 1s, 5s, 15s, 30s, 60s, 5m, 15m, 1h, 4h; combined with UTC session, liquidity/volatility bins and quote-order features. Every source was SHA256 verified, all 60,000 selected quote indices and UTC timestamps matched original R2 source indices, all lookups at or before each candidate's ordinal. Historical anchor missing or stale beyond requested horizon+10 minutes -> marked MISSING, never backfilled with a future bar. Four-hour anchor valid for 92.14%-94.45% of sampled rows, as recorded separately. This is actual causal HTF tick context, not synthetic OHLC.
3. **112 explicit grid configurations** = 14 motif families x four minimum matched-cell supports {1,3,10,30} x two gates: naive training-cell average >= 0.80 versus conservative Wilson 95% lower confidence bound >= 0.65. Independently trained BUY/SELL cells; if neither qualifies or the sides tie, output WAIT. Per-condition strong/wrong/neutral/weak results are stored separately.
4. Score every fitted grid on **the same four-month training rows** (deliberate resubstitution) and, separately, on July with **no July labels used in training** (Jan+Feb+Jun fits). The latter is an audit only; no prospective policy is approved. For support=1 and naive >=0.80, apply a further **leave-one-observation-out** test across all four months: remove the scored label from its own fitted cell. This isolates unique-key/singleton memorization. Because LOOCV still uses other future-month labels, it is not a chronological OOS validation.

## Exact results

| Mechanism | All-4 in-sample, same rows | All-4 leave-self-out | July never trained |
| --- | ---: | ---: | ---: |
| G7 dense 250ms→5m range-position/path motif | **785/785** strong | **16/416** strong; 348 wrong | **4/148** strong; 130 wrong |
| G8 fast/slow quote revision motif | **192/192** strong | **6/161** strong; 141 wrong | **4/62** strong; 50 wrong |
| G13 **NEW actual raw first-to-current 250ms→4h true-path motif** | **363/363** strong | **4/280** strong; 250 wrong | **1/105** strong; 93 wrong |
| G12 new session/persistent 15m/1h/4h quote structure | **126/126** strong | **4/117** strong | **2/70** strong |

- G7 self-exclusion monthly: January 5/103 strong, February 2/101, June 5/116, July 4/96. No month retains the apparent training perfection.
- G7 naive resub monthly: January 193/193, February 223/223, June 243/243, July 126/126; perfect four-month training set fit is precisely the unreliable property being audited.
- 14/14 families and 112/112 gate configurations fully evaluated with per-month receipts. **None of the 112 Wilson lower>=65% cell gates selected any events on the original 60k-row four-month resubstitution**; no recurring well-supported motif has demonstrated robust high-skew discrimination under this test. A 95% Wilson threshold of >=80% would be still more restrictive.
- Historical baseline R2 reoptimized future oracle: FAST3s/net10/spread100 **241,459**, FAST5s/net20/spread100 **211,096** across four months; no change. R3 selections come from 60k *sampled* 250ms candidate timestamps, may overlap, are NOT the full 15.4M event universe, and MUST NOT be converted into nonoverlapping trade counts or compared numerically against R9 SYNTH volume floors.
- Evidence: 23/23 combined old H1V2 + R2 + R3 unit tests passed at the first R3 audit, including raw quote replay-derived feature construction, same-ms ordering, side tie -> WAIT, unseen cell fail-closed, self-exclusion, and source unmodified. Full scenario JSON reports all four months for each candidate; R2 original test/parity receipts remain unchanged.

## Failure diagnosis (this is the useful discovery)

The four-month teacher has a very large supply of future-confirmed fast winners, but simple repetition of increasingly fine as-of regime/quote-path feature grids turns them into **essentially unique market-state fingerprints**. The hyper-detailed G7 fit matches 785 strong labels in-sample; removing the self-label yields only 16/416, a collapse from 100% to 3.85% strong-good. July confirms the failure (4/148, or 2.70%). Adding genuine true causal 4h trend displacement and quote-rate context likewise fails to generalize on the 60k sampled events (G13 leave-self-out 4/280, July 1/105). We thus disprove the hypothesis "more as-of feature complexity by itself creates an extreme correct-signal skew" under this experiment.

An observed rejection gate should not be judged on prediction accuracy alone; evaluate **risk versus admitted volume** and very different costs for WRONG versus NEUTRAL. Research basis: selective classification under distribution shifts https://pmc.ncbi.nlm.nih.gov/articles/PMC12470254/ . An event-marked self/cross-exciting intensity process might extract recurrent quote revision ordering unavailable in state averages; reference Oxford JFE https://academic.oup.com/jfec/article/22/4/1098/7241580 . **Their empirical results concern order book data; the H1V2 feed contains bid/ask quotes only. Never claim to have fitted real market-order intensities from Dukascopy quote updates.** Neither of these candidate mechanisms is fitted in R3.

## Next distinct hypotheses for repeated prompt (do NOT redo R2/R3 negative experiments)

1. Extract actual causally ordered event motifs (not summary feature cells): signed Bid-only, Ask-only, both-side revisions, spread shocks, multi-pivot swing renewal, time gap, and regime-dependent asymmetric first-passage crossing sequences within 250ms/1s/5s, with explicit source row ordinals.
2. Fit action-specific **quote-revision marked intensity** (Hawkes or survival/competing risk) using only observed quote changes, with calibrated six-mark autoregressive excitation and model-state continuity; compare against shuffled-event-order adversarial control and time-aligned base-rate control. Stop if extra information does not survive July-no-train test.
3. Train empirical Bayes posteriors with a hierarchical side/session/volatility/regime shrinkage prior rather than relying on rare-cell resubstitution. Use strong-good vs WRONG vs NEUTRAL separate heads. Use directional loss/expected net and retained-volume constraints jointly, require held-out Wilson lower>=80% plus monthly throughput before any policy nomination.
4. Study broker domain shift (Coinexx vs Dukascopy), genuine latency/slippage/fees, and on-policy one-position quote-ordinal execution only AFTER held-out gating qualifies. The July diagnostic already warns transfer is currently inadequate.

## Recovery and reproducibility

- **No existing source file modified or deleted.** R3 code/outputs are additive at `research/h1v2_r3_20261102/` in an isolated GitHub branch, starting exact R2 commit. The R3 ZIP carries this report, source, tests, four 15k raw-horizon feature files, all 112 config receipts, source hash manifest, and complete continuation instructions. All original label `.npz` and full raw archives remain pinned in R2/original Google Drive ZIPs, linked above.
- Commands (after restoring H1V2 + R2 + R3 to specified default paths):

```
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src pytest -q /mnt/data/h1v2/tests/test_h1v2_teacher.py /mnt/data/h1v2/tests/test_h1v2_geometry.py /mnt/data/h1v2_r2/tests/test_h1v2_r2.py /mnt/data/h1v2_r3/tests/test_multigrid.py /mnt/data/h1v2_r3/tests/test_true_quote_horizons.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r3/src python /mnt/data/h1v2_r3/src/true_quote_horizons.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r3/src python /mnt/data/h1v2_r3/src/multigrid_regime_discovery.py
```

- Required Python packages: NumPy, pandas, numba, pytest (existing R1/R2 tests may require LightGBM). File hashes stored in `SOURCE_EXACT_SHA256_MANIFEST.json`; restore member integrity checks and fail on any mismatch.

**Promotion status: NONE.** This is authorized hyper-overfit hindsight research plus falsification diagnostics only; no live V2 model, no MQL5 build, no real portfolio return verification, no 80% accurate foresight results.
