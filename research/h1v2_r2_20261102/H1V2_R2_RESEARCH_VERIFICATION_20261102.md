# H1V2 — Four-month in-sample extreme-asymmetry research, Round 2

**Scientific status:** completed offline hindsight teacher re-optimization, intentionally overfitted learner diagnostics, **NO approved causal trading model**.

## Immutable source lineage

- Original repaired H1V2 teacher GitHub: `AnhTranHarris/gold-MUWHAHA-miner`, branch `carson/h1v2-fourmonth-hindsight-teacher-20261102`, inspected HEAD `edce573d9c53b743dc5de1b0d741c81370af52c1`.
- R2 isolated branch: `carson/h1v2-is-overfit-skew-r2-20261102`, created exactly from that HEAD; original code and ActivePath not rewritten.
- Primary Google Drive original H1V2 full dependency package `https://drive.google.com/file/d/14Zqs-PyZ70qr0NTvpJRxpT0XcVc8msUu/view` and original H1V2 ledger `https://docs.google.com/document/d/1k9Gr5O8dfsASpdAgY53SpQtMnx1WnddKpHkcQwv3eWw/edit`.
- Source Dukascopy raw tick SHA256 January `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; February `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`; June `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`; July `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`. All verified again during R2 DP runs.
- Same original 32,290,648 source quote observations and 15,401,392 first-observed-250ms candidate rows. Never replace original with minute OHLC.

## R2 hypothesis testing / creative-discovery and falsification cycle

Each new hypothesis has an observable, reproducible failure condition. No purported AI hallucination or speculative theory is treated as empirical fact.

1. **Quality dominance + interval scheduling:** optimize strongest *future-confirmed* rapid directional excursions subject to exact R9 entry, stop/trail, 30s time limit, modeled costs, bid/ask and quote ordinal nonoverlap. Restrict FIRST favorable net +$0.10 prior to adverse -$0.10 and final R9 net >0 as H1V2, then demand faster first hit, stronger final net, and narrower spread. Source-exact original `schedule_oracle` called unchanged. **PASS as hindsight capacity only**.
2. **Multiresolution motif geometry:** derived directional impulse, extremum order, quote-revision lead/lag, event-time compression, inter-horizon acceleration and session cycles from the original 99 strictly-as-of geometry features. Initial small-capacity equal-complexity motif augmentation did not gain enough admission confidence. Higher-complexity inter-month transferred poorly. **NO validated cross-month transfer**.
3. **High-capacity resubstitution memorizer:** deliberately train on all Jan, Feb, Jun, Jul 60k as-of examples and observe rejection-option conditional precision. G2 scored 10,148/10,148 correct on its own TRAIN rows at cutoff 0.50; threshold 0.80 yielded 740/740. **Demonstrates memorization, not a deployable edge or trade count.** Unbounded older hyperparameters time out and are retained as an attempted negative experiment.
4. **Paired-action hard-negative taxonomy:** retain independent BUY/SELL label classes `WRONG`, `NEUTRAL`, `WEAK_GOOD`, `STRONG_GOOD`; STRONG_GOOD requires original strict label plus first hit <=3s, final net >=$0.10, spread <=$1.00. In the 60k as-of sample, 120k independent side labels consisted of 99,341 WRONG, 4,898 NEUTRAL, 12,517 WEAK_GOOD, 3,244 STRONG_GOOD. Training model `S1_overfit_all_4` selected 3,219/3,219 correctly STRONG_GOOD at cutoff 0.30; **this is resubstitution on training rows**. The identical learner family trained Jan+Feb+Jun without July selected 252 July samples at cutoff 0.10: **9 strongly correct, 26 weak-good, 216 wrong-direction, 1 neutral** (3.57% strictly correct). **FAIL as transferred mechanism**.
5. **Counterfactual directional exclusivity:** for all 513,262 H1V2 previously selected future winners the opposite action was coded WRONG; zero NEUTRAL and zero other-side GOOD. This is mainly a consequence of two-sided executable-cost and adverse/favorable label definitions; **NOT evidence of a predictive side detector**.
6. **Unimplemented research hypotheses:** fitting properly time-marked self/cross-exciting quote-revision intensities (not true order-book order flows), action-specific first-passage competing risks, survival-conditioned abstention, state-conditioned causal segmentation, and stress-pricing against Coinexx source. **DO NOT imply trained or successful.** Research inspiration: Oxford *Estimation of an Order Book Dependent Hawkes Process for Large Datasets* and JMLR *Optimal Strategies for Reject Option Classifiers*. These papers use market data differing from our XAUUSD quote-only feed.

## Strict, source-exact 4-month hindsight teacher re-optimization

Retaining only selected winners from the original maximal-count schedule yielded a conservative FAST3S+NET10+SPREAD100 count **154,560**, with all four monthly floors passing. Re-running the **unchanged original H1V2 interval DP** on all 15,401,392 candidate events using stricter qualifying labels found many more nonoverlapping winners:

| Dukascopy month | R9 SYNTH count | Monthly 80% floor | FAST3S / net >=$0.10 / spread <=$1.00 | FAST5S / net >=$0.20 / spread <=$1.00 |
|---|---:|---:|---:|---:|
| Jan | 27,980 | 22,384 | 67,124 | 58,237 |
| Feb | 33,523 | 26,819 | 57,710 | 53,066 |
| Jun | 31,801 | 25,441 | 77,943 | 66,108 |
| Jul | 24,382 | 19,506 | 38,682 | 33,685 |
| **Four-month total** | **117,686** | **94,150** | **241,459** | **211,096** |

- The FAST3S original-schedule-filtered subset was 154,560; direct strict DP added **86,899** strictly qualifying, nonoverlapping *hindsight* opportunities.
- The FAST5S/N20 subset was 151,467; direct strict DP added **59,629**.
- This optimizes count among *known future-winning intervals*, not a causal classifier. The interval DP can exploit all future tick paths and all possible entry times and sides. Every selected entry is known correct by construction. Calling its 100% oracle hit rate “predictive accuracy” or its summed net “tradable profit” is prohibited.
- Target entry count means >=80% the R9 SYNTH **count** every month. It is not 80% matching the original R9 timestamps or a common-broker execution comparison; selected opportunities are Dukascopy, historical R9 SYNTH comparator is a different feed.
- The stronger first-hit + final-net gates are tested under nominal original bid/ask + $0.02 fee and no additional slippage. **They do not establish first-hit robustness to unmodeled latency/slippage**.

## Validation

- Four original raw SHA256 pins checked before strict DP, complete 4-month quote chronology preserved.
- **All 452,555 strict re-optimized selected quote-ordinal traces** across the two rule families reconciled to original H1V2 frozen `code==1`, same side, same entry index, exact same exit index, first-favorable millisecond, and realized source-exact R9 net. Retained exact entry/exit bid/ask quotes and verified nonoverlap on each selected family; original R9 simulator was not changed.
- **15/15** original + new unit/source-invariant tests passed (`PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src pytest -q /mnt/data/h1v2/tests/test_h1v2_teacher.py /mnt/data/h1v2/tests/test_h1v2_geometry.py /mnt/data/h1v2_r2/tests/test_h1v2_r2.py`).
- Full new R2 source and result artifacts SHA256 included in ZIP manifest. Four `*_DP_REOPTIMIZED_RECEIPT.json` pin exact selected trace SHA256 values; complete original H1V2 oracle label arrays *not* redundantly archived (available locally or reproducible from pinned raw archives using original source).
- **No forward policy, MT5 build, broker slippage stress, frozen on-policy month replay, or trade PnL certification.**

## Safe continuation on repeated prompts

1. Read **this entire audit**, `SOURCE_EXACT_SHA256_MANIFEST.json`, all R2 source modules, four DP receipts, and predecessor H1V2 original complete dependency kit, **not chat summaries**.
2. Verify hashes and ZIP CRC; verify new GitHub branch ancestry. Do not overwrite original H1V2 or v2/R9 source files, do not rerun completed negative tests absent explicit new hypothesis.
3. Next priority **not** increasing the oracle count by more future-privileged scoring alone. Develop an actually discriminatory causal side-specific feature from new quote-event sequences; evaluate July absent training and robust chronological windows, then compare full exact-tick on-policy entry count to R9 SYNTH monthly floors. A qualified learner must pass both accuracy and volume and genuine execution economics simultaneously. Never confuse observed training-set precision with unseen precision.
4. Per hypothesis use: propose mechanism -> causal availability proof -> adversarial unit test -> train/fit -> residual wrong vs neutral taxonomy -> month-by-month failure audit -> checkpoint -> rollback if regression.

**Research classification:** `HINDSIGHT_QUALITY_ORACLE_SUPPLY_PASS / TRAINING_RESUBSTITUTION_EXTREME_SKEW / CROSS_MONTH_FORESIGHT_FAIL / DEPLOYMENT_PROHIBITED`.
