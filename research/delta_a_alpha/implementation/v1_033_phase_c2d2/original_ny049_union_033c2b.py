"""Source-authorized ONLINE NY16/17 original 049 parent candidate manufacture.

An exact port of the ENTRY EVENT logic in source 001 `build_perm_extension_events`
+ `014.build_ny` filters, 017 `rb_ny17`, 019 `heartbeat_candidates`
(120-ms source groups), and `017.union_dedup` priority per (time,source).
The previous source-generated *exit* arrays are intentionally absent.
Full original 049 ENTRY index parity must be tested against untouched source.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from v1_funded_core_033 import Quote,Structure,Proposal,FundedEngine
from original_funded_lineage_033c2 import Original049FundedCapacity
from original_online_sources_033c import Original131CSessionGridL1

NY17_MIN=(8000,8000,6000,3000,1000,0)
SIG16={(-1,-1,-1,-1,-1),(1,1,1,-1,1),(1,1,-1,1,1)}
SIG17={(-1,-1,-1,-1,-1),(1,1,-1,-1,1)}
TP16=(40000,0,40000,40000,40000,0)
SL16=(20000,40000,40000,60000,60000,40000)
H16=(1200000,1200000,900000,1200000,1200000,1200000)
TP17=(80000,80000,120000,80000,0,120000)
SL17=(40000,40000,60000,40000,60000,120000)
H17=(1800000,)*6

@dataclass(frozen=True)
class Native049Event:
    time_ms:int
    side:int
    hour:int
    tp_usd:float
    sl_usd:float
    hold_ms:int
    family:str

class Original049NYSourceL3:
    """Quote-causal original NY source universe, with identical first-source precedence.

    Priorities for (quote_timestamp,utc_hour): original base NY extension
    > original 017 NY17 rebreak > original 019 NY16/17 heartbeat120.
    One source event per tick per NY source is the 049 historical dedup rule.
    """
    def __init__(self,quota:Original049FundedCapacity|None=None):
        self.quota=quota or Original049FundedCapacity()
        self.minute=-1;self.anchor=0;self.hb_anchor=0;self.last_ext=0;self.ext_count=0;self.ext_dir=0
        self.rb_dir=0;self.rb_anchor=0;self.rb_peak=0;self.rb_armed=False;self.rb_armed_at=0
        self.last_fire=[-10**18]*24;self.prev_eligible=[False]*24
        self._obs_t=None;self._obs_mid=None
        self.total_source_events=0;self.eligible_source_events=0
        self.by_family={'001_NY_EXTENSION':0,'017_NY_REBREAK':0,'019_NY_HEARTBEAT120':0}

    def on_market_quote(self,q:Quote,engine:FundedEngine):
        m=q.time_ms//60000*60000;mid=(q.ask_raw+q.bid_raw)//2
        self._obs_t=q.time_ms;self._obs_mid=mid
        if m!=self.minute:
            self.minute=m;self.anchor=mid;self.hb_anchor=mid;self.last_ext=0;self.ext_count=0;self.ext_dir=0
            self.rb_anchor=mid;self.rb_dir=0;self.rb_peak=0;self.rb_armed=False;self.rb_armed_at=0

    def _make(self,q:Quote,s:Structure,side:int,hour:int,family:str)->Native049Event:
        b=int(q.time_ms//600000%6)
        tp,sl,hold=(TP16[b],SL16[b],H16[b]) if hour==16 else (TP17[b],SL17[b],H17[b])
        return Native049Event(q.time_ms,side,hour,tp/1000.,sl/1000.,hold,family)

    def _extension(self,q:Quote,s:Structure,hour:int,mid:int):
        if hour not in (16,17):return None
        d=s.h4 if s.h4!=0 and s.h4==s.h1 else 0
        if not d:return None
        if self.ext_dir!=0 and d!=self.ext_dir:
            self.anchor=mid;self.last_ext=0;self.ext_count=0
        self.ext_dir=d
        disp=(mid-self.anchor)*d
        if disp<=self.last_ext or self.ext_count>=200:return None
        step=(self.last_ext//50+1)*50
        before=self.ext_count
        while disp>=step and self.ext_count<200:
            self.last_ext=step;step+=50;self.ext_count+=1
        if self.ext_count==before:return None
        signature=(s.h4,s.h1,s.m15,s.m5,d)
        if signature not in (SIG16 if hour==16 else SIG17):return None
        threshold=500 if hour==16 else NY17_MIN[int(q.time_ms//600000%6)]
        if self.last_ext<threshold:return None
        return self._make(q,s,d,hour,'001_NY_EXTENSION')

    def _rebreak(self,q:Quote,s:Structure,hour:int,mid:int):
        # `generic_rebreaks_latency(...reset_raw=500,min_elapsed_ms=1000,
        # start_hour=16,end_hour=18,min_depth=50)` and `rb_ny17` masks.
        if hour<16 or hour>18:return None
        d=s.h4 if s.h4!=0 and s.h4==s.h1 else 0
        if d!=self.rb_dir:
            self.rb_dir=d;self.rb_anchor=mid;self.rb_peak=0
            self.rb_armed=False;self.rb_armed_at=0
            if not d:return None
        if not d:return None
        disp=(mid-self.rb_anchor)*d
        if self.rb_peak>=50 and disp<=self.rb_peak-500:
            if not self.rb_armed:self.rb_armed=True;self.rb_armed_at=q.time_ms
        event=False
        level=self.rb_peak
        if self.rb_armed and disp>=self.rb_peak:
            if q.time_ms-self.rb_armed_at>=1000:
                event=True
                self.rb_armed=False;self.rb_armed_at=0
        if disp>self.rb_peak:self.rb_peak=disp
        if not event or hour!=17:return None
        if (s.h4,s.h1,s.m15,s.m5,d) not in SIG17:return None
        if level<NY17_MIN[int(q.time_ms//600000%6)]:return None
        return self._make(q,s,d,hour,'017_NY_REBREAK')

    def _heartbeat(self,q:Quote,s:Structure,hour:int,mid:int):
        if hour not in (16,17):return None
        signature=(s.h4,s.h1,s.m15,s.m5)
        if hour==16:
            side= (-1 if signature==(-1,-1,-1,-1) else
                 1 if signature in ((1,1,1,-1),(1,1,-1,1)) else 0)
        else:
            side=(-1 if signature==(-1,-1,-1,-1) else
                 1 if signature==(1,1,-1,-1) else 0)
        eligible= bool(side) and (mid-self.hb_anchor)*side >= (500 if hour==16 else NY17_MIN[int(q.time_ms//600000%6)])
        if not eligible:
            self.prev_eligible[hour]=False
            return None
        fired=not self.prev_eligible[hour] or q.time_ms-self.last_fire[hour]>=120
        self.prev_eligible[hour]=True
        if not fired:return None
        self.last_fire[hour]=q.time_ms
        return self._make(q,s,side,hour,'019_NY_HEARTBEAT120')

    def source_events(self,q:Quote,s:Structure)->tuple[Native049Event,...]:
        if self._obs_t!=q.time_ms:self.on_market_quote(q,None)
        h=int(q.time_ms//3600000%24);mid=self._obs_mid
        # Advance ALL three underlying mechanisms, even if higher priority
        # source event consumes deduplicated event at the same time.
        extension=self._extension(q,s,h,mid)
        rebreak=self._rebreak(q,s,h,mid)
        hb=self._heartbeat(q,s,h,mid)
        e=extension or rebreak or hb
        if e is None:return ()
        self.total_source_events+=1;self.by_family[e.family]+=1
        return (e,)

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        out=[]
        for i,e in enumerate(self.source_events(q,s)):
            p=Proposal('L3',f'ORIGINAL_049_UNION_UTC{e.hour}',s.grid_key,
               e.side,e.tp_usd,e.sl_usd,e.hold_ms,
               source_event_key=f'049_UNION:{q.time_ms}:{e.hour}:{e.family}')
            if self.quota.permit(p,q.time_ms):
                self.eligible_source_events+=1;out.append(p)
        return out
    def on_funded_entry(self,p,q,s,engine):self.quota.on_funded_entry(p,q,s,engine)
    def on_funded_close(self,c,engine):self.quota.on_funded_close(c,engine)
