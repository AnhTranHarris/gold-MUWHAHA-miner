"""Unabridged R20 forensic documents. Complements lossless binary source ZIPs."""
from __future__ import annotations
import csv,json,hashlib,datetime as dt
from pathlib import Path
P=Path('/mnt/data/h1v2_r20_last46');B=P/'archives';B.mkdir(exist_ok=True)
R19=Path('/mnt/data/h1v2_r19_broker_union');
def txt(path):return path.read_text(encoding='utf-8')
def rows(path):
 with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def as_csv(rr):
 assert rr
 from io import StringIO
 f=StringIO();w=csv.DictWriter(f,fieldnames=rr[0].keys());w.writeheader();w.writerows(rr);return f.getvalue()
base=rows(P/'R20_ALL_88_EXACT_SOURCE_MONTH_CONTRACT_RESULTS.csv')
month=rows(P/'R20_ALL_UTC_MONTHLY_REFERENCE_AND_DAY_QUARTER_HOUR_RESULTS.csv')
day=rows(P/'R20_ALL_UTC_DAYS_ALL_11_SCENARIOS_EIGHT_SOURCE_MONTHS.csv')
week=rows(P/'R20_ALL_MONTH_CLIPPED_ISO_WEEKS_ALL_11_SCENARIOS.csv')
witness=rows(P/'R20_ALL_43_RESIDUAL_15MIN_FAILURE_WITNESSES_FULL.csv')
sha=json.loads((B/'R20_ALL_EIGHT_ARCHIVES_AND_EXACT_SOURCE_MEMBER_SHA_MANIFEST.json').read_text())
extra=[]
for src in ('DUKASCOPY_RAW','MT5_BROKER_EXPORT'):
 for mo in ('01','02','06','07'):
  r=R19/'results_defect_diagnostics'/f'R19_{src}_{mo}_ALL_ORIGINAL_UTC_QUARTER_RAW_SPREAD_GAPS_AND_DEFICITS.csv'
  rr=rows(r);lookup={x['original_UTC_quarter']:x for x in rr}
  for x in witness:
   if x['source']==src and x['month']==mo:
    l=lookup.get(x['UTC_quarter']);assert l is not None
    extra.append({**x,'source_original_raw_quote_rows':l['original_source_raw_quote_rows'],
    'source_spread_median_USD':l['original_quote_median_spread_USD_per_oz'],
    'source_spread_p90_USD':l['original_quote_p90_spread_USD_per_oz'],
    'source_spread_p99_USD':l['original_quote_p99_spread_USD_per_oz'],
    'source_fraction_spread_above_1p50':l['original_quote_fraction_spread_gt1p50'],
    'source_fraction_spread_above_4p00':l['original_quote_fraction_spread_gt4p00'],
    'source_gap_over_15s_inside_quarter_count':l['original_quote_gaps_gt15s_wholly_inside_quarter'],
    'source_raw_max_intraperiod_gap_ms':l['max_original_intraperiod_gap_ms'],
    'source_original_R18_frozen_union_candidate_ordinals_count':l['R18_original_10lane_frozen_unique_candidate_ordinals_in_quarter'],
    'source_any_quotes':int(l['original_source_raw_quote_rows'])>0})
assert len(extra)==43
(P/'R20_ALL_43_RESIDUAL_FULL_QUARTER_RAW_SPREAD_GAP_AND_ORACLE_FAILURE_FORENSICS.csv').write_text(as_csv(extra))

