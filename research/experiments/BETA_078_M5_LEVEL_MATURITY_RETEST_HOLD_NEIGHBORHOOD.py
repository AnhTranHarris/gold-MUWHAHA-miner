#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, hashlib
from pathlib import Path
import numpy as np, pandas as pd

UNIT='BETA_078_M5_LEVEL_MATURITY_RETEST_HOLD_NEIGHBORHOOD'
MONTHS=['2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07']
FILES={
'2026-01':'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','2026-02':'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','2026-03':'XAUUSD_DUKAS_2026_03_ticks.csv(3).gz','2026-04':'XAUUSD_DUKAS_2026_04_ticks.csv(3).gz','2026-05':'XAUUSD_DUKAS_2026_05_ticks.csv(3).gz','2026-06':'XAUUSD_DUKAS_2026_06_ticks.csv(3).gz','2026-07':'XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}
WINDOWS={'AGE_7_9':(7,9),'AGE_7_10':(7,10),'AGE_8_9':(8,9)}
WINDOW_NEIGHBORS={'AGE_7_9':['AGE_7_10','AGE_8_9'],'AGE_7_10':['AGE_7_9'],'AGE_8_9':['AGE_7_9']}
HOLDS=[600,900,1200,1800]
FEE=.02
MIN_TRADES=200; MIN_POS_MONTHS=4; NEIGHBOR_MIN=150

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(16<<20),b''):h.update(b)
 return h.hexdigest()

def load_ticks(path,head=False):
 ts=[];aa=[];bb=[]
 for df in pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],chunksize=1_000_000,dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'}):
  ts.append(df.timestamp_ms_utc.to_numpy(np.int64));aa.append(df.ask_raw.to_numpy(np.int32));bb.append(df.bid_raw.to_numpy(np.int32))
  if head: break
 t=np.concatenate(ts);a=np.concatenate(aa).astype(np.float64)*.001;b=np.concatenate(bb).astype(np.float64)*.001
 return t,a,b

def build_month(beta076,data,mon,idx,out):
 dest=out/f'BETA_078_EXEC_{mon}.csv.gz'
 if dest.exists(): return pd.read_csv(dest)
 base=pd.read_csv(beta076/f'BETA_076_EXEC_{mon}.csv.gz')
 base=base[base.level_age_m5_bars.between(7,10)].copy().reset_index(drop=True)
 t,a,b=load_ticks(data/FILES[mon])
 if idx+1<len(MONTHS):
  tn,an,bn=load_ticks(data/FILES[MONTHS[idx+1]],head=True);t=np.r_[t,tn];a=np.r_[a,an];b=np.r_[b,bn]
 # verify BETA076 900-second entry/exit identity for relevant rows.
 e=np.searchsorted(t,base.entry_ms.to_numpy(np.int64),side='left')
 if np.any(t[e]!=base.entry_ms.to_numpy(np.int64)): raise RuntimeError(f'entry timestamp identity failure {mon}')
 for H in HOLDS:
  x=np.searchsorted(t,base.entry_ms.to_numpy(np.int64)+H*1000,side='left');valid=x<len(t)
  pnl=np.full(len(base),np.nan);ex=np.full(len(base),-1,np.int64);xa=np.full(len(base),np.nan);xb=np.full(len(base),np.nan)
  ii=np.flatnonzero(valid);xx=x[ii];s=base.side.to_numpy(np.int8)[ii];ex[ii]=t[xx];xa[ii]=a[xx];xb[ii]=b[xx]
  pnl[ii]=np.where(s==1,b[xx]-base.entry_ask.to_numpy(float)[ii],base.entry_bid.to_numpy(float)[ii]-a[xx])-FEE
  base[f'exit_ms_{H}s']=ex;base[f'exit_ask_{H}s']=xa;base[f'exit_bid_{H}s']=xb;base[f'pnl_{H}s']=pnl
 if 'pnl' in base.columns:
  m=np.isfinite(base['pnl_900s'])
  if not np.allclose(base.loc[m,'pnl_900s'].to_numpy(float),base.loc[m,'pnl'].to_numpy(float),atol=1e-9):
   raise RuntimeError(f'900s pnl parity fail {mon}')
 base.to_csv(dest,index=False,compression='gzip');print('EXEC',mon,len(base),flush=True);return base

