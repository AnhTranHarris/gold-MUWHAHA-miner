# DELTA R037 — London 15-Minute Opening Range Stage-A Screen — Checkpoint 17AB

**Status:** COMPLETE PRESCREEN PASS / STRONG FAIL / RETIRE WITHOUT RETUNE  
**Unit:** R037_LONDON_15M_OPENING_RANGE_STAGE_A_SCREEN_17AB  
**Parent:** R037_LONDON_ORB_SWEEP_RECLAIM_REVERSAL_CHECKPOINT_17AA  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research basis

This was a new independent-source family, not a rescue of 17Z/17AA. Public reconstructible logic from open-source TradingView ORB scripts and recent XAUUSD community discussion converged on the first 15-minute session range followed by confirmed breakout timing. The preregistration fixed the London January range to **08:00–08:15 UTC**, with breakout observation from **08:15–10:00 UTC**.

Only trigger timing varied:
- C01 first strict tick outside the range
- C02 first completed S5 close outside
- C03 first completed S15 close outside

The frozen 17Z 30-second lifecycle, spread gate, one-trade/day rule, and zero buffer were unchanged. No side/day/range/buffer/exit tuning was allowed.

## Crash-safe official compute

- prereg commit: `4f2ebf9de9ed6fd164013e87daaa0099581e0ce7`
- producer commit: `26a20ec154f33bc71dfd48f8cc20fd167dedee04`
- producer blob: `95dd30629231cded53cad0c92ad5ace6514f908a`
- producer SHA-256: `ac6185566c0020d5fb2bc7cb43e950a56ded116ab7793339e510cd174244a9be`
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- runtime: approximately **6.3 seconds**
- result SHA-256: `a5b77ede1ede27d15f01e9fc599e6128d06e326acf9a63f13d56dbd7b6b44228`

The locally executed producer was git-blob verified against the committed GitHub producer before compute.

## Stage-A result

| Config | Trades | Official wins | Win rate | Direct net | Gate |
|---|---:|---:|---:|---:|---|
| C01 strict tick | 11 | 5 | 45.5% | -$1.67 | prescreen PASS / strong FAIL |
| **C02 completed S5 close** | **11** | **8** | **72.7%** | **-$0.41** | **prescreen PASS / strong FAIL** |
| C03 completed S15 close | 11 | 7 | 63.6% | -$1.08 | prescreen PASS / strong FAIL |

C02 is the leader and improves on the prior 17Z near-neutral/high-win clue, but the preregistered strong gate required **nonnegative** direct net. It therefore does not survive.

## Interpretation

The first 15-minute London range is a better high-win timing clue than the retired 60-minute continuation/reversal variants under the frozen 30-second lifecycle. Completed S5 confirmation produced **8/11 official wins**, but the economics remain slightly negative at **-$0.41**.

That result is useful evidence, but not a valid candidate. It is not eligible for post-result range-width, buffer, side, weekday, stop, trail, or hold-period rescue tuning inside this family.

## Decision

**RETIRE R037-L15ORB-v1 / NO RETUNE.**

Preserve the completed-close timing clue for future independent recombination only.

## Next unit

`R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`

The next source should be genuinely independent of the London ORB family. Gold-specific session structure remains eligible, but another London range-window rescue is prohibited.