header='''GOLD MUWHAHAHA MINER / XAUUSD HTF — R20 UNABRIDGED DUAL-BROKER H1V2 SOURCE-EXACT RESEARCH
Generated 2026-11-03 America/Chicago. This evidence is NOT a predictive trading system, an operational MT5 EA, financial advice, or a live broker fill certificate.

Purpose: preserve all actual experimental source lines, including negative outcomes and all original 11,520 UTC quarters of the four specific months for each independent feed, without destructive summarization. Prior five-volume audit, original R18 and R19 source ZIPs and GitHub commits remain immutable sources rather than being replaced by narrative.

SOURCE AND LINEAGE:
Five-volume audit: https://drive.google.com/drive/folders/1ilumXIGt_xiadwsrYtIH5HDopYEw-gcn
R18 immutable source and full evidence: https://drive.google.com/drive/folders/1ChZ3K0mSC64XY3BbhoUWPH-BcQsSFTEo
R19 immutable source and full evidence: https://drive.google.com/drive/folders/12lTCJ04QtCmhnkWOz5RfI94V-y4E8qH7
R19 additive Git HEAD: 0c8aaa8430bdd668ab6e8585cb75e702f21b1f9f
R9 repaired original runtime: ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0
R9 SYNTH original UTC month reference counts Jan27980, Feb33523, Jun31758, July24324. Those are comparator counts, not a price feed substituted for actual Dukascopy quotations.

CORE EVIDENCE CONTRACT:
- Eight historical independent source-month pairs: Dukascopy raw and broker-linked MT5 historical export, January/February/June/July 2026. Coinexx-linked MT5 export is not a certified live Coinexx fill, independent broker transaction ledger, or R9 synthetic spread model.
- Original Q and H quotas are original R9 SYNTH event counts aligned to UTC, not imposed by model as a trade-forcing action; 7,521 active 15m buckets and 1,917 active hours per feed; 11,520 UTC quarters and 2,880 UTC hours per feed, including all zero-reference records.
- BUY entry Ask and closes future Bid; SELL entry Bid and covers future Ask. Source integer raw unit=USD0.001 XAU quoted PRICE per oz. Nominal historical fee USD0.020 quoted price. At least USD0.100 nominal net required before a loss barrier. Never treat 0.020 quoted-price fee as 0.020 USD cash trade commission without broker contract size.
- Fill is FIRST ACTUAL observed original Bid/Ask quote at or after entry signal +100/500ms, subject to <=1000ms excess quote staleness and actual-fill spread; not interpolated using candle OHLC. Same-ms source quote ordinals are not future exits under research policy.
- Original >15s quote drought resets epoch, 300s fresh continuous warmup before entry. Source-end / gap before exit yields CENSORED, never forced win or zero-loss.
- R19 original trade dates, entry fill ordinals, future-firstTP exit ordinals are frozen. R20 adds only nonoverlapping extra future-selected successes in original residual quarters. No previously qualified trade is removed to fabricate coverage; however isolated source upper explicitly tests alternative within-quarter replacement.
- Every C1-C6 source candidate is past-observed current quote only, BUY/SELL offline outcome label uses future. Every S0-S4 changes adverse stop and can alter loss magnitude. C5 mixes 500ms/slip20 NEW interventions with old 100ms/slip0 R19 winners and is NOT an internally uniform portfolio policy.
- Strict original R11 S1 first <=15s favorable AND full30 zero adverse, source R18 60sec firstTP-before-adverse and 60sec preentry observed WATCH are DIFFERENT scientific contracts. Do not collapse all into a single accuracy label.
- Causal BUY/SELL/WAIT fitted policy, chronological future unseen validation, source-exact R9 dynamic stop/trail/timeout/account PNL and actual dealer fill remain UNVERIFIED. July cannot be called blind OOS after repeated historical exposure.

ARCHIVAL CLASSIFICATION:
SOURCE_PASS: externally hash pinned raw compressed bytes successfully reread and replayed with source ordinal consistency.
SOURCE_ORACLE_SUCCESS: future informed side and exit known after the fact, NOT learned prediction, so 100% hindsight winning labels are a tautology.
COUNTERFACTUAL_INDEPENDENT_OUTCOME: hypothetically doing every signal on BUY and SELL; simultaneous/action overlapping per-trial economics are not an implementable portfolio or expectation for an actual action policy.
EVIDENCE_LOSSLESS: every original file in eight full source-month ZIPs, quote ordinal arrays and 11 full regime calendars; per-file CRC/SHA receipts. This document is not a replacement for the source packages.
'''

