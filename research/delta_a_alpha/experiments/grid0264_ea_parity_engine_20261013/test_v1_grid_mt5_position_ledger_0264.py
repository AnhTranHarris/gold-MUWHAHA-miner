import unittest
from decimal import Decimal as D
from types import SimpleNamespace as NS
from v1_grid_mt5_position_ledger_0264 import VerifiedMT5PositionLedger0264 as Ledger,OrderRequest,ObservedDeal
from v1_grid_paid_source_position_bridge_0264 import PaidSourcePositionBridge0264
from v1_grid_funded_campaign import FundedGridCampaign,SourceProposal

def req(order='entry',t=1200,side=1,lots='0.01',kind='IN',position_id=None):
    return OrderRequest(order,t,side,D(lots),'g0:7' if kind=='IN' else 'CLOSE:88',kind,position_id)
def deal(id='entrydeal',order='entry',t=1400,kind='IN',side=1,lots='0.01',price=4000100,profit='0',fee='-0.10',reason='EXPERT'):
    return ObservedDeal(id,order,88,t,kind,side,D(lots),price,D(profit),D(fee),reason=reason,history_verified=True)
class PositionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.l=Ledger(account_mode='HEDGING',symbol_verified=True,account_cash_verified=True)
        self.l.add_request(req());self.l.acknowledge_check('entry',True);self.l.acknowledge_send('entry',True)
    def filled(self):self.l.stage_history_deal(deal())
    def closed(self):
        self.filled();self.l.add_request(req('exit',1500,-1,kind='OUT',position_id=88));self.l.acknowledge_check('exit',True);self.l.acknowledge_send('exit',True)
        self.l.stage_history_deal(deal('exitdeal','exit',1800,'OUT',-1,price=4001300,profit='2.50',fee='-0.20'))
    def test_exact_cash_and_separate_close_order(self):
        self.closed();p=self.l.audited_paid_position(88)
        self.assertEqual(p.net_cash,D('2.20'));self.assertEqual(self.l.cash,D('2.20'))
        self.assertEqual(p.entry_order_ids,{'entry'});self.assertEqual(p.exit_order_ids,{'exit'})
    def test_duplicate_is_idempotent_and_conflicting_duplicate_errors(self):
        x=deal();self.l.stage_history_deal(x);self.l.stage_history_deal(x)
        self.assertEqual(len(self.l.applied),1)
        with self.assertRaises(ValueError):self.l.stage_history_deal(deal(profit='5'))
    def test_async_deal_arrives_before_send(self):
        l=Ledger(account_mode='HEDGING',symbol_verified=True,account_cash_verified=True)
        l.add_request(req());self.assertEqual(l.stage_history_deal(deal()),());self.assertEqual(l.cash,0)
        l.acknowledge_check('entry',True);self.assertEqual(l.cash,0)
        self.assertEqual(l.acknowledge_send('entry',True),('entrydeal',));self.assertEqual(l.cash,D('-.10'))
    def test_missing_broker_permission_denied(self):
        l=Ledger(account_mode='UNKNOWN',symbol_verified=False)
        with self.assertRaises(ValueError):l.stage_history_deal(deal())
    def test_unverified_deal_denied(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):self.l.stage_history_deal(replace(deal(),history_verified=False))
    def test_unconfirmed_order_never_enters_cash(self):
        l=Ledger(account_mode='HEDGING',symbol_verified=True);l.add_request(req())
        l.stage_history_deal(deal());self.assertFalse(l.positions)
    def test_server_generated_stop_on_distinct_order(self):
        self.filled()
        self.l.stage_history_deal(deal('serverStop','stopOrder77',2000,'OUT',-1,price=3999000,profit='-1.10',fee='-.20',reason='SL'))
        self.assertEqual(self.l.audited_paid_position(88).net_cash,D('-1.40'))
    def test_close_before_entry_is_queued_and_not_guessed(self):
        l=Ledger(account_mode='HEDGING',symbol_verified=True,account_cash_verified=True)
        l.stage_history_deal(deal('serverStop','stopOrder',1800,'OUT',-1,reason='SL'))
        self.assertEqual(l.cash,0)
        l.add_request(req());l.acknowledge_check('entry',True);l.acknowledge_send('entry',True)
        l.stage_history_deal(deal());self.assertEqual(len(l.staged),0)
    def test_partial_broker_fill_not_full_position(self):
        self.l.stage_history_deal(deal(lots='0.005'))
        with self.assertRaises(ValueError):self.l.audited_paid_position(88)
    def test_out_of_sequence_late_broker_history_needs_reconciliation(self):
        self.filled()
        self.l.stage_history_deal(deal('serverStop','stopOrder',1900,'OUT',-1,reason='SL'))
        with self.assertRaises(ValueError):self.l.stage_history_deal(deal('staleFee','feeOrder',1800,'OUT',-1,reason='SERVER'))
    def test_broker_contract_cash_confirmed_requires_explicit_flag(self):
        self.closed();self.l.account_cash_verified=False
        with self.assertRaises(ValueError):self.l.audited_paid_position(88)
    def test_no_overclose(self):
        self.filled();self.l.stage_history_deal(deal('serverStop','s1',1700,'OUT',-1,lots='0.01',reason='SL'))
        with self.assertRaises(ValueError):self.l.stage_history_deal(deal('secondExit','s2',1900,'OUT',-1,lots='0.01',reason='SL'))
    def test_duplicate_order_id_rejected(self):
        with self.assertRaises(ValueError):self.l.add_request(req())
    def test_side_mismatch_rejected(self):
        self.filled()
        with self.assertRaises(ValueError):self.l.stage_history_deal(deal('serverStop','s',1700,'OUT',1,reason='SL'))
    def test_no_wrong_position_on_close(self):
        self.filled();self.l.add_request(req('exit',1500,-1,kind='OUT',position_id=99));self.l.acknowledge_check('exit',True);self.l.acknowledge_send('exit',True)
        with self.assertRaises(ValueError):self.l.stage_history_deal(deal('bad','exit',1700,'OUT',-1))
    def test_source_bridge_earned_only_from_history(self):
        r=NS(funded=FundedGridCampaign());r.funded.proposals[7]=SourceProposal(7,1000,1,1,4000000,3999800,4000000,None)
        b=PaidSourcePositionBridge0264(router=r,position_ledger=self.l);b.bind_original_proposal(7,88,source_id='g0:7')
        with self.assertRaises(KeyError):b.acknowledge_entry(88)
        self.filled();b.acknowledge_entry(88)
        self.assertEqual(r.funded.last_filled_price_raw[1],4000100)
        self.l.stage_history_deal(deal('serverStop','s1',1800,'OUT',-1,price=4001300,profit='2.50',fee='-.20',reason='TP'))
        net=b.acknowledge_close(88)
        self.assertEqual(net,D('2.20'))
        self.assertEqual(r.funded.last_paid_close[1].realized_net_cash,2.2)
        with self.assertRaises(ValueError):b.acknowledge_close(88)
    def test_source_bridge_rejects_wrong_strategy_order(self):
        r=NS(funded=FundedGridCampaign());r.funded.proposals[7]=SourceProposal(7,1000,1,1,4000000,3999800,4000000,None)
        b=PaidSourcePositionBridge0264(router=r,position_ledger=self.l)
        b.bind_original_proposal(7,88,source_id='source-of-other-strategy')
        self.filled()
        with self.assertRaises(ValueError):b.acknowledge_entry(88)
        self.assertFalse(r.funded.open_tickets)
    def test_source_bridge_rejects_future_bound_proposal(self):
        r=NS(funded=FundedGridCampaign());r.funded.proposals[7]=SourceProposal(7,1350,1,1,4000000,3999800,4000000,None)
        b=PaidSourcePositionBridge0264(router=r,position_ledger=self.l)
        b.bind_original_proposal(7,88,source_id='g0:7')
        self.filled()
        with self.assertRaises(ValueError):b.acknowledge_entry(88)
    def test_source_bridge_fractional_vwap_no_fake_rounding(self):
        r=NS(funded=FundedGridCampaign());r.funded.proposals[7]=SourceProposal(7,1000,1,1,4000000,3999800,4000000,None)
        b=PaidSourcePositionBridge0264(router=r,position_ledger=self.l);b.bind_original_proposal(7,88,source_id='g0:7')
        self.l.stage_history_deal(deal('partial1',lots='0.005',price=4000100))
        self.l.stage_history_deal(deal('partial2',t=1500,lots='0.005',price=4000101))
        with self.assertRaises(ValueError):b.acknowledge_entry(88)
    def test_async_partial_then_full(self):
        self.l.stage_history_deal(deal('p1',lots='0.005'))
        self.l.stage_history_deal(deal('p2',t=1450,lots='0.005'))
        self.assertEqual(self.l.positions[88].opened,D('0.01'))
    def test_unverified_account_remains_shadow_only(self):
        self.filled();self.l.account_cash_verified=False
        self.assertFalse(self.l.summary()['broker_account_cash_reconciled'])
    def test_full_history_replay_resolves_async_late_event(self):
        self.filled()
        self.l.stage_history_deal(deal('serverStop','stopOrder',1900,'OUT',-1,reason='SL',profit='3'))
        late=deal('late','late-order',1800,'OUT',-1,lots='0.002',reason='SERVER',profit='1')
        with self.assertRaises(ValueError):self.l.stage_history_deal(late)
        # Full real broker history would have to use volume-consistent partial
        # exits. Here a corrected full broker snapshot is supplied explicitly.
        entry=deal()
        out1=deal('outpart','s1',1800,'OUT',-1,lots='0.002',reason='SL',profit='1',fee='0')
        out2=deal('outrest','s2',1900,'OUT',-1,lots='0.008',reason='SL',profit='2',fee='-.20')
        net=entry.net+out1.net+out2.net
        result=self.l.reconcile_broker_history(observed_deals=[out2,entry,out1],
               observed_cash_delta=net,broker_snapshot_verified=True)
        self.assertEqual(result['deals'],3)
        self.assertEqual(self.l.cash,net)
        self.assertTrue(self.l.audited_paid_position(88).complete)
    def test_broker_history_net_mismatch_is_atomic(self):
        self.filled();prior=self.l.cash
        with self.assertRaises(ValueError):self.l.reconcile_broker_history(
             observed_deals=[deal()],observed_cash_delta='1000',broker_snapshot_verified=True)
        self.assertEqual(self.l.cash,prior)
    def test_broker_history_replay_requires_snapshot_evidence(self):
        self.filled()
        with self.assertRaises(ValueError):self.l.reconcile_broker_history(
             observed_deals=[deal()],observed_cash_delta='-.10',broker_snapshot_verified=False)
    def test_input_validation(self):
        with self.assertRaises(ValueError):req(lots='0')
        with self.assertRaises(ValueError):deal(lots='0')
        with self.assertRaises(ValueError):deal(profit='nan')
if __name__=='__main__':unittest.main()
