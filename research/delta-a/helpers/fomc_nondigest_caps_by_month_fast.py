import pandas as pd, numpy as np, gc, json
from pathlib import Path

BASE=Path('/mnt/data/delta_session_news')
rh=pd.read_csv(BASE/'sa100_rampH_candidate.csv')
CAL={'Mar':'2026-03-18 18:00','Apr':'2026-04-29 18:00','Jun':'2026-06-17 18:00','Jul':'2026-07-29 18:00'}
rh['phase']='NORMAL'
tm_all=rh.time_ms.to_numpy(np.int64)
for mo,v in CAL.items():
    em=int(pd.Timestamp(v,tz='UTC').timestamp()*1000)
    d=(tm_all-em)/60000.0
    for ph,lo,hi in [('PRE',-30,0),('SHOCK',0,5),('DIGEST',5,30),('POST',30,90)]:
        rh.loc[(rh.month==mo)&(d>=lo)&(d<hi),'phase']=ph

US_DST=1772953200000
UK_DST=1774746000000
DAY_MS=86400000
P75=np.array([20,20,21,21],np.int64)
TICK_RAW=10

def sess(ts):
    ts=np.asarray(ts,dtype=np.int64)
    tod=ts%DAY_MS
    ls=np.where(ts>=UK_DST,7,8)*3600000; le=ls+30600000
    ns=np.where(ts>=US_DST,12,13)*3600000; ne=ns+32400000
    il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def quotes(ts,ar,br):
    s=sess(ts); sp=P75[s]*TICK_RAW
    m=ar.astype(np.int64)+br.astype(np.int64)
    bid=((m-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+sp).astype(np.int64),bid.astype(np.int64)

files={'Mar':'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','Apr':'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','Jun':'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','Jul':'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}
caps=[60,120,180,300]
rows=[]
for mo,fn in files.items():
    idx=rh.index[(rh.month==mo)&(rh.phase.isin(['PRE','SHOCK','POST']))].to_numpy()
    base=rh.loc[idx,'pnl_final'].to_numpy(float)
    h=rh.loc[idx,'exit_horizon_s'].to_numpy(np.int64)
    t0=rh.loc[idx,'time_ms'].to_numpy(np.int64)
    side=rh.loc[idx,'side'].to_numpy(np.int8)
    ea=rh.loc[idx,'entry_ask_raw'].to_numpy(np.int64)
    eb=rh.loc[idx,'entry_bid_raw'].to_numpy(np.int64)

    d=pd.read_csv('/mnt/data/'+fn,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    ask,bid=quotes(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64))

    for cap in caps:
        p=base.copy()
        mask=h>cap
        if mask.any():
            j=np.searchsorted(t,t0[mask]+cap*1000,'left')
            p[mask]=np.where(side[mask]==1,
                             (bid[j]-ea[mask])/1000.0-0.02,
                             (eb[mask]-ask[j])/1000.0-0.02)
        rows.append({
            'month':mo,'cap_s':cap,'n':int(len(idx)),'changed':int(mask.sum()),
            'base_net':float(base.sum()),'new_net':float(p.sum()),
            'delta_net':float(p.sum()-base.sum()),
            'base_gl':float(base[base<0].sum()),'new_gl':float(p[p<0].sum()),
            'gl_improvement':float(p[p<0].sum()-base[base<0].sum())
        })
    del d,t,ask,bid
    gc.collect()

out=pd.DataFrame(rows)
out.to_csv(BASE/'FOMC_NONDIGEST_CAPS_BY_MONTH_FAST01.csv',index=False)
summary={str(cap):{
    'total_delta':float(out[out.cap_s==cap].delta_net.sum()),
    'positive_months':int((out[out.cap_s==cap].delta_net>0).sum()),
    'negative_months':int((out[out.cap_s==cap].delta_net<0).sum()),
    'min_month_delta':float(out[out.cap_s==cap].delta_net.min()),
    'max_month_delta':float(out[out.cap_s==cap].delta_net.max()),
    'total_gl_improvement':float(out[out.cap_s==cap].gl_improvement.sum())
} for cap in caps}
(BASE/'FOMC_NONDIGEST_CAPS_BY_MONTH_FAST01.json').write_text(json.dumps({
    'status':'COMPLETE_DIAGNOSTIC_NOT_PROMOTABLE',
    'rule':'FOMC PRE/SHOCK/POST only; cap existing horizon; DIGEST unchanged',
    'source':'path-conditioned sa100_rampH_candidate; exploratory only',
    'summary':summary
},indent=2))
print(out)
print(json.dumps(summary,indent=2))
