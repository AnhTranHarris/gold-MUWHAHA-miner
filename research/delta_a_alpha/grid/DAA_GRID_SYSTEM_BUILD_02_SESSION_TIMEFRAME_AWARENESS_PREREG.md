# BUILD-02 Session + Timeframe Awareness — Preregistration

Unit: `DAA_GRID_SYSTEM_BUILD_02_SESSION_TIMEFRAME_AWARENESS`
Candidate: `STMR-001`
Status: **PREREGISTERED**

Owner-directed order change: session/timeframe awareness precedes elastic geometry.

## Frozen research environment

- XAUUSD.
- January 2026 ordered Dukascopy ticks.
- Surface: `DUKAS_COINEXX_LIKE_P75`.
- Fixed lot: 0.01.
- Commission: 0.01 entry + 0.01 exit.
- No entry before 2026-01-05 00:00 UTC.
- No Martingale or loss-dependent sizing.
- Main `delta` read-only; August sealed; no MQL5.

Canonical tick SHA-256:
`d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`

## Session phases

Asia 23:00–07:00; London Open 07:00–09:00; London 09:00–13:30; overlap 13:30–16:00; New York 16:00–20:00; late NY 20:00–22:00; rollover 22:00–23:00 observe-only.

Each phase creates a fresh local lattice anchor and first-touch cell-memory scope.

## Timeframe roles

Completed bars only:
- H4/H1 = environment;
- M15 = phase;
- M5 = setup transition;
- ordered tick = trigger and fill.

Trend state is EMA(8) versus EMA(21) sign. H4/H1 path efficiency is eight-bar net displacement divided by summed absolute movement.

## Frozen routes

**ASIA_REVERSAL_INIT** — gap 0.75; TP 2.50; SL 1.00; max age 300s. H4=H1=M15=M5, H4 efficiency >=0.30, H1 efficiency >=0.25; crossing is opposite the aligned stack.

**LONDON_MICRO_RELAY** — gap 1.00; TP 2.50; SL 1.00; 300s. H4=H1=M15, M5 opposite; crossing follows M5.

**OVERLAP_LOWER_TAKEOVER** — gap 0.75; TP 2.50; SL 1.00; 300s. H4=H1, M15=M5 opposite; crossing follows M15/M5.

**NY_MIXED_MICRO_RELAY** — gap 1.50; TP 2.00; SL 1.00; 300s. H4/H1 do not form one aligned non-zero state, M15 and M5 oppose each other; crossing follows M5.

**LATE_LOWER_TAKEOVER** — gap 0.50; TP 2.50; SL 1.00; 300s. H4=H1, M15=M5 opposite; crossing follows M15/M5.

Rollover opens no new grid-owned position. Timer-only same-cell re-arm is prohibited.

## Ownership

Maximum simultaneous grid-owned positions: 3.
Every position is 0.01.

## January stability diagnostic

Discovery: entry date through Jan 16.
Validation: entry date Jan 17 onward.

Both remain January research, not external OOS proof.

## Required result

Report aggregate/discovery/validation economics; per-route ledger; active-day velocity; balance/equity drawdown; minimum equity path; 100/200/300 starting-balance diagnostics; concurrency; hold time; exit reasons.

## Acceptance

The build may become the January session/timeframe floor if:
1. net > 0 and PF > 1;
2. both January halves are positive;
3. no route is catastrophically negative;
4. 100/200/300 equity diagnostics remain positive;
5. no hidden residual inventory exists;
6. clean ordered-tick replay matches the frozen rules.

The 30% R9 milestone is not a hard gate for this dimension.
