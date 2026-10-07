# GAMMA-02 — Campaign Heartbeat Router 020

**Status:** COMPLETE JANUARY DISCOVERY — UNIQUE-TICK CHRONOLOGICAL OPPORTUNITY EXPANSION  
**Parent:** GAMMA_02_DESK_SPECIFIC_UNIQUE_TICK_REBREAK_018.md  
**Opportunity counting:** maximum one new ticket per source per market tick  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Heartbeat hypothesis

A campaign heartbeat may add a fresh entry only while the already-earned HTF/session/state permission remains valid and the M1 price remains on the required favorable side/depth.

Heartbeat entries are time-separated market-tick events. They are not same-tick ladder multiplicity.

## Desk results at cap 128

### London / overlap
Best net in the first screen:
- interval: **1,000 ms**
- **+$91,522.28**
- **13,221 trades**
- PF **5.18278**
- expectancy **+$6.92249**
- realized balance DD ~$2,302.79

Parent desk-specific rebreak base:
- +$82,329.33
- 10,907 trades
- PF 5.51051
- expectancy +$7.54830

London heartbeat therefore adds about:
- **+$9,192.95 net**
- **+2,314 completed trades**

250-500 ms produced more raw heartbeat candidates but lower quality. The 1-second cadence is the current London net frontier.

### NY17
**REJECTED.** Periodic heartbeat competes with extremely high-value trend inventory. Every tested cadence reduced total net versus the parent.

### NY16
250 ms gives only a small diagnostic gain and lower PF. It is optional rather than a core heartbeat desk.

### NY18
Heartbeat is a useful velocity specialist.
At 250 ms:
- +$83,694.61 total portfolio net
- 14,276 trades
- PF 3.85668

The NY18 source itself becomes:
- +$3,162.86
- 3,879 trades
- +$0.815/source-trade expectancy

This deliberately trades quality for chronological velocity.

## Desk-specific router

The router preserves:
- London / overlap heartbeat = **1,000 ms**
- NY17 heartbeat = **OFF**
- NY18 heartbeat = screen 250/500/1000/2000/5000 ms
- NY16 heartbeat = OFF or 250 ms diagnostic

Best cap-128 raw-net point:
- London 1,000 ms
- NY18 250 ms
- NY16 250 ms
- **+$93,885.24**
- **16,656 trades**
- PF **3.84659**
- expectancy **+$5.63672**
- realized balance DD ~$2,302.79

Cleaner variant with NY16 OFF:
- **+$92,887.56**
- **16,590 trades**
- PF 3.82112
- expectancy +$5.59901

## Scientific interpretation

This is the first successful campaign-heartbeat mechanism in GAMMA-02.

The heartbeat must be routed by specialist:
- dense London/overlap states benefit from ~1-second re-entry cadence;
- NY17 does not;
- NY18 supports fast turnover;
- NY16 adds only marginal value.

The mechanism materially increases **genuine chronological trade count** without using same-tick scale-in duplication.

## Durable artifacts

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_campaign_heartbeat_019.py`
  SHA-256 `3ddb58c2096cf33ffc092335cfae8bc3ee78d828901423f1466f3024593016d4`
- `gamma02_campaign_heartbeat_019_london.json`
  SHA-256 `9191287f2cc0892e7b4d85bd0fddc6da2dc19971d29ee97f895156e6eb877252`
- `gamma02_campaign_heartbeat_019_ny17.json`
  SHA-256 `328425f72b1b614c978960d12443a585feddbf63f90376cd514dd9b46fff723b`
- `gamma02_campaign_heartbeat_019_ny16.json`
  SHA-256 `ee3d14f729f708abe7651d0b99feaa39f45a2cc4cd7ee8cb2e01a8b98cc2ec07`
- `gamma02_campaign_heartbeat_019_ny18.json`
  SHA-256 `529c62d6817d1374139a3eca7e85f50b571fe8bfb067d54276cfcb1ef3779a62`
- `gamma02_heartbeat_router_020.py`
  SHA-256 `f33a0381ea08f4d998a67e4cee2b34c827860a947c5003ea051610fccf6b166b`
- `gamma02_heartbeat_router_020_cap128.json`
  SHA-256 `368f86329310eb0c696177ee806765baba07610e77379ba33e294977b03e6325`

## Next atomic unit

`GAMMA_02_HEARTBEAT_CAP_FRONTIER_021`

Run the clean and aggressive heartbeat routers across bounded global caps, then continue January discovery from the better risk/velocity frontier.

R9 SYNTH remains the hard target.
