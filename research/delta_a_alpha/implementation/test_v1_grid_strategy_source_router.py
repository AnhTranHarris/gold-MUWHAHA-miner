import unittest
from dataclasses import dataclass
from types import SimpleNamespace
from v1_grid_strategy_source_router import GridStrategySourceRouter
from v1_grid_funded_campaign import FundedGridCampaign

@dataclass(frozen=True)
class Event:
    side:int=1;source:str='S1_BASE';rung:int=1;crossing_level_usd:float=3099.0
class Base:
    def __init__(self):
        self.ready=True
        self.parent=SimpleNamespace(parent=SimpleNamespace(
                 cached_high=3100.0,cached_low=3090.0,parent_gap_usd=1.2))
        self.output={};self.calls=[]
    def on_tick(self,q,h1,geometry,*,last_completed_m5=None,broker_tradable=True):
        self.calls.append(q.time_ms_utc)
        return (Event(),) if q.time_ms_utc in self.output and broker_tradable else ()
    def stats(self):return {'mock':True}
class TestGridRouter(unittest.TestCase):
    def setUp(self):
        self.b=Base();self.r=GridStrategySourceRouter(multiscale=self.b)
        self.h=SimpleNamespace(start_ms=1,end_ms=1)
    def tick(self,t,ask,**kw):
        q=SimpleNamespace(time_ms_utc=t,ask_raw=ask,bid_raw=ask-100)
        return self.r.on_tick(q,self.h,'RESEARCH_ONLY',**kw)
    def test_preserve_old_base(self):
        self.b.output[2]=True
        self.tick(1,3099500)
        c=self.tick(2,3098700)
        self.assertEqual(len(c),1)
        self.assertEqual(c[0].source,'S1_BASE')
        self.assertEqual(self.r.counts['paid_collisions_rejected'],1)
        self.assertEqual(len(self.r.funded.proposals),0)
    def test_paid_only_after_real_cross_and_no_fake_ack(self):
        self.tick(1,3099500)
        c=self.tick(2,3098700)
        self.assertEqual(len(c),1)
        self.assertEqual(c[0].source,'OMEGAFX_ACKNOWLEDGED_FILL_ANCHOR')
        self.assertEqual(self.r.funded.counts['ack_fills'],0)
        self.assertEqual(self.r.funded.last_filled_price_raw[1],None)
    def test_duplicate_millisecond_no_second_request(self):
        self.tick(1,3099500)
        self.b.output[2]=True
        self.assertEqual(len(self.tick(2,3098900)),1)
        self.assertEqual(self.tick(2,3098800),())
    def test_confirmed_paid_close_credit(self):
        self.tick(1,3099500)
        p=self.tick(2,3098700)[0]
        self.r.funded.acknowledge_fill(proposal_id=p.paid_proposal_id,
                  ticket_id=7,time_ms=3,side=1,actual_price_raw=3098700,actual_lot=.01)
        self.r.funded.acknowledge_close(ticket_id=7,close_ms=5,realized_net_cash=4.)
        self.tick(6,3099500)
        new=self.tick(7,3098700)[0]
        self.assertEqual(new.paid_prior_close_id,7)
    def test_h1_owner_freezes_gap(self):
        self.tick(1,3099500)
        self.b.parent.parent.parent_gap_usd=3.0
        self.assertEqual(len(self.tick(2,3098000)),1)
        self.assertEqual(self.r.frozen_gap_raw,1200)
        self.assertEqual(self.r.funded.frozen_refs[2],1200)
    def test_future_h1_fail_closed(self):
        self.h=SimpleNamespace(start_ms=1,end_ms=200)
        with self.assertRaises(ValueError):self.tick(1,3099500)
    def test_disabled_source_not_new_proposal(self):
        self.tick(1,3099500)
        self.assertEqual(self.tick(2,3098700,broker_tradable=False),())
        self.assertEqual(self.r.counts['funded_anchor_selected'],0)
    def test_counter_source_no_margin_or_vertical(self):
        self.tick(1,3099500)
        self.tick(2,3098700)
        self.assertFalse(hasattr(self.r,'cash'))
        self.assertFalse(hasattr(self.r,'positions'))
if __name__=='__main__':unittest.main()
