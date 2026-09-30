# BETA064 — ALL-12 ENTRY SPECIALIST REFINEMENT PRESCREEN 01

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** RESEARCH CHILD / NEGATIVE BROAD-CLOCK PRESCREEN — NO CHECKPOINT CHANGE  
**Frozen control:** BETA064 Major Checkpoint 02 — 5,070 Jan–Jul one-position Entry→Hold trades / 88.44% weighted survivability / 7 of 7 observed months >85%  
**Scope:** ENTRY→HOLD only  
**Hold→Exit:** deferred  
**August:** SEALED and not read  
**Alpha/GAMMA:** prohibited and not used  
**MQL5:** no authorization / no change

## Research question

Can the existing E1–E12 specialist mechanisms be broadened into additional causal opportunity clocks, then refined through cross-month state discrimination, to increase Entry→Hold opportunity count while requiring new opportunities to survive the owner's preferred >=85% Entry→Hold floor?

## Critical non-equivalence / reproducibility boundary

The exact transient parent candidate generator historically imported as `/mnt/data/beta064_multidesk_loop.py` is not present in the authoritative corrected V2 model freeze bundle, the older V1 bundle inspected for recovery, current GitHub `beta`, or Drive search. Therefore this unit does **not** claim an exact replay or reconstruction of the frozen E1–E12 candidate universe.

Instead, this is a separate research-child prescreen: reconstructible broad causal realizations of the same twelve documented mechanisms were generated directly from original Dukascopy Bid/Ask ticks and tested as possible new opportunity clocks. The frozen Major Checkpoint 02 remains untouched and authoritative.

## Data and causal execution

- Original Dukascopy XAUUSD Bid/Ask ticks, January through July 2026 only.
- August was not read.
- Completed causal 5-second states derived from the ordered tick chronology.
- No future bar/tick in runtime features.
- BUY entry uses observed Ask and BUY markout uses observed Bid.
- SELL entry uses observed Bid and SELL markout uses observed Ask.
- Entry→Hold research geometry retained from the frozen BETA research contract:
  - `spread = max(candidate_spread, 0.05)`
  - `atr = max(atr60, spread)`
  - favorable barrier `max(0.35, 1.25*spread, 0.30*atr)`
  - adverse barrier `max(0.30, 1.00*spread, 0.22*atr)`
  - path resolution accounting includes the existing `$0.02` research lifecycle fee.
- Specialist horizon/checkpoint identities were retained from `BETA_064_R1B2_SPECIALIST_REGISTRY.py`.

## Broad mechanism prescreen

The generated clocks correspond to E1 Macro Structural Trend, E2 Structural Pullback/Reacceleration, E3 Opening Range Break, E4 VWAP/Value Trend Pullback, E5 VWAP/Value Reclaim, E6 Statistical Value Reversion, E7 Liquidity Sweep/Reclaim, E8 Key-Level Bounce/Rejection, E9 Key-Level Break/Acceptance, E10 Compression→Expansion, E11 Kinetic Ignition, and E12 Failed Expansion/Contradiction.

The broad clocks are intentionally opportunity generators, not claims that these definitions equal the missing historical frozen generator.

### Raw Jan–Jul result

| Specialist | Candidates | Raw survival | Raw favorable-first-passage | Diagnostic value |
|---|---:|---:|---:|---:|
| E1 | 501 | 17.37% | 19.76% | -$756.52 |
| E2 | 288 | 10.76% | 9.38% | -$295.27 |
| E3 | 2,701 | 19.99% | 17.59% | -$2,000.42 |
| E4 | 192 | 17.19% | 10.94% | -$202.73 |
| E5 | 11,024 | 27.66% | 15.38% | -$8,833.79 |
| E6 | 169,276 | 22.83% | 15.19% | -$128,750.64 |
| E7 | 7,198 | 30.90% | 16.69% | -$5,486.90 |
| E8 | 24,538 | 26.40% | 18.55% | -$18,262.59 |
| E9 | 5,456 | 22.95% | 18.99% | -$4,139.22 |
| E10 | 28,095 | 27.31% | 17.23% | -$22,310.32 |
| E11 | 49,774 | 35.82% | 14.51% | -$40,537.38 |
| E12 | 54,102 | 35.96% | 17.96% | -$39,702.81 |

**Decision:** no broad clock has standalone Entry→Hold quality remotely close to the 85% floor. Broadening Entry clocks is rejected as the direct expansion path.

## Cross-month refinement pass

Each specialist was treated independently in a leave-one-month-out experiment. One month was held out from fit and threshold selection; survival and favorable-first-passage models were fit on the other six months; a causal quality score was formed; a development threshold was allowed only when every development month retained at least three one-position trades, >=85% survival, and positive diagnostic value; the unchanged threshold was then applied to the held-out month with chronological specialist scheduling.

Result:

- E1, E2, E4, E5, E6, E8, E9, E10, E11, and E12 found **zero** folds where a six-month development gate could be formed under these constraints.
- E3 formed a development gate in 2 folds, but passed **0** held-out months. Its held-out selected total was 31 trades at 25.81% weighted survival and negative diagnostic value.
- E7 formed a development gate in 5 folds, but passed **0** held-out months. Its held-out selected total was 50 trades at 58.0% weighted survival and negative diagnostic value.

This is a direct portability failure. Apparent high-survival development tails did not transfer to omitted months.

## Focused E6 follow-up

Because E6 represents the dominant condition-matched coverage deficit, a separate E6 idle-opportunity experiment was run on the preserved derivative opportunity surface.

- idle E6 derivative candidates: 687,741
- development: January-April
- calibration screen: May-June
- later July discrimination check
- survival discrimination AUC: approximately 0.752 development, 0.730 May-June, 0.727 July

