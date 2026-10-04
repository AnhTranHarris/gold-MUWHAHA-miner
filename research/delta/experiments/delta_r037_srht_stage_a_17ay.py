from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit

DAY=86400000;TICK=10;SCALE=1000;END=1768737600000
US=1772953200000;UK=1774746000000;P75=np.asarray([20,20,21,21],np.int64)
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
PREREG='7b1ad1caf90a72cd5f9593d1e18c57250d7b4202'
MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);q=None
 try:
  with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=p.parent,prefix='.'+p.name+'.',suffix='.tmp',delete=False) as f:
   q=f.name;json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(q,p);q=None
 finally:
  if q:
   try:os.unlink(q)
   except FileNotFoundError:pass

def sess(t):
 tod=t%DAY;ls=np.where(t>=UK,7,8)*3600000;le=ls+30600000;ns=np.where(t>=US,12,13)*3600000;ne=ns+32400000
 il=(tod>=ls)&(tod<le);ny=(tod>=ns)&(tod<ne)
 return np.where(il&ny,2,np.where(il,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[sess(t)]*TICK;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK)//(2*TICK))*TICK
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def m1(t,mid):
 buck=t//60000;st=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];en=np.r_[st[1:],len(t)]
 return {
  'start':st.astype(np.int64),
  'end_ms':((buck[st]+1)*60000).astype(np.int64),
  'open':mid[st].astype(np.int64),
  'high':np.maximum.reduceat(mid,st).astype(np.int64),
  'low':np.minimum.reduceat(mid,st).astype(np.int64),
  'close':mid[en-1].astype(np.int64)
 }

def signals(t,b):
 hi,lo,cl,end=b['high'],b['low'],b['close'],b['end_ms'];n=len(cl)
 ph=[];pl=[]
 for k in range(2,n-2):
  if hi[k]>hi[k-1] and hi[k]>hi[k-2] and hi[k]>hi[k+1] and hi[k]>hi[k+2]:ph.append((k+2,int(hi[k])))
  if lo[k]<lo[k-1] and lo[k]<lo[k-2] and lo[k]<lo[k+1] and lo[k]<lo[k+2]:pl.append((k+2,int(lo[k])))
 ei=[];es=[];lev=[];kind=[]
 ih=il=0;lh=ll=0;hused=lused=True
 for i in range(n-1):
  while ih<len(ph) and ph[ih][0]<i:
   lh=ph[ih][1];hused=False;ih+=1
  while il<len(pl) and pl[il][0]<i:
   ll=pl[il][1];lused=False;il+=1
  if ll and not lused and lo[i]<ll and cl[i]>ll:
   lused=True
   if lo[i+1]<=ll and cl[i+1]>ll:
    j=int(np.searchsorted(t,end[i+1],side='left'))
    if j<len(t):ei.append(j);es.append(1);lev.append(ll);kind.append(1)
  if lh and not hused and hi[i]>lh and cl[i]<lh:
   hused=True
   if hi[i+1]>=lh and cl[i+1]<lh:
    j=int(np.searchsorted(t,end[i+1],side='left'))
    if j<len(t):ei.append(j);es.append(-1);lev.append(lh);kind.append(-1)
 if not ei:return np.empty(0,np.int64),np.empty(0,np.int8),np.empty(0,np.int64),np.empty(0,np.int8)
 o=np.argsort(np.asarray(ei,np.int64),kind='stable')
 return np.asarray(ei,np.int64)[o],np.asarray(es,np.int8)[o],np.asarray(lev,np.int64)[o],np.asarray(kind,np.int8)[o]

@njit(cache=True)
def qt(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def evaltr(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=dn=lg=sh=w=st=mh=en=0;gp=gl=net=0.;days=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;days[dn]=int(t[i]//DAY);dn+=1
  entry=int(ask[i]) if s>0 else int(bid[i]);stop=qt(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);sec=int(t[k])//1000;last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if sec-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
    if (s>0 and ns>stop) or (s<0 and ns<stop):stop=ns
  else:
   aa=int(ask[last]);bb=int(bid[last]);raw=((bb-entry) if s>0 else (entry-aa))/SCALE
  ex=raw-.01;net+=ex-.01;w+=ex>1e-12
  if raw>0:gp+=ex
  else:gl+=ex
  if reason==0:st+=1
  elif reason==1:mh+=1
  else:en+=1
  busy=last
 d=0
 if dn:
  x=np.sort(days[:dn]);d=1
  for k in range(1,x.size):d+=x[k]!=x[k-1]
 return tr,bs,sr,d,lg,sh,w,gp,gl,net,st,mh,en

def qs(x):
 if len(x)==0:return {}
 q=np.quantile(x,[.1,.25,.5,.75,.9,.99]);return dict(zip(['p10','p25','p50','p75','p90','p99'],map(float,q)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();h=sha(a.source)
 if h!=SHA:raise SystemExit('canonical January SHA mismatch: '+h)
 d=pd.read_csv(a.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit('Stage-A chronology/tick mismatch')
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);native=ar+br;ea,eb=p75(t,ar,br);b=m1(t,native);idx,side,level,kind=signals(t,b)
 tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaltr(idx,side,t,ea,eb)
 met={'signals':int(idx.size),'busy_skips':int(bs),'spread_rejects':int(sr),'trades':int(tr),'distinct_days':int(nd),'long':int(lg),'short':int(sh),'official_wins':int(w),'gross_profit':round(float(gp),2),'gross_loss':round(float(gl),2),'direct_net_usd':round(float(net),2),'exit_reasons':{'STOP':int(st),'MAX_HOLD':int(mh),'END':int(en)}}
 gate={'minimum_trades_20':tr>=20,'minimum_distinct_days_5':nd>=5,'direct_net_min_minus_1':met['direct_net_usd']>=-1.};gate['screen_pass']=all(gate.values());gate['strong_pass']=gate['screen_pass'] and met['direct_net_usd']>=0
 if gate['screen_pass']:leader='C01_M1_SWEEP_RECLAIM_RETEST';decision='ADVANCE_SRHT_C01_INDEPENDENT_LATER_JAN_VALIDATION';nxt='R037_SRHT_C01_INDEPENDENT_LATER_JAN_VALIDATION'
 else:leader=None;decision='RETIRE_SRHT_STAGE_A_NO_EXECUTABLE_SURVIVOR';nxt='R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST'
 et=t[idx] if idx.size else np.empty(0,np.int64);g=np.diff(et).astype(np.float64)/1000 if et.size>1 else np.empty(0)
 out={'schema':'delta-r037-srht-stage-a-screen-17ay-v1','status':'COMPLETE_STAGE_A_SCREEN','unit':'R037_SWEEP_RECLAIM_HOLD_RETEST_STAGE_A_SCREEN','family':'R037-SRHT-v1','parent_checkpoint':'R037_LMJF_STAGE_A_SCREEN_CHECKPOINT_17AX','prereg_commit':PREREG,'source_sha256':h,'stage_a_ticks':int(len(t)),'signal_surface':'NATIVE_DUKAS_M1_MID','execution_surface':'DUKAS_COINEXX_LIKE_P75','signal_spec':{'bar_seconds':60,'swing_width_each_side':2,'pivot_known_before_sweep_bar':True,'sweep_close_reclaim':True,'next_bar_retest_hold':True,'profile':'fade failed breakout after confirmed retest hold'},'numeric_retuning':False,'august_accessed':False,'diagnostics':{'m1_bars':int(len(b['close'])),'signals':int(idx.size),'signals_per_day':float(idx.size/14),'inter_event_seconds_quantiles':qs(g)},'configs':{'C01_M1_SWEEP_RECLAIM_RETEST':{'metrics':met,'gate':gate}},'finding':{'leading_config':leader,'decision':decision,'next':nxt},'mql5_authorized':False}
 atomic(a.output,out);print(json.dumps({'diagnostics':out['diagnostics'],'metrics':met,'gate':gate,'finding':out['finding']},separators=(',',':')))

if __name__=='__main__':main()
