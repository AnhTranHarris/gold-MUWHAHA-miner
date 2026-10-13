"""GRID0265 actual Python V1 broker-evidence interface to the CURRENT cumulative G0.

Dukascopy ticks never create broker DEAL_ADD. External broker evidence is
required, and the default UNKNOWN broker contract rejects paid source credit.
This is importable by active FourSessionV1, not a disconnected experiment.
"""
from __future__ import annotations
from v1_grid_mt5_transaction_contract_0264_repaired import RepairedMT5EventContract
from v1_grid_source_broker_ack_bridge_0264 import GridSourceBrokerAckBridge0264, PaidSourceBinding

class V1BrokerEvidencePort:
    def __init__(self, cumulative_adapter, *, broker_contract=None):
        router=getattr(cumulative_adapter, 'router', None)
        if router is None or not hasattr(router, 'funded'):
            raise TypeError('requires current cumulative source adapter, not archived source stub')
        self.contract=broker_contract if broker_contract is not None else RepairedMT5EventContract()
        if not isinstance(self.contract, RepairedMT5EventContract):
            raise TypeError('requires hardened GRID0264 transaction contract')
        self.paid=GridSourceBrokerAckBridge0264(router=router,contract=self.contract)

    def submit_observed_order(self, broker_order):
        """Register observed order facts, never create a source order from quote data."""
        return self.contract.submit(broker_order)

    def bind_paid_source(self, binding:PaidSourceBinding):
        return self.paid.bind(binding)

    def observe_order_check(self, order_id, *, approved:bool, reason=''):
        return self.contract.check(order_id,approved=approved,reason=reason)

    def observe_order_send(self, order_id, *, accepted:bool, reason=''):
        return self.contract.send(order_id,accepted=accepted,reason=reason)

    def observe_entry_deal_add(self, broker_deal):
        return self.contract.fill(broker_deal)

    def observe_close_deal_add(self, broker_deal):
        return self.contract.close(broker_deal)

    def observe_stop_modification(self, order_id, *, modify_id, at_ms,
                                  proposed_stop_raw, broker_accepted, freeze_clear):
        return self.contract.modify_stop(order_id,modify_id=modify_id,at_ms=at_ms,
                        proposed_stop_raw=proposed_stop_raw,
                        broker_accepted=broker_accepted,freeze_clear=freeze_clear)

    def acknowledge_full_paid_parent_entry(self, position_ticket_id:int):
        """Actual fully filled 0.01 parent enters cumulative G0 only with DEAL_ADD."""
        return self.paid.ack_full_entry(position_ticket_id)

    def acknowledge_complete_paid_parent_close(self, position_ticket_id:int):
        """Actual fully closed paid parent can earn G0 renewal credit."""
        return self.paid.ack_complete_close(position_ticket_id)

    def summary(self):
        x=self.contract.summary()
        x.update({'source_credit_entries':len(self.paid._entry_ack),
                  'source_credit_closes':len(self.paid._close_ack),
                  'broker_verification_required':True,'trading_enabled':False,
                  'source_router':'CURRENT_CUMULATIVE_G0',
                  'shadow_quote_fills_are_broker_fills':False})
        return x
