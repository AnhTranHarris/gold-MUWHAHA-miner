"""Micro-HA/Fib witness contrast BEFORE choosing any model features."""
from pathlib import Path
import pandas as pd, numpy as np, gzip,zipfile,json
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
r=pd.read_csv('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118/JAN_ATLAS_WITNESS_MATCHED_CONTROL_MAP.csv')
m=pd.read_csv(O/'JAN_27980_STRICT_ENTRY_CAUSAL_MICRO_HA_FIB.csv').set_index('source_row')
for tf in [1,5,15,30]:
 for kind in ['fib_retrace','fib_dir_side','fib_amp_atr','fib_level_dist_atr','fib_pivot_age']:
  c=f'micro{tf}s_{kind}';m.loc[m[c]<-1e5,c]=np.nan
 # prohibit stale prior information becoming "current": 3 periods or 60s max
 stale=m[f'micro{tf}s_lastbar_age_s']>3*tf
 for c in m.filter(regex=f'^micro{tf}s_').columns:
  if c not in [f'micro{tf}s_lastbar_age_s',f'micro{tf}s_closed_bar_count']:
   m.loc[stale,c]=np.nan
candidates=[k for k in m if any(t in k for t in ['fib_retrace','fib_dir_side','ha_body_atr','ha_run','ha_flip7','fib_level_dist_atr','fib_amp_atr','ha_wick_side'])]
matched=[]
for grp,g in r.groupby('source_target_type'):
 for col in candidates:
  v=m.reindex(g.target_row)[col].to_numpy(float);w=m.reindex(g.control_row)[col].to_numpy(float)
  val=np.isfinite(v)&np.isfinite(w)
  if val.sum()<8:continue
  dif=v[val]-w[val]
  matched.append({'zone':grp,'feature':col,'pairs':int(val.sum()),'target_median':float(np.median(v[val])),'control_median':float(np.median(w[val])),'difference_median':float(np.median(dif)),'higher_fraction':float((dif>0).mean())})
D=pd.DataFrame(matched);D.to_csv(O/'ATLAS_MICRO_HA_FIB_TARGET_CONTROL_CONTRASTS.csv',index=False)
for typ in ['LOSS_CLUSTER_60MIN_PREENTRY','ORIGINAL_NEGATIVE_LEG_HIGHEST_COINEXX_DD','PROTECTED_POSITIVE_HIGH_GIVEBACK','PEAK_INTRAHOLD_DD']:
 q=D.query('zone==@typ').sort_values('higher_fraction',ascending=False)
 print(typ,'top discriminators among 20 historical paired examples')
 print(q[['feature','target_median','control_median','higher_fraction']].head(10).to_string(index=False))
 # 20 pairs per label is *hypothesis generation* only, not proof
meta={'n_atlas_witness_pairs':int(len(r)),'timeframes_seconds':[1,5,15,30],'stale_policy':'do not use HA/Fib state if last completed bar ended >3 bucket durations earlier','family_report_only':True,'use':'mechanism hypothesis selection; not deployed'}
(O/'ATLAS_MICRO_MECHANISM_DISCOVERY_RECEIPT.json').write_text(json.dumps(meta,indent=2))
