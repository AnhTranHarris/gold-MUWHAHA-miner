"""R18 ADDITIVE source-exact two-feed H1V2 experimental hindsight research.

No existing R9/R11-R17 source is changed. As-of candidate features/watches are
strictly past/now. Offline first-passage teacher and interval scheduling use
future quotes and ARE NOT predictive. Maintains separate ORIGINAL S1 strict
first15/full30 safety, distinct 15/30/45/60 first-TP-before-adverse diagnostics.
Bid/Ask cross, 0.001 quote-price units, $0.02 nominal quoted-price proxy fee.
No claim of real broker fills, margin, account cash PNL, or deployability.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,json,sys,time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

HERE=Path(__file__).resolve().parents[1]
UP=HERE/'upstream'
sys.path.insert(0,str(UP))
import r13_crossbroker_horizon_lanes as r13
import entry_survivability as s1

PINS={
 'MT5_BROKER_EXPORT':{
 '01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
 '02':'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
 '06':'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
 '07':'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d'},
 'DUKASCOPY_RAW':{
 '01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'},
}
OFFSETS={'01':-2,'02':-2,'06':-3,'07':-3}
R13_PIN='e90da8141639428d173d7587d44f251748130e690c1f5f754594727ba691ed7e'
S1_PIN='c52de41072911ad53dedadfb3dba1899ea112e41a9e58e48ea29a7903e3ec475'
FEE=20; TARGET=100; ADVERSE=100; FRESH=300000; MAX_GAP=15000
HORIZONS=(15000,30000,45000,60000)
LANES=('BASE_250_1500','DENSE_1500','WIDE_REQUOTE_4000',
       'R18_VOLATILITY_COMPENSATED','R18_WATCH60_SPREAD_PERSISTENCE',
       'R18_WATCH60_FLOW_RECOVERY','R18_100MS_BROKER_GRID',
       'R18_ADAPTIVE_UNION_4000','R18_WIDE_8000_FIRST250_DIAGNOSTIC',
       'R18_ALL_OBSERVED_4000_DIAGNOSTIC')
CONTRACTS=('ORIGINAL_S1_F15_SAFE30',
           'NEW_FIRST_TOUCH_15_BEFORE_ADVERSE','NEW_FIRST_TOUCH_30_BEFORE_ADVERSE',
           'NEW_FIRST_TOUCH_45_BEFORE_ADVERSE','NEW_FIRST_TOUCH_60_BEFORE_ADVERSE')

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()

def verify_upstreams():
 for p,pin in ((UP/'r13_crossbroker_horizon_lanes.py',R13_PIN),
               (UP/'entry_survivability.py',S1_PIN)):
  if sha(p)!=pin:raise ValueError('PINNED_UPSTREAM_DRIFT '+str(p))

def month_range(mon):
 y,m=2026,int(mon)
 t0=int(dt.datetime(y,m,1,tzinfo=dt.timezone.utc).timestamp()*1000)
 end=dt.datetime(y+1,1,1,tzinfo=dt.timezone.utc) if m==12 else dt.datetime(y,m+1,1,tzinfo=dt.timezone.utc)
 return t0,int(end.timestamp()*1000)

def read_raw(source,mon,root):
 if source=='MT5_BROKER_EXPORT':
  p=root/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
  if sha(p)!=PINS[source][mon]:raise ValueError('MT5_SOURCE_HASH_DRIFT '+mon)
  f=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'],
      dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=f.time_msc.to_numpy(np.int64)+OFFSETS[mon]*3600000
  b=np.rint(f.bid.to_numpy(np.float64)*1000).astype(np.int32)
  a=np.rint(f.ask.to_numpy(np.float64)*1000).astype(np.int32)
 else:
  p=root/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
  if sha(p)!=PINS[source][mon]:raise ValueError('DUKAS_SOURCE_HASH_DRIFT '+mon)
  f=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
      dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=f.timestamp_ms_utc.to_numpy(np.int64)
  b=f.bid_raw.to_numpy(np.int32);a=f.ask_raw.to_numpy(np.int32)
 del f
 if len(t)<100 or np.any(t[1:]<t[:-1]) or np.any(a<b) or np.any(b<=0):
  raise ValueError('SOURCE_ORDER_OR_BIDASK_INVALID')
 return t,b,a,p

@njit(cache=False)
def first250_extra_above4(t,b,a):
 """Only new first-250ms quote >$4-8 after observed continuous 300s epoch.
 Earlier upstream R13 first<=4 source remains byte-for-byte unchanged.
 """
 n=len(t);selected=np.empty(n,np.int64);k=0;epoch=t[0];prev_bin=-1
 for i in range(n):
  if i and t[i]-t[i-1]>MAX_GAP:epoch=t[i]
  binid=t[i]//250;first=binid!=prev_bin;prev_bin=binid
  s=a[i]-b[i]
  if first and t[i]-epoch>=FRESH and 4000<s<=8000 and (i==0 or t[i]!=t[i-1]):
   selected[k]=i;k+=1
 return selected[:k]

@njit(cache=False)
def watch_states(t,b,a,ix,flags,ema15,ema300,m3b,m3a,v15,v60):
 """Two nontrading, as-of spread/flow state machines; next observed quote only.
 Reset if a raw quote gap is hidden between eligible candidates, not just if
 the candidate-to-candidate time difference >15s.
 """
 n=len(t);cum=np.zeros(n,np.int32)
 for i in range(1,n):cum[i]=cum[i-1]+(1 if t[i]-t[i-1]>MAX_GAP else 0)
 m=len(ix);w0=np.zeros(m,np.bool_);w1=np.zeros(m,np.bool_)
 active=np.zeros(2,np.bool_);born=np.zeros(2,np.int64);seed=np.zeros(2,np.int32)
 streak=np.zeros(2,np.int32);prev=0;starts=np.zeros(2,np.int64)
 confirms=np.zeros(2,np.int64);expires=np.zeros(2,np.int64);resets=np.zeros(2,np.int64)
 for k in range(m):
  i=ix[k];now=t[i];s=int(a[i])-int(b[i]);fresh=(k==0 or cum[i]==cum[prev])
  for z in range(2):
   if active[z] and not fresh:
    active[z]=False;streak[z]=0;resets[z]+=1
   if active[z] and now-born[z]>60000:
    active[z]=False;streak[z]=0;expires[z]+=1
   if active[z] and 250<=now-born[z]<=60000:
    # Prior actually observed spread and motion. Never future best quote.
    volbase=max(float(v15[k]),float(v60[k])*.5,float(ema300[i]))
    if z==0:
     good=(s<=4000 and 4*s<=3*seed[z] and s<=1.6*volbase
           and ema15[i]<=ema300[i])
    else:
     coherent=(m3b[i]>0 and m3a[i]>0) or (m3b[i]<0 and m3a[i]<0)
     good=(s<=4000 and 5*s<=4*seed[z] and ema15[i]<=ema300[i]
           and coherent and float(v60[k])>=.6*s and
           min(abs(m3b[i]),abs(m3a[i]))>=.5*s)
    if good:streak[z]+=1
    else:streak[z]=0
    if streak[z]>=2:
     if z==0:w0[k]=True
     else:w1[k]=True
     confirms[z]+=1;active[z]=False;streak[z]=0
   if not active[z] and (flags[k]&1)!=0 and 1600<=s<=8000:
    trigger=(z==0 or ema15[i]>=ema300[i])
    if trigger:active[z]=True;born[z]=now;seed[z]=s;streak[z]=0;starts[z]+=1
  prev=i
 return w0,w1,starts,confirms,expires,resets

def preentry_volatility(t,b,a,ix):
 """Observed quote at/before 15s and 60s ago; no future observation."""
 now=t[ix]
 l15=np.searchsorted(t,now-15000,side='right')-1
 l60=np.searchsorted(t,now-60000,side='right')-1
 l15=np.clip(l15,0,len(t)-1);l60=np.clip(l60,0,len(t)-1)
 mid=b[ix].astype(np.int64)+a[ix].astype(np.int64)
 v15=(np.abs(mid-(b[l15].astype(np.int64)+a[l15].astype(np.int64)))//2).astype(np.int32)
 v60=(np.abs(mid-(b[l60].astype(np.int64)+a[l60].astype(np.int64)))//2).astype(np.int32)
 return v15,v60

def candidate_lanes(t,b,a):
 ix0,fl0,e300,e15,m3b,m3a=r13.prefix_candidates(t,b,a)
 extra=first250_extra_above4(t,b,a)
 ix=np.sort(np.r_[ix0,extra])
 if len(ix)!=len(np.unique(ix)):raise RuntimeError('CANDIDATE_DUPLICATE')
 flags=np.zeros(len(ix),np.int8)
 orig=np.searchsorted(ix,ix0)
 flags[orig]=fl0
 if len(extra):flags[np.searchsorted(ix,extra)]=1
 s=a[ix].astype(np.int64)-b[ix].astype(np.int64)
 v15,v60=preentry_volatility(t,b,a,ix)
 first=(flags&1)!=0;anyclock=(flags&3)!=0
 # A clock is causal at this actual quote; no assumption previous bin had quote.
 is100=(t[ix]//100 != np.where(ix>0,t[np.maximum(0,ix-1)]//100,-1))
 base=first&(s<=1500)
 dense=s<=1500
 wide=anyclock&(s<=4000)
 volbase=np.maximum(np.maximum(v15.astype(np.float64),.5*v60),1.5*e300[ix])
 vol=anyclock&(s<=4000)&(s<=.8*volbase)&(e15[ix]<=1.2*e300[ix])
 w0,w1,starts,confirms,expires,resets=watch_states(t,b,a,ix,flags,e15,e300,m3b,m3a,v15,v60)
 g100=is100&(s<=4000)&(s<=np.maximum(1800,1.5*e300[ix]))
 union=base|vol|w0|w1|g100
 # >=$4 is diagnostic only: force original first250 quote, pay true spread.
 wide8=first&(s<=8000)
 lanes={
  'BASE_250_1500':base,
  'DENSE_1500':dense,
  'WIDE_REQUOTE_4000':wide,
  'R18_VOLATILITY_COMPENSATED':vol,
  'R18_WATCH60_SPREAD_PERSISTENCE':w0,
  'R18_WATCH60_FLOW_RECOVERY':w1,
  'R18_100MS_BROKER_GRID':g100,
  'R18_ADAPTIVE_UNION_4000':union,
  'R18_WIDE_8000_FIRST250_DIAGNOSTIC':wide8,
  'R18_ALL_OBSERVED_4000_DIAGNOSTIC':s<=4000}
 if tuple(lanes)!=LANES:raise RuntimeError('LANE_SCHEMA_MISMATCH')
 return ix,lanes,{'original_r13_prefix_count':int(len(ix0)),
    'new_gt4_first250_count':int(len(extra)),
    'watch_starts':starts.tolist(),'watch_confirmed':confirms.tolist(),
    'watch_expired':expires.tolist(),'watch_gap_reset':resets.tolist(),
    'v15_proxy_not_realized_future':True,'v60_proxy_not_realized_future':True}

@njit(cache=False)
def make_segment_trees(b,a):
 """Exact original observed quote extrema; query no fabricated intermediate marks."""
 n=len(b);base=1
 while base<n:base*=2
 maxb=np.full(2*base,-2147483647,np.int32)
 mina=np.full(2*base,2147483647,np.int32)
 minb=np.full(2*base,2147483647,np.int32)
 maxa=np.full(2*base,-2147483647,np.int32)
 for i in range(n):
  maxb[base+i]=b[i];minb[base+i]=b[i];mina[base+i]=a[i];maxa[base+i]=a[i]
 for j in range(base-1,0,-1):
  maxb[j]=max(maxb[2*j],maxb[2*j+1]);minb[j]=min(minb[2*j],minb[2*j+1])
  mina[j]=min(mina[2*j],mina[2*j+1]);maxa[j]=max(maxa[2*j],maxa[2*j+1])
 return base,maxb,mina,minb,maxa

@njit(cache=False)
def first_ge(tree,node,lo,hi,left,right,value):
 if right<=lo or hi<=left or tree[node]<value:return -1
 if hi-lo==1:return lo
 mid=(lo+hi)//2
 j=first_ge(tree,node*2,lo,mid,left,right,value)
 if j>=0:return j
 return first_ge(tree,node*2+1,mid,hi,left,right,value)

@njit(cache=False)
def first_le(tree,node,lo,hi,left,right,value):
 if right<=lo or hi<=left or tree[node]>value:return -1
 if hi-lo==1:return lo
 mid=(lo+hi)//2
 j=first_le(tree,node*2,lo,mid,left,right,value)
 if j>=0:return j
 return first_le(tree,node*2+1,mid,hi,left,right,value)

@njit(cache=False)
def independent_competing_firstpass(t,b,a,ix,limits,starts,base,maxb,mina,minb,maxa):
 """Full 60s first crossing for BOTH sides, never choose side from future on a live path.
 Return ordinal of first executable target, ordinal of first -0.10 opening-liq
 adverse. First favorable must strictly precede adverse and all unobserved gaps.
 """
 m=len(ix);ftb=np.full(m,-1,np.int32);fts=np.full(m,-1,np.int32)
 fab=np.full(m,-1,np.int32);fas=np.full(m,-1,np.int32)
 for k in range(m):
  i=int(ix[k]);lo=int(starts[k]);hi=int(limits[k])
  if lo>=hi:continue
  ftb[k]=first_ge(maxb,1,0,base,lo,hi,int(a[i])+FEE+TARGET)
  fts[k]=first_le(mina,1,0,base,lo,hi,int(b[i])-FEE-TARGET)
  # At the exact adverse barrier, failure is observed (<=BUY / >=SELL).
  fab[k]=first_le(minb,1,0,base,lo,hi,int(b[i])-ADVERSE)
  fas[k]=first_ge(maxa,1,0,base,lo,hi,int(a[i])+ADVERSE)
 return ftb,fts,fab,fas

def first_pass_labels(t,b,a,ix):
 starts=np.searchsorted(t,t[ix],side='right').astype(np.int32)
 limits=np.searchsorted(t,t[ix]+60000,side='right').astype(np.int32)
 base,maxb,mina,minb,maxa=make_segment_trees(b,a)
 ftb,fts,fab,fas=independent_competing_firstpass(t,b,a,ix,limits,starts,base,maxb,mina,minb,maxa)
 # Source complete & observed gap-free until actual first TP; do not label a
 # target reached across a >15-second unobserved source hole as success.
 pref=np.r_[0,np.cumsum((np.diff(t)>MAX_GAP).astype(np.int32),dtype=np.int32)]
 def valid_hit(hits,adverse):
  ok=hits>=0
  safe_idx=hits.clip(min=0)
  ok &= (adverse<0)|(hits<adverse)
  ok &= (pref[safe_idx]==pref[ix])
  return ok
 goodb=valid_hit(ftb,fab);goods=valid_hit(fts,fas)
 return {'BUY_tp':ftb,'SELL_tp':fts,'BUY_adverse':fab,'SELL_adverse':fas,
   'BUY_good':goodb,'SELL_good':goods,
   'source_last_time':int(t[-1]),'all_candidates':len(ix)}

def original_s1_labels(t,b,a,ix):
 # Frozen original independently SHA-guarded R11 helper; NOT reimplemented.
 m15,x15,a15,y15,_,_,c15=s1._rolling_extrema(t,b,a,ix,15000)
 m30,x30,a30,y30,_,_,c30=s1._rolling_extrema(t,b,a,ix,30000)
 gB=c15&c30&(x15.astype(np.int64)>=a[ix].astype(np.int64)+120)&(m30.astype(np.int64)>b[ix].astype(np.int64)-100)
 gS=c15&c30&(a15.astype(np.int64)<=b[ix].astype(np.int64)-120)&(y30.astype(np.int64)<a[ix].astype(np.int64)+100)
 if np.any(gB&gS):raise RuntimeError('IMMUTABLE_S1_DUAL_STRICT_SIDES')
 return gB,gS

@njit(cache=False)
def _greedy_future_interval_order(starts,endtimes,order):
 """Compiled exact earliest-finish maximization; strict nonoverlap."""
 chosen=np.empty(len(order),np.int32)
 n=0;last=np.int64(-9223372036854775807)
 for z in range(len(order)):
  k=order[z]
  if starts[k]>last:
   chosen[n]=k;n+=1;last=endtimes[k]
 return chosen[:n]

def selected_count(t,ix,mask,goodB,goodS,tpB,tpS,horizon_ms=None):
 """Exact earliest-finish future-informed interval cardinality with two sides.
 One observed entry quote cannot open both sides; greedy nonoverlap enforces
 one-position globally. Both good sides at same entry may compete offline.
 """
 idxB=np.flatnonzero(mask&goodB)
 idxS=np.flatnonzero(mask&goodS)
 # Note candidate side / entry pairing remains original quote ordinal.
 ids=np.r_[idxB,idxS]
 side=np.r_[np.ones(len(idxB),dtype=np.int8),-np.ones(len(idxS),dtype=np.int8)]
 ends=np.r_[tpB[idxB],tpS[idxS]]
 if not len(ids):return np.empty(0,np.int32),np.empty(0,np.int8),np.empty(0,np.int32),0
 if np.any(ends<0):raise RuntimeError('SELECTED_WITHOUT_FAVORABLE_QUOTE')
 starts=t[ix[ids]];endtimes=t[ends]
 if horizon_ms is not None and np.any(endtimes>starts+horizon_ms):raise RuntimeError('FAVORABLE_HORIZON_INVALID')
 order=np.lexsort((ids,starts,endtimes))
 # Sorting finish times gives exact max cardinality of historical favorable
 # disjoint quote intervals, NOT a feasible as-of scheduling algorithm.
 take=_greedy_future_interval_order(starts,endtimes,order)
 return ids[take].astype(np.int32),side[take],ends[take].astype(np.int32),len(ids)

def calendar_counts(t,ix,ids,refs,source_mon_start):
 qkeys=refs['qkeys'];qref=refs['qref']
 keys=(t[ix[ids]]//900000)-qkeys[0]
 if np.any(keys<0) or np.any(keys>=len(qkeys)):raise RuntimeError('ENTRY_OUTSIDE_SOURCE_CALENDAR')
 counts=np.bincount(keys,minlength=len(qkeys)).astype(np.int32)
 if len(counts)!=len(qref):raise RuntimeError('R9_QUOTA_LENGTH_MISMATCH')
 hr=counts.reshape(-1,4).sum(axis=1)
 return counts,hr

def refs_for_month(month,root):
 p=root/'R12DQ_COMPLETE_ALL_11520_SOURCE_QUARTERS_S4_R12_R12DQ.csv'
 if not p.exists():raise FileNotFoundError('ORIGINAL_QUARTER_REF_ABSENT '+str(p))
 with p.open(newline='') as f:rows=[r for r in csv.DictReader(f) if r['month']=='2026-'+month]
 expected={'01':2976,'02':2688,'06':2880,'07':2976}[month]
 if len(rows)!=expected:raise RuntimeError('FROZEN_QUOTA_CALENDAR_INCOMPLETE')
 ts=np.array([int(dt.datetime.strptime(r['utc_quarter'],'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp()*1000)//900000 for r in rows],np.int64)
 refs=np.array([int(r['original_R9_SYNTH_15min_reference']) for r in rows],np.int32)
 if np.any(np.diff(ts)!=1) or int(refs.sum())!={'01':27980,'02':33523,'06':31758,'07':24324}[month]:
  raise RuntimeError('ORIGINAL_R9_SYNTH_UTC_REFERENCE_DRIFT')
 return {'qkeys':ts,'qref':refs,'href':refs.reshape(-1,4).sum(axis=1),'rows':rows,
         'sha256':sha(p)}

def write_csv(path,rows):
 if not rows:raise ValueError('NO_ROWS')
 with open(path,'w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

def source_month(source,mon,root,out):
 verify_upstreams();tic=time.monotonic();out.mkdir(parents=True,exist_ok=True)
 t,b,a,p=read_raw(source,mon,root);refs=refs_for_month(mon,root)
 lo,hi=month_range(mon)
 ix,lanes,admission=candidate_lanes(t,b,a)
 eligible=(t[ix]>=lo)&(t[ix]<hi)
 ix=ix[eligible];lanes={k:v[eligible] for k,v in lanes.items()}
 # Exact original 15s/fulls30 benchmark first, then new 15-60 competing risk.
 gb0,gs0=original_s1_labels(t,b,a,ix)
 paths=first_pass_labels(t,b,a,ix)
 results=[];qr=[];hr=[];traces={}
 masks=[('ORIGINAL_S1_F15_SAFE30',gb0,gs0,15000)]+[
  (f'NEW_FIRST_TOUCH_{h//1000}_BEFORE_ADVERSE',
   paths['BUY_good']&(paths['BUY_tp']>=0)&(t[paths['BUY_tp'].clip(min=0)]<=t[ix]+h),
   paths['SELL_good']&(paths['SELL_tp']>=0)&(t[paths['SELL_tp'].clip(min=0)]<=t[ix]+h),h)
  for h in HORIZONS]
 for lane,lmask in lanes.items():
  for contract,qualB,qualS,h in masks:
   ids,side,exitord,allgood=selected_count(t,ix,lmask,qualB,qualS,
    paths['BUY_tp'],paths['SELL_tp'],h)
   if len(ids) and np.any(t[ix[ids[1:]]] <= t[exitord[:-1]]):raise RuntimeError('ONE_POSITION_OVERLAP')
   countq,counth=calendar_counts(t,ix,ids,refs,lo)
   qref=refs['qref'];href=refs['href']
   qa=(qref>0);ha=(href>0)
   quarter_met=int(np.sum(qa&(countq>=qref)));hour_met=int(np.sum(ha&(counth>=href)))
   row={'source':source,'month':'2026-'+mon,'lane':lane,'contract':contract,
    'horizon_ms':h,'source_sha256':PINS[source][mon],
    'candidate_asof_admitted':int(lmask.sum()),'future_eligible_actions_BUY_SELL':int(allgood),
    'hindsight_firstTP_selected_onepos':len(ids),
    'original_R9_UTC_ref_count':int(qref.sum()),
    'active_quarters':int(qa.sum()),'15m_quota_met':quarter_met,
    'active_hours':int(ha.sum()),'hourly_quota_met':hour_met,
    'strict_original_only':contract=='ORIGINAL_S1_F15_SAFE30',
    'new_contract_future_selected_hindsight_only':True,
    'MT5_broker_export_not_validated_dealer_fills':source=='MT5_BROKER_EXPORT',
    'risk_fee_proxy_only_no_account_cash_or_mql5_live':True}
   results.append(row)
   for q,x in enumerate(countq):
    qr.append({'source':source,'month':'2026-'+mon,'lane':lane,'contract':contract,
       'utc_quarter':refs['rows'][q]['utc_quarter'],'r9_SYNTH_original_ref':int(qref[q]),
       'hindsight_selected':int(x),'meets_active_quarter':int(x>=qref[q]) if qref[q] else '',
       'miss':max(0,int(qref[q]-x)),'strict_original_only':row['strict_original_only']})
   for k,x in enumerate(counth):
    hr.append({'source':source,'month':'2026-'+mon,'lane':lane,'contract':contract,
       'utc_hour':refs['rows'][4*k]['utc_hour'],'r9_SYNTH_original_ref_hour':int(href[k]),
       'hindsight_selected':int(x),'meets_active_hour':int(x>=href[k]) if href[k] else '',
       'miss':max(0,int(href[k]-x)),'strict_original_only':row['strict_original_only']})
   key=f'{lane}__{contract}'
   # Exact source-ordinal selected entry/side/exit; no future path invented.
   traces[key+'_entry_ord']=ix[ids]
   traces[key+'_side_FUTURE_SELECTED']=side
   traces[key+'_firstTP_exit_ord']=exitord
   print(source,mon,lane,contract,len(ids),quarter_met,'/',int(qa.sum()),hour_met,'/',int(ha.sum()),flush=True)
 tag=f'R18_{source}_{mon}'
 qfile=out/f'{tag}_ALL_UTC_QUARTERS.csv';hfile=out/f'{tag}_ALL_UTC_HOURS.csv'
 rfile=out/f'{tag}_FULL_LANE_CONTRACT_RESULTS.csv';npz=out/f'{tag}_LOSSLESS_SELECTED_ORIGINAL_QUOTE_ORDINALS.npz'
 write_csv(qfile,qr);write_csv(hfile,hr);write_csv(rfile,results)
 np.savez_compressed(npz,**traces)
 receipt={'source':source,'month':mon,'source_path_basename':p.name,
 'original_source_sha256':PINS[source][mon], 'raw_quotes':len(t),
 'prefix_asof_eligible_candidate_quotes':len(ix),
 'historical_clock_hours_shift':OFFSETS[mon] if source=='MT5_BROKER_EXPORT' else 0,
 'clock_shift_empirically_derived_from_six_day_midpoint_alignment':True,
 'upstream_R13_sha256':R13_PIN,'upstream_R11S1_sha256':S1_PIN,
 'original_R9_quarter_ref_sha256':refs['sha256'],
 'original_15F30S_and_new_first_touch_labels_DISTINCT':True,
 'new_extended_horizon_only_until_firstTP_no_adverse_before_exit':True,
 'no_fake_lookahead_decision_training':True,'hindsight_selected_BUY_SELL_not_live':True,
 'model_realized_failed_trade_pnl_unknown':True,'mt5_dealer_fill_not_verified':True,
 'admission':admission, 'results':results,
 'output_files':{z.name:{'bytes':z.stat().st_size,'sha256':sha(z)} for z in (qfile,hfile,rfile,npz)},
 'elapsed_wall_seconds':round(time.monotonic()-tic,2),
 'research_status':'OFFLINE_FUTURE_SELECTED_COUNTS_ONLY_NO_PREDICTIVE_OR_DEPLOYABLE_APPROVAL'}
 receip=out/f'{tag}_SOURCE_VERIFIED_RECEIPT.json';receip.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=tuple(PINS),required=True)
 ap.add_argument('--month',choices=tuple(OFFSETS),required=True)
 ap.add_argument('--root',type=Path,default=Path('/mnt/data'))
 ap.add_argument('--output',type=Path,default=HERE/'results')
 ar=ap.parse_args();v=source_month(ar.source,ar.month,ar.root,ar.output)
 print(json.dumps({'success':True,'source':ar.source,'month':ar.month,
 'source_SHA':v['original_source_sha256'],'scenario_count':len(v['results']),
 'selected_max':max(x['hindsight_firstTP_selected_onepos'] for x in v['results'])},indent=2),flush=True)

if __name__=='__main__':main()
