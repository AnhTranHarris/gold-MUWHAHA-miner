# DELTA R037 — Engulfing Commitment Failure Stage-A Screen — Checkpoint 17G

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED  
**Family:** R037-EGF-v1  
**Parent:** R037_SFP_STAGE_A_SCREEN_CHECKPOINT_17F  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen hypothesis

A completed two-candle engulf establishes a directional commitment. The commitment remains active until its first qualifying opposite-colour completed close through the Base candle's far edge. A failed BUY commitment yields a SELL proposal; a failed SELL commitment yields a BUY proposal. Wick-only breaches do not fail a commitment.

Four configurations were frozen before compute:
- C01 M1 regular failure
- C02 M1 Type-1 sweep+engulf failure
- C03 M5 regular failure
- C04 M5 Type-1 sweep+engulf failure

No expiry, threshold, session, side, timeframe, merge, or exit was tuned after the result.

## Crash-safe compute

Preregistration: `DELTA_R037_EGF_SOURCE_HARVEST_PREREG_17G.json`  
Producer commit: `d9f8032e4221e17527ffa84667f1ddfae3dd06f0`  
Producer Git blob: `72737c7238915c0bca1b63512633adfc10bf18a4`  
Producer SHA-256: `427c4715c328199c1efc3bbb13aa346ffe3e526c8a3ebd5bddf373767d9b733e`  
Recovery / rebuild gate run: **37178013014 PASS**.

Canonical January SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A ticks: **4,205,709**.

Official bounded replay: **21.023 seconds / exit 0**.  
Official raw result SHA-256:
`d124c1bac75ab8e098ac6118e16ab22fea46d317807fced81e9f9b25d2458628`

## Results

Parent: **14,034 trades / 6,349 official wins / -$2,944.94 net / $2,946.43 max equity DD**.

- **C01 M1 regular failure:** 1,864 proposals / 1,751 accepted; +1,704 trades / +798 official wins / **-$330.95 net delta**; direct EGF -$342.89; equity-DD +11.19%. FAIL.
- **C02 M1 Type-1:** 662 / 623; +608 / +283 / **-$125.31**; direct -$122.12; equity-DD +4.21%. FAIL.
- **C03 M5 regular failure:** 334 / 319; +315 / +177 / **-$32.46**; direct -$34.91; equity-DD +1.10%. FAIL.
- **C04 M5 Type-1:** 133 / 128; +127 / +63 / **-$18.33**; direct -$16.44; equity-DD +0.62%. FAIL.

## Interpretation

Higher timeframe and the stronger Type-1 sweep+engulf commitment improve the family monotonically, but the strongest frozen configuration remains far outside the -$2 Stage-A gate.

Together with SFP 17F, this rejects another class of **enter immediately after a reversal/failure candle** logic under the frozen 30-second hold. The remaining promising direction is to delay entry until the rejection is followed by an explicit structural control change and a retest.

## Decision

**Checkpoint 17G = RETIRE R037-EGF-v1 / NO RETUNE.**

Do not rescue this family with expiry tuning, session slicing, long/short splits, or candidate-specific exits.

Next:
`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

Priority research direction:
**liquidity sweep → market-structure shift → first unmitigated order-block retest**.

August remains SEALED. MQL5 remains unauthorized.
