# Gold MUWHAHA Miner — R9 v2 source-exact entry asymmetry audit

**Audit date:** 2026-11-02. **Scope:** read-only code/archived-evidence audit of the R9 v2 entry pipeline. **Status:** audit findings, not a trained/promoted policy. No MT5 EA edits, GitHub writes, Drive writes, new monthly backtest, trading authorization, or performance certification.

## Provenance and verified inputs

- GitHub frozen lineage under `AnhTranHarris/gold-MUWHAHA-miner`, branch `carson/r9-v2-dual-action-bnph-20261102`, HEAD `a4ae6633b306b53057a71acb6ff1df6a63225d32` (observed in connector).
- Dual-action ZIP: `R9_V2_DUAL_ACTION_BNP_HAWKES_SOURCE_EXACT_20261102.zip`, 714,748 bytes, SHA-256 `a8afea970daa863cd46baf8a9ed1beee89c9599a9a1edc141cfa4b7e11504b79`, ZIP CRC pass, **71/71 internal manifest-member hashes verified independently**.
- All eight source-exact paired-action `R9_V2_PAIRED_ACTION_{COINEXX|DUKASCOPY}_2026_{01|02|06|07}_FULL_CHECKPOINT.zip` archives were recovered from the existing ChatGPT Library, independently SHA-256 verified against `SOURCE_EXACT_SHA256_MANIFEST.json`, and each passed ZIP CRC. Total original event sample: 2,481,012 **old-lane baseline positions**, not a newly simulated full-market or on-policy trade stream.
- Research documents and eight separate corrected 60-second teacher archives were found in PRIMARY Google Drive. Their exact ZIP bytes have not all been independently rehashed in this audit; previous metadata matches archived sizes.
- The existing numerical research results are **historically exposed**; no claim of fresh, blind OOS data or live broker execution.

## Entry mechanism: causal data flow

1. **Original probabilistic-router research:** `pinned_original/original_v2/src/router_v2_features.py` builds millisecond-tick marked events, 250/500ms, 1/5/15/30/45/60s, rolling 5m indicators, causal impulse anchors, and completed-M1-derived 15m/1h/4h context. `router_v2_dataset.py` begins paired BUY and SELL hypothetical positions at selected scan timestamps, with 30s R9 exits; `router_v2_model.py` is a Bayesian first-passage/NP model.
2. **Later full-month high-volume lane:** `pinned_original/repair/src/high_volume_stream.py` ingests every raw quote for a 250ms slot aggregate. `FastClock.features` retains 250ms-to-5m completed-slot state and M1-derived HTF context. `specialist_evidence` nominates **one** side from fixed continuation/reversal formulas (lines 126–149); historical full-month results on Coinexx and Dukascopy show extensive losses.
3. **Previous observed-WAIT shadow:** post-WAIT quote observations improved chronology but held `pending.side` and remained subject to the earlier single-side nomination; no approved policy.
4. **Latest dual-action correction:** `new_research/src/source_exact.py` makes simultaneous [BUY, SELL] views of an archived 102-dimensional as-of feature vector, and `train_dual.py` trains 3-class LightGBM on the preselected OLD baseline event universe. `live_dual_router.py` re-evaluates both sides at eligible quote slots and defaults to WAIT unless a qualified policy exists. `decision.py` sets 80% P(correct), P(incorrect)<=20%, margin >=8%, positive calibrated expected return, side-specific empirical NP threshold. **None of eight trained models qualified.**

## Quantified failure decomposition — independently recounted from ALL paired-label source archives

Each old-position timestamp supplies one baseline-side and one opposite-side executable 30s hypothetical outcome. The first-passage `strict good` teacher class is not simply price direction; it requires favorable executable barrier ordering and positive final R9-style close. For these source-event samples, no timestamp yielded both sides strictly good.

| Broker | Old baseline position timestamps | Exactly one strictly good side | Neither side good | Original chosen side good | Direction correct given exactly one good |
|---|---:|---:|---:|---:|---:|
| Coinexx (Jan/Feb/Jun/Jul) | 1,592,993 | 854,236 (53.62%) | 738,757 (46.38%) | 432,802 (27.17% of timestamps) | 50.6654% |
| Dukascopy (same four months) | 888,019 | 245,517 (27.65%) | 642,502 (72.35%) | 123,343 (13.89% of timestamps) | 50.2381% |

