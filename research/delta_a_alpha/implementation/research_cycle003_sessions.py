"""Independent session research rerun from original protected Dukascopy raw .csv.gz.
Four desk profiles, many session hypotheses, zero trade or P&L inference.
All screening features known as-of previous 5m close; next 5m is evaluation.
Overlap contributes to BOTH desk priors (no independent funded strategies).
"""
from pathlib import Path
from collections import defaultdict,deque
from statistics import median,mean
from datetime import datetime,timezone
import json
import pandas as pd
from v1_vertical_grid import session_frame
ROOT=Path('/mnt/data')
OUT=Path(__file__).parent

def raw_windows(month):
 p=ROOT/f'XAUUSD_DUKAS_2026_{month}_ticks.csv(3).gz'
 group={};count=0;last=-1
 for ch in pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],
                       dtype={'timestamp_ms_utc':'int64','bid_raw':'int64','ask_raw':'int64'},chunksize=500000):
  if int(ch.timestamp_ms_utc.iloc[0])<last or (ch.timestamp_ms_utc.diff().iloc[1:]<0).any():raise ValueError('unsorted ticks')
  if (ch.ask_raw<ch.bid_raw).any():raise ValueError('crossed market')
  last=int(ch.timestamp_ms_utc.iloc[-1]);count+=len(ch)
  ch=ch.assign(window=(ch.timestamp_ms_utc//300000)*300000,sp=ch.ask_raw-ch.bid_raw)
  ag=ch.groupby('window',sort=True).agg(n=('bid_raw','size'),lo=('bid_raw','min'),hi=('bid_raw','max'),first=('bid_raw','first'),last=('bid_raw','last'),spread_sum=('sp','sum'))
  for ts,x in ag.iterrows():
   k=int(ts);vals=group.get(k)
   if vals is None:group[k]=[int(x.n),int(x.lo),int(x.hi),int(x["first"]),int(x['last']),int(x.spread_sum)]
   else:
    vals[0]+=int(x.n);vals[1]=min(vals[1],int(x.lo));vals[2]=max(vals[2],int(x.hi));vals[4]=int(x['last']);vals[5]+=int(x.spread_sum)
 ws=[]
 for t,z in sorted(group.items()):
  sf=session_frame(t)
  ws.append(dict(ts=t,n=z[0],rng=(z[2]-z[1])/1000,spread=z[5]/z[0]/1000,
                 chg=(z[4]-z[3])/1000,opened=list(sf.open_desks),overlap=len(sf.open_desks)>1))
 return ws,count

def evaluate(ws):
 history={k:deque(maxlen=12) for k in ('SYDNEY','TOKYO','LONDON','NEW_YORK')}
 measures=defaultdict(list);ctr=defaultdict(int)
 for i,w in enumerate(ws):
  if i+1>=len(ws):continue
  future=ws[i+1]
  if future['ts']!=w['ts']+300000:continue
  for desk in w['opened']:
   ctr[(desk,'observed_windows')]+=1
   previous=list(history[desk]);history[desk].append(w)
   if len(previous)<12:continue
   cm=median(v['n'] for v in previous);sm=median(v['spread'] for v in previous)
   rm=median(v['rng'] for v in previous)
   variants={
     'ALL':True,
     'ACTIVITY':w['n']>=cm,
     'ACTIVITY_SPREAD':w['n']>=cm and w['spread']<=sm,
     'EXPANSION':w['rng']>=max(.01,1.2*rm) and w['spread']<=1.3*sm,
     'COMPRESSION':w['rng']<=.80*rm and w['spread']<=1.3*sm,
   }
   for tag,yes in variants.items():
    if yes:measures[(desk,tag)].append((future['rng'],future['spread'],abs(future['chg']),w['spread']))
 summaries={}
 for (desk,tag),rs in measures.items():
  if desk not in summaries:summaries[desk]={}
  summaries[desk][tag]={
    'observed_windows':len(rs),
    'next_5m_range_mean':round(mean(v[0] for v in rs),4),
    'next_5m_range_median':round(median(v[0] for v in rs),4),
    'next_5m_quote_spread_mean':round(mean(v[1] for v in rs),4),
    'prior_spread_mean':round(mean(v[3] for v in rs),4),
    'next_5m_abs_openclose_move_mean':round(mean(v[2] for v in rs),4),
  }
 for desk in summaries:
  base=summaries[desk]['ALL']
  for tag,d in summaries[desk].items():
   d['next_range_lift_vs_all_pct']=round(100*(d['next_5m_range_mean']/base['next_5m_range_mean']-1),2)
   d['participation_pct']=round(100*d['observed_windows']/base['observed_windows'],2)
 return dict(sessions=summaries,desk_windows={k[0]:v for k,v in ctr.items()})

if __name__=='__main__':
 ret={'scope':'ORIGINAL_DUKAS_RAW_ONLY_CLEAN_CYCLE003','claims':'MARKET_CONTEXT_DIAGNOSTICS_NOT_EXECUTABLE_EDGE',
      'variants':['ALL','ACTIVITY','ACTIVITY_SPREAD','EXPANSION','COMPRESSION'],
      'time':'Four DST-aware desk clocks and broker clock intentionally kept separate',
      'important':'Quote count is not market traded volume; future 5m used only as out-of-sample response'}
 for mo in ('01','02'):
  ws,count=raw_windows(mo)
  ret[mo]={'ticks':count,'windows':len(ws),'evaluation':evaluate(ws)}
  print('COMPLETE',mo,count,len(ws),flush=True)
 (OUT/'CYCLE003_FOUR_SESSION_RAW_RESEARCH.json').write_text(json.dumps(ret,indent=2)+'\n')
 print('SAVED',OUT/'CYCLE003_FOUR_SESSION_RAW_RESEARCH.json',flush=True)
