"""January Atlas-first mechanism audit, no fitted model, no historical trade edits."""
import json, zipfile, gzip
from pathlib import Path
import numpy as np, pandas as pd
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118')
r='/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118/'
a='/mnt/data/AR1_JAN_R4_ADVANCED_FIB_HA_20261118/'
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f: d=pd.read_csv(f)
f=pd.read_csv(a+'JAN_ADVANCED_CAUSAL_HA_FIB_FEATURES_27980.csv.gz')
x=pd.read_pickle('/mnt/data/AR1_JAN_R3_LOSS_RESEARCH_20261118/JAN_CAUSAL_FEATURES_LOCAL_ONLY.pkl')
assert d.source_row.equals(f.source_row) and len(x)==len(d)==27980
p=pd.read_csv(r+'JAN_ATLAS_WITNESS_MATCHED_CONTROL_MAP.csv')
T=d.set_index('source_row'); F=f.set_index('source_row'); X=x.copy();X.index=d.source_row.values
features=['tf1_ha_signed_body_atr','tf5_ha_signed_body_atr','tf15_ha_signed_body_atr','tf1_ha_flip_rate_8','tf5_ha_flip_rate_8','tf5_ha_sign_entropy_8','tf1_ha_run_direction','tf5_ha_run_direction','tf15_ha_run_direction','tf1_ha_wick_asymmetry','tf5_ha_wick_asymmetry','tf1_fib_retracement_fraction','tf5_fib_retracement_fraction','tf15_fib_retracement_fraction','tf5_fib_swing_amplitude_atr','tf5_fib_nearest_level_distance_atr','tf5_fib_overshoot_extension','tf5_fib_failed_swing_reversal','ha_multiscale_phase_disagreement','fib_multiscale_swing_conflict','fib_618_cross_scale_confluence']
features+=['leg2_at_entry','sec_since_previous_exit','prior_realized_loss_indicator','prior_realized_net_to_gap','pre_move_side_10s','pre_move_side_60s','pre_flow_eff60','ln_60s_spread','ln_10s_quote_updates','asof_5m_gross_loss_to_book']
contrast=[]
for typ,g in p.groupby('source_target_type'):
 for feat in features:
  src=F if feat in F.columns else X
  v=src.reindex(g.target_row)[feat].to_numpy(float); w=src.reindex(g.control_row)[feat].to_numpy(float)
  diff=v-w; valid=np.isfinite(diff); n=valid.sum()
  if n<6:continue
  contrast.append({'witness_type':typ,'feature':feat,'n_pairs':int(n),'target_median':float(np.median(v[valid])),'matched_control_median':float(np.median(w[valid])),'median_paired_difference':float(np.median(diff[valid])),'target_higher_fraction':float(np.mean(diff[valid]>0))})
pd.DataFrame(contrast).to_csv(O/'ATLAS_MATCHED_TICK_NEIGHBORHOOD_HA_FIB_CONTRASTS.csv',index=False)
# Genuine loss prediction: first/second breakdown, previous-exit and HA+confirmed-swing zones.
dt=pd.DataFrame({'y':(d.net_cents<0).astype(int),'profitable':(d.net_cents>0).astype(int),'leg':d.leg,'prior_loss':x.prior_realized_loss_indicator,'net_usd':d.net_cents/100,'gap':d.frozen_s100_gap_cents/100,'date':d.entry_time_broker.str[:10]})
for tf in [1,5,15]:
 dt[f'ha{tf}']=np.select([f[f'tf{tf}_ha_run_direction']>0,f[f'tf{tf}_ha_run_direction']<0],['aligned','opposed'],default='neutral')
 dt[f'fib{tf}']=pd.cut(f[f'tf{tf}_fib_retracement_fraction'],[-100,0,.236,.382,.618,.786,1,100],labels=['extension','0-236','236-382','382-618','618-786','786-100','break'])
 dt[f'fib_age{tf}']=f[f'tf{tf}_fib_swing_age_bars']
 dt[f'ha_flip{tf}']=f[f'tf{tf}_ha_flip_rate_8']
for typ,cols in [('all_1st_leg',['leg','prior_loss','ha5','fib5']),('all_leg_phase',['leg','ha1','ha5','fib5'])]:
 agg=dt.groupby(cols,dropna=False,observed=True).agg(trades=('y','size'),losing=('y','sum'),profitable=('profitable','sum'),net_usd=('net_usd','sum')).reset_index();agg['loss_rate']=agg.losing/agg.trades
 agg.sort_values('loss_rate',ascending=False).to_csv(O/f'{typ}_HA_FIB_HISTORICAL_COHORTS.csv',index=False)
meta={'population':len(d),'r9_booked_sum_cents':int(d.net_cents.sum()),'negative_legs':int((d.net_cents<0).sum()),'profitable_legs':int((d.net_cents>0).sum()),'atlas_witness_pairs':len(p),'live_ineligible_labels':['family','cycle_net_cents','observed_MAE_cents','observed_peakDD_cents'],'interpretation':'descriptive historical mechanism discovery ONLY; no fitting/no filters'}
(O/'ATLAS_FIRST_MECHANISM_PROVENANCE.json').write_text(json.dumps(meta,indent=2))
print('AUDIT_COMPLETE',meta)
for typ in ['LOSS_CLUSTER_60MIN_PREENTRY','ORIGINAL_NEGATIVE_LEG_HIGHEST_COINEXX_DD','PROTECTED_POSITIVE_HIGH_GIVEBACK']:
 df=pd.DataFrame(contrast).query('witness_type == @typ').sort_values('target_higher_fraction',ascending=False)
 print(typ);print(df[['feature','target_median','matched_control_median','target_higher_fraction']].head(9).to_string(index=False))
