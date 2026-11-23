"""Narrow R03 teacher-to-REAL as-of W1/W2 witness, no source data copied."""
import os
from pathlib import Path
import numpy as np,pandas as pd,json
R=Path(os.environ.get('R9_R03_FOLDER','/mnt/data/r9_jan_r03'));O=Path(__file__).parent
t=pd.read_csv(R/'r03_teacher_5sec.csv')
t['ent_second']=t.teacher_entry_ms//1000;t['ext_second']=t.teacher_exit_ms//1000
valid=t.order_respecting.eq(1)
secs=set(t.loc[valid,'ent_second']).union(t.loc[valid,'ext_second'])
need=['sec','ms','bid_c','ask_c','phase','spread_c','gap_ms','minute_disp','minute_range','minute_ticks','ret5','ret10','ret20','ret60','eff10','eff30','range10','quotes10','quotes60','m5_atr','m15_atr','h1_atr','m5_position','m15_position','h1_position']
pieces=[]
for ch in pd.read_csv(R/'r03_phase_seconds.csv.gz',usecols=need,chunksize=100000):
 s=ch[ch.sec.isin(secs)]
 if len(s): pieces.append(s)
features=pd.concat(pieces).set_index('sec')
a=t.join(features,on='ent_second',rsuffix='_ent')
a=a.join(features,on='ext_second',rsuffix='_ext')
# after first join, .ms/.bid_c/.ask_c entry first; second join postfix _ext.
side=a.side.to_numpy()
px0=np.where(side==1,a.ask_c.to_numpy(),a.bid_c.to_numpy())
px1=np.where(side==1,a.bid_c_ext.to_numpy(),a.ask_c_ext.to_numpy())
first_net=(px1-px0)*side
ok=(valid & a.ms.notna() & a.ms_ext.notna() & (a.ms<a.ms_ext))
a['first_net_c']=np.where(ok,first_net,np.nan)
a['oracle_net_after_original_fee_c']=np.where(valid,a.teacher_best_net_c-2,np.nan)
a['first_net_after_original_fee_c']=np.where(ok,first_net-2,np.nan)
a['cohort']=np.select([
 valid &(a.teacher_best_net_c>2)&ok&(first_net<=2),
 valid &(a.teacher_best_net_c>2)&ok&(first_net>2),
 valid &(a.teacher_best_net_c<=2),
 ~valid],['oracle_positive_first_negative','oracle_positive_first_positive','oracle_nonpositive','missing_ordered_pair'],default='unclassified')
fields=['row','leg','side','entry_ref_sec','exit_ref_sec','original_booked_net_usd','source_entry_quotes','source_exit_quotes','cohort','teacher_best_net_c','oracle_net_after_original_fee_c','first_net_c','first_net_after_original_fee_c','spread_c','spread_c_ext','quotes10','quotes10_ext','gap_ms','gap_ms_ext','eff10','ret5','ret10','ret20','m5_atr','m15_atr','h1_atr','minute_disp','minute_range','minute_ticks','teacher_entry_ms','teacher_exit_ms','ms','ms_ext']
a[fields].to_csv(O/'r04_atlas_targeted_witness.csv.gz',index=False,compression={'method':'gzip','compresslevel':4})
cohorts=a.groupby('cohort',dropna=False).agg(count=('row','size'),synth_winners=('original_booked_net_usd',lambda x:int((x>0).sum())),mean_oracle_fee_c=('oracle_net_after_original_fee_c','mean'),median_spread_entry_c=('spread_c','median'),median_spread_exit_c=('spread_c_ext','median'),median_quotes10=('quotes10','median'),median_eff10=('eff10','median'),median_ret5=('ret5','median'),median_atr5=('m5_atr','median'))
summary={'original_covered':int(valid.sum()),'original_fee_cents_at_001lot':2,'cohorts':cohorts.round(5).reset_index().to_dict(orient='records'),'positive_teacher_net_fee2':int((a.oracle_net_after_original_fee_c>0).sum()),'positive_first_quote_net_fee2':int((a.first_net_after_original_fee_c>0).sum()),'protected_original_winners':int((a.original_booked_net_usd>0).sum()),'protected_two_leg_recovered_cycle_controls':2147,'excluded_other_months':True,'note':'Retrospective oracle selection is a noncausal upper bound, even when the fee matches original tester 0.01 lot. No teacher quote ordinal enters execution.'}
(O/'r04_atlas_receipt.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
