# R19 H1V2: source-exact broker-conditioned 15-minute/hourly hindsight entry research

**Nondeployable offline hindsight — no causal BUY/SELL/WAIT, no MT5 EA promotion.**

This is an **add-only branch**, created from R18 SHA `6572ad03ae76daa80e188f213a5a2d1279dac42b`. Do not edit R9 v2 repaired runtime `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`, original H1V2 teacher, or R11–R18 archives. The four source months are original Jan, Feb, Jun, Jul **2026**.

## Mandatory restart: full-source, not an abbreviated research summary

Read the complete previous five-volume forensic audit and all original R18 recovery sources before editing:
- **New R19 append-only execution/recovery ledger:** https://docs.google.com/document/d/1c-Z0pe_YwXq-yUhh_ZPNqV5BpAXIMeD80eoCFjTPvf0/edit
- **Full source-level 40-scenario and 46-negative-quarter audit:** https://docs.google.com/document/d/12VY9eLLy8LbyrK2zYi9kuNriMvSgIVp32lzM39YYgEs/edit
- **R19 all binary source ordinals, full periods, member SHA manifests:** https://drive.google.com/drive/folders/12lTCJ04QtCmhnkWOz5RfI94V-y4E8qH7
- **R18 original experimental data & full source:** https://drive.google.com/drive/folders/1ChZ3K0mSC64XY3BbhoUWPH-BcQsSFTEo
- **R18 full append-only experiment ledger:** https://docs.google.com/document/d/1aN6HOvsVj4_OQyCxsUeH8lkuUkYoW6rHH8kQbIc7Q7U/edit
- **Original full forensic audit and predecessor five-volume re-audit:** https://drive.google.com/drive/folders/1ilumXIGt_xiadwsrYtIH5HDopYEw-gcn

Raw source eight gzip SHA and broker clock evidence are in the R18 ledger; **rehash all original source gzip bytes before reproduction**. Dukascopy source uses UTC integer bid/ask 0.001 price units; MT5 historical broker export has MT5 server `time_msc`, normalized by actual verified historical -2hr Jan/Feb, -3hr Jun/Jul for these inputs. June MT5 raw source requires the real July cross-month quote halo; do not interpolate the true market gap. MT5 historical broker quote export **does not prove live Coinexx dealer fills nor replicate the R9 SYNTH Strategy Tester feed**.

## Original labels and owner-governed acceptance — never conflate

- Original R11S1 **first +$0.10 net <=15s and zero opening-liquidation -$0.10 adverse through full 30s**, with 30s future coverage, is immutable. Earlier R11S4 fixed30 occupancy teacher gives 246 30s-contract impossible hours, not a universal limitation under different contracts.
- R18/R19 new retrospective label: actual observed Ask-paid BUY/Bid-received SELL, nominal 20 raw-unit quoted-price fee, first +100 raw-unit net before first -100 raw-unit opening-liquidation adverse within 60sec, after actual observed 100/500ms fill and source quote staleness<=1s. It is a **changed 60s post-entry competing-first-passage outcome, not the original R11S1 or original R9 dynamic trailing/stop exit**.
- Separate 60s **pre-entry watch** in R18 conditions on prior observed quotes; do not mistake it for a post-entry favorable horizon.
- Up to `$4.00` spread is an experimental source diagnostic, not approved broker risk exposure. No actual commission, dealer rejection, funding, cash lot PnL, initial equity or margin survival is certified.
- No adaptive quota-forcing or post-hoc '80% precision' from hindsight. Zero-latency selected future-positive trades and reselected delayed survivors are retrospective oracles; **no prospective model is evaluated**. Owner whole EA acceptance requires >=85% original SYNTH monthly count, >=80% correctly judged trade criteria over active periods, positive realistic net and account risk survival; unproven.

## Cycle R19-1 — multischedule original R18 source union

- V1 `src/r19_multi_clock_union.py` and immutable source-equivalent `src/r19_multi_clock_union_v1.py`; speed-optimized `src/r19_multi_clock_union_v2.py`. V2's Feb Dukascopy all five scenario+quarter+hour original records reproduced V1 byte-exact.
- Ten **original zero-delay R18 future-selected**, otherwise as-of source-clock / broker-spread / volatility / WATCH60 / dense-grid schedules are deduplicated by original quote ordinal. Original side is future-labeled! Reject conflicting quote side. For each proposed quote, independently evaluate actual delayed fill and +100 before -100 raw first passage before future-privileged nonoverlapping repack.
- Experimental stress grid includes lag100/no added slip, lag100/20 raw slip per leg, lag500/20 raw slip and cap4000/cap2500/cap1500.
- **8/8 original source months independently verified**, every original selected entry quote, side, first filled quote, actual exit, net arithmetic and original UTC quarter/hour count. All 40 source cases and full original quote ordinal NPZ preserved in per-month ZIPs.
- At lag100/zero slip/cap4000 future-known source capacity: DUKAS **7,425/7,521** source-active 15m quarters and **1,911/1,917** active hours; MT5 export **7,519/7,521** and **1,917/1,917**. Improvement vs R18-S2 single-schedule DUKAS 7,378 and 1,904 is +47 periods and +7 hours.

