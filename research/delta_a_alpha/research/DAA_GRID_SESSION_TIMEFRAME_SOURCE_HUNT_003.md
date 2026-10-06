# DAA Grid Source Hunt 003 — Session + Timeframe Awareness

**Status:** COMPLETE — mechanism families frozen for a clean January replay.

## Scope
XAUUSD only. Fixed 0.01. No Martingale. Main delta read-only. August sealed.

## Governing design
Timeframes have different jobs:
- H4/H1 = structural/environment state;
- M15 = intraday phase;
- M5 = setup-state transition;
- ticks = grid crossing identity and executable Bid/Ask ordering.

This build does not use timeframe majority voting.

## Public sources inspected
- MQL5 multi-timeframe structural-confirmation work: HTF context with lower-timeframe reaction timing.
- MQL5 H4 swing-structure engine: structure is deliberately read from H4 instead of allowing a noisy execution timeframe to redefine trend continuously.
- MQL5 forex-session research: sessions can be treated as OHLC structures, and overlap is a distinct market state.
- TradingView open-source session tools: session high/low, locked previous-session extremes, opening ranges, and session resets.
- GitHub `Trujillofa/mt5-arch-integration`: DST-safe clocks, causally completed opening ranges, close-confirmation, and strong negative evidence against assuming generic session filters are alpha.
- GitHub `Moradi786/trading_bot`: explicit higher-timeframe context / lower-timeframe execution separation.
- MIT-licensed `joshyattridge/smart-money-concepts`: reusable session and prior-period primitives.

## January exploratory screening

All screening used ordered Dukascopy January ticks transformed to the frozen `DUKAS_COINEXX_LIKE_P75` surface.

Rejected:
1. raw same-cell recrossing — excessive friction/churn;
2. timer-only 1m/5m/15m re-arm — mostly destroyed expectancy;
3. generic prior-session/opening-range sweep fades — negative;
4. timeframe unanimity — strongest classes appeared during controlled disagreement;
5. state-episode micro-lattice resets — increased events but mostly destroyed expectancy.

Retained:
1. **session-local lattice reset** — new anchor and spatial memory at each session phase;
2. **first-touch cell genealogy** — same cell normally gets one directional opportunity per phase;
3. **HTF/LTF relay semantics** — disagreement can represent transition, not veto;
4. **session-dependent meaning** — Asia, London, overlap, NY, and late NY use different relay grammars.

## Original Delta-A-alpha mutations

### STMR — Session–Timeframe Morphing Router
A single grid infrastructure whose interpretation changes by session phase.

### Asia Reversal Initiation
An efficient H4/H1/M15/M5 stack can become stale. A new first-touch crossing against that stack is treated as an early reversal candidate rather than automatically rejected.

### London Micro Relay
H4/H1/M15 remain one way; M5 changes direction; a first-touch crossing in the M5 direction can own the scalp.

### Overlap Lower-TF Takeover
M15/M5 may take control before H4/H1 update during the London–NY handoff.

### NY Mixed-Macro Relay
When H4/H1 do not provide one aligned state, a coherent M15→M5 transition may own the scalp.

### Late-NY Lower Takeover
Late NY uses a bounded lower-timeframe handoff and does not inherit an earlier-session thesis indefinitely.

## Research implication
The grid should not ask “do all timeframes agree?”

It should ask:
**which timeframe currently owns which decision, and has ownership causally transferred?**

Candidate `STMR-001` is frozen separately before the clean replay.
