# F401-R96 — Source-exact dual-lab, 504D conditional-specialist falsification and bid/ask executable quote counterfactual

2026-10-28. **UNAPPROVED SCIENTIFIC RESEARCH. NOT A SUCCESS CLAIM.** Continue existing M-DK-01, 21/39 owner historical research approvals, all G01–G09 OPEN. No PRIMARY/MT5_EXPAND /02 edits. Frozen tick engine is **not rebuilt**. The honest result is a necessary strategic pivot away from reproducing static FILTER08 signal correctness toward changing actual entry/action conditions.

## Why this differs from incremental negative threshold experiments

Both original raw Dukascopy January and February L1 bid/ask quote tapes (9,135,062 and 7,538,339 quotes, respectively) and all original FILTER08 source events (344,037 Jan; 324,582 Feb) were read with original per-byte SHA pins and unchanged event t/side/three-class labels. The R96 **504-dimensional** first-stage is a *combined state model*, not a single technical indicator: 212 ordered L1 quote features from R95; 32 genuinely as-of previous outcome-memory variables (labels only available >=33.001s afterward); 48 forward-updated multi-decay quote-state variables; 50 explicit crossed state/posterior conditions; 162 features from fully closed 3/5/9-bar geometry at 5s,30s,M1,M5,M15,H1. Volume semantics: quote-arrival count only, never invented traded volume. Correct, opposite and neutral specialists trained separately with 127 leaves/64 rounds and explicit guarded routing. Chronological Jan first 60% FIT (51,604 deterministic sampled training events, embargo), next 20% CAL policy freeze, 80–90% VAL, 90–100% SHADOW, entire Feb exposed-only transfer. Jan CAL policies are not independent evidence; Jan VAL/Feb rows were never refitted or threshold-optimized. **12 predeclared policy variants, all reported, not cherry-picked.**

## Actual fixed-source model result

| Predeclared conditional policy | January VAL bad veto / right lost (34,404 events) | February exposed transfer bad veto / right lost (324,582 events) |
|---|---:|---:|
| q=.50 risk only | 8,586 / 10,226 | 74,221 / 57,502 |
| q=.50 risk + correct guardian | 2,171 / 2,251 | 39,319 / 25,903 |
| q=.70 risk + correct guardian | 1,623 / 1,671 | 22,854 / 15,467 |
| q=.85 risk + correct guardian | 985 / 1,016 | 10,647 / 7,342 |

The orthogonal risk+opposite/neutral cooperative override **added zero actual incremental vetoes** under the tested parameterization; do not claim working specialist synergy from a dormant branch. The teacher retrospective fitted Jan VAL was 7,769 bad / zero right lost and Feb 121,691 bad/27 right lost; cannot be called causal performance. R96 combined 504D does not converge to that reference. Retire its current same-t0 static voting action. No benchmark success, no new owner acceptance.

## Second independent Python environment — raw source bid/ask quote execution approximation

`f401_r96_bidask_quote_execution_lab.py` is deliberately a *small adapter* to original immutable source and does not replace the existing source-native research tick engine. It builds first available quote on/after t0+latency, buys at ASK / sells at BID and unwinds after 31 seconds at BID / ASK. It enforces one open order and zero-equity floor, computes price/oz from raw integer /1000, assumes 0.01 lot=1 oz and $0.20 round trip as **illustrative unverified** economics, tests $100/$200 starting capital × 0/250/1000ms separately per Dukascopy Jan/Feb. These are **NOT** the binding 12 whole-EA G09 scenarios, since the broker, exact fill, contract/margin, slippage, protective stops and R9 order-state join are unverified. Original fitted own-month teacher is included *only* as a retrospective diagnostic comparator, not a possible runtime decision.

Illustrative $100/no latency/NO FILTER at t0 +31s fixed exit: Jan reached <=0 after 60 admitted executions, Feb reached <=0 after 8, with huge source spreads; **NOT a tested production EA strategy**. Evaluating a meaningless one-position 31s entry is not a substitute for multi-horizon system evaluation. The trading research should avoid calling signal-label correctness a profit or using retroactive cancellation of original R9 orders. Complete both-month 12-scenario files preserve negative and positive counts.

## New research decision: replace binary event classification with an action/entry optimizer

This is a *change of formal research target*, not an assertion of edge: develop an **option-valued multi-action cooperative controller** at pre-OrderSend t0 with KEEP_NOW / PLACE_LIMIT_UNSENT / WAIT_FOR_SOURCE_QUOTE_RECONFIRM / REVOKE_NEVER_SENT / RESCUE_CORRECT, with per-session multi-regime structural specialists and separate uncertainty budget. The true hard constraints are verifiable original intent ID and pre-order causality, quote-native favorable-first/adverse-first/censored or never-filled competing hazards, executable entry spread, missed-correct opportunity, portfolio overlap/capital risk. Target the actual after-cost trade potential rather than asking a classifier to replicate own-month overfit labels. Preserve original three-class signal score and 39 objectives but make economic opportunity a distinct supervised target. **Original R94 proved existing R9 log and FILTER08 event times cannot be joined by guessed timestamps**. Without an authentic pre-OrderSend ID this cannot be claimed an R9-cancel mechanism; hypothetical new unsent-order policy must be transparently separated.

Success-first exploitation: preserve historically measured F234 parent, approved 21 objectives, and pre-submission R89/R82 controls (delayed-order shadows, not original R9 veto), and successful separate structural pullback evidence where exact source is retrieved. Reuse the healthy original backtest engine through adapters, not a rewrite. A high-volume, multi-horizon 2–4-minute specialist could overcome high entry spreads that poison a naive 31s market exit, but performance must be demonstrated rather than assumed. Differentiated future experiments should concern entry feasibility, trade-path option value, shared-capital action composition, and *incremental marginal wrong removed against the specific original predecessor*.

Research mechanism techniques: ant-research/EasyTemporalPointProcess (marked event state), online-ml/river (ADWIN online drift), havakv/pycox (competing risks), source-authorized methodology only. No external quote/orderbook feeds imported. GitHub method source URLs: https://github.com/ant-research/EasyTemporalPointProcess ; https://github.com/online-ml/river ; https://github.com/havakv/pycox . These are not measured XAUUSD wins.

## Laboratory reproducibility/causal scope

Two Python environment source scripts with exact source helper dependencies, 4 unit tests (all passed), original Jan/Feb quote simulator scenario JSON, source feature policy/count JSON, fitted experimental model files and full SHA manifest. Primary raw quote files and 51MB source FILTER08 original ZIP remain in their already verified original locations; not copied to preserve space. No compile, live/demo activation, or checkbox mutation. Original 15D F05 external ordered arrays, authentic R9 pre-OrderSend intent ID, unlocated F400 original ZIP remain separate source provenance blockers.

**Verdict: R96 FALSIFIED as a static-t0 correctedness veto. Retire that exact variant. Next justified research is an action-space / execution-conditional hypothesis using real bid/ask opportunity labels and independently verifiable intent provenance.**
