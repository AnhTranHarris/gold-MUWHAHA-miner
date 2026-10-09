"""C2C stateful 119 multi-parent admission from actual funded 049 children.

119 offline `cell_admit`: first chronological 049 parent per matching
as-of NY-local macro cell always scouts. Later 049-funded parents sponsor
child streams only after four already-realized fast profitable L4 closes;
a slow/loss close relocks. No precomputed exit arrays or denied-parent PnL.
This is an *implementation contract and causal approximation* of 084's
physical renewal (next observed quote and 0 rearm), not final full 084
exit/residual priority/MT5 brokerage parity.
"""
from __future__ import annotations
from dataclasses import dataclass,field
from collections import defaultdict
from typing import Iterable
from v1_funded_core_033c import Quote,Structure,Proposal,Position,Close,FundedEngine
from original_online_sources_033c import Funded119WatchdogL4,US_DST_START_2026_MS

@dataclass
class Window119:
    parent_id:int
    cell:str
    source:str
    side:int
    admitted_ms:int
    expires_ms:int
    active:bool=True
    children:set[int]=field(default_factory=set)
    last_good_quote_raw:int|None=None
    last_exit_ms:int=-1

class Original119MultiParentL4:
    """New physical L3 parent windows only after funded realized L4 earning.

    It shares one account and cell-level streak/earned state through the
    FundedEngine, with child ownership/actual predecessor tracked per window.
    """
    PARENT_SOURCES=('ORIGINAL_049_UNION_UTC16','ORIGINAL_049_UNION_UTC17',
                    'ORIGINAL_HB_019_UTC16','ORIGINAL_HB_019_UTC17')
    def __init__(self,parent_window_ms:int=1800000):
        self.parent_window_ms=parent_window_ms
        self.windows:dict[int,Window119]={}
        self.cell_windows:dict[str,list[int]]=defaultdict(list)
        self.accepted_children:dict[int,int]={}
        self.eligible_parents=0
        self.admitted_parent_windows=0
        self.denied_uneared_parent_windows=0
        self.rearm_denials=0
        self.outcomes=[]
        self.cell_streak=defaultdict(int)
        self.cell_earned=defaultdict(bool)
        self.earned_parent_admissions=0

    @staticmethod
    def cell_key(q:Quote,s:Structure,side:int)->str|None:
        return Funded119WatchdogL4.original_119_key(q,s,side)

    def on_funded_entry(self,p:Position,q:Quote,s:Structure,engine:FundedEngine):
        if p.layer=='L4' and p.source=='ORIGINAL_119_C2C_CHILD':
            # event key owned by an actual already admitted 049 L3 parent
            parent=int(p.source_event_key.split(':')[1]);w=self.windows.get(parent)
            if w is None or not w.active:raise ValueError('L4 fill not owned by current paid parent window')
            w.children.add(p.id);self.accepted_children[p.id]=parent
            return
        if p.layer!='L3' or p.source not in self.PARENT_SOURCES:return
        cell=self.cell_key(q,s,p.side)
        if cell is None:return
        self.eligible_parents+=1
        ids=self.cell_windows[cell]
        if ids and not self.cell_earned[cell]:
            self.denied_uneared_parent_windows+=1
            return
        w=Window119(p.id,cell,p.source,p.side,q.time_ms,
            min(q.time_ms+self.parent_window_ms,p.expiry_ms))
        self.windows[p.id]=w;ids.append(p.id)
        self.admitted_parent_windows+=1
        if len(ids)>1:self.earned_parent_admissions+=1

    def on_funded_close(self,c:Close,engine:FundedEngine):
        if c.position_id in self.windows:
            w=self.windows[c.position_id];w.active=False
            for child_id in tuple(w.children):engine.request_reduce(child_id)
            self.outcomes.append((c.time_ms,'PAID_L3_PARENT_EXIT',w.parent_id))
        parent=self.accepted_children.pop(c.position_id,None)
        if parent is not None:
            w=self.windows[parent];w.children.discard(c.position_id)
            w.last_exit_ms=c.time_ms
            good=c.net_usd>0 and c.held_ms<=engine.limits.good_hold_ms
            self.cell_streak[w.cell]=(self.cell_streak[w.cell]+1) if good else 0
            self.cell_earned[w.cell]=self.cell_streak[w.cell]>=engine.limits.min_scout_funded_wins
            if good:w.last_good_quote_raw=c.exit_raw
            self.outcomes.append((c.time_ms,'GOOD' if good else 'RELOCK',w.parent_id))

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        out=[]
        # Deterministic event priority: historical earliest admitted windows first.
        for parent_id,w in self.windows.items():
            if not w.active or q.time_ms<=w.admitted_ms:continue
            if q.time_ms>=w.expires_ms or parent_id not in engine.positions:
                w.active=False;continue
            if w.children or q.time_ms<=w.last_exit_ms:continue
            if w.last_good_quote_raw is not None:
                favor=q.bid_raw if w.side>0 else q.ask_raw
                if (favor-w.last_good_quote_raw)*w.side<0:
                    self.rearm_denials+=1;continue
            cell=engine.campaigns[w.cell]
            # Broker-independent source contract: actual funded L3 parent for
            # the first scout, actual L4 earned sponsor for later successes.
            if not cell.scout_consumed:
                sponsor=parent_id;scout=True;earned=False
            elif self.cell_earned[w.cell] and cell.earned and cell.last_good_parent_id is not None:
                sponsor=cell.last_good_parent_id;scout=False;earned=True
            elif cell.scout_children_funded<engine.limits.scout_family_budget:
                sponsor=cell.scout_root_id;scout=True;earned=False
            else:continue
            if sponsor is None or sponsor not in engine._funded_ids:continue
            off=-300 if q.time_ms<US_DST_START_2026_MS else -240
            subphase=((q.time_ms//60000+off)%60)//10
            quantum=1.10 if subphase==5 else 1.19
            ttl=w.expires_ms-q.time_ms
            if ttl<=0:continue
            out.append(Proposal('L4','ORIGINAL_119_C2C_CHILD',w.cell,w.side,
               quantum,0.0,ttl,parent_id=sponsor,first_scout=scout,
               requires_earned_watchdog=earned,
               source_event_key=f'C2CWINDOW:{parent_id}:{q.time_ms}',priority=1))
        return out