Despite useful ranking information, **no threshold** produced at least five scheduled new trades in both May and June while simultaneously achieving >=85% standalone Entry→Hold survival and positive diagnostic path value.

**Decision:** derivative-created E6 clocks are rejected as standalone Entry authority. Their useful role remains same-timestamp state/admission context around a validated parent proposal, consistent with C02G.

## Interpretation

This prescreen strongly separates two ideas:

1. **More clocks** — rejected. Broadening the twelve specialists creates enormous candidate surfaces but poor raw Entry→Hold quality and unstable high-score tails.
2. **Better admission around validated parent proposals** — remains the scientifically supported direction. Existing C02E/C02G evidence shows derivative and session state can improve discrimination even when it cannot originate safe trades.

The result preserves the frozen E1–E12 mechanism architecture but changes the optimization emphasis from signal proliferation to state-conditioned capacity recovery.

## Refined research hierarchy

### High-priority capacity recovery

**E10 Compression Release** — Current accepted child evidence is relatively strong and first-passage quality is high. Under-covered Australia/New York/UK cells remain attractive. C02E evidence says D3 state can improve discrimination. Refine compression depth, expansion participation, acceptance quality, spread/ATR burden, session age, and D3 same-timestamp state; do not invent a parallel compression clock.

**E12 Failed Expansion** — Strong current survivability with large under-covered condition cells. C02E evidence says D3 state improves discrimination. Refine effort-versus-displacement contradiction, recross quality, renewal decay, structural boundary depth, execution friction, and session state.

**E5 VWAP Reclaim** — Useful accepted quality and meaningful under-coverage. Derivative complexity previously hurt rather than helped. Focus on parent value geometry, reclaim depth, retest quality, session VWAP/value location, trend contamination, and ownership/capacity rather than new derivative clocks.

### Quality repair before substantial expansion

**E6 Value Reversion** — Largest scientific and coverage problem by far. Do not broaden the clock or loosen the 85% requirement. Split by session and parent state; use the authoritative C02G same-timestamp derivative matrix: Australia D3 5s; Asia D2 5s; Middle East D3 + completed 1s micro; Europe parent state only; UK D1 5s; New York D3 + completed 1s micro. Target rotational ownership, excursion age/depth, exhaustion vs trend contamination, return-to-value efficiency, friction, session age, and structural context.

**E7 Sweep/Reclaim** — Near the 85% boundary but unstable across sessions; broad reconstructed tails did not transfer. Keep the C02D `ps_b75 >= 0.915` child discipline. New York remains the best recovery target. Refine sweep penetration, reclaim velocity, time outside boundary, stabilization, repeated-test contamination, session liquidity state, and friction.

**E9 Level Break** — Current expansion is too permissive. Keep the C02D `ps_b75 >= 0.915` repair. Use D1 same-timestamp context only as a quality discriminator. Refine body/close acceptance, persistence outside the level, retest depth, quote participation, expansion efficiency, fakeout/sweep contradiction, and session/HTF ownership.

### Controls / lower-priority desks

**E11 Kinetic Ignition** — retain as a high-quality saturated control; penalize novelty/coverage expansion.

**E1/E2/E3/E4/E8** — do not target trade-count expansion yet. They need stronger portable state definition or recovery of the exact historical parent candidate generator before any claim of safe capacity expansion.

## Promotion gate for future additions

A future expansion candidate should not pass merely because the combined strong portfolio remains >=85%.

Require:
1. new additions themselves meet >=85% Entry→Hold survivability in every held-out month in which there is enough activity to evaluate them;
2. positive aggregate diagnostic path value for the new additions;
3. combined one-position portfolio remains >=85% in every month;
4. final trade count exceeds the relevant control rather than obtaining quality only by deleting trades;
5. condition-deficit coverage rises in under-covered cells;
6. no material displacement of better frozen base trades;
7. exact causal runtime features and reproducible scripts/results.

## Current decision

- **Major Checkpoint 02 remains unchanged:** 5,070 trades / 88.44% weighted survivability / 7 of 7 months >85%.
- The broad all-12 clock-expansion path is rejected.
- Existing derivative clocks remain context/opportunity-research tools, not standalone Entry authority.
- The next productive expansion work is **state-conditioned capacity recovery around validated parent specialists**, prioritized E10/E12/E5 for capacity and E6/E7/E9 for quality repair.
- E11 remains frozen/saturated.
- August remains sealed.
- Hold→Exit remains deferred.
- No MQL5 change.

## Durable artifacts

- `research/experiments/BETA_064_ALL12_ENTRY_SPECIALIST_BROAD_CLOCK_PRESCREEN_01.py`
- `research/experiments/BETA_064_ALL12_ENTRY_SPECIALIST_LOMO_PRESCREEN_01.py`
- `research/results/BETA_064_ALL12_ENTRY_SPECIALIST_RAW_SUMMARY_01.csv`
- `research/results/BETA_064_ALL12_ENTRY_SPECIALIST_LOMO_FOLDS_01.csv`
- `research/results/BETA_064_ALL12_ENTRY_SPECIALIST_LOMO_SUMMARY_01.csv`

Local pre-commit SHA-256 fingerprints:
- broad-clock script: `bf370058a7abfc63af60e197b276c34e8145dd6879e1aaa295ce82e82a406ca3`
- LOMO script: `69317922634ac37cfd27095972c9378523903ab5d2b7f227a0e3e37a0dfc3fe6`
- raw summary: `70099f23dc1843691c9390a75d3d3f2a19da96ddc35794f30b7fabbbf6808e95`
- LOMO folds: `97d3b40d32625b2ecace1c274f8783f91e5fb3bb640b39e92879d2460ec74869`
- LOMO summary: `2202c0dc2e1c49765e7313335ff917b77b7daa5f4678e390c31a2b97792eacf3`
