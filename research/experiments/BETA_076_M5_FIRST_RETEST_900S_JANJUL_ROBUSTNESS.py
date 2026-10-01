#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
import numpy as np, pandas as pd

UNIT='BETA_076_M5_FIRST_RETEST_900S_JANJUL_ROBUSTNESS'
FILES=[
('2026-01','XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'),
('2026-02','XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'),
('2026-03','XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177'),
('2026-04','XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f'),
('2026-05','XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d'),
('2026-06','XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2'),
('2026-07','XAUUSD_DUKAS_2026_07_ticks.csv(2).gz','e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7')]
FEE=.02; HOLD_MS=900_000; RETEST_K=(.10,.20,.30); MAX_RETEST_AGE=10

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(16<<20),b''):h.update(b)
 return h.hexdigest()

def load_ticks(path,verify=None,head_only=False):
 if verify and sha(path)!=verify:raise RuntimeError(f'sha mismatch {path.name}')
 ts=[];aa=[];bb=[]
 for n,df in enumerate(pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=1_000_000,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})):
  ts.append(df.timestamp_ms_utc.to_numpy(np.int64));aa.append(df.ask_raw.to_numpy(np.int32));bb.append(df.bid_raw.to_numpy(np.int32))
  if head_only:break
 t=np.concatenate(ts);a=np.concatenate(aa)*.001;b=np.concatenate(bb)*.001
 if np.any(np.diff(t)<0) or np.any(a<b):raise RuntimeError('quote integrity')
 return t,a,b

def raw_bars(t,a,b,minutes):
 ms=minutes*60000;ids=t//ms;st=np.r_[0,np.flatnonzero(ids[1:]!=ids[:-1])+1];en=np.r_[st[1:],len(t)];bid=ids[st];mid=(a+b)*.5
 return pd.DataFrame({'id':bid,'right':(bid+1)*ms,'o':mid[st],'h':np.maximum.reduceat(mid,st),'l':np.minimum.reduceat(mid,st),'c':mid[en-1]})

def finish_bars(df):
 df=df.sort_values('id').drop_duplicates('id').reset_index(drop=True);o=df.o.to_numpy(float);h=df.h.to_numpy(float);l=df.l.to_numpy(float);c=df.c.to_numpy(float);prev=np.r_[o[0],c[:-1]];tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)));df['atr']=pd.Series(tr).rolling(14,min_periods=14).mean().to_numpy();return df

def pivots(df):
 h=df.h.to_numpy(float);l=df.l.to_numpy(float);n=len(df);ph=np.full(n,np.nan);pl=np.full(n,np.nan)
 for i in range(2,n-2):
  if h[i]>h[i-2] and h[i]>h[i-1] and h[i]>h[i+1] and h[i]>h[i+2]:ph[i+2]=h[i]
  if l[i]<l[i-2] and l[i]<l[i-1] and l[i]<l[i+1] and l[i]<l[i+2]:pl[i+2]=l[i]
 ah=np.full(n,np.nan);al=np.full(n,np.nan);ageh=np.full(n,-1,np.int32);agel=np.full(n,-1,np.int32);hp=lp=np.nan;hi=li=-1
 for j in range(n):
  if np.isfinite(ph[j]):hp=ph[j];hi=j
  if np.isfinite(pl[j]):lp=pl[j];li=j
  ah[j]=hp;al[j]=lp;ageh[j]=j-hi if hi>=0 else -1;agel[j]=j-li if li>=0 else -1
 return ah,al,ageh,agel

def build_cumulative(data_dir):
 m1s=[];m5s=[];cert=[]
 for mon,fn,h in FILES:
  p=data_dir/fn;t,a,b=load_ticks(p,h);m1s.append(raw_bars(t,a,b,1));m5s.append(raw_bars(t,a,b,5));cert.append({'month':mon,'sha256':h,'ticks':int(len(t))});print('BARS',mon,len(t),flush=True)
 return finish_bars(pd.concat(m1s,ignore_index=True)),finish_bars(pd.concat(m5s,ignore_index=True)),cert

