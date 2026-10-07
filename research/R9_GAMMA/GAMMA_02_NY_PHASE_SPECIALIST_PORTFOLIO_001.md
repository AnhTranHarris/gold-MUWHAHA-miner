# GAMMA-02 — NY Phase Specialist Portfolio 001

**Status:** MAJOR JANUARY DISCOVERY FRONTIER — CONTINUOUS CHRONOLOGY  
**Predecessor:** GAMMA_02_CONTINUOUS_ALIGN4_M1_EXTENSION_MARKOUT_001.md  
**August:** SEALED

## Architecture

Strict completed-bar ALIGN4 direction owns side.

Three corrected New York specialists share one global position cap:

### 16 UTC — accumulation / medium runner
- favorable extension step: $0.05
- TP: $12
- SL: $12
- max hold: 300s

### 17 UTC — primary trend runner / pyramiding phase
- favorable extension step: $0.10
- TP: $40
- SL: $8
- max hold: 300s

### 18 UTC — fast harvest phase
- favorable extension step: $0.05
- TP: $4
- SL: $4
- max hold: 15s

Every add requires a new favorable extension. No averaging down, Martingale, or loss-dependent sizing.

## One integrated global-cap replay

| Global max positions | Net | Trades | PF | Exp/trade | Realized balance DD |
|---:|---:|---:|---:|---:|---:|
| 8 | +$1,544.84 | 7,506 | 1.1692 | +$0.2058 | $1,235.72 |
| 16 | +$3,168.51 | 13,038 | 1.1876 | +$0.2430 | $2,367.91 |
| 24 | +$5,029.55 | 17,305 | 1.2130 | +$0.2906 | $3,360.52 |
| 32 | +$6,911.64 | 20,876 | 1.2316 | +$0.3311 | $4,278.34 |
| 48 | +$10,541.28 | 26,836 | 1.2553 | +$0.3928 | $5,587.98 |
| 64 | **+$14,141.48** | **31,599** | **1.2761** | **+$0.4475** | **$6,373.56** |
| 96 | **+$19,047.21** | **38,920** | 1.2791 | **+$0.4894** | $7,309.99 |
| 128 | **+$22,909.06** | **43,278** | **1.2884** | **+$0.5293** | $7,698.27 |

These are fixed 0.01 tickets. Higher caps are **research exposure frontiers**, not a low-capital recommendation.

## Why this is a major milestone

The corrected real-tick architecture now demonstrates:
- tens of thousands of positive-expectancy January executions;
- five-figure January capture at fixed 0.01 sizing;
- one shared portfolio ledger rather than arithmetic summing of standalone specialists;
- explicit exposure and drawdown costs;
- lifecycle specialization by NY phase.

The cap-64 frontier alone reaches 31.6K January trades, finally putting the opportunity engine into R9-class monthly activity territory.

## Important limitation

This portfolio is NOT yet combined with the previously earned fast runner-shadow/STMR foundation (+$1,425.30 / 1,400 January trades). The systems are largely time-separated, but an exact integrated replay is required before cumulative promotion.

The event-driven screen reports realized balance DD. Finalist configurations require full tick-level equity-DD replay.

## Exact durable artifacts

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_ny_phase_portfolio_001.py`
  SHA-256 `d227c6390a16061dfb038bee95b1a03025a97e62abec3874cfdb275979dc9710`
- `gamma02_ny_phase_portfolio_001.json`
  SHA-256 `baece4bd42b5588e86a8fc5a82e6537a4ed3da6114aa93b878c6d572acb4fc99`

## Next units

1. Test looser-but-causal HTF permission states (MACRO3 / MACRO2) as opportunity feeds, without changing the earned ALIGN4 portfolio.
2. Develop causal quality specialists to raise PF/expectancy on the 31K-43K event population instead of merely increasing cap.
3. Exact tick/equity integration with the earned STMR parent.
4. Jan-Jul validation only after January architecture stabilizes.
5. No MQL5 build yet.

R9 SYNTH remains the hard target.
