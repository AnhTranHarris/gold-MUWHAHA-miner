# DELTA-B DB001B — Lightweight Event/Microstructure Correlation Smoke

Status: **BOUNDED DIAGNOSTIC — NOT PROFITABILITY EVIDENCE**

## Purpose

Test whether medium/high USD event proximity materially changes the quote environment enough to justify adaptive Grid context.

This is deliberately not a news strategy. No headline sentiment, forecast surprise, actual-vs-forecast direction, language model, or article feed is used.

## Frozen event input

Source snapshot:

- upstream repository: `janickfarrell/forfac`
- upstream file: `forexfactory_calendar.csv`
- upstream Git blob SHA1: `10b81a5529341098eb5806155a902895f9eb652c`
- DELTA-B compact file: `research/delta-b/data/FF_USD_MEDHIGH_2026_JAN_JUL.csv`
- DELTA-B compact Git blob SHA1: `c3da523e511e4b89fe1f665740adb29bd3e37428`
- compact rows: **322 events**
- retained fields only: GMT date/time, USD, Medium/High, event name
- actual / forecast / previous values deliberately discarded from the hot-path cache

The upstream project states that the tracked CSV is normalized to GMT and identifies impact from ForexFactory icon/CSS metadata. DELTA-B freezes its own snapshot so later upstream refreshes cannot silently alter historical research.

## Bounded canonical-tick probe

Canonical January Dukascopy source SHA256:

`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

Bounded interval:

- 2026-01-05 00:00 UTC through 2026-01-10 00:00 UTC
- 1,916,503 ordered quotes
- 6,840 observed minute buckets
- event neighborhood: ±30 minutes
- release bucket: first 5 minutes
- time-of-day control for the main comparison: 12:30–16:00 UTC

This time control is important because many major USD releases naturally occur during the more active U.S. session.

## Main controlled result

Within the 12:30–16:00 UTC control window, event-adjacent minutes versus non-event minutes:

| Metric | Normal mean | Event-window mean | Event / normal |
|---|---:|---:|---:|
| ticks / minute | 399.14 | 499.11 | **1.250×** |
| average quoted spread | $0.7189 | $0.7241 | **1.007×** |
| absolute tick path / minute | $21.824 | $31.178 | **1.429×** |
| minute high-low range | $2.687 | $3.557 | **1.324×** |
| absolute minute displacement | $1.452 | $1.912 | **1.317×** |

Pearson correlation between event severity code (0 normal, 2 medium, 3 high) and minute metrics inside the same time control:

- ticks/minute: **+0.379**
- quoted spread: **+0.031**
- absolute path movement: **+0.399**
- minute range: **+0.281**
- absolute displacement: **+0.160**

These are descriptive correlations only.

## Quant interpretation

The strongest first-week relationship is **activity/movement**, not spread.

That argues against a blanket event blackout or a design where calendar severity directly widens the grid to the maximum.

The better architecture is:

1. scheduled Medium/High event phase supplies a small prior defensive envelope;
2. observed quote stress determines how much of that envelope activates;
3. clean high-activity directional movement remains tradable;
4. noisy high-path / low-displacement movement can widen Q and hysteresis;
5. abnormal spread can still raise friction immediately when it genuinely occurs.

This keeps the system a trading engine rather than a news engine.

## Runtime architecture

The event cache is compiled once into phase transitions.

Hot path:

`tick timestamp -> event phase cursor -> small integer state`

No event-list scan per tick.

Session state is cached by UTC minute, so timezone conversion happens at most once per minute rather than once per quote.

Adaptive-Q robust quantiles/medians are being changed to bounded periodic refreshes instead of full rolling-window sorts on every tick.

## Caveats

- This is only the first bounded week and is not a Jan-Jul conclusion.
- Medium-impact sample size is smaller and differently timed than the high-impact sample.
- No trade lifecycle was attached.
- No direction prediction is claimed.
- No Volume Profile or RSI has been added.
- August remains sealed.

## Decision

**KEEP the lightweight event context. DO NOT build a newsroom.**

Calendar importance remains contextual metadata. Market behavior remains the authority.

Next Grid research should return to trading mechanics: quantify how the adaptive intrinsic lattice behaves across sessions/event phases and then attach the smallest executable scalp lifecycle needed to measure gross loss, drawdown and opportunity retention.