def generate_events(m1,m5):
 ah,al,ageh,agel=pivots(m5);m5r=m5.right.to_numpy(np.int64);m1r=m1.right.to_numpy(np.int64);mi=np.searchsorted(m5r,m1r,side='right')-1;mi=np.maximum(mi,0);levh=ah[mi];levl=al[mi];agh=ageh[mi];agl=agel[mi];c=m1.c.to_numpy(float);hi=m1.h.to_numpy(float);lo=m1.l.to_numpy(float);atr=m1.atr.to_numpy(float);states={1:None,-1:None};rows=[]
 for i in range(20,len(m1)):
  if not np.isfinite(atr[i]) or atr[i]<=0:continue
  prev=c[i-1]
  if np.isfinite(levh[i]) and prev<=levh[i] and c[i]>levh[i]:states[1]={'level':float(levh[i]),'break_i':i,'age':int(agh[i])}
  if np.isfinite(levl[i]) and prev>=levl[i] and c[i]<levl[i]:states[-1]={'level':float(levl[i]),'break_i':i,'age':int(agl[i])}
  for side in (1,-1):
   st=states[side]
   if st is None:continue
   age=i-st['break_i']
   if age<=0 or age>MAX_RETEST_AGE:
    if age>MAX_RETEST_AGE:states[side]=None
    continue
   level=st['level']
   for tol in RETEST_K:
    key=f'u{tol}'
    if st.get(key):continue
    touched=(lo[i]<=level+tol*atr[i]) if side==1 else (hi[i]>=level-tol*atr[i]);accepted=(c[i]>level) if side==1 else (c[i]<level)
    if touched and accepted:
     rows.append({'event_ms':int(m1r[i]),'side':side,'level_tf':'M5','level_price':level,'level_age_m5_bars':st['age'],'retest_age_m1_bars':age,'retest_tolerance_atr':tol,'m1_atr14':float(atr[i])});st[key]=True
 d=pd.DataFrame(rows)
 d['level_key']=np.round(d.level_price,4);d=d.sort_values(['event_ms','side','level_key','retest_tolerance_atr']).drop_duplicates(['event_ms','side','level_key'],keep='first').drop(columns='level_key').reset_index(drop=True)
 d['entry_month']=pd.to_datetime(d.event_ms,unit='ms',utc=True).dt.strftime('%Y-%m')
 return d

def attach_execution(events,data_dir):
 out=[]
 for idx,(mon,fn,h) in enumerate(FILES):
  ev=events[events.entry_month==mon].copy().reset_index(drop=True)
  if ev.empty:continue
  t,a,b=load_ticks(data_dir/fn,h)
  if idx+1<len(FILES):
   _,nfn,nh=FILES[idx+1];tn,an,bn=load_ticks(data_dir/nfn,None,head_only=True);t=np.r_[t,tn];a=np.r_[a,an];b=np.r_[b,bn]
  e=np.searchsorted(t,ev.event_ms.to_numpy(np.int64),side='right');valid=e<len(t);ev=ev.loc[valid].reset_index(drop=True);e=e[valid];x=np.searchsorted(t,t[e]+HOLD_MS,side='left');valid=x<len(t);ev=ev.loc[valid].reset_index(drop=True);e=e[valid];x=x[valid];s=ev.side.to_numpy(np.int8);pnl=np.where(s==1,b[x]-a[e],b[e]-a[x])-FEE
  ev['entry_ms']=t[e];ev['exit_ms']=t[x];ev['entry_ask']=a[e];ev['entry_bid']=b[e];ev['exit_ask']=a[x];ev['exit_bid']=b[x];ev['entry_spread']=a[e]-b[e];ev['pnl']=pnl;out.append(ev);print('EXEC',mon,len(ev),flush=True)
 return pd.concat(out,ignore_index=True).sort_values(['entry_ms','event_ms','side','level_price']).reset_index(drop=True)

def schedule(d):
 free=-1;rows=[]
 for r in d.itertuples(index=False):
  if r.entry_ms<free:continue
  rows.append(r._asdict());free=int(r.exit_ms)
 return pd.DataFrame(rows)

