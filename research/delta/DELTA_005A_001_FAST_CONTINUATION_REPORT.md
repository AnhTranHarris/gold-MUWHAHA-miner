# DELTA 005A-001 — Fast Continuation Tick-Flow Entry Screen

**Status:** COMPLETE — NOT PROMOTED AS A GLOBAL GATE  
**Mode:** historical Python simulation  
**Focus:** Entry + Initial-Hold diagnostics  
**Window:** 2026-01-01 00:00 UTC to 2026-01-18 12:00 UTC exclusive  
**Surface:** DUKAS_COINEXX_LIKE_P75  
**Ticks:** 4,205,709  
**Configurations:** 90  
**August:** not accessed

## Result

Short-window tick flow is informative, but using it as a universal hard entry gate produces a smooth trade-off: stricter flow steadily reduces gross loss and drawdown while steadily removing trades and winning trades.

The high-retention diagnostic anchor (250 ms fast / 1 s slow / sign-only confirmation) retained 90.88% of Stage-A trades, improved gross-loss magnitude 11.49%, reduced net-loss magnitude 13.70%, and improved balance drawdown 13.69%. Winning-trade count fell 5.99%.

The strongest headline configuration improved gross-loss magnitude 36.84% and drawdown 39.20%, but retained only 65.31% of trades and lost 32.40% of winning trades. It is therefore not acceptable as a universal activity-preserving entry replacement.

## Initial-hold finding

The 1/3/5/10/15-second survival curve barely changed under the high-retention anchor. MFE and MAE improved only slightly.

This means the tested flow formula mainly changes which opportunities are admitted; it does not materially repair the first-seconds persistence problem after entry.

## Formula-level leverage diagnosis

The limiting component is not a specific flow threshold. The limiting architecture is **global exclusion**.

No tested 250/500/1000 ms fast window, 1/3 s slow window, or threshold neighborhood produced a large improvement while preserving the original activity surface.

The next structural change is therefore:
- keep mild flow as direct-continuation ownership evidence;
- route non-confirmed first-touch breaks into a micro-retest/reclaim specialist;
- later route failed reclaims into a failed-break/sweep-reversal specialist.

This is a specialist recombination problem, not a threshold-tuning problem.

## Durable analysis

Temporary mathematical analysis Sheet:
https://docs.google.com/spreadsheets/d/17Rcz6Jq4btAgdZz7lY1vjbAhbou8IyVIjUZ_-U3k9kY/edit?usp=drivesdk

Master research ledger:
https://docs.google.com/document/d/1T9MPuuMsxB5gv7Zz8nvzFmaQy00_7Q-7X_4F2qrcR6k/edit?usp=drivesdk

Source:
`research/delta/experiments/DELTA_005A_FAST_CONTINUATION.py`

## Decision

**Do not continue local flow-threshold tightening. Proceed to DELTA_005B micro-retest/reclaim.**
