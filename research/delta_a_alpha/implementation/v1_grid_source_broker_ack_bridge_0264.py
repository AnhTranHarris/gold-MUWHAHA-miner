"""GRID0264: broker DEAL_ADD-to-cumulative-G0 paid source acknowledgement.

Only broker event contract observed fills and fully closed positions may alter
paid-source anchors. Partial fills are tracked by contract, never credited as
full 0.01-lot parent. No tick-only synthetic settlements or paper quote cash.
HEDGING and verified symbol contract mandatory, fail closed otherwise.
"""
from __future__ import annotations
from decimal import Decimal
from dataclasses import dataclass
from v1_grid_mt5_transaction_contract_0263 import MT5EventContractResearchOnly

@dataclass(frozen=True)
class PaidSourceBinding:
    proposal_id:int
    order_id:str
    position_ticket_id:int
    # The order source_id is an immutable first-party strategy proposal key.
    source_id:str

class GridSourceBrokerAckBridge0264:
    def __init__(self, *, router, contract:MT5EventContractResearchOnly):
        self.router=router
        self.contract=contract
        self.bindings:dict[int,PaidSourceBinding]={}
        self._entry_ack:set[int]=set()
        self._close_ack:set[int]=set()
    def bind(self,x:PaidSourceBinding):
        if x.proposal_id<=0 or x.position_ticket_id<=0 or not x.order_id or not x.source_id:
            raise ValueError('broker order, ticket and source IDs required')
        if x.position_ticket_id in self.bindings:raise ValueError('duplicate position binding')
        p=self.router.funded.proposals.get(x.proposal_id)
        rec=self.contract.orders.get(x.order_id)
        if p is None or rec is None or rec.proposed.source_id!=x.source_id:
            raise ValueError('unrecognized paid source proposal or order')
        if rec.proposed.side!=p.side or rec.proposed.request_ms<p.quote_ms:
            raise ValueError('source chronology or direction conflict')
        self.bindings[x.position_ticket_id]=x
    def _verified(self):
        if self.contract.account_mode!='HEDGING' or not self.contract.verified_symbol:
            raise ValueError('real verified HEDGING broker deal evidence missing')
    def ack_full_entry(self,position_ticket_id:int):
        self._verified()
        if position_ticket_id in self._entry_ack:raise ValueError('duplicate acknowledged paid entry')
        binding=self.bindings[position_ticket_id]
        rec=self.contract.orders[binding.order_id]
        if rec.send_accepted is not True or rec.check_approved is not True:
            raise ValueError('no accepted order request')
        if rec.entry_lots!=Decimal('.01') or rec.close_lots!=0:
            raise ValueError('only fully filled unclosed 0.01-lot parent is supported')
        entries=[d for d in self.contract.deal_evidence.values()
                 if d.order_id==binding.order_id and d.deal_id in rec.deal_ids]
        # Closing receipts may be in deals: entry deals are identified by the
        # still-zero closed volume and record entry chronology. Average partial
        # fill price is VWAP by actual lot, never first-order requested price.
        total=sum((d.lots for d in entries),Decimal('0'))
        if total!=Decimal('.01'):
            raise ValueError('ambiguous entry deal volume')
        vwap=sum((d.lots*Decimal(d.executed_price_raw) for d in entries),Decimal('0'))/total
        if vwap!=vwap.to_integral_value():
            raise ValueError('fractional raw-tick VWAP requires precise price conversion')
        if not entries:raise ValueError('no observed entry deals')
        self.router.funded.acknowledge_fill(proposal_id=binding.proposal_id,
           ticket_id=position_ticket_id,time_ms=max(d.time_ms for d in entries),
           side=rec.proposed.side,actual_price_raw=int(vwap),actual_lot=0.01)
        self._entry_ack.add(position_ticket_id)
    def ack_complete_close(self,position_ticket_id:int):
        self._verified()
        if position_ticket_id not in self._entry_ack or position_ticket_id in self._close_ack:
            raise ValueError('parent must have one previously observed full entry')
        x=self.bindings[position_ticket_id]
        rec=self.contract.orders[x.order_id]
        if rec.entry_lots!=Decimal('.01') or rec.close_lots!=rec.entry_lots:
            raise ValueError('cannot settle paid source while partly open')
        if rec.last_deal_ms is None:raise ValueError('missing close deal')
        # broker order-level observed money includes BOTH entry/exit fees.
        net=rec.realized_cash+rec.broker_fees
        self.router.funded.acknowledge_close(ticket_id=position_ticket_id,
            close_ms=rec.last_deal_ms,realized_net_cash=float(net))
        self._close_ack.add(position_ticket_id)
        return net
