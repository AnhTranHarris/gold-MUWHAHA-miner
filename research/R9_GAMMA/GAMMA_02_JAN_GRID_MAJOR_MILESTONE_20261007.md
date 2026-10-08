# GAMMA-02 — January Grid Major Milestone / Fallback Position

**Status:** FROZEN MAJOR JANUARY FALLBACK / DURABLE RECOVERY POINT  
**Repository:** `AnhTranHarris/gold-MUWHAHA-miner`  
**Active research branch:** `carson/r9-gamma-02-velocity-geometry-research`  
**Fallback branch:** `carson/r9-gamma-02-jan-grid-milestone`  
**Scientific parent:** `GAMMA02_DYNAMIC_RENEWAL_WATCHDOG_119`  
**Latest completed January unit at freeze:** `GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_131E`  
**Next optional January R&D unit:** `GAMMA_02_JAN_WD119_VIRTUAL_RENEWAL_RUNNER_131F`  
**August:** SEALED  
**MQL5 build:** NOT AUTHORIZED

## Purpose

This checkpoint is the formal fallback position for the January grid architecture. It exists so future February/later-month work, chat timeouts, retries, crashes, or experimental regressions cannot force reconstruction of January mechanics from conversation memory.

Future work may improve this architecture, but it must not silently overwrite or invalidate this fallback. If later work regresses materially, recover from the fallback branch and the exact durable artifacts listed below.

## January benchmark

Authoritative January R9 SYNTH comparator:

- net: **+$41,520.82**
- trades: **27,980**
- gross loss: **-$1,827.87**
- PF: **23.7154**
- win rate: **87.09%**
- expectancy: **+$1.48395/trade**
- average hold: **16.46 s**
- source SHA-256: `e5fcf4d6879193fac88e7a8e101db1111d59e1a7f5abfb793c970b06cfce7cc7`

January Dukascopy source SHA-256:

