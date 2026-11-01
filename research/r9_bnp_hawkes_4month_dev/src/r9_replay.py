#!/usr/bin/env python3
"""Source-faithful causal R9 HybridGate tick replay (NOT MT5 fill equivalence).

Pins original MQL5 EA at GitHub commit 8729a6345655a7b4ea31facc81982004ee2b8921,
blob SHA 7eecb5f1947017a01ce85b2520725de54749e523.

No generated OHLC intrabar ticks. One continuous forward pass over actual quote ticks.
Time fields remain source-native broker timestamps for reproducing R9's
InpQuoteUtcOffsetMinutes=0 bug; `utc_ms` is only for cross-source reporting.
"""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, gzip, hashlib, json, math
from dataclasses import asdict, dataclass
from pathlib import Path
from functools import lru_cache
from typing import Iterator

MS=1000
MONTH=dt.timezone.utc

@dataclass(frozen=True)
class Config:
    lots:float=.01
    gap_pips:int=30
    stop_pips:int=30
    trail_pips:int=3
    trail_activation_pips:int=10
    max_hold_s:int=30
    max_rearms:int=3
    vel_lookback_s:int=10
    min_vel_pips:int=15
    min_eff:float=.70
    range_lookback_s:int=10
    min_range_pips:int=50
    max_turns:int=9
    atr_period:int=14
    max_spread_points:int=25
    fail_closed_atr:bool=True
    pip_price:float=.01
    point:float=.01
    tick_size:float=.01
    min_stop_points:int=0
    commission_per_side:float=.01
    contract_multiplier:float=1.0 # 0.01 lot * 100 oz per lot = 1 oz
    initial_balance:float=100_000
    utc_offset_minutes:int=0 # unaltered MQL input, intentional
    atr_london:float=2.0
    atr_overlap:float=1.75
    atr_ny:float=1.75
    atr_off:float=2.5
    record_every_trade:bool=True

@dataclass(frozen=True)
class Tick:
    native_ms:int
    utc_ms:int
    bid:float
    ask:float


def dtsec(s:int)->dt.datetime:
    return dt.datetime.fromtimestamp(s,dt.timezone.utc)

