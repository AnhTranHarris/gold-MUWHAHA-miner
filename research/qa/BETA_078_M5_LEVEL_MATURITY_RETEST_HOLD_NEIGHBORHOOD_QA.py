#!/usr/bin/env python3
from pathlib import Path
import json, math, hashlib
import numpy as np, pandas as pd

ROOT=Path('/mnt/data'); OUT=ROOT/'beta078'; B76=ROOT/'beta076'
FILES={
'2026-01':'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','2026-02':'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','2026-03':'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','2026-04':'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','2026-05':'XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','2026-06':'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','2026-07':'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}
MONTHS=list(FILES); H=1800; FEE=.02

def load(path,head=False):
 ts=[];aa=[];bb=[]
 for df in pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=1_000_000,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'}):
  ts.append(df.timestamp_ms_utc.to_numpy(np.int64));aa.append(df.ask_raw.to_numpy(np.int32));bb.append(df.bid_raw.to_numpy(np.int32))
  if head:break
 return np.concatenate(ts),np.concatenate(aa).astype(float)*.001,np.concatenate(bb).astype(float)*.001

def calc_stats(d):
 v=d.selected_pnl.to_numpy(float);gp=float(v[v>0].sum());gl=float(v[v<=0].sum());eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[1:]
 return {'trades':len(v),'wins':int((v>0).sum()),'win_rate':float((v>0).mean()),'net':float(v.sum()),'gp':gp,'gl':gl,'pf':gp/abs(gl),'avg':float(v.mean()),'max_dd':float((pk-eq).max())}

res=json.loads((OUT/'BETA_078_RESULTS.json').read_text()); led=pd.read_csv(OUT/'BETA_078_SELECTED_LEDGER.csv.gz')
checks=[]
def ck(name,cond,detail=''):
 checks.append({'name':name,'pass':bool(cond),'detail':detail})
 if not cond: print('FAIL',name,detail)

ck('selected_policy_identity',res['selected']['age_lo']==7 and res['selected']['age_hi']==9 and res['selected']['hold_s']==1800)
ck('trade_count_420',len(led)==420,str(len(led)))
ck('qa_ids_sequential',np.array_equal(led.qa_trade_id.to_numpy(),np.arange(1,len(led)+1)))
ck('all_M5',set(led.level_tf)=={'M5'})
ck('maturity_7_9',bool(led.level_age_m5_bars.between(7,9).all()))
ck('valid_retest_age',bool(led.retest_age_m1_bars.between(1,10).all()))
ck('valid_tolerance',set(np.round(led.retest_tolerance_atr,2)).issubset({.1,.2,.3}))
ck('strict_entry_after_event',bool((led.entry_ms>led.event_ms).all()))
ck('selected_pnl_identity',np.allclose(led.selected_pnl,led.pnl_1800s,atol=1e-12))
ck('selected_hold_not_early',bool((led.exit_ms_1800s>=led.entry_ms+H*1000).all()))
ck('no_position_overlap',bool(np.all(led.entry_ms.to_numpy()[1:]>=led.exit_ms_1800s.to_numpy()[:-1])))
ck('months_only_jan_jul',set(led.entry_month).issubset(set(MONTHS)) and not led.entry_month.str.contains('2026-08').any())
# Quote/PnL arithmetic.
s=led.side.to_numpy(np.int8);exp=np.where(s==1,led.exit_bid_1800s-led.entry_ask,led.entry_bid-led.exit_ask_1800s)-FEE
ck('quote_side_pnl_exact',np.allclose(exp,led.selected_pnl,atol=1e-9),str(float(np.max(np.abs(exp-led.selected_pnl)))))
# Result reconciliation.
st=calc_stats(led)
for k in ['trades','wins','net','gp','gl','pf','avg','max_dd']:
 rv=res['aggregate'][k];sv=st[k];ck('aggregate_'+k,abs(float(rv)-float(sv))<1e-8,f'{rv} vs {sv}')
for m in MONTHS:
 sm=calc_stats(led[led.entry_month==m]);rm=res['monthly'][m]
 for k in ['trades','net','pf','avg']:
  ck(f'month_{m}_{k}',abs(float(sm[k])-float(rm[k]))<1e-8,f'{rm[k]} vs {sm[k]}')
# Full raw source timestamp parity for all selected trades.
for i,m in enumerate(MONTHS):
 sub=led[led.entry_month==m]
 if sub.empty:continue
 t,a,b=load(ROOT/FILES[m])
 if i+1<len(MONTHS):
  tn,an,bn=load(ROOT/FILES[MONTHS[i+1]],head=True);t=np.r_[t,tn];a=np.r_[a,an];b=np.r_[b,bn]
 e=np.searchsorted(t,sub.event_ms.to_numpy(np.int64),side='right');x=np.searchsorted(t,sub.entry_ms.to_numpy(np.int64)+H*1000,side='left')
 ck(f'{m}_entry_first_later_tick',np.array_equal(t[e],sub.entry_ms.to_numpy(np.int64)))
 ck(f'{m}_exit_first_at_after_1800s',np.array_equal(t[x],sub.exit_ms_1800s.to_numpy(np.int64)))
 ck(f'{m}_entry_quotes_source',np.allclose(a[e],sub.entry_ask) and np.allclose(b[e],sub.entry_bid))
 ck(f'{m}_exit_quotes_source',np.allclose(a[x],sub.exit_ask_1800s) and np.allclose(b[x],sub.exit_bid_1800s))
 print('RAW QA',m,len(sub),flush=True)
# Neighbor table confirms required neighborhood.
tab=pd.read_csv(OUT/'BETA_078_NEIGHBORHOOD_TABLE.csv')
def cell(w,h):return tab[(tab.window==w)&(tab.hold_s==h)].iloc[0]
for w,h in [('AGE_7_9',1200),('AGE_7_10',1800),('AGE_8_9',1800)]:
 z=cell(w,h);ck(f'neighbor_{w}_{h}',int(z.trades)>=150 and z.net>0 and z.pf>1)
# Human QA cases: admitted winners/losers across months, maturity rejects, ownership rejects.
cases=[]
for m in MONTHS:
 d=led[led.entry_month==m]
 if len(d):
  for _,r in pd.concat([d.nlargest(2,'selected_pnl'),d.nsmallest(2,'selected_pnl')]).drop_duplicates('qa_trade_id').iterrows():
   cases.append({'case_type':'ADMITTED','expected_decision':'ENTER','reason':'M5_FIRST_RETEST_LEVEL_AGE_7_9_AND_FLAT','month':m,'event_ms':int(r.event_ms),'entry_ms':int(r.entry_ms),'side':int(r.side),'level_price':r.level_price,'level_age_m5_bars':int(r.level_age_m5_bars),'retest_age_m1_bars':int(r.retest_age_m1_bars),'entry_spread':r.entry_spread,'expected_exit_ms':int(r.exit_ms_1800s),'expected_pnl':r.selected_pnl})
# Maturity rejects sampled from all BETA076 executable events.
allb=pd.concat([pd.read_csv(B76/f'BETA_076_EXEC_{m}.csv.gz') for m in MONTHS],ignore_index=True).sort_values('entry_ms')
rej=allb[allb.level_age_m5_bars.isin([6,10])].groupby(['entry_month','level_age_m5_bars'],as_index=False).head(1)
for _,r in rej.head(14).iterrows():
 cases.append({'case_type':'REJECT_MATURITY','expected_decision':'SKIP','reason':'M5_LEVEL_AGE_OUTSIDE_7_9','month':r.entry_month,'event_ms':int(r.event_ms),'entry_ms':int(r.entry_ms),'side':int(r.side),'level_price':r.level_price,'level_age_m5_bars':int(r.level_age_m5_bars),'retest_age_m1_bars':int(r.retest_age_m1_bars),'entry_spread':r.entry_spread,'expected_exit_ms':'','expected_pnl':''})
# Ownership rejects: eligible age7-9 events not selected because prior accepted trade still active.
elig=allb[allb.level_age_m5_bars.between(7,9)].sort_values('entry_ms').reset_index(drop=True)
selected_keys=set(zip(led.event_ms.astype(int),led.side.astype(int),np.round(led.level_price,4)))
free=-1;ownership=[]
for _,r in elig.iterrows():
 key=(int(r.event_ms),int(r.side),round(float(r.level_price),4))
 if r.entry_ms<free:
  if key not in selected_keys: ownership.append(r)
 else:
  free=int(r.entry_ms+H*1000) # source exit is >= target; conservative identification for examples
for r in ownership[:14]:
 cases.append({'case_type':'REJECT_OWNERSHIP','expected_decision':'BLOCK','reason':'POSITION_ALREADY_OPEN','month':r.entry_month,'event_ms':int(r.event_ms),'entry_ms':int(r.entry_ms),'side':int(r.side),'level_price':r.level_price,'level_age_m5_bars':int(r.level_age_m5_bars),'retest_age_m1_bars':int(r.retest_age_m1_bars),'entry_spread':r.entry_spread,'expected_exit_ms':'','expected_pnl':''})
pd.DataFrame(cases).to_csv(OUT/'BETA_078_HUMAN_QA_CASES.csv',index=False)
passed=sum(c['pass'] for c in checks);qa={'unit_id':'BETA_078_HUMAN_QA_ENGINEERING_QA','assertions':len(checks),'passed':passed,'failed':len(checks)-passed,'all_pass':passed==len(checks),'checks':checks,'human_qa_cases':len(cases),'august':'SEALED_NOT_READ'}
(OUT/'BETA_078_QA.json').write_text(json.dumps(qa,indent=2,sort_keys=True)+'\n')
checklist=f'''# BETA078 Human QA Checklist

Engineering QA: **{passed}/{len(checks)} assertions PASS**  
Candidate: **M5 FIRST_RETEST / level age 7–9 M5 bars / 1800-second hold**  
August: **SEALED**  
MQL5: **NOT AUTHORIZED**

## Manual review workflow

1. Open `BETA_078_HUMAN_QA_CASES.csv` and choose cases from each type: ADMITTED, REJECT_MATURITY, and REJECT_OWNERSHIP.
2. For an ADMITTED case, verify the level is a confirmed M5 pivot, the breakout precedes the retest, the retest event is RIGHT-edge observable, and entry occurs on the first later quote.
3. Confirm maturity admission is inclusive only for ages 7, 8, or 9 completed M5 bars.
4. Confirm a second eligible setup is blocked while the prior 1800-second position is still open.
5. Recalculate BUY P&L as `exit_bid - entry_ask - 0.02`; SELL as `entry_bid - exit_ask - 0.02`.
6. Verify the recorded exit is the first source quote at or after 1800 seconds from actual entry.
7. Review both largest winners and largest losers from every month; do not assess only favorable examples.
8. Reconcile monthly totals against `BETA_078_RESULTS.json` and the full selected ledger.

## Research interpretation boundary

This is a **human-QA research candidate**, not independently validated alpha. The maturity window was discovered on Jan–Jul, which are historically inspected. Human QA evaluates causality, implementation, accounting, state transitions, explainability, and reproducibility. It does not convert these Jan–Jul economics into out-of-sample evidence. August remains sealed for the blind gate after QA.
'''
(OUT/'BETA_078_HUMAN_QA_CHECKLIST.md').write_text(checklist)
print(json.dumps({k:qa[k] for k in ['assertions','passed','failed','all_pass','human_qa_cases','august']},indent=2))
