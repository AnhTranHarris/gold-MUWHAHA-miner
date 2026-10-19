"""R00-078B same-original-event cooperative frozen R00-077 + R00-078A fusion.
No new source reads; all predictions generated earlier from original registered tapes.
Evidence preserved; no trained weights or any look-ahead at inference.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REF=Path('/mnt/data/xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results')
POLICIES=['INCUMBENT_077','R00_078_FROZEN','INTERSECTION','UNION','077_VETO_STRUCT','077_PLUS_STRUCT','077_PLUS_078_EPISODE','077_PLUS_078_IF_STRONG','078_PRIO_STRONG','077_PLUS_COMPOSITE_AGREE','077_PLUS_078_IF_NEW_NOT_DAMAGE']

def score(b,m):
 with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz',allow_pickle=False) as old, np.load(ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz',allow_pickle=False) as new:
  ts=old['ts_ms'];ix=old['quote_index'];y=old['y'];base=old['BASE'];inc=old['AGREE_005'];alt=new['FLIP_010'];adv=new['advantage'];se=new['struct_edge'];he=new['specialist_edge'];episode=new['FLIP_EPISODE_010']
  assert np.array_equal(ts,new['ts_ms']) and np.array_equal(ix,new['quote_index']) and np.array_equal(y,new['y']) and np.array_equal(base,new['BASE'])
  a=inc!=base;bb=alt!=base;ss=new['FLIP_STRUCT_010']!=base;ee=episode!=base
  strategies={
   'INCUMBENT_077':inc,'R00_078_FROZEN':alt,
   'INTERSECTION':np.where(a&bb,-base,base),
   'UNION':np.where(a|bb,-base,base),
   '077_VETO_STRUCT':np.where(a&(se>0),-base,base),
   '077_PLUS_STRUCT':np.where(a|ss,-base,base),
   '077_PLUS_078_EPISODE':np.where(a|ee,-base,base),
   '077_PLUS_078_IF_STRONG':np.where(a|((adv>.16)&(se>.04)),-base,base),
   '078_PRIO_STRONG':np.where(adv>.13,-base,inc),
   '077_PLUS_COMPOSITE_AGREE':np.where(a|(bb&(se>.02)&(he>.02)),-base,base),
   '077_PLUS_078_IF_NEW_NOT_DAMAGE':np.where(a|(bb&(se>0)), -base,base),
  }
  assert list(strategies)==POLICIES
  rows=[]
  for name,p in strategies.items():
   p=p.astype('int8');changed=p!=base
   resc=int(np.count_nonzero(changed&(p==y)));dmg=int(np.count_nonzero(changed&(base==y)))
   rows.append({'broker':b,'month':m,'policy':name,'events':len(y),'correct':int(np.count_nonzero(p==y)),'accuracy':float(np.mean(p==y)),'flips':int(changed.sum()),'rescued':resc,'damaged':dmg,'net':resc-dmg,'buy':int(np.count_nonzero(p==1)),'sell':int(np.count_nonzero(p==-1))})
  pd.DataFrame(rows).to_csv(ROOT/'results'/f'R00_078B_{b}_{m}_POLICIES.csv',index=False)
  np.savez_compressed(ROOT/'results'/f'R00_078B_{b}_{m}_EVENTS.npz',ts_ms=ts,quote_index=ix,y=y,base=base,**{k:v.astype('int8') for k,v in strategies.items()})
  print('SCORE',b,m,'incumbent',rows[0]['correct'],'new_phase_fusion',max(rows,key=lambda a:a['correct'])['policy'],flush=True)

def freeze():
 a=pd.concat([pd.read_csv(ROOT/'results'/f'R00_078B_{b}_02_POLICIES.csv') for b in ('coinexx','dukascopy')])
 x=a.groupby('policy')[['events','correct','flips']].sum()
 winner=min(POLICIES,key=lambda k:(-int(x.loc[k,'correct']),0 if k=='INCUMBENT_077' else 1,int(x.loc[k,'flips']),POLICIES.index(k)))
 obj={'FEB_frozen_winner':winner,'FEB_scores':x.to_dict('index'),'plan_sha':hashlib.sha256((ROOT/'R00_078B_PREDECLARED_FUSION_PLAN.json').read_bytes()).hexdigest(),'no_transfer_reselection':True}
 (ROOT/'results'/'R00_078B_FEB_FROZEN.json').write_text(json.dumps(obj,indent=2)+'\n')
 print('FEB FROZEN',winner,'incumbent',x.loc['INCUMBENT_077'].to_dict(),'winner',x.loc[winner].to_dict(),flush=True)

def finish():
 obj=json.loads((ROOT/'results'/'R00_078B_FEB_FROZEN.json').read_text());winner=obj['FEB_frozen_winner']
 df=pd.concat([pd.read_csv(ROOT/'results'/f'R00_078B_{b}_{m}_POLICIES.csv') for b in ('coinexx','dukascopy') for m in ('02','06','07')]);df.to_csv(ROOT/'results'/'R00_078B_ALL_POLICY_BROKER_MONTH.csv',index=False)
 d=df[df.month.isin((6,7))].groupby('policy')[['events','correct','flips','rescued','damaged','net','buy','sell']].sum();d['accuracy']=d.correct/d.events
 d.to_csv(ROOT/'results'/'R00_078B_EXPOSED_ALL_POLICIES.csv')
 res={'frozen_feb':winner,'feb_scores':obj['FEB_scores'],'incumbent_exposed':d.loc['INCUMBENT_077'].to_dict(),'selected_exposed':d.loc[winner].to_dict(),'delta_vs_077_exposed':int(d.loc[winner,'correct']-d.loc['INCUMBENT_077','correct']),'descriptive_hindsight_best_NOT_SELECTED':str(d.correct.idxmax()),'original_events_unchanged':True,'no_June_July_reselection':True,'no_exit_profit_blind':True}
 (ROOT/'results'/'R00_078B_RESEARCH_RECEIPT.json').write_text(json.dumps(res,indent=2)+'\n')
 print('COMPLETE',json.dumps(res),flush=True)

if __name__=='__main__':
 action=sys.argv[1]
 if action=='score':score(sys.argv[2],sys.argv[3])
 elif action=='freeze':freeze()
 elif action=='finish':finish()
 else:raise ValueError(action)
