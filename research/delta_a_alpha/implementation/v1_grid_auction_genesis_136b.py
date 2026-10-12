"""GRID0247, source-faithful as-of April136B HIGHVOL/ASIA price-auction G0.

Recovered original 'apr_session_grid_discovery_136b.py' from protected
GRID0238 source ZIP. This ports ONLY the reproducible first-touch event
geometry, not the original April outcome-selected rule/gap/mode/horizon cells.

No L1-L7 calls, broker fills, positions, cash P/L, or predictions. The
original 136B is month-scoped: this version keeps owner and virtual rung
state continuous across input files, and fails closed on quote hiatus.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

HOUR_MS=3_600_000
DAY_MS=86_400_000

@dataclass(frozen=True)
class NativeGridCross:
    timestamp_ms:int
    source:str
    family:str
    cross_sign:int            # +1 rising midpoint / -1 falling midpoint. NOT a trade side.
    boundary_cell:int
    gap_raw:int
    anchor_raw:int
    bid_raw:int
    ask_raw:int
    owner_id:int

class NativeAuctionGrid136B:
    """One true first-touched midpoint cell per family/direction/owner.

    Source families follow the EXACT original 136B study's time windows:
    HIGHVOL 07..20 UTC hour owner, and ASIA 23..06 UTC 23:00-day owner.
    These time windows are pre-L1 research geometry, NOT broker sessions.
    Gaps are DISCLOSED hypotheses, NOT April's winning parameter selections.
    """
    def __init__(self,*,highvol_gap_raw:int=1000,asia_gap_raw:int=1500,
                 max_quote_gap_ms:int=60_000,max_abs_cell:int=8192):
        if min(highvol_gap_raw,asia_gap_raw,max_quote_gap_ms,max_abs_cell)<=0:
            raise ValueError('positive grid gap/limits required')
        self.gaps={'HIGHVOL':int(highvol_gap_raw),'ASIA':int(asia_gap_raw)}
        self.max_quote_gap_ms=max_quote_gap_ms
        self.max_abs_cell=max_abs_cell
        self.prev_time_ms:Optional[int]=None
        self.state={k:{'owner':None,'anchor':None,'cell':0,'seen':set(),
                       'reset_pending':True} for k in self.gaps}
        self.counts={k:0 for k in ('ticks','events','highvol','asia','hiatus_resets',
                                  'closed_market_resets','repeat_rejections','jump_skipped_cells')}
    @staticmethod
    def _owner(ms, family):
        h=(ms//HOUR_MS)%24
        if family=='HIGHVOL':
            return ms//HOUR_MS if 7<=h<=20 else None
        return (ms-23*HOUR_MS)//DAY_MS if h>=23 or h<7 else None
    def on_quote(self, *,time_ms:int,bid_raw:int,ask_raw:int,tradable:bool=True):
        if self.prev_time_ms is not None and time_ms<self.prev_time_ms:
            raise ValueError('source quotes must arrive in original order')
        if bid_raw<=0 or ask_raw<bid_raw:
            raise ValueError('bad original executable quote')
        hiatus=(self.prev_time_ms is not None and time_ms-self.prev_time_ms>self.max_quote_gap_ms)
        self.prev_time_ms=time_ms
        self.counts['ticks']+=1
        if hiatus:self.counts['hiatus_resets']+=1
        if not tradable:
            self.counts['closed_market_resets']+=1
            for s in self.state.values():s['reset_pending']=True
            return ()
        midpoint=(bid_raw+ask_raw)//2
        for family,gap in self.gaps.items():
            owner=self._owner(time_ms,family)
            if owner is None:continue
            state=self.state[family]
            if owner!=state['owner']:
                state['owner']=owner
                state['seen'].clear()
                state['anchor']=midpoint
                state['cell']=0
                state['reset_pending']=False
                continue
            if hiatus or state['reset_pending']:
                # Does not reset historical first-touched cells within the
                # same owner; but no fake crossing across an unobserved gap.
                state['cell']=(midpoint-state['anchor'])//gap
                state['reset_pending']=False
                continue
            cell=(midpoint-state['anchor'])//gap
            prior=state['cell']
            if cell==prior:continue
            sign=1 if cell>prior else -1
            boundary=cell if sign>0 else prior
            key=(boundary,sign)
            state['cell']=cell
            if not (-self.max_abs_cell<=boundary<self.max_abs_cell):continue
            if key in state['seen']:
                self.counts['repeat_rejections']+=1
                continue
            state['seen'].add(key)
            self.counts['jump_skipped_cells']+=max(0,abs(cell-prior)-1)
            self.counts['events']+=1
            self.counts['highvol' if family=='HIGHVOL' else 'asia']+=1
            return (NativeGridCross(time_ms,'APRIL136B_CAUSAL_CELL_FIRST_TOUCH',
                    family,sign,boundary,gap,state['anchor'],bid_raw,ask_raw,owner),)
        return ()
