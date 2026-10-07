# GAMMA-02 — NY State-Signature Portfolio 001

**Status:** MAJOR JANUARY DISCOVERY FRONTIER — CONTINUOUS CHRONOLOGY  
**Predecessor:** GAMMA_02_NY_PHASE_SPECIALIST_PORTFOLIO_001.md  
**August:** SEALED

## Discovery

The broad HTF-permission relaxation was decomposed by exact completed-bar state tuple:

`(H4, H1, M15, M5, trade direction)`

January shows strong NY phase/state asymmetry. This is discovery, not yet a cross-month structural claim.

### 16 UTC permitted signatures
- (-1,-1,-1,-1,-1): fully aligned short
- (+1,+1,+1,-1,+1): HTF/M15 long with M5 pullback
- (+1,+1,-1,+1,+1): HTF long with M15 counterphase and M5 reclaim

### 17 UTC permitted signatures
- (-1,-1,-1,-1,-1): fully aligned short
- (+1,+1,-1,-1,+1): HTF long while M15/M5 are both in pullback

### 18 UTC permitted signature
- (-1,-1,-1,-1,-1): fully aligned short only

## Fixed specialist lifecycles for this frontier

16 UTC:
- $0.05 favorable-extension step
- TP $12 / SL $12 / 300s max hold

17 UTC:
- $0.10 step
- TP $40 / SL $8 / 300s max hold

18 UTC:
- $0.05 step
- TP $4 / SL $4 / 15s max hold

## One shared global-cap replay

| Cap | Net | Trades | PF | Exp/trade | Realized DD |
|---:|---:|---:|---:|---:|---:|
| 8 | +$2,779.47 | 2,005 | 1.547 | +$1.386 | $400.50 |
| 16 | +$5,555.91 | 3,813 | 1.582 | +$1.457 | $797.41 |
| 24 | +$8,448.69 | 5,445 | 1.628 | +$1.552 | $1,192.32 |
| 32 | **+$11,305.37** | **6,977** | **1.658** | **+$1.620** | $1,587.46 |
| 48 | **+$16,423.59** | 9,859 | 1.675 | +$1.666 | $2,380.69 |
| 64 | **+$21,074.67** | **12,355** | **1.688** | **+$1.706** | $3,175.42 |
| 96 | **+$28,147.47** | 16,378 | 1.673 | +$1.719 | $5,042.00 |
| 128 | **+$33,611.39** | 18,669 | **1.690** | **+$1.800** | $6,605.27 |
| 160 | **+$37,787.95** | **20,345** | 1.682 | **+$1.857** | $8,350.16 |

For context, canonical R9 SYNTH expected payoff is about +$1.409/trade. This January discovery frontier exceeds that expectancy while still producing thousands to tens of thousands of trades, although PF and win rate remain far below the SYNTH ceiling.

Higher caps are explicit research exposure frontiers, not low-capital deployment recommendations.

## Interpretation

This is the strongest corrected GAMMA-02 quality/velocity bridge so far.

It demonstrates that:
1. broad M1 density alone is insufficient;
2. session phase + exact HTF transition state materially changes the economics;
3. the opportunity engine can trade at high frequency without relying on raw 5-10 second direction prediction;
4. specialist handoff can raise expectancy above the R9-SYNTH reference expectancy even before later lifecycle/risk specialists;
5. January direction asymmetry must be challenged chronologically before promotion.

## Exact artifact

Library:
`.../m1-density/gamma02_ny_state_signature_portfolio_001.json`

SHA-256:
`72ee89cf8abc284e8ba9f00d64687937bd3e7eb3384470ec49dabe26265611b7`

## Next unit

`GAMMA_02_STATE_SIGNATURE_LIFECYCLE_REFINEMENT_001`

- map 16/17 runner horizons beyond 300s;
- refine TP/SL by signature class;
- retain 18 UTC fast lifecycle;
- then integrate with the previously earned STMR parent/shadow foundation;
- exact tick-level equity-DD certification before any MQL5 build.

R9 SYNTH remains the hard target.
