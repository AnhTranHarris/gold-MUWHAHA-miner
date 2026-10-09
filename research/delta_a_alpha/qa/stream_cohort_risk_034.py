"""Original January 131E source-candidate *counterfactual overlay*, real Dukascopy Bid/Ask only.
All original parent proposals remain frozen: NOT full physical Watchdog genealogy parity.
Controls use current quotes and funded-book state; never improve results from future ticks.
"""
import pandas as pd,numpy as np,json,time
from numba import njit
from pathlib import Path
OUT=Path('/mnt/data/daa_jan_risk_research_034')
@njit(cache=True)
def run(t,a,b,E,X,R,D,S,M5,M15,per_tick,max_wd,loss_limit,lock_ms,min_wd,impulse,recover,spread_gate=0):
 n=len(E); oi=np.argsort(E); ox=np.argsort(X)
 status=np.zeros(n,np.uint8);link=np.full(n,-1,np.int64);head=-1
 nl=np.zeros(8,np.int64);ns=np.zeros(8,np.int64);el=np.zeros(8,np.int64);es=np.zeros(8,np.int64);bal=np.zeros(8,np.float64)
 p=np.empty(n+1000,np.float64);eg=np.empty(n+1000,np.int8);exi=np.empty(n+1000,np.int64);reason=np.empty(n+1000,np.int8);z=0
 j=0;k=0;wdopen=0;blocked=0;filtered=0;clipped=0;forced=0;stopevents=0;imp_events=0
 lastidx=-1;on_tick=0;peak=100000.;dd=0.;peak_i=0;open_max=0;firstfive=0;lastfive=0;five_lo=0;five_hi=0
 # independent L6 recovery at most one 0.01 lot per closed WD cohort
 rec_live=0; rec_dir=0; rec_entry=0;rec_deadline=0;rec_pending=0;rec_ref=0;rec_pending_expiry=0
 for i in range(len(t)):
  ti=t[i];ask=int(a[i]);bid=int(b[i]);mid=(ask+bid)//2
  if ti-t[firstfive]>5000: firstfive=i;five_lo=mid;five_hi=mid
  elif mid<five_lo:five_lo=mid
  elif mid>five_hi:five_hi=mid
  while k<n and X[ox[k]]==i:
   u=ox[k];k+=1
   if status[u]!=1:continue
   g=S[u];d=D[u];ep=R[u];v=d*((bid if d>0 else ask)-ep)/1000.-.02
   if d>0:nl[g]-=1;el[g]-=ep
   else:ns[g]-=1;es[g]-=ep
   bal[g]+=v;status[u]=2;p[z]=v;eg[z]=g;exi[z]=i;reason[z]=0;z+=1
   if g==0: wdopen-=1 # linked list retains stale nodes; skip those during cohort stop
  if rec_live:
   price=bid if rec_dir>0 else ask;ret=rec_dir*(price-rec_entry)
   if ret>=6000 or ret<=-3000 or ti>=rec_deadline:
    v=ret/1000.-.02;bal[7]+=v;p[z]=v;eg[z]=7;exi[z]=i;reason[z]=4;z+=1;rec_live=0
  while j<n and E[oi[j]]==i:
   u=oi[j];j+=1;g=S[u];d=D[u];ep=R[u]
   if g==0:
    if i!=lastidx:lastidx=i;on_tick=0
    if ti<blocked:filtered+=1;status[u]=3;continue
    if wdopen>=max_wd:clipped+=1;status[u]=3;continue
    if on_tick>=per_tick and (spread_gate==0 or ask-bid>=spread_gate):filtered+=1;status[u]=3;continue
    on_tick+=1
   if d>0:nl[g]+=1;el[g]+=ep
   else:ns[g]+=1;es[g]+=ep
   status[u]=1
   if g==0:link[u]=head;head=u;wdopen+=1
  wf=(nl[0]*bid-el[0]+es[0]-ns[0]*ask)/1000.-.02*wdopen
  bad=loss_limit>0 and wdopen>=min_wd and wf<=-loss_limit
  imp=impulse>0 and wdopen>=min_wd and ((ns[0]>nl[0] and mid-five_lo>=impulse) or (nl[0]>ns[0] and five_hi-mid>=impulse))
  if bad or imp:
   d=-1 if ns[0]>nl[0] else 1
   u=head
   while u>=0:
    nxt=link[u]
    if status[u]==1:
     ep=R[u];di=D[u];v=di*((bid if di>0 else ask)-ep)/1000.-.02
     if di>0:nl[0]-=1;el[0]-=ep
     else:ns[0]-=1;es[0]-=ep
     status[u]=2;bal[0]+=v;p[z]=v;eg[z]=0;exi[z]=i;reason[z]=2;z+=1;forced+=1
    u=nxt
   head=-1;wdopen=0;blocked=ti+lock_ms
   if bad:stopevents+=1
   if imp:imp_events+=1
   if recover: rec_pending=-d;rec_ref=mid;rec_pending_expiry=ti+60000
  if recover and not rec_live and rec_pending and ti<rec_pending_expiry and (M5[i]==rec_pending or M15[i]==rec_pending) and rec_pending*(mid-rec_ref)>=1000 and ask-bid<=2000:
   rec_dir=rec_pending;rec_entry=ask if rec_dir>0 else bid;rec_deadline=ti+90000;rec_pending=0;rec_live=1
  if ti>=rec_pending_expiry:rec_pending=0
  eq=100000.+bal[7];op=rec_live
  for g in range(7):
   eq+=bal[g]+(nl[g]*bid-el[g]+es[g]-ns[g]*ask)/1000.-.02*(nl[g]+ns[g]);op+=nl[g]+ns[g]
  if rec_live:eq+=rec_dir*((bid if rec_dir>0 else ask)-rec_entry)/1000.-.02
  if eq>peak:peak=eq;peak_i=i
  if peak-eq>dd:dd=peak-eq
  if op>open_max:open_max=op
 if rec_live:
  v=rec_dir*((b[-1] if rec_dir>0 else a[-1])-rec_entry)/1000.-.02;p[z]=v;eg[z]=7;exi[z]=len(t)-1;reason[z]=5;z+=1
 return p[:z],eg[:z],exi[:z],reason[:z],dd,open_max,forced,stopevents,imp_events,filtered,clipped

