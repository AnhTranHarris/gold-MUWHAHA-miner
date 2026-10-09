"""Phase C2: source-grounded 049/051 funded cap and 075/084/119/131A ownership.

NOT entire V1: 049's ORIGINAL candidate universe is the 024+017+019
union-deduplicated S16/S17 tape. `Original049FundedSource` optionally wraps
an online candidate source but that upstream union is NOT yet reconstructed.
075 is a retrospective quantum/window SEARCH, not itself a parent generator.
119's macro/local-cell gate operates on the 049/051-selected original stream.
The 084 child first-touch tape originally uses PRECOMPUTED parent end and
future price and is not valid as a live funded child stream. We generate from
executed funded positions and observed quotes, without importing future exits.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from v1_funded_core_033 import Quote,Structure,Proposal,Position,Close,FundedEngine
from original_online_sources_033c import Funded119WatchdogL4


@dataclass(frozen=True)
class Original049Settings:
    base_cap: int = 64
    base_step: int = 64
    base_unit: float = 2500.
    base_max: int = 256
    initial_surge: int = 512
    surge_step: int = 256
    surge_unit: float = 1000.
    max_surge: int = 3328
    hard_max: int = 3584
    def __post_init__(self):
        if min(self.base_cap,self.base_step,self.base_unit,self.base_max,
               self.surge_unit,self.hard_max) <= 0 or self.initial_surge<0:
            raise ValueError('Invalid original 049 capacity geometry')


class Original049FundedCapacity:
    """Online, actually-funded realization equivalent to 049/051 capacity rule.

    Only actual funded source closes contribute to the realized P&L.  The L7
    governor still decides whether an eligible source proposal is PHYSICALLY
    filled.  This source-specific cap is not the entire account governor.
    """
    def __init__(self, settings:Original049Settings|None=None):
        self.cfg=settings or Original049Settings()
        self.realized=0.
        self.funded_active:set[int]=set()
        self.funded_source_ids:set[int]=set()
        self.eligible=0
        self.denied=0
        self.unlocks=[]
        self._last_allowed=None

    def cap(self)->int:
        z=self.cfg
        base=min(z.base_max,z.base_cap+int(max(0.,self.realized)//z.base_unit)*z.base_step)
        surge=min(z.max_surge,z.initial_surge+int(max(0.,self.realized)//z.surge_unit)*z.surge_step)
        return min(z.hard_max,base+surge)

    @staticmethod
    def is_049_candidate(p:Proposal)->bool:
        return p.layer=='L3' and p.source in ('ORIGINAL_HB_019_UTC16','ORIGINAL_HB_019_UTC17',
                             'ORIGINAL_049_UNION_UTC16','ORIGINAL_049_UNION_UTC17')

    def permit(self, proposal:Proposal,time_ms:int)->bool:
        if not self.is_049_candidate(proposal):return True
        allowed=self.cap()
        if allowed!=self._last_allowed:
            self.unlocks.append((time_ms,allowed));self._last_allowed=allowed
        self.eligible+=1
        if len(self.funded_active)>=allowed:
            self.denied+=1
            return False
        return True

    def on_funded_entry(self,p:Position,q:Quote,s:Structure,engine:FundedEngine):
        if p.layer=='L3' and p.source in ('ORIGINAL_HB_019_UTC16','ORIGINAL_HB_019_UTC17',
                              'ORIGINAL_049_UNION_UTC16','ORIGINAL_049_UNION_UTC17'):
            self.funded_active.add(p.id)
            self.funded_source_ids.add(p.id)

    def on_funded_close(self,c:Close,engine:FundedEngine):
        if c.position_id in self.funded_active:
            self.funded_active.remove(c.position_id)
            self.realized+=c.net_usd


class Original049OnlineSource:
    """Delegates ORIGINAL 019 proposals; applies 049 quota to S16/S17.

    The raw 049 union candidate *manufacture* (024/017/019) is not here.
    For 049 exact source parity, that union generator must be ported first.
    """
    def __init__(self,underlying,quota:Original049FundedCapacity):
        self.underlying=underlying
        self.quota=quota
    def on_market_quote(self,q,engine):
        cb=getattr(self.underlying,'on_market_quote',None)
        if cb:cb(q,engine)
    def propose(self,q,s,engine)->Iterable[Proposal]:
        return tuple(p for p in self.underlying.propose(q,s,engine)
                     if self.quota.permit(p,q.time_ms))
    def on_funded_entry(self,p,q,s,engine):
        self.quota.on_funded_entry(p,q,s,engine)
        cb=getattr(self.underlying,'on_funded_entry',None)
        if cb:cb(p,q,s,engine)
    def on_funded_close(self,c,engine):
        self.quota.on_funded_close(c,engine)
        self.underlying.on_funded_close(c,engine)


class Original119FundedParentSource(Funded119WatchdogL4):
    """119/131A original parent-CELL admission and quote-causal rearm.

    119 gets parent candidates from the 049/051-selected S16/S17 stream.
    It does NOT apply 075's fitted 30-39 minute cut automatically.
    `funded` means L7 actually accepted original 049 L3 candidate.
    C1's per-cell FIRST parent is currently used (later earned additional
    119 parent windows are pending exact original parity).
    """
    def __init__(self,*,parent_quote_window_ms=1800000):
        super().__init__(parent_sources=('ORIGINAL_HB_019_UTC16','ORIGINAL_HB_019_UTC17',
                      'ORIGINAL_049_UNION_UTC16','ORIGINAL_049_UNION_UTC17'),
                      parent_quote_window_ms=parent_quote_window_ms)
        self.last_favorable_ref:dict[str,int]={}
        self.renewal_rearm_rejects=0
        self.parent_candidates=0
        self.parent_funded=0

    def on_funded_entry(self,p:Position,q:Quote,s:Structure,engine:FundedEngine):
        was=len(self.parents)
        super().on_funded_entry(p,q,s,engine)
        if p.layer=='L3' and p.source in self.parent_sources:
            if self.original_119_key(q,s,p.side) is not None:
                self.parent_candidates+=1
                if len(self.parents)>was:self.parent_funded+=1
        # First scout has no prior exit-reference; permit next observed tick.

    def on_funded_close(self,c:Close,engine:FundedEngine):
        # Executable exit price, never a hindsight-favorable MFE.
        was_cell=self.funded_wd_by_id.get(c.position_id)
        super().on_funded_close(c,engine)
        if was_cell is not None and c.net_usd>0:
            self.last_favorable_ref[was_cell]=c.exit_raw

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        proposals=super().propose(q,s,engine)
        retained=[]
        for p in proposals:
            ref=self.last_favorable_ref.get(p.cell)
            # Exact 084 rearm_raw=0: next renewal long requires executable
            # BID >= previously observed favorable BID, short ASK <= prior ASK.
            fav=q.bid_raw if p.side>0 else q.ask_raw
            if ref is not None and (fav-ref)*p.side<0:
                self.renewal_rearm_rejects+=1
                continue
            retained.append(p)
        return retained