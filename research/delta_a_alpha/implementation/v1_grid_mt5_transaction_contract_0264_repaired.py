"""GRID0264 repaired evidence-only MT5 transaction contract.

Order intent/check/send, confirmed broker DEAL_ADD, stop ACK and terminal
position state are separate. Original Dukascopy quotes never produce deals.
This module is used by the CURRENT V1 engine via GRID0265 broker evidence port.
"""
from __future__ import annotations
from decimal import Decimal
from v1_grid_mt5_transaction_contract_0263 import (
    MT5EventContractResearchOnly, BrokerOrder, BrokerDeal, money,
)

class RepairedMT5EventContract(MT5EventContractResearchOnly):
    """Reject terminal, duplicate and backwards broker-event transitions."""
    def __init__(self, *, account_mode='UNKNOWN', verified_symbol=False):
        super().__init__(account_mode=account_mode, verified_symbol=verified_symbol)
        self._last_global_event_ms = None
        self._cancelled_orders = set()
        self._closed_orders = set()
        self._stop_events = {}

    @staticmethod
    def _ms(value):
        if type(value) is not int or value < 0:
            raise ValueError('event milliseconds must be nonnegative exact integer')

    def _time(self, ms):
        self._ms(ms)
        if self._last_global_event_ms is not None and ms < self._last_global_event_ms:
            raise ValueError('global broker transaction chronology reversed')
        self._last_global_event_ms = ms

    def submit(self, q: BrokerOrder):
        self._ms(q.available_ms)
        self._ms(q.request_ms)
        self._ms(q.intended_expiry_ms)
        if type(q.side) is not int or type(q.requested_stop_raw) is not int:
            raise ValueError('exact integer signal direction and stop required')
        if q.order_id in self.orders:
            raise ValueError('duplicate order id')
        if self._last_global_event_ms is not None and q.request_ms < self._last_global_event_ms:
            raise ValueError('global broker request chronology reversed')
        result=super().submit(q)
        self._time(q.request_ms)
        return result

    def _active(self, order_id):
        if order_id in self._cancelled_orders or order_id in self._closed_orders:
            raise ValueError('broker order/position is terminal')
        return self.orders[order_id]

    def check(self, order_id, *, approved:bool, reason=''):
        self._active(order_id)
        return super().check(order_id, approved=approved, reason=reason)

    def send(self, order_id, *, accepted:bool, reason=''):
        self._active(order_id)
        return super().send(order_id, accepted=accepted, reason=reason)

    def cancel_confirmed(self, order_id: str, *, event_id: str, at_ms: int):
        """Only observed broker cancellation can terminate an unfilled order."""
        self._active(order_id)
        self._ms(at_ms)
        if self._last_global_event_ms is not None and at_ms < self._last_global_event_ms:
            raise ValueError('global broker transaction chronology reversed')
        if not event_id or at_ms < self.orders[order_id].proposed.request_ms:
            raise ValueError('invalid broker cancellation evidence')
        if self.orders[order_id].entry_lots:
            raise ValueError('partially filled order requires explicit remainder cancel semantics')
        if self.orders[order_id].send_accepted is not True:
            raise ValueError('broker cancellation must refer to sent order evidence')
        self._time(at_ms)
        self._cancelled_orders.add(order_id)

    def fill(self, d: BrokerDeal):
        p=self._active(d.order_id)
        self._ms(d.time_ms)
        if money(d.realized_cash) != 0:
            raise ValueError('entry deal cannot add realized profit cash')
        if d.time_ms < p.proposed.request_ms:
            raise ValueError('deal predates request')
        if self._last_global_event_ms is not None and d.time_ms < self._last_global_event_ms:
            raise ValueError('global broker transaction chronology reversed')
        super().fill(d)
        self._time(d.time_ms)

    def close(self, d:BrokerDeal):
        p=self._active(d.order_id)
        self._ms(d.time_ms)
        if p.entry_lots <= p.close_lots:
            raise ValueError('no open position for confirmed close')
        if self._last_global_event_ms is not None and d.time_ms < self._last_global_event_ms:
            raise ValueError('global broker transaction chronology reversed')
        super().close(d)
        self._time(d.time_ms)
        if p.entry_lots == p.close_lots:
            self._closed_orders.add(d.order_id)

    def modify_stop(self,order_id,*,modify_id,at_ms,proposed_stop_raw,
                    broker_accepted,freeze_clear):
        self._active(order_id)
        self._ms(at_ms)
        if self._last_global_event_ms is not None and at_ms < self._last_global_event_ms:
            raise ValueError('global broker transaction chronology reversed')
        if type(proposed_stop_raw) is not int:
            raise ValueError('stop must be scaled integer')
        result=super().modify_stop(order_id,modify_id=modify_id,at_ms=at_ms,
               proposed_stop_raw=proposed_stop_raw,broker_accepted=broker_accepted,
               freeze_clear=freeze_clear)
        self._time(at_ms)
        self._stop_events[modify_id]={'order_id':order_id,'at_ms':at_ms,
                'ack':broker_accepted,'freeze_clear':freeze_clear,'effective':result}
        return result

    def summary(self):
        x=super().summary()
        x.update({'engine':'GRID0264_BROKER_EVENT_EVIDENCE_REPAIRED',
                  'cancelled_unfilled_orders':len(self._cancelled_orders),
                  'fully_closed_positions':len(self._closed_orders),
                  'stop_change_evidence_events':len(self._stop_events),
                  'real_mt5_connected':False,'ea_porting_certified':False})
        return x
