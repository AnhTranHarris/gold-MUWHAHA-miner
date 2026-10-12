"""GRID0223 standalone source-derived virtual grid event tape (NOT V1 layer engine).

Uses the *independently reconstructed* GRID0221 helper, not byte-identical
GitHub source. All market inputs are immutable original Dukascopy Bid/Ask.
No funded orders, L1-L7 routing, session optimization or month-based signals.
A single fixed `TRANSITION_OR_CLOSED` geometry prevents the four-session
labels from affecting any standalone-grid event-generation decision.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,sys,time
from pathlib import Path
from collections import Counter
from dataclasses import dataclass
import numpy as np
import pandas as pd
ROOT=Path('/mnt/data'); BASE=ROOT/'grid0221_engine';OUT=ROOT/'grid0223_standalone'
sys.path.insert(0,str(BASE))
from v1_creator_grid_genesis import CreatorGridGenesis
H=3600000;M5=300000
@dataclass(frozen=True)
class Q:
    time_ms_utc:int;bid_raw:int;ask_raw:int
@dataclass(frozen=True)
class B:
    start_ms:int;end_ms:int;open_raw:int;high_raw:int;low_raw:int;close_raw:int
class Bars:
    def __init__(self,p):self.p=p;self.cur=-1;self.o=self.h=self.l=self.c=0;self.completed=None
    def on(self,t,bid):
        start=t//self.p*self.p
        if start!=self.cur:
            if self.cur!=-1:self.completed=B(self.cur,self.cur+self.p,self.o,self.h,self.l,self.c)
            self.cur=start;self.o=self.h=self.l=self.c=bid
        else:
            if bid>self.h:self.h=bid
            if bid<self.l:self.l=bid
            self.c=bid
        return self.completed

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

FILES={m:next(ROOT.glob(f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*gz')) for m in range(1,8)}

def run(month):
    fn=FILES[month];start=time.monotonic()
    df=pd.read_csv(fn,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    ts=df.timestamp_ms_utc.to_numpy();a=df.ask_raw.to_numpy();b=df.bid_raw.to_numpy();del df
    assert len(ts)>1 and np.all(np.diff(ts)>=0) and np.all(a>=b) and np.all(b>0)
    g=CreatorGridGenesis();h=Bars(H);m=Bars(M5)
    ev=[]
    for i in range(len(ts)):
        t=int(ts[i]);bid=int(b[i]);ask=int(a[i]);bh=h.on(t,bid);bm=m.on(t,bid)
        o=g.on_tick(Q(t,bid,ask),bh,'TRANSITION_OR_CLOSED',last_completed_m5=bm,broker_tradable=True)
        for x in o:ev.append((i,x.timestamp_ms,x.side,x.rung,int(round(x.active_gap_usd*1000)),1 if 'CHILD' in x.source else 0))
    events=np.array(ev,dtype=np.int64).reshape(-1,6)
    np.savez_compressed(OUT/f'GRID0223_{month:02d}_EVENT_TAPE.npz',ts=ts,ask=a,bid=b,events=events)
    summary={'month':month,'rows':len(ts),'events':len(events),'parent':int((events[:,5]==0).sum()),'child':int((events[:,5]==1).sum()),'original_gz_sha256':sha256(fn),'reconstructed_helper_sha256':sha256(BASE/'v1_creator_grid_genesis.py'),'seconds':round(time.monotonic()-start,2),'constant_geometry':'TRANSITION_OR_CLOSED','no_funded_trades':True,'no_session_tuning':True}
    (OUT/f'GRID0223_{month:02d}_EVENT_TAPE_QA.json').write_text(json.dumps(summary,indent=2))
    print('MONTH_DONE',json.dumps(summary),flush=True)

if __name__=='__main__':run(int(sys.argv[1]))
