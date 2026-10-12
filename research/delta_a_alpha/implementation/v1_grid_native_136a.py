"""April 136A original causal minute-displacement GENESIS, isolated from hindsight.

Port from original apr_native_markout_136.py: build_events. Only the as-of
rung displacement source is reconstructed; original downstream selected cells,
hold/TP/SL optimization, future markouts, and monthly labels are not imported.
H4/H1/M15/M5 signs MUST have been formed on completed bars externally, else
fail closed. Diagnostics may use clock hour as original source did, but owner
must authorize any change of discovery-stage session scope. Grid-stage only.
"""
from dataclasses import dataclass

MINUTE=60000
HOUR=3600000

@dataclass(frozen=True)
class Native136AEvent:
    timestamp_ms:int
    source:str
    side:int
    rung_raw:int
    grid_step_raw:int
    minute_owner:int
    h4:int
    h1:int
    m15:int
    m5:int
    ten_min_phase:int

class NativeMinuteRungs136A:
    def __init__(self,*,step_raw=50,minimum_rung_raw=250,first_only_per_minute=False,
                 max_quote_gap_ms=60000,source_hours=(7,19)):
        if step_raw<=0 or minimum_rung_raw<0 or max_quote_gap_ms<=0:raise ValueError('bad grid configuration')
        self.step_raw=step_raw
        self.minimum_rung_raw=minimum_rung_raw
        self.first_only_per_minute=first_only_per_minute
        self.max_quote_gap_ms=max_quote_gap_ms
        self.source_hours=source_hours
        self.prev_time=None
        self.last_minute=None
        self.last_side=0
        self.anchor=0
        self.last_ext=0
        self.emitted=False
        self.counts={'ticks':0,'reset':0,'eligible':0,'rungs':0,'discarded_unknown_completed_roles':0,'hiatus':0}
    def on_quote(self,*,time_ms,bid_raw,ask_raw,completed_h4_sign=None,
                 completed_h1_sign=None,completed_m15_sign=None,completed_m5_sign=None,
                 broker_tradable=True):
        if self.prev_time is not None and time_ms<self.prev_time:raise ValueError('unordered quote')
        if bid_raw<=0 or ask_raw<bid_raw:raise ValueError('bad Bid/Ask quote')
        hiatus=self.prev_time is not None and time_ms-self.prev_time>self.max_quote_gap_ms
        self.prev_time=time_ms
        self.counts['ticks']+=1
        if not broker_tradable or hiatus:
            if hiatus:self.counts['hiatus']+=1
            self.last_minute=None
            self.last_side=0
            return ()
        if not self.source_hours[0]<=((time_ms//HOUR)%24)<=self.source_hours[1]:return ()
        if any(s is None for s in (completed_h4_sign,completed_h1_sign,completed_m15_sign,completed_m5_sign)):
            self.counts['discarded_unknown_completed_roles']+=1
            self.last_minute=None
            return ()
        h4,h1,m15,m5=(int(completed_h4_sign),int(completed_h1_sign),int(completed_m15_sign),int(completed_m5_sign))
        if any(s not in (-1,0,1) for s in (h4,h1,m15,m5)):raise ValueError('completed signs must be -1, 0, +1')
        side=h4 if h4!=0 and h4==h1 else 0
        if side==0:
            self.last_minute=None
            return ()
        minute=time_ms//MINUTE
        midpoint=(bid_raw+ask_raw)//2
        if minute!=self.last_minute or side!=self.last_side:
            self.last_minute=minute
            self.anchor=midpoint
            self.last_side=side
            self.last_ext=0
            self.emitted=False
            self.counts['reset']+=1
            return ()
        displacement=(midpoint-self.anchor)*side
        if displacement<=self.last_ext:return ()
        level=(displacement//self.step_raw)*self.step_raw
        if level<=self.last_ext:return ()
        self.last_ext=level
        self.counts['eligible']+=1
        if level<self.minimum_rung_raw or (self.first_only_per_minute and self.emitted):return ()
        self.emitted=True
        self.counts['rungs']+=1
        return (Native136AEvent(time_ms,'APRIL136A_CAUSAL_NATIVE_MINUTE_RUNG',side,
               level,self.step_raw,minute,h4,h1,m15,m5,int((time_ms//600000)%6)),)
