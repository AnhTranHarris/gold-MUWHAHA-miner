"""January-original DUKAS 18-second EXECUTABLE QUOTE POTENTIAL study.
NONCAUSAL HINDSIGHT ORACLE used ONLY for engineering upper bounds.
NOT A SIGNAL, AND NO CLAIM OF EARNABLE PROFIT. Zero source leakage into funded strategy.
Exact ask-to-bid and bid-to-ask sides, 250ms minimum future fill, $0.20 fee.
"""
from pathlib import Path
import hashlib,json,time
import pandas as pd,numpy as np
from numba import njit
B=Path('/mnt/data');D=B/'jan_gross_loss_frontier_20261014/JAN_FRESH_R9_M1_M5_H1_FAST_GRID_REPLENISHMENT';D.mkdir(exist_ok=True)
R=B/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
@njit(cache=True)
def potential(ms,bid,ask,idx,seconds=18,fee=.20):
 n=len(idx);best_long=np.empty(n,np.float64);best_short=np.empty(n,np.float64);sp=np.empty(n,np.float64);t=np.empty(n,np.int64)
 for ii in range(n):
  anchor=idx[ii];starttime=ms[anchor]+250; k=anchor+1
  while k<len(ms) and ms[k]<starttime:k+=1
  if k==len(ms):best_long[ii]=np.nan;best_short[ii]=np.nan;sp[ii]=np.nan;t[ii]=0;continue
  start=ms[k];maxbid=-1e9;minask=1e9; j=k+1
  while j<len(ms) and ms[j]-start<=seconds*1000:
   if bid[j]>maxbid:maxbid=bid[j]
   if ask[j]<minask:minask=ask[j]
   j+=1
  best_long[ii]=maxbid/1000.-ask[k]/1000.-fee if j>k+1 else np.nan
  best_short[ii]=bid[k]/1000.-minask/1000.-fee if j>k+1 else np.nan
  sp[ii]=(ask[k]-bid[k])/1000.
  t[ii]=start
 return best_long,best_short,sp,t

def main():
 s=time.time();d=pd.read_csv(R,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
 # Every 20 seconds per observed time: at most 3 non-overlapping planned 18s opportunities per minute.
 p=np.r_[True,(ms[1:]//20000)!=(ms[:-1]//20000)];idx=np.flatnonzero(p)
 x,y,sp,t=potential(ms,bid,ask,idx)
 best=np.maximum(x,y); m=np.isfinite(best)&(t>0)
 df=pd.DataFrame({'t':pd.to_datetime(t[m],unit='ms',utc=True),'long_best':x[m],'short_best':y[m],'oracle_side_best':best[m],'spread':sp[m]})
 # $41,520.82 / 27,980 = 1.484 after fee; perfect oracle STILL cannot fill at future best without foresight.
 target=41520.82/27980.
 df['oracle_bench_trade']=df.oracle_side_best>=target
 df['oracle_any_netpositive']=df.oracle_side_best>0
 df['hour']=df.t.dt.floor('h')
 hours=df.groupby('hour').agg(eligible_anchor_samples=('oracle_side_best','size'),oracle_bench_count=('oracle_bench_trade','sum'),oracle_positive_count=('oracle_any_netpositive','sum'),oracle_best_avg=('oracle_side_best','mean'),mean_spread=('spread','mean'))
 allhours=pd.date_range('2026-01-01','2026-01-31 23:00',freq='h',tz='UTC');hours=hours.reindex(allhours,fill_value=0);hours.index.name='utc_hour';hours.to_csv(D/'JAN_744H_18SEC_NONOVERLAP_ORACLE_BUDGET.csv')
 df.to_csv(D/'JAN_18SEC_ORACLE_ANCHOR_ONLY.csv',index=False)
 summary=dict(original_quotes=len(ms),anchor_count=len(df),benchmark_net_per_close=target,oracle_any_netpositive_pct=float(df.oracle_any_netpositive.mean()),oracle_r9_net_per_trade_threshold_pct=float(df.oracle_bench_trade.mean()),hours_with_58_oracle_bench_opportunities=int((hours.oracle_bench_count>=58).sum()),hours_with_at_least_1_oracle_bench_opportunity=int((hours.oracle_bench_count>0).sum()),oracle_bench_anchor_counts_total=int(df.oracle_bench_trade.sum()),active_quote_hours=int((hours.eligible_anchor_samples>0).sum()),median_anchor_ask_bid_spread=float(df.spread.median()),oracle_scope='noncausal best of both direction and perfect high/low exits, intentionally NOT executable signal or net-return bound under variable holds')
 (D/'JAN_18SEC_EXECUTABLE_QUOTES_ORACLE_UPPER_POTENTIAL.json').write_text(json.dumps(summary,indent=2))
 print('ORACLE',summary,'elapsed',time.time()-s,flush=True)
if __name__=='__main__':main()
