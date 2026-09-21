# Checkpoint 11 — Source-Audited R10 Rebuild

## Purpose

Checkpoint 11 is a source-to-code audit of the cumulative R9→R10 executable
lineage. It does **not** introduce a new research strategy. It corrects places
where the checkpoint-10 implementation was less faithful than the project
evidence or less safe than MetaTrader's execution/event model.

## Project-source corrections

### 1. Preserve auction state + action identity

The state-stability research ranked **auction states**, not just timeframes.
Checkpoint 10 allowed the generic S1 router to overwrite labels such as
P8 Sweep/Reclaim and P9 Acceptance with only CONTINUE/FADE.

Checkpoint 11 carries both dimensions:

- event family / temporal scale / event direction
- action policy (CONTINUE, FADE, P4 rotation, P6 expansion, post-stop state)

This makes states such as `P9_ACCEPTANCE_UP|CONTINUE` distinguishable from
`P8_SWEEP_RECLAIM_UP|FADE`.

### 2. Reconstruct only source-supported state stability

The project record explicitly identified **1m upside acceptance → CONTINUE** as
a toxic gross-loss state. It is blocked by default.

The complete historical "top two states per scale" table did not survive the
research handoff. The EA therefore exposes state-specific weights but does not
invent the missing ranking table. Rebuild that table from Jan-Apr and verify on
May-Jul before freezing it.

### 3. Same-scale KEEP/FLIP

The post-catastrophe KEEP/FLIP result was a **same-scale** transition. Checkpoint
11 now applies it only when a follow-up event belongs to the scale that produced
the catastrophe.

This is separate from the 10-second catastrophe memory, which intentionally
distrusts the failed direction across the 1m/3m/5m/10m/20m hierarchy.

### 4. Failed ignition uses the correct causal state shape

The old checkpoint used a simple absolute adverse-dollar threshold. The source
record instead supports delayed failure evidence combining:

- approximately 10–15 seconds of development time;
- near-zero MFE;
- severe ATR-normalized MAE;
- efficient adverse displacement;
- tick flow opposing the trade.

Checkpoint 11 implements that state shape. Exact fitted coefficients did not
survive, so the numeric thresholds remain visible reconstructed parameters.

No automatic P3 reversal is enabled. Immediate reversal was rejected in the
research; selective post-catastrophe flip remains handled by the separate
KEEP/FLIP policy.

## MetaTrader execution corrections

### 5. Harvest-armed means the stop actually moved

A favorable excursion crossing the activation threshold does not by itself
count as harvest protection.

The EA marks harvest as armed only after:

1. `PositionModify(ticket,...)` returns successfully; and
2. `ResultRetcode()` is accepted.

Reference:
https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradepositionmodify

### 6. Runtime state is keyed by position identifier

MetaTrader does not guarantee trade-transaction notification ordering.

Checkpoint 11 maintains runtime records keyed by `POSITION_IDENTIFIER` and
matches closes through `DEAL_POSITION_ID`. This protects MFE/MAE, harvest
state, entry ATR and catastrophe classification when multiple XAUUSD sleeves
coexist.

References:
- https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties
- https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties
- https://www.mql5.com/en/docs/event_handlers/ontradetransaction

The handler also:
- falls back to entry-deal registration if `CTrade::ResultDeal()` was not
  immediately available;
- ignores partial close fragments while the position identifier is still open;
- clears state only after that position actually disappears.

### 7. Tick-by-tick MFE/MAE

Core and auxiliary sleeves track executable-side favorable and adverse
excursion on every tick. That is consistent with the project's REAL-path
forensics and with current MQL5 excursion-journal architecture.

Reference:
https://www.mql5.com/en/articles/22855

### 8. Compact diagnostic comments

Broker comments are not used as strategy state. Magic numbers and position
identifiers are authoritative.

The EA nevertheless compacts the event/action label to <=30 characters for
tester diagnostics while logging the full state internally.

## What remains reconstructed, not historically exact

These mechanisms are implemented, but their original fitted Python constants
were not preserved:

- P3 failure thresholds
- P4 rotation ATR/efficiency cutoffs
- P6 expansion ATR/efficiency cutoffs
- P7 compression thresholds
- P8/P9 penetration/reclaim/acceptance geometry
- complete state-stability rank table
- KEEP/FLIP score thresholds

They require Jan-Apr reconstruction and May-Jul validation before final freeze.

## Rejected logic still excluded

Checkpoint 11 does not resurrect:

- intrasecond look-ahead;
- retrospective pending-order scheduling;
- global session kill switches;
- boundary-fatigue blacklists;
- forced trades in the ambiguous S1 middle;
- generic automatic runner promotion;
- harvest-then-reenter runner churn.

## Certification gate

This remains a **MetaEditor compile/test candidate**.

1. Compile with zero errors.
2. Fix only implementation defects.
3. XAUUSD Every Tick Based on Real Ticks, Jan-Jul 2026.
4. Record monthly net, gross loss, max dollar DD.
5. Test $100 and $200 marked-equity / margin survivability.
6. Reconstruct the missing Jan-Apr stability table if needed.
7. Freeze R10.
8. Open August exactly once.

**August remains sealed.**
