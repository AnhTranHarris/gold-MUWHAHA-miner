"""Render every R15 source-hour, 15-minute, friction and recovered witness row.
Never compress/round underlying source CSVs or rewrite source inputs.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
AUDIT=Path('/mnt/data/H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md')
REPORT=ROOT/'R15_COMPLETE_UNABRIDGED_HINDSIGHT_WATCH60_CROSSFEED_REPORT_20261103.md'
D={
 'R15_ALL_84_SOURCE_LANE_HORIZON_HOURS.csv':'1. All 84 source × lane × favorable-horizon hourly results (verbatim, full precision)',
 'R15_ALL_336_SOURCE_LANE_HORIZON_QUARTERS.csv':'2. All 336 quarter-hour frontier and quota result rows (verbatim)',
 'R15_ALL_189_ORIGINAL_STRICT_LATENCY_STRESS.csv':'3. All 189 original strict15/full30 delayed source scenario result rows (verbatim)',
 'R15_ALL_756_ORIGINAL_STRICT_LATENCY_QUARTERS.csv':'4. All 756 delayed actual-fill-quarter result rows (verbatim)'
}
intro=r'''# R15 COMPLETE, UNABRIDGED SOURCE-EXACT CROSSFEED HINDSIGHT ENTRY-ADMISSION RESEARCH

Date 2026-11-03 America/Chicago | Gold MUWHAHAHA Miner XAUUSD | Nondeployable research | R15 isolated add-only branch work.

**NOT AN ABBREVIATION.** All four entire result CSVs appear verbatim below. Every one of 37,038 alternative source quote-selected entry/exit ordinal rows remains in its separate untruncated original CSV; all 189 frozen lag/slippage per-trade NPZs and all three full candidate/BUY/SELL outcome NPZs are preserved in the executable recovery archive. Earlier 85KB complete forensic audit, R11 251KB append-only execution ledger, original R12/R13/R14 full reports/ZIPs and original GitHub branches remain authoritative immutable source. Existing R9 v2 EA is not modified.

## Research and tested contracts

### Original audit root bottleneck—not replaced

2026 Jan/Feb/Jun/Jul 2,880 original Dukascopy UTC hours, 1,917 R9 SYNTH-active hours, 246 proven infeasible under original strict-first15/full30 zero adverse and 30s one-position occupancy; 10 strict timestamp supply shortages, 236 safe-window temporal concentration shortages. The 2026-02-02 06:00 UTC raw Dukascopy spread median is original $3.157 and only six original strict-good first250ms timestamps versus 104 historical R9 SYNTH entries. This proves a frozen research-contract bound, NOT a universal limit on changed spread, firstTP exit or other brokers. Exact complete original document incorporated under Appendix A below for maximal non-loss source recovery.

### Previous verified additive dependency states

Original teacher `edce573d9c53b743dc5de1b0d741c81370af52c1`; R9 v2 repaired `ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0`; source-R13 `8d2e5524edd6f52f43503e30060285d909855925`; source-R14 (R15 parent) `743bc5768fd39e34a7d2ea8d1528318c50692f8e`. Full R14 experiment had 72 source-hour rows +288 quarters, source-evaluated all nine latency/friction scenarios: all-nine future-qualified $4.00 spread lane could pass retrospective 104/hour and 28/27/25/24 quarter counts, but real independent frozen-signal delay showed failures at 100ms. R14's 9/9 source future-known labels are NOT a valid as-of student. Original R13 stress 100ms/0-slept: Dukascopy widened 124 GOOD/54 FAIL, MT5 REAL tester 152/75, MT5 SYNTH tester1128/28. Preserve negative results and never equate MT5 REAL tester to live Coinexx fills.

### Three independently hash-pinned quote streams, one historically exposed hour

- R9_REAL_MT5_TESTER Feb2 (Strategy Tester real-tick): `24e4b31935ead7b0eb039fe84dc8972c59500b362cac21721739f1b0c050b3d7`.
- R9_SYNTH_MT5_TESTER Feb2 (Strategy Tester synthetic): `dcedb28f7453c80d2dec5ffe5d386dad1661134ba61765337155fbbaeb6213a2`.
- DUKASCOPY_RAW all Feb 2026: `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`.
- Exact original R11S1 full quote rolling-extrema helper SHA `c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475` unchanged; all three source SHA independently checked on input, and R13 original first15 baseline exact parity verified after R15.
- Source test focal hour 2026-02-02 06:00–07:00 UTC, quote input halo 05:54 UTC to 07:01:40 UTC; MT5 tester original event clock corrected -2h (server UTC time shift). Original R9 SYNTH source quarter references [28,27,25,24] and hour 104, not hourly count/4. This is not full four-month transfer or independent calendar OOS; July already historically exposed.

### Strict original acceptance and distinct expanded research class

Raw quoted price units are **integer $0.001**, NOT account-dollar profits and not the 0.01-lot broker cash value. BUY entry ASK, executable liquidation BID; SELL entry BID, executable cover ASK. Original research fee $0.02 of quoted price, target positive net +$0.10; therefore BUY future Bid>=entry Ask+$0.12, SELL future Ask<=entry Bid-$0.12. Correct original strict observation: first actual observed favorable post-entry quote by <=15s, no liquidation-side price adverse $0.10 or more anywhere through full 30s, full30 source quote coverage, gap<=15s, source day completion and 300s fresh eligible prefix after last >15s gap. Earlier same-millisecond quote ordinals never used as first TP in the original fill convention. A future favorable price **after 15 seconds** does not count toward the original accepted 15s strict class.

Separately new counterfactuals favorable at <=30s/full30 safe; <=45s/full45 safe; <=60s/full60 safe. A safer 60s FULL adverse monitor can eliminate many formerly valid first15/full30 actions; new favorable horizons are NOT simply additional original winners. Every selected trade’s original strict15/full30 status is independently retained, with altered-horizon original-strict fraction explicitly reported. All scheduling uses earliest future-known ACTUAL observed first target quote and one-position strict entry > previous exited quote. This is a **future-privileged hindsight interval schedule**; it has no prospective direction, no realized failed-stop exit, no MT5 live fill or account risk.

### Three independent 60s as-of watch mechanisms and non-interchangeable lanes

Existing R13 BASE first-observed quote per occupied 250ms max spread $1.50; R13 WIDE first observed 250ms OR first actually observed within-250ms spread compression >=$0.02, max current spread $4.00 **EXPERIMENTAL/UNAPPROVED**. New R15 creates watch state upon actually observed wide-spread first-250ms quote. This does NOT buy or sell and does not decide side. The watch expires at 60,000ms, clears on observed gap >15s, ignores same-ms future ordinals, and can confirm only on first subsequently OBSERVED quote at least 250ms later. Its current observed Bid/Ask and previously observed 15s/300s spread EMAs and 3s directional Bid/Ask moves are its only inputs.

`WATCH60_COOL_TO_1500`: seed current spread $2.00–$4.00; within 60s first actual observed quote with current spread <=$1.50 and <=70% seed spread. `WATCH60_COOL_TO_2500`: seed spread $2.80–$4.00; first actual quote <=$2.50 and <=80% seed spread, with observed 15s spread EMA <=300s EMA. `WATCH60_FLOW_RELIEF_4000`: seed $1.80–$4.00 and short EMA>=long EMA; observed quote must show spread relief <=80% seed while <=$4.00, 15s EMA<=300s EMA, coherent same-sign past3s Bid and Ask move each >=current spread+$0.12. No future price is used in these candidate admission decisions; the OFFLINE future-good side is still future-privileged.

Two union lanes are counterfactual: `UNION_BASE_AND_WATCH1500`, `UNION_ALL_WATCH_DIAGNOSTIC`. A widened >$1.50 price at actual ENTRY is NEVER silently treated as originally allowed; R13 WIDE and WATCH60<=2500 or FLOW<=4000 are research-only changed spread contracts. Every scenario pays actual spread in first-passage price geometry, and 0/100/500ms delayed true observed quote and 0/$0.02/$0.05 additional per-leg slippage only use the delayed actual bid/ask (no interpolated fill). Filled failure/censor reserves 30s; nonfilled rejects count as no trade; portfolio one-position busy drops queued signals. Quotas are held as observational acceptance, never used to force a negative expectancy entry.

### Internal scientific validity and broad negative controls

R15 code source and eight adversarial tests pass, including no retroactive entry-price, future mutation invariance of earlier watch signals, >15s observed quote gap resetting unconfirmed watcher, strict15/full30 versus strict60 incompatibility, 60s-only successes never relabeled as original15, BUY ASK/BID correct fee sign, original quarter references and high spread not receiving a fictitious cost discount. An initial source execution (F01) failed a reporting assertion because an SYNTH feed watch lane correctly produced ZERO eligible actions and the stress recording conditional skipped zero-action outcomes. This was corrected ONLY in new R15 source to emit all nine ZERO-trade scenarios per lane; original failure log preserved. No original EA or R13/R14 code changed. R15 independent verifier checked **ALL** original 37,038 selected quote ordinal entry/exit records against newly read original source Bid/Ask, 189 trace-scenario NPZ output codes against exact CSV, all 84/336 complete hour and quarter records, and all three SHA pins. R13 exact original strict15 control counts reproduce REAL705 / SYNTH1853 / DUKAS6; widened REAL765 / SYNTH1853 / DUKAS347. Empty buckets never become invented successes.

### Interpreting the research result; no fabricated solution

At 100ms delayed fill, no added slippage, the experimental Dukascopy WATCH60_COOL_TO_2500 yielded 18 strict GOOD and 4 completed failures (81.8181818% **conditional on completed**), but only 18 strict correct entries versus 104 original R9 SYNTH hour quota. Neither that tiny ratio nor its 27 future-selected entries establishes honest out-of-sample alpha or 15-minute quota viability. The <=$4 widened counterfactual yields many more eligible hindsight trades but fails 80% strict after delayed execution (Dukas124/54 and REAL tester152/75), exactly as R13 already found. The new strict safe FULL60 historical label schedules generally select LESS than the original strict15/SAFE30 schedules, so a "longer initial trade window" hypothesis must separate PRE-ENTRY WAIT confirmation from POST-ENTRY horizon length. 15-minute/1h/4h historical structure is an **open extension**, not an implemented proven predictor in R15: present R15 derives as-of 3s/15s/300s microstate and measures 15min/hour calendar quotas, but does not claim to compute multi-hour structure or broker fills.

Further falsifiers: stable spread-compression plateau for 250/500ms before entry rather than first quote after relief; infer competing favorable / adverse / timeout cause-specific intensities and opportunity-occupancy value vs WAIT using purged multi-day blocks, monitor conditional 60-second opportunity state without scheduling from future labels; full original 11,520 quarter frozen Dukas source tests across January,February,June,July; full Coinexx SYNTH and REAL source day comparisons when data for every intended UTC period and historical offset are available; symbol-level live fees, fill rejection, stop levels, actual dollar per lot P&L and margin; frozen causal BUY/SELL/WAIT student tested on truly new unexposed calendar. All remain UNRUN; no same-month student, demo/live authority, no MQL5 compile.

## Immutable prior scientific materials

Canonical entire original forensic audit https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit . Original append-only 251,650 character R11 ledger https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit . R12/R13/R14 append-only MT5_EXPAND ledger https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit . Original R14 complete source 36-member ZIP https://drive.google.com/file/d/1T7Rpy8eg_4bJL9fhYmU34yVYVNc5lAPG/view . Original all four month R12D-Q complete 161+17 member research/trade ZIPs in MT5_EXPAND folder https://drive.google.com/drive/folders/1vpHz_U-eVFyiC4Tf6YLgFlCK3HN3vP7L .

## Source-end scientific classification

R15 exposes **complete original observation-based source quote and after-fee entry price geometry** plus *future-privileged selected side and first-TP exit*. The quote path and original full30 adverse observation are recorded correctly, but the user cannot know a full 15/30/60 future quote outcome when sending a live trade. The ratio from this filtered hindsight schedule is tautologically high and is NOT a learned predictor. The delayed scenario retains that future-selected side/time and does not re-pick it after lag; the delayed ratio is meaningful as a counterfactual fragility diagnostic, but still remains retrospectively selected. No executable full account PnL is claimed because failed completed trades do not have economic stop/trail/timeout exits. No full-month/quarter opportunity count is claimed beyond the one verified focal hour.

'''
parts=[intro]
for fname,title in D.items():
 p=OUT/fname
 txt=p.read_text(encoding='utf8')
 with p.open(encoding='utf8',newline='') as f:
  n=sum(1 for _ in csv.DictReader(f))
 parts.append(f'\n## {title}\n\nRaw source member: `{fname}`; original byte count `{p.stat().st_size}`; SHA256 `{hashlib.sha256(p.read_bytes()).hexdigest()}`; exact source row count `{n}`. The following is raw original CSV text in full, including every field and row:\n\n```csv\n{txt.rstrip()}\n```\n')
parts.append('\n## 5. Entire exact observation, test, failure and source receipt\n\n```json\n'+(OUT/'R15_RECEIPT.json').read_text().rstrip()+'\n```\n')
parts.append('\n## 6. Entire independently audited quote ordinal verification\n\n```json\n'+(OUT/'R15_INDEPENDENT_QUOTE_ORDINAL_VERIFICATION.json').read_text().rstrip()+'\n```\n')
parts.append('\n## 7. Verbatim initial failed execution and corrected unit-test receipt\n\n```text\n'+(ROOT/'logs/R15_FAILURE_F01_ZERO_ELIGIBLE_WATCH_NOT_REPORTED.log').read_text().rstrip()+'\n```\n\n```text\n'+(ROOT/'logs/r15_pytest.log').read_text().rstrip()+'\n```\n')
parts.append('\n## 8. Full source quote ordinal trade/traces inventory\n\nEvery row of `R15_ALL_FUTURE_SELECTED_ORIGINAL_SOURCE_ORDINALS.csv` (37,038, alternative schedules, mutually nonadditive) is kept in the original bytes inside complete archive, because these 5,094,*** bytes are too large for prose duplication. All 189 original candidate-level delayed outcome trace NPZ and three complete candidate-label/source-prefix NPZ are included in the archive, with independent member hashes. The original raw quote gzip archives are SHA-pinned *dependencies* and are not duplicated or relabeled.\n')
parts.append('\n## Appendix A — ENTIRE ORIGINAL 2026-11-03 85KB SOURCE AUDIT UNABRIDGED\n\n'+AUDIT.read_text(encoding='utf8')+'\n')
REPORT.write_text(''.join(parts),encoding='utf8')
print(json.dumps({'path':str(REPORT),'bytes':REPORT.stat().st_size,'sha256':hashlib.sha256(REPORT.read_bytes()).hexdigest(),'full_tables':{k:sum(1 for _ in csv.DictReader((OUT/k).open())) for k in D}},indent=2))
