"""Causal quote-by-quote original JAN037 50ms L3 heartbeat event manufacturer.

Source authority (full exact source files, NOT a research summary):
 * original 032_source/gamma02_campaign_heartbeat_019.py
   london_rule, ny_dir, heartbeat_candidates, original literal THR/NY bands.
 * JAN037 research/jan037_expand_l3.py originally invokes
   HB.heartbeat_candidates(t,mid,h4,h1,m15,m5,50,4) and maps source S=hour+10.

Receives completed original source HTF states and observed quote midpoint.
Produces source entry events but NEVER reads original future exit/PnL arrays.
Source event != physical trade. L7 needs original separate risk permission.
"""
from __future__ import annotations
from dataclasses import dataclass

THR=(0,0,0,0,0,0,0,1000,3000,0,0,2000,0,4000,4000,3000,0,0,0,0,0,0,0,0)
NY17_MIN=(8000,8000,6000,3000,1000,0)
NY18_MIN=(0,0,500,500,2000,1000)
NY18_MAX=(1000000000,1000000000,1000000000,1000000000,1000000000,6000)
TP16=(40000,0,40000,40000,40000,0)
SL16=(20000,40000,40000,60000,60000,40000)
H16=(1200000,1200000,900000,1200000,1200000,1200000)
TP17=(80000,80000,120000,80000,0,120000)
SL17=(40000,40000,60000,40000,60000,120000)
H17=(1800000,)*6
TP18=(12000,12000,12000,8000,4000,4000)
SL18=(8000,8000,6000,8000,1000,2000)
H18=(60000,60000,20000,30000,5000,10000)


def london_rule(hour:int,h4:int,h1:int,m15:int,m5:int)->int:
    if h4!=1 or h1!=1: return 0
    if hour==7:
        if m15==-1 and m5==-1:return 1800000
    elif hour==8:
        if m15==-1 and m5==-1:return 300000
        if m15==-1 and m5==1:return 900000
    elif hour==9:
        if (m15==-1 and m5==-1) or (m15==1 and m5==-1):return 1800000
    elif hour==11:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 1800000
        if m15==1 and m5==-1:return 900000
    elif hour==12:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
        if m15==1 and m5==-1:return 1800000
    elif hour==13:
        if (m15==-1 and m5==-1) or (m15==-1 and m5==1) or (m15==1 and m5==-1):return 1800000
    elif hour==14:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
    elif hour==15:
        if (m15==-1 and m5==1) or (m15==1 and m5==-1) or (m15==1 and m5==1):return 1800000
    return 0


def ny_dir(hour:int,h4:int,h1:int,m15:int,m5:int)->int:
    if hour==16:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==1 and m5==-1:return 1
        if h4==1 and h1==1 and m15==-1 and m5==1:return 1
    elif hour==17:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==-1 and m5==-1:return 1
    elif hour==18:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
    return 0


@dataclass(frozen=True,slots=True)
class OriginalL3HeartbeatEvent:
    quote_ordinal:int
    time_ms:int
    source_id:int
    side:int
    hold_ms:int
    target_raw:int
    stop_raw:int
    @property
    def source_event_key(self)->str:
        return f'JAN037_HEARTBEAT:{self.quote_ordinal}:{self.source_id}:{self.side}'


class OriginalJAN037Heartbeat50ms:
    """Literal streaming state machine of original heartbeat_candidates(...,50,4).

    Assumes caller has already produced independent *completed* original HTF
    states, e.g. source STMR032. No month selection or future exit feedback.
    One first-eligible event per 50ms observed tick or continuous eligibility.
    """
    def __init__(self, interval_ms:int=50,group_code:int=4):
        if interval_ms<=0 or group_code not in (0,1,2,3,4):
            raise ValueError('Invalid frozen JAN037 heartbeat configuration')
        self.interval_ms=interval_ms
        self.group_code=group_code
        self._last_time=-1
        self._last_index=-1
        self._minute=-1
        self._anchor=0
        self._last_fire=[-10**18]*24
        self._last_eligible=[0]*24
        self.events=0

    def on_observed_quote(self,quote_ordinal:int,time_ms:int,mid_raw:int,h4:int,h1:int,m15:int,m5:int)->OriginalL3HeartbeatEvent|None:
        if quote_ordinal<=self._last_index or time_ms<self._last_time:
            raise ValueError('Out-of-order original source quote')
        if mid_raw<=0 or any(type(v) not in (int,) or v not in (-1,0,1) for v in (h4,h1,m15,m5)):
            raise ValueError('Invalid original completed source-state inputs')
        self._last_index=quote_ordinal
        self._last_time=time_ms
        minute=(time_ms//60000)*60000;hour=(time_ms//3600000)%24;b10=(time_ms//600000)%6
        if minute!=self._minute:
            self._minute=minute;self._anchor=mid_raw
        eligible=False;d=0;hh=0;tt=0;ss=0
        if hour<=15 and self.group_code in (0,4):
            hm=london_rule(hour,h4,h1,m15,m5)
            if hm>0:
                d=1;disp=mid_raw-self._anchor
                if disp>=THR[hour]:eligible=True;hh=hm
        elif hour==17 and self.group_code in (1,4):
            d=ny_dir(17,h4,h1,m15,m5)
            if d!=0 and (mid_raw-self._anchor)*d>=NY17_MIN[b10]:
                eligible=True;hh=H17[b10];tt=TP17[b10];ss=SL17[b10]
        elif hour==16 and self.group_code in (2,4):
            d=ny_dir(16,h4,h1,m15,m5)
            if d!=0 and (mid_raw-self._anchor)*d>=500:
                eligible=True;hh=H16[b10];tt=TP16[b10];ss=SL16[b10]
        elif hour==18 and self.group_code in (3,4):
            d=ny_dir(18,h4,h1,m15,m5)
            disp=(mid_raw-self._anchor)*d
            if d!=0 and disp>=NY18_MIN[b10] and disp<NY18_MAX[b10]:
                eligible=True;hh=H18[b10];tt=TP18[b10];ss=SL18[b10]
        if not eligible:
            self._last_eligible[hour]=0
            return None
        fire=self._last_eligible[hour]==0 or time_ms-self._last_fire[hour]>=self.interval_ms
        self._last_eligible[hour]=1
        if not fire:return None
        self._last_fire[hour]=time_ms
        self.events+=1
        return OriginalL3HeartbeatEvent(quote_ordinal,time_ms,hour+10,d,hh,tt,ss)

    def to_live_trade(self,*_args,**_kwargs):
        raise NotImplementedError('JAN037 source event needs separate owner V1 source-permission, L7 funded risk and realized exit verification')
