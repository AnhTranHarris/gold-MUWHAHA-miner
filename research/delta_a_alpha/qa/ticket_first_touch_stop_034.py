"""Tick-causal quote-side candidate tape stop tests; no normalized fills or future-bar use.
Original January 131E source candidates remain frozen: changing exits does NOT recreate
funded Watchdog genealogy. Interpret as micro-risk sensitivity, not final whitepaper V1.
"""
from pathlib import Path
import pandas as pd,numpy as np,json,time
from numba import njit
O=Path('/mnt/data/daa_jan_risk_research_034')
@njit(cache=True)
def find_stops(t,a,b,E,X,R,D,S,m5,m15,stop_raw,minage_ms,confirmation):
 xx=X.copy();pp=np.empty(len(E),np.float64);triggered=0
 for k in range(len(E)):
  d=int(D[k]);ent=int(E[k]);end=int(X[k]);en=int(R[k]);xp=int(b[end] if d>0 else a[end]);ix=end
  if S[k]==0 and stop_raw>0:
   for j in range(ent+1,end):
    if t[j]-t[ent]<minage_ms:continue
    if confirmation==1 and m5[j]!=-d:continue
    if confirmation==2 and m5[j]!=-d and m15[j]!=-d:continue
    px=int(b[j] if d>0 else a[j])
    if d*(px-en)<=-stop_raw:ix=j;xp=px;triggered+=1;break
  xx[k]=ix;pp[k]=d*(xp-en)/1000.-.02
 return xx,pp,triggered

@njit(cache=True)
def equity_sweep(a,b,E,X,R,D,S,P):
 ke=np.argsort(E);kx=np.argsort(X);n=len(E);j=0;k=0;nl=np.zeros(8,np.int64);ns=np.zeros(8,np.int64);el=np.zeros(8,np.int64);es=np.zeros(8,np.int64);bal=np.zeros(8,np.float64)
 pk=100000.;dd=0.;maxop=0;peak_i=0;tr_i=0
 for i in range(len(a)):
  while k<n and X[kx[k]]==i:
   q=kx[k];g=S[q];d=D[q];ep=R[q];k+=1
   if d>0:nl[g]-=1;el[g]-=ep
   else:ns[g]-=1;es[g]-=ep
   bal[g]+=P[q]
  while j<n and E[ke[j]]==i:
   q=ke[j];g=S[q];d=D[q];ep=R[q];j+=1
   if d>0:nl[g]+=1;el[g]+=ep
   else:ns[g]+=1;es[g]+=ep
  eq=100000.;op=0
  for g in range(8):
   eq+=bal[g]+(nl[g]*int(b[i])-el[g]+es[g]-ns[g]*int(a[i]))/1000.-.02*(nl[g]+ns[g]);op+=nl[g]+ns[g]
  if eq>pk:pk=eq;peak_i=i
  if pk-eq>dd:dd=pk-eq;tr_i=i
  if op>maxop:maxop=op
 return dd,maxop,peak_i,tr_i

def main():
 raw=pd.read_csv('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
 t=raw.timestamp_ms_utc.to_numpy();a=raw.ask_raw.to_numpy();b=raw.bid_raw.to_numpy()
 z=np.load('/mnt/data/daa_jan_risk_audit_033/JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz');E,X,R,D,S=[z[k] for k in ['entry_index','exit_index','entry_price_raw','direction','source_id']]
 import sys;sys.path.insert(0,'/mnt/data/daa_jan_exact_032');from stmr_base import bar_states
 mid=(a.astype(np.int64)+b.astype(np.int64))//2;m5=bar_states(t,mid,300000);m15=bar_states(t,mid,900000)
 configs=[('unmodified',0,0,0),('stop3',3000,0,0),('stop5',5000,0,0),('stop8',8000,0,0),('stop12',12000,0,0),('stop16',16000,0,0),('stop25',25000,0,0),('stop8_age15s',8000,15000,0),('stop12_age15s',12000,15000,0),('stop8_age60s',8000,60000,0),('stop12_age60s',12000,60000,0),('stop8_m5_reversal',8000,0,1),('stop12_m5_reversal',12000,0,1),('stop8_m5_or_m15',8000,0,2),('stop12_m5_or_m15',12000,0,2),('stop12_age15_m5',12000,15000,1),('stop16_age15_m5',16000,15000,1)]
 for name,stop,age,conf in configs:
  start=time.monotonic();xi,p,changed=find_stops(t,a,b,E,X,R,D,S,m5,m15,stop,age,conf)
  dd,mo,pk,tr=equity_sweep(a,b,E,xi,R,D,S,p)
  gp=float(p[p>0].sum());gl=float(p[p<0].sum())
  obj={'scenario':name,'stop_raw':stop,'minimum_live_age_ms':age,'completed_tf_confirm':conf,'net':round(float(p.sum()),3),'trades':len(p),'gross_profit':round(gp,3),'gross_loss':round(gl,3),'PF':round(gp/-gl,4),'win_pct':round(100*float(np.mean(p>0)),2),'equity_dd':round(float(dd),3),'max_open':int(mo),'WD_net':round(float(p[S==0].sum()),3),'hourly_net':round(float(p[S==1].sum()),3),'WD_earlier_exits':int(changed),'maxDD_trough_tick':int(tr),'seconds':round(time.monotonic()-start,2)}
  if name=='unmodified':assert abs(obj['net']-93425.311)<.01 and abs(dd-56921.6)<.1,obj
  (O/(name+'.json')).write_text(json.dumps(obj,indent=2))
  np.savez_compressed(O/(name+'_trade_ledger.npz'),E=E,X=xi,P=p,S=S,D=D)
  print('CHECKPOINT',json.dumps(obj),flush=True)
if __name__=='__main__':main()