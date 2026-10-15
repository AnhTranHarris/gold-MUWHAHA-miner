"""JANUARY original-tick finite multi-regime replenishment study.
Original R9 generated-tick results supply benchmarks, not live data or fills.
Tests causal, previously completed 1s, 5s, 15s bar geometry against a held-fixed
squeeze+M1 shield+M5 ATR runner: one funded position, exact real Bid/Ask.
All negative trials preserved; no live-mode changes.
"""
from pathlib import Path
import sys,time,json,hashlib
import numpy as np,pandas as pd
B=Path('/mnt/data'); D=Path(__file__).parent; J=B/'jan_new_discovery_20261014'
sys.path[:0]=[str(D),str(J),str(B)]
from r9_teacher_informed_dukas_executor import features
from r9_teacher_community_dukas_jan_causal_mutations_20261014 import bar_groups,prev_frame_index
from jan_r9_teacher_m1_phase_risk_v1 import replay_phase,COLS
RAW=B/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
PIN='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
Z=J/'jan_parent_causal_squeeze_signals.npz'
OUT=D/'JAN_FRESH_R9_M1_M5_H1_FAST_GRID_REPLENISHMENT';OUT.mkdir(exist_ok=True)

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def sign(x):return np.sign(x).astype('int8')

def construct(sec,hi,lo,cl,f):
 n=len(sec); old=np.r_[np.nan,cl[:-1]];old2=np.r_[np.nan,np.nan,cl[:-2]]
 price=np.nan_to_num(old-old2); candidates={}
 prev={};hi0={};lo0={};av={}
 for w in (5,15,60,300,3600):
  ep,c,h,l=bar_groups(sec,hi,lo,cl,w)
  k,valid=prev_frame_index(ep,sec,w)
  k0=np.clip(k,0,len(c)-1);good=valid&(k>=1)
  pre=np.full(n,np.nan);pre[good]=c[k0[good]]
  b=np.full(n,np.nan);b[good]=c[np.maximum(0,k0[good]-1)]
  prev[w]=pre;hi0[w]=np.where(good,h[k0],np.nan);lo0[w]=np.where(good,l[k0],np.nan)
  av[w]=np.where(good,pre-b,np.nan)
  print('geometry',w,'bars',len(ep),flush=True)
 # completed M1 5,15s direction; completed m5 ATR values from underlying source.
 atr=f[300][1]
 # Reclaim after >0.1 break of last completed 5/15s high on last 2 observed seconds
 for width in (5,15):
  for gap in (.10,.25,.5):
   for delta in (.15,.4,.75):
    s=np.zeros(n,np.int8);upper=hi0[width];lower=lo0[width]
    valid=np.isfinite(upper)&np.isfinite(lower)&(atr>3.5)
    # compare last closed second (old) with prior (old2) and completed range; a rounded measure of as-of mean-reverting failure
    sf=valid&(old2>=upper+gap)&(old<upper-gap/2)&(price<-delta) # failed bullish break short
    lf=valid&(old2<=lower-gap)&(old>lower+gap/2)&(price>delta) # failed bearish break long
    s[sf]=-1;s[lf]=1
    candidates[f'RECLAIM_{width}S_G{gap:.2f}_D{delta:.2f}']=s
 # completed 5s trend and last completed 1sec directional regain after an adverse 1sec
 for thr in (.35,.65,1.0):
  for wt in (5,15):
   for mode in ('ALIGNED','OPPOSED'):
    s=np.zeros(n,np.int8)
    slope=sign(av[wt]); ht=sign(av[3600]);mm=sign(av[300])
    cond=np.isfinite(av[wt])&(np.abs(av[wt])>thr)&(np.abs(price)>thr/2)&(atr>3.95)
    d=sign(price)
    cond &= d==slope
    cond &= (mm==d) if mode=='ALIGNED' else (mm==-d)
    s[cond&(d>0)]=1;s[cond&(d<0)]=-1
    candidates[f'REIGNITE_{wt}S_{mode}_D{thr:.2f}']=s
 # 15s range rotation: divergent price reversion to completed 15s mid vs price slope, only if within broad H1 drift limit
 for gap in (.3,.6,1.):
  for size in (1.,2.):
   s=np.zeros(n,np.int8);mid=(hi0[15]+lo0[15])/2
   ntrend=np.abs(av[300])<size
   cond=np.isfinite(mid)&np.isfinite(av[300])&ntrend&(atr>2)
   s[cond&(old>mid+gap)&(price<-.2)]=-1
   s[cond&(old<mid-gap)&(price>.2)]=1
   candidates[f'ROTATION15_G{gap:.2f}_T{size:.2f}']=s
 return candidates

