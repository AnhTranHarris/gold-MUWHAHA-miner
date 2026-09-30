# BETA064 CHECKPOINT 02B — SYNTH Condition-Matched Coverage & Session×Specialist Gap Diagnostic

**Date:** 2026-09-30  
**Parent control:** BETA064 Major Checkpoint 02 — frozen, unchanged  
**Scope:** ENTRY→HOLD only  
**HOLD→EXIT:** deferred  
**August:** sealed  
**Status:** diagnostic research record — no checkpoint promotion

## Question

Re-run the R9 SYNTH comparison after adding the six-session contextual specialist layer and determine:

1. how much of the prior 71,810 SYNTH Entry→Hold opportunity pool is represented by frozen Major Checkpoint 02;
2. which gaps are concentrated in a particular session × specialist combination;
3. whether the 71,810 denominator is truly comparable to BETA in causal state space.

Major Checkpoint 02 remains immutable during this measurement.

## Frozen BETA reference

Major Checkpoint 02:

- 5,070 Jan–Jul one-position Entry→Hold trades;
- 88.44% weighted Entry→Hold survivability;
- all seven observed months >85%;
- all seven leave-one-month-out held-out months >85%;
- six session authorities: Australia, Asia, Middle East, Europe, UK, New York;
- session gap filling only when frozen base ownership is idle.

## SYNTH mechanism-matched pool

The prior dual-tick diagnostic produced 71,810 SYNTH opportunities that:

- map into one of the frozen E1–E12 specialist mechanisms; and
- survive the specialist-specific SYNTH Entry→Hold checkpoint.

This 71,810 count is retained as the **mechanism/taxonomy-matched denominator**.

It must no longer be described as an exact causal-state-matched denominator.

## Gross coverage

Frozen Checkpoint 02 trades / SYNTH mechanism-matched Entry→Hold opportunities:

`5,070 / 71,810 = 7.06%`

Month by month:

| Month | SYNTH Entry→Hold | BETA Ckpt-02 trades | Gross count ratio | session×specialist recovered | cell coverage |
|---|---:|---:|---:|---:|---:|
| Jan | 9,156 | 726 | 7.93% | 491 | 5.36% |
| Feb | 10,496 | 910 | 8.67% | 546 | 5.20% |
| Mar | 13,196 | 1,463 | 11.09% | 914 | 6.93% |
| Apr | 10,225 | 589 | 5.76% | 319 | 3.12% |
| May | 9,826 | 509 | 5.18% | 269 | 2.74% |
| Jun | 10,410 | 585 | 5.62% | 311 | 2.99% |
| Jul | 8,501 | 288 | 3.39% | 194 | 2.28% |

Using the existing side/state-aware session×specialist matcher, 3,044 of 71,810 SYNTH mechanism opportunities are represented by the frozen BETA session/specialist mix: approximately **4.24%**.

The raw 5,070 count is larger because BETA produces substantial excess activity in cells where SYNTH has relatively few opportunities.

## Specialist distribution mismatch

SYNTH mechanism pool:

- E6 Value Reversion: 46,648 = 64.96%
- E7 Sweep/Reclaim: 7,295 = 10.16%
- E12 Failed Expansion: 5,403 = 7.52%
- E10 Compression Release: 5,126 = 7.14%
- E8 Level Bounce: 3,331 = 4.64%
- E5 VWAP Reclaim: 1,829 = 2.55%
- E9 Level Break: 1,254 = 1.75%
- E11 Kinetic Ignition: only 246 = 0.34%

Frozen BETA Checkpoint 02:

- E11 Kinetic Ignition: 2,114 = 41.70%
- E6 Value Reversion: 1,315 = 25.94%
- E9 Level Break: 714 = 14.08%
- remaining specialists share the balance.

Thus Checkpoint 02 is not merely a lower-frequency copy of SYNTH.

It has learned a substantially different opportunity distribution, especially:

- far more real Kinetic Ignition;
- far more Level Break relative to SYNTH;
- far less broad Value Reversion.

This is a useful sign of orthogonal real-market behavior, but it also explains why gross trade count overstates SYNTH coverage.

