"""Offline immutable original January target grading. NEVER included in autonomous replay."""
from pathlib import Path
import csv,json,hashlib,numpy as np,pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
R=Path(__file__).parent
orig=pd.read_csv('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
assert (len(orig),int((orig.original_booked_net_usd>0).sum()),round(orig.original_booked_net_usd.sum(),2))==(27980,24368,41520.82)
assert int(((orig.leg==1)&(orig.cycle_legs==2)&(orig.original_booked_net_usd<0)&(orig.cycle_net_usd>0)).sum())==2147
ri=orig.entry_sec.to_numpy('int64');ro=orig.exit_sec.to_numpy('int64');s=np.where(orig.side=='BUY',1,-1)
recover=np.flatnonzero((orig.leg==1)&(orig.cycle_legs==2)&(orig.original_booked_net_usd<0)&(orig.cycle_net_usd>0))
files=sorted(R.glob('r05_joint_mode*.csv'))
rows=[]
for file in files:
 d=pd.read_csv(file);net=d.net_cash_cents.to_numpy('int64');assert len(d)==int((d.exit_ordinal>d.entry_ordinal).sum());assert int((d.net_quote_cents-2!=net).sum())==0; assert d.entry_ordinal.is_monotonic_increasing
 base={'file':file.name,'executed':len(d),'first_legs':int((d.leg==1).sum()),'second_legs':int((d.leg==2).sum()),'fee_wins':int((net>0).sum()),'net_account_usd':round(net.sum()/100,2),'daily_positive':0,'daily_negative':0}
 z=d.pivot_table(index='minute_id',columns='leg',values='net_cash_cents',aggfunc='first');g2=z.dropna(subset=[1,2]);base['simulated_negative_first_recovered_cycle_count']=int(((g2[1]<0)&(g2[2]>0)&(g2[1]+g2[2]>0)).sum())
 dates=(d.exit_time_msc//86400000).astype('int64');g=pd.Series(net).groupby(dates).sum();base['daily_positive']=int((g>0).sum());base['daily_negative']=int((g<0).sum());equity=10000+np.r_[0,np.cumsum(net)];base['closed_book_dd_usd']=round(np.max(np.maximum.accumulate(equity)-equity)/100,2);cross=np.flatnonzero(equity[1:]<=0);base['first_nonpositive_cash_after_trade']=int(cross[0]+1) if len(cross) else None;base['hypothetical_closed_cash_survives_above_zero']=not bool(len(cross))
 ge=d.entry_time_msc.to_numpy('int64')//1000;gx=d.exit_time_msc.to_numpy('int64')//1000;gs=d.side.to_numpy('int8');
 for tol in (2,5):
  find={direction:np.flatnonzero(gs==direction) for direction in (-1,1)};ii=[0];jj=[]
  for k in range(len(orig)):
   ind=find[s[k]];x=ge[ind];start=np.searchsorted(x,ri[k]-tol);stop=np.searchsorted(x,ri[k]+tol,'right');co=ind[start:stop];co=co[np.abs(gx[co]-ro[k])<=tol];jj.extend(co.tolist());ii.append(len(jj))
  mat=csr_matrix((np.ones(len(jj),dtype=np.int8),np.asarray(jj,dtype=np.int32),np.asarray(ii,dtype=np.int32)),shape=(len(orig),len(d)))
  mapping=maximum_bipartite_matching(mat,perm_type='column');valid=np.flatnonzero(mapping>=0);sim=mapping[valid];win=orig.original_booked_net_usd.to_numpy()[valid]>0;cash=net[sim]
  eligible=recover[(mapping[recover]>=0)&(mapping[recover+1]>=0)]
  matchpos=eligible[(net[mapping[eligible]]+net[mapping[eligible+1]])>0]
  base.update({f'match_{tol}s':len(valid),f'original_winners_matched_{tol}s':int(win.sum()),f'original_winners_matched_and_fee_win_{tol}s':int((win&(cash>0)).sum()),f'protected_2leg_both_matched_{tol}s':len(eligible),f'protected_2leg_fee_positive_{tol}s':len(matchpos)})
 rows.append(base);print(json.dumps(base),flush=True)
pd.DataFrame(rows).to_csv(R/'R05_GRADED_JANUARY.csv',index=False)
(R/'R05_GRADED_JANUARY.json').write_text(json.dumps({'original_target':{'trades':27980,'profitable':24368,'profit_target_95pct':23150,'matching_target_95pct':26581,'recovered':2147,'booked_original_net_usd':41520.82},'trials':rows},indent=2))
