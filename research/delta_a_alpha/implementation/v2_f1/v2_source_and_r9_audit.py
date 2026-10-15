"""Independent V2 initial full original-quote audit and R9 UTC+2 comparative scorecard.
Do not treat inferred Coinexx clock offset as certified. R9 SYNTH trades are not
real-quote price matches; V2 uses original Dukascopy as a separate data feed.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
BASE=Path('/mnt/data'); OUT=Path(__file__).parent
SRC=BASE/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
REFERENCE=BASE/'R9_JAN2026_TICK_M1_M5_H1_HOURLY_CROSS_SCALE/R9_JAN2026_H1_REPORT_CLOCK_CLOSE_BAR_RISK_VELOCITY.csv'
LEDGER=OUT/'V2_NATIVE_CONTROL_SMOKE_TRADES.csv'

def run():
 df=pd.read_csv(SRC,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'])
 time=df.timestamp_ms_utc.to_numpy();bid=df.bid_raw.to_numpy()*0.001;ask=df.ask_raw.to_numpy()*0.001
 deals=pd.read_csv(LEDGER)
 discrepancies=[];validated=0
 for i,r in deals.iterrows():
    ei=np.searchsorted(time,int(r.entry_ms));xi=np.searchsorted(time,int(r.exit_ms))
    if ei>=len(time) or time[ei]!=r.entry_ms or xi>=len(time) or time[xi]!=r.exit_ms:discrepancies.append((i,'not_raw_quote'));continue
    e=ask[ei] if r.side==1 else bid[ei];x=bid[xi] if r.side==1 else ask[xi]
    if abs(e-r.entry_price)>1e-7 or abs(x-r.exit_price)>1e-7:discrepancies.append((i,'raw_price_mismatch'))
    if abs((x-e)*r.side-.20-r.net_usd)>1e-6:discrepancies.append((i,'cash_mismatch'))
    if r.entry_ms<r.signal_ms+250:discrepancies.append((i,'latency_lookahead'))
    if i and r.entry_ms<deals.iloc[i-1].exit_ms:discrepancies.append((i,'overlap'))
    validated+=1
 if len(deals):
  if not np.allclose(100+deals.net_usd.cumsum(),deals.closing_cash,atol=1e-6):discrepancies.append(('all','running_cash'))
 h=pd.read_csv(REFERENCE)
 h['r9_clock_hour']=pd.to_datetime(h.bar_start_tester)
 hidx=pd.date_range('2026-01-01',periods=744,freq='h')
 if not h['r9_clock_hour'].equals(pd.Series(hidx)) : discrepancies.append(('r9','744_hour_shape_not_matched'))
 # Map student's UTC quote times into assumed Coinexx tester clock (UTC +2)
 tr=pd.to_datetime(deals.exit_ms,unit='ms',utc=True)+pd.Timedelta(hours=2)
 tr=tr.dt.tz_localize(None)
 st=pd.DataFrame({'r9_clock_hour':tr.dt.floor('h'),'net':deals.net_usd,'trade':1})
 a=st.groupby('r9_clock_hour').agg(v2_net=('net','sum'),v2_closes=('trade','sum')).reindex(hidx,fill_value=0)
 a.index.name='r9_clock_hour';a=a.reset_index()
 a['r9_net']=h.net_usd;a['r9_closes']=h.closes;a['r9_gross_losses']=h.gross_losses_usd
 a['hour_net_60pct_pass']=(a.r9_net>0)&(a.v2_net>=.6*a.r9_net)
 a['hour_velocity_60pct_pass']=(a.r9_closes>0)&(a.v2_closes>=.6*a.r9_closes)
 a.to_csv(OUT/'V2_R9_744_HOUR_ABSOLUTE_SCORECARD.csv',index=False)
 a['day']=a.r9_clock_hour.dt.floor('D')
 d=a.groupby('day').agg(v2_net=('v2_net','sum'),r9_net=('r9_net','sum'),v2_closes=('v2_closes','sum'),r9_closes=('r9_closes','sum'))
 d['day_net_60pct_pass']=(d.r9_net>0)&(d.v2_net>=.6*d.r9_net)
 d['day_velocity_60pct_pass']=(d.r9_closes>0)&(d.v2_closes>=.6*d.r9_closes)
 d.to_csv(OUT/'V2_R9_31_DAY_ABSOLUTE_SCORECARD.csv')
 exact=dict(quote_count=len(df),source_sha=hashlib.file_digest(SRC.open('rb'),'sha256').hexdigest(),audit_trades=len(deals),actual_original_quote_matches=validated,errors=discrepancies,
           assumed_server_clock_offset_hours=2,server_clock_certified=False,
           r9_original_report_active_hours=int((a.r9_closes>0).sum()),r9_original_report_active_days=int((d.r9_closes>0).sum()),
           hours_meeting_r9_60pct_net=int(a.hour_net_60pct_pass.sum()),hours_meeting_r9_60pct_volume=int(a.hour_velocity_60pct_pass.sum()),
           days_meeting_r9_60pct_net=int(d.day_net_60pct_pass.sum()),days_meeting_r9_60pct_volume=int(d.day_velocity_60pct_pass.sum()),
           absolute_success=False,comment='In-sample R9 MT5 generated tick reference vs separate Dukascopy real-quote V2 causal test; no claim of same broker fill parity.')
 (OUT/'V2_INDEPENDENT_SOURCE_QA.json').write_text(json.dumps(exact,indent=2)+'\n')
 if discrepancies:raise AssertionError(discrepancies[:10])
 print('INDEPENDENT_QA',json.dumps(exact))
if __name__=='__main__':run()