## Specialist coverage

| Specialist | SYNTH Entry→Hold | BETA trades | Coverage | BETA survivability |
|---|---:|---:|---:|---:|
| E11 Kinetic Ignition | 246 | 2,114 | 100% + excess | 93.95% |
| E9 Level Break | 1,254 | 714 | 56.94% | 81.79% |
| E5 VWAP Reclaim | 1,829 | 231 | 12.63% | 90.48% |
| E12 Failed Expansion | 5,403 | 316 | 5.85% | 90.51% |
| E7 Sweep/Reclaim | 7,295 | 255 | 3.50% | 87.45% |
| E6 Value Reversion | 46,648 | 1,315 | 2.82% | 82.05% |
| E10 Compression Release | 5,126 | 107 | 2.09% | 96.26% |
| E8 Level Bounce | 3,331 | 14 | 0.42% | 78.57% |
| E4 VWAP Pullback | 66 | 2 | 3.03% | 100% |
| E3 ORB | 287 | 2 | 0.70% | 50% |
| E1 Macro Trend | 36 | 0 | 0% | — |
| E2 Pullback/Reacceleration | 289 | 0 | 0% | — |

The largest numerical deficit is E6.

E6 alone represents 64.96% of the SYNTH mechanism pool, while its current BETA selected population is below the 85% standalone survivability goal. Therefore blindly adding E6 frequency would violate the governing quality objective.

## Session coverage

| Session authority | SYNTH Entry→Hold | BETA trades | Coverage | BETA survivability |
|---|---:|---:|---:|---:|
| UK | 7,655 | 1,722 | 22.50% | 90.30% |
| Asia | 4,492 | 620 | 13.80% | 85.16% |
| Australia | 12,996 | 732 | 5.63% | 89.21% |
| New York | 25,082 | 1,187 | 4.73% | 88.54% |
| Middle East | 10,475 | 468 | 4.47% | 86.54% |
| Europe | 9,683 | 341 | 3.52% | 85.63% |
| BASE / outside authority | 1,393 | 0 | 0% | — |
| Unassigned | 34 | 0 | 0% | — |

The UK authority is presently the strongest session bridge to SYNTH-like mechanisms.

## Causal-score distribution shift

A more important diagnostic was run by applying the frozen real-trained BETA causal models to the 71,810 SYNTH Entry→Hold survivors.

| Score | Frozen BETA selected mean | SYNTH survivor mean | KS distance |
|---|---:|---:|---:|
| P_survive | 0.8714 | 0.1976 | 0.9989 |
| P_first_passage | 0.6502 | 0.1092 | 0.9685 |
| session-blended P_survive | 0.9262 | 0.1962 | 0.9986 |
| session-blended P_first_passage | 0.7667 | 0.1218 | 0.9291 |
| session economic score | 0.7106 | 0.0369 | 0.9683 |

This is an extreme distribution separation.

The frozen Checkpoint-02 state gates admit only **7 of 71,810 SYNTH mechanism survivors**.

That is approximately 0.0097%.

No SYNTH mechanism survivor passes the frozen base Entry gate. The seven gate-compatible events enter only through session-gap eligibility and are all E6 Value Reversion.

Gate proximity:

| Distance below session survival authority | SYNTH survivors also meeting economic precheck |
|---|---:|
| exact / no relaxation | 7 |
| within 0.02 | 88 |
| within 0.05 | 272 |
| within 0.10 | 676 |
| within 0.15 | 1,093 |
| within 0.20 | 1,492 |

Therefore the former 71,810 denominator is **not** a population of events that the frozen real-market model considers statistically similar to its live-quality Entry→Hold states.

It is a population sharing the same broad mechanism labels on a fundamentally different synthetic path distribution.

## Strict one-to-one replay interpretation

Only 19 frozen Checkpoint-02 selected trades align one-to-one with the SYNTH survivor ledger under the strict timestamp/state comparison.

This does not contradict the previous Checkpoint-02 finding that 2,965 SYNTH opportunities had a same-time real-state survivor.

The earlier number asks:

> did any comparable real candidate state survive at that SYNTH time?

The new 19 asks:

