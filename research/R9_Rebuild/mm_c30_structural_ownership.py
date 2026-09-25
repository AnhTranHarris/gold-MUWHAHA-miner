import json, hashlib, time, glob, gc
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

ROOT=Path('/mnt/data')
IN=ROOT/'mmc30_struct'
OUT=ROOT/'MM_C30_STRUCTURAL_OWNERSHIP'
OUT.mkdir(exist_ok=True)
H=.10
BASELINE_JANJUL=1574.8774999999296
BASELINE_MJJ=208.83299999998508+114.16699999998718-60.874999999999545
BASELINE_TRADES=15+13+19+13+19+20+21
MIN_TRADES=int(np.ceil(BASELINE_TRADES*.70))
FILES={m:sorted(glob.glob(str(ROOT/f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz')))[0] for m in range(1,8)}

# Precommitted transparent causal grid. No May-Jul information participates in selection.
DEPTHS=[0.0,0.02,0.05,0.08,0.12,0.18]
VOL_FLOORS=[0.0,0.75,0.85,0.95,1.05]
PRIOR2=[-1e9,-0.25,0.0,0.20,0.40]

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def metrics(rows):
 x=np.asarray([float(r.pnl) for r in rows],float)
 gp=float(x[x>0].sum()) if len(x) else 0.; gl=float(x[x<0].sum()) if len(x) else 0.
 return {'trades':int(len(x)),'net':float(x.sum()) if len(x) else 0.,'gp':gp,'gl':gl,
         'pf':float(gp/(-gl)) if gl<0 else 1e9,'win':float((x>0).mean()) if len(x) else 0.0,
         'avg_hold':float(np.mean([float(r.hold) for r in rows])) if rows else 0.0}

def nonoverlap(df):
 free=-1; chosen=[]
 for r in df.sort_values('signal_ms').itertuples(index=False):
  if int(r.signal_ms)<=free or not np.isfinite(r.pnl) or int(r.exit_ms)<0: continue
  chosen.append(r); free=int(r.exit_ms)
 return chosen

def wilder(bars,n=14):
 h=bars.high.to_numpy(float); l=bars.low.to_numpy(float); c=bars.close.to_numpy(float)
 pc=np.r_[np.nan,c[:-1]]
 tr=np.maximum(h-l,np.maximum(np.abs(h-pc),np.abs(l-pc)))
 a=np.full(len(bars),np.nan)
 if len(bars)>n:
  a[n]=np.nanmean(tr[1:n+1])
  for i in range(n+1,len(bars)): a[i]=(a[i-1]*(n-1)+tr[i])/n
 return a

def feature_bars(bars):
 z=bars.sort_values('bucket').drop_duplicates('bucket').reset_index(drop=True).copy()
 # Exact C25 source lineage: derived H4 volatility state is recomputed after historical+current bars are concatenated.
 z['atr']=wilder(z)
 z['atrmean20']=z.atr.shift(1).rolling(20,min_periods=20).mean()
 z['volratio']=z.atr/z.atrmean20
 ph=z.high.shift(1).rolling(5,min_periods=5).max(); pl=z.low.shift(1).rolling(5,min_periods=5).min()
 # signed breakout depth beyond the prior 5 completed H4 bars
 up=(z.close-ph)/(z.atr+1e-12); dn=(pl-z.close)/(z.atr+1e-12)
 z['depth_long']=up; z['depth_short']=dn
 z['prior2_raw']=z.close.shift(1)-z.close.shift(3)
 z['body_raw']=z.close-z.open
 return z

def attach_features(d,bars):
 b=feature_bars(bars)[['end_ms','atr','volratio','depth_long','depth_short','prior2_raw','body_raw']]
 z=d.merge(b,left_on='signal_ms',right_on='end_ms',how='left',suffixes=('','_bar'))
 z['depth_atr']=np.where(z.side>0,z.depth_long,z.depth_short)
 atr=z.atr_bar.fillna(z.atr).to_numpy(float)
 z['prior2_al']=z.side.to_numpy(float)*z.prior2_raw.to_numpy(float)/(atr+1e-12)
 z['body_al']=z.side.to_numpy(float)*z.body_raw.to_numpy(float)/(atr+1e-12)
 return z

def load_discovery(m,bars):
 d=pd.read_pickle(IN/f'C25_OUTCOMES_{m:02d}.pkl.gz',compression='gzip')
 d=d[(d.tf=='H4')&(d.breakout==5)&(d.life=='HIST')&(d.volratio<=1.5)].copy()
 return attach_features(d,bars)

def gate(z,depth,vol_floor,prior2):
 return z[(z.depth_atr>=depth)&(z.volratio>=vol_floor)&(z.volratio<=1.5)&(z.prior2_al>=prior2)].copy()

def load_ticks(path,nrows=None):
 d=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],nrows=nrows,
               dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
 t=d.timestamp_ms_utc.to_numpy(np.int64); mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.; del d
 return t,mid

@njit(cache=True)
def sim(t,mid,sig,side,atr):
 i0=np.searchsorted(t,sig)
 if i0>=len(t): return np.nan,-1,np.nan,np.nan,np.nan
 p=mid[i0]; entry=p+H if side>0 else p-H; bid=p-H; ask=p+H
 stop=bid-atr*1.5 if side>0 else ask+atr*1.5; act=atr*.25; trail=atr*1.; ot=t[i0]; mfe=0.; mae=0.; ei=i0; mh=24*3600*1000
 for i in range(i0+1,len(t)):
  tt=t[i]; p=mid[i]; bid=p-H; ask=p+H; fav=(bid-entry) if side>0 else (entry-ask); adv=(entry-bid) if side>0 else (ask-entry)
  if fav>mfe: mfe=fav
  if adv>mae: mae=adv
  if (side>0 and bid<=stop) or (side<0 and ask>=stop):
   return ((bid-entry)*side if side>0 else (entry-ask)),tt,(tt-ot)/1000.,mfe,mae
  if tt-ot>=mh:
   return ((bid-entry)*side if side>0 else (entry-ask)),tt,(tt-ot)/1000.,mfe,mae
  if fav>=act:
   cand=bid-trail if side>0 else ask+trail
   if side>0:
    if cand>stop: stop=cand
   else:
    if cand<stop: stop=cand
  ei=i
 p=mid[ei]; bid=p-H; ask=p+H
 return ((bid-entry)*side if side>0 else (entry-ask)),t[ei],(t[ei]-ot)/1000.,mfe,mae

def forward_month(m,allbars,rule):
 # signal creation is frozen C25: H4 breakout=5, volratio<=1.5. Gate is applied using only completed signal-bar context.
 b=feature_bars(allbars)
 # month raw establishes month boundaries and execution path
 t,mid=load_ticks(FILES[m]); first=int(t[0]); last=int(t[-1])
 rows=[]
 for i in range(21,len(b)):
  sig=int(b.end_ms.iloc[i])
  if not(first<=sig<=last+14400*1000): continue
  atr=float(b.atr.iloc[i]); vr=float(b.volratio.iloc[i])
  if not np.isfinite(atr) or not np.isfinite(vr) or vr>1.5: continue
  ph=float(b.high.iloc[i-5:i].max()); pl=float(b.low.iloc[i-5:i].min()); cl=float(b.close.iloc[i])
  side=1 if cl>ph else (-1 if cl<pl else 0)
  if not side: continue
  depth=((cl-ph) if side>0 else (pl-cl))/(atr+1e-12)
  prior2=side*(float(b.close.iloc[i-1])-float(b.close.iloc[i-3]))/(atr+1e-12)
  # first generate all frozen baseline signals; rule marks ownership eligibility
  take=(depth>=rule['depth']) and (vr>=rule['vol_floor']) and (prior2>=rule['prior2'])
  rows.append((sig,side,atr,vr,depth,prior2,take))
 if m<7:
  tn,mn=load_ticks(FILES[m+1],nrows=2000000); t=np.concatenate([t,tn]); mid=np.concatenate([mid,mn]); del tn,mn; gc.collect()
 outs=[]
 for sig,side,atr,vr,depth,prior2,take in rows:
  p,ex,h,mfe,mae=sim(t,mid,sig,side,atr)
  outs.append((sig,side,atr,vr,depth,prior2,take,p,ex,h,mfe,mae))
 d=pd.DataFrame(outs,columns=['signal_ms','side','atr','volratio','depth_atr','prior2_al','take','pnl','exit_ms','hold','mfe','mae'])
 base=metrics(nonoverlap(d))
 cand=metrics(nonoverlap(d.loc[d['take'].astype(bool)]))
 return d,base,cand

def main():
 started=time.time()
 jan04=pd.read_pickle(IN/'H4_bars_Jan04.pkl.gz',compression='gzip')
 D={m:load_discovery(m,jan04) for m in range(1,5)}
 base={m:metrics(nonoverlap(D[m])) for m in range(1,5)}
 rows=[]
 for dep in DEPTHS:
  for vf in VOL_FLOORS:
   for pr in PRIOR2:
    mm={m:metrics(nonoverlap(gate(D[m],dep,vf,pr))) for m in range(1,5)}
    disc_ok=all(mm[m]['trades']>=8 and mm[m]['net']>0 for m in [1,2,3])
    apr_ok=mm[4]['trades']>=7 and mm[4]['net']>0
    retain=sum(mm[m]['net'] for m in range(1,5))/sum(base[m]['net'] for m in range(1,5))
    # Robust freeze: all discovery + April positive, retain >=80% Jan-Apr PnL.
    eligible=disc_ok and apr_ok and retain>=.80
    score=min(mm[m]['pf'] for m in range(1,5)) if eligible else -1
    rows.append({'depth':dep,'vol_floor':vf,'prior2':pr,'eligible':eligible,'retain_janapr':retain,'score':score,
                 **{f'm{m}_net':mm[m]['net'] for m in range(1,5)},**{f'm{m}_trades':mm[m]['trades'] for m in range(1,5)},
                 **{f'm{m}_pf':mm[m]['pf'] for m in range(1,5)}})
 grid=pd.DataFrame(rows).sort_values(['eligible','score','retain_janapr'],ascending=[False,False,False])
 if not bool(grid.iloc[0].eligible):
  rule={'depth':0.0,'vol_floor':0.0,'prior2':-1e9}; freeze_status='NO_ELIGIBLE_RULE'
 else:
  r=grid.iloc[0]; rule={'depth':float(r.depth),'vol_floor':float(r.vol_floor),'prior2':float(r.prior2)}; freeze_status='FROZEN'
 grid.to_csv(OUT/'MM_C30_STRUCTURAL_DISCOVERY.csv',index=False)
 # Assemble previously completed H4 bars and run untouched forward May-Jul exactly once.
 bars=jan04.copy()
 forward={}; artifacts=[]
 for m in [5,6,7]:
  cur=pd.read_pickle(IN/f'H4_bars_{m:02d}.pkl.gz',compression='gzip')
  bars=pd.concat([bars,cur],ignore_index=True).drop_duplicates('bucket').sort_values('bucket').reset_index(drop=True)
  d,bm,cm=forward_month(m,bars,rule)
  d.to_pickle(OUT/f'MM_C30_STRUCT_M{m:02d}.pkl.gz',compression='gzip')
  forward[m]={'baseline':bm,'candidate':cm}
  artifacts.append(OUT/f'MM_C30_STRUCT_M{m:02d}.pkl.gz')
 # Candidate Jan-Apr metrics from frozen rule
 cand14={m:metrics(nonoverlap(gate(D[m],**rule))) for m in range(1,5)}
 janjul_net=sum(cand14[m]['net'] for m in range(1,5))+sum(forward[m]['candidate']['net'] for m in [5,6,7])
 janjul_trades=sum(cand14[m]['trades'] for m in range(1,5))+sum(forward[m]['candidate']['trades'] for m in [5,6,7])
 mjj_net=sum(forward[m]['candidate']['net'] for m in [5,6,7])
 all_month_nets=[cand14[m]['net'] for m in range(1,5)]+[forward[m]['candidate']['net'] for m in [5,6,7]]
 promoted=(freeze_status=='FROZEN' and all(x>0 for x in all_month_nets) and mjj_net>BASELINE_MJJ and janjul_net>BASELINE_JANJUL and janjul_trades>=MIN_TRADES)
 result={
  'job_id':'MM-C30-A-STRUCTURAL-OWNERSHIP','status':'COMPLETED_LOCAL','freeze_status':freeze_status,'rule':rule,
  'selection_contract':{'discovery':'Jan-Mar','calibration':'April','forward':'May-Jul untouched','min_discovery_trades_per_month':8,'min_april_trades':7,'min_janapr_profit_retention':0.80,
                        'promotion_requires_all_7_positive':True,'promotion_requires_mjj_gt_baseline':BASELINE_MJJ,'promotion_requires_janjul_gt_baseline':BASELINE_JANJUL,'min_total_trades':MIN_TRADES},
  'baseline_janapr':base,'candidate_janapr':cand14,'forward':forward,
  'candidate_janjul_net':janjul_net,'candidate_janjul_trades':janjul_trades,'candidate_mjj_net':mjj_net,
  'baseline_janjul_net':BASELINE_JANJUL,'baseline_mjj_net':BASELINE_MJJ,'baseline_trades':BASELINE_TRADES,
  'all_month_nets':all_month_nets,'promotion':'BREAKTHROUGH' if promoted else 'REJECTED',
  'elapsed_seconds':time.time()-started,
  'inputs':{str(p):sha256(p) for p in list(IN.glob('C25_OUTCOMES_*.pkl.gz'))+list(IN.glob('H4_bars_*.pkl.gz'))},
  'raw_inputs':{str(m):{'path':FILES[m],'sha256':sha256(FILES[m])} for m in [5,6,7]},
 }
 for p in artifacts: result.setdefault('artifact_sha256',{})[p.name]=sha256(p)
 with open(OUT/'MM_C30_STRUCTURAL_RESULT.json','w') as f: json.dump(result,f,indent=2,sort_keys=True)
 print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
