# GAMMA-02 — 083 Parent-Phase Desynchronization 086

**Status:** COMPLETE REJECTION FOR HEAT REDUCTION / CAUSAL PHASE TEST  
**Parent:** GAMMA_02_083_WAVE_MULTIPLICITY_QA_085.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Hypothesis

Preserve each structural parent's child ownership, but derive a deterministic post-harvest rearm phase from the parent's executable entry-price phase. This is causal at parent admission and uses no future exit/P&L information.

## Screen

25 combinations of early- and late-desk phase-coded rearm maps were tested.

Many variants still crossed all six exact January R9 SYNTH metrics. Example:
- early rearm phases [125,250,375,500] raw
- late phases [0,125,250,375,500,625,750,875]
- +$66,939.47
- 45,068 trades
- PF 21,387.41
- +$1.48530 expectancy
- 14.025s average hold

However the heat objective failed:
- maximum simultaneous child positions remained **1,443**
- maximum same-tick child cluster remained **1,443**
- exact full-tick equity DD remained approximately **$19,371.52** for the low-heat-ranked valid variants

## Scientific disposition

REJECT parent-entry price phase offsets as a sufficient heat-reduction mechanism.

The dominant heat is not caused merely by synchronized rearm thresholds. It is caused by the number of parent-owned children simultaneously alive.

This makes the next experiment simpler and more directly causal:

**GAMMA_02_083_GLOBAL_CHILD_CAP_087**

Impose one global admission ceiling on child tickets while preserving:
- parent ownership;
- original 083 renewal rules;
- chronological first-come admission;
- no future ranking or hindsight.

Search the minimum global child cap that still crosses all six exact January R9 SYNTH metrics.

## Exact artifacts

Helper SHA-256:
`4ab44f0e6851fe31e53a0957664815a7b99d5a1068b6477fd1aa2a275df9f1a3`

Result SHA-256:
`bcc8594652482568579a080de83ca759d0520102753d1fc2f184771d79d09aa5`

Do not rerun <=086 after timeout.
