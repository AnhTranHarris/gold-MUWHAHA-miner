"""GRID0264: broker-side stop change is real only after observed MT5 ACK.

A Python trailing calculation is NOT proof that the broker installed the SL.
Require an independent observed MT5 server quote, SYMBOL_* constraint values
and observed position SL readback. Rejections leave the original stop intact.
"""
from __future__ import annotations
from dataclasses import dataclass
from v1_grid_mt5_position_ledger_0264 import VerifiedMT5PositionLedger0264

@dataclass(frozen=True)
class ObservedStopModify:
    modify_id:str
    position_id:int
    request_ms:int
    reply_ms:int
    proposed_stop_raw:int
    reported_position_stop_raw:int|None
    current_broker_bid_raw:int
    current_broker_ask_raw:int
    stops_distance_raw:int
    freeze_distance_raw:int
    tick_size_raw:int
    accepted:bool
    server_quote_verified:bool
    position_readback_verified:bool
    def __post_init__(self):
        if (not self.modify_id or self.position_id<=0 or self.request_ms<0 or
            self.reply_ms<self.request_ms or self.proposed_stop_raw<=0 or
            self.current_broker_bid_raw<=0 or self.current_broker_ask_raw<self.current_broker_bid_raw or
            self.stops_distance_raw<0 or self.freeze_distance_raw<0 or self.tick_size_raw<1):
            raise ValueError('invalid observed broker stop modification evidence')
        for k in ('accepted','server_quote_verified','position_readback_verified'):
            if type(getattr(self,k)) is not bool:raise TypeError('broker evidence requires bool')

class BrokerAcknowledgedStops0264:
    def __init__(self, ledger:VerifiedMT5PositionLedger0264):
        self.ledger=ledger
        self.confirmed_stop_raw={}
        self.events={}
    def on_observed_stop_response(self,x:ObservedStopModify):
        self.ledger._verified()
        if x.modify_id in self.events:raise ValueError('duplicate broker stop modification receipt')
        pos=self.ledger.positions.get(x.position_id)
        if pos is None or pos.closed>=pos.opened:
            raise ValueError('stop update requires externally observed open position')
        if not x.server_quote_verified or not x.position_readback_verified:
            raise ValueError('not verified broker quote AND actual position SL readback')
        if x.proposed_stop_raw%x.tick_size_raw:
            raise ValueError('off-grid proposed stop price')
        # Buy protective SL closes on BID, sell protective SL closes on ASK.
        close_quote=x.current_broker_bid_raw if pos.side==1 else x.current_broker_ask_raw
        distance=(close_quote-x.proposed_stop_raw)*pos.side
        if x.accepted:
            if distance < max(x.stops_distance_raw,x.freeze_distance_raw):
                raise ValueError('accepted stop outside documented broker constraint; reconcile')
            if x.reported_position_stop_raw!=x.proposed_stop_raw:
                raise ValueError('OrderSend accepted but position SL readback mismatch')
            self.confirmed_stop_raw[x.position_id]=x.proposed_stop_raw
        elif x.reported_position_stop_raw is not None:
            # A rejected request cannot modify the last broker-confirmed stop.
            prior=self.confirmed_stop_raw.get(x.position_id)
            if prior is not None and prior!=x.reported_position_stop_raw:
                raise ValueError('rejected SL still changed in position history; reconcile')
        self.events[x.modify_id]=x
        return self.confirmed_stop_raw.get(x.position_id)
