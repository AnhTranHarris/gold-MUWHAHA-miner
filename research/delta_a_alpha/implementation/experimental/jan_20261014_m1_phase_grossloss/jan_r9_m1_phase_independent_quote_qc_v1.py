"""Independent original Dukascopy Bid/Ask reprice for Jan R9 M1 phase+M5 ATR profit protection.
Separate from signal generator simulator accounting; also reconciles R9 H1 observation buckets.
"""
from pathlib import Path
import hashlib, sys, json, time, zipfile
import numpy as np,pandas as pd
D=Path(__file__).resolve().parent;P=Path('/mnt/data/jan_new_discovery_20261014')
sys.path.insert(0,str(D));sys.path.insert(1,str(P))
from jan_r9_teacher_m1_phase_risk_v1 import replay_phase,COLS
from r9_teacher_informed_dukas_executor import features
RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
R9=Path('/mnt/data/R9_JAN2026_TICK_M1_M5_H1_HOURLY_CROSS_SCALE/R9_JAN2026_H1_REPORT_CLOCK_CLOSE_BAR_RISK_VELOCITY.csv')
PIN='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
def sha(x):
 h=hashlib.sha256(); f=open(x,'rb')
 for t in iter(lambda:f.read(1048576),b''):h.update(t)
 f.close();return h.hexdigest()