**Crucial decomposition:** There are TWO failures, not one: (a) the baseline chooses the correct side almost randomly when a strictly good side exists; and (b) at many old entry timestamps **neither side** can meet the strict executable R9 outcome, even with hindsight. Direction repair alone cannot resolve bad entry timing, severe spread/execution geometry, or unavoidable losses. These are old-position-conditional **hindsight opportunity bounds**, not general full-market impossibility results, not executable policy performance, and not a reason to collapse time to M1.

Latest dual-action retrospective ranking among the one-good stratum was only ~51%–54%. Each source/month `*_dual_evaluation.json` records zero qualified selections, no full on-policy replay, and unapproved research status. All eight `*_policy_data.npz` files have **negative net payoff in every 20-bin side-specific calibration bucket**: the largest observed bucket mean is at most -0.1777 for Coinexx and at most -0.5838 for Dukascopy; all are negative. Therefore a `positive expected net` condition formally cannot pass with these frozen buckets. This is not merely over-conservative threshold tuning.

## Source-exact confirmed defects and representation limits

### A. Full subminute path is compressed before the final decision (major)

`FastClock.add` sees every quote, but `SlotHawkes.update` processes aggregates of six event counts over each 250ms slot; within-slot event ORDER is not supplied to the later high-volume specialist. The latest 102-dimensional `ExactQuoteState.vector` exposes first/last displacements, average spread, counts of up/down bid/ask revisions, spread-change counts, squared-change sum, quote rate and absolute-path efficiency in each selected horizon. The model does **not** receive the actual ordered quote trajectory, causal local highs/lows, consecutive bid-leads-ask/ask-leads-bid transitions, nor its signed swing/rejection geometry.

**Constructive reproduction:** Start two quote streams at bid=100.0, ask=100.2; timestamps 0,30,60,90,120,150ms. Stream U changes bid and ask together by `[+0.2,-0.2,+0.1,-0.1,+0.1]` (upper-first swing); Stream D changes them together by `[-0.2,+0.2,-0.1,+0.1,+0.1]` (lower-first swing). Despite dramatically different early high/low ordering, `ExactQuoteState.vector()` returns **identical 102/102 float32 features** for the two streams. Reproduced with exact extracted source on 2026-11-02. Thus the frozen LightGBM *mathematically cannot distinguish those two states* at this decision time. This is an information-loss demonstration, not empirical profit proof.

**Second deterministic exact-exit reproduction:** Two six-quote trajectories with identical 102-dimensional *as-of* vectors at t=150ms and identical tick timestamps/spreads/terminal quotes were fed into the archived `TickExactActivePath`, with a hypothetical BUY opened at t=0 (entry ASK 100.20, research fee 0.02). Increments U `[+0.8,-0.1,-0.2,-0.5,+0.1]` produced a trailing exit at BID 100.70, modeled net **+0.48**; increments D `[-0.5,+0.8,-0.1,-0.2,+0.1]` hit the hard stop at BID 99.50, modeled net **-0.72**. Both trajectories had exactly equal 102-element feature vectors at t=150ms (maximum difference 0.0). These examples are synthetic **unit test counterexamples**, not real-market predictive results, and compare historical trade exits from t=0 rather than prospective entries at t=150ms. They prove that order-dependent R9 trade-life information can be lost under this feature compression.

The 102-feature tensor uses h=[250,500,1000,5000,15000,45000,300000,900000,3600000,14400000]ms. It notably omits explicit **30s and 1m** statistics available in the original `FastClock.WINDOWS`, and it does not pass the richer original v2 `CausalImpulseTracker` state through to the frozen training model. HTF geometry is mostly compressed into a signed/magnitude specialist summary and coarse point-to-point displacement, not a full structure state. A continuously rolling 5-minute *brain* must not be reduced to 5-minute summary endpoints.

### B. Wrong objective/target distribution (major)

The latest 3-class LightGBM uses ordinary multiclass log loss (`objective='multiclass'`) with a shared side-reoriented feature tensor, 15-leaf / max-depth-5 trees and 32 training rounds. It is not trained to **maximize BAD rejection with correct retention as a hard constraint**, nor to optimize first-passage net utility under a minimum execution-throughput constraint. The asymmetric controls are applied afterward as rejection gates; they do not make the input informative. Source records show all model-calibrated expected payoff bins negative.

### C. Labels are conditional on the OLD trade lane (major)

`source_exact.load` loads the original high-volume lane's **already executed (hypothetical) trade timestamps**. The dual model is not trained on every eligible flat-market 250ms decision under a new WAIT/return policy; it consequently cannot certify opportunity replacement and tends to see the old negative-prospect distribution. No eight-source held-out **on-policy** single-position trade stream for the selected policy exists. The 2.48M paired counterfactual outcomes must never be counted as newly filled simultaneous positions.

