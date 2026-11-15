"""Source exact causal entry-time price location snapshot for historical V9 signals.

Never compute per-entry features from completed future bars. This script
uses observed quote timestamps and source ordinals and the original V12 ledger.
The outcome column is ONLY for offline model fitting, never available at signal.
"""
from __future__ import annotations
import json,sys,time,os
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).parent))
from research import ROOT,Tape,SHA_2026
import hashlib
COLUMNS=['entry_ordinal','entry_time_msc','side','entry_spread_u','entry_execution_u','exit_price_u','exit_reason','lane_count','pre_quotes_1000ms','entry_quant_score','entry_indicator_bias','entry_z15','forward_censored_gap','forward_1000ms_liq_mark_u','first_drift_pos_50_ordinal','first_drift_neg_25_ordinal']
FEATURES=['side','hour_utc','lane_count','spread_c','prequotes1s','v9_quant','v9_z15','v9_direction_bias',
 'micro_range_c','micro_position_frac','micro_return_c','micro_efficiency','micro_twap_dev_c',
 'session_twap_dev_c','ema9_dev_c','ema20_dev_c','ema20_slope_c','m5_sma12_dev_c',
 'm5_sma20_dev_c','m5_sma20_slope_c','ema20_sma20_spread_c','fib_m1_dist_382_c','fib_m1_dist_50_c',
 'fib_m1_dist_618_c','fib_m1_swing_c','fib_m1_direction','fib_m5_dist_382_c','fib_m5_dist_50_c',
 'fib_m5_dist_618_c','fib_m5_swing_c','fib_m5_direction','elapsed_since_last_gap_ms']

