# R9B_Gamma_1_Toxicity_Ownership_Gate — Public Technical White Paper

## Status
- **Canonical breakthrough ID:** `R9B_Gamma_1_Toxicity_Ownership_Gate`
- **Promotion state:** FORMAL SPECIALIST BREAKTHROUGH
- **Role:** R9 high-frequency entry/toxicity loss-avoidance gate
- **Standalone EA status:** **NOT PROFITABLE / NOT AN MT5 REPLACEMENT**
- **Research period:** January–July 2026
- **Discovery:** January–March
- **Calibration:** April
- **Frozen forward:** May–July
- **August:** sealed

## 1. Executive Summary

`R9B_Gamma_1_Toxicity_Ownership_Gate` is a causal entry-ownership specialist that learns where original R9 entries are disproportionately toxic and converts those states into **ABSTAIN** rather than attempting to predict a new direction.

The breakthrough does not solve the complete R9 REAL→SYNTH problem. It solves one narrower but economically large component: **gross-loss financing of low-quality R9 opportunities**.

On the source-equivalent Jan–Jul exact chronology, the frozen gate changes:

- net: **-$43,693.01 → -$18,383.30**
- gross loss: **-$75,154.49 → -$34,985.24**
- max drawdown: **$43,694.85 → $18,385.75**
- profit factor: **0.4186 → 0.4745**
- trades: **236,374 → 105,358**
- net-loss reduction: **57.93%**
- gross-loss reduction: **53.45%**
- trade retention: **44.57%**
- full R9 REAL→SYNTH bridge closed: **7.04%**

The result is robust enough to qualify as a formal specialist breakthrough, but it remains negative and therefore must be paired with positive opportunity/action and lifecycle specialists rather than tightened into an ever-more-selective filter.

## 2. Problem Definition

R9 REAL does not fail because Gold lacks opportunities. Its largest failure is that many source-equivalent R9 triggers convert into short-lived adverse paths, producing a large gross-loss pool. Earlier clean pre-entry research showed that ordinary profitable-direction prediction was weak, while toxic-state and survival classification were materially stronger.

The research question was therefore changed from:

> “Can pre-entry state tell us BUY versus SELL?”

to:

> “Can pre-entry state tell us when the existing R9 opportunity should not be financed at all?”

## 3. Discovery History

The path to this mechanism was:

1. R9 REAL↔SYNTH forensics showed high similarity in outer opportunity structure but severe divergence in post-entry path ordering and persistence.
2. Three earlier causal specialist families—fixed-clock auction state, completed structural context, and directional-change state—showed useful information primarily as **loss avoidance**, not positive direction prediction.
3. Historical ANY3 results demonstrated that unioning toxicity specialists could materially reduce loss, but exact historical fitted thresholds were not sufficiently reconstructible for a new formal promotion.
4. A fresh shallow causal model was therefore rebuilt from the current optimized R9/Dukascopy event stack instead of importing historical thresholds.
5. Jan–Mar discovery and April calibration showed a broad stable plateau.
6. The rule was converted from the fitted tree into explicit deterministic thresholds and committed **before** May–Jul was opened.
7. May, June and July were then evaluated once without retuning.
8. Parameter-neighborhood and spread stress preserved the material improvement.

No external proprietary indicator or opaque black box is required.

## 4. Reconstructible Mechanism

The gate is evaluated only when an otherwise valid R9 entry trigger already exists.

Inputs are causal and observable at the trigger:
- rearm ordinal;
- aligned 10-second S1 displacement;
- S1 directional efficiency;
- S1 range;
- S1 turn count;
- completed M5 ATR;
- completed multi-resolution alignment context;
- session state.

The promoted deterministic gate is:

```text
if ATR_M5 <= 14.155770:
    if session <= 1:
        if ATR_M5 <= 4.964402:
            KEEP only if aligned_S1_displacement > 1.042500
        else:
            KEEP
    else:
        if S1_range <= 2.980750:
            KEEP only if ATR_M5 > 11.730434
        else:
            ABSTAIN
else:
    if ATR_M5 <= 24.628465:
        KEEP only if S1_turns <= 4.5
    else:
        KEEP
```

When the gate returns ABSTAIN, that R9 opportunity is consumed. When it returns KEEP, original R9 entry and lifecycle semantics remain unchanged.

