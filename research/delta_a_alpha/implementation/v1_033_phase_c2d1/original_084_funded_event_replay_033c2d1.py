"""DAA-033 C2D1: chronological, source-equivalent 084 owned renewal event machine.

This module deliberately separates source event geometry from physical funding.
Only genuinely funded parent-open callbacks may initialize a window; a real
funded parent-close callback terminates it and causes the original 084 residual
close on that quote (before the ordinary intra-window TP/entry examination).
Actual child funding/denials, spread friction/margin and downstream effects
still belong to the original V1 funded engine; THIS IS NOT ITS REPLACEMENT.

SOURCE: archived gamma02_083_heat_parent_ownership_084.py::renewal_owned.
All price units are raw 1/1000 USD. No future quote/exit arrays are read.
"""
from dataclasses import dataclass,field

@dataclass(frozen=True)
class Event:
    owner:int
    action:str
    tick:int
    entry_tick:int
    raw:int
    exit_pnl:float=0.0
    hold_s:float=0.0
    reason:str=""

@dataclass
class Window:
    owner:int
    side:int
    quantum_raw:int
    rearm_raw:int
    initial_rearm_raw:int
    parent_tick:int
    parent_time_ms:int
    ref_raw:int
    child_tick:int=-1
    child_time_ms:int=-1
    child_entry_raw:int=0
    active:bool=True
    wins:int=0
    residuals:int=0
    events:list=field(default_factory=list)

class Owned084Online:
    """One-pass parent-funded ownership; passive geometry, no order submission."""
    def __init__(self,fee_usd=0.02):
        self.fee=fee_usd
        self.windows={}
        self.events=[]
        self._last_tick=-1

    def _emit(self,w,action,tick,time_ms,price_raw,reason=""):
        if action=='OPEN':
            evt=Event(w.owner,action,tick,tick,price_raw,reason=reason)
        else:
            close_pnl=(price_raw-w.child_entry_raw)*w.side/1000.-self.fee
            evt=Event(w.owner,action,tick,w.child_tick,price_raw,close_pnl,
                      (time_ms-w.child_time_ms)/1000.,reason)
        w.events.append(evt);self.events.append(evt)
        return evt

    def funded_parent_open(self,owner,side,tick,time_ms,ask_raw,bid_raw,quantum_raw,rearm_raw=0,initial_rearm_raw=0):
        if owner in self.windows or side not in (-1,1):raise ValueError('Duplicate parent or invalid direction')
        if min(quantum_raw,rearm_raw,initial_rearm_raw)<0 or quantum_raw==0:raise ValueError('Bad source geometry')
        favored=bid_raw if side>0 else ask_raw
        w=Window(owner,side,quantum_raw,rearm_raw,initial_rearm_raw,tick,time_ms,favored)
        self.windows[owner]=w
        if initial_rearm_raw<=0:
            w.child_tick=tick;w.child_time_ms=time_ms
            w.child_entry_raw=ask_raw if side>0 else bid_raw
            self._emit(w,'OPEN',tick,time_ms,w.child_entry_raw,reason='INITIAL_084')
        return w

    def on_tick(self,tick,time_ms,ask_raw,bid_raw):
        if tick<=self._last_tick:raise ValueError('Ticks must be strictly increasing in index')
        self._last_tick=tick
        emitted=[]
        for w in self.windows.values():
            if not w.active or tick<=w.parent_tick:continue
            fav=bid_raw if w.side>0 else ask_raw
            if w.child_tick<0:
                threshold=w.initial_rearm_raw
                if (fav-w.ref_raw)*w.side>=threshold:
                    w.child_tick=tick;w.child_time_ms=time_ms
                    w.child_entry_raw=ask_raw if w.side>0 else bid_raw
                    emitted.append(self._emit(w,'OPEN',tick,time_ms,w.child_entry_raw,reason='INITIAL_REARM_084'))
                continue
            if w.child_entry_raw==0:
                if (fav-w.ref_raw)*w.side>=w.rearm_raw:
                    w.child_tick=tick;w.child_time_ms=time_ms
                    w.child_entry_raw=ask_raw if w.side>0 else bid_raw
                    emitted.append(self._emit(w,'OPEN',tick,time_ms,w.child_entry_raw,reason='NEXT_REARM_084'))
                continue
            if (fav-w.child_entry_raw)*w.side>=w.quantum_raw:
                emitted.append(self._emit(w,'CLOSE',tick,time_ms,fav,reason='FIRST_TOUCH_QUANTUM_084'))
                w.wins+=1
                w.ref_raw=fav
                w.child_entry_raw=0
                # Original 084 sets cur_i=exit tick: rearm is NEXT tick only.
        return emitted

    def funded_parent_close(self,owner,tick,time_ms,ask_raw,bid_raw):
        w=self.windows[owner]
        if not w.active:raise ValueError('Already terminated')
        w.active=False
        if w.child_entry_raw!=0:
            favored=bid_raw if w.side>0 else ask_raw
            w.residuals+=1
            return self._emit(w,'CLOSE',tick,time_ms,favored,reason='PARENT_RESIDUAL_084')
        return None