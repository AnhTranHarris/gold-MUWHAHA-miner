# DELTA-A Transparent S1 Frontier Rediscovery — 2026-10-05

Status: COMPLETE RECONSTRUCTION BOUNDARY / COUNTERFACTUAL FRONTIER ONLY  
August: SEALED / NOT ACCESSED  
MQL5: NOT AUTHORIZED

## Recovered concept
The historical transparent S1 boundary router is reconstructible.

Event population: R9-style minute bracket + completed S1 quality gate.

Router:
- CONTINUE when prior completed S1 aligned return <= -0.255 and S1 range >= $0.285.
- FADE when prior completed S1 aligned return >= +0.275 and prior completed S1 tick count >= 5.
- Otherwise ABSTAIN.
- Defensive profile: CONTINUE <= -0.290; FADE >= +0.310.

Lifecycle:
- emergency room $5.00
- harvest activation +$0.01
- harvest trail $0.01
- maximum hold 120 seconds
- historical integration EA additionally carries 10-second same-direction catastrophe memory after an unharvested stop loss.

## Surviving historical frontier
The earlier preserved refined two-state counterfactual table reports:
- 61,646 trades
- +$19,247.981367 net
- +$20,107.872314 GP
- -$859.890947 GL
- PF 23.3842
- closed-trade DD ~$5.3598
- win 86.502%

The later documented balanced-strengthened frontier reports approximately:
- 54,119 trades
- +$18,983.36 net
- -$649.16 GL
- PF ~30.24
- closed-trade DD ~$5.33

Relative to the preserved predecessor, the strengthened step therefore:
- removes ~12.2100% of trades
- sacrifices only ~1.3748% of net
- reduces gross loss ~24.5067%

This quantitative fingerprint is consistent with the later integration EA adding the CONT range-strength and FADE tick-strength conditions.

## Fresh falsification 1 — Delta-A/Dukascopy January
Fresh from-zero January fixed-entry replay:
- R9 events: 33,793
- balanced-strengthened routed trades: 9,513
- net: -$1,922.42
- GP: +$1,750.86
- GL: -$3,673.28
- PF: 0.47665
- win: 68.59%
- closed DD: ~$1,940.90

Decision: historical positive frontier does not reproduce on independent Delta-A/Dukascopy chronology.

## Fresh falsification 2 — actual Coinexx R9 REAL January
Source: all 21 January daily R9 REAL ticklogger partitions; 31,915 original ENTRY events.

Balanced-strengthened:
- 7,423 routed trades
- net -$1,278.86
- GP +$1,317.99
- GL -$2,596.85
- PF 0.50753
- win 68.79%
- closed DD ~$1,288.45

Defensive:
- 6,706 trades
- net -$1,159.75
- PF 0.50892

Decision: the historical +$18.98K / -$649 frontier was not an exact bid/ask chronological replay on the current reconstructed Dukascopy R9 population or the actual Coinexx R9 REAL ENTRY population. It must be treated as a counterfactual/event-scoring research frontier.

## Carry-forward
The concept is still valuable as an ownership classifier:
1. event != action;
2. adverse one-second pullback can imply CONTINUE rather than automatic failure;
3. late same-direction one-second extension can imply FADE/exhaustion;
4. ambiguous state should ABSTAIN;
5. strength qualifiers reduce gross-loss exposure disproportionately.

For DELTA-A, import these as causal state features/ownership hypotheses only. Do not import the historical profit metrics as current proof. Any promotion requires fresh chronological tick replay on DELTA-A plus preservation of the frozen $100-$1,000 survival guardrails.


## Fresh falsification 3 — Coinexx REAL events on Dukascopy path
A first attempt failed before simulation because the runtime dependency import was missing. Per timeout/helper policy it was not resumed; the run was discarded and restarted from zero.

Fresh rerun:
- frozen Coinexx R9 REAL January entry events: 31,915
- balanced-strengthened routed trades: 4,529
- net: -$858.27
- GP: +$827.64
- GL: -$1,685.91
- PF: 0.49092
- win: 68.47%
- closed DD: ~$858.27

Decision: this hybrid interpretation also fails. The old positive headline is now excluded from three fresh chronological interpretations.

## Reconstruction conclusion
The transparent mechanics are recovered. The historical economic headline can be arithmetically reconciled to its surviving predecessor frontier, but the original counterfactual scorer implementation/outcome surface has not yet been recovered well enough to claim a fresh <=5% metric reproduction. Do not manufacture parity. Carry the router mechanics forward as a causal ownership hypothesis only.
