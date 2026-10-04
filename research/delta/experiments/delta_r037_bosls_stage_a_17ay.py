from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
DAY=86400000;TICK=10;SCALE=1000;END=1768737600000
US=1772953200000;UK=1774746000000;P75=np.asarray([20,20,21,21],np.int64)
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5';PREREG='34ef5741861a41f52807986260b86847005c759f'
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

def bars(t,mid,tf):
 bucket=t//tf;st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1];en=np.r_[st[1:],len(t)]
 return ((bucket[st]+1)*tf).astype(np.int64),mid[st].astype(np.int64),np.maximum.reduceat(mid,st).astype(np.int64),np.minimum.reduceat(mid,st).astype(np.int64),mid[en-1].astype(np.int64)

@njit(cache=True)
def events(t,end,o,h,l,c):
 n=len(c);idx=np.empty(n,np.int64);side=np.empty(n,np.int8);m=0
 prev_hi=0;prev_lo=0;cur_hi=0;cur_lo=0;trend=0
 for i in range(4,n):
  # SwingLength=5 means pivot center k=i-2 becomes knowable only when bar i closes.
  k=i-2
  ph=h[k]>h[k-1] and h[k]>h[k-2] and h[k]>h[k+1] and h[k]>h[k+2]
  pl=l[k]<l[k-1] and l[k]<l[k-2] and l[k]<l[k+1] and l[k]<l[k+2]
  if ph:
   newhi=int(h[k])
   if prev_hi>0 and newhi>prev_hi:trend=1
   cur_hi=newhi;prev_hi=newhi
  if pl:
   newlo=int(l[k])
   if prev_lo>0 and newlo<prev_lo:trend=-1
   cur_lo=newlo;prev_lo=newlo

  s=0
  if trend==1 and cur_lo>0 and int(l[i])<cur_lo and int(c[i])>cur_lo and int(c[i])>int(o[i]):
   s=1
  elif trend==-1 and cur_hi>0 and int(h[i])>cur_hi and int(c[i])<cur_hi and int(c[i])<int(o[i]):
   s=-1
  if s!=0:
   j=np.searchsorted(t,int(end[i]),side='left')
   if j<t.size:
    idx[m]=j;side[m]=s;m+=1
    trend=0
 return idx[:m],side[:m]

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

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();hsh=sha(a.source)
 if hsh!=SHA:raise SystemExit('canonical January SHA mismatch: '+hsh)
 d=pd.read_csv(a.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);d=d[d.timestamp_ms_utc<END];t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit('Stage-A chronology/tick mismatch')
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);native=ar+br;ea,eb=p75(t,ar,br);be,bo,bh,bl,bc=bars(t,native,300000);idx,sd=events(t,be,bo,bh,bl,bc)
 tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaltr(idx,sd,t,ea,eb)
 met={'signals':int(idx.size),'busy_skips':int(bs),'spread_rejects':int(sr),'trades':int(tr),'distinct_days':int(nd),'long':int(lg),'short':int(sh),'official_wins':int(w),'gross_profit':round(float(gp),2),'gross_loss':round(float(gl),2),'direct_net_usd':round(float(net),2),'exit_reasons':{'STOP':int(st),'MAX_HOLD':int(mh),'END':int(en)}}
 gate={'minimum_trades_20':tr>=20,'minimum_distinct_days_5':nd>=5,'direct_net_min_minus_1':met['direct_net_usd']>=-1.};gate['screen_pass']=all(gate.values());gate['strong_pass']=gate['screen_pass'] and met['direct_net_usd']>=0
 if gate['screen_pass']:leader='C01_M5_SWING5_BOS_SWEEP_RECLAIM';decision='ADVANCE_BOSLS_C01_INDEPENDENT_LATER_JAN_VALIDATION';nxt='R037_BOSLS_C01_INDEPENDENT_LATER_JAN_VALIDATION'
 else:leader=None;decision='RETIRE_BOSLS_STAGE_A_NO_EXECUTABLE_SURVIVOR';nxt='R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST'
 out={'schema':'delta-r037-bosls-stage-a-screen-17ay-v1','status':'COMPLETE_STAGE_A_SCREEN','unit':'R037_BOS_LIQUIDITY_SWEEP_RECLAIM_STAGE_A_SCREEN','family':'R037-BOSLS-v1','parent_checkpoint':'R037_LMJF_STAGE_A_SCREEN_CHECKPOINT_17AX','prereg_commit':PREREG,'source_sha256':hsh,'stage_a_ticks':int(len(t)),'signal_surface':'NATIVE_DUKAS_M5_MID','execution_surface':'DUKAS_COINEXX_LIKE_P75','signal_definition':{'timeframe_seconds':300,'swing_length':5,'trend':'HH bullish BOS / LL bearish BOS','event':'wick through opposing confirmed swing + close reclaim + directional candle','entry':'first P75 tick at/after completed bar right edge'},'numeric_retuning':False,'august_accessed':False,'diagnostics':{'m5_bars':int(len(bc)),'signals':int(idx.size),'signals_per_day':float(idx.size/14)},'configs':{'C01_M5_SWING5_BOS_SWEEP_RECLAIM':{'metrics':met,'gate':gate}},'finding':{'leading_config':leader,'decision':decision,'next':nxt},'mql5_authorized':False}
 atomic(a.output,out);print(json.dumps({'diagnostics':out['diagnostics'],'metrics':met,'gate':gate,'finding':out['finding']},separators=(',',':')))
if __name__=='__main__':main()
