"""GRID0265: tests for CURRENT V1 integrated external broker evidence port.

Quote-driven shadow research is intentionally separate from actual broker
DEAL_ADD and earned cumulative source-anchor credit.
"""
import unittest
from decimal import Decimal
from types import SimpleNamespace as NS
from v1_grid_broker_evidence_port_0265 import V1BrokerEvidencePort
from v1_grid_mt5_transaction_contract_0264_repaired import RepairedMT5EventContract
from v1_grid_mt5_transaction_contract_0263 import BrokerDeal, BrokerOrder
from v1_grid_source_broker_ack_bridge_0264 import PaidSourceBinding
from v1_grid_funded_campaign import FundedGridCampaign, SourceProposal
from v1_four_session_architecture import FourSessionV1

def setup_port(verified=True):
    source=NS(router=NS(funded=FundedGridCampaign()))
    source.router.funded.proposals[7]=SourceProposal(7,1000,1,1,4000000,3999800,4000000,None)
    contract=RepairedMT5EventContract(account_mode='HEDGING' if verified else 'UNKNOWN',
                                      verified_symbol=verified)
    port=V1BrokerEvidencePort(source,broker_contract=contract)
    port.submit_observed_order(BrokerOrder('g0:7','order7',1000,1100,1,
                          Decimal('.01'),3990000,300000))
    port.bind_paid_source(PaidSourceBinding(7,'order7',88,'g0:7'))
    return port,source

class V1BrokerEvidencePortTests(unittest.TestCase):
    def test_active_V1_uses_current_router_identity_not_stub(self):
        engine=FourSessionV1()
        self.assertIs(engine.broker_evidence.paid.router,engine.creator_genesis.router)
        self.assertFalse(engine.broker_evidence.contract.verified_symbol)
        self.assertEqual(engine.result()['broker_event_evidence']['confirmed_deals'],0)

    def test_no_broker_permission_defaults_fail_closed(self):
        port=V1BrokerEvidencePort(NS(router=NS(funded=FundedGridCampaign())))
        self.assertEqual(port.contract.account_mode,'UNKNOWN')
        self.assertFalse(port.contract.verified_symbol)
        self.assertEqual(port.summary()['source_credit_entries'],0)

    def test_require_actual_cumulative_source_router(self):
        with self.assertRaises(TypeError):V1BrokerEvidencePort(NS())

    def test_reject_unhardened_event_contract(self):
        with self.assertRaises(TypeError):V1BrokerEvidencePort(
            NS(router=NS(funded=FundedGridCampaign())),broker_contract=object())

    def test_OrderSend_does_not_generate_paid_credit(self):
        port,src=setup_port()
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        with self.assertRaises(ValueError):port.acknowledge_full_paid_parent_entry(88)
        self.assertFalse(src.router.funded.open_tickets)

    def test_full_actual_deals_populate_same_current_source_ledger(self):
        port,src=setup_port()
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        port.observe_entry_deal_add(BrokerDeal('order7','entry',1400,Decimal('.01'),
                         4000100,fee_cash=Decimal('-.10')))
        port.acknowledge_full_paid_parent_entry(88)
        self.assertIn(88,src.router.funded.open_tickets)
        port.observe_close_deal_add(BrokerDeal('order7','close',1800,Decimal('.01'),
                         4001500,Decimal('3.50'),Decimal('-.20')))
        net=port.acknowledge_complete_paid_parent_close(88)
        self.assertEqual(net,Decimal('3.20'))
        self.assertEqual(port.summary()['source_credit_closes'],1)
        self.assertAlmostEqual(src.router.funded.last_paid_close[1].realized_net_cash,3.2)

    def test_partial_entry_has_no_full_credit(self):
        port,src=setup_port()
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        port.observe_entry_deal_add(BrokerDeal('order7','half',1400,Decimal('.005'),4000100))
        with self.assertRaises(ValueError):port.acknowledge_full_paid_parent_entry(88)
        self.assertFalse(src.router.funded.open_tickets)

    def test_unknown_broker_prevents_real_broker_deal_claim(self):
        port,_=setup_port(False)
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        with self.assertRaises(ValueError):
            port.observe_entry_deal_add(BrokerDeal('order7','entry',1400,Decimal('.01'),4000100))

    def test_stop_modification_needs_actual_open_deal(self):
        port,_=setup_port()
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        with self.assertRaises(ValueError):
            port.observe_stop_modification('order7',modify_id='m1',at_ms=1450,
                proposed_stop_raw=3990000,broker_accepted=True,freeze_clear=True)

    def test_duplicate_source_credit_blocked(self):
        port,_=setup_port()
        port.observe_order_check('order7',approved=True)
        port.observe_order_send('order7',accepted=True)
        port.observe_entry_deal_add(BrokerDeal('order7','entry',1400,Decimal('.01'),4000100))
        port.acknowledge_full_paid_parent_entry(88)
        with self.assertRaises(ValueError):port.acknowledge_full_paid_parent_entry(88)

    def test_source_shadow_is_separate_from_broker_cash(self):
        port,_=setup_port()
        self.assertEqual(port.summary()['confirmed_deals'],0)
        self.assertFalse(port.summary()['trading_enabled'])
        self.assertFalse(port.summary()['shadow_quote_fills_are_broker_fills'])

if __name__=='__main__':unittest.main()
