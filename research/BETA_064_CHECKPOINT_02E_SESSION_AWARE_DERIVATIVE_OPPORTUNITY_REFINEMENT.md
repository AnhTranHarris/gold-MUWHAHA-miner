# BETA064 CHECKPOINT 02E — Session-Aware Entry Derivative Opportunity Research

**Date:** 2026-09-30  
**Branch:** `beta`  
**Frozen control:** BETA064 Major Checkpoint 02 — immutable  
**Research parent:** Checkpoint-02C / Checkpoint-02D opportunity-expansion children  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**Alpha/GAMMA:** prohibited and not used  
**August:** sealed and not read  
**Status:** RESEARCH CHILD — NO NEW MAJOR CHECKPOINT

## Research question

Can derivatives of existing Entry specialists, made explicitly session-aware, create materially more Entry→Hold opportunities while preserving the preferred >=85% monthly survivability requirement?

## Architectural distinction

A derivative is useful only if it changes the opportunity clock or the causal state definition.

Two derivative roles were therefore separated:

1. **Expansion derivative** — emits a new causal opportunity that the parent specialist did not emit.
2. **Quality derivative** — session-specific discriminator deciding whether an expanded opportunity is safe enough to admit.

A threshold-only copy of an existing specialist is not counted as a new opportunity specialist.

## Public-mechanics research

Reconstructible community mechanics repeatedly use:
- Asia/London/New York session liquidity boundaries;
- sweep + reclaim;
- structure-shift confirmation;
- VWAP/value reclaim or retest;
- compression/expansion;
- volatility/activity confirmation;
- session-specific handling rather than universal rules.

These mechanics were treated only as testable hypotheses. Community performance claims were not imported.

## Derivative generation pass D1

Four broad derivative clocks were built:

- E5D1 Session-VWAP Reclaim→Retest
- E6D1 Session-Value Turn
- E7D1 Pre-open Sweep→Reclaim
- E9D1 Break→Accept→Retest

Raw Jan-Jul survivability:
- E5D1: ~21.6%
- E6D1: ~23.9%
- E7D1: ~20.9%
- E9D1: ~15.9%

Session-specific leave-one-month-out rule/model isolation found no material robust >=85% tail.

Decision: D1 clocks rejected for executable authority.

## Derivative generation pass D2

The mechanisms were made materially stricter:

### E5D2 — Trend-aligned Session-VWAP Reclaim Retest
Requires:
- session VWAP reclaim;
- retest;
- r15/r60 continuation;
- 15-minute directional ownership;
- low friction;
- minimum short-horizon efficiency.

Raw Jan-Jul:
- 410 candidates
- 50.24% survivability.

### E6D2 — Sustained Extreme Reversal
Requires:
- deeper value displacement;
- sustained excursion;
- reversal confirmation;
- session context;
- friction/efficiency controls.

Raw Jan-Jul:
- 12,955 candidates
- 56.02% survivability.

### E7D2 — Sweep Reclaim Stabilize
Requires:
- pre-open/ORB liquidity sweep;
- reclaim;
- 5–20 second stabilization inside the reclaimed boundary;
- minimum clearance and efficiency.

Raw Jan-Jul:
- 748 candidates
- 51.20% survivability.

### E9D2 — Expansion Break Retest
Requires:
- volatility/range expansion;
- accepted break;
- two outside closes;
- first shallow retest;
- r15/r60/r300 alignment;
- low friction;
- no excessive extension.

Raw Jan-Jul:
- 401 candidates
- 39.40% survivability.

These are better than D1 but still not safe as standalone desks.

## Strict session-specific derivative LOMO

Each D2 specialist was then split by session and trained as a separate survival child with the held-out month excluded from both fitting and threshold selection.

Result:
no derivative/session pair produced a sufficiently large standalone >=85% held-out opportunity stream.

The useful tails were extremely sparse.

This is strong evidence that simply making the derivatives session-aware does not automatically create a new high-quality specialist.

## Portfolio-level derivative LOMO

The research question was then changed to the actual BETA use case:

> Can session-aware derivative children fill chronological slots left idle by Checkpoint-02C while the **combined portfolio** stays >=85% survivability every month?

The frozen C02C selected portfolio used as control:
- 5,519 trades
- ~88.20% weighted survivability
- every month >=85%
- diagnostic path-resolution value +$6,012.177

Nested leave-one-month-out session models selected derivative additions using only the other months.

### Combined held-out result

| Month | C02C control trades | Derivative additions | Total | Combined survivability |
|---|---:|---:|---:|---:|
| Jan | 766 | 1 | 767 | 88.79% |
| Feb | 1,032 | 5 | 1,037 | **85.54%** |
| Mar | 1,495 | 19 | 1,514 | 87.45% |
| Apr | 667 | 4 | 671 | 88.38% |
| May | 586 | 4 | 590 | 90.51% |
| Jun | 640 | 12 | 652 | 89.26% |
| Jul | 333 | 5 | 338 | 89.35% |
| **Total** | **5,519** | **50** | **5,569** | **88.04% weighted** |

Every held-out month remains >=85%.

