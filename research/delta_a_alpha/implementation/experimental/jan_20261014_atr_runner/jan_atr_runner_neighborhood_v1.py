"""One experimental net-growth neighborhood around prior January ATR runner; unchanged source.
Post-hoc January-only parameter discovery, explicitly in-sample, not prospective evidence.
"""
from pathlib import Path
import itertools,sys,time
import numpy as np,pandas as pd
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from jan_atr_regime_harvest_finite_grid_v1 import replay
from r9_teacher_informed_dukas_executor import features
B=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
S=D/'jan_parent_causal_squeeze_signals.npz'
# Small discrete forward-looking neighborhoods for profit size, exit patience, structural invalidation.
# High ATR from prior COMPLETE M5, no current-bar future.
CONFIGS=[(target,arm,gap,hold,threshold)
  for threshold in (5.25,7.77,10.0)
  for target,arm,gap,hold in [
  (24.,6.,3.,1800), (24.,6.,3.5,2700),
  (30.,7.,3.5,1800), (30.,7.,3.5,2700),
  (32.,6.,3.0,1800), (32.,6.,3.5,2700),
  (40.,7.,3.5,2700), (40.,7.,4.5,3600),
  (48.,8.,4.0,2700), (48.,8.,5.0,3600),
  (28.,5.,3.0,2700), (40.,5.,3.,2700),
  ]]
# Materially different ATR cutoffs; preserve 36 full rows and independent source path.

def main():
  st=time.time();d=pd.read_csv(B,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
  p=np.load(S);secs=p['sec'];sig=p['signal'];st_secs,first,hi,lo,cl,f=features(ms,bid);assert np.array_equal(st_secs,secs)
  atr=f[300][1];dummy=np.zeros(len(secs),np.int8)
  oldq=np.isfinite(atr) & (atr>7.77)
  row=[];leaders=[]
  for i,(target,arm,gap,hold,cut) in enumerate(CONFIGS):
    # replay inherited uses 7.77 hard coded, so transform ONLY regime membership, not ATR logging/entry values.
    stage=atr.copy();stage[np.isfinite(stage)&(stage>=cut)]=8.0;stage[np.isfinite(stage)&(stage<cut)]=3.0
    settings=np.array([(7.,20.,5.,2.5,1500.),(7.,target,arm,gap,hold)],np.float64)
    trades,stat=replay(ms,bid,ask,secs,sig,stage,dummy,dummy,100.,settings,1)
    net=float(stat[0]);pnls=trades[:,6] if len(trades) else np.zeros(0)
    gp=np.maximum(pnls,0).sum();gl=np.minimum(pnls,0).sum()
    df=pd.DataFrame(trades,columns=['signal_ms','entry_ms','exit_ms','side','entry_quote','exit_quote','net','exit_reason','best_fav_gross','regime_indicator_not_raw_atr','stop','target','trail_arm','trail_gap'])
    if len(df):
      df['day']=pd.to_datetime(df.exit_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d'); daily=df.groupby('day').net.sum()
    else:daily=pd.Series(dtype=float)
    r=dict(test_id=i,atr_m5_threshold=cut,high_target=target,high_trail_arm=arm,high_trail_gap=gap,high_hold_s=hold,net=round(net,4),trades=len(df),pf=round(gp/-gl,4) if gl<0 else None,maxdd=round(float(stat[2]),4),halt=int(stat[3]),positive_days=int((daily>0).sum()),negative_days=int((daily<0).sum()))
    row.append(r);leaders.append((net,r,df))
  pd.DataFrame(row).to_csv(D/'JAN_ATR_RUNNER_NEIGHBORHOOD_36_CASES.csv',index=False)
  for rank,(_,r,df) in enumerate(sorted(leaders,key=lambda a:a[0],reverse=True)[:8],1):
    df.to_csv(D/f'JAN_RUNNER_NEIGHBORHOOD_TOP{rank}_TRADE_LEDGER.csv',index=False)
    df.groupby('day',as_index=False).agg(net=('net','sum'),trades=('net','size'),winners=('net',lambda a:(a>0).sum())).to_csv(D/f'JAN_RUNNER_NEIGHBORHOOD_TOP{rank}_DAILY.csv',index=False)
  print(pd.DataFrame(row).sort_values('net',ascending=False).head(18).to_string(index=False),flush=True)
  print('DONE',round(time.time()-st,2),flush=True)
if __name__=='__main__':main()