def main():
 start=time.time();assert sha(RAW)==PIN
 q=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});ms=q.timestamp_ms_utc.to_numpy();b=q.bid_raw.to_numpy().astype(np.float64)/1000.;a=q.ask_raw.to_numpy().astype(np.float64)/1000.;del q
 # exact original integer dataset for original simulator
 bid=np.round(b*1000).astype(np.int32);ask=np.round(a*1000).astype(np.int32)
 z=np.load(P/'jan_parent_causal_squeeze_signals.npz');sec,_,_,_,_,f=features(ms,bid);assert np.array_equal(sec,z['sec']);sig=z['signal'];atr=f[300][1];dummy=np.zeros(len(sec),np.int8)
 controls={
  'BASE_ATR_RUNNER':(np.array([(7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,2700.)]),0),
  'PHASE_RISK_PROTECTION':(np.array([(7.,20.,5.,2.5,1500.),(7.,40.,7.,3.5,1500.)]),2),
  'PHASE_MAX_NET':(np.array([(7.,20.,5.,2.5,1500.),(7.,40.,8.,4.,2100.)]),2)
 }
 res={}; ledgers={}
 for label,(cfg,phase_min) in controls.items():
  for cap in (100.,200.):
   led,stat=replay_phase(ms,bid,ask,sec,sig,atr,dummy,dummy,cap,cfg,1,-1,999.,0.,phase_min,59,(1<<24)-1)
   T=pd.DataFrame(led,columns=COLS);viol=[];cash=cap;hi=cap;dd=0.;prev_exit=-1.;gross_wins=gross_losses=0.
   for ix,r in T.iterrows():
    s=int(r.signal_ms);ent=int(r.entry_ms);ex=int(r.exit_ms);side=int(r.side)
    if (s//1000)%60<phase_min:viol.append(('phase',ix));
    k=int(np.searchsorted(sec,s//1000,side='left'))
    if k>=len(sec) or sec[k]!=s//1000 or sig[k]!=side:viol.append(('source_signal',ix))
    if ent<s+250 or ent>s+15000:viol.append(('entry_latency',ix))
    if ent<=prev_exit:viol.append(('slot_collision',ix))
    ie=int(np.searchsorted(ms,ent,side='left'));j=int(np.searchsorted(ms,ex,side='right'))
    buy_ask=a if side>0 else b; sell_bid=b if side>0 else a
    if ie>=len(ms) or ms[ie]!=ent or abs(buy_ask[ie]-r.entry_quote)>1e-8:viol.append(('entry_exact_quote',ix))
    if j<=ie or ms[j-1]!=ex or abs(sell_bid[j-1]-r.exit_quote)>1e-8:viol.append(('exit_exact_quote',ix))
    if a[ie]-b[ie]>.55000001:viol.append(('admission_spread',ix))
    isidx=int(np.searchsorted(ms,s,side='left'));basepx=buy_ask[isidx]
    if abs(r.entry_quote-basepx)>1.5000001:viol.append(('signal_drift',ix))
    gain=side*(r.exit_quote-r.entry_quote)-.20
    if abs(gain-r.net)>1e-7:viol.append(('net_book',ix))
    # Mark every bid/ask tick while position is alive, independently from generator.
    live=cash+side*(sell_bid[ie:j]-r.entry_quote)-.20
    if len(live):
     xp=np.maximum.accumulate(np.r_[hi,live])
     dd=max(dd,float((xp[1:]-live).max()))
     hi=max(hi,float(live.max()))
    cash+=r.net;hi=max(hi,cash);prev_exit=ex
    if r.net>0:gross_wins+=r.net
    else:gross_losses+=r.net
   assert not viol,(label,cap,viol[:15])
   assert abs(cash-cap-stat[0])<1e-7
   assert abs(float(stat[2])-dd)<1e-6,(label,cap,stat[2],dd)
   assert int(stat[-1])==0 # no end-of-January open inventory
   T['close_utc']=pd.to_datetime(T.exit_ms,unit='ms',utc=True);T['day']=T.close_utc.dt.floor('D');T['hour']=T.close_utc.dt.floor('h');T['week']=T.close_utc.dt.isocalendar().week
   dayidx=pd.date_range('2026-01-01','2026-01-31',freq='D',tz='UTC');hridx=pd.date_range('2026-01-01','2026-01-31 23:00',freq='h',tz='UTC')
   def aggregates(col,index=None):
    g=T.groupby(col).net.agg(trades='size',net='sum',gross_profit=lambda x:float(x.clip(lower=0).sum()),gross_loss=lambda x:float(x.clip(upper=0).sum()),winners=lambda x:int((x>0).sum()))
    return g.reindex(index,fill_value=0) if index is not None else g
   daily=aggregates('day',dayidx);hours=aggregates('hour',hridx);weeks=aggregates('week')
   assert abs(daily.net.sum()-stat[0])<1e-6
   T.to_csv(D/f'JAN_{label}_{int(cap)}_SOURCE_QUOTE_AUDITED_TRADE_LEDGER.csv',index=False)
   daily.to_csv(D/f'JAN_{label}_{int(cap)}_31_UTC_DAY.csv');hours.to_csv(D/f'JAN_{label}_{int(cap)}_744_UTC_HOUR.csv');weeks.to_csv(D/f'JAN_{label}_{int(cap)}_ISO_WEEK.csv')
   result=dict(label=label,cap=cap,net=round(float(stat[0]),6),trades=len(T),gross_profit=round(gross_wins,6),gross_loss=round(gross_losses,6),pf=round(gross_wins/-gross_losses,6),win_rate=round(int((T.net>0).sum())/len(T),6),max_tick_floating_dd=round(dd,6),start_cash=cap,end_cash=round(cash,6),closed_active_hours=int((hours.trades>0).sum()),hours_positive=int((hours.net>0).sum()),hours_negative=int((hours.net<0).sum()),hours_no_close=int((hours.trades==0).sum()),hourly_wins_above75=int(((hours.winners/hours.trades)>.75).sum()),positive_days=int((daily.net>0).sum()),negative_days=int((daily.net<0).sum()),jan1_15_net=round(float(T.loc[T.day.dt.day<=15,'net'].sum()),6),jan16_31_net=round(float(T.loc[T.day.dt.day>15,'net'].sum()),6),source_entries_exact_matched=len(T),source_exits_exact_matched=len(T),first_observed_price_verified=True,interval_latency_verified=True,instantaneous_single_slot=True,ledger_sha256=sha(D/f'JAN_{label}_{int(cap)}_SOURCE_QUOTE_AUDITED_TRADE_LEDGER.csv'))
   res[f'{label}_{int(cap)}']=result;ledgers[f'{label}_{int(cap)}']=T.copy()
   print('AUDITED',result,flush=True)
 # source event lineage - what changed from original to edited
 old=ledgers['BASE_ATR_RUNNER_100'].set_index('signal_ms');new=ledgers['PHASE_RISK_PROTECTION_100'].set_index('signal_ms')
 same=old.index.intersection(new.index)
 pair=old.loc[same,['net','exit_ms']].join(new.loc[same,['net','exit_ms']],lsuffix='_old',rsuffix='_new');pair['delta']=pair.net_new-pair.net_old;pair.to_csv(D/'JAN_PHASE_RISK_BASELINE_MATCHED_SOURCE_ATTRIBUTION.csv')
 result=dict(parent_signal_count=int(np.count_nonzero(sig)),matched_signals=len(same),matched_net_lift=round(float(pair.delta.sum()),6),old_only=len(old)-len(same),old_only_net=round(float(old.loc[old.index.difference(new.index),'net'].sum()),6),new_only=len(new)-len(same),new_only_net=round(float(new.loc[new.index.difference(old.index),'net'].sum()),6))
 assert abs(result['matched_net_lift']-result['old_only_net']+result['new_only_net'] - (res['PHASE_RISK_PROTECTION_100']['net']-res['BASE_ATR_RUNNER_100']['net'])) <1e-5
 res['attribution']=result
 H=pd.read_csv(R9); assert len(H)==744;assert int(H.closes.sum())==27980; assert abs(H.net_usd.sum()-41520.82)<1e-5
 res['R9_SYNTH_H1_REFERENCE']=dict(tester_report_hours=744,active_hours=int((H.closes>0).sum()),completed_trades=int(H.closes.sum()),net=round(float(H.net_usd.sum()),6),gross_loss=round(float(H.gross_losses_usd.sum()),6),average_net_per_active_hour=round(float(H.net_usd.sum()/(H.closes>0).sum()),6),average_gross_loss_per_active_hour=round(float(H.gross_losses_usd.sum()/(H.closes>0).sum()),6),source='Original Coinexx R9 Every tick H1 report re-bucketed Deals, NOT Dukascopy simulation; tester clock estimated UTC+02 offset')
 (D/'JAN_GROSS_LOSS_PHASE_AND_ATR_INDEPENDENT_QA.json').write_text(json.dumps(res,indent=2),encoding='utf-8');print('DONE',round(time.time()-start,2),result,flush=True)
if __name__=='__main__':main()
