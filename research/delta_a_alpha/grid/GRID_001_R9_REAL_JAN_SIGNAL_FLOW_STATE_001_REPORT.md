# GRID-001 R9 REAL January Signal-Flow State 001

**Status:** COMPLETE / NEGATIVE / WRONG EVENT CLOCK

## Question

Can the recent R9 BUY/SELL signal stream itself act like an HFT-style event-flow state that identifies wrong-direction January losses?

## Frozen experiment

Before each current R9 signal, the test measured:
- time since the previous R9 signal;
- same-direction run length;
- exponentially decayed signed prior-signal pressure with tau = 2 seconds and 10 seconds;
- nested FAST/SLOW support-vs-opposition state;
- predefined interactions with the frozen market owner relation and trend phase.

No future signal was used.

## Main result

The chosen pressure clocks are simply too fast for the R9 signal stream.

- FAST 2s pressure was NEUTRAL for **31,908 / 31,915 trades = 99.98%**.
- SLOW 10s pressure was NEUTRAL for **31,555 / 31,915 = 98.87%**.
- Combined nested state was NEUTRAL/MIXED for **31,554 / 31,915 = 98.87%**.

The pressure tensor therefore carries almost no useful state.

Other event-flow families again behaved mostly like broad partitions:
- signal gap >=30s: 69.43% of trades, 69.91% of gross loss, 68.97% of gross profit;
- NEW/FLIP: 64.60% of trades, 64.17% of gross loss, 64.63% of gross profit;
- RUN_2: 23.54% of trades, 24.04% of gross loss, 23.50% of gross profit.

These are not selective enough to justify vetoing.

## Interpretation

The HFT concept was useful; the chosen **data clock** was not.

R9 signal events are too sparse for 2s/10s pressure decay. Increasing the decay constants repeatedly until something looks good would become parameter rescue, so it is explicitly rejected.

The correct fast-state source is the market feed itself.

Dukascopy gives us causal top-of-book information:
- Bid;
- Ask;
- Bid volume;
- Ask volume;
- exact event timestamps.

That supports a legitimate L1 micro-state layer without inventing L2 depth.

## Next mutation

Build a **nested micro-market state** under the existing 5m/15m trend-within-trend router.

Candidate causal primitives:
- subsecond / 1s / 5s quote displacement;
- path efficiency;
- quote-update intensity;
- directional persistence;
- spread state;
- L1 volume imbalance:
  `(bid_volume - ask_volume) / (bid_volume + ask_volume)`;
- L1 microprice displacement from midpoint using the standard size-weighted top-of-book formula.

The research objective remains entry/risk admission for actual R9 signals, not another standalone overlay.

## Decision

REJECT:
- 2s/10s R9-signal pressure;
- decay-window tuning.

KEEP:
- HFT event-clock separation principle;
- nested trend-within-trend architecture;
- actual R9 context mapping.

NEXT:
**R9 REAL January nested micro-market state / admission research.**

August remains sealed. Main `delta` remains read-only. MQL5 unauthorized.