def offset_minutes_for_coinexx_ms(ms:int)->int:
    # Observed 2026 broker clock transition around March 6-9; for Jan/Jul replay.
    # This is a conservative per-date segmentation, not a universal timezone library.
    ymd=int(dtsec(ms//1000).strftime('%Y%m%d'))
    return 180 if 20260309<=ymd<20261102 else 120

def iter_ticks(path:str,source:str,limit:int|None=None)->Iterator[Tick]:
    with gzip.open(path,'rt',newline='') as fh:
        rows=csv.DictReader(fh)
        prev=-1
        for i,row in enumerate(rows):
            if limit is not None and i>=limit:break
            if source=='coinexx':
                ts=int(row['time_msc']);bid=float(row['bid']);ask=float(row['ask'])
                utc=ts-offset_minutes_for_coinexx_ms(ts)*60_000
            elif source=='dukascopy':
                ts=int(row['timestamp_ms_utc']);bid=int(row['bid_raw'])/1000;ask=int(row['ask_raw'])/1000;utc=ts
            else:raise ValueError(source)
            if ts<prev:raise ValueError(f'Nonmonotonic input tick at {i}: {ts} < {prev}')
            prev=ts
            if bid<=0 or ask<=0 or ask<bid:continue
            yield Tick(ts,utc,bid,ask)


def mql_round_price(price:float,tick:float)->float:
    # MQL MathRound: half-interval away from zero for nonnegative XAUUSD quotes.
    return round(math.floor(price/tick+0.5)*tick, 6)

@lru_cache(maxsize=100000)
def session_minimum(native_s:int,cfg:Config)->float:
    utc=dtsec(native_s-cfg.utc_offset_minutes*60)
    year=utc.year
    def nth_sunday(y,m,n):
        first=dt.datetime(y,m,1,tzinfo=dt.timezone.utc)
        return 1+(6-first.weekday())%7+(n-1)*7
    def last_sunday(y,m):
        if m==12:nxt=dt.datetime(y+1,1,1,tzinfo=dt.timezone.utc)
        else:nxt=dt.datetime(y,m+1,1,tzinfo=dt.timezone.utc)
        d=(nxt-dt.timedelta(days=1))
        return d.day-(d.weekday()+1)%7
    london_start=dt.datetime(year,3,last_sunday(year,3),1,tzinfo=dt.timezone.utc)
    london_end=dt.datetime(year,10,last_sunday(year,10),1,tzinfo=dt.timezone.utc)
    ny_start=dt.datetime(year,3,nth_sunday(year,3,2),7,tzinfo=dt.timezone.utc)
    ny_end=dt.datetime(year,11,nth_sunday(year,11,1),6,tzinfo=dt.timezone.utc)
    lo_offset=60 if london_start<=utc<london_end else 0
    ny_offset=-240 if ny_start<=utc<ny_end else -300
    l=utc+dt.timedelta(minutes=lo_offset);n=utc+dt.timedelta(minutes=ny_offset)
    lom=l.hour*60+l.minute;nom=n.hour*60+n.minute
    in_l=8*60<=lom<16*60+30;in_n=8*60<=nom<17*60
    if in_l and in_n:return cfg.atr_overlap
    if in_l:return cfg.atr_london
    if in_n:return cfg.atr_ny
    return cfg.atr_off

class M5ATR:
    """Completed source-native bid M5 bars; classic Wilder smoothing, no hindsight."""
    def __init__(self,period:int):
        self.period=period;self.m5=None;self.o=self.h=self.l=self.c=0.
        self.prev_close=None;self.tr_seed=[];self.atr=None
        self.completed=0
    def update(self,s:int,bid:float):
        bar=(s//300)*300
        if self.m5 is None:
            self.m5=bar;self.o=self.h=self.l=self.c=bid;return
        if bar!=self.m5:
            if self.prev_close is not None:
                tr=max(self.h-self.l,abs(self.h-self.prev_close),abs(self.l-self.prev_close))
                if self.atr is None:
                    self.tr_seed.append(tr)
                    if len(self.tr_seed)==self.period:self.atr=sum(self.tr_seed)/self.period
                else:self.atr=(self.atr*(self.period-1)+tr)/self.period
            self.completed+=1
            self.prev_close=self.c
            self.m5=bar;self.o=self.h=self.l=self.c=bid
        else:
            self.h=max(self.h,bid);self.l=min(self.l,bid);self.c=bid
    def ready(self):
        return self.atr is not None and self.completed>=self.period+2

class Replay:
    def __init__(self,cfg:Config):
        self.cfg=cfg
        self.atr=M5ATR(cfg.atr_period)
        self.bucket=None;self.bar=[];self.micro=collections.deque(maxlen=128)
        self.cycle_min=0;self.cycle_buy=0.;self.cycle_sell=0.;self.pending_mode=0;self.rearms=0
        self.had_position=False;self.last_position_type=1;self.position=None
        self.balance=cfg.initial_balance;self.high_balance=cfg.initial_balance;self.max_dd=0.
        self.stats=collections.Counter();self.closed=[];self.entries=[];self.n=0
    def update_bucket(self,s,bid):
        if self.bucket is None:
            self.bucket=s;self.bar=[bid,bid,bid,bid];return
        if s!=self.bucket:
            self.micro.append((self.bucket,*self.bar))
            self.bucket=s;self.bar=[bid,bid,bid,bid]
            return
        self.bar[1]=max(self.bar[1],bid)
        self.bar[2]=min(self.bar[2],bid)
        self.bar[3]=bid
    def start_cycle(self,s,bid,ask):
        m=s-s%60
        if m!=self.cycle_min:
            self.cycle_min=m;self.rearms=0;self.pending_mode=2
            mid=(bid+ask)/2;half=self.cfg.gap_pips*self.cfg.pip_price/2
            self.cycle_buy=mql_round_price(mid+half,self.cfg.tick_size)
            self.cycle_sell=mql_round_price(mid-half,self.cfg.tick_size)
    def quality(self,side):
        c=self.cfg;need=max(c.vel_lookback_s,c.range_lookback_s)+1
        if len(self.micro)<need:return False
        arr=list(self.micro)
        closes=[x[4] for x in arr[-c.vel_lookback_s:]]
        disp=closes[-1]-closes[0]
        travel=sum(abs(b-a) for a,b in zip(closes,closes[1:]))
        eff=abs(disp)/(travel+1e-9)
        prevsign=0;turns=0
        for a,b in zip(closes,closes[1:]):
            sign=1 if b>a else -1 if b<a else 0
            if sign:
                if prevsign and sign!=prevsign:turns+=1
                prevsign=sign
        recent=arr[-c.range_lookback_s:]
        ran=max(r[2] for r in recent)-min(r[3] for r in recent)
        return (eff+1e-12>=c.min_eff and turns<=c.max_turns
                and ran+1e-12>=c.min_range_pips*c.pip_price
                and (disp+1e-12>=c.min_vel_pips*c.pip_price if side>0
                    else disp-1e-12<=-c.min_vel_pips*c.pip_price))
    def gate(self,t,s):
        c=self.cfg
        if (t.ask-t.bid)/c.point>c.max_spread_points+1e-9:
            self.stats['gate_spread']+=1;return False
        if not self.atr.ready():
            self.stats['gate_no_atr']+=1
            return not c.fail_closed_atr
        if self.atr.atr+1e-12<session_minimum(s//60*60,c):
            self.stats['gate_low_atr']+=1;return False
        return True
    def close(self,t,s,why,exit_price):
        p=self.position
        pnl=(exit_price-p['entry_price'])*p['side']*self.cfg.contract_multiplier-2*self.cfg.commission_per_side
        self.balance+=pnl
        self.high_balance=max(self.high_balance,self.balance)
        self.max_dd=max(self.max_dd,self.high_balance-self.balance)
        trade={**p,'exit_time_ms':t.native_ms,'exit_time_utc_ms':t.utc_ms,'exit_price':exit_price,'reason':why,'hold_seconds':s-p['entry_sec'],'net':round(pnl,5),'balance':round(self.balance,5)}
        self.closed.append(trade)
        self.stats['closed_'+why]+=1
        self.position=None
        # MQL had_pos remains True until next tick (Reconcile handles missing position)
    def on_tick(self,t):
        self.n+=1;s=t.native_ms//1000
        self.atr.update(s,t.bid);self.update_bucket(s,t.bid);self.start_cycle(s,t.bid,t.ask)
        p=self.position
        if p is not None:
            # MT5 broker executes the existing SL before MQL OnTick sees the quote.
            if p['side']==1 and t.bid<=p['sl']:
                self.close(t,s,'stop',t.bid);return
            if p['side']==-1 and t.ask>=p['sl']:
                self.close(t,s,'stop',t.ask);return
            if s-p['entry_sec']>=self.cfg.max_hold_s:
                self.close(t,s,'timeout',t.bid if p['side']==1 else t.ask);return
            if self.cfg.trail_pips>0:
                ts=self.cfg.tick_size;broker=self.cfg.min_stop_points*self.cfg.point
                if p['side']==1 and t.bid-p['entry_price']>=self.cfg.trail_activation_pips*self.cfg.pip_price:
                    cand=mql_round_price(t.bid-self.cfg.trail_pips*self.cfg.pip_price,ts)
                    cand=min(cand,mql_round_price(t.bid-broker-ts,ts))
                    if cand>p['sl']+ts*0.5:p['sl']=cand;self.stats['trail_updates']+=1
                if p['side']==-1 and p['entry_price']-t.ask>=self.cfg.trail_activation_pips*self.cfg.pip_price:
                    cand=mql_round_price(t.ask+self.cfg.trail_pips*self.cfg.pip_price,ts)
                    cand=max(cand,mql_round_price(t.ask+broker+ts,ts))
                    if cand<p['sl']-ts*0.5:p['sl']=cand;self.stats['trail_updates']+=1
            return
        if self.had_position:
            self.had_position=False
            if self.rearms>=self.cfg.max_rearms:self.pending_mode=0
            else:
                self.rearms+=1
                self.pending_mode=-self.last_position_type
            self.stats['rearms']+=1;return
        if self.pending_mode==0:return
        if not self.gate(t,s):return
        side=0
        if self.pending_mode in (2,1) and t.ask>=self.cycle_buy:side=1
        elif self.pending_mode in (2,-1) and t.bid<=self.cycle_sell:side=-1
        if side==0:return
        if not self.quality(side):
            self.stats['gate_s1']+=1;return
        # Normalize and quote-side anchored SL exactly as current R9 code.
        stop=max(self.cfg.stop_pips*self.cfg.pip_price,self.cfg.min_stop_points*self.cfg.point+self.cfg.tick_size)
        sl=mql_round_price(t.bid-stop if side==1 else t.ask+stop,self.cfg.tick_size)
        entry_price=t.ask if side==1 else t.bid
        self.position={'entry_time_ms':t.native_ms,'entry_time_utc_ms':t.utc_ms,'entry_sec':s,'entry_price':entry_price,'initial_sl':sl,'sl':sl,'side':side,'entry_cycle_s':self.cycle_min,'rearm':self.rearms}
        self.entries.append({'time_ms':t.native_ms,'utc_ms':t.utc_ms,'side':side,'price':entry_price,'initial_sl':sl,'cycle_s':self.cycle_min,'rearm':self.rearms})
        self.had_position=True;self.last_position_type=side;self.pending_mode=0
        self.stats['entries']+=1

def run(path,source,cfg,limit=None):
    sim=Replay(cfg);first=None;last=None
    for t in iter_ticks(path,source,limit):
        if first is None:first=t.native_ms
        last=t.native_ms
        sim.on_tick(t)
    result={'status':'research_only_unverified_fill_parity','source':source,'input':str(Path(path).name),
            'source_sha256':sha256(path),'config':asdict(cfg),'ticks_seen':sim.n,
            'first_tick_ms':first,'last_tick_ms':last,
            'entries':len(sim.entries),'closed':len(sim.closed),'open_at_eof':sim.position,
            'net_closed':round(sim.balance-cfg.initial_balance,4),'final_balance':round(sim.balance,4),
            'max_balance_dd':round(sim.max_dd,4),'by_reason':dict(sim.stats),
            'first_entries':sim.entries[:20],'first_closed':sim.closed[:20]}
    return sim,result

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def write_results(sim,summary,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/'summary.json').open('w') as f:json.dump(summary,f,indent=2)
    for name,records in [('entries.csv',sim.entries),('trades.csv',sim.closed)]:
        if records:
            with (out/name).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ticks',required=True);ap.add_argument('--source',required=True,choices=['coinexx','dukascopy'])
    ap.add_argument('--out',required=True);ap.add_argument('--limit',type=int)
    ap.add_argument('--config',help='JSON object of overrides')
    args=ap.parse_args()
    cfg=Config(**(json.loads(Path(args.config).read_text()) if args.config else {}))
    sim,summary=run(args.ticks,args.source,cfg,args.limit);write_results(sim,summary,args.out)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('first_entries','first_closed','config')},indent=2))
if __name__=='__main__':main()
