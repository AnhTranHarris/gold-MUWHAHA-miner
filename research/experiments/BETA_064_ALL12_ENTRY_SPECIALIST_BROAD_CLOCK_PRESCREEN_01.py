import pandas as pd, numpy as np, glob, sys, gc, json, os
from pathlib import Path
from numba import njit
ROOT=Path('/mnt/data')
SESS={
 'AUSTRALIA':('Australia/Sydney',8,17),
 'ASIA':('Asia/Tokyo',9,18),
 'MIDEAST':('Asia/Dubai',8,17),
 'EUROPE':('Europe/Berlin',8,17),
 'UK':('Europe/London',8,17),
 'NY':('America/New_York',8,17),
}
SPEC={
'E1_MACRO_TREND':(900,60),'E2_PULLBACK_REACCEL':(300,30),'E3_ORB':(300,30),
'E4_VWAP_PULLBACK':(300,30),'E5_VWAP_RECLAIM':(120,15),'E6_VALUE_REVERSION':(180,20),
'E7_SWEEP_RECLAIM':(120,15),'E8_LEVEL_BOUNCE':(300,30),'E9_LEVEL_BREAK':(300,30),
'E10_COMPRESSION_RELEASE':(120,15),'E11_KINETIC_IGNITION':(45,10),'E12_FAILED_EXPANSION':(120,15),
}
@njit
def labels(ct,side,hor,chk,sp,atr,times,bid,ask):
 n=len(ct); out=np.zeros((n,3),np.float64)
 for k in range(n):
  i=np.searchsorted(times,ct[k])
  if i>=len(times): continue
  ent=ask[i] if side[k]>0 else bid[i]
  spr=max(sp[k],.05); at=max(atr[k],spr)
  fav=max(.35,1.25*spr,.30*at); adv=max(.30,1.0*spr,.22*at)
  check=ct[k]+chk[k]*1000; end=ct[k]+hor[k]*1000
  fh=-1; ah=-1; last=i; j=i+1
  while j<len(times) and times[j]<=end:
   px=bid[j] if side[k]>0 else ask[j]; ex=(px-ent)*side[k]; last=j
   if fh<0 and ex>=fav: fh=j
   if ah<0 and ex<=-adv: ah=j
   if fh>=0 and ah>=0: break
   j+=1
  surv=1. if ah<0 or times[ah]>check else 0.
  fp=1. if fh>=0 and (ah<0 or fh<ah) else 0.
  jj=fh if fp>0 else (ah if ah>=0 else last)
  px=bid[jj] if side[k]>0 else ask[jj]
  out[k,0]=surv; out[k,1]=fp; out[k,2]=(px-ent)*side[k]-.02
 return out

def eff(s,n): return (s-s.shift(n)).abs()/(s.diff().abs().rolling(n,n).sum()+1e-9)