def month_extract(mon:int):
 mm=f'{mon:02d}';src=ROOT/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
 with src.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==SHA_2026[mm]
 tape=Tape(src)
 ev=pd.read_csv(ROOT/f'r9_micro180_v12_results/2026-{mm}_V12_exactms_micro180_events.csv.gz',usecols=COLUMNS,low_memory=False)
 ev['original_net']=ev.side*(ev.exit_price_u-ev.entry_execution_u)/100-.20
 ev['original_win']=ev.original_net>0
 i=ev.entry_ordinal.to_numpy(dtype='int64')-1
 ts=tape.ms[i]
 if not np.array_equal(ts,ev.entry_time_msc.to_numpy()):raise ValueError('ordinal mismatch')
 n=len(ev);side=ev.side.to_numpy();mid=tape.mid[i]
 out={k:np.full(n,np.nan,dtype=np.float64) for k in FEATURES}
 def assign(k,v):out[k]=np.asarray(v,dtype=float)
 assign('side',side)
 assign('hour_utc',(ts//3_600_000)%24)
 assign('lane_count',ev.lane_count)
 assign('spread_c',ev.entry_spread_u)
 assign('prequotes1s',ev.pre_quotes_1000ms)
 for a,b in [('v9_quant','entry_quant_score'),('v9_z15','entry_z15'),('v9_direction_bias','entry_indicator_bias')]:
  assign(a,pd.to_numeric(ev[b],errors='coerce'))
 assign('session_twap_dev_c',side*(mid-tape.twap[i]))
 assign('elapsed_since_last_gap_ms',ts-tape.ms[tape.last_gap_start[i]])
 b1=tape.bars['M1'];b5=tape.bars['M5'];j=np.searchsorted(b1['available'],ts,side='right')-1;k=np.searchsorted(b5['available'],ts,side='right')-1
 valid1=(j>=20)&(np.where(j>=0,ts-b1['available'][np.clip(j,0,len(b1['available'])-1)],999999)<=120000)
 valid5=(k>=20)&(np.where(k>=0,ts-b5['available'][np.clip(k,0,len(b5['available'])-1)],999999)<=600000)
 for span in (9,20):
  ema=b1[f'EMA{span}'][np.clip(j,0,len(b1['close'])-1)]
  out[f'ema{span}_dev_c'][:]=np.where(valid1,side*(mid-ema),np.nan)
 e=b1['EMA20'];out['ema20_slope_c'][:]=np.where(valid1,side*(e[np.clip(j,0,len(e)-1)]-e[np.clip(j-1,0,len(e)-1)]),np.nan)
 for span in (12,20):
  sm=b5[f'SMA{span}'];out[f'm5_sma{span}_dev_c'][:]=np.where(valid5,side*(mid-sm[np.clip(k,0,len(sm)-1)]),np.nan)
 sm=b5['SMA20'];out['m5_sma20_slope_c'][:]=np.where(valid5,side*(sm[np.clip(k,0,len(sm)-1)]-sm[np.clip(k-1,0,len(sm)-1)]),np.nan)
 out['ema20_sma20_spread_c'][:]=np.where(valid1&valid5,side*(e[np.clip(j,0,len(e)-1)]-sm[np.clip(k,0,len(sm)-1)]),np.nan)
 prev180=np.searchsorted(tape.ms,ts-180_000,'left');prev180=np.maximum(prev180,tape.last_gap_start[i])
 for q,(idx,st) in enumerate(zip(i,prev180)):
  if idx-st<5 or ts[q]-tape.ms[st]<10_000:continue
  span=tape.mid[st:idx+1];high=span.max();low=span.min();width=high-low
  if width<=0:continue
  out['micro_range_c'][q]=width
  out['micro_position_frac'][q]=side[q]*(mid[q]-low)/width if side[q]>0 else (high-mid[q])/width
  out['micro_return_c'][q]=side[q]*(mid[q]-span[0])
  # Endpoint efficiency from original last 180s quote path, anti-overfit. 
  steps=np.abs(np.diff(span));out['micro_efficiency'][q]=side[q]*(mid[q]-span[0])/max(1.,steps.sum())
  den=tape.total_weight[idx]-tape.total_weight[st]
  if den>=10_000:
   tw=(tape.total_quote_value[idx]-tape.total_quote_value[st])/den
   out['micro_twap_dev_c'][q]=side[q]*(mid[q]-tw)
 for frame in ('M1','M5'):
  bar=tape.bars[frame];hi=bar['piv_hi'];lo=bar['piv_lo']
  # last confirmed pivot at each signal; 2 completed right bars after pivot
  hi_av=bar['available'][np.minimum(hi+2,len(bar['available'])-1)]
  lo_av=bar['available'][np.minimum(lo+2,len(bar['available'])-1)]
  hi_pos=np.searchsorted(hi_av,ts,'right')-1
  lo_pos=np.searchsorted(lo_av,ts,'right')-1
  for n0,(hp,lp) in enumerate(zip(hi_pos,lo_pos)):
   if hp<0 or lp<0:continue
   hindex=int(hi[hp]);lindex=int(lo[lp]);d=abs(hindex-lindex)
   if d> (24 if frame=='M1' else 15):continue
   H=float(bar['high'][hindex]);L=float(bar['low'][lindex]);width=H-L
   if width<90:continue
   bullish=int(hindex>lindex)
   if bullish:
    levels=[H-r*width for r in (.382,.5,.618)]
   else:
    levels=[L+r*width for r in (.382,.5,.618)]
   out[f'fib_{frame.lower()}_direction'][n0]=side[n0]*(1 if bullish else -1)
   out[f'fib_{frame.lower()}_swing_c'][n0]=width
   for ratio,level in zip(('382','50','618'),levels):
    out[f'fib_{frame.lower()}_dist_{ratio}_c'][n0]=side[n0]*(mid[n0]-level)
 result=ev[['entry_ordinal','entry_time_msc','side','original_net','original_win','exit_reason']].copy()
 result['month']=mm
 for key,value in out.items():result[key]=value
 target=Path(os.environ.get('CFAEL_V13_OUTPUT',str(ROOT/'cfael_v13')))/f'{mm}_causal_entry_features.csv.gz'
 result.to_csv(target,index=False,compression={'method':'gzip','compresslevel':4})
 return {'month':mm,'rows':len(result),'sha256':sha,'features_path':str(target),'profit_events':int(result.original_win.sum()),'mean_net':float(result.original_net.mean()),'completed':int(result.original_net.notna().sum()),'file_bytes':target.stat().st_size,'nonmissing_features':{x:int(result[x].notna().sum()) for x in FEATURES}}

if __name__=='__main__':
 a=sys.argv[1:] or ['01','05','09']
 for m in a:
  s=time.monotonic();r=month_extract(int(m));print(json.dumps(r),flush=True);print('SECONDS',round(time.monotonic()-s,2),flush=True)
  (Path(os.environ.get('CFAEL_V13_OUTPUT',str(ROOT/'cfael_v13')))/f'{m}_feature_manifest.json').write_text(json.dumps(r,indent=2))
