"""R15: separate source-exact 60s AS-OF staged confirmation from 60s FUTURE labels.

Research only. The source is original observed raw Bid/Ask chronology. Watching a
candidate is NOT a trade; entry is at the FIRST observed quote passing as-of
confirmation, and never at the watching quote. Buyer pays Ask, seller receives
Bid, fee is the historically specified 0.02 QUOTED-price units. An offline
hindsight selector sees future first-TP and safety outcomes; NO causal side
model, broker fill or deployable strategy is produced.

Old S1 strict first15 favorable, full30 zero adverse is a separate immutable
outcome. New 30/45/60-horizon event labels are DIFFERENT acceptance classes;
none can overwrite strict-S1. The new source is entirely additive R15.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

ROOT=Path(__file__).resolve().parents[1]
SYS=Path('/mnt/data')
R13SRC=SYS/'h1v2_r13_broker_adaptive/src'
if str(R13SRC) not in sys.path:sys.path.insert(0,str(R13SRC))
import r13_crossbroker_horizon_lanes as r13
import r13_delayed_executable_stress as r13stress

THIRTY=30000; MS_QUARTER=900000; MS_HOUR=3600000
HALO_START=r13.T0-360000;HALO_END=r13.T1+100000
FAV_HORIZONS=(15000,30000,45000,60000)
REFERENCE=(28,27,25,24)
FEE=20;TP=100;BAD=100;MAX_GAP=15000;FRESH=300000
STAGED=('WATCH60_COOL_TO_1500','WATCH60_COOL_TO_2500','WATCH60_FLOW_RELIEF_4000')
LANES=('BASE_250_1500','R13_WIDE_REQUOTE_4000',*STAGED,'UNION_BASE_AND_WATCH1500','UNION_ALL_WATCH_DIAGNOSTIC')
WATCH_MIN_AGE=250;WATCH_MAX_AGE=60000


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for buf in iter(lambda:f.read(1<<20),b''):h.update(buf)
 return h.hexdigest()


def load_source(source):
 path=SYS/r13.EXPECTED[source][0];pin=r13.EXPECTED[source][1]
 if sha(path)!=pin:raise ValueError(f'RAW_SOURCE_HASH_MISMATCH {source}')
 if source=='DUKASCOPY_RAW':
  f=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
   dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy(np.int64);b=f.bid_raw.to_numpy(np.int32);a=f.ask_raw.to_numpy(np.int32)
 else:
  f=pd.read_csv(path,compression='gzip',usecols=['time_msc','bid','ask'],
    dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=f.time_msc.to_numpy(np.int64)-2*3600000
  b=np.rint(f.bid.to_numpy(np.float64)*1000).astype(np.int32)
  a=np.rint(f.ask.to_numpy(np.float64)*1000).astype(np.int32)
 if len(t)<10 or np.any(np.diff(t)<0) or np.any(a<b):raise ValueError('INVALID_SOURCE_BID_ASK')
 lo=np.searchsorted(t,HALO_START,'left');hi=np.searchsorted(t,HALO_END,'right')
 t=t[lo:hi].copy();b=b[lo:hi].copy();a=a[lo:hi].copy()
 if t[0]>r13.T0-FRESH or t[-1]<r13.T1+60000:raise ValueError('INCOMPLETE_60S_HALO')
 return t,b,a,pin


@njit(cache=True)
def watch60_first_observed(t,b,a,all_ix,flags,ema300,ema15,moveb3,movea3):
 """As-of deterministic three independent watch-state machines.

 The only promise from the initial observed wide-spread quote is to RECHECK
 for <=60s; it is NEVER a filled trade. Subsequent quote is a decision only
 when it is observed. At most one watch per mechanism; no future knowledge.
 0 started, 1 confirmed, 2 expired, 3 reset, counters per lane.
 """
 m=len(all_ix);seen=np.zeros((3,m),np.bool_)
 starts=np.zeros(3,np.int64);confirm=np.zeros(3,np.int64)
 expire=np.zeros(3,np.int64);gapreset=np.zeros(3,np.int64)
 active=np.zeros(3,np.bool_);birth=np.zeros(3,np.int64)
 initial_s=np.zeros(3,np.int32);prev_idx=-1
 for k in range(m):
  i=all_ix[k];ti=t[i];s=a[i]-b[i]
  if prev_idx>=0 and t[i]-t[i-1]>MAX_GAP:
   for z in range(3):
    if active[z]:active[z]=False;gapreset[z]+=1
  prev_idx=i
  for z in range(3):
   if active[z] and ti-birth[z]>WATCH_MAX_AGE:
    active[z]=False;expire[z]+=1
   if active[z] and WATCH_MIN_AGE<=ti-birth[z]<=WATCH_MAX_AGE:
    if z==0:
     eligible=(s<=1500 and 10*s<=7*initial_s[z])
    elif z==1:
     eligible=(s<=2500 and 10*s<=8*initial_s[z] and ema15[i]<=ema300[i])
    else:
     coherent=(moveb3[i]>0 and movea3[i]>0) or (moveb3[i]<0 and movea3[i]<0)
     motion=min(abs(moveb3[i]),abs(movea3[i]))
     eligible=(s<=4000 and 10*s<=8*initial_s[z] and
       ema15[i]<=ema300[i] and coherent and motion>=s+FEE+TP)
    if eligible:
     seen[z,k]=True;confirm[z]+=1;active[z]=False
   if not active[z] and ((int(flags[k])&1)!=0):
    if z==0:trigger=(2000<=s<=4000)
    elif z==1:trigger=(2800<=s<=4000)
    else:trigger=(1800<=s<=4000 and ema15[i]>=ema300[i])
    if trigger:
     active[z]=True;birth[z]=ti;initial_s[z]=s;starts[z]+=1
 return seen,starts,confirm,expire,gapreset


def independent_labels(t,b,a,ix):
 """Official frozen extrema plus new 45/60 horizon as distinct outputs."""
 labels={};extrema={}
 for h in FAV_HORIZONS:
  minb,maxb,mina,maxa,_,_,covered=r13.frozen_extrema(t,b,a,ix,h)
  b_safe=covered & (minb.astype(np.int64)>b[ix].astype(np.int64)-BAD)
  s_safe=covered & (maxa.astype(np.int64)<a[ix].astype(np.int64)+BAD)
  favb=covered & (maxb.astype(np.int64)>=a[ix].astype(np.int64)+FEE+TP)
  favs=covered & (mina.astype(np.int64)<=b[ix].astype(np.int64)-FEE-TP)
  labels[h]={'BUY_favorable':favb,'SELL_favorable':favs,
    'BUY_safe':b_safe,'SELL_safe':s_safe,'covered':covered,
    'BUY_strict':favb&b_safe,'SELL_strict':favs&s_safe}
  extrema[h]=(minb,maxb,mina,maxa)
 original={'BUY_strict':labels[15000]['BUY_favorable']&labels[30000]['BUY_safe']&labels[30000]['covered'],
   'SELL_strict':labels[15000]['SELL_favorable']&labels[30000]['SELL_safe']&labels[30000]['covered']}
 original['any']=original['BUY_strict']|original['SELL_strict']
 # The original S1 confirmation must be distinct from the 60s research label.
 if np.any(original['BUY_strict']&original['SELL_strict']):raise ValueError('ORIGINAL_STRICT_BOTH_SIDES')
 return labels,original


def get_lanes(t,b,a,ix,flags,e300,e15,mb3,ma3):
 base=r13.lane_membership(ix,flags,b,a,e300,e15,mb3,ma3)
 seen,starts,confirm,expire,resets=watch60_first_observed(t,b,a,ix,flags,e300,e15,mb3,ma3)
 out={
  'BASE_250_1500':base['BASE_250_1500'],
  'R13_WIDE_REQUOTE_4000':base['WIDE_REQUOTE_4000'],
  STAGED[0]:seen[0],STAGED[1]:seen[1],STAGED[2]:seen[2],
  'UNION_BASE_AND_WATCH1500':base['BASE_250_1500']|seen[0],
  'UNION_ALL_WATCH_DIAGNOSTIC':base['BASE_250_1500']|seen[0]|seen[1]|seen[2]
 }
 assert tuple(out)==LANES
 return out,{'starts':starts.tolist(),'confirms':confirm.tolist(),
   'expires':expire.tolist(),'gap_resets':resets.tolist()}


def selected_schedule(t,b,a,ix,goodb,goods,h):
 """Exact interval count from source-FUTURE firstTP exits; no live predictor."""
 ids=np.flatnonzero(goodb|goods)
 if not len(ids):return ids,np.empty(0,np.int8),np.empty(0,np.int64),np.empty(0,np.int64)
 if np.any(goodb[ids]&goods[ids]):raise ValueError('TWO_FUTURE_SIDES')
 s=np.where(goodb[ids],1,-1).astype(np.int8)
 j,ends=r13.first_tp(t,b,a,ix[ids],s,h)
 if np.any(j<0) or np.any(ends<=t[ix[ids]]):raise ValueError('MISSING_FUTURE_FIRST_TP')
 net=np.where(s==1,b[j]-a[ix[ids]],b[ix[ids]]-a[j])-FEE
 if np.any(net<TP):raise ValueError('FALSE_FIRST_TP_ECONOMICS')
 pick=r13.exact_interval_schedule(t[ix[ids]],ends)
 return ids[pick],s[pick],j[pick],net[pick]


def writecsv(path,rows):
 if not rows:raise ValueError('EMPTY_CSV')
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def quarter_count(starts,ref=REFERENCE):
 return [int(np.sum((starts>=r13.T0+q*MS_QUARTER)&(starts<r13.T0+(q+1)*MS_QUARTER))) for q in range(4)]


def run_source(source):
 t,b,a,pin=load_source(source)
 ix,flags,e300,e15,mb3,ma3=r13.prefix_candidates(t,b,a)
 inhour=(t[ix]>=r13.T0)&(t[ix]<r13.T1)
 ix=ix[inhour];flags=flags[inhour]
 if not len(ix):raise RuntimeError('EMPTY_SOURCE_CANDIDATES')
 # Features are past-only; filtering is by decision clock before outcomes.
 lanes,stats=get_lanes(t,b,a,ix,flags,e300,e15,mb3,ma3)
 labels,original=independent_labels(t,b,a,ix)
 results=[];quarters=[];traces=[];stress=[];stressq=[]
 for lane,valid in lanes.items():
  for horizon in FAV_HORIZONS:
   if horizon==15000:
    goodb=valid&original['BUY_strict'];goods=valid&original['SELL_strict']
    safety='full30_zero_adverse';metric='original_strict15_full30'
   else:
    goodb=valid&labels[horizon]['BUY_strict'];goods=valid&labels[horizon]['SELL_strict']
    safety=f'full{horizon//1000}_zero_adverse';metric=f'NEW_strict{horizon//1000}'
   sel,side,exit_ix,net=selected_schedule(t,b,a,ix,goodb,goods,horizon)
   sidx=ix[sel];st=t[sidx]
   qcounts=quarter_count(st)
   orig15=original['any'][sel]
   oorig=original['BUY_strict'][sel] if len(sel) else np.array([],bool)
   if len(sel):
    oorig=np.where(side==1,original['BUY_strict'][sel],original['SELL_strict'][sel])
   hour={'source':source,'lane':lane,'forward_favorable_horizon_ms':horizon,
      'label_contract':metric,'no_adverse_contract':safety,
      'source_original_raw_sha256':pin,'asof_lane_candidate_count':int(valid.sum()),
      'hindsight_eligible_candidate_count':int((goodb|goods).sum()),
      'future_selected_exact_firstTP_onepos_count':int(len(sel)),
      'original_15s_correct_among_future_selected':int(oorig.sum()),
      'original_15s_correct_rate_of_future_selected':None if not len(sel) else float(oorig.mean()),
      'original_R9_reference_hour':104,'future_selected_count_meets_hour':bool(len(sel)>=104),
      'every_quarter_meets_ref':bool(all(c>=r for c,r in zip(qcounts,REFERENCE))),
      'hindsight_side_not_causal':True,'future_selected_not_deployable':True,
      'experimental_spread_cap_4_NOT_APPROVED':lane not in ('BASE_250_1500','WATCH60_COOL_TO_1500','UNION_BASE_AND_WATCH1500')}
   results.append(hour)
   for q in range(4):
    inq=(t[ix]>=r13.T0+q*MS_QUARTER)&(t[ix]<r13.T0+(q+1)*MS_QUARTER)
    local=np.flatnonzero((goodb|goods)&inq)
    # Optimistic crossing bound ignores global intervals outside the quarter.
    if len(local):
     ls=np.where(goodb[local],1,-1).astype(np.int8)
     jj,ee=r13.first_tp(t,b,a,ix[local],ls,horizon)
     local_pick=r13.exact_interval_schedule(t[ix[local]],ee)
     upper=len(local_pick)
    else:upper=0
    qr={k:hour[k] for k in ('source','lane','forward_favorable_horizon_ms','label_contract','source_original_raw_sha256')}
    qr.update({'quarter_UTC_start':dt.datetime.fromtimestamp((r13.T0+q*MS_QUARTER)/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
      'original_R9_SYNTH_reference_quarter':REFERENCE[q],
      'source_independent_quarter_optimistic_upper':int(upper),
      'source_independent_quarter_proven_impossible_under_THIS_contract':bool(upper<REFERENCE[q]),
      'global_future_selected_in_quarter':qcounts[q],
      'global_hindsight_selection_meets_quarter':bool(qcounts[q]>=REFERENCE[q]),
      'original_strict15_selected_in_this_quarter':int(np.count_nonzero((st>=r13.T0+q*MS_QUARTER)&(st<r13.T0+(q+1)*MS_QUARTER)&oorig)),
      'changed_horizon_cannot_credit_original_strict':horizon!=15000})
    quarters.append(qr)
   for k,j in enumerate(sidx):
    e=int(exit_ix[k]);price_net=int(net[k]);
    traces.append({'source':source,'lane':lane,'horizon_ms':horizon,'signal_utc_ms':int(t[j]),
     'entry_source_quote_ordinal':int(j),'exit_source_quote_ordinal':e,'exit_utc_ms':int(t[e]),
     'entry_bid_raw':int(b[j]),'entry_ask_raw':int(a[j]),'exit_bid_raw':int(b[e]),'exit_ask_raw':int(a[e]),
     'spread_raw':int(a[j]-b[j]),'BUY_1_SELL_minus1_FUTURE_KNOWN':int(side[k]),
     'net_after_nominal_fee_raw':price_net,'original_strict15_full30':int(oorig[k]),
     'asof_observed_entry_not_watch_trigger':True,'hindsight_only':True})
   # For ORIGINAL strict class only, stress the originally selected positions.
   # The changed 30/45/60 class is not silently counted as original-good.
   if horizon==15000:
    for lag in (0,100,500):
     for slip in (0,20,50):
      cap=1500 if lane in ('BASE_250_1500','WATCH60_COOL_TO_1500','UNION_BASE_AND_WATCH1500') else 4000
      outcome,fill,ex,netstress=r13stress.stressed_frozen_signal(t,b,a,sidx,side,lag,slip,cap)
      goodn=int((outcome==1).sum());badn=int((outcome==0).sum());cens=int((outcome==-3).sum())
      den=goodn+badn;accuracy=None if not den else goodn/den
      sr={'source':source,'lane':lane,'lag_ms':lag,'slippage_raw_per_leg':slip,
        'source_original_raw_sha256':pin,'future_known_original_strict_signals':int(len(sidx)),
        'strict_good_after_delay':goodn,'strict_completed_failure_after_delay':badn,
        'right_censored_after_delay':cens,'spread_or_quote_reject':int((outcome==-1).sum()),
        'busy_position_skip':int((outcome==-2).sum()),
        'completed_accuracy':accuracy,'original_hour_ref':104,
        'joint_hour_good_and80pct':bool(goodn>=104 and accuracy is not None and accuracy>=0.8),
        'NO_FAILED_TRADE_PNL_MODEL':True,'original_future_selected_signals_NOT_CAUSAL':True}
      stress.append(sr)
      for q in range(4):
       lo=r13.T0+q*MS_QUARTER;hi=lo+MS_QUARTER
       qsel=(fill>=0)&(t[np.maximum(fill,0)]>=lo)&(t[np.maximum(fill,0)]<hi)
       g=int(np.count_nonzero(qsel&(outcome==1)));bd=int(np.count_nonzero(qsel&(outcome==0)))
       denq=g+bd;accq=None if not denq else g/denq
       stressq.append({**{k:sr[k] for k in ('source','lane','lag_ms','slippage_raw_per_leg')},
        'quarter_UTC':dt.datetime.fromtimestamp(lo/1000,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
        'quarter_original_ref':REFERENCE[q],'good_at_actual_fill_quote':g,'bad_at_actual_fill_quote':bd,
        'censored_at_actual_fill_quote':int(np.count_nonzero(qsel&(outcome==-3))),
        'completed_accuracy_quarter':accq,'joint_good_ref_and80pct':bool(g>=REFERENCE[q] and accq is not None and accq>=.8),
        'only_filled_positions_counted':True})
      tag=f'R15_{source}_{lane}_lag{lag}_slip{slip}'
      np.savez_compressed(ROOT/'results'/(tag+'_ALL_FROZEN_SOURCE_ORDINALS.npz'),
       original_source_signal_ix=sidx,original_signal_ts=t[sidx],future_known_side=side,
       fill_source_ix=fill,firstTP_exit_source_ix=ex,outcome_code=outcome,net_reachable_raw=netstress)
 # Save full source candidate membership and labels to prove geometry truly asof.
 np.savez_compressed(ROOT/'results'/f'R15_{source}_ALL_ASOF_CANDIDATES_ALL_LANES_AND_SEPARATE_STRICT_LABELS.npz',
   source_quote_ix=ix,source_utc_ms=t[ix],quote_bid_raw=b[ix],quote_ask_raw=a[ix],
   lane_names=np.asarray(LANES),lane_bits=np.column_stack([lanes[k] for k in LANES]),
   original_strict15_buy=original['BUY_strict'],original_strict15_sell=original['SELL_strict'],
   strict30_buy=labels[30000]['BUY_strict'],strict30_sell=labels[30000]['SELL_strict'],
   strict45_buy=labels[45000]['BUY_strict'],strict45_sell=labels[45000]['SELL_strict'],
   strict60_buy=labels[60000]['BUY_strict'],strict60_sell=labels[60000]['SELL_strict'],
   complete30=labels[30000]['covered'],complete60=labels[60000]['covered'])
 src={'source':source,'source_sha256':pin,'quotes_in_source_halo':len(t),
      'source_observed_candidates_before_labels':len(ix),'watch':stats,
      'future_hindsight_not_runtime':True}
 return results,quarters,traces,stress,stressq,src


def run():
 started=time.time();ROOT.joinpath('results').mkdir(exist_ok=True)
 hr=[];qr=[];trace=[];strs=[];strq=[];sources=[]
 for source in r13.EXPECTED:
  h,q,tr,s,sq,info=run_source(source)
  hr+=h;qr+=q;trace+=tr;strs+=s;strq+=sq;sources.append(info)
  print(json.dumps({'source':source,'hours':len(h),'quarters':len(q),
   'selected_trace_rows':len(tr),'strict_stress_scenarios':len(s),
   'full_source_sha':info['source_sha256'],'watch':info['watch']}),flush=True)
 assert len(hr)==3*len(LANES)*len(FAV_HORIZONS) and len(qr)==4*len(hr)
 assert len(strs)==3*len(LANES)*9 and len(strq)==4*len(strs)
 writecsv(ROOT/'results/R15_ALL_84_SOURCE_LANE_HORIZON_HOURS.csv',hr)
 writecsv(ROOT/'results/R15_ALL_336_SOURCE_LANE_HORIZON_QUARTERS.csv',qr)
 writecsv(ROOT/'results/R15_ALL_FUTURE_SELECTED_ORIGINAL_SOURCE_ORDINALS.csv',trace)
 writecsv(ROOT/'results/R15_ALL_189_ORIGINAL_STRICT_LATENCY_STRESS.csv',strs)
 writecsv(ROOT/'results/R15_ALL_756_ORIGINAL_STRICT_LATENCY_QUARTERS.csv',strq)
 receipt={'sources':sources,'lanes':LANES,'horizons_ms':FAV_HORIZONS,
    'source_lane_horizon_count':len(hr),'full_quarter_rows':len(qr),
    'source_lane_latency_rows':len(strs),'source_lane_latency_quarters':len(strq),
    'total_all_alternative_trace_rows':len(trace),
    'original_strict_fav15_safe30_label_immutable':True,
    'new_60s_label_is_not_original_15s':True,
    'watch_trigger_does_not_enter_at_trigger_price':True,
    'full_account_realized_PNL_and_broker_execution_UNKNOWN':True,
    'future_selected_side_and_schedule_not_predictive':True,
    'research_only_no_MQL5_live_deployment':True,'elapsed_s':time.time()-started}
 (ROOT/'results/R15_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 members={str(p.relative_to(ROOT)):{'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.rglob('*'))
     if p.is_file() and '__pycache__' not in str(p) and '.pytest_cache' not in str(p) and 'R15_MEMBER_SHA256_MANIFEST' not in p.name}
 (ROOT/'R15_MEMBER_SHA256_MANIFEST.json').write_text(json.dumps({'inputs':sources,'members':members},indent=2,allow_nan=False)+'\n')
 print(json.dumps({'complete':True,'receipts':receipt,'manifest_members':len(members)},indent=2),flush=True)
 return receipt

if __name__=='__main__':run()
