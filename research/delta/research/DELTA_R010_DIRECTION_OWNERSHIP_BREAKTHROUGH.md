# DELTA R010 — Directional Adverse-Selection / Overextension Ownership Breakthrough

**Status:** BREAKTHROUGH REFINEMENT CANDIDATE — NOT PROMOTED / NOT LOCKED  
**Parent:** `DELTA_004_COINEXX_LIKE_DUKASCOPY_RESEARCH_SURFACE`  
**Scope:** ENTRY + INITIAL-HOLD  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Canonical v0 mechanism

At an R9 entry-eligible event, before fill:

```
I250 = signed Bid/Ask impulse over prior 250 ms, oriented to the R9 intended side

H1NetATR =
    signed net displacement across the last 3 completed H1 bars
    / completed H1 ATR(14),
    oriented to the R9 intended side

OWNERSHIP_TRANSFER =
    I250 <= -0.55
    OR H1NetATR > 0.35
```

If false:
- keep R9 side;
- keep ordinary R9 lifecycle.

If true:
- ownership transfers to a reversal branch;
- flip entry side;
- after the owned trade exits, suppress generic opposite-side same-minute R9 rearm;
- reset ownership at the next M1 boundary.

No future bars or future ticks are used.

## Stage-A modeled-surface results

### P50
Control net -$3,504.86.  
R010 net -$2,778.01.  
Net/DD improvement ~20.74%.  
GL improvement ~17.23%.  
Trade retention ~87.04%.  
Winner retention ~91.95%.

### P75
Control:
- 16,801 trades
- 7,351 winners
- GL -$5,343.02
- net -$3,768.25
- DD $3,769.83

R010:
- 14,582 trades
- 6,803 winners
- WR 46.65%
- GP +$1,426.64
- GL -$4,393.28
- net -$2,966.64
- DD $2,967.63

Relative:
- trade retention ~86.79%
- winner retention ~92.53%
- net-loss improvement ~21.27%
- GL improvement ~17.78%
- DD improvement ~21.28%

All 13 active Stage-A trading days improved net. All four session buckets improved net.

### P90
Net/DD improvement ~20.9%.  
GL improvement ~19.0%.  
Trade retention ~84.05%.  
Winner retention ~87.93%.

### Native spread
Control has only 91 trades because the existing R9 25-point spread gate rejects almost the entire native Dukascopy surface.

R010 worsens those sparse native results:
- control net -$28.424
- R010 net -$39.08

This required failing sensitivity remains a promotion blocker.

## Robustness

Threshold surface:
- micro thresholds -0.65, -0.55, -0.45
- H1 thresholds 0.30, 0.35, 0.45, 0.60
- P50/P75/P90

Every tested combination improved modeled-surface net/DD roughly 17.5%–21.5%. H1 0.30–0.35 is the strongest robust region.

Horizon ablation:
- M15, M30, H1, H4
- 100, 250, 500, 1000 ms

H1 + 250 ms is strongest. M30/M15/H4 and other micro horizons are weaker.

Adding M30 to H1 slightly changes loss reduction but costs enough activity/winner retention that the simpler H1 rule is retained.

## Out-of-sample caution

A frozen predecessor rule:
`I250 <= -0.5505 OR H1NetATR > 0.4613`

was already replayed after discovery.

Later-January holdout:
- control net -$3,270.40
- predecessor net -$3,026.96
- improvement ~7.44%

A near-R010 threshold `-0.5505 / 0.35` on the same holdout improved net ~8.45%.

Frozen predecessor month-by-month P75:
- February ~10.46% net-loss improvement
- March ~11.94%
- April ~9.12%
- May ~15.87%
- June ~13.43%
- July ~9.46%

It remained better than R9 in every tested month, but the magnitude shrank materially versus Stage-A.

Therefore:
- the **mechanism** has encouraging temporal robustness;
- the Stage-A ~21% magnitude is optimistic;
- the rounded R010 rule is **not yet claimed as exact Jan–Jul validated**.

## DH-05 selective handoff test

A later experimental handoff from R010/R009 ownership to DH-05 generated only 0–3 actual handoffs in tested policies and changed net by at most roughly $0.52.

Decision: no incremental value from that handoff mapping; do not add complexity.

## Decision

R010 is the strongest structural breakthrough of the restart so far, but remains a refinement candidate.

No promotion.  
No metric lock.  
No MQL5.  
No August.

Next work:
1. exact rounded-R010 month-by-month validation;
2. bounded causal refinement seeking incremental improvement without destroying activity/winners;
3. do not reopen generic post-entry DH-06 action mapping;
4. keep DH-05/DH-02/DH-03 as conditional research branches rather than global filters.

## Provenance
- robustness: `121b5a8936cfa73a4ce96aff34e07b1823d30ce36a700877a3e4adb5bb8ae99e`
- threshold surface: `567067db8e5016158af6170bb4d68127be52ecb8b29bc955e9cee918b429e842`
- horizon ablation: `b3b5288c0d3d783fa979324a3a90fafe6c444029691dfbdd2d4fd84eea8ad4f5`
- dual horizon: `a7e505bd1c44ac51eaf5df45c25d3b93b457de83699413c5bb8aed6538a11524`
- January holdout: `de10d567a199641e270932c4158120afbb43acb2954ecd208d247aa2b03d51b0`
- holdout sensitivity: `86a1e1313d33a3f765a8b4097318b96f701f50cc6187cf9cbf3120ca4e397253`
- February predecessor validation: `debb335005bce37b3a1248d8073c8f495a3619319eba07ac7c66e10967367059`
- March: `61178e976c6f7ccc17111411db1b325d3a0dfa85cd9d1ba80f78f908446e2c47`
- April: `a08e18d1c7157766ae1067fc6b94aa73dcb73fd1a8bc315df050d73e7e1063d0`
- May: `183acfd63561343b9721c2e0524cb140c38982a09044bb1f2bd6aa8da19456d9`
- June: `8f62cd89a8c59e8892936ef27d1d0c29e69181c6f913d14454526b8c7f9c4dd8`
- July: `1686a4e5d2c49a1dafc35ba7b82350c2343ee7d0a659f3a885d052b637e437ae`
- DH-05 handoff: `128318115e3da27884f2283e9023113b3b4319c783cda6e48d569915f79f9575`

Drive:
https://docs.google.com/document/d/1pW14EDoo9muzFQyZy7IcP3ifvDBIbMkV3apRodiPXLM/edit
