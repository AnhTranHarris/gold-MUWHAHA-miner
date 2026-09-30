# BETA064 CHECKPOINT 02B — Session×Specialist SYNTH Condition-Matched Coverage Diagnostic

**Date:** 2026-09-30  
**Branch:** `beta`  
**Parent control:** BETA064 Major Checkpoint 02 — frozen and unchanged  
**Scope:** Entry→Hold only  
**Hold→Exit:** deferred  
**August:** sealed  
**Status:** diagnostic research child; no EA promotion

## Objective

Re-run the R9 SYNTH condition-matched Entry→Hold coverage comparison using the frozen session-aware Major Checkpoint 02 architecture.

The comparison uses the previously established **71,810 R9 SYNTH Entry→Hold-surviving opportunities** as the benchmark pool.

The frozen Checkpoint-02 BETA portfolio contains:

- 5,070 one-position Entry→Hold trades;
- 88.44% weighted survivability;
- 2,097 frozen Major Checkpoint-01 base trades;
- 2,973 session-gapfill trades.

No Checkpoint-02 thresholds, models, session definitions, or selected trades were changed during this diagnostic.

## Session authority attribution

The final Checkpoint-02 session-context router was reconstructed from its research recipe and validated against the stored `beta064_session_meta_all.pkl` checkpoint state.

Validation result:

- session-authority identity match: **100%**
- maximum absolute difference in session survival probability: **0**
- maximum absolute difference in blended `ps_b75`: **0**
- maximum absolute difference in blended economic score: **0**

Therefore the same frozen Australia / Asia / Middle East / Europe / UK / New York authority logic was applied to the SYNTH opportunity pool.

Important methodological finding:

Applying BETA's learned probability gates directly to SYNTH states produces almost no accepted SYNTH entries. This is expected because the probability calibration is feed-specific. Those gates are therefore **not** used to redefine the SYNTH denominator.

The denominator remains the 71,810 SYNTH opportunities that already passed the original path-aware Entry→Hold survival definition.

## Coverage metrics

Three distinct quantities are reported.

### 1. Gross trade-count ratio

`5,070 / 71,810 = 7.06%`

This is only the raw trade-count ratio.

### 2. Session×specialist condition-matched coverage

Credit is capped inside each **month × session authority × specialist** cell.

If BETA has more trades than SYNTH in a cell, the extra BETA trades do not compensate for missing trades in another cell.

Under this stricter metric:

- Major Checkpoint 01 matched: **1,127 / 71,810 = 1.57%**
- Major Checkpoint 02 matched: **3,044 / 71,810 = 4.24%**
- incremental matched recovery: **+1,917 opportunities**
- relative improvement versus Checkpoint 01: **+170.1%**
- absolute improvement: **+2.67 percentage points**

Checkpoint 02 therefore materially improves condition-matched coverage, but the 85% coverage target is not close to being met.

85% target count:

`ceil(71,810 × 0.85) = 61,039`

Remaining matched opportunities required:

`61,039 - 3,044 = 57,995`

### 3. Strict synchronous same-time recovery

A much stricter diagnostic requires the SYNTH opportunity to:

- have a same-time/same-side/same-specialist Dukascopy state;
- survive the real Entry→Hold path;
- and be the exact state selected by frozen Checkpoint 02.

Only 19 one-to-one opportunities satisfy this strict requirement.

This strict metric is useful as a path-transfer forensic, but it is too restrictive to use as the primary condition-matched coverage measure.

The earlier heuristic statement that 2,097 / 2,965 implied ~70.7% direct capture must therefore be retired: that was a **count ratio**, not proof of direct opportunity capture.

## Month-by-month condition-matched coverage

| Month | SYNTH Entry→Hold | Ckpt-01 trades | Ckpt-02 trades | Capped matched | Coverage |
|---|---:|---:|---:|---:|---:|
| Jan | 9,156 | 278 | 726 | 491 | 5.36% |
| Feb | 10,496 | 337 | 910 | 546 | 5.20% |
| Mar | 13,196 | 568 | 1,463 | 914 | 6.93% |
| Apr | 10,225 | 274 | 589 | 319 | 3.12% |
| May | 9,826 | 249 | 509 | 269 | 2.74% |
| Jun | 10,410 | 261 | 585 | 311 | 2.99% |
| Jul | 8,501 | 130 | 288 | 194 | 2.28% |