`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

## Frozen architecture

The January system is an asymmetric session/state portfolio built around Watchdog-119, not a calendar-month rule.

### Core Watchdog grid

Watchdog-119 remains the high-renewal NY specialist. The current refined grid uses:

- exact completed H4/H1/M15/M5 structural state,
- direction + 10-minute subphase ownership,
- first-parent scout,
- four consecutive profitable <=60 s renewals to unlock,
- immediate relock after losing/slow realized renewal,
- renewal quantum map approximately `$1.19` in bins 0-4 and `$1.10` in bin 5,
- explicit physical scaling only inside the known Watchdog grid,
- maximum renewal-depth control from 131B/131E.

### Session specialists retained in the January portfolio

- `ASIA02_CONT` — UTC 02 continuation specialist.
- `LONDON10_ROTATE_LONG` — UTC 10 rotation-long specialist.
- `OVERLAP13_SHORT` — UTC 13 London/NY-overlap short specialist.
- `LATE21_LONG` — UTC 21 late-session continuation specialist.
- source12 cold-start microgrid cap64.
- recovered earlier-session causal coverage V3 across source-hours 9/11/12/13/14/15/16.

No month, ISO week, weekday, or calendar date is an execution feature. Calendar partitions are evaluation only.

## Frozen performance frontiers

### Firm-style session milestone — 131D

`WD119_COVERAGE_LEAN4_COLD64`

- net: **+$207,653.32**
- trades: **88,958**
- gross profit: **+$212,728.42**
- gross loss: **-$5,075.10**
- PF: **41.9161**
- win rate: **97.96%**
- expectancy: **+$2.33428/trade**
- balance DD: **~$818.71**
- full-tick equity DD: **~$62,763.84**
- max open: **703**
- positive R9-SYNTH trading days: **21/21**
- days beating same-date R9 SYNTH: **13/21**
- positive ISO weeks: **5/5**
- weeks beating same-week R9 SYNTH: **5/5**
- excluding Jan 30: **+$67,633.55** vs R9 SYNTH **+$34,628.80**

Weekly candidate net versus R9 SYNTH:

- W01: **$1,217.78** vs $1,027.95
- W02: **$8,091.31** vs $5,332.33
- W03: **$18,316.62** vs $5,817.38
- W04: **$16,718.60** vs $7,692.42
- W05: **$163,309.01** vs $21,650.74

### Preferred balanced fallback — 131E

`L35_C640`

- Watchdog max renewal layer: **35**
- Watchdog cap: **640**
- net: **+$194,425.92**
- trades: **80,929**
- gross loss: **-$3,642.86**
- PF: **54.3718**
- win rate: **98.03%**
- expectancy: **+$2.40243/trade**
- balance DD: **~$451.92**
- full-tick equity DD: **~$57,139.20**
- max open: **640**
- positive trading days: **21/21**
- days beating same-date R9 SYNTH: **13/21**
- weeks beating R9 SYNTH: **5/5**

This is the recommended January fallback when balancing profit, velocity, realized loss, and heat.

### Aggressive >$200K fallback — 131E

`L35_C703`

- net: **+$203,532.62**
- trades: **86,090**
- gross loss: **-$4,293.48**
- PF: **48.4050**
- win rate: **98.08%**
- expectancy: **+$2.36418/trade**
- balance DD: **~$650.62**
- full-tick equity DD: **~$62,763.84**
- max open: **703**
- positive trading days: **21/21**
- weeks beating R9 SYNTH: **5/5**

Use only as the aggressive January profit frontier; it does not solve synchronized floating heat.

## Durable scientific chain

Read in this order:

1. `research/R9_GAMMA/GAMMA_02_JAN_WATCHDOG119_GRID_LAYER_REFINEMENT_131A.md`
2. `research/R9_GAMMA/GAMMA_02_JAN_WATCHDOG119_LAYER_DEPTH_HEAT_131B.md`
3. `research/R9_GAMMA/GAMMA_02_JAN_SESSION_FIRM_DAILY_WEEKLY_131D.md`
4. `research/R9_GAMMA/GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_131E.md`
5. `research/R9_GAMMA/GAMMA_02_CURRENT_RESEARCH_CURSOR.json`
6. this milestone document + JSON manifest

Key helpers/results:

- `research/R9_GAMMA/helpers/gamma02_jan_watchdog119_grid_layer_refinement_131a.py`
- `research/R9_GAMMA/helpers/gamma02_jan_watchdog119_layer_depth_heat_131b.py`
- `research/R9_GAMMA/helpers/gamma02_jan_wd119_plus_causal_grid_coverage_131b.py`
- `research/R9_GAMMA/helpers/general_session_state_discovery_131c.py`
- `research/R9_GAMMA/helpers/jan_session_portfolio_131d.py`
- `research/R9_GAMMA/helpers/jan_session_portfolio_lean_131d.py`
- `research/R9_GAMMA/helpers/r9_synth_jan_daily_weekly.py`
- `research/R9_GAMMA/helpers/jan_profit_per_heat_atomic_131e.py`
- `research/R9_GAMMA/helpers/jan_profit_per_heat_highrange_131e.py`
- `research/R9_GAMMA/artifacts/gamma02_jan_watchdog119_grid_layer_refinement_131a.json`
- `research/R9_GAMMA/artifacts/gamma02_jan_watchdog119_layer_depth_heat_131b.json`
- `research/R9_GAMMA/artifacts/jan_wd119_plus_coverage_v3_131b.json`
- `research/R9_GAMMA/artifacts/r9_synth_jan_daily_weekly.json`
- `research/R9_GAMMA/artifacts/gamma02_jan_session_firm_daily_weekly_131d.json`
- `research/R9_GAMMA/artifacts/jan_profit_per_heat_atomic_131e.json`
- `research/R9_GAMMA/artifacts/jan_profit_per_heat_highrange_131e.json`
- `research/R9_GAMMA/artifacts/gamma02_jan_wd119_profit_per_heat_131e.json`

## Hash authority

- 131A helper SHA-256: `c1f80f99376f2fec47dc2897ff2312c310799bde8392cd28976a44849ef1b660`
- 131A full-result SHA-256: `863bd4551027effa72e5e63ba3b5e016be4ac45840ecbef11f2cc6e7e89c1687`
- 131B helper SHA-256: `aade099a0efdb504bd6f16b4d3cbcacce7f37572d76c7ff931aed07449f36057`
- 131B result SHA-256: `63438e6cb8edba62630868b918faea9085369856908f8e49a5a4e323bf49f7b5`
- recovered coverage result SHA-256: `e685ebd2a9a5d23615439b57a0daaa8fcd4549e7dd5018f4bd85455d3851e3ad`
- 131D selected helper SHA-256: `9f290909b172ce97924caf028a66c733a71cd7d6bc519e08d72389911c2f4456`
- 131D compact artifact SHA-256: `fc5d1ea59eeefa5720100e36352e3e7445e7c99aebdc5083bc4ba1dce6d4d42f`
- 131D full-result SHA-256: `1d9813c92ad6aae1eef7e1f40de0d324f1696de2081fa960ebd92fd5b97c4aa7`
- 131E atomic helper SHA-256: `8c90db97910ee8fc9df193060b56507ac2cb55a91a766a856c395774f7cf7595`
- 131E atomic result SHA-256: `00ea46d09edae27200cc758ffc1438db4e195d9c197b9bad0ea7dde9a771c7b7`
- 131E high-range helper SHA-256: `a633c9332de0bcc8186e2c59751f400d440c5e623125d1a117551d773195ba2c`
- 131E high-range result SHA-256: `435f50189f7f13fdc8f9edff580194d64bea498503ff8e10d36d831e2fa9cbb6`
- 131E compact artifact SHA-256: `0f3c50459fad2ca861806a68cb4b51ffb2222ca73ccb9b3a44d6b3a7621e912f`

## Recovery procedure

If a chat crashes, times out, is retried, or starts fresh:

1. Open the fallback branch `carson/r9-gamma-02-jan-grid-milestone`.
2. Read this milestone document and its JSON manifest.
3. Read `GAMMA_02_CURRENT_RESEARCH_CURSOR.json` on the milestone branch.
4. Read checkpoints 131A → 131B → 131D → 131E.
5. Use exact helper/result bytes; do **not** reconstruct January from memory.
6. Verify the January raw market SHA-256 before replay.
7. Treat `L35_C640` as the balanced fallback and `L35_C703` as the aggressive >$200K frontier.
8. Do not modify the milestone branch. Continue experiments on the active research branch or a new descendant branch.
9. Do not access August unless the owner explicitly unseals it.

## Governance

This January milestone remains the fallback until a later month or adaptive multi-month architecture demonstrates comparable or superior performance and reliability under the owner's month-by-month, day-by-day, week-by-week criteria.

Future February/later work must therefore extend or route around this January capability, not casually replace it with a weaker universal system.