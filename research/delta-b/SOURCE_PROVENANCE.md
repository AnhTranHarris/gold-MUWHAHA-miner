# DELTA-B Source Provenance — Grid Layer 1

Status: **CONCEPT / RECONSTRUCTION RECORD**

Purpose: preserve where ideas came from without importing performance claims or opaque code into DELTA-B.

## Project-Governing Sources

- MASTER EA Research & Handoff Protocol — Google Doc ID `1ycB5bQ3P24w7BZz54RwgJbc5CX5aRcqgr0KiI0Iidkw`
- Parent repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Parent branch at fork: `delta`
- Parent `CURRENT_STATE.json` blob at fork: recorded in DELTA-B root `CURRENT_STATE.json`

DELTA parent remains unchanged by DELTA-B research.

## GitHub Community Donors

### n30dyn4m1c/gold-pro-scalper
URL: https://github.com/n30dyn4m1c/gold-pro-scalper

Useful disclosed mechanisms:
- explicit XAUUSD Every-Tick vs simplified-model robustness problem
- cost gate relative to spread/commission
- turn confirmation
- spread/news/session state
- cooldown after loss
- server-side safety orders
- README states MIT license

DELTA-B use:
- conceptual inspiration for executable-cost gating and real-tick scepticism
- no performance claim inherited
- no closed-M1 decision rule adopted as Grid Layer 1 foundation

### NadirAliOfficial/trillex-10s-ea
URL: https://github.com/NadirAliOfficial/trillex-10s-ea

Useful disclosed mechanisms:
- 5s/10s synthetic bars
- midpoint construction from Bid/Ask to prevent spread movement being misread as directional price
- real-tick confirmation concept
- spread cap and safety stop

DELTA-B use:
- midpoint state / executable Bid-Ask separation
- concept only unless licensing is separately verified
- no lot-scaling logic adopted

### AAH20/hft-microstructure-kernel
URL: https://github.com/AAH20/hft-microstructure-kernel

Useful disclosed mechanisms:
- event-driven architecture
- compact deterministic state
- efficient price-ladder and matching-engine thinking
- Apache-2.0 indicated in README

DELTA-B use:
- computational architecture inspiration only
- exchange order-book / market-making assumptions are NOT imported into Coinexx XAUUSD CFD research without matching data

### pavanamthomas/market-microstructure-algorithmic-trading-lab
URL: https://github.com/pavanamthomas/market-microstructure-algorithmic-trading-lab

Useful disclosed mechanism:
- same signal can look positive at midpoint and turn negative after quoted spread, walked execution, fees, impact, or delay
- emphasizes causal execution evaluation

DELTA-B use:
- reinforces executable-edge gate and rejection of midpoint PnL
- no claim that its simulated order book describes Coinexx XAUUSD

### raphi6/High-Frequency-trading-based-on-Directional-Change-Intrinsic-Time
URL: https://github.com/raphi6/High-Frequency-trading-based-on-Directional-Change-Intrinsic-Time

Useful disclosed mechanisms:
- event-based / intrinsic-time representation
- movement-threshold directional-change events
- overshoot concept

DELTA-B use:
- conceptual basis for intrinsic-time lattice
- no repository performance claim imported
- code is not copied absent explicit license verification

### EarnForex/Volume-Profile
URL: https://github.com/EarnForex/Volume-Profile

Reserved for future Layer 2 review:
- tick-volume price-level activity histogram

DELTA-B use now:
- none in Grid Layer 1
- Volume Profile is intentionally deferred until Grid Layer 1 freeze

## MetaQuotes / MQL5 Authority for News/Event Handling

Official references:

- https://www.mql5.com/en/docs/calendar
- https://www.mql5.com/en/docs/calendar/calendarvaluehistory
- https://www.mql5.com/en/docs/calendar/calendareventbyid
- https://www.mql5.com/en/book/advanced/calendar
- https://www.mql5.com/en/book/advanced/calendar/calendar_cache_tester

Important implementation facts to preserve:

- Calendar data is expressed in trade-server time.
- Event descriptions expose importance metadata.
- DELTA-B cares about MEDIUM and HIGH scheduled events.
- Economic Calendar functions are not relied upon directly in Strategy Tester research; historical testing must use a frozen exported/cache representation so Python and later MQL5 tester logic can share the same events.

## Scientific Boundary

For every donor mechanism, DELTA-B must separate:

1. what the public source says;
2. what DELTA-B reconstructed;
3. what Python causal tests show;
4. what MT5 real-tick testing later shows;
5. what remains unverified.

No community profit figure is project evidence.


## Frozen Historical Event Cache Donor

### janickfarrell/forfac
URL: https://github.com/janickfarrell/forfac

Useful disclosed mechanisms/data contract:
- MIT-licensed ForexFactory calendar scraper
- tracked `forexfactory_calendar.csv`
- normalized GMT timestamps
- explicit High / Medium / Low impact extraction from ForexFactory metadata
- event, actual, forecast and previous fields

DELTA-B use:
- source snapshot blob SHA1: `10b81a5529341098eb5806155a902895f9eb652c`
- filtered once to USD + Medium/High + Jan-Jul 2026
- compact DELTA-B cache blob SHA1: `c3da523e511e4b89fe1f665740adb29bd3e37428`
- retained hot-path fields: GMT date/time, currency, impact, event name
- actual/forecast/previous values are intentionally excluded from Grid Layer 1
- cache is frozen in DELTA-B; upstream daily refreshes do not mutate historical research silently
- public calendar data is contextual evidence, not proof of trading profitability

