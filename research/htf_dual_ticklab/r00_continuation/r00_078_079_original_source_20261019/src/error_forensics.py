"""Non-promotional original-event diagnostic: attributable WRONG initial directions by broker,
source-provenance, regime and model disagreement. Does not use June/July to fit/select.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
ROOT=Path(__file__).resolve().parents[1]
REF=Path('/mnt/data/xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results')
rows=[];aggregate=[];families=['BASE','MICRO_DIRECT','STRUCTURE_DIRECT','COOP_DIRECT','ORACLE_CONSENSUS','ORACLE_GEOMEAN']
for b in ('coinexx','dukascopy'):
 for m in ('06','07'):
  with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz') as o,np.load(ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz') as s,np.load(ROOT/'features'/f'R00_078_{b}_{m}_ASOF.npz') as f:
   y=o['y'];base=o['BASE'];inc=o['AGREE_005'];new=s['FLIP_010'];x=f['feature'];ts=o['ts_ms'];assert np.array_equal(y,f['y'])
   h=(ts//3600000)%24
   sessions=np.select([(h>=0)&(h<6),(h>=6)&(h<12),(h>=12)&(h<18),(h>=18)&(h<24)],['UTC00-06','UTC06-12','UTC12-18','UTC18-24'],default='UNKNOWN')
   phase=np.select([x[:,44+17]==2,x[:,44+21]==2,((x[:,44+24:44+26]==2)|(x[:,44+28:44+30]==2)).any(axis=1),((x[:,44+33]==2)|(x[:,44+36]==2))],['IMPULSE_LIVE','EXHAUSTION_LIVE','PIVOT_RECLAIM','PULLBACK_LIVE'],default='NO_PUBLISHED_PHASE')
   model_sources=[base,s['MICRO_DIRECT'],s['STRUCTURE_DIRECT'],s['COOP_DIRECT'],s['ORACLE_CONSENSUS'],s['ORACLE_GEOMEAN']]
   pr=np.column_stack(model_sources)
   all_agree=np.all(pr==pr[:,0:1],axis=1)
   for level,keys in [('session',sessions),('episode',phase),('side',np.where(base>0,'BUY','SELL')),('model_agreement',np.where(all_agree,'ALL_6_AGREE','AT_LEAST_1_DISAGREES'))]:
    for key in np.unique(keys):
     sel=keys==key;n=int(sel.sum());actual=y[sel];bb=base[sel];ii=inc[sel];nn=new[sel]
     rows.append({'broker':b,'month':m,'dimension':level,'category':key,'events':n,'baseline_correct':int(np.sum(bb==actual)),'incumbent_correct':int(np.sum(ii==actual)),'new_correct':int(np.sum(nn==actual)),'opposite_labels':int(np.sum((actual==-bb)&(actual!=0))),'neutral_missing':int(np.sum(actual==0)),'baseline_accuracy':float(np.mean(bb==actual)),'incumbent_accuracy':float(np.mean(ii==actual))})
   aggregate.append({'broker':b,'month':m,'events':len(y),'base_correct':int(np.sum(base==y)),'inc_correct':int(np.sum(inc==y)),'opposite_wrong':int(np.sum((base==-y)&(y!=0))),'neutral_missing':int(np.sum(y==0)),'trading_signals_buy':int(np.sum(base==1)),'trading_signals_sell':int(np.sum(base==-1)),'all_oracles_agree_count':int(all_agree.sum()),'oracle_disagree_count':int((~all_agree).sum()),'all_agree_base_correct':int(np.sum(all_agree&(base==y))),'all_agree_base_wrong':int(np.sum(all_agree&(base!=y)))})
pd.DataFrame(rows).to_csv(ROOT/'results'/'R00_078_079_ERROR_ATTRIBUTION_BY_PHASE_SESSION_SIDE.csv',index=False)
a=pd.DataFrame(aggregate);a.to_csv(ROOT/'results'/'R00_078_079_ERROR_ATTRIBUTION_ORIGINAL_MONTH.csv',index=False)
s=a[['events','base_correct','inc_correct','opposite_wrong','neutral_missing','trading_signals_buy','trading_signals_sell','all_oracles_agree_count','oracle_disagree_count','all_agree_base_correct','all_agree_base_wrong']].sum()
print('TOTAL',s.to_dict());print('Session attribution selected samples:');d=pd.DataFrame(rows)
print(d[d.dimension=='session'].groupby('category')[['events','baseline_correct','incumbent_correct','opposite_labels','neutral_missing']].sum().to_string());print('Specialist');print(d[d.dimension=='episode'].groupby('category')[['events','baseline_correct','incumbent_correct']].sum().to_string())
