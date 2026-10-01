#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, numpy as np, pandas as pd

ROOT=Path('/mnt/data')
OUT=ROOT/'beta066'
PROP=ROOT/'beta065_stage1'/'BETA_065_PREOWNERSHIP_CANDIDATES.npz'
PRED65=ROOT/'beta065_stage1'/'BETA_065_ACTION_VALUE_PREDICTIONS.npz'
SRC=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
RESULT=OUT/'BETA_066_RESULTS.json'
EXPECT_SRC='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
EXPECT_PROP='600e3b73d7d053f6ed0785a5dd68aadad72f1e8928054a61b3eb1b2840be8773'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()

def ck(name,cond,detail=None):
 checks[name]={'pass':bool(cond),'detail':detail}

checks={}
r=json.loads(RESULT.read_text())
p=np.load(PROP,allow_pickle=True); y65=np.load(PRED65,allow_pickle=True); z=np.load(OUT/'BETA_066_DELAYED_ACTION_LABELS.npz',allow_pickle=True); pr=np.load(OUT/'BETA_066_DELAYED_ACTION_PREDICTIONS.npz',allow_pickle=True)
ck('unit_id',r['unit_id']=='BETA_066_NONLINEAR_DELAYED_ACTION_WAIT_SHORT_30S',r['unit_id'])
ck('source_sha',sha(SRC)==EXPECT_SRC,sha(SRC));ck('proposal_sha',sha(PROP)==EXPECT_PROP,sha(PROP))
ck('proposal_rows',len(p['event_time_ms'])==371013,len(p['event_time_ms']))
ck('event_identity_labels',np.array_equal(p['event_time_ms'],z['event_time_ms']) and np.array_equal(p['source_ordinal'],z['source_ordinal']))
ck('event_identity_predictions',np.array_equal(p['event_time_ms'],pr['event_time_ms']) and np.array_equal(p['source_ordinal'],pr['source_ordinal']))
ck('action_shape',z['labels'].shape==(371013,8),z['labels'].shape)
ck('delays',np.array_equal(z['delays_ms'],np.array([0,250,1000,3000])),z['delays_ms'].tolist())
tt=[];aa=[];bb=[]
end_need=int(p['event_time_ms'].max()+3000+30000+5000)
for df in pd.read_csv(SRC,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'},chunksize=750000):
 t0=df.timestamp_ms_utc.to_numpy(np.int64,copy=False)
 if len(t0)==0:continue
 if t0[0]>end_need:break
 mm=t0<=end_need
 if not mm.any():continue
 tt.append(t0[mm].copy());aa.append(df.ask_raw.to_numpy(np.int64,copy=False)[mm].copy());bb.append(df.bid_raw.to_numpy(np.int64,copy=False)[mm].copy())
 if int(t0[mm][-1])>=end_need:break
t=np.concatenate(tt);a=np.concatenate(aa);b=np.concatenate(bb)
expected_ord=np.searchsorted(t,p['event_time_ms'],side='left').astype(np.int64)
ck('beta065_source_ordinal_searchsorted_identity',np.array_equal(p['source_ordinal'],expected_ord),int(np.max(np.abs(p['source_ordinal']-expected_ord))))
sample=np.linspace(0,len(p['event_time_ms'])-1,1000,dtype=np.int64)
ei0=z['entry_idx'][sample,0].astype(np.int64);xi0=z['exit_idx'][sample,0].astype(np.int64);ok=(ei0>=0)&(xi0>=0)
long_expected=(b[xi0[ok]].astype(float)-a[ei0[ok]].astype(float))*.001-0.02
short_expected=(b[ei0[ok]].astype(float)-a[xi0[ok]].astype(float))*.001-0.02
ck('now_label_direct_quote_fixture',np.allclose(z['labels'][sample[ok],0],long_expected,atol=1e-5) and np.allclose(z['labels'][sample[ok],1],short_expected,atol=1e-5),{'rows':int(ok.sum())})
ck('now_exit_is_entry_plus_30s_first_tick',bool(np.all(t[xi0[ok]]>=t[ei0[ok]]+30000) and np.all((xi0[ok]==0)|(t[xi0[ok]-1]<t[ei0[ok]]+30000))),{'rows':int(ok.sum())})
ei=z['entry_idx'];xi=z['exit_idx']
ck('entry_delay_monotone',bool(np.all(ei[:,0]<=ei[:,2]) and np.all(ei[:,2]<=ei[:,4]) and np.all(ei[:,4]<=ei[:,6])))
valid=ei>=0
ck('exit_after_entry',bool(np.all(xi[valid]>ei[valid])))
ck('diagnostic_not_used_for_selection',r['diagnostic_used_for_selection'] is False,r['diagnostic_used_for_selection'])
ck('status_null_demote',r['status']=='NO_GUARDED_CAL_CANDIDATE__DEMOTE_CLOCK_SURFACE',r['status'])
ck('all_grid_fail',not any(x['guard_pass'] for x in r['model_grid']),sum(x['guard_pass'] for x in r['model_grid']))
active=[x for x in r['model_grid'] if x['trades']>0]
ck('all_active_cal_nonpositive',all(x['net']<=0 for x in active),max([x['net'] for x in active],default=None))
ck('cal_oracle_delay_increment_positive',r['oracle_capacity']['CAL']['delay_increment_mean']>0,r['oracle_capacity']['CAL']['delay_increment_mean'])
ck('cal_oracle_all_positive',r['oracle_capacity']['CAL']['oracle_all_mean']>0,r['oracle_capacity']['CAL']['oracle_all_mean'])
ck('selected_skip_all',r['selected'].get('selection')=='SKIP_ALL',r['selected'])
ck('selected_ledgers_zero',all(v['trades']==0 for v in r['selected_replay'].values()),r['selected_replay'])
ck('august_sealed',r['august']=='SEALED_NOT_READ',r['august'])
for mn in ['HGB_D3_L2_5','HGB_D4_L2_10','EXTRA_D8_L150']:
 arr=pr[f'pred_{mn}'];ck(f'pred_shape_{mn}',arr.shape==(371013,8),arr.shape);ck(f'pred_finite_{mn}',np.isfinite(arr).all())
for fn in ['BETA_066_DELAYED_ACTION_LABELS.npz','BETA_066_DELAYED_ACTION_PREDICTIONS.npz','BETA_066_SELECTED_LEDGER_FIT.csv.gz','BETA_066_SELECTED_LEDGER_CAL.csv.gz','BETA_066_SELECTED_LEDGER_DIAGNOSTIC.csv.gz']:
 ck('hash_'+fn,Path(OUT/fn).exists(),sha(OUT/fn) if (OUT/fn).exists() else None)
passed=sum(v['pass'] for v in checks.values());res={'unit_id':r['unit_id'],'qa_status':'PASS' if passed==len(checks) else 'FAIL','pass_count':passed,'check_count':len(checks),'checks':checks}
(OUT/'BETA_066_QA.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(json.dumps({'qa_status':res['qa_status'],'pass_count':passed,'check_count':len(checks),'failed':[k for k,v in checks.items() if not v['pass']]},indent=2))
if passed!=len(checks):raise SystemExit(1)
