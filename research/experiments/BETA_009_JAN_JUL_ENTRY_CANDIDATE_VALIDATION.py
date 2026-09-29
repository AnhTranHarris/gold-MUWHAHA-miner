from __future__ import annotations
import pandas as pd, numpy as np, json, hashlib, os, math, time
from pathlib import Path
from numba import njit
FILES=[
('2026-01','XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'),
('2026-02','XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'),
('2026-03','XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177'),
('2026-04','XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f'),
('2026-05','XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d'),
('2026-06','XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2'),
('2026-07','XAUUSD_DUKAS_2026_07_ticks.csv(2).gz','e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7')]
STOP=.30;TRAIL_ACT=.10;TRAIL=.03;COMM=.20

def load_month(path):
 ts=[];asks=[];bids=[];problems={};prev=None;count=0
 sha=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(16<<20),b''):sha.update(b)
 for df in pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=1_000_000,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'}):
  t=df.timestamp_ms_utc.to_numpy(copy=True);a=df.ask_raw.to_numpy(dtype=np.int32,copy=True);b=df.bid_raw.to_numpy(dtype=np.int32,copy=True)
  if len(t):
   if prev is not None and t[0]<prev:problems['timestamp_descended']=problems.get('timestamp_descended',0)+1
   d=np.diff(t);z=int((d<0).sum());
   if z:problems['timestamp_descended']=problems.get('timestamp_descended',0)+z
   z=int((a<b).sum());
   if z:problems['crossed_quote']=problems.get('crossed_quote',0)+z
   prev=int(t[-1]);count+=len(t)
  ts.append(t);asks.append(a);bids.append(b)
 return np.concatenate(ts),np.concatenate(asks),np.concatenate(bids),sha.hexdigest(),problems

def build_s1(t,bid):
 sec=t//1000;starts=np.r_[0,np.flatnonzero(sec[1:]!=sec[:-1])+1];ends=np.r_[starts[1:],len(t)]
 sid=sec[starts];c=bid[ends-1].astype(np.float64)/1000.;h=np.maximum.reduceat(bid,starts).astype(np.float64)/1000.;lo=np.minimum.reduceat(bid,starts).astype(np.float64)/1000.
 return sid,h,lo,c
@njit(cache=True)
def qarr(sid,h,l,c):
 n=len(sid);d=np.zeros(n);e=np.zeros(n);r=np.zeros(n);turn=np.zeros(n,np.int16);span=np.zeros(n,np.int32)
 for i in range(10,n):
  st=c[i-9];prev=st;travel=0.;ps=0.;tt=0;hh=-1e99;ll=1e99
  for j in range(i-9,i+1):
   if h[j]>hh:hh=h[j]
   if l[j]<ll:ll=l[j]
   if j>i-9:
    dd=c[j]-prev;travel+=abs(dd);sg=1. if dd>0 else (-1. if dd<0 else 0.)
    if sg!=0:
     if ps!=0 and sg!=ps:tt+=1
     ps=sg
    prev=c[j]
  d[i]=c[i]-st;e[i]=abs(d[i])/(travel+1e-9);r[i]=hh-ll;turn[i]=tt;span[i]=int(sid[i]-sid[i-9])
 return d,e,r,turn,span

def build_m5(t,bid):
 b=t//300000;starts=np.r_[0,np.flatnonzero(b[1:]!=b[:-1])+1];ends=np.r_[starts[1:],len(t)];ids=b[starts]
 hi=np.maximum.reduceat(bid,starts).astype(np.float64)/1000.;lo=np.minimum.reduceat(bid,starts).astype(np.float64)/1000.;cl=bid[ends-1].astype(np.float64)/1000.
 tr=np.empty(len(ids));tr[0]=hi[0]-lo[0];tr[1:]=np.maximum(hi[1:]-lo[1:],np.maximum(np.abs(hi[1:]-cl[:-1]),np.abs(lo[1:]-cl[:-1])))
 atr=np.full(len(ids),np.nan)
 if len(ids)>=14:atr[13:]=np.convolve(tr,np.ones(14)/14,'valid')
 return ids,atr

