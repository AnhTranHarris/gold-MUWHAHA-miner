# R9 MOD 01 — P1–P5 Breakthrough Foundation

## Status

This branch is the new executable carry-forward line for the Gold MUWHAHA Miner.

- Base branch: `carson/mt5-r9-hybrid-gate-certification`
- Base EA: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- Base R9 source SHA inspected before reconstruction: `7eecb5f1947017a01ce85b2520725de54749e523`
- New EA: `Experts/GoldMuwahahaMiner_R9_MOD_P1P5.mq5`
- New branch: `carson/r9-mod-01-p1-p5-breakthrough-foundation`

The existing `carson/r10-from-r9-code-*` branches are **roadmap/reference material only** for this reset. No P6+ or later roadmap modules are included in this checkpoint.

This is an MT5 QC candidate. It has been source-audited and structurally checked, but it has **not** been compiled in the user's local MetaEditor/Coinexx environment yet.

## Why this reset exists

The project discovered useful causal mechanisms in Python tick-level research, but the executable EA lineage was not being advanced in lockstep with each breakthrough. This branch resets the workflow:

> R9 executable chassis → one validated breakthrough checkpoint at a time → MT5 REAL-tick QC → keep/revise/reject → next checkpoint.

The accumulated R9 modifications that survive MT5 QC become the official R10.

## R9 behavior preserved

The original R9 event chassis remains the source of activity:

- minute bracket geometry;
- 0.01 lot default;
- 30-pip bracket input;
- 30-pip R9 fallback stop;
- 3-pip R9 fallback trail after 10-pip activation;
- 30-second R9 fallback maximum hold;
- same-minute opposite rearm;
- 10-second S1 velocity/range quality gate;
- minimum directional efficiency 0.70;
- M5 ATR/session/spread regime gate;
- magic 5559.

If `InpUseP1Harvester=false`, the entry path falls back to the original R9 directional event behavior for control testing.

## P1 — Pullback/Reacceleration Harvester

P1 uses the R9-qualified event as an **activity detector**, then reads the latest completed one-second auction before deciding what action to take.

Recovered QC defaults:

- CONTINUE if aligned completed-S1 return <= -0.255 and completed-S1 range >= 0.285;
- FADE if aligned completed-S1 return >= +0.275 and completed-S1 tick count >= 5;
- ambiguous middle state = ABSTAIN;
- emergency stop room = $5.00;
- favorable ignition = $0.01;
- high-water harvest trail = $0.01;
- HFT maximum hold = 30 seconds in this checkpoint.

The important change from raw R9 is that the event direction is **not automatically inherited**.

## P2 — Expansion/Persistence Runner

P2 is implemented as a **lifecycle promotion**, not a new entry engine.

At the first favorable excursion where P1 would normally arm the tiny harvest, the EA checks only already-completed information:

- recent directional tick flow;
- aligned displacement;
- path efficiency;
- completed M1/M5 structural agreement.

Default reconstructed promotion knee:

- directional flow >= 0.30;
- path efficiency >= 0.70;
- continued aligned displacement >= $0.01;
- structural agreement must be positive;
- runner trail = 1.0 ATR;
- runner lifecycle ceiling = 120 seconds.

The research record preserves the mechanism and approximate knee, but not every original fitted coefficient. These are therefore **transparent QC defaults**, not claimed historical constants.

## P3 — Failed-Ignition Reversal

P3 only evaluates a trade after it has had time to declare itself.

Default causal failure shape:

- age >= 15 seconds;
- MFE remains below $0.01;
- MAE >= 2.0 ATR;
- recent adverse path efficiency >= 0.70;
- adverse displacement >= 0.15 ATR;
- directional tick flow strongly opposes the trade (<= -0.30).

If the condition is met:

1. close the failed original thesis;
2. if `InpP3FlipAfterExit=true`, open the opposite-direction P3 flip;
3. manage that flip with the normal P1 harvest lifecycle;
4. never recursively P3-flip an existing P3 flip.

The failed-state decision uses the current Strategy Tester tick timestamp, not wall-clock time.

## P4 — Low-Volatility Rotation

P4 is deliberately **subordinate to P1** in this checkpoint.

It is consulted only when a qualified R9 event reaches the P1 ABSTAIN state. It therefore attempts to fill idle P1 opportunity rather than suppress a P1 trade that already has positive action-value evidence.

Current reconstructed QC defaults:

- completed M5 ATR / prior ATR baseline <= 1.05;
- ten-second path efficiency <= 0.78;
- action = FADE/rotate the R9 event side.

The exact historical P4 coefficient table did not survive the research handoff with enough fidelity to claim exact recovery. The mechanism is preserved; these thresholds must be re-certified in MT5.

## P5 — H1/H4 Structural Trend Core

P5 is a separate slower sleeve, but this first reset checkpoint retains the earlier one-position-at-a-time architecture. P5 is therefore allowed to enter only while the R9/P1–P4 engine is flat.

Causal signal:

- new H1/H4 bar detected;
- use only the just-completed bar;
- completed close must break the prior N-bar high/low;
- completed ATR must remain below a relative-volatility ceiling.

QC defaults:

- H1 breakout = 5 bars;
- H4 breakout = 6 bars;
- ATR baseline = 20 completed bars;
- H1 max ATR ratio = 1.20;
- H4 max ATR ratio = 2.00;
- stop = 1.50 ATR;
- trail activation = 0.25 ATR;
- trail = 1.00 ATR;
- H1 max hold = 12 hours;
- H4 max hold = 24 hours.

## MT5 QC sequence

Run **XAUUSD M1, Every tick based on real ticks, Jan 1–Jul 31 2026**, using the same Coinexx tester/account conditions as the R9 REAL benchmark.

Do not open August.

Recommended ablation order:

1. **R9 control**
   - P1 OFF
   - P2 OFF
   - P3 OFF
   - P4 OFF
   - P5 OFF
   - Confirm behavior is reasonably aligned with R9 HybridGate before judging breakthroughs.

2. **P1 only**
   - P1 ON
   - P2/P3/P4/P5 OFF

3. **P1 + P2**
   - tests selective runner promotion.

4. **P1 + P2 + P3**
   - tests failed-ignition exit/flip.

5. **P1 + P2 + P3 + P4**
   - tests whether the low-volatility rotation specialist adds useful idle-state trades.

6. **P1 + P2 + P3 + P4 + P5**
   - full current breakthrough foundation.

For every run record:

- total net profit;
- gross profit;
- gross loss;
- profit factor;
- trade count;
- win rate;
- maximal balance/equity drawdown;
- largest losing trade;
- average trade;
- monthly Jan–Jul net;
- Journal counts for `P1_CONT`, `P1_FADE`, `P2_RUNNER_PROMOTE`, `P3_FAILED_EXIT`, `P3_FLIP`, `P4_ROTATION`, `P5_H1`, and `P5_H4`.

## Promotion rule

Nothing in this branch is promoted because it compiled or because Python liked it.

A breakthrough is carried into the next R9 MOD checkpoint only if the MT5 REAL-tick QC is directionally consistent with the causal Python evidence and does not introduce an execution defect that invalidates the comparison.

**August 2026 stays sealed until the final Jan–Jul architecture is frozen.**
