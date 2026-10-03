# DELTA R037 — R032 Parent Backbone Clean-Room Parity

**Status:** COMPLETE — NON-SPECIALIST BACKBONE PARITY PASS  
**R037 integrated SORB replay:** STILL NOT STARTED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Why this unit was required

The historical producing Python bytes for R025/R028/R032 were not found in the live GitHub tree, Git history inspected for the DELTA lab, Google Drive file inventory, or Project/Library retrieval. The durable records preserve script SHA-256 identities and results, but not the original source bytes.

R037 therefore used the protocol's clean-room reconstruction path rather than approximating R032-C03.

## Durable clean-room source

Path:
`research/delta/experiments/delta_r037_r032_parent_backbone.py`

Commit:
`48f29d54fd43809205fba607b9cda62003df75db`

Blob:
`12e037bc44c8587f2305357ff085380473c40963`

The implementation uses only reconstructible frozen DELTA definitions:
- exact R9 state/execution order;
- DH-01 completed-bar DirectionalDisplacement formula;
- DH-06 BidAskImpulse formula over the prior 250 ms;
- R010 P01 condition/action;
- R024 M30-only KEEP-owned condition/action;
- R028 GLOBAL NO_REARM semantics.

## Source and surface

January canonical gzip:
- bytes: 68,690,420
- SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Stage-A:
- ticks: 4,205,709
- interval: `[2026-01-01T00:00:00Z, 2026-01-18T12:00:00Z)`
- surface: `DUKAS_COINEXX_LIKE_P75`

## Metric-definition reconciliation

R010 reported a raw-positive exit winner count.
R024/R028/R032 use an exit-deal-positive winner count:

`raw_trade_pnl - $0.01 exit commission > 0`.

This is confirmed by exact parity:
- R9 raw-positive wins: 7,351
- R9 later official winner denominator: **7,265**
- P01 raw-positive wins: 6,803
- P01 R024 official wins: **6,734**
- M30_KEEP raw-positive wins: 6,527
- M30_KEEP R024 official wins: **6,461**

Gross-profit/gross-loss accounting remains the frozen R9 deal accounting: the entry commission is booked to gross loss; an exit deal is classified by raw exit P/L sign after subtracting the exit commission from the deal value.

## Exact Stage-A P75 parity

### R9 control

Frozen target:
- trades 16,801
- raw-positive wins 7,351
- gross profit +$1,574.77
- gross loss -$5,343.02
- net -$3,768.25
- balance DD $3,769.83

Clean-room:
- trades **16,801**
- raw-positive wins **7,351**
- official later wins **7,265**
- gross profit **+$1,574.77**
- gross loss **-$5,343.02**
- net **-$3,768.25**
- balance DD **$3,769.83**
- equity DD **$3,770.33**

Result: **EXACT PARITY** on the frozen economic/control metrics.

### P01 ownership

Frozen R010/R024 target:
- trades 14,582
- raw-positive wins 6,803
- R024 official wins 6,734
- gross profit +$1,426.64
- gross loss -$4,393.28
- net -$2,966.64
- balance DD $2,967.63
- flips 6,658
- owned-exit suppressed rearms 6,582

Clean-room:
- trades **14,582**
- raw-positive wins **6,803**
- official wins **6,734**
- gross profit **+$1,426.64**
- gross loss **-$4,393.28**
- net **-$2,966.64**
- balance DD **$2,967.63**
- P01 hits/flips **6,658**
- suppressed rearms **6,582**

Result: **EXACT PARITY**.

### M30_KEEP_OWNED

Frozen R024 target:
- trades 14,025
- official wins 6,461
- gross profit +$1,370.90
- gross loss -$4,234.24
- net -$2,863.34
- balance DD $2,864.33
- M30-only hits 1,906

Clean-room:
- trades **14,025**
- raw-positive wins **6,527**
- official wins **6,461**
- gross profit **+$1,370.90**
- gross loss **-$4,234.24**
- net **-$2,863.34**
- balance DD **$2,864.33**
- M30-only hits **1,906**

Result: **EXACT PARITY**.

### R025 + GLOBAL NO_REARM

Frozen R028 P75 target:
- trades 12,504
- official wins 5,723
- net -$2,571.31
- generic rearms 0

Clean-room:
- trades **12,504**
- raw-positive wins **5,788**
- official wins **5,723**
- gross profit **+$1,225.76**
- gross loss **-$3,797.07**
- net **-$2,571.31**
- balance DD **$2,572.30**
- generic rearms **0**

Result: **EXACT PARITY** on the R028 reported control metrics.

## Architectural consequence

The entire non-specialist R032 backbone is now independently reproducible from the canonical tick corpus:

`R9 -> P01 -> M30_KEEP_OWNED -> GLOBAL NO_REARM`.

The remaining R032 parity work is isolated to four frozen specialist streams:
- DH03-S06
- DH05-S06
- DH02-S11
- DH02-S08

No R037 SORB integration is permitted until those four are reconstructed and the full R032-C03 P75 control matches the authoritative:
- 13,868 trades
- 6,331 official winners
- net -$2,842.16
- 2,083 specialist entries
- specialist net -$383.55.

## Decision

**PARENT_BACKBONE_PARITY_PASS.**

Next bounded unit:
reconstruct the four frozen specialist signal generators one at a time, beginning with DH05-S06 because it has the strongest standalone parity fixture:
672 signals -> 615 standalone trades -> 307 official wins -> -$101.08 net.

Do not tune SORB or any specialist thresholds during parity reconstruction.
