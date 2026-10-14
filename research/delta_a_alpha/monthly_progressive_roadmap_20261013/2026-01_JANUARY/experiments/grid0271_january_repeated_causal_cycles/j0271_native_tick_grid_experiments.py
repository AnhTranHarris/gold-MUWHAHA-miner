"""GRID0271: explicit nonpromoted causal grid SOURCE hypothesis, full Jan original Dukascopy quotes.
This is NOT the frozen full L0-L7 V1 nor the original Watchdog119 machine: it is a falsifiable
research source probe. One accepted entry/exit action per UTC tick; sequential 250ms latency,
actual Ask->Bid/Bid->Ask, fixed 0.01 XAUUSD lot=1oz, 20 cents per completed position.
No date/month name features, no hindsight, no Martingale; observed tick event price crossing.
"""
from pathlib import Path
import pandas as pd,numpy as np,json,time,csv
from numba import njit
BASE=Path('/mnt/data/GRID0271_JAN_RESEARCH');OUT=BASE/'JAN_ORIGINAL_TICK_COUNTERFACTUAL';OUT.mkdir(exist_ok=True)
src=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
@njit(cache=True)
def backtest(t,ask,bid,q_gap,spread_limit,stop,target,max_hold_ms,max_open,side_mode,confirm5,require_wins4,cooldown_ms):
 # caller uses January original UTC timestamps, avoids any platform-clock inference
 n=len(t);mid=np.empty(n,np.int64)
 for i in range(n):mid[i]=np.int64(ask[i])+np.int64(bid[i])
 # 1 action per original market-tick, strict pending 250ms, finite-expiry
 pos_side=np.zeros(max_open,np.int8);pos_ms=np.zeros(max_open,np.int64);pos_entry=np.zeros(max_open,np.float64)
 pos_n=0;pending_at=-1;pending_side=0;pending_until=-1;pending_raw=0
 grid_reference=mid[0];last_signal_ms=-1_000_000;past5_idx=0
 fee=.20;cash=100000.;high=100000.;maxdd=0.;maxpos=0
 closed=0;win=0;gp=0.;gl=0.;cntsig=0;rejectspread=0;rejectcap=0;expired=0
 proves=0;renewable=False;renew_adm=0;tick_actions=0;last_scout_ms=-1_000_000
 dnum=np.empty(100000,np.int32);dpnl=np.empty(100000,np.float64);closed_t=np.empty(100000,np.int64)
 for i in range(n):
  ms=t[i];this_mid=mid[i];sp=(ask[i]-bid[i])/1000.;action=False
  # Real quote at this tick can settle at most ONE existing position
  for k in range(pos_n):
   sg=pos_side[k];px=(bid[i] if sg==1 else ask[i])/1000.;fav=(px-pos_entry[k])*sg
   outcome=0
   if fav<=-stop:outcome=1
   elif fav>=target:outcome=2
   elif ms-pos_ms[k]>=max_hold_ms:outcome=3
   if outcome:
    pnl=fav-fee;cash+=pnl;gp+=max(0.,pnl);gl+=min(0.,pnl);closed+=1;win+=pnl>0
    if closed<=100000:
     dnum[closed-1]=int(ms//86400000);dpnl[closed-1]=pnl;closed_t[closed-1]=ms
    proves=proves+1 if (pnl>0 and ms-pos_ms[k]<=60000) else 0
    if proves>=4:renewable=True
    elif pnl<=0:renewable=False
    pos_n-=1
    if k<pos_n:pos_side[k]=pos_side[pos_n];pos_ms[k]=pos_ms[pos_n];pos_entry[k]=pos_entry[pos_n]
    action=True;tick_actions+=1;break
  # Tick-by-tick floating equity, not just closed positions
  eq=cash
  for k in range(pos_n):eq+=((bid[i] if pos_side[k]==1 else ask[i])/1000.-pos_entry[k])*pos_side[k]-fee
  high=max(high,eq);maxdd=max(maxdd,high-eq)
  if action:continue
  if pending_at>=0 and ms>=pending_at:
   if ms>pending_until:expired+=1
   elif pos_n<max_open and sp<=spread_limit:
    pos_side[pos_n]=pending_side;pos_ms[pos_n]=ms;pos_entry[pos_n]=(ask[i] if pending_side==1 else bid[i])/1000.;pos_n+=1
    maxpos=max(maxpos,pos_n);action=True;tick_actions+=1
   pending_at=-1
  if action:continue
  if pending_at>=0:continue
  if ms-last_signal_ms<cooldown_ms:continue
  dif=(this_mid-grid_reference)/2000.
  if dif>=q_gap:dir0=1
  elif dif<=-q_gap:dir0=-1
  else:continue
  # A real grid crossing is first observed now; no generated in-between ticks
  grid_reference=this_mid;last_signal_ms=ms;cntsig+=1
  if require_wins4 and not renewable:
   # First real scout MUST be allowed or the four-win proof can never accumulate.
   if ms-last_scout_ms<30000:continue
   last_scout_ms=ms
  if sp>spread_limit:rejectspread+=1;continue
  if pos_n>=max_open:rejectcap+=1;continue
  if confirm5:
   while past5_idx+1<i and t[past5_idx+1]<=ms-5000:past5_idx+=1
   observed=np.sign(this_mid-mid[past5_idx]);
   if observed*dir0<=0:continue
  side=dir0 if side_mode==1 else -dir0
  pending_side=side;pending_at=ms+250;pending_until=ms+2000
 # open inventory never paper-settled at nonexistent market close; reported separately
 nobs=min(closed,100000)
 return np.array([closed,cash-100000.,gp,gl,win,maxdd,maxpos,cntsig,rejectspread,rejectcap,expired,pos_n,renew_adm,tick_actions],dtype=np.float64),dnum[:nobs],dpnl[:nobs],closed_t[:nobs]

def main():
 begin=time.monotonic();df=pd.read_csv(src,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=df.timestamp_ms_utc.to_numpy();a=df.ask_raw.to_numpy();b=df.bid_raw.to_numpy();del df
 assert len(t)==9135062
 settings=[
 ('NATIVE_GRID_MOM_Q119_CAP2',1.19,.78,2.4,1.2,60000,2,1,0,0,50),
 ('NATIVE_GRID_FADE_Q119_CAP2',1.19,.78,2.4,1.2,60000,2,-1,0,0,50),
 ('NATIVE_GRID_MOM_Q080_CAP8',.80,.78,2.4,1.2,60000,8,1,0,0,50),
 ('NATIVE_GRID_MOM_Q150_CAP8',1.50,.78,3.0,2.2,120000,8,1,0,0,50),
 ('NATIVE_GRID_CONFIRM5_Q119_CAP8',1.19,.78,2.4,1.2,60000,8,1,1,0,50),
 ('NATIVE_GRID_LOW_SPREAD_Q119_CAP8',1.19,.60,2.4,1.2,60000,8,1,0,0,50),
 ('NATIVE_GRID_WATCHDOG4_Q119_CAP8',1.19,.78,2.4,1.2,60000,8,1,0,1,50),
 ('NATIVE_GRID_MOM_Q119_CAP16',1.19,.78,2.4,1.2,60000,16,1,0,0,50),
 ('NATIVE_GRID_WATCHDOG4_SCOUT_BOOTSTRAP_CAP8',1.19,.78,2.4,1.2,60000,8,1,0,1,50),
 ('NATIVE_GRID_WATCHDOG4_SCOUT_BOOTSTRAP_CAP16',1.19,.78,2.4,1.2,60000,16,1,0,1,50),
 ]
 rows=[]
 for name,*cfg in settings:
  st=time.monotonic();result,day,pnl,closed_at=backtest(t,a,b,*cfg)
  days={}
  for dd,v in zip(day,pnl):days[str(pd.Timestamp(int(dd)*86400000,unit='ms',tz='UTC').date())]=days.get(str(pd.Timestamp(int(dd)*86400000,unit='ms',tz='UTC').date()),0.)+float(v)
  ddp=sum(v>0 for v in days.values());week={}
  for ds,v in days.items():
   iso=pd.Timestamp(ds).isocalendar();w=f'{iso.year}-W{iso.week:02d}';week[w]=week.get(w,0.)+v
  r=dict(name=name,grid_gap=cfg[0],spread_limit=cfg[1],stop=cfg[2],target=cfg[3],hold_ms=cfg[4],max_open_config=cfg[5],side=cfg[6],confirm5=bool(cfg[7]),watchdog4=bool(cfg[8]),closed=int(result[0]),net=round(float(result[1]),4),gp=round(float(result[2]),4),gl=round(float(result[3]),4),win=round(float(result[4]/max(1,result[0])),5),pf=round(float(result[2]/(-result[3])),4) if result[3]<0 else None,max_quote_equity_dd=round(float(result[5]),4),max_open_seen=int(result[6]),virtual_crossings=int(result[7]),spread_denials=int(result[8]),capacity_denials=int(result[9]),expirations=int(result[10]),open_end=int(result[11]),positive_trading_days=ddp,positive_month_weeks=sum(v>0 for v in week.values()),day_cash={k:round(v,4) for k,v in sorted(days.items())},week_cash={k:round(v,4) for k,v in sorted(week.items())},seconds=round(time.monotonic()-st,2),unverified_assumptions='Original Dukascopy Bid/Ask, research 0.01lot 1 oz / .20 USD RT fee / 250ms hypothetical fills. Single pending. No broker queue certification or full V1 layer context')
  rows.append(r);print('NATIVE',name,r['net'],r['closed'],'pf',r['pf'],'dd',r['max_quote_equity_dd'],'s',r['seconds'],flush=True)
 package=dict(scope='RESEARCH_ONLY_NEW_CAUSAL_SOURCE_PROTOTYPE_NOT_FULL_V1_OR_PREVIOUS_ACCEPTED_SOURCE',data_original_sha256='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',ticks=len(t),trials=rows,benchmark_jan_target_cash=41520.82,elapsed=time.monotonic()-begin)
 (OUT/'JAN_NINE_CAUSAL_NATIVE_GRID_FULL_TICK_TRIALS.json').write_text(json.dumps(package,indent=2))
 with (OUT/'JAN_NATIVE_GRID_FULL_TICK_CYCLES.csv').open('w',newline='') as f:
  cols=['name','closed','net','pf','gp','gl','win','max_quote_equity_dd','max_open_seen','virtual_crossings','spread_denials','capacity_denials','expirations','open_end','positive_trading_days','positive_month_weeks','seconds'];w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(rows)
 print('DONE',len(rows),'elapsed',round(time.monotonic()-begin,1),flush=True)
if __name__=='__main__':main()