The tree is therefore not an execution black box; the final implementation is a small deterministic state machine.

## 5. Data and Causal Contract

- Authoritative Python research data: ordered Dukascopy XAUUSD ticks.
- R9 REAL: execution-failure benchmark.
- R9 SYNTH: teacher/north-star only.
- Discovery/calibration/forward wall: Jan–Mar / April / May–Jul.
- August remained sealed.
- No SYNTH future outcome, oracle direction, future MFE, future bar, or retrospective action enters the execution rule.
- Completed multi-timeframe inputs use completed state only.
- Source-equivalent R9 execution chronology is preserved for accepted events.

Frozen implementation was committed before forward evaluation:
- source commit: `85f166ff0a3f6a686b7c56b949eb63ae6e896857`
- freeze manifest commit: `4be54c8190bbacd6e4c0f116f6c30ae972b58794`

## 6. Quantitative Validation

### Jan–Jul aggregate

| Metric | Baseline | Breakthrough |
|---|---:|---:|
| Trades | 236,374 | 105,358 |
| Net | -$43,693.01 | **-$18,383.30** |
| Gross Profit | $31,461.48 | $16,601.94 |
| Gross Loss | -$75,154.49 | **-$34,985.24** |
| Profit Factor | 0.4186 | **0.4745** |
| Max DD | $43,694.85 | **$18,385.75** |
| Avg hold | 6.27s | 4.12s |

Net-loss reduction is **57.93%** and gross-loss reduction is **53.45%**.

### Monthly breakdown

| Month | Net | Gross Loss | Max DD | Net-loss improvement |
|---|---:|---:|---:|---:|
| Jan | -$2,184.67 | -$4,283.84 | $2,187.62 | 65.07% |
| Feb | -$2,939.03 | -$7,354.57 | $2,939.13 | 46.40% |
| Mar | -$4,084.64 | -$8,441.10 | $4,086.63 | 40.60% |
| Apr | -$2,469.62 | -$4,331.74 | $2,469.86 | 58.77% |
| May | -$2,540.21 | -$3,959.82 | $2,540.89 | 60.87% |
| Jun | -$2,660.46 | -$4,436.11 | $2,660.46 | 57.24% |
| Jul | -$1,504.66 | -$2,178.06 | $1,505.87 | 76.40% |

Every month remains negative, which is why this is explicitly a **loss-avoidance specialist**, not a complete strategy.

## 7. Economic Function and System Value

Primary ownership:
- **ENTRY/ACTION:** ABSTAIN from toxic R9 opportunities.
- **GROSS-LOSS / TAIL CONTAINMENT:** reduce capital spent on low-quality adverse paths.
- **OPPORTUNITY QUALITY:** preserve the existing R9 trigger but require causal state ownership before financing it.

It adds system value because the full chronological engine loses **$25,309.72 less** while cutting gross loss by more than half and reducing max drawdown by roughly the same magnitude.

Its limitation is equally important: it also gives up substantial gross profit and retains only 44.57% of R9 trades. The next system layer must therefore create or preserve positive opportunity rather than simply add more filtering.

## 8. Interaction With Existing Specialists

The gate is deliberately separate from:
- positive action/direction ownership;
- HARVEST/MEDIUM/RUNNER lifecycle;
- H4 structural ownership;
- slower independent structural sleeves.

This separation is intentional. Earlier testing showed that pre-entry toxicity information and post-entry lifecycle-value information do not improve when blindly collapsed into one shallow model.

The gate should run upstream of an HFT action owner. Structural sleeves may remain independent and must be merged chronologically rather than added arithmetically.

## 9. Optimization and Robustness

The promoted rule was selected from a broad shallow neighborhood rather than a single best point.

Nearby Jan–Jul exact results include:
- depth 4 / leaf 800: about **-$18.19K**
- depth 4 / leaf 1500: **-$18.38K**
- depth 4 / leaf 3000: about **-$18.41K**
- depth 5 / leaf 3000: about **-$17.98K**

This is a plateau, not a single fragile optimum.

Spread stress also preserves the effect:

| Half-spread | Net-loss improvement | GL reduction |
|---|---:|---:|
| $0.100 | 57.93% | 53.45% |
| $0.110 | 57.64% | 53.55% |
| $0.120 | 57.46% | 53.67% |
| $0.125 | 57.38% | 53.73% |

