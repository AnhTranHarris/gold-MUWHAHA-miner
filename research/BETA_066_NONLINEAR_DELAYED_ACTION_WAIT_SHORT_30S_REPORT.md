# BETA066 — Nonlinear Delayed-Action / WAIT_SHORT 30-second Study

**Date:** 2026-10-01  
**Lineage:** independent BETA  
**Scientific parent:** BETA063  
**Research input:** exact durable BETA065 RIGHT-edge proposal surface  
**Status:** COMPLETED DURABLE NULL / CLOCK SURFACE DEMOTED  
**August 2026:** SEALED / NOT READ  
**MQL5:** NOT AUTHORIZED

## Purpose

BETA065 showed that its three RIGHT-edge clocks had substantial 30-second hindsight movement capacity but no positive causal linear action-value policy on CAL. BETA066 tested two direct corrections without weakening the no-trade gate: (1) bounded nonlinear models, and (2) explicit delayed stopping actions rather than treating WAIT as a synonym for SKIP.

## Frozen executable action space

At each of the **371,013** BETA065 proposals, the model could choose LONG/SHORT immediately, commit to LONG/SHORT after 250 ms, 1 s, or 3 s, or SKIP. A delayed action enters on the first actual quote at/after the fixed delay and exits on the first actual quote at/after **entry +30 seconds**. BUY enters Ask / exits Bid; SELL enters Bid / exits Ask; $0.02 round-trip research fee is included. Inference sees only the 28 BETA065 RIGHT-edge features at the original proposal time.

## Split discipline

- FIT: Jan 1–Jan 9 — fitting only.
- CAL: Jan 9–Jan 11 — model/config/q-threshold selection only.
- DIAGNOSTIC: Jan 11–Jan 18 12:00 UTC wall — never used for selection. Available market quotes in the bounded source end Jan 16 21:59:59 UTC.
- August remained sealed.

## Models tested

Preregistered bounded grid:

1. `HGB_D3_L2_5` — shallow histogram gradient boosting.
2. `HGB_D4_L2_10` — moderately larger bounded histogram gradient boosting.
3. `EXTRA_D8_L150` — bounded Extra Trees regression.

Thresholds were fixed at $0.00 / $0.05 / $0.10 / $0.15 predicted after-cost value. A CAL candidate required >=100 completed one-position trades, positive net, PF >1, and positive mean trade.

## Core result

**No configuration passed the CAL gate.** The correct frozen policy remains **SKIP_ALL**.

The best active (non-zero-trade) CAL attempt was `HGB_D3_L2_5` at $0.05: 11 trades, 3 wins, net **-$12.071**, PF **0.336**, average **-$1.097/trade**.

`EXTRA_D8_L150` predicted no action above the $0 threshold on CAL and therefore reduced to no-trade. The active HGB predictions that crossed zero were sparse and materially loss-making.

## Important new information: delay has real hindsight capacity

| Split | Oracle now-only mean | Oracle all now/wait mean | Increment from delay options | Oracle all positive |
|---|---:|---:|---:|---:|
| FIT | $0.108 | $0.332 | $0.224 | 55.6% |
| CAL | $0.107 | $0.326 | $0.219 | 54.6% |
| DIAGNOSTIC | $0.249 | $0.486 | $0.237 | 61.7% |

On CAL, adding fixed wait choices raises hindsight best-action mean from about **$0.107 to $0.326 per proposal**. The most frequently best actions are often the 3-second delayed variants. This is **not** a tradable result; it identifies a timing/phase information problem.

## Why BETA066 is rejected

The failure is no longer explained by insufficient action diversity or a linear-only model. Nonlinear trees/boosting still cannot infer the profitable side/delay from the existing BETA065 feature surface. The evidence therefore supports the preregistered failure rule: **demote the BETA065 three-clock + 28-feature surface as an entry architecture**. Do not relax q thresholds or minimum trade count.

## Next research direction

The next unit should be materially different rather than another threshold/model-size sweep. Priority is a **causal state-enrichment + hurdle/actionability architecture** using only observable RIGHT-edge state:

- time/session phase and second-of-minute;
- trailing spread rank/percentile and spread compression/release;
- same-specialist/opposite-specialist event age and retrigger density;
- quote-pressure divergence and acceleration;
- explicit clock phase / state age / distance-to-boundary;
- first-stage `ACTIONABLE vs NO-TRADE` probability, followed by direction/delay selection only when actionability clears a cost-aware gate.

This directly targets the information missing from BETA065/066 instead of adding more confirmations.

## Methodological/public implementation anchors

- Transaction-cost optimal timing/no-trade region: https://www.sciencedirect.com/science/article/pii/S0305048301000603
- MQL5 BUY/SELL/WAIT gradient-boosting example: https://www.mql5.com/en/articles/18985
- MetaQuotes ONNX reference: https://www.mql5.com/en/docs/onnx

These are methodological/implementation references only; they do not validate XAUUSD profitability.

## QA and disposition

Independent BETA066 QA: **33/33 PASS**. Checks include source/proposal hashes, exact BETA065 proposal identity, executable source-ordinal/searchsorted identity, delayed entry monotonicity, entry+30s exit semantics, direct quote-side label fixtures, model/prediction shapes, diagnostic exclusion from selection, all active CAL candidates non-positive, SKIP_ALL disposition, and August sealed.

**Promotion:** REJECTED.  
**Rollback/scientific parent:** BETA063.  
**BETA065/066 surfaces:** retain as durable negative evidence and feature-engineering diagnostics; do not promote them as parents of MT5 logic.