## Cycle R19-S3 — new 25ms as-observed source-admission on failing periods

- New source `src/r19_s3_targeted_source_admission.py`, independent `verify_r19_s3_source_exact.py`, full member-SHA ZIP packager `build_r19_s3_archives.py`.
- Only missing quarter source timewindows from R19-1: first **actually observed quote per 25ms bin**, real 300s gap-free freshness after >15s source drought, source spread<=4000, actual first quote at least 100ms afterward, age<=1000ms, fill spread<=4000. Both BUY and SELL individually future-first-passage tested (full two-side NPZ including losses/censors).
- Additional future winners only admitted into *old position-free gaps*, so every R19-1 winner retains its original entry and exit quote ordinals. One-position exact-firstTP occupancy, no crowding or retroactive alteration.
- **8/8 original source/month independent verifiers passed** exact raw quote membership, gap warmup, bid/ask favorable-before-adverse, fill ordering, no overlap, every source UTC quarter/hour. 3/3 Cycle1 unit tests and Python compileall pass.
- Dukascopy Jan **+33** future winners, 1,875/1,878 Q 480/480 H; Feb **+156**, 1,793/1,819 Q 456/458 H; Jun **+32**, 1,949/1,954 Q 497/497 H; Jul **+226**, 1,860/1,870 Q 481/482 H.
- Total Dukascopy +447 retrospective nonoverlap positions, **7,477/7,521** quarter goals, **1,914/1,917** hours; +52 quarters, +3 hours over Cycle1; +99 quarters and +10 hours over original R18-S2. **44 Dukascopy 15m periods and 3 hours still fail.**
- MT5 linked broker export **7,519/7,521 15m, 1,917/1,917 hours**, two nonfilled source quarters: Jan01 23:30 UTC (503 raw quote rows but 0 pass 300s post-gap freshness) and Feb01 23:00 UTC (4587 raw quotes, 75 as-of eligible but zero new observed first-touch winning actions), all other quarters met.
- Every one of the **46** two-feed negative quarters, including spread50/p90, >1.5/>4 fraction, raw gaps and exact slot deficit, remains in **full audit document**, not hidden behind these navigational fields.
- All eight S3 source ZIPs uploaded MT5_EXPAND folder, complete selected source ordinal, **every** 25ms candidate dual-side outcome array, complete original UTC quarter CSV and SHA; local ZIP byte/member SHA+CRC pass. Google remote metadata size+parent matches; **remote byte-level ZIP hash was not repeated**.

## Current blockers and distinct next falsification

1. **Sufficiency and identifiability:** 100%-future-selected repacking is an optimistic capacity bound for these original candidate universes. A strictly causal BUY/SELL/WAIT classifier remains absent; R18-S1 frozen original actions lost quality to 100ms delay (DUKAS 74.1313% conditional strict), thus the current capacity is not executable trading alpha.
2. **Remaining 44/2 quarters:** source-exact 25ms including original gap/warmup may still have inadequate profitable observed paths; no safe generic widening or shorter-risk override allowed. Retain source quote and original R9 reference counts.
3. **New path model:** fit cause-specific favorable-before-adverse, adverse-before-favorable, censor, spread widening and quote stale hazards conditioned on **previous** 250ms/3s/15s/60s/300s quote chronology and completed 15m/H1/H4 market structure, source broker and session. Explicit option value of WAIT vs one-position occupation. Separate P(opportunity exists) from directional ranking.
4. **Execution:** first 100ms/500ms observed-price stress with slippage/fees not assumed to match dealer latency/fills. No R9 full dynamic stop/trail plus account economic PnL, no actual Coinexx historical fills.
5. **Testing:** purged chronological embargo, entirely unused later-calendar OOS source (July already exposed), out-of-broker transfer and sessions, tail loss, funded account constraints; fail closed on missing model/feature/artifact SHA.
6. **Preservation:** append **all** new source hashes, every failed run and proof, monthly quarter/hour evidence to existing append-only Drive ledger; create an isolated new branch for further distinct mechanisms, do not rewrite this R19 branch or earlier artifacts.

Scientific classification: **source-verified hindsight opportunity improvement**, not an 80%-correct deployed EA.
