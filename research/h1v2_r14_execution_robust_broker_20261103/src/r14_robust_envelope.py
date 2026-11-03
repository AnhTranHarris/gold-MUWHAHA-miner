"""R14 independent observed-quote latency-envelope HINDSIGHT research.

Immutable upstream R13 and original H1V2 labels remain separate. At original
observed entry quote i, side is FUTURE-PRIVILEGED, chosen only if strict 15s
favorable+complete 30s zero-$0.10-adverse on source Bid/Ask. For each fixed
possible entry test 9 (lag, slippage) combinations using the same original
quote chronology and first-observed filled quote; never re-pick entry after
lag. We compare K-of-9 and ALL-9 robust hindsight capacities and independent
15-minute bounds. None of this selects BUY/SELL from as-of features, implies
broker execution, or constitutes a valid true realized P&L backtest.
"""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, sys
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path(__file__).resolve().parents[1]
UP=Path('/mnt/data/h1v2_r13_broker_adaptive/src')
sys.path.insert(0,str(UP))
import r13_crossbroker_horizon_lanes as r13
LAGS=(0,100,500)
SLIPS=(0,20,50)
TIERS=(('strict_9of9',9),('robust_7of9',7),('robust_5of9',5),('base_1of9',1))
REFERENCE=(28,27,25,24)
LANES=('BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000','BROKER_CONTRACTION','DIRECTIONAL_MICROPATH','RELIEF_SHOCK_4000')

@njit(cache=True)
def evaluate_independent_stress(t,b,a,ix,side,cap_raw,lag_ms,slip_raw):
 """Each candidate evaluated independently. NO position busy suppression here.

code 1 strict good; 0 observed strict failure; -1 fill reject;
-3 censored/coverage failed. Fills and exits are observed raw ordinals.
"""
 n=len(t);m=len(ix)
 code=np.full(m,-3,np.int8);fills=np.full(m,-1,np.int64)
 exits=np.full(m,-1,np.int64);net=np.full(m,-2147483647,np.int32)
 for k in range(m):
  i=ix[k];s=side[k];target=t[i]+lag_ms
  f=i
  if lag_ms>0:
   lo=i+1;hi=n
   while lo<hi:
    md=(lo+hi)//2
    if t[md]<target:lo=md+1
    else:hi=md
   f=lo
  if f>=n or t[f]-target>1000 or t[f]>=r13.T1 or a[f]-b[f]>cap_raw or a[f]<b[f]:
   code[k]=-1;continue
  fills[k]=f
  e=a[f]+slip_raw if s==1 else b[f]-slip_raw
  opening=b[f] if s==1 else a[f]
  first=-1;prev=t[f];last=t[f];seen=False;bad=False;gap=False;covered=False
  h15=t[f]+15000;h30=t[f]+30000
  for j in range(f+1,n):
   if t[j]==t[f]:continue
   if t[j]>h30:
    if t[j]-last<=15000:covered=True
    break
   if t[j]-prev>15000:gap=True
   prev=t[j];last=t[j];seen=True
   liquidation=b[j] if s==1 else a[j]
   if s==1 and liquidation<=opening-100:bad=True
   if s==-1 and liquidation>=opening+100:bad=True
   if first<0 and t[j]<=h15:
    px=b[j]-slip_raw if s==1 else a[j]+slip_raw
    p=s*(px-e)-20
    if p>=100:first=j;net[k]=p
  if last==h30:covered=True
  if not seen or not covered or gap:code[k]=-3
  elif bad or first<0:code[k]=0
  else:code[k]=1;exits[k]=first
 return code,fills,exits,net


def additional_prefix_lane(ix,flag,b,a,ema300,ema15,moveb3,movea3):
 """New causal spread relief (distinct from R13 BROKER_CONTRACTION):
 initially 250ms or FIRST actually observed within-bin compression of .02,
 current spread <=70% of past-only EMA300, and BID/ASK 3s move coherent.
 Wide spread<=4 is a counterfactual only and still fully paid in targets.
 """
 s=a[ix].astype(np.int64)-b[ix].astype(np.int64)
 return ((flag.astype(np.int32)&3)!=0)&(s<=4000)&(s<=.70*ema300[ix])&(ema15[ix]<=ema300[ix])&(np.sign(moveb3[ix])==np.sign(movea3[ix]))


def greedy_nonoverlap(starts,ends):
 """Exact max cardinality for these fully known intervals; no quotas optimized."""
 if len(starts)==0:return np.empty(0,np.int64)
 if np.any(ends<=starts):raise ValueError('bad future interval')
 order=np.lexsort((np.arange(len(starts)),starts,ends));out=[];last=-2**62
 for k in order:
  if starts[k]>last:out.append(k);last=int(ends[k])
 return np.asarray(out,np.int64)


