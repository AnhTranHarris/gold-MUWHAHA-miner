# Delta-A-alpha 040: JAN039 reproducible January research-mechanism freeze

**Status:** `ACCEPTED_AS_JANUARY_RESEARCH_REFERENCE_ONLY`; not a production V1 alteration, deployable selection policy, MT5 Expert Advisor, funded-parent genealogy certification, or blind/generalized performance claim.

## Owner decision and what is frozen

Preserve the original owner-frozen, unabridged V1 **L0–L7** architecture as the system default. Preserve production `delta` read-only. Freeze the **JAN039 lowest exact-tick-DD candidate** as a versioned, inspectable research *mechanism library and reference replay*, available for future market-state correlation and native EA integration **after independent confirmation**. This freeze is **not** permission to run the JAN039 risk settings on live or small accounts.

Authoritative source: `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, hardlock `_031`, GitHub state journal 0057, and archived Jan037/038/039 Library source bundles. `JAN039_SELECTED_VERIFIED.json` in the Library contains original metrics. January is **already exposed in-sample**. August 2026 SEALED, September RESERVED.

## January research performance (real Dukascopy Bid/Ask, proposal-tape model)

- January gzip SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- 9,135,062 ordered quotes, fixed research 0.01 lot, research balance $100,000, simplified leverage assumption 1:500, $0.02 modeled fee per position; **no certified Coinexx fills, actual margin/stop-out or slippage**.
- Net **+$201,226.483**, gross loss **−$5,562.307**, PF **37.1768**, **12,520** trades, exact quote-path floating equity DD **$12,640.925**, balance DD **$1,491.854**, max-open **512**.
- Relative to JAN037 gross loss decreased **76.307%**, equity DD decreased **70.142%**, and 78.693% of JAN037 trading volume remained. Strict 75% DD goal **was not met**.
- 21/21 research trading days and 5/5 ISO weeks positive; **Jan 30 alone generated 58.52% of net**. Further cost of ~$0.10/trade would erase the narrow $200k profit headroom.
- As-of/source proposal and static profit-model conditions are **not a live proof**. The upstream source-proposal tape was not regenerated after every rejected child or modified funded lifecycle; native L5 and conditional recovery L6 are not wholly restored; L7 broker margin acceptance and actual MT5 parity are pending.

## Exactly reproduced JAN039 mechanisms

The source-era numeric IDs (S26, S27, S21 etc.) identify **original preserved generator instances** in JAN037/038. These identifiers require explicit mapping to proper L1–L5 market-structure ownership before MT5 implementation. Do NOT substitute simplistic indicator streams.

1. L0: original ordered executable Bid/Ask quote-side entry and first passage; no mid-price trade fills. Keep baseline original exits unless a **profitable first-touch override** is observed at a later quote.
2. L1/L2: the **original upstream source's session-specific grid geometry and completed H4/H1/M15/M5 permission** must be preserved; JAN039 adapter never creates trades by itself.
3. L3: experimental 10-minute subphase mask `(source_ID, UTC phase index 0..5)` is frozen in `jan039_research_policy.py`. The mask comes from **January-fitted JAN038** and must NOT become a universal month-blind rule without validation. L3 expands original hourly heartbeat candidates as in JAN037 source (`JAN037_EXPANDED_L3_50MS_PROPOSALS.npz`). A previous 25ms proposal cadence was empirically identical to 50ms on January data.
4. L3 S27 short source: if original proposal and spread/phase gates pass, first profitable executable close before original source exit at **$60** on phase0, **$50** on phases2/3, **$35** on phase4 per 0.01 lot. For other phases and other sides, use original exits. S27 phase0 max **224** positions; phase5 max **128** positions (counts attributed to each opening phase, decremented on funded close); phase 2/3/4 do not gain additional standalone caps.
5. L3 S26 short source: first profitable executable close before original exit at **$35** per 0.01 lot; source-wide max **432** positions (not an absolute broker capability). Original S26 opportunities must still pass their geometry and HTF gates.
6. L4 Watchdog: bounded global **8**, same price-cell/side **4**, earned unlock after **two qualifying genuinely closed children**, one scout budget per cell. Never credit shadow/non-funded child outcomes. Rejecting child invalidates its parent's subsequent sequence. **Original future parent proposal generation still must be rebuilt endogenously before V1 certification**.
7. L5/L6: preserve original V1 native trend-within-trend and conditional wrong-direction recovery interfaces; **JAN039 replay did not independently certify their final V1 versions**. No generic inversion, hedging, Martingale, DCA or loss-triggered lot scaling.
8. L7: total maximum **512**, one order per quote and at most **three modeled admissions per UTC second**; spread max **$3**; signed 20-second source impulse >= 0 for original L3 IDs >=17; original excluded hourly sources inherited from JAN037 `l3_excluded_hours=291712`. Real broker symbol contract, order acceptance, margin, stopout, account heat, concentration, latency and slippage MUST independently control/possibly reduce these experimental caps.

### Portable, reproducible replay

Dependencies: Python 3.11+, numpy, pandas, numba. Obtain the ORIGINAL nonmodified source artifacts from Library, rather than constructing new proposed trades or using R9 SYNTH as execution truth. Required assets:

- `JAN037_ORIGINAL_SOURCE_PROPOSALS.npz`
- `JAN037_EXPANDED_L3_50MS_PROPOSALS.npz`
- `JAN037_WD_EXACT_8.json` (all from JAN037 bundle)
- `JAN038_SELECTED_EXACT.json` (from JAN038 bundle)
- `gamma02_funded_cap_equity_dd_028.py` (from 032 original frozen helper chain)
- `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` (verify SHA above)

For example, from this directory:

```sh
python jan039_reference_replay.py \
  --ticks '/path/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz' \
  --jan037-dir /path/jan037_extract \
  --jan038-selected /path/JAN038_SELECTED_EXACT.json \
  --legacy-equity-dir /path/original_032/source \
  --out jan039_reference_qa.json --save-ledger
