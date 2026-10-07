# GAMMA-02 — One Event Per Tick Audit 014

**Status:** COMPLETE CONSERVATIVE MICROSTRUCTURE QA — NEW DEFAULT OPPORTUNITY COUNTING RULE  
**Predecessor:** GAMMA_02_LONDON_NY_HOURLY_CONVICTION_002.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## QA finding

The extension builders emit one event per newly crossed $0.05 level. If one market tick jumps across multiple levels, several candidate tickets can therefore share the exact same tick index and executable Bid/Ask.

Recovered January candidate populations before the cap:
- London/overlap: 31,714 candidate events on 12,827 unique market ticks; ~78.5% of events belong to a multi-event tick; maximum 47 events on one tick.
- NY: 23,725 candidate events on 4,336 unique market ticks; ~94.2% of events belong to a multi-event tick; maximum 103 events on one tick.

These multi-level tickets are potentially executable as pyramiding/scaling, but they are NOT independent chronological opportunity discoveries.

## Conservative policy

For scientific opportunity counts:
> maximum one new ticket per source per market tick, retaining the deepest newly reached extension.

Same-tick multi-level tickets remain eligible for later explicit **pyramid multiplicity** research, but must be labelled exposure scaling rather than new opportunity velocity.

## Conservative January one-ledger frontier

| Cap | Net | Trades | PF | Exp/trade | Realized balance DD |
|---:|---:|---:|---:|---:|---:|
| 32 | +$23,503.50 | 3,895 | 4.1546 | +$6.034 | $798.86 |
| 64 | **+$45,644.74** | **6,494** | **5.1616** | **+$7.029** | $1,307.94 |
| 96 | +$63,139.18 | 8,601 | 5.2640 | +$7.341 | $2,183.86 |
| 128 | **+$77,049.12** | **10,351** | **5.3715** | **+$7.444** | $2,927.21 |
| 160 | +$89,914.11 | 11,862 | 5.3704 | +$7.580 | $3,517.80 |
| 192 | +$101,373.27 | 13,397 | 5.2156 | +$7.567 | $3,958.58 |
| 256 | **+$118,661.07** | **15,216** | **5.4112** | **+$7.798** | $4,597.32 |
| 384 | +$145,153.03 | 16,799 | 6.2518 | +$8.641 | $4,729.68 |
| 512 | **+$158,579.97** | **17,157** | **6.6604** | **+$9.243** | $4,729.68 |

At cap 512 the engine did not actually require all 512 positions; observed max open was 497.

## Scientific disposition

The high-quality London/NY discovery survives the conservative audit.

However, earlier 30K-50K trade-count frontiers combined:
1. genuine chronological opportunity frequency;
2. multiple same-tick pyramid tickets created by a price jump through several ladder levels.

Those concepts are now permanently separated.

The one-event-per-tick frontier becomes the default for:
- trade/opportunity count claims;
- next feature research;
- later Jan-Jul validation.

Same-tick multiplicity may be reintroduced only as an explicit position-sizing/pyramiding layer with separate heat accounting.

## Exact durability

Helper SHA-256:
`6f566cd0dc7544ba2d2829b175515a76d2de8c08ba40627831f94ad3b4043b61`

Result SHA-256:
`33905746b7d0bf0ecd89dd1461ba09d155b79bbfedefb711d6019b9f771fd62d`

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

## Next units

1. Continue January discovery from the one-event-per-tick engine.
2. Search for causal mechanisms that increase **unique-tick** opportunity count rather than duplicating tickets on the same quote.
3. Treat same-tick scale-ins separately as explicit pyramiding exposure.
4. Full tick-level equity-DD on finalists.
5. Jan-Jul only after January architecture freezes.

R9 SYNTH remains the hard target.
