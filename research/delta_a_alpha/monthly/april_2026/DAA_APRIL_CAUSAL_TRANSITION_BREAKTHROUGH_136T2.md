# Delta-A-alpha — April causal transition breakthrough 136T2

**Status:** COMPLETE MAJOR CAUSAL-FEATURE BREAKTHROUGH

## Breakthrough

April renewal depth is not best controlled by a static month/depth table or by simple recent PF/win history. The decisive causal state is:

**renewal rule → current depth → previous child realized P/L bucket → previous child realized hold-time bucket**

136S0 proved that, across every April renewal rule, the next child never enters before the previous child exits. Therefore previous-child P/L and hold time are known before the current child's admission decision.

## April R9 SYNTH

- net: +$38,353.96
- trades: 31,758
- gross loss: -$2,414.22
- PF: 16.8867
- win: 86.759%
- expectancy: $1.2077

## Maximum transition frontier

- net: +$71,267.89
- trades: 35,111
- gross loss: -$2,220.94
- PF: 33.0891
- win: 96.585%
- expectancy: $2.0298
- balance DD: $156.07
- full-tick equity DD: $8,160.12
- max open: 819
- positive days: 23/23
- positive weeks: 5/5
- weeks beating R9 SYNTH: 5/5
- benchmark days beating R9 SYNTH: 12/21

## Balanced physical frontier — cap 512

This is the lowest tested cap that still beats R9 SYNTH simultaneously on net, trade count, gross loss, PF, win rate and expectancy:

- net: +$67,531.19
- trades: 31,974
- gross loss: -$2,211.36
- PF: 31.5383
- win: 96.310%
- expectancy: $2.1121
- balance DD: $156.07
- full-tick equity DD: $7,431.12
- max open exact: 633 (renewal admission cap 512 plus protected-core overlap)
- positive days: 23/23
- positive weeks: 5/5
- weeks beating SYNTH: 5/5
- benchmark days beating SYNTH: 12/21

Relative to April R9 SYNTH, cap512 is about 1.761x net, 1.007x trades, 1.868x PF, +9.55 win-rate percentage points, and 1.749x expectancy, while gross-loss magnitude is about $202.86 lower.

## Scientific boundary

The **features are causal**. The **cell whitelist/threshold selection is not yet deployable**, because profitable RL_PH cells were selected using April realized outcomes. Preserve this as a mechanics breakthrough and research upper bound. Do not encode “April” or a static April whitelist into the final EA.

The next task is `DAA_APRIL_TRANSITION_WALKFORWARD_ADMISSION_136U`: learn/qualify the same causal transition cells from already-closed shadow outcomes only, then carry the mechanism unchanged into May for cross-month validation.