methods='''
EXPERIMENT PRE-REGISTRATION — exact mechanisms tested before outcome inspection

R20-C1 (strict cap 4): At each original R19 residual failed quarter, emit first quote observed at a unique 1ms tick timestamp, after full v5 warmup. Filter source spread and actual delayed quote spread <=4.00 and lag100ms. Independently label BUY and SELL first true executable +0.10 net before opening-liquidation -0.10 adverse touch within 60s, then add only winners that do not overlap original R19 incumbent intervals. This tests whether 25ms discretization suppressed sufficient real historical opportunities. It recovers zero additional selected positions. This falsifies the tested residual candidate-clock hypothesis, not every possible new entry universe.

R20-C2 (experimental cap 8): Identical to C1 except source and executed spread<=8.00. Full bid/ask barrier is paid. Spread widening may admit events whose required gross move is larger than spread + USD0.12, while adverse loss remains USD0.10 relative to opening liquidation; no free spread reduction. Only one extra hindsight winner was added across all eight source-months and no new quota. Widened spread is NOT approved as a live Coinexx/Dukascopy broker risk configuration.

R20-C3/C4 first favorable horizon30/15: Same other geometry as C2, but 30,000/15,000ms first touch before adverse. These are distinct new labels and have no claim of full30 adverse-free S1. C3 one new winner without added quota; C4 zero. The longer 60s initial trade window can increase oracle capacity in a limited cohort but does not by itself provide predictive direction or lower account risk.

R20-C5 execution alternative: source+fill <=8, 500ms first delayed observed fill, extra 20 raw units per leg, horizon60. Five newly retrospectively selected winners, one new UTC quarter and one hour across eight source-months. CRITICAL LIMITATION: old incumbents remain original lag100/slip0 fillcap4; the combined portfolio has heterogeneous fill assumptions without a trained as-of broker execution mode/router. It is an offline counterfactual fragility exploration, not a consistent uniform execution-policy result.

R20-C6 source grid 25ms at enlarged cap8: A distinct control that shares C2 fill/horizon. In this residual event universe the 25ms grid recovered one candidate offline winner, same C2 result. More timestamp reconsiderations are not proof of a new edge under one-position concurrency.

R20-C7 isolated quarter replacement upper: For each original R19 failed quarter collect all frozen existing successful source intervals with fills in that quarter, plus every newly classified future-good fill interval in C1-C6. Exact earliest-finish greedy under identical quote intervals provides maximum nonoverlapping wins within that isolated quarter, deliberately ignoring predecessor/successor quarter occupancy. These are source RESTRICTED optimistic uppers, not universe-wide source impossibility. Of 46 baseline failed quarters, C1 max could meet only three under that restricted intervention; C2 three, C3 three, C4 two, C5 four, C6 three. Even direct quota-priority reoptimization cannot remove the missing candidates within these restricted event universes. It might require a truly different source candidate or target/action/risk contract, not a beam-width retune.

R20-C8 broker-conditioned conditional adverse stop research (distinct risk target): Source and filled spread<=8, observed distinct-ms admission, actual first quote after 100ms, full nominal spread & fee, net TP>=+0.10, first-touch within60s. Use adverse -0.10/-0.20/-0.50/-1.00 quote-price, and dynamic max(0.10,min(1.00,0.25*current_executable_spread)), all quoted-price USD/oz. Analyze BOTH side possible outcomes independently, including stop loss and first-observed timeout with separately registered NET, CENSORED and rejected. Only hindsight winning intervals free of R19 incumbent positions are added. Original -0.10 hard adversarial label is NOT preserved for S1-S4. This is a new historical risk contract, not an original H1V2 fixed15full30 success.

Every version tests long/short independently against the actual BID/ASK. Stop is checked before favorable on each original later tick (conservative within same updated quote). Because the remaining candidates are severely event-clustered and often have >15s source gaps, increasing adverse budget partly increases available future-positive intervals but also exposes substantially greater downside. Evaluation of all independently possible BUY and SELL actions produces negative aggregate hypothetical quote PNL in this cohort: it is mathematically INAPPROPRIATE to present the future-selected winning subset alone as an expected positive portfolio.

Cross-broker adaptive candidate design that MAY deserve future NEW tests — NOT executed/confirmed by R20: latent quote-state hazard graph conditioned on actual spread strain, bid/ask leadership, realized observed 3s/15s/1m/5m volatility, as-of completed 15m/H1/H4 price features, bid and ask joint 9+-mark excitation process, quote drought hysteresis, weighted competing favorable/adverse/timeout causes, and optional 0-60s spread-confirmation WATCH option value. This must be independently calibrated and then LIVE/OOS tested; merely naming sophisticated mechanisms or generating future winners cannot promote alpha.

RECOMMENDED NEXT FALSIFIABLE MODEL CLASS (unimplemented, SPECIFICATION): For each broker B and time t, forecast independent cause-specific hazards lambda_{B,side,favorable}(tau|F_t), lambda_{B,side,adverse}(tau|F_t), lambda_{B,censor/gap}(tau|F_t) for tau<=60sec, with F_t containing ONLY observed raw Bid/Ask marks, current spread/age, quote burst state, completed HTF history, and frozen known costs. Forecast executable expected net including adverse dynamic stop/trail, margin/opportunity occupancy cost and tail loss; BUY and SELL each must independently pass positive expected net and calibrated false-entry constraint before comparing to WAIT. Train by purged date and independent acquisition source, broker stratification/hierarchical pooling, censored likelihood, walk-forward with frozen thresholds, fail closed on missing source or stale model hash. Trading quotas are ex-post scorecards, never a mandate to enter negative-expectancy states. This is an explicit untested proposal, not a research result.

ADVERSARIAL CONTROLS AND OBSERVED IMPLEMENTATION FAILURES:
- 7/7 new quote-geometry and stop-first unit tests passed, including BUY/SELL bid/ask price differences, full nominal fee and extra slip, strict first profitable observed quote, stop-before-TP, 15 vs 60s horizon, right censor on unobserved >15s quote interval, incumbent trade overlap.
- Initial R20 Feb run successfully wrote atomic CSV, NPZ and receipt then raised a reporting-only JSON encoder TypeError caused by wrongly passing flush=True into json.dumps. Source printer fixed and tests rerun; all original outputs preserved, negative failure log retained.
- First R20-C7 archive generator attempted to emit data rows where an MT5 source had ZERO originally failed quarters, raising EMPTY_RESULTS. Corrected to explicit header-only zero-row artifact. Never manufactured a false failure witness.
- Full eight-source independent source quoted-price firstpassage verifier passed all original 138,240 C1–C6 quarter rows, 34,560 hour rows, all original source month SHA pins and individually reexamined every selected extra trade against original source quoted prices.
- All eight C8 source-month independent verifiers passed all 115,200 C8 quarterly rows and 28,800 hourly rows, quote entry/exit/fee, exact first-price touch for 39 newly selected records across the five alternative risk contracts. No original selected interval removed.
- ZIP CRC, local full member SHA, eight archive SHA, all source input SHA and original event cardinalities retained. Uploaded remote archive metadata does NOT by itself independently prove remote byte rehash; remote binary hashes can be reverified by authenticated download on a later session.
- Neither original tick flags in actual MT5 MqlTick structure nor dealer queue/order book/fill audit were verified. MetaQuotes reference identifies the MqlTick time_msc plus bid/ask and flags, and distinction between COPY_TICKS_INFO and COPY_TICKS_ALL. See https://www.mql5.com/en/docs/series/copyticksrange and https://www.mql5.com/en/docs/series/copyticks .
- Source quote ends and UTC clock gaps have not been synthesized into trades. July raw source halo in Coinexx-linked MT5 June used separate real original July gzip and independently recorded provenance; no fabricated June closing quotes.

STATISTICAL STOP RULE: When a new counterfactual only produces 1-13 additional future-selected winners in 8 four-month source subwindows while independently possible BUY/SELL/WAIT economic evidence remains negative, stop iterating stop parameters merely to make retrospective accuracy look better. Prioritize a causal two-broker state/hazard learner and complete broker-accurate account risk and PNL, or admit infeasibility under currently priced quotes. Beware researcher multiple-testing and no blind independent validation date in this exposed four-month calendar.
'''

