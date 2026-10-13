"""GRID0264 paid-source bridge from broker-position HISTORY, not tick quotes.

Research bridge supplies an EA-portable contract. Router earns one source
anchor only after confirmed .01 lot history entry; positive paid-credit only
after full exit, including all observed commission, fee and swap.
"""
from __future__ import annotations
from decimal import Decimal
from v1_grid_mt5_position_ledger_0264 import VerifiedMT5PositionLedger0264,LOT

class PaidSourcePositionBridge0264:
    def __init__(self,*,router,position_ledger:VerifiedMT5PositionLedger0264):
        self.router=router
        self.ledger=position_ledger
        self.proposals:dict[int,tuple[int,str]]={}
        self._entry_ack=set()
        self._exit_ack=set()
    def bind_original_proposal(self,proposal_id:int,position_id:int, *, source_id:str):
        if position_id<=0 or position_id in self.proposals or not source_id:
            raise ValueError('missing or duplicated MT5 position ID')
        if proposal_id not in self.router.funded.proposals:
            raise ValueError('no live original source proposal')
        self.proposals[position_id]=(proposal_id,source_id)
    def acknowledge_entry(self,position_id:int):
        self.ledger._verified()
        if position_id in self._entry_ack:raise ValueError('duplicate entry ACK')
        p=self.ledger.positions[position_id]
        if p.opened!=LOT or p.closed!=0:raise ValueError('complete still-open .01 fill required')
        proposal_id,expected_source=self.proposals[position_id]
        for order_id in p.entry_order_ids:
            req=self.ledger.requests.get(order_id)
            if req is None or req.source_id!=expected_source or req.request_ms<self.router.funded.proposals[proposal_id].quote_ms:
                raise ValueError('paid-source order identity or chronology disagrees with original proposal')
        candidate=self.router.funded.proposals[proposal_id]
        if p.side!=candidate.side:raise ValueError('candidate and broker position direction mismatch')
        # Full partial-fill VWAP may be a FRACTION of the integer raw scale.
        # Research anchor only accepts an exact representable original raw
        # quote; do not guess/round an economic entry price.
        raw=p.vwap_price_raw
        if raw!=raw.to_integral_value():
            raise ValueError('fractional raw-price VWAP needs explicit approved price-grid conversion')
        last_entry_ms=max(d.time_ms for d in self.ledger.applied.values()
                          if d.position_id==position_id and d.kind=='IN')
        self.router.funded.acknowledge_fill(proposal_id=proposal_id,ticket_id=position_id,
                    time_ms=last_entry_ms,side=p.side,actual_price_raw=int(raw),actual_lot=float(LOT))
        p.paid_ack_entry=True
        self._entry_ack.add(position_id)
    def acknowledge_close(self,position_id:int):
        if position_id not in self._entry_ack or position_id in self._exit_ack:
            raise ValueError('paid source requires existing confirmed unique parent entry')
        p=self.ledger.audited_paid_position(position_id)
        latest_close=max(d.time_ms for d in self.ledger.applied.values()
                         if d.position_id==position_id and d.kind=='OUT')
        self.router.funded.acknowledge_close(ticket_id=position_id,close_ms=latest_close,
                                             realized_net_cash=float(p.net_cash))
        p.paid_ack_close=True
        self._exit_ack.add(position_id)
        return p.net_cash
