# GAMMA-02 — Cross-Month Expert Ensemble Breakthrough 133C

**Status:** MAJOR CROSS-MONTH BREAKTHROUGH — PROVISIONAL PARETO, RISK REFINEMENT STILL OPEN  
**January fallback:** untouched at `carson/r9-gamma-02-jan-grid-milestone`  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Objective

Recover from repeated UI timeout failures and test a bounded non-AI expert ensemble that can enter February blind, learn causally from realized outcomes, and adapt quickly enough to survive a materially different March regime. Month/day labels are evaluation partitions only and are not execution features.

## Architectural breakthrough

The successful structure is:

`session/HTF state -> validated specialist experts run in shadow -> fast/slow expert evidence -> earned physical capacity -> global heat cap/risk gate`

Current expert stack:

1. January-derived Watchdog shadow router.
2. Stable causal session coverage + cold-start microgrid.
3. March-native PF10 continuation expert reconstructed from the legal March-130 pipeline (completed H4/H1/M15/M5 state, UTC subphase, already-realized favorable M1 displacement, state-specific lifecycle).
4. February adaptive heartbeat/grid learner, but now wrapped by an **expert-level session-aware realized-outcome gate** so it can be demoted back to shadow when its fast evidence deteriorates.

The key insight is that the February learner is an accelerator, not the foundation. The native continuation specialist is almost complementary: modestly positive in February and extremely strong in March.

## No-learner ensemble control

With the adaptive learner removed entirely:

- February: **+$61,591.37 / 28,273 trades / PF 4.16** — ~93% of February R9 SYNTH net.
- March: **+$81,350.01 / 23,228 trades / PF 4.46** — **107.5% of March R9 SYNTH net**.
- March remains positive in 5/5 weeks.

This proves the expert ensemble has strong cross-month economics before any learner contribution.

## First SYNTH-beating cross-month gate — G1

Expert-level gate parameters:

- fast window: 4 completed shadow outcomes
- slow window: 32
- session-specific evidence after at least 8 samples; global evidence used earlier
- demote when fast mean < 0, fast PF < 0.9, fast gross-loss burst < -$20, or slow mean < -$0.25
- promote when fast mean >= +$0.50, fast PF >= 1.10, and slow mean >= 0
- shadow outcomes continue updating while demoted

### February

R9 SYNTH: **+$66,213.65 / 33,523 trades / PF 33.59 / 88.30% win / +$1.975 expectancy**.

G1 ensemble:

- net: **+$71,884.88** (**108.6% of SYNTH net**)
- trades: **30,059**
- gross loss: **-$20,509.48**
- PF: **4.505**
- win: **88.67%**
- expectancy: **+$2.391/trade**
- balance DD: **~$2,633.73**
- positive days: **14**
- days beating same-date SYNTH: **7**
- positive weeks: **4/4**
- weeks beating SYNTH: **2/4**

Adaptive learner contribution after expert gate: **+$10,514.82 / 1,878 trades / PF 8.94 / +$5.60 expectancy**.

### March

R9 SYNTH: **+$75,698.63 / 40,985 trades / PF 38.38 / 90.01% win / +$1.847 expectancy**.

G1 ensemble:

- net: **+$86,864.48** (**114.8% of SYNTH net**)
- trades: **25,440**
- gross loss: **-$32,993.27**
- PF: **3.633**
- win: **84.38%**
- expectancy: **+$3.414/trade**
- balance DD: **~$7,855.20**
- positive days: **14**
- days beating same-date SYNTH: **8**
- positive weeks: **5/5**
- weeks beating SYNTH: **4/5**

Adaptive learner contribution after expert gate: **+$5,514.47 / 2,212 trades / PF 1.58 / +$2.49 expectancy**. This is a major repair versus the same learner's ungated March result of approximately **-$11.66K / PF 0.64**.

March weekly G1 net:

- W10: +$5,642.94
- W11: +$11,822.04
- W12: +$16,370.84
- W13: +$46,091.16
- W14: +$6,937.50

## Interpretation

This is the first recovered architecture in this research sequence that exceeds the time-matched R9 SYNTH monthly net in **both February and March** while remaining fully causal and calendar-blind at execution time.

It is **not yet risk-quality complete**. Gross loss and balance DD remain much worse than R9 SYNTH, and full-tick equity DD has not yet been recomputed for the new G1 ensemble. Therefore G1 is a major economic breakthrough, not a final deployable winner.

## Crash/time-out remediation

From this unit forward, research is split into small atomic blocks. Every completed frontier is written immediately to JSON and checkpointed before the next sweep. Parallel Python processes are avoided because three concurrent ensemble runs exceeded available memory and two were killed; single atomic configurations complete reliably in ~15–30 seconds.

## Exact authority

Helper:
`research/R9_GAMMA/helpers/expert_gate_133c.py`

Helper SHA-256:
`e1072d3a314a445973c1d49b62233820c84c96b9dd9e23e0a7312fe1dd81081b`

Result:
`research/R9_GAMMA/artifacts/expert_gate_133c_G1.json`

Result SHA-256:
`fa9ba09864c66e6c6618ac6c9ddcce1702ec5d3e9200016064f23068e0357f0b`

Framework helper SHA-256:
`1a6443a5aadbc00be1aa8b53a91281088c0d8172d8199e049885b549331421d3`

Large cached expert streams remain in persistent Library storage and are not to be reconstructed from chat memory if available.

## Next

Continue `133C` risk/Pareto refinement in small atomic blocks:

1. tighter expert demotion/promotion variants;
2. full-tick equity-DD calculation on finalists;
3. session-aware and trend-within-trend capacity allocation;
4. preserve February > SYNTH and March > SYNTH monthly net if possible while materially reducing gross loss/DD;
5. January regression gate before promotion to a frozen cross-month milestone.