def score(lbl,led,st):
 net=float(st[0]); pn=led[:,6] if len(led) else np.zeros(0);win=np.maximum(pn,0).sum();loss=np.minimum(pn,0).sum()
 if len(led):
  dates=pd.to_datetime(led[:,2],unit='ms',utc=True);h=dates.floor('h');days=dates.floor('D')
  hour=pd.DataFrame({'h':h,'net':pn}).groupby('h').net.sum();day=pd.DataFrame({'d':days,'net':pn}).groupby('d').net.sum()
  pos_h=int((hour>0).sum());neg_h=int((hour<0).sum());pos_d=int((day>0).sum());neg_d=int((day<0).sum());worsthour=float(hour.min());half1=float(pn[dates.day<=15].sum());half2=float(pn[dates.day>15].sum())
 else:pos_h=neg_h=pos_d=neg_d=0;worsthour=half1=half2=0.
 return dict(name=lbl,net=round(net,5),trades=len(led),gross_loss=round(float(loss),5),gross_win=round(float(win),5),pf=round(float(win/-loss),5) if loss<0 else None,dd=round(float(st[2]),5),halt=int(st[3]),active_hours=pos_h+neg_h,positive_hours=pos_h,negative_hours=neg_h,positive_days=pos_d,negative_days=neg_d,worst_net_hour=round(worsthour,5),first_half=round(half1,5),second_half=round(half2,5),offered=int(st[4]))

def main():
 t=time.time();assert sha(RAW)==PIN
 raw=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
 ms=raw.timestamp_ms_utc.to_numpy();b=raw.bid_raw.to_numpy();a=raw.ask_raw.to_numpy();del raw
 sec,first,hi,lo,cl,f=features(ms,b);atr=f[300][1]
 src=np.load(Z); assert np.array_equal(sec,src['sec']);parent=src['signal'];cand=construct(sec,hi,lo,cl,f)
 dummy=np.zeros(len(sec),np.int8)
 cfg=np.array([[7.,20.,5.,2.5,1500.],[7.,40.,7.,3.5,1500.]])
 before,ss=replay_phase(ms,b,a,sec,parent,atr,dummy,dummy,100.,cfg,1,-1,999.,0.,2,59,(1<<24)-1)
 summary=[score('FROZEN_PHASE_ATR_PARENT',before,ss)]; pd.DataFrame(before,columns=COLS).to_csv(OUT/'ORIGINAL_VERIFIED_CONTROL_LEDGER.csv',index=False)
 print('BASE',summary[-1],flush=True)
 tests=[]; champs=[]
 for index,(name,x) in enumerate(cand.items()):
  amount=int(np.count_nonzero(x))
  if amount>0:
   # Always stand-alone first; composite takes original parent's source priority.
   for mode in ('standalone','union'):
    sig=x if mode=='standalone' else np.where(parent!=0,parent,x).astype(np.int8)
    # Original phase-minute shield enforced on all event sources.
    trade,st=replay_phase(ms,b,a,sec,sig,atr,dummy,dummy,100.,cfg,1,-1,999.,0.,2,59,(1<<24)-1)
    row=score(name+':'+mode,trade,st);row['proposals']=amount;tests.append(row)
    if mode=='union' and row['net']>summary[0]['net'] and row['gross_loss']>=summary[0]['gross_loss'] and row['trades']>summary[0]['trades'] and not row['halt']:
     champs.append((row['net'],row,trade.copy()))
  if index%12==0:print('PROGRESS',index,len(cand),round(time.time()-t,2),'best',max([k['net'] for k in tests],default=0),flush=True)
 pd.DataFrame(summary+tests).to_csv(OUT/'ALL_CAUSAL_CANDIDATE_TRIALS.csv',index=False)
 champs.sort(key=lambda x:x[0],reverse=True)
 for idx,(_,row,trade) in enumerate(champs[:3],1):pd.DataFrame(trade,columns=COLS).to_csv(OUT/f'UNION_CANDIDATE_{idx}_LEDGER.csv',index=False)
 top=sorted(tests,key=lambda row:row['net'],reverse=True)[:12]
 report={'raw_original_sha256':PIN,'tick_count':len(ms),'source_parent_events':int(np.count_nonzero(parent)),'candidate_families':len(cand),'tested_configurations':len(tests),'benchmark':{'r9_coinexx_synth_hourly_net_active_mean_usd':41520.82/480,'r9_coinexx_synth_hourly_trades_active_mean':27980/480,'r9_coinexx_synth_monthly_net':41520.82,'r9_coinexx_synth_gross_loss':-1827.87,'r9_coinexx_synth_active_hours':480},'control':summary[0],'winner_count_meeting_joint_gate':len(champs),'best_replays':top,'status':'JANUARY_IN_SAMPLE_RESEARCH_ONLY'}
 (OUT/'RUN_SUMMARY.json').write_text(json.dumps(report,indent=2))
 print('FINAL',json.dumps(report,indent=2)[:7000],flush=True)
if __name__=='__main__':main()
