# GAMMA-02 — Low-Activity March Specialist 109

**Status:** COMPLETE MARCH DISCOVERY / FROZEN APRIL VALIDATION  
**Architecture:** parallel specialist; does NOT modify the high-activity 103/104 engine  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Parent architecture retained

High-activity router 103/104 remains frozen:
- Jan +$43,959.75 / 28,119 trades / all six exact Jan R9-SYNTH metrics crossed
- Feb +$43,937.72 / 28,221 / all six crossed
- Mar-Jun stand aside
- Jul +$16.19 / 28

Do not weaken this router merely to force trades.

## 108 — failed-ignition reversal discovery

March late-desk parents that fail to achieve the normal +$1.25 continuation quantum within the first 2 seconds exhibit a strong opposite-direction mean-reversion response.

348 late failures.

Reverse executable markout:
- 10s: +$67.88
- 15s: +$173.73
- 30s: +$240.20
- 60s: +$478.72
- **120s: +$2,262.46**
- 120s win rate 95.40%
- 120s PF ~291.43
- +$6.501/event

Early-desk failed-ignition reversal remains negative and is rejected.

## 109 — March reverse-renewal specialist

Trigger:
1. original frozen late NY17 parent is otherwise qualified;
2. original direction fails to reach +$1.25 within 2 seconds;
3. only then reverse direction;
4. run a 120-second reverse renewal campaign;
5. fixed 0.01 tickets;
6. q=$4.00;
7. zero-distance rearm;
8. child cap 703;
9. no Martingale / loss-dependent sizing.

March:
- **+$2,067.33**
- **807 trades**
- PF **24.4604**
- win **88.5998%**
- expectancy **+$2.56175/trade**
- average hold **50.8078s**
- max open event 196

It beats exact January R9-SYNTH PF, win rate and expectancy, but not net, trade count or holding-time target.

## Frozen April validation

Same q=$4.00 geometry, no retuning:
- 0 qualifying failed-late parents
- $0.00
- 0 trades

109 is therefore a **March-regime specialist**, not a generic low-activity engine.

## Scientific disposition

The system architecture is now explicitly parallel:

1. **High-activity R9-like renewal specialist 103/104**
   - Jan/Feb crossover
   - stands aside in Mar-Jun.
2. **March failed-ignition reverse specialist 109**
   - activates only when late continuation ignition fails in the March-type regime.
3. Future specialists must target remaining inactive regimes without altering prior earned layers.

## Exact artifacts

GitHub helpers:
- `research/R9_GAMMA/helpers/gamma02_low_activity_failed_ignition_markout_108.py`
- `research/R9_GAMMA/helpers/gamma02_low_activity_reverse_renewal_109.py`

GitHub summaries:
- `research/R9_GAMMA/artifacts/gamma02_low_activity_failed_ignition_markout_108_summary.json`
- `research/R9_GAMMA/artifacts/gamma02_low_activity_reverse_renewal_109_m3_summary.json`
- `research/R9_GAMMA/artifacts/gamma02_low_activity_reverse_renewal_109_m4_summary.json`

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/post-crossover-recovery/low-activity-specialists/`

SHA-256:
- 108 helper: `4473680ab846e72c2a62ba25e7d855a09da229b75a37c448460f73522e636ea1`
- 108 result: `137f3777937e5e508e1075732cb918b21d7fd0e089805500ca0699d55f35d17d`
- 109 helper: `a19aee022dec3870231a21608f9e9ac8b00112ec658fe45613d526919de1c04e`
- 109 March q4: `89382c8be8532faab89f1097447eda97024b7c2590d9511db96ec65b82e274b3`
- 109 April q4: `754c7c0e5c28b359a0cd7c5bdb51b6c9035e8053f69109a8d0bc67a69d401fa3`

## Next unit

`GAMMA_02_APRIL_SPECIALIST_DISCOVERY_110`

Rules:
- 103/104 and 109 are frozen.
- April is discovery for a new specialist.
- May is first validation month for any April specialist.
- no August access.
- no MQL5 build yet.