python -m unittest discover -p 'test_jan039_research_policy.py' -v
python jan039_market_context.py '/path/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz' jan_context.json
```

`jan039_reference_replay.py` checks tick-input SHA and compares exact net, gross loss, trade count and complete tick-path equity DD to the archival reference. It writes fresh daily/weekly attribution and optional ledger. The archived model is in `jan039_legacy_engine.py`, with **only local input paths made portable**. The thin adapter `jan039_research_policy.py` exposes frozen rules for later integration, **not a replacement engine**. The independent test suite validates structural permissions, UTC phase, initial history, capacity and risk-denial paths.

## Market-blind and month-blind deployment specification

The owner correctly distinguishes **startup read-in** from **ongoing adaptation**. Within 300s from first valid tradable broker quote (and ideally immediately when prehistory is hydrated): load real *completed historical bars* for H4/H1/M15/M5, session/DST, original session grid and order/risk state; test quote freshness, spread, margin/free equity/stopout, symbol lot permissions and prior funded campaigns. **Five minutes is a readiness deadline, not five minutes of total HTF history, a mandatory minimum observation period, a forced order, or a performance guarantee.** Without required completed pre-T0 bars, flag readiness failure; don't invent December history or silently trade with incomplete structure. The baseline V1 remains available as soon as the context is qualified.

`jan039_market_context.py` produces **observed 10-minute closed-bucket descriptors** (tick density, price range, directional movement, mean/max quoted spread) for each January bucket, plus evaluation-only January30-versus-other summary. These are NOT causal Jan-specific winning-condition thresholds. `jan039_research_policy.ObservableMarketFingerprint` extends candidate context with **previously completed** M5/M15/H1/H4 range, causal 20-second impulse, DST/session state, 10-minute subphase, and physical portfolio exposure/heat. Store signature at *decision time* and compare to settled funded results only later. Do not use same-day realized range or the closed 10m bucket while it is forming.

### Required future mechanism for adaptive activation, not yet learned

1. Build exact 049→051→075→084→119→131E *and* February/March/April source lineage preserving L0–L7; replace fixed proposal tape with **online, true funded parent-child genealogy** and actual broker acceptance/margin state.
2. From completed January replay, create *entry-known* decision snapshots, not retrospective day labels; relate fingerprints to realized outcomes and cohort heat with timestamp audits.
3. Carry unmodified V1 and this JAN039 candidate into February, March, April and subsequent monthly chronological replays. Calibrate an explainable state→geometry/TP/caps selection rule using strictly earlier available observations; test original V1 fallback and regressions on previously seen months, then untouched validation; reset/reduce on conflicting evidence.
4. No `if month==January` or `if date==Jan30` selectors. Compare observable activity/volatility, MTF phase, HTF ownership, session/DST, spread, displacements, funded renewal quality, and global heat.
5. Evaluate **net profit as high-priority**, alongside gross loss, realized and equity DD, PF, velocity, funded max-open, realistic leverage/margin and $100/$200/$300 small-account survivability. The January high-account 512 positions are NOT small-account compliant.
6. MQL5 faithful port only after layer-level Python↔MT5 parity; zero compiler errors, tests on MT5 Every tick based on real ticks, ongoing demo, appropriate risk controls and documented fallbacks.

## Governance

This is a **separate source-frozen research branch**. No alteration of the original V1 whitepaper, `Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5`, production Delta, sealed data or currently accepted monthly floors. The original V1 system stays primary and its behavior must remain reproducible. JAN039 is **kept as a candidate mechanism with exact evidence** for later adaptive correlation and possible *explicit* promotion. Reference replay parity is **NOT** funded-V1 implementation certification.