## 10. Failure Modes and Boundaries

Known limitations:
- negative in all seven months;
- PF remains below 1;
- substantial opportunity suppression;
- cannot reproduce SYNTH winner magnitude or persistence by itself;
- does not own direction;
- does not decide HARVEST versus RUNNER;
- closes only 7.04% of the total MT5 R9 REAL→SYNTH bridge.

Do not tighten the gate merely to improve loss statistics. That risks converting a useful ownership layer into a low-activity dead strategy.

## 11. Where It Is Used

Proposed architecture:

```text
R9 opportunity detector
    ↓
R9B_Gamma_1_Toxicity_Ownership_Gate
    ↓ KEEP
positive action / direction owner
    ↓
specialist-specific lifecycle
    ↓
HARVEST / MEDIUM / RUNNER / failure containment
```

ABSTAIN events do not proceed into the HFT action/lifecycle chain.

Independent slower structural sleeves remain outside this path and require their own portfolio ownership rules.

## 12. Python Reference Implementation

Canonical frozen implementation:
`research/R9_Rebuild/r9b_toxicity_ownership_exact.py`

Formal result:
`research/R9_Rebuild/results/R9B_Gamma_1_Toxicity_Ownership_Gate.json`

Important hashes:
- Jan–Jul aggregate: `09eeb1a42ab5c5bc2db5c696b5548126bae089444584e278b7e6cfef3b6498a7`
- parameter stress: `8af226442c4f906b90b936bbb35e51fe8c9ace4358d97644bb8351b50ae784c8`
- spread stress: `7d1e0f92471acc94116867d98243435a9abb8c8ea3c73cf4a96d1723ed42ddea`

## 13. MT5 / MQL5 Translation Contract

The final gate is MQL5-translatable because it contains only explicit scalar comparisons over deterministic causal state.

Before any MT5 certification:
- replicate completed M5 ATR exactly;
- replicate session mapping;
- replicate S1 displacement/range/turn arithmetic and threshold boundaries exactly;
- preserve R9 trigger/rearm semantics;
- preserve ABSTAIN-as-consumed-opportunity semantics;
- verify decision classification parity event by event.

This paper does **not** authorize MT5 coding yet.

## 14. Refinement Starting Point

Current best version:
`R9B_Gamma_1_Toxicity_Ownership_Gate`

Frozen assumptions:
- depth-4 equivalent deterministic rule above;
- original R9 lifecycle for accepted events;
- ABSTAIN consumes the candidate opportunity;
- no post-entry data in gate decisions.

Known bottleneck:
**The gate removes bad financing but does not create enough positive expectancy.**

Highest-value next experiments:
1. rebuild a positive action owner on the retained population;
2. route 10-second-survival / persistence state into HARVEST versus RUNNER;
3. integrate the positive H4 structural sleeve under explicit portfolio ownership;
4. measure whether the gate should be conditional on a positive owner rather than universal;
5. restore trade density through orthogonal positive specialists, not by weakening causal protection blindly.

Semantics that must not change without reopening certification:
- source chronology;
- feature timing;
- completed-bar semantics;
- frozen forward separation;
- opportunity consumption behavior;
- decision-boundary arithmetic.

## 15. Provenance and Artifact Index

- frozen source commit: `85f166ff0a3f6a686b7c56b949eb63ae6e896857`
- frozen manifest commit: `4be54c8190bbacd6e4c0f116f6c30ae972b58794`
- July Dukascopy raw SHA-256: `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`
- aggregate SHA-256: `09eeb1a42ab5c5bc2db5c696b5548126bae089444584e278b7e6cfef3b6498a7`
- parameter stress SHA-256: `8af226442c4f906b90b936bbb35e51fe8c9ace4358d97644bb8351b50ae784c8`
- spread stress SHA-256: `7d1e0f92471acc94116867d98243435a9abb8c8ea3c73cf4a96d1723ed42ddea`

## 16. Revision History

| Revision | Change | Validation impact |
|---|---|---|
| 1.0 | Initial formal specialist promotion | Jan–Jul + parameter/spread stress certified |

---
This paper documents a research mechanism and measured historical behavior. It is not a promise of future trading performance.
