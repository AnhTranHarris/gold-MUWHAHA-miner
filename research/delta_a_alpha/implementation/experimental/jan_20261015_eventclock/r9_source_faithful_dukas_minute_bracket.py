"""Source-derived MQL5 R9 bracket/quality/rearm Python research port, JANUARY ONLY.
Original refs: Experts/GoldMuwahahaMiner_R9_HybridGate.mq5 Git blob
7eecb5f1947017a01ce85b2520725de54749e523.
MQL5 operations not fully broker-parity: absent stop/freeze levels, partial order failures,
Commission broker exact, fill queues, server DST and feed source. 250 ms delayed first actual
Bid/Ask quote for conservative executable research. Frozen V1 unchanged; August sealed.
"""
from pathlib import Path
import hashlib, time, json
import numpy as np,pandas as pd
from numba import njit
B=Path('/mnt/data');D=Path(__file__).parent;RAW=B/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'

@njit(cache=True)
def s1_qualities(cl,hi,lo):
  n=len(cl);dir=np.zeros(n,np.int8);eff=np.zeros(n,np.float32);rg=np.zeros(n,np.float32);turn=np.zeros(n,np.int8)
  for i in range(11,n):
    start=cl[i-10];end=cl[i-1];d=end-start;travel=0.;turns=0;older=0;high=-1e20;low=1e20
    prev=start
    for k in range(i-9,i):
      delta=cl[k]-prev;travel+=abs(delta);sgn=1 if delta>0 else (-1 if delta<0 else 0)
      if sgn and older and sgn!=older:turns+=1
      if sgn:older=sgn
      prev=cl[k]
    for k in range(i-10,i):
      if hi[k]>high:high=hi[k]
      if lo[k]<low:low=lo[k]
    eff[i]=abs(d)/(travel+1e-9);rg[i]=high-low;turn[i]=turns
    if eff[i]>=.70 and turns<=9 and rg[i]>=.5:
      if d>=.15:dir[i]=1
      if d<=-.15:dir[i]=-1
  return dir,eff,rg,turn

@njit(cache=True)
def completed_m5_atr(sec,hi,lo,cl):
  n=len(sec);frame=sec//300;idx=np.empty(n,np.int64);m=0
  for i in range(n):
    if i==0 or frame[i]!=frame[i-1]:idx[m]=i;m+=1
  idx=idx[:m];high=np.empty(m,np.float64);low=np.empty(m,np.float64);close=np.empty(m,np.float64);atr=np.empty(m,np.float64);atr[:]=np.nan
  for j in range(m):
    a=idx[j];z=idx[j+1] if j<m-1 else n;high[j]=max(hi[a:z]);low[j]=min(lo[a:z]);close[j]=cl[z-1]
  if m>15:
    sm=0.
    for j in range(1,15):sm+=max(high[j]-low[j],abs(high[j]-close[j-1]),abs(low[j]-close[j-1]))
    sm/=14.;atr[14]=sm
    for j in range(15,m):
      tr=max(high[j]-low[j],abs(high[j]-close[j-1]),abs(low[j]-close[j-1]));sm=(sm*13+tr)/14;atr[j]=sm
  out=np.empty(n,np.float64);out[:]=np.nan
  k=0
  for i in range(n):
    while k+1<m and idx[k+1]<=i:k+=1
    if k>=1:out[i]=atr[k-1]
  return out