def read_raw(m):
 f=glob.glob(str(ROOT/f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz'))[0]
 d=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume'],
   dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32','ask_volume':'float32','bid_volume':'float32'})
 d['time']=pd.to_datetime(d.timestamp_ms_utc,unit='ms',utc=True)
 d['ask']=d.ask_raw.astype('float64')/1000.;d['bid']=d.bid_raw.astype('float64')/1000.;d['mid']=(d.ask+d.bid)/2.;d['spread']=d.ask-d.bid
 return d

def build5(d):
 x=d.set_index('time')
 b=pd.DataFrame({'open':x.mid.resample('5s').first(),'high':x.mid.resample('5s').max(),'low':x.mid.resample('5s').min(),
  'mid':x.mid.resample('5s').last(),'bid':x.bid.resample('5s').last(),'ask':x.ask.resample('5s').last(),
  'spread':x.spread.resample('5s').last(),'ticks':x.mid.resample('5s').count(),
  'askv':x.ask_volume.resample('5s').sum(),'bidv':x.bid_volume.resample('5s').sum()}).dropna(subset=['mid'])
 b.index=b.index+pd.Timedelta(seconds=5)
 b['body']=b.mid-b.open;b['range']=b.high-b.low
 for sec,n in [(15,3),(30,6),(60,12),(300,60),(900,180),(3600,720),(14400,2880)]:
  b[f'r{sec}']=b.mid-b.mid.shift(n); b[f'eff{sec}']=eff(b.mid,n)
 b['atr60']=b.high.rolling(12,12).max()-b.low.rolling(12,12).min();b['atr300']=b.high.rolling(60,60).max()-b.low.rolling(60,60).min();b['atr900']=b.high.rolling(180,180).max()-b.low.rolling(180,180).min()
 b['tick_z']=(b.ticks-b.ticks.rolling(180,60).mean())/(b.ticks.rolling(180,60).std()+1e-6)
 b['qp']=(b.mid.diff().fillna(0)*b.ticks).rolling(12,3).sum()/(b.ticks.rolling(12,3).sum()+1e-6)
 b['qv']=(b.bidv-b.askv)/(b.bidv+b.askv+1e-6)
 b['v1']=b.mid.diff();b['v3']=(b.mid-b.mid.shift(3))/3.;b['v12']=(b.mid-b.mid.shift(12))/12.
 b['a1']=b.v1-b.v1.shift();b['a3']=(b.v3-b.v3.shift(3))/3.;b['j1']=b.a1-b.a1.shift();b['j3']=(b.a3-b.a3.shift(3))/3.
 scale=b.mid.diff().abs().rolling(180,60).median()+1e-5
 for c in ['v1','v3','v12','a1','a3','j1','j3']: b[c+'n']=b[c]/scale
 b['friction']=b.spread/b.atr60.clip(lower=.05)
 for n in [60,180]:
  b[f'prior{n}_hi']=b.high.rolling(n,n).max().shift(1); b[f'prior{n}_lo']=b.low.rolling(n,n).min().shift(1)
 w=b.ticks.clip(lower=1); num=(b.mid*w).rolling(180,60).sum();den=w.rolling(180,60).sum();b['vwap15']=num/(den+1e-9);b['vwap15_z']=(b.mid-b.vwap15)/b.atr60.clip(lower=.05)
 b['range60']=b.high.rolling(12,12).max()-b.low.rolling(12,12).min();b['range900']=b.high.rolling(180,60).max()-b.low.rolling(180,60).min();b['compression']=b.range60/(b.range900+1e-6)
 return b.replace([np.inf,-np.inf],np.nan)

def session_state(b,name,tz,op,cl):
 loc=b.index.tz_convert(tz);mins=loc.hour*60+loc.minute+loc.second/60.;dates=pd.Series(loc.date,index=b.index);o=op*60;c=cl*60
 x=pd.DataFrame(index=b.index);x['active']=((mins>=o)&(mins<c));x['rel']=mins-o;x['svwap']=np.nan;x['orb_hi']=np.nan;x['orb_lo']=np.nan;x['pre_hi']=np.nan;x['pre_lo']=np.nan
 for dt,idx in dates.groupby(dates).groups.items():
  ii=pd.Index(idx);pos=b.index.get_indexer(ii);lm=mins[pos];am=(lm>=o)&(lm<c);ai=ii[am]
  if not len(ai): continue
  prem=(lm>=o-30)&(lm<o);pi=ii[prem]
  if len(pi):x.loc[ai,'pre_hi']=b.loc[pi,'high'].max();x.loc[ai,'pre_lo']=b.loc[pi,'low'].min()
  om=(lm>=o)&(lm<o+15);oi=ii[om]
  if len(oi):
   e=oi.max()+pd.Timedelta(seconds=5);aft=ai[ai>=e];x.loc[aft,'orb_hi']=b.loc[oi,'high'].max();x.loc[aft,'orb_lo']=b.loc[oi,'low'].min()
  w=b.loc[ai,'ticks'].clip(lower=1);x.loc[ai,'svwap']=((b.loc[ai,'mid']*w).cumsum()/w.cumsum()).to_numpy()
 return x

def edge(mask):
 m=mask.fillna(False); return m & ~m.shift(1,fill_value=False)

def candidates(b):
 rows=[]
 def emit(mask,side,name,sess='GLOBAL',rel=np.nan):
  m=edge(mask); inds=np.flatnonzero(m.to_numpy()); hor,chk=SPEC[name]
  last=-10**30
  for i in inds:
   tm=b.index[i].value//1_000_000
   if tm-last<30000: continue
   sd=int(side.iloc[i] if hasattr(side,'iloc') else side)
   rv=float(rel.iloc[i]) if hasattr(rel,'iloc') else (float(rel) if np.isfinite(rel) else np.nan)
   rows.append((b.index[i],sd,name,sess,hor,chk,rv));last=tm
 s1=pd.Series(np.where((b.r3600.fillna(0)+.35*b.r14400.fillna(0))>=0,1,-1),index=b.index)
 fresh=((s1>0)&(b.mid>b.prior60_hi)&(b.r900*s1>0))|((s1<0)&(b.mid<b.prior60_lo)&(b.r900*s1>0))
 emit(fresh&(b.eff3600>.14)&(b.eff900>.14)&(b.friction<=.28),s1,'E1_MACRO_TREND')
 s2=pd.Series(np.where(b.r3600>=0,1,-1),index=b.index)
 emit((b.r3600*s2>0)&(b.r300*s2<0)&(b.r60*s2>0)&(b.r15*s2>0)&(b.eff3600>.12)&(b.friction<=.28),s2,'E2_PULLBACK_REACCEL')
 near=b.vwap15_z.abs()<=.60
 emit(near&(b.r3600*s2>0)&(b.r60*s2>0)&(b.r15*s2>0)&(b.eff3600>.12)&(b.friction<=.25),s2,'E4_VWAP_PULLBACK')
 long8=(b.low<=b.prior180_lo+.10*b.atr60)&(b.mid>b.prior180_lo+.05*b.atr60)&(b.body>0);short8=(b.high>=b.prior180_hi-.10*b.atr60)&(b.mid<b.prior180_hi-.05*b.atr60)&(b.body<0);ss8=pd.Series(np.where(long8,1,-1),index=b.index)
 emit((long8|short8)&(b.eff60>=.20)&(b.friction<=.22),ss8,'E8_LEVEL_BOUNCE')
 ss11=pd.Series(np.where(b.v3>=0,1,-1),index=b.index)
 emit((b.v3n.abs()>=1.0)&((b.a3n*ss11)>=.12)&(b.tick_z>=.5)&(b.eff15>=.55)&(b.friction<=.20),ss11,'E11_KINETIC_IGNITION')
 for sess,(tz,op,cl) in SESS.items():
  st=session_state(b,sess,tz,op,cl); active=st.active&(st.rel>=15)
  if sess in ('UK','NY'):
   long=active&st.orb_hi.notna()&(b.open<=st.orb_hi)&(b.mid>st.orb_hi)&(b.body>0);short=active&st.orb_lo.notna()&(b.open>=st.orb_lo)&(b.mid<st.orb_lo)&(b.body<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
   emit((long|short)&((b.body*ss)>=.12*b.atr60)&(b.eff15>=.45)&(b.friction<=.22),ss,'E3_ORB',sess,st.rel)
  dv=b.mid-st.svwap;pv=dv.shift(1);long=active&st.svwap.notna()&(pv<0)&(dv>0)&(b.r15>0);short=active&st.svwap.notna()&(pv>0)&(dv<0)&(b.r15<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
  emit((long|short)&(b.eff15>=.35)&(b.friction<=.22),ss,'E5_VWAP_RECLAIM',sess,st.rel)
  z=dv/b.atr60.clip(lower=.05);ss=pd.Series(np.where(dv>=0,-1,1),index=b.index)
  emit(active&st.svwap.notna()&(z.abs()>=1.10)&(b.eff300<=.45)&((b.v3n*ss)>=-.10)&((b.a3n*ss)>=.06)&(b.friction<=.22),ss,'E6_VALUE_REVERSION',sess,st.rel)
  hi=pd.concat([st.pre_hi,st.orb_hi],axis=1).max(axis=1);lo=pd.concat([st.pre_lo,st.orb_lo],axis=1).min(axis=1);base=active&hi.notna()&lo.notna()
  long=base&(b.low<lo)&(b.mid>lo)&(b.body>0);short=base&(b.high>hi)&(b.mid<hi)&(b.body<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
  emit((long|short)&(b.eff15>=.25)&(b.tick_z>=-.25)&(b.friction<=.22),ss,'E7_SWEEP_RECLAIM',sess,st.rel)
  long=base&(b.open<=hi)&(b.mid>hi)&(b.body>0);short=base&(b.open>=lo)&(b.mid<lo)&(b.body<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
  emit((long|short)&((b.body*ss)>=.10*b.atr60)&(b.eff15>=.35)&(b.friction<=.20),ss,'E9_LEVEL_BREAK',sess,st.rel)
  long=active&(b.open<=b.prior60_hi)&(b.mid>b.prior60_hi)&(b.body>0);short=active&(b.open>=b.prior60_lo)&(b.mid<b.prior60_lo)&(b.body<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
  emit((long|short)&(b.compression.shift(1)<=.30)&(b.tick_z>=.5)&(b.eff15>=.5)&(b.friction<=.20),ss,'E10_COMPRESSION_RELEASE',sess,st.rel)
  prev_hi=b.prior60_hi.shift(1);prev_lo=b.prior60_lo.shift(1)
  long=active&(b.mid.shift(1)<prev_lo)&(b.mid>b.prior60_lo)&(b.body>0);short=active&(b.mid.shift(1)>prev_hi)&(b.mid<b.prior60_hi)&(b.body<0);ss=pd.Series(np.where(long,1,-1),index=b.index)
  emit((long|short)&(b.tick_z>=-.25)&(b.eff15>=.25)&(b.friction<=.22),ss,'E12_FAILED_EXPANSION',sess,st.rel)
 c=pd.DataFrame(rows,columns=['time','side','specialist','session','horizon','checkpoint','rel_open'])
 return c.drop_duplicates(['time','side','specialist','session']).sort_values('time').reset_index(drop=True)

def attach(b,c):
 cols=['spread','atr60','atr300','atr900','tick_z','friction','r15','r30','r60','r300','r900','r3600','r14400','eff15','eff30','eff60','eff300','eff900','eff3600','eff14400','v1n','v3n','v12n','a1n','a3n','j1n','j3n','body','range','compression','vwap15_z','qp','qv']
 q=b.reindex(c.time)[cols].reset_index(drop=True)
 for col in cols:c[col]=q[col].to_numpy()
 for col in ['r15','r30','r60','r300','r900','r3600','r14400','v1n','v3n','v12n','a1n','a3n','j1n','j3n','body','qp','qv','vwap15_z']:
  c['s_'+col]=c[col]*c.side
 return c

def process(m):
 print('READ',m,flush=True);d=read_raw(m);b=build5(d);c=attach(b,candidates(b));c=c[c.time<=d.time.max()-pd.Timedelta(minutes=16)].copy()
 a=labels(c.time.astype('int64').to_numpy()//1_000_000,c.side.to_numpy(np.int64),c.horizon.to_numpy(np.int64),c.checkpoint.to_numpy(np.int64),c.spread.fillna(.1).to_numpy(float),c.atr60.fillna(.2).to_numpy(float),d.timestamp_ms_utc.to_numpy(np.int64),d.bid.to_numpy(float),d.ask.to_numpy(float))
 c['survive']=a[:,0];c['fp_win']=a[:,1];c['resolved_pnl']=a[:,2];c['month']=m
 out=ROOT/f'beta064_all12_pass1_{m:02d}.pkl';c.to_pickle(out)
 print(c.groupby('specialist').agg(n=('survive','size'),surv=('survive','mean'),fp=('fp_win','mean'),net=('resolved_pnl','sum')).to_string(),flush=True)
 del d,b,c;gc.collect()
if __name__=='__main__':process(int(sys.argv[1]))
