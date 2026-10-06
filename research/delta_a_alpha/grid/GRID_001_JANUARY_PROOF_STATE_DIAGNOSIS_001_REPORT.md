# GRID-001 January Proof-State Diagnosis 001

**Status:** COMPLETE / DIAGNOSTIC / NO STANDALONE STATE PROMOTED

## Question

Why does A15 Proof-Before-Entry lose in the first two-thirds of January but win strongly in the final third?

## Parent result

A15 proof-before-entry:
- full January: **+$142.77 / PF 1.0102**
- discovery: **-$697.43 / PF 0.8004**
- validation: **+$840.20 / PF 1.0801**

## Frozen causal diagnostics

Only state known at or before proof entry was examined:

- completed-M1 ATR14 / ATR240 volatility-expansion ratio;
- whether A15 spacing had reached the $5 clamp;
- five-minute directional efficiency;
- continuation-aligned five-minute displacement;
- time since the prior A15 lattice event.

No model training and no threshold search were allowed.

## Large population shift

The market state changes materially across January:

- $5-capped A15 events: discovery **19.98%**, validation **93.91%**
- median ATR14 / ATR240: discovery **0.930**, validation **1.176**
- median event pace: discovery **194.4 sec**, validation **18.0 sec**

Late January is clearly a faster, higher-volatility lattice regime.

## But no simple filter explains the edge

### $5 gap clamp

- full: **+$633.86 / PF 1.0565**
- discovery: **-$222.18 / PF 0.8049**
- validation: **+$856.04 / PF 1.0850**

The cap state itself is not the cause of profitability.

### Volatility expansion >= 2.0

- full: **+$361.00 / PF 1.1700**
- discovery: **-$89.81 / PF 0.7616**
- validation: **+$450.81 / PF 1.2580**

The same state reverses sign chronologically.

### Fast event pace < 1 second

- full: **+$63.60 / PF 1.1842**
- discovery: **14 trades, +$4.47 / PF 1.2576**
- validation: **117 trades, +$59.13 / PF 1.1804**

This is directionally consistent, but the discovery sample is too small to promote.

### Slow event pace >= 120 seconds

- full: **-$398.47 / PF 0.8696**
- discovery: **-$433.29 / PF 0.7909**
- validation: **+$34.82 / PF 1.0354**

Removing slow events would improve aggregate economics but still would not solve the negative discovery segment.

## Interpretation

The A15 improvement is not explained by one simple volatility, spacing, efficiency, or pace threshold.

Do not create an arbitrary ATR-ratio or $5-gap rule merely because late January is profitable.

Proof-before-entry fixed **when** to risk capital. The next mutation should improve **which direction earns ownership**.

## Decision

REJECT as standalone filters:
- volatility-expansion ratio;
- $5 cap state;
- five-minute efficiency;
- event pace.

KEEP as contextual descriptors only.

NEXT: **DUAL PROOF OWNERSHIP**.

After a lattice event:
- no physical trade exists;
- continuation and mean-reversion compete causally;
- the first hypothesis to produce the frozen proof movement earns the single physical position;
- one position maximum;
- no averaging;
- no Martingale.

This directly tests whether early January's weakness is caused by forcing continuation semantics onto range/reclaim events.

August remains sealed. Main `delta` remains read-only. MQL5 remains unauthorized.
