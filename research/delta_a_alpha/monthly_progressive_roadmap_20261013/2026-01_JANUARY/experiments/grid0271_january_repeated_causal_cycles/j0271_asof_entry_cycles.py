"""GRID0271 January causal as-of market microstate diagnostic and dream-oracle upper bounds.
Original V1 entries kept fixed; filtered/side-flipped markouts are CONDITIONAL and cannot be counted as
full integrated engine profits or R9_OVERFIT trade teacher matching. No future prices in decisions.
"""
from pathlib import Path
import pandas as pd,numpy as np,json,csv,time
from numba import njit
ROOT=Path('/mnt/data/GRID0271_JAN_RESEARCH');OUT=ROOT/'JAN_ORIGINAL_TICK_COUNTERFACTUAL';OUT.mkdir(exist_ok=True)
src=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
@njit(cache=True)
def statichorizon(t,ask,bid,idx,side,hh,reverse):
 out=np.empty(len(idx))
 for k in range(len(idx)):
  i=idx[k];s=(-int(side[k]) if reverse else int(side[k])); en=(float(ask[i]) if s==1 else float(bid[i]))/1000.
  j=np.searchsorted(t,t[i]+hh,side='left');j=min(j,len(t)-1)
  ex=(float(bid[j]) if s==1 else float(ask[j]))/1000.
  out[k]=(ex-en)*s-.20
 return out
@njit(cache=True)
def oracle(t,ask,bid,idx,side,horizon):
 out=np.empty(len(idx)); alt=np.empty(len(idx)); may=np.empty(len(idx)); mae=np.empty(len(idx))
 for k in range(len(idx)):
  i=idx[k];a=float(ask[i])/1000.;b=float(bid[i])/1000.;last=np.searchsorted(t,t[i]+horizon,side='right');last=min(last,len(t))
  bestLong=-1e10;bestShort=-1e10;worstLong=1e10
  for j in range(i,last):
   x=float(bid[j])/1000.-a;y=b-float(ask[j])/1000.
   if x>bestLong:bestLong=x
   if y>bestShort:bestShort=y
   if x<worstLong:worstLong=x
  may[k]=bestLong;mae[k]=worstLong
  out[k]=(bestLong if side[k]==1 else bestShort)-.20
  alt[k]=max(bestLong,bestShort)-.20
 return out,alt,may,mae

def stats(x,days):
 vals={z:float(x[days==z].sum()) for z in np.unique(days)}
 gp=x[x>0].sum();gl=x[x<0].sum()
 return {'trades':int(len(x)),'net':round(float(x.sum()),4),'win':round(float(np.mean(x>0)),5) if len(x) else 0,'profit_factor':round(float(gp/-gl),5) if gl<0 else None,'avg_pnl':round(float(x.mean()),5) if len(x) else 0,'positive_entry_days':sum(v>0 for v in vals.values()),'max_daily_profit':round(max(vals.values()),2) if vals else 0}

def main():
 t0=time.monotonic();f=pd.read_csv(src,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=f.timestamp_ms_utc.to_numpy();a=f.ask_raw.to_numpy();b=f.bid_raw.to_numpy();del f
 tr=pd.read_csv(ROOT/'JAN_BASELINE/all_completed_shadow_trades.csv');idx=np.searchsorted(t,tr.entry_utc_ms.to_numpy(np.int64));sgn=np.where(tr.side=='BUY',1,-1).astype('int8');d=pd.to_datetime(tr.entry_utc_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d').to_numpy()
 mid=(a.astype('int64')+b.astype('int64'));split=d<'2026-01-17';spread=(a[idx]-b[idx])/1000.
 past={};
 for sec in [1,5,30,120]:
  pi=np.maximum(0,np.searchsorted(t,t[idx]-sec*1000,side='right')-1)
  past[sec]=np.sign(mid[idx]-mid[pi]).astype('int8')
 raw=tr.net_shadow_usd.to_numpy(float)
 scenarios=[]
 def emit(name,sel,vals,method):
  x=vals[sel];dd=d[sel];rec={'case':name,'method':method,'first_half_net':round(float(vals[sel & split].sum()),4),'second_half_net':round(float(vals[sel & ~split].sum()),4),'selected_share':round(float(sel.mean()),5),**stats(x,dd)};scenarios.append(rec);print('SCREEN',name,rec['net'],rec['trades'],rec['second_half_net'],flush=True)
 emit('FIXED_ENTRY_BASELINE_ALL',np.ones(len(d),bool),raw,'ACTUAL_V1_EXECUTION_BASELINE')
 for thr in [0.20,0.4,0.60,0.8]:emit('C5_RAW_SPREAD_MAX_'+str(thr),spread<=thr,raw,'KNOWN_AT_ENTRY_SPREAD_GATE_SHADOW_FILTER_ONLY')
 for sec in [1,5,30,120]:
  good=past[sec]*sgn>0;bad=past[sec]*sgn<0
  emit('C6_WITH_PAST_'+str(sec)+'S_MOMENTUM',good,raw,'KNOWN_AT_ENTRY_MOMENTUM_GATE')
  emit('C6_AGAINST_PAST_'+str(sec)+'S_MOMENTUM',bad,raw,'KNOWN_AT_ENTRY_MOMENTUM_GATE')
  for hh in [10000,30000,120000]:
   v=statichorizon(t,a,b,idx,sgn,hh,False)
   emit('C7_MOM_'+str(sec)+'S_EXIT_'+str(hh//1000)+'S',good,v,'ASOF_SAME_ORIGINAL_ENTRY_FIXED_TIME_EXIT')
   emit('C7_CONTRA_'+str(sec)+'S_EXIT_'+str(hh//1000)+'S',bad,v,'ASOF_SAME_ORIGINAL_ENTRY_FIXED_TIME_EXIT')
 for hh in [30000,120000,240000]:
  x,y,mx,mae=oracle(t,a,b,idx,sgn,hh)
  emit('UPPERBOUND_FUTURE_BEST_EXIT_SAME_SIDE_'+str(hh//1000)+'S',np.ones(len(d),bool),x,'INADMISSIBLE_FUTURE_ORACLE_DIAGNOSTIC_ONLY')
  emit('UPPERBOUND_FUTURE_BEST_SIDE_AND_EXIT_'+str(hh//1000)+'S',np.ones(len(d),bool),y,'INADMISSIBLE_FUTURE_ORACLE_DIAGNOSTIC_ONLY')
 result={'source_hash':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','original_tick_count':len(t),'baseline_current_engine_cash':float(raw.sum()),'cases':scenarios,'CAUTION':'Entry-cohort filtering does not reallocate slots or simulate the engine; ORACLE uses future ticks and is illegal for trading. These results cannot be promoted. Holdout half is reporting only, not pristine unseen research.','elapsed':time.monotonic()-t0}
 (OUT/'JAN_ASOF_ENTRY_MOMENTUM_COST_AND_ORACLE_43_CYCLES.json').write_text(json.dumps(result,indent=2))
 cols=['case','method','trades','net','profit_factor','win','avg_pnl','positive_entry_days','first_half_net','second_half_net','selected_share']
 with (OUT/'JAN_ASOF_COST_DIRECTION_ORACLE.csv').open('w',newline='') as f:w=csv.DictWriter(f,cols,extrasaction='ignore');w.writeheader();w.writerows(scenarios)
 print('ALL_DONE',len(scenarios),'seconds',round(time.monotonic()-t0,2),flush=True)
if __name__=='__main__':main()
