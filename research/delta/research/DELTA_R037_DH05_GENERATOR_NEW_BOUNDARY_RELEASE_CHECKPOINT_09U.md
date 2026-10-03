# DELTA R037 — Generator Ownership / New-Boundary Release — Checkpoint 09U

**Status:** COMPLETE NEGATIVE QA / NEW-BOUNDARY RELEASE UNDER-PRODUCES  
**Unit:** R037_DH05_GENERATOR_OWNERSHIP_NEW_BOUNDARY_RELEASE_PARITY_RECONSTRUCTION  
**Parent:** R037_DH05_CONDITIONAL_FAILURE_CLOCK_CHALLENGER_CHECKPOINT_09T  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED  
**R037-SORB:** BLOCKED

## Question

Can the probe generator remain locked after FAILURE_CANDIDATE and become eligible only when a **new causally confirmed width-2 M5 swing identity** appears, while the old failed-break episode continues downstream?

This is the constrained middle ground between:
- Checkpoint 09H immediate FAILURE_CANDIDATE decoupling, which was too early and over-produced; and
- fully serial POST_QUAL ownership, which still under-produces sparse historical density.

No frozen numeric vector changed.

## Producer / crash-safety

Producer:
`research/delta/experiments/delta_r037_dh05_generator_new_boundary_release_parity.py`

- commit: `8c8f007bdf5c6b4247d955a31f0e3abc7ee3fcb0`
- Git blob: `4a586ecd6b507763662ec2c0a8e95e37927fe592`
- SHA-256: `9f623f26e577d2941d21023176451b2e3d60cfb2d9223736649c7c158c427a43`

Dependencies remained the exact durable 09T/helper blobs.

Official compute:
- Stage-A ticks: **4,205,709**
- elapsed: **19.44 s**
- peak RSS: **698,960 KB**
- exit: **0**
- result SHA-256: `2622eafae5bda6037283b2eaaf63acc9f177f0899100f1c4bfa87df59dc0c808`

The producer was committed before compute, exact local/GitHub blob parity was verified, a fresh Numba cache was used, a hard 120-second external timeout was applied, and output was atomic.

## Frozen serial control

POST_QUAL serial total eight-stage error: **978**.

Stage absolute errors:
- probe 642
- qualified 55
- accepted 24
- failure 63
- reentry 34
- reclaim 34
- reversal 63
- signal 63

## New-boundary release profiles

### NEW_ANY_BOUNDARY

Total funnel error: **22,360**  
Aggregate trade-count error: **899**  
Max concurrent failure episodes: **2**  
Episode overflow: **0**  
Signal overflow: **0**

Signals:
- A03 94
- S05 6
- S06 213
- S09 10
- S10 93
- S16 7

S06: 213 signals / 212 trades / 89 wins / -$50.99.

### NEW_SAME_SIDE_BOUNDARY

Total funnel error: **25,547**  
Aggregate trade-count error: **962**

Signals:
82 / 4 / 181 / 8 / 77 / 7.

### NEW_OPPOSITE_SIDE_BOUNDARY

Total funnel error: **26,635**  
Aggregate trade-count error: **1,015**

Signals:
72 / 6 / 144 / 8 / 70 / 7.

All profiles had zero episode and signal buffer overflow.

## Interpretation

New-boundary release is decisively **too late**. It keeps the generator locked across too much of the failed-break lifecycle and sharply suppresses probes, qualifications and signals.

This complements the earlier bounds:

- 09H immediate release at FAILURE_CANDIDATE: **too early / severe overproduction**
- 09I release at REENTRY: **too early / severe overproduction**
- 09I release at RECLAIM: **much safer but total parity still worse than serial POST_QUAL**
- 09U release only on a newly revealed M5 boundary: **too late / severe underproduction**

That brackets the remaining plausible generator-release region much more tightly.

The next causal state transition after RECLAIM but before completed signal termination is the **reversal clock** itself. A controlled release on a new completed reversal-timeframe bar after reclaim—or specifically after an unsuccessful reversal-confirmation attempt—can be tested without inventing a numeric delay.

## Decision

**Checkpoint 09U = QA PASS / NEGATIVE.**

Reject all new-boundary release profiles. Keep serial POST_QUAL as control.

## Next bounded unit

`R037_DH05_GENERATOR_RELEASE_ON_REVERSAL_CLOCK_TRANSITION_PARITY_RECONSTRUCTION`

Test only reconstructible causal variants after RECLAIM:
1. release generator on the first new completed reversal-timeframe bar after reclaim;
2. release only when that bar fails the frozen reversal confirmation;
3. retain serial POST_QUAL control.

No threshold retuning. No August. No SORB. No MQL5.
