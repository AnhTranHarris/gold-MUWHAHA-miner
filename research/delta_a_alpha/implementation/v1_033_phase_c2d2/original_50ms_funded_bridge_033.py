"""C2D3M source-to-physical V1 interface, not historical funded-performance parity.

Unmodified executable authorities (not handoff narratives):
  JAN037/032_source/gamma02_campaign_heartbeat_019.py::heartbeat_candidates
  JAN037/research/jan037_expand_l3.py::S = original_hour + 10
  JAN038/JAN038_SELECTED_EXACT.json::signal_gating_source_phase_pairs
  FEB042/prepare.py::20-second first-observation/phase/spread
  FEB044/feb044_screen.py and FEB045/run_pocket_screens.py (separate gate)
  v1_funded_core_033c.py::FundedEngine.process_quote / funded entry / close

No archived JAN037/FEB042 exit index, PnL, or 25k-lookahead ledger is read.
All source emissions require genuine *as-of* 4-frame structure for physical
funding and remain subject to shared L7. Calendar date/month cannot select mode.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

from v1_funded_core_033c import Quote, Structure, Proposal, Close, FundedEngine
from original_jan037_heartbeat50_online_033 import OriginalJAN037Heartbeat50ms, OriginalL3HeartbeatEvent
from source_jan038_feb042_online_033 import OriginalJAN038FEB042Online, OriginalEntryContext
from source_stmr_completed_ema_033 import STMRState, SourceSTMRCompletedStack


class OriginalJAN037L3QuoteBridge:
    """Sources run on each real quote even when an L7 broker fill must fail shut.

    First call observe_raw_bidask with the current quote/ordinal and original
    completed source states, then FundedEngine.process_quote(q, structure).
    Event state cannot be re-emitted by delayed quotes and cannot emit any
    archive-fitted future exit. Mode flags are fixed for an ENTIRE replay.
    """
    def __init__(self, jan038_rules_path, *, apply_jan038:bool=True,
                 label_family:str='JAN037'):
        if label_family not in ('JAN037','F045'):
            raise ValueError('Source family must be fixed and documented for full run')
        self.manufacturer=OriginalJAN037Heartbeat50ms()
        self.entry_context=OriginalJAN038FEB042Online(jan038_rules_path)
        self.apply_jan038=bool(apply_jan038)
        self.label_family=label_family
        self._latest_quote:Quote|None=None
        self._current_states:tuple[int,int,int,int]|None=None
        self._pending:OriginalL3HeartbeatEvent|None=None
        self._ctx:OriginalEntryContext|None=None
        self._consumed=True
        self.source_events=0
        self.excluded_by_jan038=0
        self.physical_callbacks=0
        self.native_funded_ids=[]
        self.closes=[]

    def observe_raw_bidask(self,ordinal:int, q:Quote,
                           completed_original_states:tuple[int,int,int,int]) -> None:
        if self._latest_quote is not None and q.time_ms<self._latest_quote.time_ms:
            raise ValueError('Source quote order violated')
        if len(completed_original_states)!=4:
            raise ValueError('Four distinct original completed source roles required')
        # Original JAN037 materializes the mid with integer floor exactly.
        mid=(q.ask_raw+q.bid_raw)//2
        self.entry_context.on_quote(q.time_ms,q.ask_raw,q.bid_raw)
        event=self.manufacturer.on_observed_quote(ordinal,q.time_ms,mid,
                                                  *completed_original_states)
        self._latest_quote=q
        self._current_states=tuple(completed_original_states)
        self._pending=event
        self._ctx=self.entry_context.context_for(event.source_id) if event else None
        self._consumed=False
        if event:self.source_events+=1

    def propose(self, q:Quote, s:Structure, engine:FundedEngine)->Iterable[Proposal]:
        if self._consumed or q!=self._latest_quote:
            return ()
        self._consumed=True
        e=self._pending
        if e is None:return ()
        if self._current_states != (s.h4,s.h1,s.m15,s.m5):
            raise ValueError('Source event and L7 structure differ: fail closed')
        if not s.valid_at(q.time_ms):return ()
        if self.apply_jan038 and self._ctx.excluded_by_jan038:
            self.excluded_by_jan038+=1
            return ()
        if e.hold_ms<=0 or e.target_raw<0 or e.stop_raw<0:
            raise ValueError('Source lifecycle not valid for physical bridge')
        # The original JAN037 source defines TP/SL in raw price thousandths;
        # its zero TP/SL explicitly DISABLES that exit, not an invented default.
        oz=engine.one_oz_size
        source=(f'ORIGINAL_F045_S{e.source_id}' if self.label_family=='F045'
                else f'ORIGINAL_J037_S{e.source_id}')
        return (Proposal('L3',source,s.grid_key,e.side,
                         e.target_raw/1000*oz,e.stop_raw/1000*oz,e.hold_ms,
                         source_event_key=e.source_event_key),)

    def on_funded_entry(self,pos,q,s,engine):
        self.physical_callbacks+=1
        self.native_funded_ids.append(pos.id)

    def on_funded_close(self,close:Close,engine:FundedEngine):
        self.closes.append(close)


@dataclass(slots=True)
class OriginalSourceFeed033:
    """Feed pure real BidAsk and original source EMA, independent of L7.

    The JAN037/FEB041 recovery source uses true Bid for its completed EMA
    calculation in its archived original reconstructed tape. The feature
    research mid is still never substituted for physical fills.
    """
    bridge:OriginalJAN037L3QuoteBridge
    structural:SourceSTMRCompletedStack
    ordinal:int=-1

    def on_quote(self,q:Quote)->Structure|None:
        self.ordinal+=1
        state:STMRState=self.structural.on_quote(q.time_ms,source_bid_raw=q.bid_raw)
        roles=state.source_states()
        self.bridge.observe_raw_bidask(self.ordinal,q,roles)
        if not state.fully_observed or any(x is None for x in state.ends_ms):
            return None
        end=tuple(int(x) for x in state.ends_ms)
        completed=max(end)
        if completed>=q.time_ms:return None
        hour=(q.time_ms//3600000)%24
        return Structure('LONDON' if hour<=15 else 'NY',*roles,completed,
            f'ORIGINAL_JAN037_L3_SOURCE_HOUR_{hour}',
            (q.time_ms//600000)%6, end)