# Machine-level source manifest preserved exactly, not a prose abstraction.
manifesttext=json.dumps(sha,indent=2)

vA=header+'\n'+methods+'\nSOURCE ARCHIVE MANIFEST — COMPLETE, ALL MEMBERS AND SHA RECORDS\n'+manifesttext+'\n'
(P/'VOLUME_A_R20_FULL_METHODS_MECHANISMS_NEGATIVE_BROKER_FORENSIC_20261103.txt').write_text(vA)
vB=(header+"\nVOLUME B — ALL 88 SOURCE-MONTH-CASE RESULT ROWS, ALL 43 UNMET QUARTERS WITH SOURCE RAW SPREAD AND GAP DIAGNOSTICS, ALL 88 ORIGINAL MONTHLY SCORECARD RECORDS. NO ABRIDGEMENT.\n\n"+
  "ALL_88_CASE_ROWS\n"+as_csv(base)+"\nALL_88_MONTH_AND_DAY_SOURCE_COMPARATOR_ROWS\n"+as_csv(month)+"\nALL_43_SOURCE_EXACT_NEGATIVE_WITNESSES_WITH_R19_RAW_BIDASK_DIAGNOSTICS\n"+as_csv(extra))
(P/'VOLUME_B_R20_ALL_88_CYCLE_RESULTS_ALL_43_UNMET_ORIGINAL_SOURCE_WITNESSES_20261103.txt').write_text(vB)
# Split the exact full calendar into 3 native volumes for Google Docs import safety.
part=880
for i in range(3):
 group=day[part*i:part*(i+1)]
 assert len(group)==880
 v=header+f'\nVOLUME C{i+1}: ALL DAYS NO SAMPLING. Calendar source row numbers {i*part+1} through {(i+1)*part}, total {len(day)}.\n\n'+as_csv(group)
 (P/f'VOLUME_C{i+1}_R20_880_FULL_SOURCE_UTC_DAILY_RECORDS_20261103.txt').write_text(v)
vD=header+'\nVOLUME D — ALL 440 MONTH-CLIPPED UTC ISO WEEK SOURCE RECORDS, NO SAMPLING. Some ISO weeks are clipped at month boundaries and not full calendar week.\n\n'+as_csv(week)
(P/'VOLUME_D_R20_440_ALL_SOURCE_ISO_WEEK_MONTH_CLIPPED_RECORDS_20261103.txt').write_text(vD)
print(json.dumps({p.name:p.stat().st_size for p in P.glob('VOLUME_*.txt')},indent=2));print('WITNESSES',len(extra),'ALL_DAY',len(day),'ALL_WEEK',len(week),'ALL_SCENARIO',len(base))
