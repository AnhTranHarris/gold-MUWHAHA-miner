# BETA066 — Nonlinear Delayed-Action / WAIT_SHORT 30-second Study

**Date:** 2026-10-01  
**Lineage:** independent BETA  
**Scientific parent:** BETA063  
**Research input:** exact durable BETA065 RIGHT-edge proposal surface  
**Status:** PREREGISTERED / NOT YET TESTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

BETA065 established that the proposal clocks contain 30-second hindsight movement capacity but its linear causal models cannot identify a positive executable action on CAL. BETA066 tests whether bounded nonlinear interactions can discriminate side and whether **delaying entry itself** has causal option value after spread.

## Frozen action space

At each BETA065 proposal, inference sees only the 28 BETA065 RIGHT-edge features available at that proposal. It may choose:

- LONG now / SHORT now;
- wait 250 ms, then enter a preselected LONG or SHORT at the first observed quote at/after the delay;
- wait 1 s, then enter a preselected LONG or SHORT;
- wait 3 s, then enter a preselected LONG or SHORT;
- SKIP.

All entered actions exit at the first observed source quote at/after entry +30 seconds. BUY enters Ask and exits Bid; SELL enters Bid and exits Ask. Add $0.02 round-trip research fee. No future state is visible to inference.

This makes WAIT operational rather than rhetorical: it is an explicit delayed stopping action with a known side and delay.

## Split discipline

FIT Jan1-Jan9: model fitting only.  
CAL Jan9-Jan11: select model family/configuration and q-threshold only.  
DIAGNOSTIC Jan11-Jan18 12UTC: one frozen read after selection; never used to choose features, model, delay or threshold.

## Nonlinear model grid

1. HGB_D3_L2_5 — shallow histogram gradient boosting.
2. HGB_D4_L2_10 — slightly larger bounded boosting.
3. EXTRA_D8_L150 — bounded Extra Trees ensemble.

No AutoML, no unbounded parameter search, no diagnostic-driven tuning.

## Economic gate

Thresholds: $0.00, $0.05, $0.10, $0.15 predicted after-cost value. CAL candidate must have at least 100 one-position completed trades, positive net, PF >1, and positive average trade. Selection priority is CAL net subject to those safeguards; ties prefer fewer model degrees of freedom and lower turnover.

Because BETA065 selected zero trades, percentage improvement versus its selected ledger is undefined. A BETA066 success therefore requires **absolute positive CAL economics first**. Any candidate that survives CAL is then frozen and read once on DIAGNOSTIC. Formal BETA063 comparable-window improvement remains required before any later promotion claim.

## Failure rule

If no preregistered nonlinear/delay configuration produces positive guarded CAL economics, demote the three BETA065 clocks as insufficient for this feature surface. Do not lower the economic gate and do not inspect August.

## Research anchors

The methodological motivation is transaction-cost no-trade/inaction regions and explicit BUY/SELL/WAIT modeling. MQL5 supports ONNX inference, and public MQL5 examples use gradient boosting and BUY/SELL/WAIT classifiers; these are implementation/research anchors, not evidence that the model is profitable on XAUUSD.

## Durability

BETA GOV-001 applies. Exact labels, predictions, winning model/config, selected ledger, source/QA and hashes must be persisted before this unit may be called durable.