# 2026 DST boundaries exactly matching source functions.
NY_DST_START=1772953200000 # 2026-03-08 07:00 UTC
LON_DST_START=1774746000000 # 2026-03-29 01:00 UTC
@njit(cache=True)
def atr_min(tms):
 minute=(tms//60000)%1440
 loff=60 if tms>=LON_DST_START else 0
 noff=-240 if tms>=NY_DST_START else -300
 lm=(minute+loff)%1440;nm=(minute+noff)%1440
 london=lm>=480 and lm<990;ny=nm>=480 and nm<1020
 if london and ny:return 1.75
 if london:return 2.0
 if ny:return 1.75
 return 2.5

@njit(cache=True)
def sim(t,askr,bidr,start_i,s1last,qd,qe,qr,qt,qspan,m5ids,m5atr,idx250,idx1,idx5,mode,spreadcap,ratio,d5min,start_equity,start_peak,start_maxdd):
 equity=start_equity;peak=start_peak;maxdd=start_maxdd;month_gp=month_gl=month_net=0.;wins=trades=0;pos=0;entry=sl=0.;entrysec=0;cycle=-1;buy=sell=0.;pending=0;had=False;lastpos=0;rearms=0;lastExit=-10**18;m5p=0;atr=np.nan
 for i in range(start_i,len(t)):
  tm=t[i];ask=askr[i]/1000.;bid=bidr[i]/1000.;mid=(ask+bid)*.5;sp=ask-bid;mb=tm//300000
  while m5p+1<len(m5ids) and m5ids[m5p+1]<mb:m5p+=1
  p=m5p
  if m5ids[p]>=mb:p-=1
  if p>=0:atr=m5atr[p]
  minute=tm//60000
  if minute!=cycle:cycle=minute;buy=mid+.15;sell=mid-.15;pending=2;rearms=0
  if pos:
   close=False;px=0.
   if pos==1:
    if bid<=sl or tm//1000-entrysec>=30:close=True;px=bid
    elif bid-entry>=.10:
     c=bid-.03
     if c>sl:sl=c
   else:
    if ask>=sl or tm//1000-entrysec>=30:close=True;px=ask
    elif entry-ask>=.10:
     c=ask+.03
     if c<sl:sl=c
   if close:
    pnl=((px-entry) if pos==1 else (entry-px))-COMM;equity+=pnl;month_net+=pnl;trades+=1
    if pnl>0:wins+=1;month_gp+=pnl
    else:month_gl+=pnl
    if equity>peak:peak=equity
    if peak-equity>maxdd:maxdd=peak-equity
    lastpos=pos;pos=0;had=True;lastExit=tm
   continue
  if had:
   had=False
   if tm//60000==cycle and rearms<3:rearms+=1;pending=-1 if lastpos==1 else 1
   else:pending=0
   continue
  qi=s1last[i]
  if qi<10 or math.isnan(atr) or atr+1e-12<atr_min(tm):continue
  if qe[qi]<.70 or qr[qi]<.50 or qt[qi]>9:continue
  qside=1 if qd[qi]>=.15 else (-1 if qd[qi]<=-.15 else 0)
  if qside==0:continue
  j250=idx250[i];j1=idx1[i];j5=idx5[i];m250=(askr[j250]+bidr[j250])*.0005 if j250>=0 else mid;m1=(askr[j1]+bidr[j1])*.0005 if j1>=0 else mid;m5=(askr[j5]+bidr[j5])*.0005 if j5>=0 else mid;d250=mid-m250;d1=mid-m1;d5=mid-m5
  if spreadcap>0 and sp>spreadcap:continue
  if ratio>0 and sp/(qr[qi]+1e-9)>ratio:continue
  side=0
  if mode==0:
   if (pending==2 or pending==1) and ask>=buy and qside==1:side=1
   elif (pending==2 or pending==-1) and bid<=sell and qside==-1:side=-1
  else:
   if tm-lastExit<500:continue
   if qside==1 and d250>0 and d1>.04 and d5>d5min and qspan[qi]<=12:side=1
   elif qside==-1 and d250<0 and d1<-.04 and d5<-d5min and qspan[qi]<=12:side=-1
  if side:
   entry=ask if side==1 else bid;entrysec=tm//1000;sl=bid-STOP if side==1 else ask+STOP;pos=side;pending=0
 # Since file endpoints occur at weekend/close and hold <=30s, close any residual at month end for bounded accounting; note in report.
 if pos:
  ask=askr[-1]/1000.;bid=bidr[-1]/1000.;pnl=((bid-entry) if pos==1 else (entry-ask))-COMM;equity+=pnl;month_net+=pnl;trades+=1
  if pnl>0:wins+=1;month_gp+=pnl
  else:month_gl+=pnl
  if equity>peak:peak=equity
  if peak-equity>maxdd:maxdd=peak-equity
 return trades,wins,(wins/trades if trades else 0.),month_net,month_gp,month_gl,equity,peak,maxdd

def prep(t,a,b):
 sid,h,l,c=build_s1(t,b);qd,qe,qr,qt,qspan=qarr(sid,h,l,c);s1last=np.searchsorted(sid,t//1000,side='left').astype(np.int64)-1;m5ids,m5atr=build_m5(t,b);i250=np.searchsorted(t,t-250,side='right').astype(np.int64)-1;i1=np.searchsorted(t,t-1000,side='right').astype(np.int64)-1;i5=np.searchsorted(t,t-5000,side='right').astype(np.int64)-1
 return s1last,qd,qe,qr,qt,qspan,m5ids,m5atr,i250,i1,i5

def main():
 configs=[('R9_FEED_NORMALIZED',0,0.,0.,0.),('ENTRY_A_VOLUME',1,.80,0.,.18),('ENTRY_B_PRECISION',1,1.00,.50,.18)]
 totals={n:{'trades':0,'wins':0,'net':0.,'gp':0.,'gl':0.,'equity':0.,'peak':0.,'maxdd':0.} for n,_,_,_,_ in configs};months=[];cert=[];tail=None;start=time.time()
 for month,fn,expect in FILES:
  p=Path('/mnt/data')/fn;t,a,b,sha,problems=load_month(p);assert sha==expect and not problems
  cert.append({'month':month,'file':fn,'sha256':sha,'sha_match':True,'gzip_crc_eof_verified':True,'rows':int(len(t)),'first_ms':int(t[0]),'last_ms':int(t[-1])})
  if tail is not None:
   tw,aw,bw=tail;tall=np.concatenate([tw,t]);aall=np.concatenate([aw,a]);ball=np.concatenate([bw,b]);start_i=len(tw)
  else:tall,aall,ball=t,a,b;start_i=0
  prepv=prep(tall,aall,ball);mrow={'month':month,'rows':int(len(t)),'strategies':{}}
  for name,mode,cap,ratio,d5 in configs:
   T=totals[name]
   res=sim(tall,aall,ball,start_i,*prepv,mode,cap,ratio,d5,T['equity'],T['peak'],T['maxdd'])
   tr,wi,wr,net,gp,gl,eq,peak,dd=res;T['trades']+=int(tr);T['wins']+=int(wi);T['net']+=float(net);T['gp']+=float(gp);T['gl']+=float(gl);T['equity']=float(eq);T['peak']=float(peak);T['maxdd']=float(dd)
   mrow['strategies'][name]={'trades':int(tr),'wins':int(wi),'win_rate':float(wr),'net_usd':float(net),'gross_profit_usd':float(gp),'gross_loss_usd':float(gl),'cumulative_equity_usd':float(eq),'cumulative_max_dd_usd':float(dd)}
  months.append(mrow)
  # retain 2h of actual observed data as causal warmup for next month; no trades from warmup
  cutoff=t[-1]-2*3600*1000;j=np.searchsorted(t,cutoff,side='left');tail=(t[j:].copy(),a[j:].copy(),b[j:].copy())
  print(month,{k:(v['strategies'][k]['trades'],v['strategies'][k]['wins'],round(v['strategies'][k]['net_usd'],2)) for k in v['strategies']} if False else {k:(mrow['strategies'][k]['trades'],mrow['strategies'][k]['wins'],round(mrow['strategies'][k]['net_usd'],2)) for k,_,_,_,_ in configs},flush=True)
 base=totals['R9_FEED_NORMALIZED']
 for name in totals:
  T=totals[name];T['win_rate']=T['wins']/T['trades'] if T['trades'] else 0.;T['win_count_change_pct']=100*(T['wins']/base['wins']-1) if base['wins'] else None;T['win_rate_change_pct']=100*(T['win_rate']/(base['wins']/base['trades'])-1) if base['wins'] else None;T['net_improvement_usd']=T['net']-base['net'];T['net_improvement_vs_abs_baseline_net_pct']=100*(T['net']-base['net'])/abs(base['net']) if base['net'] else None;T['dd_change_pct']=100*(T['maxdd']/base['maxdd']-1) if base['maxdd'] else None
 out={'unit_id':'BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION__003','status':'JAN_JUL_ANALYSIS_AFTER_JAN_10PCT_ENTRY_SCREEN','sources':cert,'fixed_geometry':{'stop':STOP,'trail_activation':TRAIL_ACT,'trail':TRAIL,'max_hold_s':30,'extra_roundtrip_commission':COMM},'candidate_definitions':{'ENTRY_A_VOLUME':'early momentum; R9 S1/ATR quality; 250ms>0, 1s>|0.04|, 5s>|0.18|; observed-second span<=12s; Dukascopy spread <=$0.80','ENTRY_B_PRECISION':'same early momentum; spread <=$1.00 and spread/recent-10bar-range <=0.50'},'monthly':months,'aggregate':totals,'method_note':'Each month verified full gzip read/CRC and manifest SHA. 2h prior-month tail is warmup only. Month-end residual positions are force-closed for bounded accounting; R9 hold max is 30s and files end at market close, so this should be rare. Same fixed R9 hold/exit geometry across strategies. Dukascopy actual Bid/Ask fills plus $0.20 extra fee.','august_read':False,'runtime_sec':time.time()-start}
 Path('/mnt/data/BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out['aggregate'],indent=2))
if __name__=='__main__':main()