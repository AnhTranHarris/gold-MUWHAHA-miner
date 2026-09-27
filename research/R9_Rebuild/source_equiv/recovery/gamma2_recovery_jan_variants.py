import pandas as pd, numpy as np, json, time, gc
from numba import njit
from pathlib import Path
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'); H=.10
TARGET=(30943,25368,0.8198300100184209,5131.0509999771375,-6091.20650000407)

def active_seconds(t,p):
 s=t//1000; ch=np.empty(len(s),bool); ch[0]=1; ch[1:]=s[1:]!=s[:-1]; ix=np.flatnonzero(ch); last=np.r_[ix[1:]-1,len(s)-1]
 return s[ix].astype(np.int64),t[ix].astype(np.int64),p[ix],np.maximum.reduceat(p,ix),np.minimum.reduceat(p,ix),p[last],ix.astype(np.int64),last.astype(np.int64)

def aggregate(sec,h,l,c,tf):
 b=sec//tf; ch=np.empty(len(b),bool); ch[0]=1; ch[1:]=b[1:]!=b[:-1]; ix=np.flatnonzero(ch); last=np.r_[ix[1:]-1,len(b)-1]; ids=b[ix]; cc=c[last]; hh=np.maximum.reduceat(h,ix); ll=np.minimum.reduceat(l,ix); end=(ids+1)*tf
 prev=np.r_[np.nan,cc[:-1]]; tr=np.maximum(hh-ll,np.maximum(np.abs(hh-prev),np.abs(ll-prev))); atr=np.full(len(tr),np.nan); e=np.nan
 for i,x in enumerate(tr):
  if not np.isfinite(x):continue
  e=x if not np.isfinite(e) else (13/14)*e+(1/14)*x
  if i>=13:atr[i]=e
 ret=np.r_[np.nan,np.diff(cc)]
 return end.astype(np.int64),ret,atr

def map_completed(sec,end,v):
 j=np.searchsorted(end,sec,side='right')-1; out=np.full(len(sec),np.nan); ok=j>=0; out[ok]=v[j[ok]]; return out

@njit
def floor_session(sec):
 # exact 2026 DST
 lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
 ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
 lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
 l=lm>=480 and lm<990; n=nm>=480 and nm<1020
 if l and n:return 1.75
 if l:return 2.
 if n:return 1.75
 return 2.5

@njit
def replay(t,mid,X):
 n=len(X);o=np.empty((n,3),np.float64)
 for k in range(n):
  sig=int(X[k,0]);side=int(X[k,1]);ac=X[k,3];i=np.searchsorted(t,sig)
  if i>=len(t):o[k]=np.nan;continue
  stopd=1. if ac>=3 else 3.;act=.10 if ac>=3 else .18;trail=.04 if ac>=3 else .05
  p=mid[i];entry=p+H if side>0 else p-H;bid=p-H;ask=p+H;stop=bid-stopd if side>0 else ask+stopd;ot=t[i];done=False
  for q in range(i+1,len(t)):
   tt=t[q];p=mid[q];bid=p-H;ask=p+H;fav=bid-entry if side>0 else entry-ask
   if (side>0 and bid<=stop) or (side<0 and ask>=stop) or tt-ot>=60000:
    ex=bid if side>0 else ask;o[k,0]=(ex-entry)*side;o[k,1]=tt;o[k,2]=(tt-ot)/1000.;done=True;break
   if fav>=act:
    cand=bid-trail if side>0 else ask+trail
    if side>0:
     if cand>stop:stop=cand
    else:
     if cand<stop:stop=cand
  if not done:o[k]=np.nan
 return o

@njit
def nonoverlap(X,O):
 ix=np.argsort(X[:,0]);keep=np.empty(len(ix),np.int64);n=0;free=-1
 for q in ix:
  if X[q,0]<=free or not np.isfinite(O[q,0]):continue
  keep[n]=q;n+=1;free=int(O[q,1])
 return keep[:n]

