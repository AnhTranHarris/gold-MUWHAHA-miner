# GAMMA-02 — Selective Unique-Tick Rebreak 016

**Status:** COMPLETE JANUARY DISCOVERY — CURRENT CONSERVATIVE OPPORTUNITY BASE  
**Predecessor:** GAMMA_02_ONE_EVENT_PER_TICK_AUDIT_014.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Scientific base

Opportunity-count claims remain governed by the conservative one-event-per-source-per-market-tick rule. Same-tick multi-level ladder fills are excluded from chronological opportunity counts and remain a separate future pyramiding/scaling topic.

Conservative cap-128 parent:
- +$77,049.12
- 10,351 trades
- PF 5.37153
- +$7.44364 expectancy/trade
- realized balance DD ~$2,927.21

## New causal opportunity factory

Pullback -> reclaim -> re-break.

A re-break can exist only after:
1. a favorable M1 extreme has already formed;
2. price causally pulls back from that extreme by at least the reset distance;
3. price subsequently reclaims/re-breaks the prior favorable extreme;
4. the re-break is deduplicated against the primary entry stream by source+market-tick;
5. another re-break cannot occur until another qualifying pullback occurs.

Direction remains owned by the existing completed-bar HTF/state rules.

## Generic re-break screen

Cap 128:
- reset $0.10: +$79,667.02 / 11,006 trades / PF 5.0371
- reset $0.20: +$79,367.44 / 10,791 / PF 5.1348
- reset $0.30: +$79,283.13 / 10,668 / PF 5.2051
- reset $0.50: +$78,950.55 / 10,569 / PF 5.2343
- reset $0.75: +$78,817.35 / 10,493 / PF 5.3048
- reset $1.00: +$78,389.43 / 10,454 / PF 5.3106

Generic re-breaks add net and genuinely time-separated trades, but NY16/18 degrade.

## Selective re-break

Re-break is therefore enabled only for:
- London / overlap source families;
- NY17.

NY16 and NY18 retain only the primary conservative opportunity stream.

Cap-128 screen:
- base: +$77,049.12 / 10,351 / PF 5.3715 / +$7.4436 exp
- **reset $0.10: +$80,358.08 / 10,749 / PF 5.3690 / +$7.4759 exp / DD ~$2,916.35**
- reset $0.20: +$79,859.54 / 10,580 / PF 5.4092 / +$7.5482
- reset $0.30: +$79,668.68 / 10,498 / PF 5.4386 / +$7.5889
- reset $0.50: +$79,238.95 / 10,427 / PF 5.4329
- reset $0.75: +$79,079.43 / 10,376 / PF 5.4726 / +$7.6214
- reset $1.00: +$78,633.02 / 10,360 / PF 5.4551

Best net gain versus the conservative parent is approximately:
- **+$3,308.96**
- **+398 completed trades**
- no same-tick duplicate opportunity counting.

The $0.10 selective reset is the current **net-maximizing base**. Larger resets trade some net for higher PF/expectancy.

## Exact durable artifacts

Persistent Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- `gamma02_rebreak_unique_tick_015.py`
  SHA-256 `20fd49774bb29bfd1d9cd9c6e6ce4d7d236b4e63639ac41b9888c45862001815`
- `gamma02_rebreak_unique_tick_015_cap128.json`
  SHA-256 `a6c787c44e796956cc454ba25966d9868e7a12e4504dea72adeb52f9ba9d14a5`
- `gamma02_rebreak_selective_016.py`
  SHA-256 `f025f12fdce1e70a8662342cf4b6a2fe1633fc4c2575f86c00e2c2bb6df6a083`
- `gamma02_rebreak_selective_016_cap128.json`
  SHA-256 `0d4790d7e54a25e7643bed49e0b87e921797ad0e9d7e478657f390ca70c21fb6`

## Next atomic refinements

1. Add a causal minimum elapsed-time requirement between pullback arming and reclaim (0.5/1/2/5 seconds) to distinguish genuine auction reset from immediate quote noise.
2. Test source-specific reset distances; NY17 likely wants a deeper reset than dense London sources.
3. Test state-transition-age / campaign heartbeat only after the selective re-break base is frozen.
4. Full tick-level equity DD only for finalists.
5. Jan-Jul only after January architecture freezes.

R9 SYNTH remains the hard target.
