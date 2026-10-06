# GRID-001 January Proof-Before-Entry 001 — Preregistration

**Unit:** `DAA_GRID_001_JANUARY_PROOF_BEFORE_ENTRY_001`  
**Status:** FROZEN BEFORE COMPUTE

## Question

Can the adaptive lattice reduce gross loss structurally by keeping new continuation events virtual until favorable path evidence arrives, instead of paying a provisional loss while waiting for confirmation?

## Lattices

- A05
- A10
- A15

All use the already-promoted completed-M1 ATR(14) adaptive geometry:
- multipliers 0.50 / 1.00 / 1.50;
- gap clamp $0.75–$5.00;
- $0.10 quantization;
- per-event frozen gap.

## Event direction

Continuation only for this unit.

No mean-reversion classifier, recovery classifier, session/news filter, or specialist routing.

## State machine

At lattice crossing:

`SHADOW_UNCONFIRMED`

No physical trade exists yet.

Using the executable continuation path relative to the original event quote:

- favorable proof = **+0.25 event gap**
- failure = **-0.50 event gap**

If failure arrives first:
- event retires;
- physical PnL = $0;
- no recovery in this unit.

If proof arrives first:
- enter one continuation trade at the executable quote on the proof tick;
- TP = +1.00 event gap from the **actual proof-entry price**;
- SL = -1.00 event gap from the actual proof-entry price;
- physical trade must finish inside the **remaining original five-minute event horizon**;
- no horizon reset.

If neither proof nor failure occurs before the original horizon:
- no trade.

## Economics

- fixed 0.01;
- $0.02 round-trip commission only when a physical trade is opened;
- no averaging;
- no Martingale;
- no second entry for the same event.

## Required comparisons

Against each lattice's immediate-continuation baseline and, where available, Early Thesis Failure 001:

- event count;
- accepted physical trade count/share;
- accepted trades per active event day;
- net;
- gross profit;
- gross loss;
- PF;
- expected payoff per physical trade;
- expected payoff per lattice event;
- win rate;
- timeout count;
- discovery vs validation.

## Advancement

Proof-before-entry is structurally interesting if:
- gross-loss magnitude falls dramatically;
- PF/net improve in both discovery and validation qualitatively;
- accepted trade velocity remains useful for the system-wide lattice;
- improvement is not created solely by deleting nearly every event.

No proof/failure threshold sweep is authorized.

If the mechanism works, the next question becomes how to combine its accepted trades with recovery/routing rather than tightening thresholds.

August sealed. Main `delta` read-only. MQL5 unauthorized.
