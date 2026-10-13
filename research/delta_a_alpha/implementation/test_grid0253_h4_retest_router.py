"""Grid-only G0 prioritization of completed-H4 research invites."""
import unittest
from types import SimpleNamespace
from v1_grid_strategy_source_router import GridStrategySourceRouter
from v1_grid_h4_retest_0253 import FinishedH4Rung,H4_MS,M1_MS

class ExistingBase:
    def __init__(self):
        self.ready=True
        self.output=set()
        self.parent=SimpleNamespace(parent=SimpleNamespace(
            cached_high=3100.,cached_low=3090.,parent_gap_usd=1.2))
    def on_tick(self,q,h1,geometry,*,last_completed_m5=None,broker_tradable=True):
        if q.time_ms_utc in self.output and broker_tradable:
            return (SimpleNamespace(side=1,source='PRESERVED_S1',
                rung=1,crossing_level_usd=3099.),)
        return ()
    def stats(self):return {}

class TestH4GridRouter(unittest.TestCase):
    def make(self):
        base=ExistingBase()
        router=GridStrategySourceRouter(multiscale=base)
        t=8*H4_MS+M1_MS
        ref=FinishedH4Rung(8*H4_MS,3100000,3090000,4800,1.15)
        invite=None
        for offset,(prev,close) in enumerate(((3099000,3101000),
                (3101000,3098800),(3098800,3101200))):
            invite=router.on_completed_m1(end_ms=t+offset*M1_MS,
                 prev_close_raw=prev,close_raw=close,h4=ref)
        self.assertIsNotNone(invite)
        return base,router,invite
    @staticmethod
    def observed(router,ms,tradable=True):
        q=SimpleNamespace(time_ms_utc=ms,bid_raw=3100300,ask_raw=3100400)
        h=SimpleNamespace(start_ms=1,end_ms=1)
        return router.on_tick(q,h,'G0_RESEARCH_ONLY',
             broker_tradable=tradable,completed_grid_signs=(None,)*4)
    def test_delayed_observed_bidask_only(self):
        base,router,invite=self.make()
        now=invite.signal_known_at_ms+100
        out=self.observed(router,now)
        self.assertEqual([(v.source,v.side,v.available_ms) for v in out],
            [('GRID0253_COMPLETED_H4_BREAK_PULLBACK_RECROSS',1,now)])
        self.assertIsNone(out[0].paid_prior_close_id)
    def test_existing_multiscale_wins_source_timestamp(self):
        base,router,invite=self.make()
        now=invite.signal_known_at_ms+100
        base.output.add(now)
        first=self.observed(router,now)
        self.assertIn('PRESERVED_S1',[v.source for v in first])
        self.assertNotIn('GRID0253_COMPLETED_H4_BREAK_PULLBACK_RECROSS',
            [v.source for v in first])
        next_quote=self.observed(router,now+2)
        self.assertIn('GRID0253_COMPLETED_H4_BREAK_PULLBACK_RECROSS',
            [v.source for v in next_quote])
    def test_closed_broker_or_stale_quote_abstains(self):
        base,router,invite=self.make()
        self.assertEqual(self.observed(router,invite.signal_known_at_ms+800,False),())
        self.assertEqual(self.observed(router,invite.signal_known_at_ms+1500),())
        self.assertEqual(router.counts['h4_retest_stale_expired'],1)
if __name__=='__main__':unittest.main()