def schedule(d,H):
 d=d[np.isfinite(d[f'pnl_{H}s'])].sort_values(['entry_ms','event_ms','side','level_price']).reset_index(drop=True)
 rows=[];free=-1
 for r in d.itertuples():
  if r.entry_ms<free:continue
  rows.append(r.Index);free=int(getattr(r,f'exit_ms_{H}s'))
 return d.loc[rows].copy().reset_index(drop=True)

def stats(d,H):
 a=d[f'pnl_{H}s'].to_numpy(float) if len(d) else np.array([],float)
 if not len(a):return {'trades':0,'wins':0,'win_rate':0.,'net':0.,'gp':0.,'gl':0.,'pf':0.,'avg':0.,'max_dd':0.}
 gp=float(a[a>0].sum());gl=float(a[a<=0].sum());w=int((a>0).sum());eq=np.cumsum(a);pk=np.maximum.accumulate(np.r_[0.,eq])[1:];dd=pk-eq
 return {'trades':len(a),'wins':w,'win_rate':w/len(a),'net':float(a.sum()),'gp':gp,'gl':gl,'pf':gp/abs(gl) if gl<0 else math.inf,'avg':float(a.mean()),'max_dd':float(dd.max())}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--beta076-dir',required=True);ap.add_argument('--data-dir',required=True);ap.add_argument('--out-dir',required=True);q=ap.parse_args();b76=Path(q.beta076_dir);data=Path(q.data_dir);out=Path(q.out_dir);out.mkdir(parents=True,exist_ok=True)
 parts=[build_month(b76,data,m,i,out) for i,m in enumerate(MONTHS)];surf=pd.concat(parts,ignore_index=True).sort_values('entry_ms').reset_index(drop=True)
 rows=[];ledgers={}
 for wn,(lo,hi) in WINDOWS.items():
  sub=surf[surf.level_age_m5_bars.between(lo,hi)]
  for H in HOLDS:
   led=schedule(sub,H);ledgers[(wn,H)]=led;r=stats(led,H);monthly={m:stats(led[led.entry_month==m],H) for m in MONTHS};pos=sum(v['net']>0 for v in monthly.values())
   rows.append({'window':wn,'age_lo':lo,'age_hi':hi,'hold_s':H,**r,'positive_months':pos,'monthly_json':json.dumps(monthly,sort_keys=True)})
 tab=pd.DataFrame(rows);tab.to_csv(out/'BETA_078_NEIGHBORHOOD_TABLE.csv',index=False)
 candidates=[]
 for r in tab.itertuples():
  if r.trades<MIN_TRADES or r.net<=0 or r.pf<=1 or r.avg<=0 or r.positive_months<MIN_POS_MONTHS:continue
  neigh=[];hs=HOLDS;hi=hs.index(r.hold_s)
  if hi>0:neigh.append((r.window,hs[hi-1]))
  if hi+1<len(hs):neigh.append((r.window,hs[hi+1]))
  neigh += [(w,r.hold_s) for w in WINDOW_NEIGHBORS[r.window]]
  good=[]
  for w,h in neigh:
   z=tab[(tab.window==w)&(tab.hold_s==h)]
   if len(z):
    z=z.iloc[0]
    if z.trades>=NEIGHBOR_MIN and z.net>0 and z.pf>1 and z.avg>0:good.append({'window':w,'hold_s':int(h),'trades':int(z.trades),'net':float(z.net),'pf':float(z.pf)})
  if good:candidates.append((r,good))
 selected=None
 if candidates:
  r,good=sorted(candidates,key=lambda x:(x[0].positive_months,x[0].net,x[0].pf),reverse=True)[0]
  selected={'window':r.window,'age_lo':int(r.age_lo),'age_hi':int(r.age_hi),'hold_s':int(r.hold_s),'neighbor_support':good}
  led=ledgers[(r.window,r.hold_s)].copy();led.insert(0,'qa_trade_id',np.arange(1,len(led)+1));led['selected_pnl']=led[f'pnl_{r.hold_s}s'];led.to_csv(out/'BETA_078_SELECTED_LEDGER.csv.gz',index=False,compression='gzip')
  agg=stats(led,r.hold_s);monthly={m:stats(led[led.entry_month==m],r.hold_s) for m in MONTHS}
 else:
  pd.DataFrame(columns=['qa_trade_id','entry_ms','selected_pnl']).to_csv(out/'BETA_078_SELECTED_LEDGER.csv.gz',index=False,compression='gzip');agg=stats(pd.DataFrame(),900);monthly={}
 qa=selected is not None
 res={'unit_id':UNIT,'status':'HUMAN_QA_RESEARCH_CANDIDATE_NONBLIND' if qa else 'NO_STABLE_NEIGHBORHOOD_CANDIDATE','selected':selected,'aggregate':agg,'monthly':monthly,'human_qa_ready_for_inspection':bool(qa),'selection_data':'Jan-Jul historically inspected/nonblind','august':'SEALED_NOT_READ','warning':'Human QA readiness is engineering/research inspection only; not alpha validation or MT5 approval.'}
 (out/'BETA_078_RESULTS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
 if selected:
  packet='# BETA078 Human-Facing QA Review Packet\n\n'+f"Status: **{res['status']}**  \nAugust: **SEALED**  \nMQL5: **NOT AUTHORIZED**\n\nCandidate: **M5 FIRST_RETEST; level maturity {selected['age_lo']}–{selected['age_hi']} completed M5 bars; fixed {selected['hold_s']}s hold.**\n\nJan-Jul nonblind research score: **{agg['trades']} trades, ${agg['net']:.2f} net, PF {agg['pf']:.3f}, {agg['win_rate']:.1%} win rate, ${agg['avg']:.3f}/trade, max DD ${agg['max_dd']:.2f}.**\n\nMonthly:\n"+'\n'.join([f"- {m}: {v['trades']} trades, ${v['net']:.2f}, PF {v['pf']:.3f}, avg ${v['avg']:.3f}" for m,v in monthly.items()])+"\n\nNeighbor support:\n"+'\n'.join([f"- {n['window']} @ {n['hold_s']}s: {n['trades']} trades, ${n['net']:.2f}, PF {n['pf']:.3f}" for n in selected['neighbor_support']])+"\n\n**Interpretation:** this packet is suitable for human inspection of timing, state-machine logic, trade ledger and reconstruction. The candidate was discovered and selected on Jan-Jul historical data, so profitability is not independently validated. August remains the sealed blind gate.\n"
 else:packet='# BETA078 Human-Facing QA Review Packet\n\nNo stable maturity/hold neighborhood passed. August remains sealed.\n'
 (out/'BETA_078_HUMAN_QA_REVIEW_PACKET.md').write_text(packet);(out/'BETA_078_M5_LEVEL_MATURITY_RETEST_HOLD_NEIGHBORHOOD_REPORT.md').write_text(packet)
 # Compact multi-horizon surface for rebuild/QA.
 np.savez_compressed(out/'BETA_078_MULTI_HORIZON_EXECUTION.npz',event_ms=surf.event_ms.to_numpy(np.int64),entry_ms=surf.entry_ms.to_numpy(np.int64),side=surf.side.to_numpy(np.int8),level_age_m5_bars=surf.level_age_m5_bars.to_numpy(np.int16),**{f'pnl_{h}s':surf[f'pnl_{h}s'].to_numpy(float) for h in HOLDS},**{f'exit_ms_{h}s':surf[f'exit_ms_{h}s'].to_numpy(np.int64) for h in HOLDS})
 (out/'BETA_078_HASHES.json').write_text(json.dumps({p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='BETA_078_HASHES.json'},indent=2,sort_keys=True)+'\n')
 print(json.dumps(res,indent=2,sort_keys=True))
if __name__=='__main__':main()
