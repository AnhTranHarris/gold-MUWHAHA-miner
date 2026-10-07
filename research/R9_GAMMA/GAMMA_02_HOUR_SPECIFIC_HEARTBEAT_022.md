# GAMMA-02 — Hour-Specific Heartbeat Cadence 022

**Status:** COMPLETE JANUARY DISCOVERY — VELOCITY FRONTIER, NOT QUALITY REPLACEMENT  
**Parent:** GAMMA_02_CAMPAIGN_HEARTBEAT_ROUTER_020.md  
**Opportunity counting:** maximum one new ticket per source per market tick  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Objective

Replace the uniform 1-second London/overlap heartbeat with per-hour causal heartbeat cadence while keeping:
- NY17 heartbeat OFF;
- NY18 heartbeat fixed at 250 ms;
- NY16 heartbeat OFF.

All entries remain time-separated market-tick events under already-earned HTF/state permission.

## Greedy cap-128 cadence auction

Final London/overlap cadence map:

| UTC hour | Heartbeat cadence |
|---:|---:|
| 07 | 1,000 ms |
| 08 | **500 ms** |
| 09 | **250 ms** |
| 11 | 1,000 ms |
| 12 | **250 ms** |
| 13 | **250 ms** |
| 14 | 1,000 ms |
| 15 | 1,000 ms |

NY18 remains 250 ms. NY17 and NY16 heartbeat remain OFF.

## Result

Uniform clean router:
- +$92,887.56
- 16,590 trades
- PF 3.82112
- +$5.59901 expectancy
- realized balance DD ~$2,302.79

Hour-specific cadence:
- **+$94,897.31**
- **16,927 trades**
- PF **3.74289**
- +$5.60627 expectancy
- realized balance DD **~$3,167.52**

Delta:
- **+$2,009.75 net**
- **+337 completed chronological trades**
- slightly higher expectancy
- lower PF and higher realized balance DD

Therefore this is retained as a **velocity frontier**. The uniform 1-second London router remains the cleaner quality comparator.

## Final source attribution

- 07: +$821.96 / 256 trades
- 08: +$1,991.67 / 567
- 09: +$5,119.44 / 2,176
- 11: +$7,628.26 / 1,325
- 12: +$11,916.70 / 3,522
- 13: +$5,809.72 / 730
- 14: +$2,091.68 / 712
- 15: +$11,946.60 / 2,042
- 16: +$16,337.49 / 1,157
- 17: +$28,070.93 / 561
- 18: +$3,162.86 / 3,879

## Durability

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_hour_specific_heartbeat_022.py`
  SHA-256 `8bb8fd7c69e79f1232ec8257a64b2b30d4d32670ed92c43b5fa311e909acd7d1`
- `gamma02_hour_specific_heartbeat_022_cap128.json`
  SHA-256 `3259cf745ddbee67558ec52e71d83f9aaf73730742f96f879fbeaf21f9caed04`

## Next unit

`GAMMA_02_HEARTBEAT_LIFECYCLE_SPECIALIST_023`

Test whether heartbeat entries should have shorter lifecycle than structural primary/rebreak tickets. Primary/rebreak lifecycle remains untouched.

R9 SYNTH remains the hard target.
