# BETA 006 — Coinexx Real-Tick Winner → Cumulative EA Baseline Promotion

**Independent lineage:** `AnhTranHarris/gold-MUWHAHA-miner` / `beta`  
**Type:** Owner-issued promotion governance, not a strategy result or MT5 certification.  
**Effective:** 2026-09-28. Supplements BETA 000–005; preserves the BETA 003 human gates and BETA 004 scientific gates.

## 1. Governing rule

A **candidate** that (a) succeeds in the causal January–July Dukascopy **raw-tick Python** research campaign, (b) receives explicit **owner authorization before MQL5 coding**, and (c) passes the **owner-run Coinexx MT5 XAUUSD M1 Strategy Tester using “Every tick based on real ticks”** with **similar or better economically meaningful results** relative to the candidate’s Dukascopy Python benchmark **may become the next approved cumulative BETA EA baseline, but only after explicit owner acceptance**. Neither Python promise nor MT5 pass automatically promotes a candidate.

**The key cumulative rule:** the *immediately preceding owner-approved MT5 EA* is the frozen incumbent; after owner acceptance of a new candidate, the accepted candidate becomes the sole **next baseline/parent** for future candidates. All future proposed ENTRY, HOLD, EXIT or PROFIT mechanisms must show incremental value over that newest parent. Do not restart from an R9, Alpha or Gamma EA. Preserve previous approved versions for rollback.

The **first** owner-approved BETA EA establishes `BETA_BASELINE_001`, even though there is no approved predecessor. A percentage gain over a nonexistent parent must never be invented. Thereafter use `BETA_BASELINE_002`, etc. Formal research breakthroughs still use owner-specified `R09_BETA_<order>_<breakthrough-name>` IDs and dedicated public white papers. The baseline ID records approval lineage; it is not a new strategy name.

## 2. Preregister what “similar or better” means

The two feeds are independent: **Dukascopy ticks in Python vs Coinexx broker real ticks in MT5**. Their tick paths, spreads, swaps, commissions, fills, leverage, stop levels and margin conventions can differ. Therefore do not demand tick-by-tick trade identity or declare identical experiments from equal headline P&L. Before the MT5 run, the candidate’s compact review manifest must **freeze**:

- Exact strategy commit/build and `.set` inputs, XAUUSD specification, lots/sizing, account deposit/currency, test **dates and timezone mapping**, fee/spread/slippage assumptions, and any day-boundary settings.
- Candidate’s January–July Dukascopy **monthly and total** net P&L, gross profit, **gross loss**, maximum equity/balance drawdown (type declared), trade count, profit factor, average trade, and volatility/risk measures; full chronological account and boundary-state integrity.
- **Explicit, numeric acceptance tolerances** for Python↔MT5 similarity across meaningful economics: at minimum total and monthly net, gross loss, max drawdown, trades retained, and any critical tail/small-account risk constraints. Tolerances must be set *before* reading MT5 results, not retrospectively to pass a favored EA.
- Threshold interpretation when metrics are zero/negative or ratios are unstable: assess signed dollars and preregistered risk bounds, rather than a bogus percentage. Passing by merely reducing trades or hidden leverage is invalid.

**MT5 better than Python** on a headline metric does not excuse materially worse gross losses, drawdown, monthly fragility, broker survivability or violated risk constraints. **MT5 similar** means the predefined economic/risk tolerance vector is satisfied, not just a vague resemblance or profit figure. A candidate that loses money in both systems does not become a winning baseline merely because it repeats the loss. A winning candidate must meet its preregistered economically positive/meaningful goal and all safety constraints.

For **subsequent** candidates, also run the previous approved EA under **matching Coinexx MT5 settings and period**, so the incremental broker-native change can be assessed. The Python candidate-vs-current-parent comparison and the MT5 candidate-vs-current-parent comparison are **separate, same-feed** improvement tests; the cross-feed Python/MT5 comparison is an independent translation/robustness gate. If the parent's report is missing or conditions differ, label that comparison unverified and do not pretend it is proven.

## 3. Gate sequence and irreversible evidence

