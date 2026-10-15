"""V2 F1 incremental stream chassis. No broker orders. Source-neutral timeframes.
Research code built to verify as-of causal feature parity with batch precomputation.
Caller must provide original UTC millisecond quote events, strictly nondecreasing.
Missing time intervals are NOT synthesized; open candles close only on next observed tick.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import math

PERIODS={'S1':1000,'S5':5000,'S15':15000,'S30':30000,'M1':60000,'M5':300000,'M15':900000,'H1':3600000,'H4':14400000}

@dataclass(frozen=True)
class Bar:
    start_ms:int
    end_ms:int
    opening:float
    high:float
    low:float
    closing:float
    quote_updates:int

class Candle:
    __slots__=('p','start','o','h','l','c','count','complete')
    def __init__(self,period_ms:int):
        self.p=period_ms;self.start=None;self.o=self.h=self.l=self.c=None;self.count=0;self.complete=None
    def push(self,ts:int,bid:float):
        start=(ts//self.p)*self.p
        if self.start!=start:
            if self.start is not None:self.complete=Bar(self.start,self.start+self.p,self.o,self.h,self.l,self.c,self.count)
            self.start=start;self.o=self.h=self.l=self.c=bid;self.count=1
            return self.complete
        self.h=max(self.h,bid);self.l=min(self.l,bid);self.c=bid;self.count+=1
        return None

@dataclass(frozen=True)
class Snapshot:
    time_ms:int
    bid:float
    ask:float
    spread:float
    elapsed_m1_s:float
    minute_open_mid:float
    minute_buy_bracket:float
    minute_sell_bracket:float
    sessions:tuple[str,...]
    completed:dict[str,Bar|None]
    s1_quality:int
    s1_efficiency:float
    s1_range:float
    s1_turns:int
    s1_displacement:float

class StreamingF1:
    def __init__(self):
        self.bars={name:Candle(p) for name,p in PERIODS.items()}
        self.micro=deque(maxlen=12)
        self.last_second=None
        self.last_ts=None
        self.minute=-1;self.mid=0.;self.total_ticks=0
        self.last_snapshot=None
    def _market_sessions(self,ts):
        utc=datetime.fromtimestamp(ts/1000,timezone.utc)
        sess=[]
        for name,zone,lo,hi in [('SYDNEY','Australia/Sydney',8,17),('TOKYO','Asia/Tokyo',9,18),('LONDON','Europe/London',8,17),('NEW_YORK','America/New_York',8,17)]:
            t=utc.astimezone(ZoneInfo(zone))
            if t.weekday()<5 and lo<=t.hour<hi:sess.append(name)
        return tuple(sess)
    def _micro_quality(self):
        # Match original R9 S1QualityForSide semantics over completed S1 candle closes.
        if len(self.micro)<10:return 0,0.,0.,0,0.
        recent=list(self.micro)[-10:]
        start=recent[0].closing;end=recent[-1].closing
        vals=[x.closing for x in recent];travel=sum(abs(vals[k]-vals[k-1]) for k in range(1,len(vals)))
        disp=end-start;eff=abs(disp)/(travel+1e-9)
        signs=[1 if vals[k]>vals[k-1] else(-1 if vals[k]<vals[k-1] else 0) for k in range(1,len(vals))]
        active=[x for x in signs if x];turns=sum(active[k]!=active[k-1] for k in range(1,len(active)))
        span=max(x.high for x in recent)-min(x.low for x in recent)
        direction=0
        if eff>=.70 and turns<=9 and span>=.50:
            direction=1 if disp>=.15 else(-1 if disp<=-.15 else 0)
        return direction,eff,span,turns,disp
    def on_quote(self,time_ms_utc:int,bid_raw:int,ask_raw:int)->Snapshot:
        if self.last_ts is not None and time_ms_utc<self.last_ts:raise ValueError('unordered raw tick input')
        if bid_raw<=0 or ask_raw<bid_raw:raise ValueError('invalid original Bid/Ask quote')
        self.last_ts=time_ms_utc;bid=bid_raw*.001;ask=ask_raw*.001
        sec=time_ms_utc//1000
        if self.minute!=time_ms_utc//60000:
            self.minute=time_ms_utc//60000;self.mid=.5*(bid+ask)
        for name,c in self.bars.items():
            completed=c.push(time_ms_utc,bid)
            if name=='S1' and completed is not None:
                # Prevent S1 buffer completing with nonexistent synthetic seconds.
                self.micro.append(completed)
        d,eff,span,turns,disp=self._micro_quality()
        # Never interpret a stale S1 buffer across a gap as a contiguous 10-second window.
        if self.micro and (sec*1000-self.micro[-10].start_ms>22000 if len(self.micro)>=10 else False):
            d,eff,span,turns,disp=0,0.,0.,0,0.
        self.total_ticks+=1
        s=Snapshot(time_ms_utc,bid,ask,ask-bid,(time_ms_utc%60000)/1000,self.mid,self.mid+.15,self.mid-.15,self._market_sessions(time_ms_utc),{k:v.complete for k,v in self.bars.items()},d,eff,span,turns,disp)
        self.last_snapshot=s
        return s
    def candidate_bracket(self,s:Snapshot,after_actual_funded_exit_opposite:int=0)->int:
        if s.s1_quality==0:return 0
        if after_actual_funded_exit_opposite!=0 and after_actual_funded_exit_opposite!=s.s1_quality:return 0
        if s.s1_quality==1 and s.ask>=s.minute_buy_bracket:return 1
        if s.s1_quality==-1 and s.bid<=s.minute_sell_bracket:return -1
        return 0
