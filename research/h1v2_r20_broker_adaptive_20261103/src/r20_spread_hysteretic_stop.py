"""R20-C8 broker spread-normalized initial inventory risk STOP counterfactual.

Original R19-S3 winner intervals remain frozen, so the tested opportunity
population is only its failed 15min windows. This test CHANGES the stop geometry
and cannot be counted as original H1V2 first15/full30 surviving correctness.
Each new candidate direction is FUTURE-LABELED independently, never as-of chosen.
Wins found here cost the whole observed entry spread and nominal fee. Loss tails
and opportunity value must be measured; do not promote a widened stop to an EA.
"""
from __future__ import annotations
import argparse,json,csv,sys,time
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path('/mnt/data');LAB=ROOT/'h1v2_r20_last46'
sys.path.insert(0,str(LAB/'src'))
import r20_residual_quote_hazard as parent
CASE=(('S0_FIXED_ADVERSE100',100),('S1_FIXED_ADVERSE200',200),('S2_FIXED_ADVERSE500',500),('S3_FIXED_ADVERSE1000',1000),('S4_SPREAD_RATIO_25PC_BOUNDED',-1))

@njit(cache=False)
def independent_paths(t,b,a,fill,stop_raw,slip):
 n=len(fill);code=np.full((n,2),-3,np.int8);exits=np.full((n,2),-1,np.int32);net=np.full((n,2),-2147483647,np.int32)
 for k in range(n):
  f=fill[k];barrier=stop_raw[k]
  for z in range(2):
   buy=z==0;paid=(a[f]+slip) if buy else (b[f]-slip)
   opening=b[f] if buy else a[f];prev=t[f];done=False
   for j in range(f+1,len(t)):
    if t[j]==t[f]:continue
    if t[j]-prev>15000:code[k,z]=-3;done=True;break
    prev=t[j]
    liq=b[j] if buy else a[j]
    pnl=(int(liq)-int(paid)-20-slip) if buy else (int(paid)-int(liq)-20-slip)
    if t[j]>t[f]+60000:
     if t[j]-(t[f]+60000)<=15000:
      code[k,z]=2;exits[k,z]=j;net[k,z]=pnl
     done=True;break
    adverse=(liq<=opening-barrier) if buy else (liq>=opening+barrier)
    if adverse:code[k,z]=0;exits[k,z]=j;net[k,z]=pnl;done=True;break
    if pnl>=100:code[k,z]=1;exits[k,z]=j;net[k,z]=pnl;done=True;break
   if not done:code[k,z]=-3
 return code,exits,net