1. **Research candidate:** preregister KPI, category, recovery checkpoint and current approved parent; screen only using actually certified caches; fully retest finalists on exact chronological Jan–Jul Dukascopy ticks, with suitable forward, parameter and stress gates. >10% meaningful improvement vs the approved incumbent in a preregistered same-feed KPI is the normal candidate gate. For the first baseline, use an owner-agreed starting comparator and explicitly label no incumbent.
2. **Pre-code owner gate:** owner reviews the compact seven-month candidate results and explicitly authorizes *this* MQL5 implementation. Without approval, do not code an EA candidate.
3. **Versioned MQL5 candidate:** build cumulatively on the latest *approved* BETA EA; first baseline starts clean. Freeze full source, compile result, settings, parent SHA, Python SHA and manifest. Never silently import retired R9/Alpha/Gamma implementation.
4. **Owner-run Coinexx real-tick MT5 test:** XAUUSD, M1 chart/tester timeframe, **“Every tick based on real ticks”** model, aligned Jan–Jul windows, documented contract and conditions. The owner shares **only ordinary compact Strategy Tester reports and essential settings**. No raw MT5 tick logger/export is required. M1 is the tester display setting and does not change the EA’s intra-second tick processing requirements.
5. **Independent pass/fail evaluation:** examine frozen Python↔MT5 tolerances, positive/meaningful net economics, monthly results, gross loss, drawdown, trade velocity, tail/small-account behavior and, for later revisions, broker-native improvement vs previous MT5 baseline. Explain known cross-feed divergences without asserting exact fill parity. A failure stays a rejected/diagnostic candidate; approved prior baseline remains untouched.
6. **Final owner gate:** present MT5 and Python comparisons, explicit caveats, and candidate/parent revision identifiers. Promote **only on owner’s affirmative acceptance**; “test passed” is not the same as “owner accepted.” Record owner decision and timestamp.
7. **Atomic cumulative promotion:** save approved EA source and `.set`/input manifest, compact report and validation scorecard, key hashes and owner approval in GitHub `beta` and Google Drive. Set `approved_beta_ea` and `current_approved_baseline` only after both sides are read back and the owner acceptance is documented. Set `last_verified_durable_unit` only after verification. Tag/freeze incumbent for rollback. Then make the promoted EA the mandatory parent for the **next** candidate.

## 4. Rejected, partial, and first-baseline cases

- **Python works, MT5 deviates outside tolerances:** do not promote; investigate input/fee/timing differences and bounded execution reasons. Do not request large MT5 tick logs. Any materially changed EA is a new candidate requiring its own gates.
- **MT5 works but underperforms prior approved MT5 EA or materially worsens safety:** keep previous baseline unless the owner explicitly approves a separately justified trade-off under preregistered constraints. Never overwrite a known-good release automatically.
- **MT5 beats Python but fails risk or causality checks:** reject; better headline profit is insufficient.
- **Python/MT5 agree but both are weak or negative:** record consistency, not a winner.
- **First approved BETA EA:** preregister the initial comparator and positive-economic/risk acceptance thresholds; on owner approval it becomes `BETA_BASELINE_001` and establishes the parent against which subsequent >10% improvements are judged.
- **Unavailable Coinexx comparable month:** record missing evidence rather than manufacture a Python↔MT5 or parent↔candidate percentage.

## 5. Current state and non-regression

As of this protocol, **no BETA EA or candidate is accepted**, no full January–July strategy result is certified, and August remains **SEALED**. BETA 005’s last verified bounded source scan and **first incomplete January UTC-boundary source unit** must not be reset by writing this BETA 006 governance document. Keep Jan–Mar, Apr–Jun and Jul as execution/checkpoint spans, not assumed statistical holdout boundaries. BETA 004 durable-science and BETA 003 manual MT5-approval conditions remain in force.

**Reference documents:** `research/BETA_004_DURABLE_QUANT_CAMPAIGN_PROTOCOL.md`, `research/BETA_005_MULTI_SPECIALIST_ARCHITECTURE_HYPOTHESIS.md`, `beta/CURRENT_STATE.json`, and the original BETA 003 Drive protocol. Large raw tick sources remain read-only and outside GitHub.
