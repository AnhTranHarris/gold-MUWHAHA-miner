"""GRID0245 grid-only regression suite. Run: python -m unittest test_v1_grid_funded_campaign.py"""
import unittest
from v1_grid_funded_campaign import FundedGridCampaign

class GridPaidCampaignTest(unittest.TestCase):
    def setUp(self):
        self.g=FundedGridCampaign()
    def tick(self,t,ask,**kwargs):
        kw=dict(time_ms=t,bid_raw=ask-100,ask_raw=ask,
                completed_h1_window_id=2,completed_h1_high_raw=3100000,
                completed_h1_low_raw=3090000,gap_raw=1000)
        kw.update(kwargs)
        return self.g.observe(**kw)
    def test_proposal_not_fill(self):
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        self.assertEqual((p.side,p.rung,p.threshold_raw),(1,1,3099000))
        self.assertIsNone(self.g.last_filled_price_raw[1])
        self.assertEqual(self.g.depth[1],0)
        self.assertEqual(self.tick(3,3098700),())
    def test_fill_price_is_anchor(self):
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        self.g.acknowledge_fill(proposal_id=p.id,ticket_id=7,time_ms=3,side=1,
                                actual_price_raw=3099050,actual_lot=.01)
        self.tick(4,3098200)
        self.tick(5,3099000)
        q=self.tick(6,3097900)[0]
        self.assertEqual((q.rung,q.threshold_raw),(2,3098050))
    def test_expired_proposal_never_fills(self):
        self.tick(1,3099500)
        p=self.tick(2,3098990)[0]
        self.tick(2004,3099500)
        with self.assertRaises(ValueError):
            self.g.acknowledge_fill(proposal_id=p.id,ticket_id=1,time_ms=2004,
                                    side=1,actual_price_raw=3098990,actual_lot=.01)
        self.assertIsNone(self.g.last_filled_price_raw[1])
    def test_no_shadow_paid_credit(self):
        with self.assertRaises(ValueError):
            self.g.acknowledge_close(ticket_id=99,close_ms=200,realized_net_cash=10)
    def test_paid_win_only_after_close(self):
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        self.g.acknowledge_fill(proposal_id=p.id,ticket_id=7,time_ms=3,side=1,
                                actual_price_raw=3098980,actual_lot=.01)
        self.g.acknowledge_close(ticket_id=7,close_ms=10,realized_net_cash=2)
        self.tick(11,3099500)
        self.assertEqual(self.tick(12,3098900)[0].prior_paid_close_id,7)
    def test_loser_is_not_paid_success(self):
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        self.g.acknowledge_fill(proposal_id=p.id,ticket_id=7,time_ms=3,side=1,
                                actual_price_raw=3098980,actual_lot=.01)
        self.g.acknowledge_close(ticket_id=7,close_ms=10,realized_net_cash=-2)
        self.tick(11,3099500)
        self.assertIsNone(self.tick(12,3098900)[0].prior_paid_close_id)
    def test_changed_grid_without_bar_is_rejected(self):
        self.tick(1,3099500)
        with self.assertRaises(ValueError):self.tick(2,3098990,gap_raw=1300)
    def test_no_martingale(self):
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        with self.assertRaises(ValueError):
            self.g.acknowledge_fill(proposal_id=p.id,ticket_id=7,time_ms=3,side=1,
                                    actual_price_raw=3098980,actual_lot=.02)
    def test_out_of_order_tick_and_quote_gap(self):
        self.tick(2,3099500)
        with self.assertRaises(ValueError):self.tick(1,3098990)
        self.assertEqual(self.tick(70003,3098990),())
        self.assertEqual(self.g.counts['stale'],1)
    def test_parent_credit_staleness(self):
        self.g=FundedGridCampaign(paid_credit_max_age_ms=5)
        self.tick(1,3099500)
        p=self.tick(2,3098980)[0]
        self.g.acknowledge_fill(proposal_id=p.id,ticket_id=7,time_ms=3,side=1,
                                actual_price_raw=3098980,actual_lot=.01)
        self.g.acknowledge_close(ticket_id=7,close_ms=10,realized_net_cash=2)
        self.tick(10000,3099500)
        self.assertIsNone(self.tick(10001,3098900)[0].prior_paid_close_id)

if __name__=='__main__':unittest.main()
