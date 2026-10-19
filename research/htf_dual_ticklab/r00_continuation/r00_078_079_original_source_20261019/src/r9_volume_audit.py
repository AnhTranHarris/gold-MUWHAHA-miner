"""R00-078/079 R9 SYNTH original UTC quota on EXACT original broker/month reference keys.
This corrected version retains ALL original hourly/day R9 month-boundary rows;
earlier combined-month deduplication had incorrectly collapsed reference windows.
Historical diagnostic only, never fills/profits. Original bad v0 retained separately.
"""
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
REF=Path('/mnt/data/xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results')
H=pd.read_csv(REF/'R00_077_R9_HOUR_DAY_ALL.csv')
W=pd.read_csv(REF/'R00_077_R9_WEEK_MONTH_ALL.csv')
POL={'R00_077_incumbent':('ref','AGREE_005'),'R00_078A_frozen':('a','FLIP_010'),'R00_078B_frozen':('b','078_PRIO_STRONG'),'R00_079_frozen':('c','PREVIOUS_FUSION_SELECTED')}

def obtain(b,m):
 with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz') as z0,np.load(ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz') as z1,np.load(ROOT/'results'/f'R00_078B_{b}_{m}_EVENTS.npz') as z2,np.load(ROOT/'results'/f'R00_079_{b}_{m}_EVENTS.npz') as z3:
  assert all(np.array_equal(z0['ts_ms'],z['ts_ms']) and np.array_equal(z0['y'],z['y']) for z in (z1,z2,z3))
  obj={'ts':z0['ts_ms'].copy()}
  for p,(s,k) in POL.items():obj[p]=(z0['y']=={'ref':z0,'a':z1,'b':z2,'c':z3}[s][k]).copy()
  return obj

def period_counts(keys,positive,ref,reference_key):
 cnt=pd.Series(keys).value_counts();corr=pd.Series(keys[positive]).value_counts()
 rows=[]
 for row in ref.itertuples():
  key=str(getattr(row,reference_key)) if reference_key=='UTC_key' else int(getattr(row,reference_key))
  n=int(cnt.get(key,0));good=int(corr.get(key,0));floor=int(row.floor90)
  rows.append((str(key),int(row.R9_SYNTH_trades),floor,n,good,n>=floor,good>=floor,n>=floor and good>=floor))
 return rows

def run():
 res=[]
 for b in ('coinexx','dukascopy'):
  months={m:obtain(b,m) for m in ('06','07')}
  tsall=np.concatenate([months[m]['ts'] for m in ('06','07')]);dt=pd.to_datetime(tsall,unit='ms',utc=True)
  iw=dt.isocalendar();wkeys=np.asarray([f'{int(y)}-W{int(w):02d}' for y,w in zip(iw.year,iw.week)],dtype='U10');mkeys=np.asarray(dt.strftime('%Y-%m'),dtype='U7')
  for policy in POL:
   for m,arr in months.items():
    ts=arr['ts'];pos=arr[policy]
    for kind,unit in [('hour',3600000),('day',86400000)]:
     ref=H[(H.broker==b)&(H.month==int(m))&(H.interval==kind)&(H.policy=='BASE')].copy()
     # All references including overlapped month boundary must survive.
     assert ref[['broker','month','interval','key']].duplicated().sum()==0
     for key,r9,floor,n,good,vpass,cpass,both in period_counts(ts//unit,pos,ref,'key'):
      res.append({'broker':b,'source_month':m,'interval':kind,'key':key,'policy':policy,'R9_SYNTH_trades':r9,'floor90':floor,'source_emissions':n,'direction_correct':good,'emissions_pass':vpass,'correct_pass':cpass,'both_pass':both})
   joint=np.concatenate([months[m][policy] for m in ('06','07')])
   for kind,keys in [('ISO_week',wkeys),('UTC_month',mkeys)]:
    ref=W[(W.broker==b)&(W.interval==kind)&(W.policy=='BASE')].copy()
    assert ref[['broker','interval','UTC_key']].duplicated().sum()==0
    for key,r9,floor,n,good,vpass,cpass,both in period_counts(keys,joint,ref,'UTC_key'):
     res.append({'broker':b,'source_month':'06+07','interval':kind,'key':key,'policy':policy,'R9_SYNTH_trades':r9,'floor90':floor,'source_emissions':n,'direction_correct':good,'emissions_pass':vpass,'correct_pass':cpass,'both_pass':both})
 d=pd.DataFrame(res);d.to_csv(ROOT/'results'/'R00_078_079_ORIGINAL_R9_ALL_INTERVAL_QUOTA.csv',index=False)
 z=d.groupby(['policy','interval']).agg(total=('both_pass','size'),both_pass=('both_pass','sum'),volume=('emissions_pass','sum'),correct_floor=('correct_pass','sum'),emitted=('source_emissions','sum'),correct=('direction_correct','sum')).reset_index()
 z.to_csv(ROOT/'results'/'R00_078_079_ORIGINAL_R9_QUOTA_SUMMARY.csv',index=False)
 d[~d.both_pass].to_csv(ROOT/'results'/'R00_078_079_R9_ALL_FAILED_REFERENCE_WINDOWS.csv',index=False)
 print(z.to_string(index=False))
 assert z[(z.policy=='R00_077_incumbent')&(z.interval=='hour')].iloc[0]['total']==2006
 assert z[(z.policy=='R00_077_incumbent')&(z.interval=='hour')].iloc[0]['both_pass']==1998
 assert z[(z.policy=='R00_077_incumbent')&(z.interval=='day')].iloc[0]['total']==110
 assert z[(z.policy=='R00_077_incumbent')&(z.interval=='day')].iloc[0]['both_pass']==108
if __name__=='__main__':run()
