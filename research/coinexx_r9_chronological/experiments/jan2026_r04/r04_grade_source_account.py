"""Full January fixed-original trade/control grading only. NO original reference inside runtime."""
import os
import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
R=Path(__file__).parent; ORIG=Path(os.environ.get('R9_R03_FOLDER','/mnt/data/r9_jan_r03'))
ref=pd.read_csv(os.environ.get('R9_REFERENCE_MANIFEST','/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv'))
assert len(ref)==27980 and int((ref.original_booked_net_usd>0).sum())==24368
assert round(ref.original_booked_net_usd.sum(),2)==41520.82
ro=ref.entry_sec.to_numpy('int64');rx=ref.exit_sec.to_numpy('int64');rs=np.where(ref.side=='BUY',1,-1)

def matching(df,sec):
 ge=df.entry_time_msc.to_numpy('int64')//1000;gx=df.exit_time_msc.to_numpy('int64')//1000;gs=df.side.to_numpy('int8');find={s:np.flatnonzero(gs==s) for s in (-1,1)}
 ind=[0];ix=[]
 for j in range(len(ref)):
  inds=find[int(rs[j])];etime=ge[inds]
  lo=np.searchsorted(etime,ro[j]-sec);hi=np.searchsorted(etime,ro[j]+sec,side='right')
  z=inds[lo:hi];z=z[np.abs(gx[z]-rx[j])<=sec]
  ix.extend(z.tolist());ind.append(len(ix))
 mat=csr_matrix((np.ones(len(ix),dtype=np.int8),np.array(ix,dtype=np.int32),np.array(ind,dtype=np.int32)),shape=(len(ref),len(df)))
 return maximum_bipartite_matching(mat,perm_type='column')
recovered=np.flatnonzero((ref.leg==1)&(ref.cycle_legs==2)&(ref.original_booked_net_usd<0)&(ref.cycle_net_usd>0))
assert len(recovered)==2147
filelist=['r04_meta_0.csv','r04_meta_0p65.csv','r04_meta_0p75.csv','r04_mfe56.csv','r04_book98.csv','r04_phase_mfe56.csv','r04_phase_mfe56_70.csv','r04_phase_mfe56_80.csv','r04_mode_0.csv','r04_mode_1.csv','r04_mode_2.csv','r04_mode_3.csv']
summary=[]
for name in filelist:
 df=pd.read_csv(R/name).sort_values('entry_time_msc').reset_index(drop=True)
 net=df.net_cash_cents.to_numpy('int64') if 'net_cash_cents' in df else df.net_quote_cents.to_numpy('int64')-2
 assert int(net.sum())==int(df.net_quote_cents.sum()-2*len(df))
 assert df.entry_ordinal.is_monotonic_increasing and (df.exit_ordinal>df.entry_ordinal).all()
 pre=10000+np.r_[0,np.cumsum(net)]
 peak=np.maximum.accumulate(pre);maxdd=int(max(peak-pre))
 days=(df.exit_time_msc//86400000).astype('int64')
 g=pd.Series(net).groupby(days).sum()
 record={'name':name,'positions':len(df),'fee_positive':int((net>0).sum()),'gross_positive':int((df.net_quote_cents>0).sum()),'cash_net_usd':round(net.sum()/100,2),'cash_balance_from_100_usd':round(100+net.sum()/100,2),'positive_utc_days':int((g>0).sum()),'negative_utc_days':int((g<0).sum()),'trading_days':len(g),'exit_booked_maxdd_usd':round(maxdd/100,2),'source_fee_usd_per_complete_trade':0.02}
 for tol in (2,5):
  a=matching(df,tol);rr=np.flatnonzero(a>=0);jj=a[rr];isorigpos=(ref.iloc[rr].original_booked_net_usd.to_numpy()>0)
  rec1=recovered[(a[recovered]>=0)&(a[recovered+1]>=0)]
  cycle_recovered=(net[a[rec1]]+net[a[rec1+1]])>0
  record.update({f'joint_{tol}s':len(rr),f'matched_original_winner_fee_positive_{tol}s':int((isorigpos&(net[jj]>0)).sum()),f'protected_recovered_2leg_both_matched_{tol}s':len(rec1),f'protected_recovered_2leg_fee_net_positive_{tol}s':int(cycle_recovered.sum())})
 summary.append(record)
(R/'r04_grade_results.json').write_text(json.dumps({'immutable_original':{'trades':len(ref),'original_fee_booked_PnL_usd':round(ref.original_booked_net_usd.sum(),2),'original_winners':24368,'original_recovered_cycles':2147},'full_results':summary},indent=2))
pd.DataFrame(summary).to_csv(R/'r04_graded_trials.csv',index=False)
for z in summary:print(z['name'],z['positions'],z['fee_positive'],z['cash_net_usd'],z['joint_2s'],z['matched_original_winner_fee_positive_2s'],z['protected_recovered_2leg_both_matched_2s'],z['positive_utc_days'],z['negative_utc_days'],flush=True)