@njit
def gen_tick(t,mid,sec_ids,first_ix,m5,al,ash,cont_mode,liq_shift):
 # exact tick-native R8 event processing; detached signal population. cont_mode: 0 ignore CONT,1 reset only,2 reset+quota+cooldown,3 quota only,4 cooldown only
 cap=120000;X=np.empty((cap,4),np.float64);n=0
 state=0;level=0.;started=0;minute=-1;trades=0;cool_until=-1
 j=0
 for i in range(len(t)):
  s=t[i]//1000
  while j+1<len(sec_ids) and sec_ids[j+1]<=s: j+=1
  # current active second index j. completed bars end at j-1 unless tick belongs a gap mismatch; first_ix[j]<=i
  mn=s//60
  if mn!=minute:
   minute=mn;trades=0;state=0;level=0.;started=0
  if s<cool_until or trades>=5:continue
  if j<21:continue
  av=m5[j]
  if not np.isfinite(av) or av+1e-12<floor_session(s):continue
  # newest completed bar index j-1. shift 0 exact R8; shift -1 reproduces 007 older window
  newest=j-1+liq_shift
  oldest=newest-19
  if oldest<0:continue
  upper=-1e18;lower=1e18
  for q in range(oldest,newest+1):
   if (mid[first_ix[q]]-H)>1e99: pass
   # bars not stored here: approximate from sec first/last impossible; passed later? no
  # placeholder unreachable
 return X[:n]

@njit
def gen_tick_bars(t,mid,sec_ids,first_ix,hb,lb,cb,m5,al,ash,cont_mode,liq_shift):
 cap=160000;X=np.empty((cap,4),np.float64);n=0
 state=0;level=0.;started=0;minute=-1;trades=0;cool_until=-1;j=0
 for i in range(len(t)):
  s=t[i]//1000
  while j+1<len(sec_ids) and sec_ids[j+1]<=s:j+=1
  mn=s//60
  if mn!=minute:
   minute=mn;trades=0;state=0;level=0.;started=0
  if s<cool_until or trades>=5 or j<21:continue
  av=m5[j]
  if not np.isfinite(av) or av+1e-12<floor_session(s):continue
  newest=j-1+liq_shift;oldest=newest-19
  if oldest<0 or newest>=j:continue
  upper=-1e18;lower=1e18
  for q in range(oldest,newest+1):
   if hb[q]>upper:upper=hb[q]
   if lb[q]<lower:lower=lb[q]
  bid=mid[i]-H;ask=mid[i]+H
  # 5 completed closes + current bid, matching R8
  oldestv=j-5
  if oldestv<0:continue
  prev=cb[oldestv];start=prev;travel=0.
  for q in range(oldestv+1,j):
   v=cb[q];travel+=abs(v-prev);prev=v
  travel+=abs(bid-prev);disp=bid-start;eff=abs(disp)/(travel+1e-9)
  if state==0:
   if ask>=upper+.10:state=1;level=upper;started=s
   elif bid<=lower-.10:state=-1;level=lower;started=s
  if state==1:
   if ask<=level-.15:state=2;started=s
   elif s-started>=2 and ask>=level+.08 and disp>=.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool_until=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool_until=s+1
  elif state==-1:
   if bid>=level+.15:state=-2;started=s
   elif s-started>=2 and bid<=level-.08 and disp<=-.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool_until=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool_until=s+1
  elif state==2:
   if disp<=-.15 and eff>=.30:
    X[n,0]=t[i];X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1;trades+=1;cool_until=s+1;state=0;level=0.;started=0
  elif state==-2:
   if disp>=.15 and eff>=.30:
    X[n,0]=t[i];X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1;trades+=1;cool_until=s+1;state=0;level=0.;started=0
  if state!=0 and started>0 and s-started>20:state=0;level=0.;started=0
 return X[:n]