> did the final frozen one-position Checkpoint-02 selector actually choose that same opportunity?

Most Checkpoint-02 trades are independent real-market opportunities occurring at different moments from SYNTH entries.

## Session × specialist recovery map

The largest SYNTH gaps fall into two different categories.

### A. Large deficit but current real analog is below the 85% quality requirement

These must not be expanded by simply loosening thresholds:

- NY × E6 Value Reversion: gap 16,740; selected survivability ~82.96%; broader admissible ~83.40%.
- Middle East × E6: gap 8,064; selected ~79.78%; admissible ~75.42%.
- Australia × E6: gap 6,985; selected ~80.00%; admissible ~84.38%.
- Europe × E6: gap 6,441; selected ~78.29%; admissible ~79.77%.
- UK × E6: gap 4,457; selected ~83.47%; admissible ~84.32%.
- Asia × E6: gap 1,654; selected ~79.05%; admissible ~73.02%.
- NY × E8 Level Bounce: gap 1,179; selected sample ~50%; broader admissible ~75%.

These are **mechanism redesign / sub-specialization targets**, not threshold-relaxation targets.

### B. Large deficit where a high-quality real analog already exists

These are the safest coverage-expansion research targets:

- NY × E7 Sweep/Reclaim: gap 2,528; selected survival 93.22%; broader admissible 86.16%.
- Australia × E10 Compression Release: gap 1,377; selected 93.75%; admissible 90.00%.
- NY × E10 Compression Release: gap 1,204; selected 90.48%; admissible 92.31%.
- Australia × E12 Failed Expansion: gap 1,043; selected 92.73%; admissible 93.00%.
- Europe × E7 Sweep/Reclaim: gap 993; selected 92.86%; admissible 91.11%.
- UK × E10 Compression Release: gap 668; selected 100%; admissible 93.00%.
- UK × E7 Sweep/Reclaim: gap 640; selected 89.53%; admissible 88.48%.
- Asia × E12 Failed Expansion: gap 629; selected 94.59%; admissible 90.59%.
- Europe × E12 Failed Expansion: gap 618; selected 92.59%; admissible 91.94%.
- UK × E12 Failed Expansion: gap 484; selected 92.13%; admissible 90.28%.
- NY × E5 VWAP Reclaim: gap 461; selected 93.55%; admissible 92.16%.
- Australia × E5 VWAP Reclaim: gap 459; selected 93.65%; admissible 94.57%.

These cells offer genuine real-market survivability headroom and should be attacked before broad E6 expansion.

## Quant conclusion

Checkpoint 02 improves real Entry→Hold opportunity count materially, but the old 85%-of-71,810 target needs scientific refinement.

The 71,810 population is useful as a **SYNTH mechanism ceiling**, not as a literal same-condition trade-count denominator.

The frozen BETA models see almost all of those synthetic survivors as belonging to a different causal distribution.

Therefore future coverage metrics should report three separate quantities:

1. **Mechanism coverage** — BETA count versus SYNTH E1–E12 survivor count.
2. **Session×specialist coverage** — matched mechanism/session cells.
3. **Causal-state overlap** — SYNTH states that fall inside or near the frozen BETA admission manifold.

Do not merge these three into one percentage.

## Next bounded research recommendation

Preserve Major Checkpoint 02 unchanged as control.

First attack high-quality under-covered cells:

1. NY E7 Sweep/Reclaim;
2. Australia / NY / UK E10 Compression Release;
3. Australia / Asia / Europe / UK E12 Failed Expansion;
4. NY / Australia E5 VWAP Reclaim.

In parallel, split E6 Value Reversion into genuinely distinct session/state sub-specialists rather than increasing the existing E6 threshold envelope. Candidate partitions should include:

- quiet-session value rotation;
- post-sweep return-to-value;
- failed-expansion value recapture;
- high-intensity snapback;
- session-transition inventory unwind;
- trend-contained pullback-to-value versus true rotational mean reversion.

Each E6 child must independently demonstrate >=85% Entry→Hold survivability or improve the routed portfolio without lowering any monthly total below 85%.

HOLD→EXIT remains deferred.

August remains sealed.
