"""January-only corrected R9 $100 benchmark; absolute H1/UTC day scorecards.
Time conversion is an unverified inference: Coinexx report server ~UTC+02h.
All ratios use R9 SYNTH as denominator, never a weaker student variant.
R9 'Every tick' synthetic ≠ original Dukascopy real quote executor.
"""
from pathlib import Path
import numpy as np,pandas as pd,json
O=Path('/mnt/data/jan_gross_loss_frontier_20261014/JAN_FRESH_R9_M1_M5_H1_FAST_GRID_REPLENISHMENT');O.mkdir(exist_ok=True)
R=Path('/mnt/data/R9_JAN2026_TICK_M1_M5_H1_HOURLY_CROSS_SCALE/R9_JAN2026_H1_REPORT_CLOCK_CLOSE_BAR_RISK_VELOCITY.csv')
S=Path('/mnt/data/jan_gross_loss_frontier_20261014/JAN_PHASE_RISK_PROTECTION_100_744_UTC_HOUR.csv')
assert R.is_file() and S.is_file()
a=pd.read_csv(R);b=pd.read_csv(S)
a.index=pd.to_datetime(a.bar_start_tester,utc=True)  # labels are TESTER wall-clock, tz-localized for joins only
b.index=pd.to_datetime(b['Unnamed: 0'],utc=True)+pd.Timedelta(hours=2)  # hypothesis: UTC+2 tester clock
span=pd.date_range('2026-01-01','2026-01-31 23:00',freq='h',tz='UTC')
A=a.reindex(span,fill_value=0);B=b.reindex(span,fill_value=0)
h=pd.DataFrame(index=span)
h['r9_synth_h1_net_usd']=A.net_usd;h['dukas_h1_net_usd']=B.net
h['r9_synth_h1_closes']=A.closes.astype('int32');h['dukas_h1_closes']=B.trades.astype('int32')
h['r9_synth_h1_gross_loss_usd']=A.gross_losses_usd;h['dukas_h1_gross_loss_usd']=B.gross_loss
h['r9_synth_win_trades']=A.win_count;h['dukas_win_trades']=B.winners
h['net_attainment_pct_of_r9']=np.where(h.r9_synth_h1_net_usd>0,100*h.dukas_h1_net_usd/h.r9_synth_h1_net_usd,np.nan)
h['trade_attainment_pct_of_r9']=np.where(h.r9_synth_h1_closes>0,100*h.dukas_h1_closes/h.r9_synth_h1_closes,np.nan)
h['gross_loss_abs_pct_of_r9']=np.where(h.r9_synth_h1_gross_loss_usd<0,100*abs(h.dukas_h1_gross_loss_usd)/abs(h.r9_synth_h1_gross_loss_usd),np.nan)
h.index.name='tester_clock_hour_inferred';h.to_csv(O/'JAN_ALL_744_HOURS_R9_100_VS_REAL_DUKAS_100.csv')
d=h.groupby(h.index.floor('D')).agg(r9_synth_net=('r9_synth_h1_net_usd','sum'),dukas_net=('dukas_h1_net_usd','sum'),r9_synth_closes=('r9_synth_h1_closes','sum'),dukas_closes=('dukas_h1_closes','sum'),r9_synth_gross_loss=('r9_synth_h1_gross_loss_usd','sum'),dukas_gross_loss=('dukas_h1_gross_loss_usd','sum'),r9_synth_profitable_hours=('r9_synth_h1_net_usd',lambda x:int((x>0).sum())),dukas_profitable_hours=('dukas_h1_net_usd',lambda x:int((x>0).sum())),r9_synth_active_hours=('r9_synth_h1_closes',lambda x:int((x>0).sum())),dukas_active_hours=('dukas_h1_closes',lambda x:int((x>0).sum())))
d['net_attainment_pct_of_r9']=np.where(d.r9_synth_net>0,100*d.dukas_net/d.r9_synth_net,np.nan)
d['trades_attainment_pct_of_r9']=np.where(d.r9_synth_closes>0,100*d.dukas_closes/d.r9_synth_closes,np.nan)
d.index.name='tester_clock_day_inferred';d.to_csv(O/'JAN_ALL_31_DAYS_R9_100_VS_REAL_DUKAS_100.csv')
# Preserve R9 source's own 744 bars; hour alignment shifts out of range only if nonzero; verify monthly invariant.
assert abs(h.r9_synth_h1_net_usd.sum()-41520.82)<1e-4
assert int(h.r9_synth_h1_closes.sum())==27980
assert abs(h.dukas_h1_net_usd.sum()-243.779)<1e-4
assert int(h.dukas_h1_closes.sum())==194
assert int((d.r9_synth_closes>0).sum())==21
summary=dict(initial_capital=100,source_mode_r9='Coinexx MT5 Every tick generated synthetic',student_mode='Dukascopy original real bid/ask quote replay',r9_monthly_net=41520.82,student_monthly_net=243.779,student_as_pct_r9_monthly_net=100*243.779/41520.82,r9_monthly_gross_loss=-1827.87,student_monthly_gross_loss=-438.611,student_abs_gross_loss_as_pct_r9=100*438.611/1827.87,r9_monthly_trades=27980,student_monthly_trades=194,student_trades_as_pct_r9=100*194/27980,r9_active_hours=480,student_active_hours=134,student_active_hour_coverage_pct_r9=100*134/480,r9_average_net_per_active_hour=41520.82/480,student_average_net_per_active_hour=243.779/134,student_active_h_net_rate_pct_r9=100*(243.779/134)/(41520.82/480),r9_average_trades_per_active_hour=27980/480,student_average_trades_per_active_hour=194/134,student_active_h_trade_rate_pct_r9=100*(194/134)/(27980/480),r9_profitable_hours=480,student_profitable_hours=int((h.dukas_h1_net_usd>0).sum()),r9_loss_hours=int((h.r9_synth_h1_net_usd<0).sum()),student_loss_hours=int((h.dukas_h1_net_usd<0).sum()),r9_daily_profitable_days=int((d.r9_synth_net>0).sum()),student_daily_profitable_days=int((d.dukas_net>0).sum()),r9_active_days=int((d.r9_synth_closes>0).sum()),student_active_days=int((d.dukas_closes>0).sum()),hourly_clock_offset='unverified Coinexx tester wall clock = original Dukascopy UTC+02 inferred; student shifted +2 for comparable report-clock buckets',disposition='UNDER_BENCHMARK_NOT_ACCEPTED')
(O/'JAN_R9_100_ABSOLUTE_BENCHMARK_GATE.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
