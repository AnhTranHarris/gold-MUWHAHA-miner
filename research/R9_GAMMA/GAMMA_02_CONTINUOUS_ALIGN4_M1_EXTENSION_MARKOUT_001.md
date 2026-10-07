# GAMMA-02 — Continuous ALIGN4 M1 Extension Markout 001

**Status:** COMPLETE DIAGNOSTIC OPPORTUNITY MAP  
**Predecessor:** GAMMA_02_SLICE_CONTINUOUS_PARITY_001.md  
**Discovery:** January 2026 ordered Dukascopy Bid/Ask  
**August:** SEALED

Every causal $0.05 favorable M1 extension under strict completed-bar ALIGN4 permission was recorded from the continuous January stream. Entry is executable Ask for longs / Bid for shorts. Fixed-horizon markout exits use executable Bid/Ask and the existing $0.02 trade-cost convention.

Independent event markouts are diagnostic opportunity statistics, NOT simultaneously executable portfolio PnL.

## Major corrected correlation

New York decomposes into different lifecycle phases.

### 16 UTC NY
~24,182 events.
- 5s mean: -$0.0525/event
- 10s: +$0.0714
- 15s: +$0.0886
- 60s: +$0.0367
- 120s: **+$0.4290**
- 300s: **+$0.9918**

### 17 UTC NY
~23,454 events.
- 5s: -$0.0577
- 10s: -$0.0654
- 15s: -$0.0724
- 30s: +$0.0800
- 60s: **+$0.1953**
- 120s: **+$1.2665**
- 300s: **+$3.3426/event**, ~56.8% positive markout

### 18 UTC NY
~19,290 events.
- 5s: **+$0.2772**
- 10s: **+$0.1631**
- 15s: **+$0.3083**
- 30s: -$0.1788
- 60s: -$0.7549
- 120s: -$0.3823
- 300s: -$0.3368

The previously corrected NY18 displacement specialist also survives continuous chronology at +$2,159.08 / 1,081 trades / PF 2.1046.

## Interpretation

A universal short scalp lifecycle is rejected.

The corrected causal data support a phase-specialist handoff:
- **16-17 UTC:** trend accumulation / runner / favorable-direction pyramiding candidate.
- **18 UTC:** fast harvest / scalp candidate.

This is directly relevant to the owner's high-volume goal because the raw opportunity feed contains tens of thousands of favorable-extension events. The next unit must convert those independent opportunities into one executable capped portfolio with explicit aggregate exposure and drawdown.

## Next unit

`GAMMA_02_NY_PHASE_SPECIALIST_PORTFOLIO_001`

Test:
1. 16 UTC medium/long runners;
2. 17 UTC long runner-pyramids;
3. 18 UTC fast harvest;
4. global exposure caps and honest heat accounting;
5. no arithmetic summing of independent markouts.

Exact JSON is durable in Library:
`.../m1-density/gamma02_continuous_align4_markout_001.json`

SHA-256: `655806f09f30f8702f17aa67c7999666632f59bc1aa281a1f08ef623fa02882a`