def stats(v):
 a=np.asarray(v,float)
 if len(a)==0:return {'trades':0,'wins':0,'win_rate':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.,'avg':0.,'max_dd':0.}
 gp=float(a[a>0].sum());gl=float(a[a<=0].sum());w=int((a>0).sum());eq=np.cumsum(a);pk=np.maximum.accumulate(np.r_[0.,eq])[1:];dd=pk-eq
 return {'trades':int(len(a)),'wins':w,'win_rate':w/len(a),'net':float(a.sum()),'gp':gp,'gl':gl,'pf':gp/abs(gl) if gl<0 else math.inf,'avg':float(a.mean()),'max_dd':float(dd.max())}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);ap.add_argument('--out-dir',required=True);q=ap.parse_args();data=Path(q.data_dir);out=Path(q.out_dir);out.mkdir(parents=True,exist_ok=True);t0=time.time();m1,m5,cert=build_cumulative(data);ev=generate_events(m1,m5);np.savez_compressed(out/'BETA_076_CUMULATIVE_STRUCTURE_CACHE.npz',m1_right=m1.right.to_numpy(np.int64),m1_c=m1.c.to_numpy(float),m1_atr=m1.atr.to_numpy(float),m5_right=m5.right.to_numpy(np.int64),m5_c=m5.c.to_numpy(float),m5_atr=m5.atr.to_numpy(float));ev.to_csv(out/'BETA_076_M5_FIRST_RETEST_EVENTS.csv.gz',index=False,compression='gzip');exe=attach_execution(ev,data);led=schedule(exe);led.insert(0,'qa_trade_id',np.arange(1,len(led)+1));led.to_csv(out/'BETA_076_JANJUL_LEDGER.csv.gz',index=False,compression='gzip');monthly={}
 for mon,_,_ in FILES:monthly[mon]=stats(led.loc[led.entry_month==mon,'pnl'].to_numpy(float))
 agg=stats(led.pnl.to_numpy(float));positive=sum(1 for v in monthly.values() if v['net']>0);qa=agg['trades']>=200 and agg['net']>0 and agg['pf']>1 and agg['avg']>0 and positive>=4
 res={'unit_id':UNIT,'status':'HUMAN_QA_READY_RESEARCH_CANDIDATE' if qa else 'ROBUSTNESS_FAILED_NO_PROMOTION','frozen_candidate':{'mechanism':'FIRST_RETEST','level_tf':'M5','hold_seconds':900},'source_certification':cert,'preownership_events':int(len(ev)),'executable_events':int(len(exe)),'aggregate':agg,'monthly':monthly,'positive_months':positive,'human_qa_ready':qa,'jan_jul_historically_inspected':True,'august':'SEALED_NOT_READ','elapsed_sec':round(time.time()-t0,2)};(out/'BETA_076_RESULTS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');packet='# BETA076 Human-Facing QA Review Packet\n\n'+f"Status: **{res['status']}**  \nAugust: **SEALED**  \nMQL5: **NOT AUTHORIZED**\n\nFrozen policy: confirmed M5 pivot -> causal break -> first accepted M1 retest within 10 M1 bars -> next-tick executable entry -> 900-second executable hold.\n\nAggregate Jan-Jul: **{agg['trades']} trades, ${agg['net']:.2f} net, PF {agg['pf']:.3f}, {agg['win_rate']:.1%} win rate, ${agg['avg']:.3f}/trade, max DD ${agg['max_dd']:.2f}.**\n\nPositive months: **{positive}/7**.\n\nMonthly scorecard:\n"+'\n'.join([f"- {m}: {v['trades']} trades, ${v['net']:.2f}, PF {v['pf']:.3f}, avg ${v['avg']:.3f}" for m,v in monthly.items()])+"\n\nThe ledger exposes each confirmed M5 level, break/retest timing, entry/exit Bid/Ask, spread, hold, PnL and chronological QA trade ID. Jan-Jul are robustness data, not pristine OOS; August remains the sealed blind gate.\n";(out/'BETA_076_HUMAN_QA_REVIEW_PACKET.md').write_text(packet);(out/'BETA_076_M5_FIRST_RETEST_900S_JANJUL_ROBUSTNESS_REPORT.md').write_text(packet);(out/'BETA_076_HASHES.json').write_text(json.dumps({p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='BETA_076_HASHES.json'},indent=2,sort_keys=True)+'\n');print(json.dumps(res,indent=2,sort_keys=True))
if __name__=='__main__':main()
