from pathlib import Path
import pandas as pd, numpy as np, json, math, hashlib, sys

DATA=Path('/mnt/data'); OUT=DATA/'beta076'
FILES=[
('2026-01','XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'),
('2026-02','XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'),
('2026-03','XAUUSD_DUKAS_2026_03_ticks.csv(3).gz'),
('2026-04','XAUUSD_DUKAS_2026_04_ticks.csv(3).gz'),
('2026-05','XAUUSD_DUKAS_2026_05_ticks.csv(3).gz'),
('2026-06','XAUUSD_DUKAS_2026_06_ticks.csv(3).gz'),
('2026-07','XAUUSD_DUKAS_2026_07_ticks.csv(2).gz')]
FEE=.02; HOLD_MS=900_000

def load(path, head=False):
    ts=[];aa=[];bb=[]
    for df in pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=1_000_000,
                          dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'}):
        ts.append(df.timestamp_ms_utc.to_numpy(np.int64)); aa.append(df.ask_raw.to_numpy(np.int32)); bb.append(df.bid_raw.to_numpy(np.int32))
        if head: break
    t=np.concatenate(ts); a=np.concatenate(aa).astype(np.float64)*.001; b=np.concatenate(bb).astype(np.float64)*.001
    return t,a,b

def process_month(mon, idx, ev):
    dest=OUT/f'BETA_076_EXEC_{mon}.csv.gz'
    if dest.exists():
        d=pd.read_csv(dest); print('CACHE',mon,len(d),flush=True); return d
    fn=FILES[idx][1]; t,a,b=load(DATA/fn)
    if idx+1<len(FILES):
        tn,an,bn=load(DATA/FILES[idx+1][1],head=True)
        t=np.r_[t,tn];a=np.r_[a,an];b=np.r_[b,bn]
    d=ev[ev.entry_month==mon].copy().reset_index(drop=True)
    e=np.searchsorted(t,d.event_ms.to_numpy(np.int64),side='right')
    v=e<len(t); d=d.loc[v].reset_index(drop=True);e=e[v]
    x=np.searchsorted(t,t[e]+HOLD_MS,side='left')
    v=x<len(t); d=d.loc[v].reset_index(drop=True); e=e[v];x=x[v]
    s=d.side.to_numpy(np.int8)
    d['entry_ms']=t[e];d['exit_ms']=t[x]
    d['entry_ask']=a[e];d['entry_bid']=b[e];d['exit_ask']=a[x];d['exit_bid']=b[x]
    d['entry_spread']=a[e]-b[e]
    d['pnl']=np.where(s==1,b[x]-a[e],b[e]-a[x])-FEE
    d.to_csv(dest,index=False,compression='gzip')
    print('EXEC',mon,len(d),flush=True); return d

def schedule(d):
    d=d.sort_values(['entry_ms','event_ms','side','level_price']).reset_index(drop=True)
    rows=[];free=-1
    for r in d.itertuples(index=False):
        if r.entry_ms < free: continue
        rows.append(r._asdict()); free=int(r.exit_ms)
    return pd.DataFrame(rows)

def stats(vals):
    a=np.asarray(vals,float)
    if len(a)==0:return {'trades':0,'wins':0,'win_rate':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.,'avg':0.,'max_dd':0.}
    gp=float(a[a>0].sum()); gl=float(a[a<=0].sum()); wins=int((a>0).sum())
    eq=np.cumsum(a); peak=np.maximum.accumulate(np.r_[0.,eq])[1:]; dd=peak-eq
    return {'trades':int(len(a)),'wins':wins,'win_rate':wins/len(a),'net':float(a.sum()),'gp':gp,'gl':gl,
            'pf':gp/abs(gl) if gl<0 else (math.inf if gp>0 else 0.),'avg':float(a.mean()),'max_dd':float(dd.max() if len(dd) else 0.)}

ev=pd.read_csv(OUT/'BETA_076_M5_FIRST_RETEST_EVENTS.csv.gz')
parts=[]
months=sys.argv[1:] or [m for m,_ in FILES]
for mon in months:
    idx=[m for m,_ in FILES].index(mon)
    parts.append(process_month(mon,idx,ev))
# Only aggregate when all month cache files exist.
if all((OUT/f'BETA_076_EXEC_{m}.csv.gz').exists() for m,_ in FILES):
    exe=pd.concat([pd.read_csv(OUT/f'BETA_076_EXEC_{m}.csv.gz') for m,_ in FILES],ignore_index=True)
    led=schedule(exe);led.insert(0,'qa_trade_id',np.arange(1,len(led)+1));led.to_csv(OUT/'BETA_076_JANJUL_LEDGER.csv.gz',index=False,compression='gzip')
    monthly={m:stats(led.loc[led.entry_month==m,'pnl']) for m,_ in FILES}; agg=stats(led.pnl); positive=sum(v['net']>0 for v in monthly.values())
    qa=agg['trades']>=200 and agg['net']>0 and agg['pf']>1 and agg['avg']>0 and positive>=4
    res={'unit_id':'BETA_076_M5_FIRST_RETEST_900S_JANJUL_ROBUSTNESS','status':'HUMAN_QA_READY_RESEARCH_CANDIDATE' if qa else 'ROBUSTNESS_FAILED_NO_PROMOTION',
         'frozen_candidate':{'mechanism':'FIRST_RETEST','level_tf':'M5','hold_seconds':900},'preownership_events':int(len(ev)),'executable_events':int(len(exe)),
         'aggregate':agg,'monthly':monthly,'positive_months':positive,'human_qa_ready':bool(qa),'jan_jul_historically_inspected':True,'august':'SEALED_NOT_READ',
         'resume_note':'Execution resumed from previously verified cumulative cache/event ledger after runtime timeout; no bars/events regenerated.'}
    (OUT/'BETA_076_RESULTS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    packet='# BETA076 Human-Facing QA Review Packet\n\n'+f"Status: **{res['status']}**  \nAugust: **SEALED**  \nMQL5: **NOT AUTHORIZED**\n\nFrozen policy: confirmed M5 pivot -> causal break -> first accepted M1 retest within 10 M1 bars -> next-tick executable entry -> 900-second executable hold.\n\nAggregate Jan-Jul: **{agg['trades']} trades, ${agg['net']:.2f} net, PF {agg['pf']:.3f}, {agg['win_rate']:.1%} win rate, ${agg['avg']:.3f}/trade, max DD ${agg['max_dd']:.2f}.**\n\nPositive months: **{positive}/7**.\n\nMonthly scorecard:\n"+'\n'.join([f"- {m}: {v['trades']} trades, ${v['net']:.2f}, PF {v['pf']:.3f}, avg ${v['avg']:.3f}" for m,v in monthly.items()])+"\n\nJan-Jul are robustness data, not pristine OOS. August remains sealed.\n"
    (OUT/'BETA_076_HUMAN_QA_REVIEW_PACKET.md').write_text(packet)
    (OUT/'BETA_076_M5_FIRST_RETEST_900S_JANJUL_ROBUSTNESS_REPORT.md').write_text(packet)
    print(json.dumps(res,indent=2,sort_keys=True),flush=True)