### D. Hawkes and Bayesian components are implemented but not active trained advantages (major)

`competing_hawkes.py` implements a six-mark state and a manually parameterized excitation matrix but exports `fitted=False`. `live_dual_router.py` records this state in `last_hawkes` but passes only the 102-vector to a 103-feature LightGBM (after appending side). The separately implemented `bayesian_dirichlet.py` is likewise not fitted into the evaluated model. The latest "Bayesian/NP/Hawkes" title should not be misread as a fitted multivariate Hawkes or a demonstrated Bayesian performance gain.

### E. Earlier Bayesian action eligibility bug (confirmed logic defect in earlier source)

`pinned_original/original_v2/src/router_v2_model.py`, lines 258–267, chooses the largest raw-utility action FIRST, then checks NP validity of that one candidate. If BUY has utility 1.0 and fails NP, while SELL has utility 0.5 and passes NP, the routine returns WAIT instead of examining SELL. Reproduced using the original method and synthetic `ModelPrediction` objects. The newer `DualActionPolicy.decide` performs per-side eligibility first and does NOT contain this same defect; repair of old v2 path is relevant only if it is reused.

### F. Old 250ms SELL teacher arithmetic was inverted (confirmed historical label defect)

Original `research/r9_v2_250ms_action_timing_20261102/src_action_timing.py` SELL branch uses `(ask[last]-e)*side*(-1)-.02`, with `side=-1`: incorrect return orientation. The later 60s teacher sources repaired and reconciled recorded entry/exit results. **Do not recycle the earlier 212,628,296 all-action label totals or short-side labels** as valid training proof. The independently constructed paired-action returns used here are not sourced from this flawed SELL-delay teacher.

### G. The source package assumes machine-specific absolute paths (reproducibility/portability, not predictive edge)

`source_exact.BASE` and the live adapter import paths are hardcoded to old `/mnt/data/` locations. The isolated 11-test subset initially failed one file-location test, then passed **11/11** after using symlinks to the original archived directories without modifying any source code. Real-raw-tick live/offline parity test was **not run** in this audit because the matching full raw tick file was not present at the configured path. This should be fixed only as a separate nonstrategic portability change with identical source SHA256 checks.

## Priority causal research next actions (without repeating completed failed experiments)

1. Freeze/retain current source identities; use the corrected 60s teacher and independent old paired labels, never flawed earlier SELL-delay labels. Preserve separate definitions for original 2.48M position timestamps vs 1.65M sequential observed-WAIT positions vs 250ms opportunity candidates.
2. Build an information-retention regression suite: distinguish equal-aggregate/different-path 250ms trajectories, confirm observed bid↔ask lead/lag, same-ms index order, causal subminute pivots/extrema, pullback/continuation transitions, genuine 30s/60s state and session-conditional Hawkes state. Make the full 5m causal structural state available for decision-making. Use 15m/1h/4h completed geometry only as optional context, never an M1/HTF entry trigger or 15m startup block.
3. Decompose `OPPORTUNITY` (any executable side good at t), `DIRECTION` (which side is better, if any), `TIMING/WAIT` (observed next quote stream) and `REALIZED EXIT VALUE` (quote-side net and downside) into cooperating, calibratable source-specific or hierarchical models. Predict both BUY/SELL from genuinely as-of ordered quote state, not score the old nominated side. Use **future quote path only OFFLINE** to label, never at runtime.
4. Optimize explicitly asymmetric constrained decisions (correct-opportunity retention as binding floor, incorrect veto maximize, side+session+regime budgets), combined with expected executable net and minimum real nonoverlapping trade-volume requirements. Do not invent high-confidence thresholds where calibration has shown no positive expectancy.
5. Reuse original exact-tick engine and source/UTC hash manifests. Train/purge/calibrate chronologically, freeze before evaluation, test both feed domains, and ultimately perform a **full source-month on-policy one-position simulation** with spread, timing lag, realistic slippage/commission/margin/stop and account survivability. Compare to R9 SYNTH volume reference only as a separately named quota; never equate overlapping teacher events to filled trades.

## Audit evidence boundaries

This audit independently verified the exact current source bundle and eight historical input archives, inspected source code, ran 11 local unit tests under a path-only compatibility shim, reproduced one deterministic action-selection defect and one explicit 102-feature information collision, and independently recounted all eight old-paired-label classes. It **did not** create or certify an improved trading policy, re-run 64M raw quotes, independently validate all 60s ZIP hashes, or compile MQL5. These are concrete engineering findings, not a new positive trading-performance claim.
