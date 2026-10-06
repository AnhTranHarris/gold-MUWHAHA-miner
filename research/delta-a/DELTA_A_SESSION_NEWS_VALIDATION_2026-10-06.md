# DELTA-A Session / News Validation — 2026-10-06

**Status:** COMPLETE DIAGNOSTIC CHECKPOINT / NOT FULL 186,569-TRADE GRID REPLAY / NOT MT5 AUTHORIZED / AUGUST SEALED

## Helper forensic

The message-delivery timeout did not leave an active research helper running.

Latest completed January continuation helper:
- `SA100_R10AR_CAPITAL_GATED_INTEGRATION01`
- status: `COMPLETE_CONDITIONAL_SECOND_VELOCITY_INTEGRATION`

The older `sa100_build_core_stop_variants.py` remains:
- `INCOMPLETE_ANALYSIS_DO_NOT_RESUME`
- it was not resumed and is unrelated to this session/news unit.

The session/news unit was restarted from scratch after the delivery timeout.

## Durable bundle

Google Drive:
https://drive.google.com/file/d/1KJM9B_Saf_S4qj4rCLIn3KEZ9RvUKwKg/view?usp=drivesdk

ZIP SHA-256:
`18fdf9f4b41828b1564c3081ab4877ab841c008e60453436d0c61b9d8e13454d`

Contents: 16 files containing helper source, exact JSON outputs, result tables, diagnostics and the Tier-1 Jan-Jul scheduled-event calendar.

## Research surfaces

This checkpoint deliberately does **not** pretend the 73,205-event rampH diagnostic ledger is the frozen 186,569-trade R9 Grid Milestone 01 ledger.

Available surfaces used:
- January R2 rich-event ledger: 39,253 events, used only as a separate session diagnostic.
- Feb-Jul `sa100_rampH_candidate.csv`: 73,205 events, used for session/news policy research.
- Official R9 Grid Milestone 01 remains the certified comparison point: 186,569 trades, +$194,674.33 net, PF 1.2525.
- R9 SYNTH reference remains 219,342 trades, +$309,122.85 net, PF ~20.04, expected payoff ~$1.4093.

Therefore the last certified full-grid R9-SYNTH net alignment remains **62.98%** until the exact full milestone ledger/producer is replayed.

## VALIDATION01

Status: `COMPLETE_DIAGNOSTIC_NOT_FINAL_GRID_REPLAY`.

Initial Feb-Apr calibration / May-Jul screen showed:
- hard session exclusion is not supported;
- London/NY overlap is consistently the strongest session;
- source-wide filtering can reduce gross loss but sacrifices too much velocity;
- simple action filtering retains ~95%+ velocity but gives only small gains;
- naive event-type cells were unstable and were not promoted.

## VALIDATION02 — frozen split

Status: `COMPLETE_FROZEN_SPLIT_DIAGNOSTIC_NOT_FULL_GRID_REPLAY`.

Split:
- calibration: Feb-Mar
- selection: Apr
- final diagnostic: May-Jul

The Apr-selected action-only family did **not** improve final May-Jul net. It slightly improved GL/PF, so it remains negative evidence rather than a promoted adaptive layer.

A low-disruption secondary session/action cell emerged:
- suppress London-only / `c5400`
- May-Jul retention: **99.77%**
- May-Jul net: **$21,758.66 vs $21,650.22**
- May-Jul GL: **$157,543.07 vs $157,858.76**
- Feb-Jul retention: **99.61%**
- Feb-Jul net: **$50,225.77 vs $49,606.03**

## VALIDATION03 — causal adaptive test

Status: `COMPLETE_CAUSAL_ADAPTIVE_DIAGNOSTIC_NOT_FULL_186569_GRID_REPLAY`.

Adaptive session helpers were required to:
- use only virtual trade outcomes whose `exit_time_ms <= current entry time`;
- keep blocked opportunities virtual so state learning continues;
- use no current/future trade outcome.

Adaptive news helpers were required to:
- collapse simultaneous scheduled releases into one composite event;
- decide a current release quarantine only from **fully completed prior release windows**;
- use no current-release outcome.

### Session result

The online session/action EWMA-style gates were too aggressive. They removed too much velocity and did not survive the Feb-Mar -> Apr selection rule.

The surviving session-aware candidate remains the minimal static state cell:
`session == London-only AND action == c5400 -> no physical admission`.

Feb-Jul:
- retention **99.605%**
- diagnostic event-sum net **$50,225.77 vs $49,606.03**
- GL **$279,461.61 vs $281,373.85**
- PF **1.17972 vs 1.17630**

This is a candidate for full-grid replay, not a promoted architecture.

### News/event result

A blanket five-minute quarantine after every Tier-1 release looks attractive only after seeing later months:
- May-Jul: **+$24,419.12 vs +$21,650.22**
- retention **99.05%**
- GL improves materially.

But it loses net in Feb-Mar and April. Therefore it is **not causally selectable** from the earlier regime and is not promoted.

Likewise, adaptive prior-release policies become very strong in May-Jul. Example:
`GLOBAL_LAST1_Q15`
- May-Jul net: **$25,552.64 vs $21,650.22**
- retention **98.86%**
- GL: **$151,403.82 vs $157,858.76**
- PF: **1.16877 vs 1.13715**

However, it fails the April selection criterion. The correct conclusion is **news-regime nonstationarity**, not “always block news.”

No news policy was promoted by VALIDATION03.

## Current scientific interpretation

1. **Do not hard-disable sessions.** London/NY overlap remains valuable.
2. A tiny session/action ownership correction is promising because it preserves >99.6% of event velocity.
3. Tier-1 event behavior changes materially through the Jan-Jul regime. Static event blackouts are not robust.
4. News adaptation should eventually use scheduled event phase plus realized microstructure/auction state, not event name alone.
5. The next exact gate is to recover or reconstruct the frozen R3.4/A1 producer / 186,901 event specification and replay the 186,569 pressure-capped portfolio with the session candidate and preregistered event-state alternatives.
6. August remains sealed.
7. No MQL5 build is authorized or created.

## Hashes

- VALIDATION03 helper: `bd74081e95f0af6aa6524d625e9dab4be668da78e1f70562dd0e422bbf964699`
- VALIDATION03 JSON: `7af4de93c691173435ce63dbad6230152d48082360beacbb59f9358c8faad07b`
- VALIDATION03 results CSV: `c1f8d679b1e1454f3daea3d66d4ee7302e3d8df36c15d7ffc11578d9d24d1c4b`
- VALIDATION03 monthly CSV: `0a108f56e4a056de9a7aae993e5ae3f0accae58a1be1512e9a0e9d2015763430`
