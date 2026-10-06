# DAA GRID-001 — R9 REAL January Context Mapping 001 Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_CONTEXT_MAPPING_001`  
**Status:** FROZEN BEFORE MAPPING/FILTERING

## Purpose

Map the already-promoted Delta-A-alpha grid state engine onto the **actual R9 REAL January 2026 trade stream** so later research can attack wrong-direction gross loss directly.

This unit is infrastructure only. It does not authorize vetoing, rerouting, or modifying R9 trades.

## Why this is the next high-leverage category

The standalone phase sandwich is positive but contributes only +$315.39, equal to 4.74% of R9 REAL January's -$6,651.62 net loss.

R9 REAL January itself contains:
- 31,915 trades;
- +$3,785.28 gross profit;
- -$10,436.90 gross loss;
- PF 0.362682;
- max balance drawdown $6,659.15.

A 20% preferred gross-loss improvement requires removing/recovering roughly **$2,087.38** of January gross loss.

That scale is more plausible by intercepting bad R9 entries than by adding another sparse overlay.

## Frozen scientific sequence

### M1 — Extract canonical R9 REAL January trades

From the canonical MT5 report:
`ReportTester-871471_jan2026_jul2026_R9_ticklog_real(4).xlsx`

For each completed January position extract at minimum:
- entry timestamp;
- exit timestamp;
- BUY/SELL direction;
- entry price;
- exit price;
- price PnL;
- swap;
- commission/cashflow when reconstructible;
- holding time.

### M2 — Infer MT5-report clock offset to Dukascopy UTC

Do **not** assume broker timezone.

For candidate whole-hour offsets, map report entry time to Dukascopy January ticks and compare report entry price against the corresponding executable quote:
- BUY entry -> Ask;
- SELL entry -> Bid.

Choose clock mapping only if:
- one offset is materially superior on median/quantile price error;
- the result is stable over a large sample;
- ambiguity is reported rather than hidden.

### M3 — Verify accounting/sample parity

Mapped January trade count/economics must reconcile with the canonical R9 REAL January benchmark closely enough to support contextual research.

### M4 — Attach causal grid context

Only after clock alignment is verified, tag each actual R9 entry with pre-entry causal state from the frozen grid engine:
- A05/A10/A15 lattice relation;
- 5m/15m nested trend owner;
- owner relation: aligned/opposed/conflict/neutral;
- trend phase/age;
- volatility-expansion state;
- grid event pace / finite state when available.

No future information may be used in the entry tag.

## Explicitly not authorized in this unit

- no R9 trade veto;
- no reroute;
- no replacement direction;
- no threshold search;
- no session/news filter;
- no changes to R9 source history;
- no MQL5 work.

## HFT/scalping cross-reference

Public HFT implementations reinforce three architectural principles used here:
1. event-time processing should remain distinct from slower alpha/state estimation;
2. risk admission/protection is a separate layer from sizing;
3. hostile/extreme state may block new risk while preserving exit/reduce actions.

Delta-A-alpha adapts those principles to Bid/Ask tick data without assuming unavailable order-book depth.

## Advancement

Context mapping advances only if the report-to-Dukascopy clock/price alignment is empirically verified.

The next unit, if mapping succeeds, will measure which grid state families contain R9 REAL January gross losses and whether any family is large enough to support the user's soft preferred ~20% improvement target.

August remains sealed. Main `delta` read-only. Fixed 0.01. No Martingale. MQL5 unauthorized.
