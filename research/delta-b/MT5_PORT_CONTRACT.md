# DELTA-B MT5 Port Contract

Status: **FUTURE TRANSLATION CONTRACT — MQL5 BUILD NOT AUTHORIZED**

This file exists so Python research cannot drift into logic that is impossible or materially different in MetaTrader 5.

## 1. Translation Preconditions

No `.mq5` candidate may be produced until the owner explicitly authorizes MQL5 work.

Before translation, Grid Layer 1 must have:

- deterministic Python producer
- exact timing/state-machine specification
- independent QA
- source/hash manifest
- fixed session/event semantics
- explicit Bid/Ask execution semantics
- frozen parameter neighborhood
- causal Jan-Jul evidence
- no August access unless separately authorized

## 2. Tick Semantics

Python and MQL5 must agree on:

- ordered quote chronology
- midpoint state calculation
- executable side of fills
- spread measurement
- commission/slippage model
- directional-change extrema updates
- same-timestamp ordering policy
- Q update timing
- session/event state update timing

No Python-only future resampling is allowed.

## 3. Economic Calendar Contract

### Live/Demo EA

MetaTrader's Economic Calendar may be queried online. Calendar timestamps are expressed in **trade-server time**. Medium and high importance events are required DELTA-B state.

The live EA must:

- filter relevant currencies/countries explicitly
- read event importance from the event description
- compare event time with trade-server time
- never infer event direction before the release
- handle calendar API failure/timeouts conservatively

### Strategy Tester

Do **not** depend on live Calendar API calls inside the Strategy Tester.

The tester implementation must consume a frozen historical calendar cache/file containing, at minimum:

- event ID/name
- event timestamp in the chosen canonical timezone/server-time mapping
- currency/country
- importance
- release/revision metadata needed by the tested rule

The cache must be versioned and hashed.

Python research must use the same historical event table or a demonstrably equivalent normalized copy.

This avoids tester/live semantic mismatch.

## 4. Session / DST Contract

Session logic must have one explicit canonical clock representation.

If the EA uses broker/server time, DST transitions must be deterministically mapped.

No hard-coded local-computer timezone assumptions.

The Python replay must reproduce the same session labels for parity fixtures.

## 5. Adaptive Grid Contract

MQL5 translation must preserve the exact bounded causal function for:

- executable movement quantum Q
- Q clamps
- spread percentile or rolling friction state
- micro-noise estimator
- intrinsic scales Q/2Q/4Q/8Q
- hysteresis
- event age
- cross-scale coherence
- five primary states
- medium/high news phase
- unscheduled shock state

A translation is invalid if Python uses a library/model unavailable to the EA without an equivalent frozen deterministic implementation.

## 6. Performance Contract

The live tick handler should be event-driven and compact.

Preferred:

- fixed-size/ring buffers
- incremental rolling statistics
- no full-history scans on every tick
- no repeated indicator recreation
- heavy diagnostics only on state transition or bounded refresh
- explicit restart reconstruction of active grid state where necessary

## 7. Martingale Prohibition

The MQL5 implementation must reject:

- adverse-position grid adds
- lot escalation after loss
- recovery baskets
- widened stops to create room for additional losing-grid positions

Future favorable pyramiding requires its own owner-approved contract.

## 8. Parity Gate

Before human Strategy Tester review, produce deterministic fixtures proving Python/MQL5 agreement on:

- Q
- session label
- news/event phase
- shock state
- L0-L3 directional-change events
- primary grid state
- entry authority
- any later favorable-pyramid authority

The official Coinexx Strategy Tester report remains broker-level evidence and does not retroactively excuse parity failures.