def main():
 raw=pd.read_csv('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
 t=raw.timestamp_ms_utc.to_numpy();a=raw.ask_raw.to_numpy();b=raw.bid_raw.to_numpy()
 z=np.load('/mnt/data/daa_jan_risk_audit_033/JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz')
 import sys;sys.path.insert(0,'/mnt/data/daa_jan_exact_032');from stmr_base import bar_states
 mid=(a.astype(np.int64)+b.astype(np.int64))//2;m5=bar_states(t,mid,300000);m15=bar_states(t,mid,900000)
 E,X,R,D,S=[z[k] for k in ['entry_index','exit_index','entry_price_raw','direction','source_id']]
 configs=[('base',999,640,0,0,1,0,0),('clone64',64,640,0,0,1,0,0),('clone16',16,640,0,0,1,0,0),('wd128',999,128,0,0,1,0,0),('wd64',999,64,0,0,1,0,0),('loss5000',999,640,5000,60000,32,0,0),('loss2000',999,640,2000,60000,32,0,0),('loss1000',999,640,1000,60000,32,0,0),('loss2000_cool300',999,640,2000,300000,32,0,0),('loss2000_recovery',999,640,2000,60000,32,0,1),('impulse5',999,640,0,60000,32,5000,0),('clone64_loss2000',64,640,2000,60000,32,0,0),('clone64_loss2000_impulse5',64,640,2000,60000,32,5000,0),('clone64_loss2000_impulse5_recovery',64,640,2000,60000,32,5000,1),('clone96',96,640,0,0,1,0,0),('clone128',128,640,0,0,1,0,0),('clone192',192,640,0,0,1,0,0),('clone256',256,640,0,0,1,0,0),('clone384',384,640,0,0,1,0,0),('clone512',512,640,0,0,1,0,0),('clone64_spread1',64,640,0,0,1,0,0),('clone64_spread1p5',64,640,0,0,1,0,0),('clone64_spread2',64,640,0,0,1,0,0),('clone64_spread2p5',64,640,0,0,1,0,0),('clone64_spread3',64,640,0,0,1,0,0),('clone128_spread1p5',128,640,0,0,1,0,0),('clone128_spread2',128,640,0,0,1,0,0),('clone192_spread1p5',192,640,0,0,1,0,0),('clone192_spread2',192,640,0,0,1,0,0),('clone192_spread2p5',192,640,0,0,1,0,0),('clone256_spread1p5',256,640,0,0,1,0,0),('clone256_spread2',256,640,0,0,1,0,0),('clone64_wd256',64,256,0,0,1,0,0),('clone128_wd256',128,256,0,0,1,0,0),('clone192_wd256',192,256,0,0,1,0,0),('clone192_wd384',192,384,0,0,1,0,0),('clone256_wd384',256,384,0,0,1,0,0)]
 for name,pc,c,loss,lock,minw,imp,rec in configs:
        if (OUT/(name+'.json')).exists():continue
        spread_gate=(1000 if name.endswith('spread1') else 1500 if name.endswith('spread1p5') else 2000 if name.endswith('spread2') else 2500 if name.endswith('spread2p5') else 3000 if name.endswith('spread3') else 0)
        start=time.monotonic();p,s,x,why,dd,mo,forced,events,impevents,filt,clipped=run(t,a,b,E,X,R,D,S,m5,m15,pc,c,loss,lock,minw,imp,rec,spread_gate)
        gp=float(p[p>0].sum());gl=float(p[p<0].sum());out={'scenario':name,'params':{'max_same_tick_WD':pc,'max_WD_open':c,'stop_cohort_usd':loss,'cooldown_ms':lock,'min_WD_positions':minw,'observed_5s_impulse_raw':imp,'recovery_enabled':bool(rec),'same_tick_cap_only_if_entry_spread_at_least':spread_gate},'net':round(float(p.sum()),3),'trades':len(p),'gross_profit':round(gp,3),'gross_loss':round(gl,3),'PF':round(gp/-gl,4),'win_pct':round(100*float(np.mean(p>0)),2),'max_equity_dd':round(dd,2),'max_open':int(mo),'WD_net':round(float(p[s==0].sum()),3),'hourly_net':round(float(p[s==1].sum()),3),'recovery_net':round(float(p[s==7].sum()),3),'recovery_trades':int((s==7).sum()),'cohort_exit_count':int(forced),'cohort_stop_events':int(events),'impulse_events':int(impevents),'rejected':int(filt),'capacity_blocked':int(clipped),'seconds':round(time.monotonic()-start,2)}
        if name=='base':
            assert len(p)==47511,(len(p),float(p.sum()));assert abs(float(p.sum())-93425.311)<.01,(float(p.sum()));assert abs(dd-56921.6)<.1,dd
        # persist exit timestamps and source PnL for detailed daily/weekly once scenario selected
        (OUT/(name+'.json')).write_text(json.dumps(out,indent=2))
        np.savez_compressed(OUT/(name+'_trades.npz'),p=p,s=s,x=x,reason=why)
        print('CHECKPOINT',json.dumps(out),flush=True)
if __name__=='__main__':main()