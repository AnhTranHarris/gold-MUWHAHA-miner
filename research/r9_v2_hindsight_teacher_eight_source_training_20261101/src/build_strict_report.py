from pathlib import Path
import json,math
R=Path('/mnt/data/r9_v2_eight_source_training_20261101');M=('01','02','06','07');S=('coinexx','dukascopy')
REF={'01':27980,'02':33523,'06':31801,'07':24382}
a=['# R9 v2 — Source-exact ordered first-30-second hindsight teacher training','',
'**STRICT ENTRY-SURVIVABILITY RESULT: FAIL. No trained policy approved, no v2 execution changes promoted.**','',
'## First-event laboratory labels','',
'Post-entry actual real-tick quote sequence was replayed for all 2,481,012 previously executed baseline entries. At the earliest executable quote after entry, classify favorable event when exiting at bid (BUY) or ask (SELL) would produce net +$0.10 or better (including the existing $0.02 fee); classify an adverse event when executable liquidation quote moves at least $0.10 against the liquidation-side quote at entry (spread separately accounted for). Both prices are observed from actual source ticks, in original chronological event order even when timestamps are equal. An accepted teacher-positive example must encounter favorable event first AND the recorded R9-style close must realize positive net within <=30 seconds. If neither event occurs, mark neutral; all other cases, including late market-open timeout, are not success. This is a research-specific $0.10 adverse diagnostic, **not** the broker initial stop of $0.30 plus spread. The original R9 holding/exits remain unchanged.','',
'## Full source-month first-event label availability (no sampling)','',
'| Source | Month | Baseline entries | Strict favorable-first successful | Strict supply rate | 85% SYNTH floor |','|---|---|---:|---:|---:|---:|']
for s in S:
 for m in M:
  d=json.loads((R/'checkpoints'/f'{s}_{m}_ordered_barrier_receipt.json').read_text());floor=math.ceil(.85*REF[m])
  a.append(f"| {s} | {m} | {d['rows']:,} | {d['ordered_good']:,} | {100*d['ordered_good']/d['rows']:.2f}% | {floor:,} |")
a+=['','All eight sources have mathematically sufficient strict favorable-first winners for >=80% of their separate monthly trade-count floors. However, Dukascopy July has 20,552 strict good candidates versus a 20,725 minimum count; an oracle restricted to **100% good entries** would need 173 extra trades, although a permitted 80%-survival policy could include some non-successes. This is a hindsight supply ceiling, not causal predictability.','',
'## Chronological student with ordered first-event labels','',
'The exact same 89 causal runtime features and LightGBM/Hawkes-style quote-signature student were re-trained; model thresholds were calibrated only on dates before a separate check window in each source-month. SYNTH teacher marker was offline sample weight (+5% only for true real-tick positives), not runtime input. 9 historical NP false-class quantiles searched, and no calibration choice produced both >=80% strict favorable-first positive outcomes AND positive P&L. Chosen negative diagnostic thresholds are not approved and represent tiny filtered subsets only.','',
'| Source | Month | Diagnostic filtered count (check dates) | Strict first-event winrate | Diagnostic net | Check days clearing 80% |','|---|---|---:|---:|---:|---:|']
for s in S:
 for m in M:
  r=json.loads((R/'results'/f'{s}_{m}_ordered_firstpass_chronological.json').read_text())['evaluation']
  a.append(f"| {s} | {m} | {r['selected']:,} | {100*(r['win30_rate'] or 0):.2f}% | ${r['net']:,.2f} | {r['daily_pass_count']}/{r['daily_total']} |")
a+=['','## Final four-month retrospective source-specific fit: optimistic 85%-volume analysis','',
'Final students were trained on **all** January, February, June, July real outcomes. For each month an unrealizable ex-post threshold picked the model top scores equal to exactly 85% of R9 SYNTH. This is only a *training-set discriminability ceiling*, not deployable trade performance.','',
'| Source | Month | Trade quota | Strict good-first percentage, in-sample top scores | Modeled net | Days passing 80% | Weeks passing 80% |','|---|---|---:|---:|---:|---:|---:|']
for s in S:
 ds=json.loads((R/'results'/f'{s}_ordered_in_sample_full_volume_boundary.json').read_text())
 for m in M:
  q=ds[m]
  a.append(f"| {s} | {m} | {q['quota_trades']:,} | {100*q['30s_survival_rate']:.2f}% | ${q['net']:,.2f} | {q['days_passing_80']}/{q['total_days']} | {q['weeks_passing_80']}/{q['total_weeks']} |")
a+=['','## Scientific verdict and required build direction','',
'No model passes the 80% daily, 80% weekly, 80% monthly success plus 85% SYNTH volume and positive-profit mandate on both sources. Even ex-post in-sample top-score quota ranking cannot achieve 80%, strongly indicating the current candidate-direction selection and 89 features do not resolve enough event ordering at this trade frequency. Causal student time-fold predictions have weaker discrimination still. This experiment is recorded and rejected, not forgotten or mislabeled as acceptable.','',
'**Critical remaining issue:** A veto on the old, high-volume baseline-ledger entries is an off-policy candidate subset; skipped positions create opportunity for other live entries. Therefore all scored filtered subsets are diagnostic only until the frozen trained classifier is connected to the real-tick, single-position chronological streaming runner with consistent BUY/SELL/WAIT and the complete sources rerun. The next architecture experiment must learn opportunity timing and opposing direction jointly, not merely veto the preselected lane direction, and must include source-specific cost realism.','',
'Full unabridged source scripts, trade and feature research datasets, ten baseline fit models, ten ordered fit models, all per-source/month results, full synthetic teacher source and byte-exact parent source pins are preserved separately; original v2 and high-volume branches are not changed.']
out=R/'docs/ORDERED_FIRSTPASS_FINAL_ACCEPTANCE.md';out.write_text('\n'.join(a)+'\n');print(out,len(out.read_text()))