Coverage deterioration after March is real and remains an important distribution-shift problem even though survivability stays above 85%.

## Session attribution

| Session authority | SYNTH Entry→Hold | BETA trades | BETA survival | Capped coverage |
|---|---:|---:|---:|---:|
| UK | 7,655 | 1,722 | 90.30% | **22.50%** |
| Asia | 4,492 | 620 | 85.16% | **13.80%** |
| Australia | 12,996 | 732 | 89.21% | 5.63% |
| New York | 25,082 | 1,187 | 88.54% | 4.73% |
| Middle East | 10,475 | 468 | 86.54% | 4.47% |
| Europe | 9,683 | 341 | 85.63% | 3.52% |
| No active frozen session authority | 1,393 | 0 | — | 0% |
| Unassigned merge residual | 34 | 0 | — | 0% |

UK and Asia show the strongest relative count coverage.

New York remains the largest absolute opportunity pool and therefore the largest absolute session gap.

## Specialist attribution

| Specialist | SYNTH Entry→Hold | BETA trades | BETA survival | Capped coverage | Remaining gap |
|---|---:|---:|---:|---:|---:|
| E6 Value Reversion | 46,648 | 1,315 | **82.05%** | 2.82% | **45,333** |
| E7 Sweep/Reclaim | 7,295 | 255 | 87.45% | 3.50% | 7,040 |
| E12 Failed Expansion | 5,403 | 316 | 90.51% | 5.85% | 5,087 |
| E10 Compression Release | 5,126 | 107 | 96.26% | 2.09% | 5,019 |
| E8 Level Bounce | 3,331 | 14 | 78.57% | 0.42% | 3,317 |
| E5 VWAP Reclaim | 1,829 | 231 | 90.48% | 12.63% | 1,598 |
| E9 Level Break | 1,254 | 714 | 81.79% | 56.94% | 540 |
| E2 Pullback/Reaccel | 289 | 0 | — | 0% | 289 |
| E3 ORB | 287 | 2 | 50.00% | 0.70% | 285 |
| E11 Kinetic Ignition | 246 | 2,114 | **93.95%** | **100% capped** | 0 |
| E4 VWAP Pullback | 66 | 2 | 100% | 3.03% | 64 |
| E1 Macro Trend | 36 | 0 | — | 0% | 36 |

## Central bottleneck — E6 is quantity-dominant but quality-limited

E6 Value Reversion represents:

`46,648 / 71,810 = 64.96%`

of the complete SYNTH Entry→Hold benchmark pool.

It also represents:

`45,333 / 68,766 = 65.92%`

of the current condition-matched coverage deficit.

However the currently selected real E6 population survives only **82.05%**, below the owner's 85% gate.

Session-level selected E6 survivability is also below 85% across the major session authorities.

Therefore the 85% coverage objective cannot be reached by simply admitting more existing E6 candidates.

E6 requires a **structural redesign / decomposition into better-defined real-market reversion states**, not a looser threshold.

## High-quality undercoverage reserve

A separate group of session×specialist cells already has:

- at least 10 selected BETA examples;
- selected survivability >=85%;
- a positive SYNTH opportunity deficit.

Those cells contain **13,839 remaining benchmark opportunities**, approximately 19.27% of the full 71,810 pool.

Gap by specialist:

- E12 Failed Expansion: **4,521**
- E7 Sweep/Reclaim: **4,161**
- E10 Compression Release: **3,735**
- E5 VWAP Reclaim: **1,419**
- E9 Level Break: 3

These are the safer families for the next coverage-expansion research.

Largest cells include:

- NY × E7 Sweep/Reclaim: gap 2,528; selected survival 93.22%
- NY × E12 Failed Expansion: gap 1,747; selected survival 89.55%
- Australia × E10 Compression Release: gap 1,377; selected survival 93.75%
- NY × E10 Compression Release: gap 1,204; selected survival 90.48%
- Australia × E12 Failed Expansion: gap 1,043; selected survival 92.73%
- Europe × E7 Sweep/Reclaim: gap 993; selected survival 92.86%
- UK × E10 Compression Release: gap 668; selected survival 100%
- UK × E7 Sweep/Reclaim: gap 640; selected survival 89.53%
- Asia × E12 Failed Expansion: gap 629; selected survival 94.59%
- Europe × E12 Failed Expansion: gap 618; selected survival 92.59%

