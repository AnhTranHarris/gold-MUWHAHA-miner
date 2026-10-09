"""Daily ISO-week/month comparison on January 034 candidate-tape risk tests.
Raw quote execution only; never present fixed tape as a full physical funded replay.
"""
from pathlib import Path
import json, pandas as pd,numpy as np
O=Path('/mnt/data/daa_jan_risk_research_034')
ref=json.load(open('/mnt/data/daa_jan_exact_032/r9_synth_jan_daily_weekly.json'))
raw=pd.read_csv('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',compression='gzip',usecols=['timestamp_ms_utc'],dtype={'timestamp_ms_utc':'i8'})
t=raw.timestamp_ms_utc.to_numpy()
chosen=['base','clone16','clone64','clone96','clone128','clone192','clone256','clone64_spread2','clone192_wd384','clone192_spread2','loss2000','loss2000_recovery','stop8_m5_reversal']
week_dates=sorted(ref['weekly']);dates=sorted(ref['daily'])
md=[];wr=[];dr=[]
for name in chosen:
 s=json.loads((O/(name+'.json')).read_text())
 if (O/(name+'_trades.npz')).exists():
  z=np.load(O/(name+'_trades.npz')); p=z['p'];ix=z['x'];src=z['s']
 else:
  z=np.load(O/(name+'_trade_ledger.npz'));p=z['P'];ix=z['X'];src=z['S']
 dt=pd.to_datetime(t[ix],unit='ms',utc=True)
 f=pd.DataFrame({'date':dt.strftime('%Y-%m-%d'),'week':dt.strftime('%G-W%V'),'pnl':p,'source':src})
 g=f.groupby('date').pnl.agg(['sum','size']);w=f.groupby('week').pnl.agg(['sum','size'])
 for date in dates:
  rr=ref['daily'][date];grid=float(g['sum'].get(date,0));count=int(g['size'].get(date,0))
  dr.append({'scenario':name,'date':date,'grid_net':round(grid,3),'r9_synth_net':round(rr['net'],3),'grid_trade_count':count,'r9_synth_trades':rr['trades'],'grid_better_net':grid>=rr['net']})
 for week in week_dates:
  rr=ref['weekly'][week];grid=float(w['sum'].get(week,0));count=int(w['size'].get(week,0))
  wr.append({'scenario':name,'iso_week':week,'grid_net':round(grid,3),'r9_synth_net':round(rr['net'],3),'grid_trades':count,'r9_synth_trades':rr['trades'],'grid_beats_r9_net':grid>=rr['net']})
 gp=float(p[p>0].sum());gl=float(p[p<0].sum());net=float(p.sum());model='individual_stop' if name.startswith('stop') else 'source_tape_gate'
 md.append({'scenario':name,'method':model,'net':round(net,3),'trades':len(p),'gross_profit':round(gp,3),'gross_loss':round(gl,3),'pf':round(gp/-gl,4),'win_pct':round(100*float(np.mean(p>0)),3),'equity_dd':s.get('max_equity_dd',s.get('equity_dd')),'positive_days':sum(g['sum'].get(d,0)>0 for d in dates),'r9_days_beaten':sum(g['sum'].get(d,0)>=ref['daily'][d]['net'] for d in dates),'positive_weeks':sum(w['sum'].get(k,0)>0 for k in week_dates),'r9_weeks_beaten':sum(w['sum'].get(k,0)>=ref['weekly'][k]['net'] for k in week_dates),'hourly_net':round(float(p[src==1].sum()),3),'watchdog_net':round(float(p[src==0].sum()),3),'recovery_net':round(float(p[src==7].sum()),3),'watchdog_fraction_wd_last_week':round(float(p[(src==0)&(dt>=pd.Timestamp('2026-01-26',tz='UTC'))].sum()),3)})
pd.DataFrame(md).to_csv(O/'JAN034_MONTHLY_METRICS.csv',index=False)
pd.DataFrame(wr).to_csv(O/'JAN034_WEEKLY_VS_R9_SYNTH.csv',index=False)
pd.DataFrame(dr).to_csv(O/'JAN034_DAILY_VS_R9_SYNTH.csv',index=False)
print(pd.DataFrame(md).to_string(index=False))
print('WEEKLY key baseline vs clone192')
print(pd.DataFrame(wr).query("scenario in ['base','clone192']").to_string(index=False))