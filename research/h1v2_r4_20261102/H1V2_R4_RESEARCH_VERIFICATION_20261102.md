# H1V2 R4 — Four-month ordered quote mark and strict asymmetric rejection research

**2026-11-02 — Final research status: intentional overfit confirms high in-sample memorization; July-withheld transfer fails; no eligible execution policy.**

## Source-exact dependency chain

- Repaired R9 v2 baseline Git SHA `997dfdbd06157faa426c143874ad84277971570e`. Original source engine and exits **not modified**.
- Original H1V2 Git SHA `edce573d9c53b743dc5de1b0d741c81370af52c1`; original teacher on four Dukascopy source months: 513,262 selected future-privileged wins, explicitly not tradable.
- R2 parent Git SHA `0a6f860bf2b3e265922af55bd2547e4970037101`. Original strict rapid-hindsight nonoverlapping FAST3S/NET10/SPREAD100 reference = 241,459. All counts future privileged.
- R3 112 finely binned session/regime trend grid configurations had failed leave-self-out and July-withheld; the signed true-path and quote rates used here come from its exact-source, as-of 15k monthly feature matrices.
- R4 separate branch: `carson/h1v2-r4-ordered-marks-hawkes-skew-20261102`. Created from frozen R2 parent. New R4 source is additive only; prior files preserved.
- Raw gzip SHA-256 original Dukascopy month pins checked January, February, June, July; original candidate ordinals `ix` and millisecond timestamps joined exactly to all source derived arrays.
- Dataset per month 15,000 independently sampled as-of candidate timestamps, each independently labeled BUY and SELL as R2 WRONG/NEUTRAL/WEAK_GOOD/STRONG_GOOD. **This is a 60k timestamp sample, NOT the exhaustive 15.4M event universe.**

## New untried vs R2/R3 mechanism families

1. **M1:** Six observable quote revision marks (bid up/down, ask up/down, both up/down) in original time and row order, including simultaneous millisecond ordering and abstention on mixed revisions. Not actual executed order/book volume.
2. **M2:** Multi-horizon marked-event count/intensity 250ms,1s,5s,15s,30s and exponential excitation **basis** 250ms,1s,5s; this is not a fitted multivariate Hawkes intensity model, only observed past explanatory covariates.
3. **M3:** Full 6x6 ordered mark transitions 5s, three latest marks, event-run dynamics, signed bid/ask quote revision asymmetry, and raw event count; no future tick leakage.
4. **M4:** Four-class action-conditional competing consequence head: 4-class LightGBM trained on BUY and SELL independently (shared parameters with direction indicator). Neyman–Pearson-style constrained selective gate: choose side by strong-probability minus 1.5x wrong-probability minus 0.3x neutral-probability, otherwise WAIT. Policy needs Wilson 95% lower-bound >=80%, 150+ June calibrator actions; failed.
5. **M5:** Hierarchical Dirichlet empirical-Bayes posterior shrinkage side x session x spread x signed quote event flow x 5m true trend; coarse and fine motifs; smoothing 20 and 100 observations. Tried with all-four contaminated scores and July withheld independently.
6. **M6:** Model ablation baseline causal original geometry+true signed path, plus quote mark counts, plus full order/decay; same exact 15k July tuples, controlled 120 rounds. Full-order model did NOT improve strict withheld accuracy.

## 3s strong teacher definition and evidence boundary

STRONG_GOOD requires independently checked exact original BUY or SELL R9 quote-side exit, first favorable >=$0.10 net ahead of adverse -$0.10, first favorable <=3000ms, exit net >=$0.10, and spread <=$1.00. The other R2 labels: WRONG, NEUTRAL, WEAK_GOOD. Original R9 hard stop, trail and exit, fee remain pinned. Do not use hindsight price/net/first_ms labels as model input.

## Strict July-withheld top-ranked outcomes (train Jan+Feb+Jun)

| Frozen causal features | 150 top-ranked July entries | STRONG_GOOD | WRONG | NEUTRAL | WEAK | Strict correctness |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 150 | 4 | 126 | 16 | 4 | 2.67% |
| counts | 150 | 0 | 125 | 21 | 4 | 0.00% |
| ordered | 150 | 2 | 125 | 15 | 8 | 1.33% |