def quarter_metrics(t,ix,ok,ends,min_quality,require_good):
 """Independent optimistic quote-domain per-quarter upper, boundary conflicts ignored."""
 rec=[]
 for q in range(4):
  lo=r13.T0+q*900_000;hi=lo+900_000
  z=np.flatnonzero(ok&(t[ix]>=lo)&(t[ix]<hi))
  sel=greedy_nonoverlap(t[ix[z]],ends[z])
  ref=REFERENCE[q]
  rec.append({'quarter':dt.datetime.fromtimestamp(lo/1000,dt.timezone.utc).isoformat(),
    'original_R9_synth_reference':ref,'strict_eligible_candidate_count':int(len(z)),
    'independent_isolated_quarter_upper':int(len(sel)),
    'provably_unattainable_under_THIS_changed_envelope':bool(len(sel)<ref),
    'minimum_source_quarter_deficit':max(0,ref-len(sel)),
    'passes_80pct_future_selected_label':True if len(sel) else None})
 return rec


def source_replay(name):
 t,b,a,pin=r13.load_source(name)
 ix,flags,e300,e15,mb3,ma3=r13.prefix_candidates(t,b,a)
 mask=(t[ix]>=r13.T0)&(t[ix]<r13.T1)
 ix=ix[mask];flags=flags[mask]
 lanes=r13.lane_membership(ix,flags,b,a,e300,e15,mb3,ma3)
 lanes['RELIEF_SHOCK_4000']=additional_prefix_lane(ix,flags,b,a,e300,e15,mb3,ma3)
 # Reuse cryptographically pinned unmodified R11S1 two windows. Both original
 # quote future and 30s coverage required, not dynamic/changed 30s label.
 mn_b,mx_b,mn_a,mx_a,_,_,cov30=r13.frozen_extrema(t,b,a,ix,30000)
 _,mx_b15,mn_a15,_,_,_,cov15=r13.frozen_extrema(t,b,a,ix,15000)
 goodB=cov30&cov15&(mn_b.astype(np.int64)>b[ix].astype(np.int64)-100)&(mx_b15.astype(np.int64)>=a[ix].astype(np.int64)+120)
 goodS=cov30&cov15&(mx_a.astype(np.int64)<a[ix].astype(np.int64)+100)&(mn_a15.astype(np.int64)<=b[ix].astype(np.int64)-120)
 if np.any(goodB&goodS):raise AssertionError('future labels contradictory at same quote')
 good=goodB|goodS
 # One original side per future-good raw timestamp, independently from lane.
 eligible_ix=np.flatnonzero(good);raw_ix=ix[eligible_ix]
 side=np.where(goodB[eligible_ix],1,-1).astype(np.int8)
 maxcap=np.where(a[raw_ix]-b[raw_ix]<=1500,1500,4000).astype(np.int32)
 scenario=[]; fills=[];exits=[];nets=[]
 for lag in LAGS:
  for slip in SLIPS:
   # Run both caps to correctly preserve the lane-specific <=$1.50 fill gate
   # even when a signal at initial $1.50 can see widened spread after delay.
   c15,f15,e15x,n15=r14_eval_caps(t,b,a,raw_ix,side,lag,slip,1500)
   c40,f40,e40x,n40=r14_eval_caps(t,b,a,raw_ix,side,lag,slip,4000)
   scenario.append((c15,c40));fills.append((f15,f40));exits.append((e15x,e40x));nets.append((n15,n40))
 source_rows=[];qrows=[];traces=[]
 for lane in LANES:
  choose=lanes[lane][eligible_ix]
  isbase=lane in ('BASE_250_1500','DENSE_1500')
  ci=0 if isbase else 1
  mat=np.stack([p[ci] for p in scenario],axis=1)
  ext=np.stack([p[ci] for p in exits],axis=1)
  fl=np.stack([p[ci] for p in fills],axis=1)
  success=(mat==1).sum(axis=1)
  # Worst observed occupancy including failed/censored filled scenarios must
  # take full30s after delayed fill. No rejected order gets a fake position.
  worst=np.full(len(eligible_ix),-1,np.int64)
  for z in range(len(eligible_ix)):
   e=int(t[raw_ix[z]]+1)
   for j in range(9):
    if mat[z,j]==1:e=max(e,int(t[ext[z,j]]))
    elif mat[z,j] in (0,-3) and fl[z,j]>=0:e=max(e,int(t[fl[z,j]]+30000))
   worst[z]=e
  for tier,need in TIERS:
   ok=choose&(success>=need)
   m=quarter_metrics(t,raw_ix,ok,worst,success,need)
   ids=np.flatnonzero(ok)
   sel=greedy_nonoverlap(t[raw_ix[ids]],worst[ids]); chosen=ids[sel]
   hour={'source':name,'lane':lane,'tier':tier,'required_robust_success_scenarios':need,
     'raw_sha256':pin,'full_original_hour_R9_SYNTH_reference':104,
     'source_original_STRICT15_SAFE30_future_good_events':int(good.sum()),
     'lane_original_strict_candidate_count':int(choose.sum()),
     'latency_robust_candidates':int(ok.sum()),
     'globally_selected_nonoverlap_worst_scenario_reservation':int(len(chosen)),
     'hour_coverage_by_selected_count':int(len(chosen)>=104),
     'independent_quarters_feasible':int(sum(not x['provably_unattainable_under_THIS_changed_envelope'] for x in m)),
     'full_hour_selected_accuracy_is_ORACLE':True,
     'original_15s_favorable_and_full30_zero_adverse_intact':True,
     'all_stress_outcomes_causal_feature':False,
     'live_or_OOS_prediction_qualified':False}
   source_rows.append(hour)
   for q,v in enumerate(m):
    cnt=int(np.count_nonzero((t[raw_ix[chosen]]>=r13.T0+q*900000)&(t[raw_ix[chosen]]<r13.T0+(q+1)*900000)))
    qrows.append({**{k:hour[k] for k in ('source','lane','tier','required_robust_success_scenarios')},**v,
      'globally_selected_entries_in_quarter':cnt,'global_selection_meets_quarter':bool(cnt>=REFERENCE[q])})
   for z in chosen:
    i=int(raw_ix[z]);q=int((t[i]-r13.T0)//900000)
    traces.append({'source':name,'lane':lane,'tier':tier,'signal_source_quote_ix':i,
      'signal_utc_ms':int(t[i]),'quote_bid_raw':int(b[i]),'quote_ask_raw':int(a[i]),
      'buy_1_sell_minus1_FUTURE_KNOWN':int(side[z]),'strict_success_of_9_lag_slip':int(success[z]),
      'worst_scenario_observed_occupation_end_utc_ms':int(worst[z]),
      'entry_quarter_idx':q,'hindsight_only':True})
   # Compact all candidate outcome matrices retained separately; nothing is
   # reselected after latency for the original future-known signal.
  # All original future good candidate outcomes, not just selected trades.
  np.savez_compressed(ROOT/'results'/f'R14_{name}_{lane}_COMPLETE_CANDIDATE_STRESS_MATRIX.npz',
    source_raw_quote_index=raw_ix[choose],entry_time_utc_ms=t[raw_ix[choose]],
    future_selected_side=side[choose],nine_scenario_outcome=mat[choose],
    nine_scenario_fill_quote_index=fl[choose],nine_scenario_exit_quote_index=ext[choose],
    worst_case_occupied_until_utc_ms=worst[choose],successful_scenario_count=success[choose])
 return source_rows,qrows,traces,{'source':name,'sha256':pin,'halo_quote_count':len(t),'original_strict_good_universe':int(good.sum()),'asof_spread_up_to4_observed_candidates':len(ix)}


def r14_eval_caps(t,b,a,ix,side,lag,slip,cap):
 return evaluate_independent_stress(t,b,a,ix,side,cap,lag,slip)


def writecsv(p,rows):
 if not rows:raise ValueError('NO_ROWS')
 with p.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for buf in iter(lambda:f.read(1<<20),b''):h.update(buf)
 return h.hexdigest()


def run():
 out=ROOT/'results';out.mkdir(exist_ok=True)
 allh=[];allq=[];allt=[];sr=[]
 for name in r13.EXPECTED:
  h,q,t,rec=source_replay(name);allh+=h;allq+=q;allt+=t;sr.append(rec)
  print(json.dumps({'source':name,'completed_source_hours':len(h),'complete_quarter_results':len(q),
                    'source_raw_quote_sha256':rec['sha256']}),flush=True)
 assert len(allh)==3*len(LANES)*len(TIERS) and len(allq)==4*len(allh)
 writecsv(out/'R14_ALL_72_SOURCE_LANE_ROBUSTNESS_HOURS.csv',allh)
 writecsv(out/'R14_ALL_288_SOURCE_LANE_ROBUSTNESS_QUARTERS.csv',allq)
 writecsv(out/'R14_ALL_SELECTED_ORIGINAL_QUOTE_ORDINALS.csv',allt)
 proof={'source_sha256':sr,'hours':len(allh),'quarters':len(allq),
        'original_reference_quarters':list(REFERENCE),
        'nine_fixed_stress_scenarios':[(l,s) for l in LAGS for s in SLIPS],
        'full_30_second_original_strict_adverse':'never weakened',
        'favorable_original_15s':'never weakened',
        'research_status':'RETROSPECTIVE FUTURE-LABEL AND ROBUSTNESS-ORACLE ONLY; NOT CAUSAL; NO ACCOUNT PNL; NO LIVE'}
 (out/'R14_RECEIPT.json').write_text(json.dumps(proof,indent=2,allow_nan=False)+'\n')
 manifest={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file() and p.name!='R14_MANIFEST.json'}
 (out/'R14_MANIFEST.json').write_text(json.dumps({'sources':sr,'members':manifest},indent=2)+'\n')
 return proof

if __name__=='__main__':print(json.dumps(run(),indent=2),flush=True)
