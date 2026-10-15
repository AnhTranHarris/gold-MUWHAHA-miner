"""JAN ONLY candidate flow-H1/M5 regime specialists and additive source composition.
No future OHLC, no R9 teacher labels; strictly real first tick for order following signal.
Original R9 source is explanatory only. Exploratory research child, no V1 source overwrite.
"""
from pathlib import Path
import time,sys
import numpy as np,pandas as pd
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from r9_teacher_informed_dukas_executor import features
from r9_teacher_community_dukas_jan_causal_mutations_20261014 import build_second_events,bar_groups,prev_frame_index
from jan_atr_regime_harvest_finite_grid_v1 import replay
PATH=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz');P=D/'jan_parent_causal_squeeze_signals.npz'

def completed_direction(sec,hi,lo,cl,width):
 ep,c,h,l=bar_groups(sec,hi,lo,cl,width)
 ind,valid=prev_frame_index(ep,sec,width);v=valid&(ind>=1)
 out=np.zeros(len(sec),np.int8)
 ii=ind[v];out[v]=np.sign(c[ii]-c[ii-1]).astype(np.int8)
 return out

def main():
 t=time.time();d=pd.read_csv(PATH,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
 ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy();del d
 ss,first,hi,lo,cl,f=features(ms,bid);z=np.load(P);assert np.array_equal(ss,z['sec']);primary=z['signal'];n=len(ss)
 flow,counts,op=build_second_events(ms,bid,first)
 h1=completed_direction(ss,hi,lo,cl,3600);m5=completed_direction(ss,hi,lo,cl,300)
 atr=f[300][1];is_new5=np.r_[True,np.diff(ss//5)!=0];is_new15=np.r_[True,np.diff(ss//15)!=0]
 pflow=np.r_[0.,flow[:-1]];pmove=np.r_[0.,(cl-op)[:-1]];pcnt=np.r_[0,counts[:-1]]
 series={}
 # Based on original 1-sec observed quote bursts / as-of M5 regime, no future tape.
 for move in (.35,.60,1.0):
  base=is_new5&(pcnt>=4)&(np.abs(pflow)>=.65)&(np.abs(pmove)>=move)&(np.sign(pflow)==np.sign(pmove))&(atr>=7.77)
  direct=np.sign(pmove).astype(np.int8)
  for strategy,keep in [
   ('FOLLOW_H1',base&(direct==h1)),
   ('FOLLOW_M5',base&(direct==m5)),
   ('DUAL_ALIGN',base&(direct==m5)&(direct==h1)),
   ('M5_AGAINST_H1',base&(direct==m5)&(direct==-h1)),
   ('PULLBACK_TO_H1',base&(direct==h1)&(m5==-h1)),
   ('TREND_ANY',base),
   ('OPPOSE_FLOW',base & (h1==-direct)),
   ]:
   out=np.zeros(n,np.int8);out[keep]=direct[keep]
   name=f'{strategy}_D{int(move*100)}';series[name]=out
 summary=[];top=[]
 for label,secondary in series.items():
  for comb in (0,1):
   sig=secondary.copy()
   if comb==1:sig[primary!=0]=primary[primary!=0]
   for cap in (100.,):
    led,stat=replay(ms,bid,ask,ss,sig,atr,h1,m5,cap,np.array([(7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,2700.)]),1)
    pnls=led[:,6] if len(led) else np.empty(0)
    gp=float(np.maximum(pnls,0).sum());gl=float(np.minimum(pnls,0).sum());net=float(stat[0])
    a=dict(name=label,comb=comb,raw_signals=int(np.count_nonzero(secondary)),total_signals=int(np.count_nonzero(sig)),net=round(net,4),trades=len(led),pf=(round(gp/-gl,5) if gl<0 else None),maxdd=round(float(stat[2]),4),halt=int(stat[3]))
    summary.append(a)
    if net>0 and len(led)>=100 and not stat[3]:top.append((net,label,comb,led.copy()))
  if len(summary)%14==0:print('DONE',len(summary),'elapsed',round(time.time()-t,1),flush=True)
 dd=pd.DataFrame(summary);dd.to_csv(D/'JAN_FLOW_MULTI_REGIME_INTEGRATION_SCOPED_SCREENS.csv',index=False)
 print('TOP',dd.sort_values('net',ascending=False).head(12).to_string(index=False),flush=True)
 if top:
  for i,(net,label,comb,ledger) in enumerate(sorted(top,key=lambda x:x[0],reverse=True)[:3],1):
   pd.DataFrame(ledger,columns=['signal_ms','entry_ms','exit_ms','side','entry_quote','exit_quote','net','exit_reason','best_fav_gross','asof_m5_atr','stop','target','trail_arm','trail_gap']).to_csv(D/f'JAN_FLOW_COMPOSITE_TOP{i}_LEDGER.csv',index=False)
 print('DONE',round(time.time()-t,1),flush=True)
if __name__=='__main__':main()