@njit(cache=True)
def replay(ms,bid,ask,ix,sec,quality,atr,capital,spreadcap,fee=.20,stop=.30,arm=.10,trail=.03,holdsec=30,latency=250):
  # Source-faithful MINUTE reset, source signal quality and opposite rearm;
  # funded Bid/Ask fills delayed 250ms, margin assumed 1:500; no virtual overlapping profit.
  led=np.empty((70000,9),np.float64);closed=0;bank=capital;eqpeak=capital;maxdd=0.;halt=0
  minute=-1;buy_level=0.;sell_level=0.;mode=0;rearms=0;lastside=0;sid=0;last_sec=-1;pos=0
  pend=0;ptime=0;pbase=0.;sigtime=0;entry=0.;enttime=0;sl=0.;last_open=0
  total_offers=0;total_fills=0;rejected=0;spreads=0
  for i in range(len(ms)):
    now=ms[i];ss=now//1000
    if ss!=last_sec:
      sid+=1;last_sec=ss
    si=sid-1
    if si>=len(sec) or sec[si]!=ss:break
    bp=bid[i]*.001;ap=ask[i]*.001;spread=ap-bp
    mm=ss//60
    if mm!=minute:
      minute=mm;mid=(bp+ap)*.5;buy_level=mid+.15;sell_level=mid-.15;mode=2;rearms=0
      # Pending order from earlier minute is cleared when new minute starts
      pend=0
    equity=bank+((bp-entry) if pos==1 else (entry-ap))-.20 if pos else bank
    if equity>eqpeak:eqpeak=equity
    if eqpeak-equity>maxdd:maxdd=eqpeak-equity
    if equity<capital*.60:halt=1
    if pos:
      favor=bp-entry if pos==1 else entry-ap
      why=0
      if (pos==1 and bp<=sl) or (pos==-1 and ap>=sl):why=1
      elif now-enttime>=holdsec*1000:why=2
      if why:
        xp=bp if pos==1 else ap;pnl=(xp-entry)*pos-fee
        if closed<len(led):
          led[closed,0]=enttime;led[closed,1]=now;led[closed,2]=pos;led[closed,3]=entry;led[closed,4]=xp;led[closed,5]=pnl;led[closed,6]=why;led[closed,7]=sigtime;led[closed,8]=spread
          closed+=1
        bank+=pnl;lastside=pos;pos=0;mode=(-lastside if rearms<3 else 0);rearms+=1;continue
      if favor>=arm:
        cand=bp-trail if pos==1 else ap+trail
        if pos==1 and cand>sl:sl=cand
        if pos==-1 and cand<sl:sl=cand
      continue
    if pend:
      if now-ptime>6000 or mm!=ptime//60000:pend=0;rejected+=1
      elif now>=ptime+latency:
        ep=ap if pend==1 else bp
        if spread>spreadcap or abs(ep-pbase)>1.5 or ep/500.+spread+fee>bank*.8 or bank<capital*.60:
          rejected+=1;pend=0
        else:
          pos=pend;entry=ep;enttime=now;total_fills+=1;sl=(bp-stop) if pos==1 else (ap+stop)
          pend=0;mode=0;continue
    if pos or pend or halt or mode==0:continue
    if not (np.isfinite(atr[si])):continue
    hour=ss%86400//3600;minute_day=ss%86400//60
    # Jan both London/NY standard time, London 08:00-16:30, NY 13:00-22:00 UTC.
    lon=(480<=minute_day<990);ny=(780<=minute_day<1320)
    threshold=1.75 if ny else (2.0 if lon else 2.5)
    if atr[si]<threshold:continue
    if spread>spreadcap:spreads+=1;continue
    side=1 if (mode==2 or mode==1) and ap>=buy_level else (-1 if (mode==2 or mode==-1) and bp<=sell_level else 0)
    if side==0 or quality[si]!=side:continue
    pend=side;ptime=now;sigtime=now;pbase=ap if side==1 else bp;total_offers+=1
  return led[:closed],np.array([bank-capital,maxdd,halt,total_offers,total_fills,rejected,spreads,pos],np.float64)

def main():
  t=time.time();h=hashlib.sha256(RAW.read_bytes()).hexdigest();assert h==SHA
  data=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  ms=data.timestamp_ms_utc.to_numpy();bid=data.bid_raw.to_numpy();ask=data.ask_raw.to_numpy();del data
  ss=ms//1000;ix=np.r_[0,np.flatnonzero(ss[1:]!=ss[:-1])+1];bb=bid[ix].astype(float)/1000;end=np.r_[ix[1:]-1,len(ms)-1];cc=bid[end].astype(float)/1000
  hh=np.maximum.reduceat(bid,ix).astype(float)/1000;ll=np.minimum.reduceat(bid,ix).astype(float)/1000;sec=ss[ix]
  qual,eff,rg,turn=s1_qualities(cc,hh,ll);atr=completed_m5_atr(sec,hh,ll,cc)
  rows=[]
  for spreadcap in [.25,.5,.75,1.,1.25]:
    for lag in [250,750]:
      ledger,stat=replay(ms,bid,ask,ix,sec,qual,atr,100.,spreadcap,latency=lag)
      pn=ledger[:,5] if len(ledger) else np.array([])
      row={'spreadcap':spreadcap,'latency_ms':lag,'net_usd':float(stat[0]),'max_tick_dd':float(stat[1]),'capital_halt':int(stat[2]),'proposals':int(stat[3]),'fills':int(stat[4]),'rejected':int(stat[5]),'entry_spread_rejects':int(stat[6]),'end_open':int(stat[7]),'trades':len(pn),'gross_losing':float(np.minimum(pn,0).sum()),'gross_winning':float(np.maximum(pn,0).sum())}
      rows.append(row)
      if spreadcap==.25 and lag==250:
        pd.DataFrame(ledger,columns=['entry_ms','exit_ms','side','entry','exit','net','why','signal_ms','exit_spread']).to_csv(D/'NATIVE_R9_DEFAULT_SPREAD_025_LATENCY250_LEDGER.csv',index=False)
      print('PARITY',row,flush=True)
  pd.DataFrame(rows).to_csv(D/'R9_MINUTE_BRACKET_SPREAD_ECONOMIC_RECONSTRUCTION.csv',index=False)
  info={'research_only':True,'r9_mql5_hybrid_source_blob':'7eecb5f1947017a01ce85b2520725de54749e523','r9_tick_logger_source_blob':'5c7655cd3357f9126e8bffd97c34374dfb29f83e','source_file_sha256':SHA,'original_ticks':len(ms),'seconds':len(sec),'cases':len(rows),'broker_point_size_unverified':True,'stop_level_unverified':True,'source_logic_approximation':'minimum 250ms fill latency instead of synchronous native MT5 and selected broker order/capacity abstractions','owner_R9_absolute_60_gate':.6*41520.82,'max_net':max(x['net_usd'] for x in rows),'status':'INTERNAL_EXPERIMENT_NOT_PROMOTED','elapsed':time.time()-t}
  (D/'R9_SOURCE_FAITHFUL_PORT_INTERNAL_QA.json').write_text(json.dumps(info,indent=2))
if __name__=='__main__':main()