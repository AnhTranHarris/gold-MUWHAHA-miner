import inspect
import unittest
from dataclasses import replace
from r150_native_intent_first_passage import (
    Action, FrozenCausalState, Intent, IntentState, Proposal, Quote,
    first_decision_index, propose_unsubmitted, replay_action_time, frozen_receipt,
)

T0 = 1_000_000

def intent(side=1, state=IntentState.NEVER_SUBMITTED):
    return Intent('dukascopy', 101, 'orig-101-new-unsent-001', T0, side, state, T0-1)

def state(**kw):
    d=dict(published_before_ms=T0+15001, micro_direction=1., htf_direction=1.,
           session_direction=1., grid_distance_ticks=10, quote_staleness_ms=0,
           spread_ticks=20, parent_veto=False, parent_score=.4)
    d.update(kw)
    return FrozenCausalState(**d)

def quotes():
    return [Quote(T0+14999, 2000000,2000020), Quote(T0+15002,2000000,2000020),
            Quote(T0+15004,1999990,2000010), Quote(T0+15006,2001100,2001120)]

class R150Tests(unittest.TestCase):
    def test_first_genuine_quote_boundary(self):
        self.assertEqual(first_decision_index(quotes(),T0),1)
        self.assertIsNone(first_decision_index([Quote(T0+14999,1,2),Quote(T0+16000,1,2)],T0))
    def test_exact_same_timestamp_causality(self):
        p=propose_unsubmitted(intent(),quotes(),state(published_before_ms=T0+15002))
        self.assertFalse(p.eligible)
    def test_earlier_causal_state_only(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        self.assertTrue(p.eligible);self.assertEqual(p.action,Action.PLACE_UNSENT_LIMIT)
    def test_filled_and_submitted_immutable(self):
        for s in (IntentState.FILLED,IntentState.SUBMITTED,IntentState.CANCELLED):
            p=propose_unsubmitted(intent(state=s),quotes(),state())
            self.assertEqual(p.action,Action.KEEP_PARENT)
            self.assertFalse(p.eligible)
    def test_parent_veto_not_rescued_by_new_policy(self):
        p=propose_unsubmitted(intent(),quotes(),state(parent_veto=True))
        self.assertEqual(p.action,Action.CANCEL_NEVER_SENT)
    def test_spread_staleness_guard(self):
        self.assertEqual(propose_unsubmitted(intent(),quotes(),state(spread_ticks=999)).action,Action.WAIT_RECONFIRM)
        self.assertEqual(propose_unsubmitted(intent(),quotes(),state(quote_staleness_ms=3000)).action,Action.WAIT_RECONFIRM)
    def test_micro_htf_conflict(self):
        self.assertEqual(propose_unsubmitted(intent(),quotes(),state(micro_direction=-1,htf_direction=-1,session_direction=-1)).action,Action.WAIT_RECONFIRM)
    def test_buy_favorable_first_and_fees(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        r=replay_action_time(intent(),p,quotes(),latency_ms=0,target_ticks=1000,stop_ticks=800)
        self.assertEqual(r.exit_reason,'FAVORABLE_FIRST');self.assertEqual(r.fill_ms,T0+15004)
        self.assertAlmostEqual(r.net_usd,.89,places=2)
        self.assertEqual(r.first_favorable_ms,T0+15006)
    def test_sell_favorable_ask_exit(self):
        q=[Quote(T0+15001,2000000,2000020),Quote(T0+15003,2000030,2000050),Quote(T0+15005,1998700,1998720)]
        p=Proposal(intent(-1).intent_id,Action.PLACE_UNSENT_LIMIT,T0+15001,'fixture',True,False,2000030)
        r=replay_action_time(intent(-1),p,q,latency_ms=0,target_ticks=1000)
        self.assertEqual(r.exit_reason,'FAVORABLE_FIRST')
        self.assertEqual(r.fill_ms,T0+15003)
    def test_stop_bid_ask_asymmetry(self):
        q=[Quote(T0+15001,2000000,2000020),Quote(T0+15003,1999990,2000010),Quote(T0+15005,1998000,1998020)]
        p=Proposal(intent().intent_id,Action.PLACE_UNSENT_LIMIT,T0+15001,'fixture',True,False,2000010)
        r=replay_action_time(intent(),p,q,latency_ms=0,stop_ticks=800)
        self.assertEqual(r.exit_reason,'ADVERSE_FIRST');self.assertLess(r.net_usd,0)
    def test_latency_changes_fill_not_retroactive(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        r=replay_action_time(intent(),p,quotes(),latency_ms=1000)
        self.assertIsNone(r.fill_ms)
    def test_no_lookahead_on_decision(self):
        original=quotes()
        p=propose_unsubmitted(intent(),original,state())
        changed=original[:2]+[Quote(T0+15004,1500000,1500020),Quote(T0+15006,1000000,1000020)]
        self.assertEqual(propose_unsubmitted(intent(),changed,state()),p)
    def test_new_action_horizon_not_original_label(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        r=replay_action_time(intent(),p,quotes(),latency_ms=0,horizon_ms=1)
        self.assertEqual(r.exit_reason,'UNFILLED_BY_ACTION_HORIZON')
    def test_no_quote_after_fill_unresolved(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        r=replay_action_time(intent(),p,quotes()[:3],latency_ms=0)
        self.assertEqual(r.exit_reason,'OPEN_UNRESOLVED');self.assertIsNone(r.net_usd)
    def test_no_truth_teacher_in_decision_api(self):
        sig=set(inspect.signature(propose_unsubmitted).parameters)
        self.assertFalse(sig & {'truth','teacher','future_outcome','label','original_class'})
    def test_receipt_deterministic(self):
        p=propose_unsubmitted(intent(),quotes(),state())
        r=replay_action_time(intent(),p,quotes(),latency_ms=0)
        self.assertEqual(frozen_receipt(intent(),p,r),frozen_receipt(intent(),p,r))
    def test_no_decision_quote_fill_or_same_timestamp(self):
        q=[Quote(T0+15002,1999990,2000010),Quote(T0+15002,1999980,2000000)]
        p=Proposal(intent().intent_id,Action.PLACE_UNSENT_LIMIT,T0+15002,'fixture',True,False,2000010)
        r=replay_action_time(intent(),p,q,latency_ms=0)
        self.assertIsNone(r.fill_ms)
    def test_limit_price_never_exceeded_by_slippage(self):
        q=[Quote(T0+15002,2000000,2000020),Quote(T0+15004,1999990,2000010),Quote(T0+15006,2001100,2001120)]
        p=Proposal(intent().intent_id,Action.PLACE_UNSENT_LIMIT,T0+15002,'fixture',True,False,2000010)
        r=replay_action_time(intent(),p,q,latency_ms=0,slippage_ticks=30)
        self.assertEqual(r.fill_ticks,2000010)
    def test_quote_order_and_broker_validation(self):
        with self.assertRaises(ValueError):
            first_decision_index(list(reversed(quotes())),T0)
        with self.assertRaises(ValueError):
            Quote(T0,200,199)

if __name__=='__main__': unittest.main(verbosity=2)
