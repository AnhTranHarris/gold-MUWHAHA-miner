from pathlib import Path
import json
base=Path('/mnt/data/h1v2_r24s5')
p=base/'results/DUKASCOPY_RAW/07'
manifest=json.loads((base/'archives/R24S5_JULY_COMPLETE_LOSSLESS_ARCHIVE_MANIFEST_SHA256.json').read_text())
r=json.loads((p/'R24S5_DUKASCOPY_RAW_07_ALL60_FINAL_SOURCE_AND_CALENDAR_RECEIPT.json').read_text())
check=json.loads((base/'R24S5_JULY_60CASE_INDEPENDENT_FULL_SOURCE_VERIFICATION.json').read_text())
assert r['cases']==60 and check['checks']==1680 and check['failed']==0
month=p/'R24S5_DUKASCOPY_RAW_07_ALL_60_CASES_COMPLETE_MONTH_CASES.csv'
txt='''# R24S5 H1V2 JULY — COMPLETE SOURCE EXACT 60-POLICY IN-SAMPLE INITIAL SURVIVABILITY TRIAL, NEGATIVE RESULT, FULL SOURCE RECEIPTS

2026-11-04 America/Chicago. Original XAUUSD raw source DUKASCOPY July quote month SHA e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7. Eight prior source-month raw records and R9 EA remain immutable.

Every source point reported in the complete ZIPs: 7415841 actual Bid/Ask ticks, 1566284 past-only 1sec candidate observations under >15sec stale quote epoch and 300sec new-history, 1449925 +100ms actual first later observed fill quote ordinals. Independent original target-before-stop first passage per BUY/SELL and 15/30/60 second horizon (STOP/TARGET/TIMEOUT/CENSORED/UNFILLED). Features 47 original strictly as-of +17 enhanced prefix, current broker domain DUKASCOPY_RAW, 120000 selected fit indices * 6 sides/horizons, separate 10sec WAIT, all month deliberately IN-SAMPLE. All 48 independent 32768/remainder source/model SHA-bound blocks complete before 60 one-position policy replays. No future outcomes in entry predictor. Historical future-selected teacher remains separate and not a student precision score.

Original 2026 July broker-UTC R9 SYNTH 24324 entry count, 2976 quarter-hour slots (1870 reference-active), 744 UTC hourly slots (482 reference-active), 31 UTC source days. The complete 60-case data contains 178560 source quarter rows, 44640 hour rows, 1860 day rows and ALL original filled selection ordinals (both successful and stopped, timeout and censored), source actual fill/exit quote times, source SHA, model SHA, exact per-case independent verification. No unrecorded zero-reference quarter deleted. Data are split into FOUR 15-policy ZIPs, a consolidated full-calendar ZIP, a frozen model + source + audit ZIP and SHA-256 manifest. All have verified ZIP CRC locally. Exactly 60 original cases and 60 original case receipts; archive dates preserved.

The 60-case lexicographic research choice P0.12_STOP0.99_WAIT0.00_H0.00 selects 243497 filled quote positions, 42207 true future target-first, 200188 first adverse stops, 1095 timeouts, 7 quote-gap censored. Conditional completed target-first accuracy 0.1733418210193437. 1485/1870 active quarters meet R9 original quarter target if counting actual TARGET-first wins only; 391/482 hours. But source calendar JOINT condition target-first correct >=80% AND matching benchmark passes 4/1870 quarters, 0/482 hourly periods, 0 daily periods. This DOES NOT solve initial survivability. Volume is not sufficient. An exposed in-sample teacher is not an OOS policy.

Adversarial provenance: first monolithic original R24S4 inference reached partial 327680 July decision scores and timed out; INCOMPLETE partial never promoted. New S5 code scores and hashes all 48 blocks and then promotes a full finite normalized probability array. Four 15-case restartable replay chunks, all negative outcomes preserved. Independent full 1680-check source ordinal / position / calendar verifier PASSED 0 failure. However the verifier re-aggregates independently against frozen R24 true-label arrays rather than re-running each underlying raw bidask first-passage path; no claim beyond tested scope.

Calendar original IANA UTC research source status: nominal Tokyo, London, New York, Sydney clock signals available as earlier as-of features; point-in-time 2026 medium/high MT5 and ForexFactory economic-release archive with original vintage and independently verified historical UTC offsets NOT available, no recorded actual news impacts. Operational prop-like hours require configured owner/broker permissions; unknown is NEVER zero or a zero-trade claim. MT5 online CalendarValueHistory trade server time, Strategy Tester cannot directly call it. Original nontrading MT5 exporter source exists, but compiler/session-history/point-in-time archive not certified.

CURRENT SCIENTIFIC FALSIFICATION: 60 policies with all 15/30/60 first passage: 0 original active hours jointly qualified at 80% target-first on Dukascopy July. No equity/cash PNL claim; research entry survival only. Future research must distinguish two-broker varied spread, hazard calibration and local 15min, hour, daily mechanism, without using quotas as entry-side future information. Both June and July specialist source exactly certified, Jan/Feb earlier S4 certified separately; MT5-linked June/July new S4 family remains NOT COMPLETE.

## 60/60 unabridged original source-month case CSV (verbatim)
'''
txt+=month.read_text()
txt+='\n## Unabridged complete independent 1680-check original source evidence\n'+json.dumps(check,indent=2)+'\n'
txt+='\n## Original complete 60-case source, model and calendar receipt\n'+json.dumps(r,indent=2)+'\n'
txt+='\n## Complete model, selected trace, calendar archive member SHA-256 manifest\n'+json.dumps(manifest,indent=2)+'\n'
out=base/'R24S5_JULY_2026_COMPLETE_UNABRIDGED_SOURCE_EVIDENCE_AND_NEGATIVE_TRIALS.txt';out.write_text(txt);print(out,len(txt))