def run(src,mon):
 started=time.monotonic();t,b,a,_,_,_,_=parent.get_frozen(src,mon)
 refs=parent.r18.refs_for_month(mon,ROOT);keys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 of,oe,baseline,miss=parent.get_old(src,mon,t,refs)
 ids,counts=parent.source_candidates(t,b,a,keys,miss,1)
 sp=a[ids].astype(np.int64)-b[ids].astype(np.int64)
 ids=ids[(sp>=0)&(sp<=8000)]
 delay=100;target=t[ids]+delay;ii=np.searchsorted(t,target,'left');j=np.minimum(ii,len(t)-1)
 valid=(ii<len(t))&(j>ids)&(t[j]>t[ids])&(t[j]-target<=1000)
 valid&=(t[j]>=keys[0]*900000)&(t[j]<(keys[-1]+1)*900000)
 after=a[j].astype(np.int64)-b[j].astype(np.int64)
 valid&=(after>=0)&(after<=8000)
 signal=ids[valid];rawfill=j[valid];fill,uniqueidx=np.unique(rawfill,return_index=True);signal=signal[uniqueidx]
 spread=(a[fill].astype(np.int64)-b[fill].astype(np.int64)).astype(np.int32)
 allresults=[];allq=[];allh=[];trace={}
 for case,value in CASE:
  stop=(np.full(len(fill),value,np.int32) if value>0 else np.minimum(1000,np.maximum(100,(spread+3)//4)).astype(np.int32))
  codes,exits,net=independent_paths(t,b,a,fill.astype(np.int32),stop,0)
  wins=np.argwhere(codes==1)
  f=fill[wins[:,0]].astype(np.int32);e=exits[wins[:,0],wins[:,1]].astype(np.int32)
  si=signal[wins[:,0]].astype(np.int32);s=np.where(wins[:,1]==0,1,-1).astype(np.int8);v=net[wins[:,0],wins[:,1]].astype(np.int32)
  nonoverlap=parent.exclude_occupied(t,f,e,of,oe)
  freef=f[nonoverlap];freee=e[nonoverlap];freev=v[nonoverlap];frees=s[nonoverlap];freesig=si[nonoverlap]
  pick=parent.pack_future_good(t,freef,freee,np.ones(len(freef),bool))
  addedf=freef[pick];addede=freee[pick];addeds=frees[pick];addedv=freev[pick];addedsig=freesig[pick]
  delta=np.bincount(t[addedf]//900000-keys[0],minlength=len(qref)).astype(np.int32)
  qn=baseline+delta;hn=qn.reshape(-1,4).sum(axis=1)
  completed=(codes==0)|(codes==1)|(codes==2)
  pairnet=net[completed].astype(np.int64)
  result={'source':src,'month':mon,'mechanism':case,'stop_raw_units':value,'max_horizon_ms':60000,
   'input_initial_spread_cap_raw':8000,'actual_fill_spread_cap_raw':8000,'nominal_lag_ms':100,'actual_quoted_price_fee_raw':20,
   'original_R19S3_missing_quarters':len(miss),'failed_quarter_raw_observations':counts['raw_quotes'],
   'fresh_unique_executable_fill_events':len(fill),'independent_dual_side_completed_good':int((codes==1).sum()),
   'independent_dual_side_completed_stop':int((codes==0).sum()),
   'independent_dual_side_completed_timeout':int((codes==2).sum()),
   'independent_dual_side_right_censored':int((codes==-3).sum()),
   'independent_dual_side_COMPLETED_quote_net_sum_counterfactual_RAW':int(pairnet.sum()),
   'independent_dual_side_COMPLETED_quote_net_mean_counterfactual_RAW':None if not len(pairnet) else float(pairnet.mean()),
   'new_source_future_selected_packed_trades':len(addedf),
   'base_active_quarter_quota_met':int(np.sum((qref>0)&(baseline>=qref))),
   'new_active_quarter_quota_met':int(np.sum((qref>0)&(qn>=qref))),
   'all_active_quarters':int(np.sum(qref>0)),
   'base_active_hour_quota_met':int(np.sum((href>0)&(baseline.reshape(-1,4).sum(axis=1)>=href))),
   'new_active_hour_quota_met':int(np.sum((href>0)&(hn>=href))),
   'all_active_hours':int(np.sum(href>0)),
   'mixed_original_R19_contract_and_new_conditional_regime_only':True,
   'widened_stop_IS_NOT_original_0p10_strict_label':value!=100,
   'independent_all_events_are_NOT_independent_portfolio_trades':True,
   'future_selected_winners_not_asof_predictable':True,
   'no_actual_broker_fill_cash_economics':True}
  allresults.append(result)
  for q in range(len(keys)):
   allq.append({'source':src,'month':mon,'mechanism':case,'UTC_quarter':refs['rows'][q]['utc_quarter'],
      'R9_SYNTH_source_ref':int(qref[q]),'base_R19_S3_future_winners':int(baseline[q]),
      'new_counterfactual_future_winners':int(delta[q]),'R20_future_total':int(qn[q]),
      'quota_met':int(qn[q]>=qref[q]) if qref[q] else '',
      'source_count_deficit':max(0,int(qref[q]-qn[q]))})
  for h in range(len(href)):
   allh.append({'source':src,'month':mon,'mechanism':case,'UTC_hour':refs['rows'][4*h]['utc_hour'],
     'R9_SYNTH_ref_hour':int(href[h]),'future_total_hour':int(hn[h]),
     'quota_met':int(hn[h]>=href[h]) if href[h] else '',
     'missing_slots':max(0,int(href[h]-hn[h]))})
  trace[case]={'source_signal_quote_ordinal':signal,'filled_quote_ordinal':fill,
   'stop_raw':stop,'both_buy_sell_independent_codes':codes,
   'both_side_exit_quote_ordinals':exits,'both_side_realized_quoted_price_net_raw':net,
   'new_source_signal_quote_ordinal':addedsig,'new_future_side':addeds,
   'new_fill_quote_ordinal':addedf,'new_first_target_exit_quote_ordinal':addede,'new_net_quote_raw':addedv}
  print(src,mon,case,'added',len(addedf),'Q',result['new_active_quarter_quota_met'],'H',result['new_active_hour_quota_met'],'all independent net raw',int(pairnet.sum()),flush=True)
 tag=f'R20C8_{src}_{mon}';d=LAB/'results'
 files=(d/f'{tag}_ALL_SCENARIOS.csv',d/f'{tag}_ALL_UTC_QUARTERS.csv',d/f'{tag}_ALL_UTC_HOURS.csv',d/f'{tag}_ALL_TRIAL_SOURCE_ORDINALS_AND_TWO_SIDES.npz')
 for path,rr in zip(files[:3],(allresults,allq,allh)):parent.write_csv(path,rr)
 np.savez_compressed(files[3],**{c+'__'+name:val for c,z in trace.items() for name,val in z.items()})
 receipt={'source':src,'month':mon,'raw_source_sha':parent.r18.PINS[src][mon],
  'full_calendar_quarters':len(keys),'full_calendar_hours':len(href),
  'cases':allresults,'files':{p.name:{'sha256':parent.sha(p),'size':p.stat().st_size} for p in files},
  'source_future_oracle_ONLY':True,'no_frozen_OOS_or_portfolio_economic_approval':True}
 (d/f'{tag}_SHA_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'),required=True);p.add_argument('--month',choices=('01','02','06','07'),required=True)
 a=p.parse_args();run(a.source,a.month)
