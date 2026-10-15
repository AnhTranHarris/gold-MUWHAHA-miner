"""Identical January parent signals: matched event decomposition and slot displacement.
Separates net-per-matched-event from new/blocked opportunities. No forward labels.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
from r9_teacher_informed_dukas_executor import features
from jan_atr_regime_harvest_finite_grid_v1 import replay
D=Path(__file__).resolve().parent
p=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz');z=np.load(D/'jan_parent_causal_squeeze_signals.npz')
f=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=f.timestamp_ms_utc.to_numpy();bid=f.bid_raw.to_numpy();ask=f.ask_raw.to_numpy();del f
sec,first,hi,lo,cl,fts=features(ms,bid);assert np.array_equal(sec,z['sec']);atr=fts[300][1];dummy=np.zeros(len(sec),np.int8)
ctl=np.array([(7.,20.,5.,2.5,1500.),(7.,20.,5.,2.5,1500.)]);best=np.array([(7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,2700.)]);cols=['signal_ms','entry_ms','exit_ms','side','entry_quote','exit_quote','net','exit_reason','best_fav_gross','asof_m5_atr','stop','target','trail_arm','trail_gap']
base,st0=replay(ms,bid,ask,sec,z['signal'],atr,dummy,dummy,100.,ctl,0)
new,st1=replay(ms,bid,ask,sec,z['signal'],atr,dummy,dummy,100.,best,1)
A=pd.DataFrame(base,columns=cols);B=pd.DataFrame(new,columns=cols)
A.to_csv(D/'JAN_RUNNER_IDENTICAL_SOURCE_BASELINE_100_LEDGER.csv',index=False)
base_key=set(A.signal_ms.astype('int64')); new_key=set(B.signal_ms.astype('int64')); both=base_key&new_key
ap=A[A.signal_ms.astype('int64').isin(both)].set_index('signal_ms');bp=B[B.signal_ms.astype('int64').isin(both)].set_index('signal_ms');paired=ap[['net','exit_ms','asof_m5_atr']].join(bp[['net','exit_ms']],lsuffix='_control',rsuffix='_new');paired['net_uplift']=paired.net_new-paired.net_control
paired.to_csv(D/'JAN_RUNNER_SOURCE_MATCHED_TRADE_ATTRIBUTION.csv')
res={'baseline_net':round(float(st0[0]),6),'new_net':round(float(st1[0]),6),'incremental_net':round(float(st1[0]-st0[0]),6),'baseline_trades':len(A),'new_trades':len(B),'source_events_matched':len(both),'matched_control_net':round(float(ap.net.sum()),6),'matched_new_net':round(float(bp.net.sum()),6),'matched_uplift':round(float(paired.net_uplift.sum()),6),'baseline_only_events':len(base_key-both),'baseline_only_net':round(float(A[~A.signal_ms.astype('int64').isin(both)].net.sum()),6),'new_only_events':len(new_key-both),'new_only_net':round(float(B[~B.signal_ms.astype('int64').isin(both)].net.sum()),6),'matched_high_atr_events':int((paired.asof_m5_atr>=7.77).sum()),'matched_high_atr_uplift':round(float(paired.loc[paired.asof_m5_atr>=7.77,'net_uplift'].sum()),6),'matched_not_high_atr_uplift':round(float(paired.loc[paired.asof_m5_atr<7.77,'net_uplift'].sum()),6),'exits_control':A.exit_reason.value_counts().to_dict(),'exits_new':B.exit_reason.value_counts().to_dict()}
(D/'JAN_RUNNER_MECHANISM_ABLATION.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
print(json.dumps(res,indent=2),flush=True)
