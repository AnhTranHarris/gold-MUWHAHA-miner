# DELTA R037 — Sweep → MSS → Order-Block Retest Stage-A Screen — Checkpoint 17H

**Status:** ORDINARY SCREEN PASS / NO STRONG PASS / NON-PROMOTING BREAKTHROUGH CLUE  
**Family:** R037-SMOR-v1  
**Parent:** R037_EGF_STAGE_A_SCREEN_CHECKPOINT_17G  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen hypothesis

The entry is delayed through three causal stages:

1. a width-2 confirmed swing is swept and the completed bar closes back inside;
2. price later closes through the opposite swing that was already visible at sweep time, establishing an MSS;
3. the last opposite-colour candle before that MSS becomes the order-block body, and only the first later unmitigated retest can propose an entry.

The immutable implementation contract also froze same-direction sweep supersession, active-zone ownership, first-touch consumption, invalidation, and bidirectional collision handling before compute.

Public reconstructible grounding:
- MetaQuotes 24184: sweep = beyond level + failure to continue + close back inside + reaction;
- MetaQuotes 21212: distinguish liquidity raid from genuine MSS; shifts after liquidity grabs are higher-quality context;
- MetaQuotes 23341: last opposite candle before displacement that breaks structure, held until mitigation/retest;
- community corroboration: sweep traders frequently wait for MSS and then OB/FVG retest rather than entering on the sweep candle.

## Crash-safe compute

Prereg commit: `947b101e1a8d289b5832556e1795d71b653a444b`  
Lifecycle contract commit: `15334fe4d1f19ef0d58ca27552243fb08037bd58`  
Producer commit: `e5acbd86f244b739279b21b78c35b56ee286a6fb`  
Producer blob: `bb944bb9052b95f039e0cdd0942598d2a4b2d47d`  
Producer SHA-256: `e28d27e0f79d1be79b4bc44653421e0de532297ce870b925e73febc4292ae6e0`  
Precompute recovery gate: **37178401397 PASS**.

Canonical January SHA:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.  
Official bounded runtime: **20.525 seconds / exit 0**.  
Official raw-result SHA:
`6937752f233b07c219b8e7b084cf37b7501f5e3c7c147da459d271a5c3b9aa20`

## Results

Parent: **14,034 trades / 6,349 official wins / -$2,944.94 net**.

- **C01 M1 BODY_TOUCH:** 18 proposals / 16 accepted / 9 days; +16 trades / +8 wins / **-$1.31 net delta**. Ordinary screen **PASS**, strong screen FAIL.
- **C02 M1 MIDPOINT:** 11 proposals / 11 accepted / 6 days; +11 trades / +7 wins / **-$0.03 net delta**. GP +$2.10, GL -$2.13, equity-DD deterioration only **0.0010%**. Ordinary screen **PASS**, strong screen FAIL by three cents.
- **C03 M5 BODY_TOUCH:** 7 proposals / 7 accepted; +7 / +1 / -$3.24. Supply/net FAIL.
- **C04 M5 MIDPOINT:** 5 proposals / 5 accepted; +5 / +1 / -$1.70. Supply FAIL.

## Breakthrough interpretation

This is not a promoted DELTA candidate. However, it is the strongest new independent structural clue after 17E.

The progression is material:

- generic SFP M5-half: **-$18.85**
- M5 Type-1 engulf failure: **-$18.33**
- sweep → MSS → M1 OB midpoint retest: **-$0.03**

The extra causal stages nearly remove the economic penalty without threshold or exit tuning.

C02 also added **7 official wins on 11 trades** while leaving drawdown almost unchanged. The result therefore supports the research hypothesis that **entry timing after structural confirmation/retest is materially superior to immediate rejection-bar entry**.

## Decision

**NO PROMOTION. NO C02 RETUNE.**

Freeze:
`R037-SMOR-C02_M1_MIDPOINT`
as a **recombination clue only**.

The separately discovered 17E clue,
`R037-MSF-C04_M5_BOS_FVG_RETEST`,
also reached near-neutral Stage-A economics (**-$0.05 net delta**) while adding winners.

The next valid research direction is therefore a **new preregistered recombination family** that requires the SMOR sequence and an independently derived FVG/imbalance confirmation. This is not a rescue parameter change to C02.

August remains SEALED. MQL5 remains unauthorized.
