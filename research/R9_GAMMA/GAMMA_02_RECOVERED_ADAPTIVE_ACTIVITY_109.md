# GAMMA-02 — Recovered Adaptive Activity / Multi-Scout Chain 109

**Status:** RECOVERED FROM SURVIVING RUNTIME AFTER REPEATED UI TIMEOUTS  
**Predecessor:** GAMMA_02_EMERGENCY_CHAT_HANDOFF_108.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Recovery scope

The runtime preserved completed experiments 092-104 that had not all been persisted before the UI timed out. Exact important helpers/results were copied into persistent Library under:

`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/adaptive-092-104/`

## Multi-scout / activity findings

### 093 multi-scout

A multi-scout proof requirement improves over binary scout gating but does not repair March:
- Jan +$23,122.07 / 15,514 trades / PF ~85,638 / +$1.4904 expectancy
- Feb +$24,657.23 / 18,369 / PF 12.72 / +$1.3423
- Mar -$5,633.86 / 2,973 / PF 0.283 / -$1.895

Disposition: REJECTED as transfer solution.

### 095 activity unlock

Pre-entry activity unlock improves Jan/Feb and reduces March damage but March remains negative:
- Jan +$40,113.91 / 28,952
- Feb +$40,433.79 / 30,557
- Mar -$1,986.65 / 2,206

Disposition: useful activity feature, insufficient alone.

### 099 desk-health circuit

Win-only desk-health gating retains Jan/Feb but still fails March:
- Jan +$48,647.90 / 32,784
- Feb +$52,802.86 / 39,731
- Mar -$8,936.52 / 6,160

Disposition: REJECTED as cross-month regime protection.

### 100/101 mixed and pre-activity gates

Stricter activity gating can reduce March damage dramatically:
- mixed gate 15/70: Mar -$61.62 / 67 trades
- pre-activity 15/70: Jan +$31,080.37 / Feb +$31,047.97 / Mar -$157.48

But these sacrifice too much Jan/Feb capture and remain negative in March.

## 103 rolling-activity breakthrough

Causal rolling activity of candidate parents with N=64 reveals a sharp Jan/Feb vs March regime separation.

Boundary parameters:
- early rolling threshold 12.9
- late rolling threshold 64.93

January:
- **+$43,959.75**
- **28,119 trades**
- PF ~19,625.89
- win 99.9004%
- expectancy +$1.56335
- avg hold 14.93s
- existing harness: all-six January R9-SYNTH metrics crossed

February:
- **+$43,937.72**
- **28,221 trades**
- PF 328.43
- win 99.8618%
- expectancy +$1.55692
- avg hold 15.55s
- existing harness: all-six January R9-SYNTH metrics crossed

March:
- **0 trades**
- March maximum rolling activities remain just below both frozen thresholds.

Frozen later months:
- Apr 0 trades
- May 0
- Jun 0
- Jul +$16.19 / 28 trades

Interpretation:
- rolling activity is an extremely strong quality separator;
- the absolute threshold is NOT transferable because it encodes Jan/Feb tape scale;
- the next router must normalize activity to its own causal local baseline.

## 104 exact equity confirmation

Rolling-activity boundary results have exact tick-level equity confirmation for Jan/Feb:
- Jan equity DD $10,348.16
- Feb same stored equity-DD value in the current 104 artifact; this should be independently rechecked if promoted because identical cross-month DD deserves QA attention.
- minimum total equity $98,551.89 in stored artifacts.

## Current scientific problem

Build a **scale-free activity regime router**:
1. strict completed-bar alignment still owns direction;
2. current short-window tick arrival activity is measured causally;
3. normalize against a longer trailing baseline or causal percentile/rank;
4. preserve Jan/Feb fast quantum regime;
5. suppress March dead renewal regime;
6. restore opportunity in Apr-Jul without month labels;
7. combine with realized early renewal speed only after the normalized signal earns transfer value.

Candidate features:
- 1s activity / trailing 30-60s expected activity;
- 5s activity / trailing 30-60s expected activity;
- activity acceleration;
- causal rolling percentile among recent candidate parents;
- activity + realized renewal-speed handoff.

## Next unit

`GAMMA_02_SCALE_FREE_ACTIVITY_ACCELERATION_110`

Do not rerun <=109 after another timeout. Use persistent Library and /mnt/data recovered helpers.
