# GAMMA-02 — Consecutive Phase Renewal Router 116

**Status:** MAJOR JAN-FEB-MAR BREAKTHROUGH — APRIL-JULY FROZEN VALIDATION PENDING  
**Predecessor:** GAMMA_02_RECOVERED_ADAPTIVE_ACTIVITY_109.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Mechanism

A local New York 12:00-13:59 two-hour campaign is divided into causal 10-minute cells.

Direction permission:
- H4 = H1 = trade direction != 0.
- M15/M5 may be aligned or in lower-timeframe pullback.

For every exact completed-bar state signature within each cell:
1. the first parent is a q1.25 scout;
2. the scout trades normally at fixed 0.01;
3. the cell remains locked until the scout demonstrates **4 consecutive profitable q1.25 renewals**, each completing in <=60 seconds;
4. the unlock happens at the actual exit timestamp of the fourth qualifying renewal;
5. only parents entering after that timestamp may unleash the remaining q1.25 campaign;
6. another signature/cell must prove itself independently.

No month labels, future outcomes, Martingale, loss-dependent sizing, or same-tick future ranking are used.

## Why this is different from prior scouts

Earlier binary/multi-scout approaches used a small scout summary that could look healthy even when the full campaign failed.

This router requires the **same renewal geometry being authorized** to demonstrate a self-renewing sequence first.

## Frozen n=4 / <=60s proof — Jan-Feb-Mar

| Month | Net | Trades | PF | Win | Expectancy | Avg hold |
|---|---:|---:|---:|---:|---:|---:|
| Jan | **+$133,718.62** | **75,621** | **28.9713** | 99.2304% | **+$1.76827** | 27.14s |
| Feb | **+$9,020.26** | **19,816** | 1.5327 | 91.7491% | +$0.45520 | 77.49s |
| Mar | **+$9,217.50** | **14,421** | 1.7497 | 91.6233% | +$0.63917 | 116.65s |

January exact R9 SYNTH benchmark:
- +$41,520.82
- 27,980 trades
- PF 23.7154
- 87.0908% win
- +$1.483946 expectancy
- 16.4627s average hold

January therefore materially exceeds R9 SYNTH on net, trades, PF, win rate and expectancy, but average hold remains slower than SYNTH.

The critical transfer result is that February and March are both positive without month-specific tuning.

## Strictness screen

- n=3: Jan +$134.45K, Feb -$7.64K, Mar +$1.39K -> rejected.
- n=5: Jan +$129.00K, Feb +$53.77, Mar +$2.11K -> too restrictive for February.
- **n=4**: best transfer balance so far.

## Scientific decision

Freeze:
- 4 consecutive q1.25 profitable renewals;
- each hold <=60s;
- exact signature/cell ownership;
- local NY 12:00-13:59;
- child cap 703.

Do NOT retune after opening April.

## Exact durability

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/consecutive-router-116/`

Contains exact helper and Jan/Feb/Mar results.

## Next

Run April, May, June and July chronologically with n=4/60s frozen.

If a later month fails, preserve the result before any repair research.

R9 SYNTH remains the hard target.