@njit
def gen_second(sec,first_t,hb,lb,cb,m5,al,ash,mode,entry_shift,liq_variant):
 # completed-second state machine. mode 0/1/2/3/4 cont side effect as above. entry_shift: 0 enter next sec first tick; -1 enter evaluated bar first tick (lookahead); +1 one sec later
 cap=150000;X=np.empty((cap,4),np.float64);n=0;state=0;level=0.;started=0;minute=-1;trades=0;cool=-1
 for j in range(21,len(sec)):
  s=sec[j];prev=j-1;mn=s//60
  if mn!=minute:minute=mn;trades=0;state=0;level=0.;started=0
  if s<cool or trades>=5:continue
  if not np.isfinite(m5[j]) or m5[j]+1e-12<floor_session(s):continue
  # liq_variant 0 = exact newest prior sec j-1; 1=007 old j-2; 2=samebar leakage includes prev in both level and event bar with older 20 before it
  if liq_variant==0: newest=prev; oldest=prev-19; event=prev
  elif liq_variant==1: newest=prev-1; oldest=prev-20; event=prev
  else: newest=prev-1; oldest=prev-20; event=prev
  upper=-1e18;lower=1e18
  for q in range(oldest,newest+1):
   if hb[q]>upper:upper=hb[q]
   if lb[q]<lower:lower=lb[q]
  # completed-event bar values; velocity 5 completed bars ending event
  e=event; start=cb[e-4];p0=start;travel=0.
  for q in range(e-3,e+1):v=cb[q];travel+=abs(v-p0);p0=v
  disp=cb[e]-start;eff=abs(disp)/(travel+1e-9)
  ask_hi=hb[e]+2*H; ask_cl=cb[e]+2*H # hb/cb are modeled bid; ask=bid+.20
  bid_lo=lb[e];bid_cl=cb[e]
  if state==0:
   if ask_hi>=upper+.10:state=1;level=upper;started=s
   elif bid_lo<=lower-.10:state=-1;level=lower;started=s
  if state==1:
   if ask_cl<=level-.15:state=2;started=s
   elif mode!=0 and s-started>=2 and ask_cl>=level+.08 and disp>=.15 and eff>=.30:
    if mode==1:state=0;level=0.;started=0
    elif mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
    elif mode==3:state=0;level=0.;started=0;trades+=1
    elif mode==4:state=0;level=0.;started=0;cool=s+1
  elif state==-1:
   if bid_cl>=level+.15:state=-2;started=s
   elif mode!=0 and s-started>=2 and bid_cl<=level-.08 and disp<=-.15 and eff>=.30:
    if mode==1:state=0;level=0.;started=0
    elif mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
    elif mode==3:state=0;level=0.;started=0;trades+=1
    elif mode==4:state=0;level=0.;started=0;cool=s+1
  elif state==2:
   if disp<=-.15 and eff>=.30:
    ix=j+entry_shift
    if ix>=0 and ix<len(first_t):X[n,0]=first_t[ix];X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1
    trades+=1;cool=s+1;state=0;level=0.;started=0
  elif state==-2:
   if disp>=.15 and eff>=.30:
    ix=j+entry_shift
    if ix>=0 and ix<len(first_t):X[n,0]=first_t[ix];X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1
    trades+=1;cool=s+1;state=0;level=0.;started=0
  if state!=0 and started>0 and s-started>20:state=0;level=0.;started=0
 return X[:n]

def met(v):
 gp=float(v[v>0].sum());gl=float(v[v<0].sum());return {'trades':len(v),'winners':int((v>0).sum()),'win':float((v>0).mean()),'net':float(v.sum()),'gl':gl,'pf':gp/-gl}

def evalx(label,X,t,mid):
 O=replay(t,mid,X);ix=nonoverlap(X,O);q=O[ix];m=met(q[:,0]);m['raw']=len(X);m['label']=label;m['trade_delta']=m['trades']-TARGET[0];m['winner_delta']=m['winners']-TARGET[1];m['net_delta']=m['net']-TARGET[3];print(json.dumps(m),flush=True);return m

def main():
 st=time.time();d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);a=d.ask_raw.to_numpy(np.float64)/1000.;b=d.bid_raw.to_numpy(np.float64)/1000.;mid=(a+b)*.5;mb=mid-H
 sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb)
 e5,r5,a5=aggregate(sec,h,l,c,300);m5=map_completed(sec,e5,a5);al=np.zeros(len(sec),np.int8);ash=np.zeros(len(sec),np.int8)
 for tf in (60,180,300,600,1200):
  e,r,a2=aggregate(sec,h,l,c,tf);rr=map_completed(sec,e,r);aa=map_completed(sec,e,a2);ok=np.isfinite(aa);al+=((rr>0)&ok).astype(np.int8);ash+=((rr<0)&ok).astype(np.int8)
 rows=[]
 # exact tick-native modes, exact and shifted liquidity windows
 for lv in (0,-1):
  for cm in (0,1,2,3,4):
   X=gen_tick_bars(t,mid,sec,first_ix,h,l,c,m5,al,ash,cm,lv);rows.append(evalx(f'tick_lv{lv}_cont{cm}',X,t,mid))
 # completed-second modes with causal and lookahead entry shifts
 for lv in (0,1):
  for cm in (0,1,2,3,4):
   for es in (0,-1,1):
    X=gen_second(sec,first_t,h,l,c,m5,al,ash,cm,es,lv);rows.append(evalx(f'sec_lv{lv}_cont{cm}_eshift{es}',X,t,mid))
 Path('/mnt/data/GAMMA2_JAN_VARIANTS.json').write_text(json.dumps({'rows':rows,'elapsed':time.time()-st},indent=2))
if __name__=='__main__':main()
