# GRID-001 January Negative Probe Ledger 001

**Purpose:** durable anti-repetition ledger. These mechanism families were tested on the January elastic-grid research surface and did not justify refinement.

| Probe family | Outcome | Research decision |
|---|---|---|
| Fixed $1 automatic mean reversion | Strongly negative | REJECT |
| Fixed $1 automatic continuation | Negative | REJECT |
| 250ms–3s signed-displacement observation gate | All 9 variants negative | REJECT; do not tune waits |
| Single virtual same-side stack depth | Not stable discovery→validation | REJECT standalone router |
| Virtual BUY/SELL unresolved-stack imbalance | Regime-shifted / not robust | REJECT standalone router |
| Completed-M1 60m/240m parent trend ownership | Negative / often worse validation | REJECT simple parent-direction router |
| Micro first-passage barrier race | Improved subsets but remained negative | REJECT standalone |
| Blind early-stop-and-reverse recovery | Strongly negative | REJECT; recovery cannot be automatic reversal |
| Tight-stop / larger-target arithmetic rescue | Negative across screened geometry | REJECT payoff-only rescue |
| L1 Dukascopy quote imbalance 1s/5s/15s | Weak/no standalone edge | REJECT standalone microstructure router |
| Event run-length / recent event sequence | Interesting pockets only, not stable | REJECT standalone |
| ExtraTrees causal path-shape microscope | Held-out validation negative | REJECT model/feature family |

## What these failures mean

The grid's problem is not lack of event supply. It is not solved by one generic trend indicator, one short confirmation delay, one virtual-stack threshold, one quote-imbalance threshold, automatic stop-and-reverse, payoff arithmetic alone, or nonlinear ML applied to the same weak information.

The retained structural improvement is the **alpha-0.50 elastic event clock**.

The next research family changes the regime/trade contract itself: volatility expansion + causal breakout ownership + event-origin invalidation.

## Weak seed, deliberately not tuned

A failed-break/reclaim mean-reversion lane produced a small positive pocket only under very quiet volatility (ATR14/ATR240 <= ~0.6) with a deep excursion/reclaim contract. Evidence is too weak and narrow to spend research budget on now. Preserve as a future range-mode seed only if the later system explicitly asks for range help.

This ledger is not a claim that these mechanisms can never work in any strategy. It records that these specific Delta-A-alpha January formulations failed sufficiently to prohibit immediate retesting/tuning.
