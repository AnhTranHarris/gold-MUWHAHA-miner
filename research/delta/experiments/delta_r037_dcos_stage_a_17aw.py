from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
DAY_MS=86400000;TICK_RAW=10;SCALE=1000;END=1768737600000
US_DST=1772953200000;UK_DST=1774746000000;P75=np.asarray([20,20,21,21],np.int64)
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5';PREREG='fdc3ec8d81d9183ebd9f8985e513ac128797ec99'
DC_DEN=2000;MAX_SPREAD=250;STOP=300;TRAIL_ACT=100;TRAIL_DIST=30;MAX_HOLD=30

def file_sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def atomic_json(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);q=None
 try:
  with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=p.parent,prefix='.'+p.name+'.',suffix='.tmp',delete=False) as f:
   q=f.name;json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(q,p);q=None
 finally:
  if q:
   try:os.unlink(q)
   except FileNotFoundError:pass

def session(t):
 tod=t%DAY_MS;ls=np.where(t>=UK_DST,7,8)*3600000;le=ls+30600000;ns=np.where(t>=US_DST,12,13)*3600000;ne=ns+32400000
 il=(tod>=ls)&(tod<le);iny=(tod>=ns)&(tod<ne)
 return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,a,b):
 sp=P75[session(t)]*TICK_RAW;m=a.astype(np.int64)+b.astype(np.int64);bid=((m-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

@njit(cache=True)
def qtick(x):return ((int(x)+5)//10)*10

@njit(cache=True)
def events(t,a,b):
 n=t.size;idx=np.empty(n,np.int64);side=np.empty(n,np.int8);move=np.empty(n,np.int64);m=0
 x=int(a[0])+int(b[0]);hi=x;lo=x;state=0
 for i in range(1,n-1):
  x=int(a[i])+int(b[i])
  if state==0:
   if x>hi:hi=x
   if x<lo:lo=x
   if (x-lo)*DC_DEN>=lo:state=1;hi=x;idx[m]=i+1;side[m]=1;move[m]=x-lo;m+=1
   elif (hi-x)*DC_DEN>=hi:state=-1;lo=x;idx[m]=i+1;side[m]=-1;move[m]=hi-x;m+=1
  elif state>0:
   if x>hi:hi=x
   elif (hi-x)*DC_DEN>=hi:state=-1;lo=x;idx[m]=i+1;side[m]=-1;move[m]=hi-x;m+=1
  else:
   if x<lo:lo=x
   elif (x-lo)*DC_DEN>=lo:state=1;hi=x;idx[m]=i+1;side[m]=1;move[m]=x-lo;m+=1
 return idx[:m],side[:m],move[:m]

@njit(cache=True)
def evaltr(idx,side,t,ask,bid):
 busy=-1;tr=bs=sr=daysn=lg=sh=w=st=mh=en=0;gp=gl=net=0.;days=np.empty(idx.size,np.int64)
 for z in range(idx.size):
  i=int(idx[z]);s=int(side[z])
  if i<=busy:bs+=1;continue
  if int(ask[i]-bid[i])>MAX_SPREAD:sr+=1;continue
  tr+=1;lg+=s>0;sh+=s<0;days[daysn]=int(t[i]//DAY_MS);daysn+=1
  entry=int(ask[i]) if s>0 else int(bid[i]);stop=qtick(int(bid[i])-STOP if s>0 else int(ask[i])+STOP);sec0=int(t[i])//1000;raw=0.;reason=2;last=i
  for k in range(i+1,t.size):
   aa=int(ask[k]);bb=int(bid[k]);sec=int(t[k])//1000;last=k
   if s>0 and bb<=stop:raw=(bb-entry)/SCALE;reason=0;break
   if s<0 and aa>=stop:raw=(entry-aa)/SCALE;reason=0;break
   if sec-sec0>=MAX_HOLD:raw=((bb-entry) if s>0 else (entry-aa))/SCALE;reason=1;break
   fav=(bb-entry) if s>0 else (entry-aa)
   if fav>=TRAIL_ACT:
    ns=qtick(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
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
 if daysn:
  x=np.sort(days[:daysn]);d=1
  for k in range(1,x.size):d+=x[k]!=x[k-1]
 return tr,bs,sr,d,lg,sh,w,gp,gl,net,st,mh,en

def qs(x):
 if len(x)==0:return {}
 q=np.quantile(x,[.1,.25,.5,.75,.9,.99]);return dict(zip(['p10','p25','p50','p75','p90','p99'],map(float,q)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 h=file_sha(a.source)
 if h!=SHA:raise SystemExit('canonical January SHA mismatch: '+h)
 d=pd.read_csv(a.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);d=d[d.timestamp_ms_utc<END]
 t=d.timestamp_ms_utc.to_numpy(np.int64)
 if len(t)!=4205709 or np.any(t[1:]<t[:-1]):raise SystemExit('Stage-A chronology/tick mismatch')
 ar=d.ask_raw.to_numpy(np.int64);br=d.bid_raw.to_numpy(np.int64);ea,eb=p75(t,ar,br);idx,side,mv=events(t,ar,br)
 tr,bs,sr,nd,lg,sh,w,gp,gl,net,st,mh,en=evaltr(idx,side,t,ea,eb)
 met={'signals':int(idx.size),'busy_skips':int(bs),'spread_rejects':int(sr),'trades':int(tr),'distinct_days':int(nd),'long':int(lg),'short':int(sh),'official_wins':int(w),'gross_profit':round(float(gp),2),'gross_loss':round(float(gl),2),'direct_net_usd':round(float(net),2),'exit_reasons':{'STOP':int(st),'MAX_HOLD':int(mh),'END':int(en)}}
 gate={'minimum_trades_50':tr>=50,'minimum_distinct_days_6':nd>=6,'direct_net_min_minus_1':met['direct_net_usd']>=-1.0};gate['screen_pass']=all(gate.values());gate['strong_pass']=gate['screen_pass'] and met['direct_net_usd']>=0
 if gate['screen_pass']:leader='C01_DC_005_OVERSHOOT_CONTINUATION';decision='ADVANCE_DCOS_C01_INDEPENDENT_LATER_JAN_VALIDATION';nxt='R037_DCOS_C01_INDEPENDENT_LATER_JAN_VALIDATION'
 else:leader=None;decision='RETIRE_DCOS_STAGE_A_NO_EXECUTABLE_SURVIVOR';nxt='R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST'
 et=t[idx] if idx.size else np.empty(0,np.int64);g=np.diff(et).astype(np.float64)/1000 if et.size>1 else np.empty(0)
 out={'schema':'delta-r037-dcos-stage-a-screen-17aw-v1','status':'COMPLETE_STAGE_A_SCREEN','unit':'R037_DIRECTIONAL_CHANGE_OVERSHOOT_STAGE_A_SCREEN','family':'R037-DCOS-v1','parent_checkpoint':'R037_QRBM_STAGE_A_SCREEN_CHECKPOINT_17AV','prereg_commit':PREREG,'source_sha256':h,'stage_a_ticks':int(len(t)),'signal_surface':'NATIVE_DUKAS_BBO','execution_surface':'DUKAS_COINEXX_LIKE_P75','event_definition':{'directional_change_threshold_fraction':.0005,'threshold_pct':.05,'direction':'new directional-change trend / overshoot continuation','entry':'first strictly subsequent tick after causal confirmation'},'numeric_retuning':False,'august_accessed':False,'diagnostics':{'directional_change_signals':int(idx.size),'signals_per_day':float(idx.size/14),'confirmation_move_mid2_quantiles':qs(mv),'inter_event_seconds_quantiles':qs(g)},'configs':{'C01_DC_005_OVERSHOOT_CONTINUATION':{'metrics':met,'gate':gate}},'finding':{'leading_config':leader,'decision':decision,'next':nxt},'mql5_authorized':False}
 atomic_json(a.output,out);print(json.dumps({'metrics':met,'gate':gate,'finding':out['finding']},separators=(',',':')))
if __name__=='__main__':main()