Held-out selected outcomes are **not** nonoverlapping source-simulator trades; the figures are action-label diagnostics only. Strict admission requires much more than selecting a top-ranked row.

## January/February fit — June qualification; July untouched

- June calibrated 95% Wilson lower >=80% at n>=150: **False**; maximum reported top-bin Wilson lower **5.68%**.
- Threshold: **None**. Frozen July entries admitted: **0**. No authorized classifier or trading policy.

## Intentionally overfitted four-month teacher (label contamination disclosed)

| Training and scoring month | Top 1% selected | Strong | Wrong | Strict precision |
|---|---:|---:|---:|---:|
| 01 | 150 | 150 | 0 | 100.0% |
| 02 | 150 | 150 | 0 | 100.0% |
| 06 | 150 | 150 | 0 | 100.0% |
| 07 | 150 | 150 | 0 | 100.0% |

This 100% top-1% resubstitution is contamination / memorization: the fitted model is tested on its own labels. The 600 selected sampled timestamps do not establish the 94,150 full-market monthly-volume target or remotely indicate forward predictions.

## Empirical Bayesian rejection diagnostic

| Feature motif | Prior support | Fit months | July top 1% strong | July max posterior P(strong) |
|---|---:|---|---:|---:|
| coarse | 20 | Jan/Feb/Jun | 0.67% | 6.36% |
| coarse | 100 | Jan/Feb/Jun | 0.67% | 6.19% |
| fine | 20 | Jan/Feb/Jun | 0.67% | 8.72% |
| fine | 100 | Jan/Feb/Jun | 1.33% | 6.88% |

The smoothed independent class posterior never approaches an 80% conditional strong label threshold; high-confidence rejection is the correct response. Sophisticated priors do not manufacture missing information.

## Audits and precise scope

- 29/29 combined original H1V2+R2+R3+R4 tests passed, including exact same-ms ordinal prefix invariance, six mark classes, Markov transition order-change detection, 4-class posterior training-exclusion and strict Wilson bound tests.
- Four-month original raw gzip SHA pins independently verified; each novel 15k-row 92-column mark atlas stored, SHA receipts below. Existing exact-exit validation from H1V2/R2 retained, not rerun in R4.
- Original tick exit mechanism was never modified; model trial not translated into MQL5, no Coinexx out-of-sample domain, no latency/slippage/margin / nonoverlap on-policy replay.
- Experimental external academic context: Oxford JFE 2024 order-book-dependent Hawkes, and 2026 journal research on multivariate Hawkes with limit order book data. These use **order book** events, which are NOT available in Dukascopy best Bid/Ask feed; our quote revision marks are not market-order flow. No fitted Hawkes claim.

## Next distinct scientific hypothesis (do not repeat past failed G1-G14 grid or this R4 model)

Implement a **properly fitted** six-mark self/cross excitation likelihood, with out-of-sample quote mark arrival prediction and a time-order shuffled control; test whether fitted excitations improve directional strong-vs-wrong discrimination at shared as-of event timestamp before adding any policy. Also test competing risk first-hit-to-positive vs first-hit-to-adverse with real 0.25/1/3/5s elapsed source labels, dropout detection, domain robustness and strict nonoverlap replay only after qualifying. Never confuse future-selected oracle supply and real policy action volumes.

## Full reproducibility

Restoration: original H1V2 complete dependency ZIP, R2 full ZIP, R3 multigrid ZIP and R4 full ZIP; preserve these original independent artifacts without overwriting. R4 code expects R2 and R3 matrices in original directory layout or source-tracked equivalents. Rebuild mark atlas from original raw gzip using:
```bash
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/extract_marked_atlas.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/finish_competing_risks.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src python /mnt/data/h1v2_r4/src/bayesian_quote_abstention.py
PYTHONPATH=/mnt/data/h1v2/src:/mnt/data/h1v2_r2/src:/mnt/data/h1v2_r3/src:/mnt/data/h1v2_r4/src pytest -q /mnt/data/h1v2/tests /mnt/data/h1v2_r2/tests /mnt/data/h1v2_r3/tests /mnt/data/h1v2_r4/tests
```

Status: **R4_HINDSIGHT_RESUB_100_PERCENT_AT_TOP1 / R4_CROSS_MONTH_DIRECTIONAL_STRICT_FAIL / R4_CAUSAL_APPROVAL_NONE**.