This is the strongest current evidence for expanding E7/E12/E10/E5 before loosening E6.

## E11 overcoverage is real-market orthogonal alpha research, not SYNTH recovery

E11 Kinetic Ignition has:

- SYNTH benchmark pool: 246
- BETA trades: 2,114
- BETA survival: 93.95%

Therefore 1,868 BETA E11 trades are **excess relative to the SYNTH condition cell**.

They are not counted as recovered SYNTH coverage.

This is nevertheless encouraging: the session-aware BETA architecture is discovering a large real-market Entry→Hold family that the synthetic teacher scarcely represents.

The correct response is to preserve E11 as an orthogonal real-market specialist, not force it to impersonate missing E6 volume.

## Session layer contribution

The 2,973 session-gapfill additions produce only 1,917 incremental condition-matched recoveries because some additions occur in cells already fully covered relative to the SYNTH benchmark.

Incremental matched recovery by session:

- UK: +622
- New York: +550
- Asia: +341
- Europe: +169
- Middle East: +121
- Australia: +114

Incremental matched recovery by specialist:

- E6: +1,083
- E12: +210
- E7: +210
- E9: +199
- E5: +124
- E10: +78
- E11: +13

The session layer is therefore a genuine coverage improvement, especially UK/NY, but it does not solve the dominant E6 transfer problem.

## Ownership-horizon diagnostic

Because Hold→Exit is deferred, a secondary diagnostic tested whether the current long specialist research horizon artificially suppresses Entry→Hold trade capacity.

Using the same frozen gates but reserving ownership only until the specialist Hold checkpoint (10–60s):

- unadjusted capacity: 7,247 Entry→Hold selections
- weighted survivability: 87.06%
- January survivability: 83.55%
- February survivability: 84.44%

Thus the unadjusted checkpoint-only capacity violates the 85% monthly floor in Jan/Feb.

A conservative capacity sweep found:

- session pre-survival floor: 0.92
- unchanged session authority thresholds
- same base gates
- Hold-checkpoint-only ownership

Result:

- **5,952 Entry→Hold capacity selections**
- **88.51% weighted survivability**
- every month >=85%
- weakest month approximately 85.23%

This is only 882 more quality-preserving opportunities than the frozen 5,070-trade checkpoint.

Conclusion:

The full-horizon placeholder ownership suppresses some trade count, but it **does not explain the order-of-magnitude SYNTH coverage deficit**.

The dominant problem remains real-market state/path transfer and specialist definition.

This checkpoint-only result is a capacity diagnostic only. It is not an exit policy and does not modify Major Checkpoint 02.

## Quant decision

Major Checkpoint 02 remains frozen.

Checkpoint 02B establishes:

1. session-aware coverage improved materially versus Checkpoint 01;
2. true condition-matched coverage is 4.24%, not 7.06%, after cell capping;
3. 85% SYNTH condition-matched coverage is not currently close;
4. E6 Value Reversion is the dominant quantitative blocker and cannot safely be expanded in its current form;
5. E7/E12/E10/E5 contain the best high-quality undercoverage reserve;
6. E11 is a valuable BETA-native real-market specialist but cannot be counted as substitute SYNTH coverage;
7. deferred Hold→Exit/full-horizon ownership explains only a modest portion of the deficit.

## Next bounded research unit

Do not alter Major Checkpoint 02.

Create child specialists / refinements in this order:

1. **E7 Sweep/Reclaim session refinements**
   - NY, Europe, UK first.
2. **E12 Failed Expansion session refinements**
   - NY, Australia, Asia, Europe, UK.
3. **E10 Compression Release session refinements**
   - Australia, NY, UK, Asia, Europe.
4. **E5 VWAP Reclaim session refinements**
   - NY, Australia, UK, Europe, Asia.
5. **E6 Value Reversion decomposition**
   - split by session, volatility, value-distance, efficiency, structural owner, and path-renewal state;
   - no simple threshold loosening.
6. Revisit E8/E2/E3 only after the above because their current real survivability/participation is too weak.

Every child must report:

- incremental condition-matched coverage;
- Entry→Hold survivability;
- monthly stability;
- session×specialist attribution;
- overlap with frozen Checkpoint 02;
- opportunity count gained without modifying the parent checkpoint.

Hold→Exit remains deferred.
August remains sealed.
