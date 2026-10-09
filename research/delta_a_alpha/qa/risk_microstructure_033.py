"""Add concrete peak-trough position, quote, loss-tail diagnostics to Jan 033.
No modification of source strategy or P/L. Source labels from original 131E replay.
"""
from pathlib import Path
import numpy as np,pandas as pd,json,collections,datetime
O=Path('/mnt/data/daa_jan_risk_audit_033')
r=json.loads((O/'JAN033_ORIGINAL_SOURCE_EXACT_TICK_LAYER_DD_ATTRIBUTION.json').read_text())
z=np.load(O/'JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz')
raw=pd.read_csv('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=raw.timestamp_ms_utc.to_numpy();a=raw.ask_raw.to_numpy();b=raw.bid_raw.to_numpy()
E=z['entry_index'];X=z['exit_index'];S=z['source_id'];D=z['direction'];R=z['entry_price_raw'];P=z['pnl']
peak=int(r['drawdown']['peak_tick']);tr=int(r['drawdown']['trough_tick'])
wd=S==0
obs={}
for name,i in [('peak',peak),('trough',tr)]:
    m=(E<=i)&(X>i)&wd
    v=np.flatnonzero(m);di=D[v]
    unreal=(np.where(di>0,b[i]-R[v],R[v]-a[i]))/1000.-.02
    entrysp=(a[E[v]]-b[E[v]])/1000.
    obs[name]={
       'timestamp':pd.to_datetime(t[i],unit='ms',utc=True).isoformat(),
       'ask':round(a[i]/1000,3),'bid':round(b[i]/1000,3),'spread':round((a[i]-b[i])/1000,3),
       'watchdog_open':int(len(v)), 'long':int((di>0).sum()),'short':int((di<0).sum()),
       'watchdog_unrealized':float(unreal.sum()),'watchdog_mean_unrealized':float(unreal.mean()),
       'unique_entry_ticks':int(np.unique(E[v]).size),'largest_same_entry_tick':int(max(collections.Counter(E[v]).values())) if len(v) else 0,
       'median_entry_spread':float(np.median(entrysp)), 'median_age_s':float(np.median((t[i]-t[E[v]])/1000)),
       'p90_age_s':float(np.percentile((t[i]-t[E[v]])/1000,90)),
       'min_age_s':float(np.min((t[i]-t[E[v]])/1000)), 'max_age_s':float(np.max((t[i]-t[E[v]])/1000)),
       'median_entry_raw':float(np.median(R[v])/1000),
       'five_largest_entry_multiplicities':[{'tick_index':int(k),'n':int(x)} for k,x in collections.Counter(E[v]).most_common(5)],
    }
mpeak=(E<=peak)&(X>peak)&wd;mtr=(E<=tr)&(X>tr)&wd
both=(mpeak&mtr)
wdwins=P[wd & (P>0)];wdloss=P[wd & (P<0)]
wdloss_q={str(k):float(np.quantile(wdloss,k)) for k in [.0,.01,.1,.25,.5,.75,.9,.95, .99,1.]}
# Losses from original Watchdog research stream, by UTC exit hour (not policy admission features)
wdlossexit=pd.to_datetime(t[X[wd & (P<0)]],unit='ms',utc=True)
hourly=pd.DataFrame({'hour':wdlossexit.hour,'loss':wdloss,'date':wdlossexit.date}).groupby(['date','hour']).loss.agg(['count','sum']).reset_index().sort_values('sum')
losses_by_source=[]
for i,n in enumerate(z['source_names']):
    p=P[S==i];wins=p[p>0];los=p[p<=0]
    losses_by_source.append({'name':str(n),'trade_count':len(p),'loss_count':len(los),'gross_loss':float(los.sum()),'median_loser':float(np.median(los)) if len(los) else None,'p90_loss_magnitude':float(np.quantile(-los,.9)) if len(los) else None,'worst_trade':float(los.min()) if len(los) else None,'median_winner':float(np.median(wins)) if len(wins) else None})
report={
 'peak_trough_watchdog':obs,
 'watchdog_same_open_ticket_overlap':int(both.sum()),
 'watchdog_open_turnover_during_dd':{'closed_before_trough':int((mpeak&~mtr).sum()),'newly_opened_at_trough':int((mtr&~mpeak).sum())},
 'quotes_movement':{'bid_change_dollars':(int(b[tr])-int(b[peak]))/1000.,'ask_change_dollars':(int(a[tr])-int(a[peak]))/1000.,'spread_change_dollars':(int(a[tr]-b[tr])-int(a[peak]-b[peak]))/1000.},
 'watchdog_losing_ticket_quantiles':wdloss_q,
 'worst_realized_loss_hours':[{'date':str(q['date']),'hour_utc':int(q['hour']),'losses':int(q['count']),'gross_loss':float(q['sum'])} for q in hourly.head(12).to_dict('records')],
 'ticket_quality_by_original_source':losses_by_source,
 'exposure_warning':'Historical simultaneous fills and funded parent credit NOT validated. Risk attribution is exact for recorded research ticket stream, not guaranteed broker execution.'
}
(O/'JAN033_ORIGINAL_SOURCE_WATCHDOG_MICROSTRUCTURE.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'peak':obs['peak'],'trough':obs['trough'],'same_open':report['watchdog_same_open_ticket_overlap'],'change':report['quotes_movement'],'loss_hours':report['worst_realized_loss_hours'][:5],'loss_tails':wdloss_q,'ticket_quality':losses_by_source},indent=2))