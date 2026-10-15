"""Independent reprice and mark-to-market QA for JAN new ATR exit specialist.
Does not call simulator; rereads original tick source and exported ledgers.
"""
from pathlib import Path
import numpy as np,pandas as pd,json,hashlib
D=Path(__file__).resolve().parent
SOURCE=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
RESULT={}

def hh(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()

def main():
 global RESULT
 d=pd.read_csv(SOURCE,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'});
 ms=d.timestamp_ms_utc.to_numpy();b=d.bid_raw.to_numpy(dtype=np.float64)/1000.;a=d.ask_raw.to_numpy(dtype=np.float64)/1000.;del d
 assert hh(SOURCE)=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
 for cap in (100,200):
  file=D/f'JAN_ATR_REGIME_{cap}_TOP1_LEDGER.csv';T=pd.read_csv(file);assert len(T)==244
  # independently scan actual source quotes by exact times and prices + mark intratrade for equity DD.
  cash=float(cap);hi=float(cap);dd=0.;bad=[];prev_exit=-1;signal_count=0;first_price_violations=0
  gross_winners=0.;gross_losers=0.;win=0
  for k,r in T.iterrows():
   s=int(r.signal_ms);st=int(r.entry_ms);en=int(r.exit_ms);side=int(r.side)
   if st<s+250 or st>s+15000:bad.append(('latency_ttl',k))
   if st<=prev_exit:bad.append(('slot_overlap',k))
   i0=int(np.searchsorted(ms,st,side='left'));i1=int(np.searchsorted(ms,en,side='right'))
   xs=(a if side==1 else b)[i0:i1];ys=(b if side==1 else a)[i0:i1]
   if i0==i1 or not np.any((ms[i0:i1]==st)&(np.abs(xs-float(r.entry_quote))<1e-8)):bad.append(('entry_quote',k))
   if not np.any((ms[i0:i1]==en)&(np.abs(ys-float(r.exit_quote))<1e-8)):bad.append(('exit_quote',k))
   calc=side*(float(r.exit_quote)-float(r.entry_quote))-.20
   if abs(calc-float(r.net))>1e-7:bad.append(('pnl',k))
   if (float(r.net)>0):gross_winners+=float(r.net);win+=1
   else:gross_losers+=float(r.net)
   # Original mark-to-market path from each real Bid/Ask quote; fixed pretrade cash before this trade.
   # Exchange cash gap not modeled because no external deposits/withdrawals.
   live_eq=cash+side*(ys-float(r.entry_quote))-.20
   peak_in=np.maximum.accumulate(np.r_[hi,live_eq]); draw=peak_in[1:]-live_eq
   dd=max(dd,float(np.max(draw)) if len(draw) else 0.);hi=max(hi,float(np.max(live_eq)))
   cash+=float(r.net);hi=max(hi,cash)
   prev_exit=en;signal_count+=1
  if bad:raise RuntimeError(str(bad[:30]))
  T['close_utc']=pd.to_datetime(T.exit_ms,unit='ms',utc=True)
  T['day']=T.close_utc.dt.strftime('%Y-%m-%d');T['hour']=T.close_utc.dt.strftime('%Y-%m-%dT%H');T['iso_week']=T.close_utc.dt.isocalendar().week
  dayidx=pd.date_range('2026-01-01','2026-01-31',freq='D',tz='UTC');hridx=pd.date_range('2026-01-01','2026-01-31 23:00',freq='h',tz='UTC')
  daily=T.groupby(T.close_utc.dt.floor('D')).agg(net=('net','sum'),trades=('net','size'),wins=('net',lambda x:int((x>0).sum())),gross_loss=('net',lambda x:float(x.clip(upper=0).sum())),gross_profit=('net',lambda x:float(x.clip(lower=0).sum()))).reindex(dayidx,fill_value=0)
  daily.index.name='UTC_date';daily.to_csv(D/f'JAN_ATR_HARVEST_QA_{cap}_31_DAY.csv')
  hour=T.groupby(T.close_utc.dt.floor('h')).agg(net=('net','sum'),trades=('net','size'),wins=('net',lambda x:int((x>0).sum())),gross_loss=('net',lambda x:float(x.clip(upper=0).sum())),gross_profit=('net',lambda x:float(x.clip(lower=0).sum()))).reindex(hridx,fill_value=0)
  hour.index.name='UTC_hour';hour.to_csv(D/f'JAN_ATR_HARVEST_QA_{cap}_744_HOUR.csv')
  week=T.groupby('iso_week').agg(net=('net','sum'),trades=('net','size'),gross_loss=('net',lambda x:float(x.clip(upper=0).sum())),gross_profit=('net',lambda x:float(x.clip(lower=0).sum())))
  week.to_csv(D/f'JAN_ATR_HARVEST_QA_{cap}_ISO_WEEK.csv')
  res=dict(capital=cap,original_quotes=len(ms),funded_trade_count=len(T),cash_net=round(cash-cap,6),close_win_rate=round(win/len(T),6),gross_profit=round(gross_winners,6),gross_loss=round(gross_losers,6),profit_factor=round(gross_winners/(-gross_losers),6),full_tick_floating_equity_dd=round(dd,6),jan_active_days=int((daily.trades>0).sum()),jan_profit_days=int((daily.net>0).sum()),jan_loss_days=int((daily.net<0).sum()),jan_zero_close_days=int((daily.trades==0).sum()),jan_active_hours=int((hour.trades>0).sum()),jan_profit_hours=int((hour.net>0).sum()),jan_loss_hours=int((hour.net<0).sum()),jan_zero_close_hours=int((hour.trades==0).sum()),hours_gt75_accuracy=int(((hour.wins/hour.trades)>.75).sum()),ledger_hash=hh(file),no_overlap=True,all_quoted_legs_match=True,all_delays_250ms_to_15sec=True,all_pnl_identity_match=True,monthly_marked_open_exposure_not_yet_audited_if_present=True)
  RESULT[str(cap)]=res
  print('QA',res,flush=True)
 Path(D/'JAN_ATR_RUNNER_INDEPENDENT_TICK_QA.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
if __name__=='__main__':main()
