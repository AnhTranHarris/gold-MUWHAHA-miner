# R9 Coinexx Research Acceptance Rule — 2026-11-13

## Owner-directed hard gate (new studies; do not rewrite earlier receipts)
- **ROC-AUC < 0.75 = FAIL** for the specified, preregistered prediction target and entire untouched chronological evaluation population.
- **ROC-AUC >= 0.75 to <= 0.80 = RESEARCH ONLY, NOT TARGET ACHIEVED**.
- **ROC-AUC > 0.80 = DISCRIMINATION TARGET** only if reproducible on independently unseen full Coinexx months. A high AUC alone never authorizes trading.
- Maintain independent hard gates for after-cost executable quote-side expected P&L, drawdown, active trading days, and trade volume. Never improve AUC by silently narrowing its label universe, dropping neutral/censored cases, picking retrospectively favorable sessions, or tuning on a held-out month.
- Report AUC per full held-out month, pooled out-of-sample AUC, class balance, confidence intervals using day-block bootstrap, precision/recall and cost/volume frontier, and base rate. If a conditional subset is scored, report its coverage and also overall decision-universe result.
- Use only as-of inputs. Train/validation/test splits are ordered and purged by **actual event end time**, not entry timestamp alone; overlapping labels require concurrency treatment. Fit preprocessing on train only. Preserve original row order, duplicate/equal-ms quote events and source SHA.
- Explicitly separate prediction families: (1) independent BUY or SELL first-favorable-versus-first-adverse within a stated 1/3/5/10/15/30-second horizon, (2) directional future movement, and (3) R9 policy-specific trade results. Do not compare AUC across differing labels as evidence of a better model.
- The January–September 2026 samples and September P5 results have been examined by researchers; **fresh later Coinexx data** is required for final unexposed confirmation. Historical nine-month walk-forward checks are development evidence, not a newly untouched final holdout.
- All previous R9 P1 five-pass models with AUC 0.52665–0.53858 remain frozen FAILED research, without posthoc relabeling.
- Keep the source-exact Python chronological engine unchanged unless a separately verified execution bug requires a targeted, versioned repair. Research remains shadow-only; no EA change or demo/live promotion.

## Evaluated public-source candidates; permissions apply to each upstream repository
1. [aeon](https://github.com/aeon-toolkit/aeon) — BSD-3-Clause; MiniRocket, MultiRocket, Hydra, InceptionTime; first copy-ready sequence baseline with causal Bid/Ask paths, no invented LOB depth.
2. [mlfinpy](https://github.com/baobach/mlfinpy) — MIT; triple-barrier and meta-labeling, sample uniqueness. Adapt executable Bid/Ask first passage: do NOT directly use close-to-close implementation as an execution-price oracle.
3. [tsai](https://github.com/timeseriesAI/tsai) — Apache-2.0; InceptionTime, temporal and attention architectures; secondary stage after a validated sequence baseline.
4. [tsfresh](https://github.com/blue-yonder/tsfresh) — MIT; automated feature discovery on irregular tick sequences, but time-agnostic calculators require caution; selection on train only.

## Papers / practitioner guidance
- Zhang et al., *DeepLOB* (2018): https://arxiv.org/abs/1808.03668 — reported FI-2010 benchmark classification ACCURACY, not XAUUSD ROC-AUC, using 10-level exchange LOB unavailable from Coinexx quotes.
- Briola et al., *Deep Limit Order Book Forecasting* (2024): https://arxiv.org/abs/2403.09267 — forecast accuracy need not imply executable opportunities.
- Community HFT net-cost warning: https://www.reddit.com/r/quant/comments/1b244r1/
- Community data-leak warning: https://www.reddit.com/r/algorithmictrading/comments/1tl3fak/
- [FinancialComputingUCL/LOBFrame](https://github.com/FinancialComputingUCL/LOBFrame) is CC BY-NC-ND 4.0: **reference only, do not copy for commercial EA**.
- [angus924/minirocket](https://github.com/angus924/minirocket) is GPL-3.0: prefer aeon's BSD-licensed implementation.
- Check LICENSE notices on any additional copied source; retain copyright/notices and record upstream commit hashes in the resulting integration.

## Action
No model has yet demonstrated >0.80 AUC on this Coinexx task. Begin source-exact event-label and leakage audit, then compare aeon MiniRocket/MultiRocket/Hydra using identical frozen labels and chronological folds. Do not proceed by tuning historical P1 model thresholds toward a desired AUC.
