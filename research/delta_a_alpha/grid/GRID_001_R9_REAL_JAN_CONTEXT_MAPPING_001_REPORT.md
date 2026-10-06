# GRID-001 R9 REAL January Context Mapping 001

**Status:** COMPLETE / CLOCK + ACCOUNTING MAPPING VERIFIED

## Purpose

Attach the frozen Delta-A-alpha grid state engine to the **actual 31,915 R9 REAL January trades** so later research can directly attack wrong-direction gross loss rather than rely on sparse additive overlays.

## MT5 report clock

The MT5 Strategy Tester report clock was not assumed.

Whole-hour offsets were tested against Dukascopy January entry prices. The unique best mapping is:

`UTC = MT5 report time - 2 hours`

At UTC+2 report offset:
- median executable-quote price error: **$0.09**
- 75th percentile: **$0.17**
- 90th percentile: **$0.28**
- mean: **$0.135**
- median nearest-tick time error: **53 ms**
- 90th-percentile time error: **359 ms**
- **99.55%** of entries are within $1.00 of the mapped P75 executable quote.

Neighboring offsets are dramatically worse:
- +1 hour median error: ~**$7.26**
- +3 hours: ~**$7.51**
- zero offset: ~**$9.77**

The clock mapping is therefore strong enough for causal context tagging.

## Accounting parity

Mapped trades: **31,915**

MT5 deal-level January economics reproduce the canonical benchmark exactly:
- net: **-$6,651.62**
- gross profit: **+$3,785.28**
- gross loss: **-$10,436.90**
- PF: **0.362682**

Entry commission is preserved as its own negative deal, so gross-profit/gross-loss accounting remains MT5-native rather than being regrouped by trade.

## Frozen context attached at each R9 entry

Using only information available at or before the entry tick:

- 5m nested trend state + age;
- 15m nested trend state + age;
- parent owner timeframe;
- aligned / opposed / conflict / neutral relation to the R9 trade direction;
- EARLY / MATURE / EXTENDED trend phase;
- completed-M1 ATR14/ATR240 volatility-expansion state;
- latest A05/A10/A15 adaptive-grid event direction, age, gap, and relation to R9 direction.

Population:
- 15m owner: **11,277**
- 5m owner: **7,020**
- owner-aligned: **9,043**
- owner-opposed: **9,254**
- owner-conflict: **291**
- owner-neutral: **13,327**
- phase early: **10,502**
- phase mature: **6,008**
- phase extended: **1,787**
- volatility expansion >=1.75: **2,309**
- volatility expansion >=2.00: **1,167**

## What is not yet claimed

No R9 trade has been vetoed, delayed, reversed, or replaced.

This unit proves only that:
1. the clocks align;
2. the economics reconcile;
3. the grid context can be mapped causally to the real trade stream.

## Next

Measure **gross-loss concentration** by frozen state families.

The preferred structural target remains roughly **20%+ of R9 REAL January gross loss**, equivalent to at least **$2,087.38** of the canonical -$10,436.90 gross loss, without deleting a similar amount of gross profit.

Only after a large causal family is identified will veto/defer/reroute logic be authorized.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