The additions are concentrated in:
- E6D2 UK
- E6D2 Australia
- E6D2 Asia
- isolated E6D2 NY/Middle East/Europe tails
- one NY E7D2 case

This validates the **concept** that session-aware derivatives can increase opportunity count without violating the portfolio survivability floor.

## Coverage effect

Checkpoint-02C session×specialist condition-cell matched coverage:
- 3,164 / 71,810 = ~4.41%

Because the 50 derivative additions occur in under-covered E5/E6/E7 cells, an optimistic condition-cell accounting becomes approximately:
- 3,214 / 71,810 = **~4.48%**

This is a real but small coverage gain.

## Important adverse finding

The 50 held-out derivative additions reduce aggregate diagnostic path-resolution value:

- control: +$6,012.177
- derivative-expanded child: +$5,976.592

Difference:
- approximately **-$35.585**

Therefore the derivative layer currently creates more valid Entry→Hold opportunities but does not yet improve the broader path-value diagnostic.

This is why it must not be promoted.

## Coverage-utility refinement

A second nested LOMO router added favorable-first-passage probability to the admission utility:

`utility = P_survive × (0.40 + 0.60 × P_first_passage)`

Training admission also required:
- all training-month combined portfolios >=85.5% survivability;
- derivative-tail survivability >=78%;
- derivative-tail favorable-first-passage >=25%;
- nonnegative aggregate derivative diagnostic value.

Result:
the acceptable held-out derivative tail collapsed to only a handful of additions.

Observed examples:
- one NY E7D2 held-out trade survived and produced positive diagnostic value;
- a few UK/Asia E6D2 additions passed the survival geometry but did not transfer positive path value reliably;
- NY E6D2 produced no robust utility-qualified held-out expansion.

Interpretation:
the main bottleneck is no longer the survivability gate alone. It is identifying derivative opportunities that are both **survivable and directionally valuable after entry**.

## Cross-session handoff derivative pass D3

A separate pass tested truly session-handoff-specific clocks rather than a generic rule with a different session label.

Predecessor mapping:
- Australia <- prior New York
- Asia <- Australia
- Middle East <- Asia
- Europe <- Asia
- UK <- Asia
- New York <- UK/London

Three handoff derivatives were tested:

- E7D3 predecessor-session Sweep→Reclaim
- E9D3 predecessor-session Break→Accept→Retest
- E5D3 predecessor-session VWAP Reclaim→Retest

Raw survivability remained poor.

Examples:
- E7D3 across sessions: roughly 29–33% raw survivability
- E9D3: roughly 24–40%
- E5D3: roughly 37–50%

Decision:
cross-session handoff mechanics are useful state/context features, but the current clocks are not executable specialists.

## Scientific conclusion

**Yes, derivatives can help find more opportunities, but the current evidence says they should be hierarchical children, not parallel full-authority specialists.**

Recommended architecture:

`Parent thesis`
→ `session authority`
→ `session-specific derivative proposal clocks`
→ `derivative quality model`
→ `coverage utility / novelty filter`
→ `idle-slot ownership only`
→ `Entry→Hold thesis packet`

The derivative layer should be allowed to search broadly but should not own positions until it passes both:

1. portfolio survivability requirement; and
2. path-value / favorable-first-passage requirement.

## Carry-forward derivative families

### Carry as active research children
- E6D2 UK Sustained-Extreme Reversal
- E6D2 Australia Sustained-Extreme Reversal
- E6D2 Asia Sustained-Extreme Reversal
- E7D2 New York Sweep-Reclaim Stabilize

These produced the most repeatable held-out portfolio-compatible additions.

### Keep as shadow/context only
- E6D2 NY/Europe/Middle East until better state discrimination
- E5D2
- E9D2
- all D3 cross-session handoff clocks

### Do not expand
- E11 Kinetic Ignition, because its condition cell is already saturated relative to SYNTH.

## Next refinement

The next bounded unit should not create more derivative names.

It should improve the four carry-forward child streams through:

1. **coverage-deficit-aware utility**
   - reward under-covered session×specialist cells;
   - penalize duplicate timestamps/states;
   - preserve one-position ownership.

2. **first-passage-quality discrimination**
   - excursion speed after entry;
   - favorable/adverse path asymmetry;
   - rejection/continuation renewal;
   - spread/ATR burden;
   - session age;
   - cross-scale trend contamination.

3. **parent/derivative disagreement**
   - derivative is most valuable when the parent did not already emit or approve;
   - measure whether disagreement identifies truly new opportunity or merely lower-quality versions of the same setup.

4. **February buffer**
   - because February remains the binding month, derivative admission must be explicitly stress-tested against its narrow survivability cushion.

## Quant decision

- Major Checkpoint 02 remains frozen and unchanged.
- C02C/C02D remain research children.
- Session-aware derivatives are validated as a **small opportunity-expansion mechanism**.
- Current robust held-out expansion: +50 trades versus C02C while all months remain >=85%.
- Current derivative layer is **not promotion-ready** because path-value diagnostic worsens and utility-qualified tails are too sparse.
- Hold→Exit remains deferred.
- August remains sealed.
- No MQL5 change.
- No Alpha/GAMMA dependency.
