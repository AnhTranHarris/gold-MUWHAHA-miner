"""C2D3-B direct L7 parent denial and delayed 084 paid-child ablations.

Engine-source diagnostic regression; not full owner V1 source/economic parity.
Original 049/119/084 source adapters and original shared L7 kernel unmodified.
"""
import unittest
from v1_funded_core_033c import Limits
from funded_084_l7_bridge_033c2d2 import Funded084L7Bridge
from test_funded_084_l7_bridge_033c2d2 import T, q, s, parent
from c2d3b_feb_funded_replay_033 import C2D3BL7FundingAblation, IndependentPhysicalOracle


class FundingL7Ablations(unittest.TestCase):
    def make(self, *, deny=False, delay=0):
        w = Funded084L7Bridge()
        lim = Limits(max_open=40,max_layer_open=40,max_per_source_open=40,
                     max_same_direction=40,max_per_cell_side=40)
        e = C2D3BL7FundingAblation(lim,[w],broker_contract_verified=True,
                                   deny_049_parents=deny,child_after_parent_ms=delay)
        o = IndependentPhysicalOracle(lim)
        return e,w,o

    @staticmethod
    def step(e, o, ms, bid=100000, proposals=()):
        quote=q(ms,bid); idx=len(e.events)
        e.process_quote(quote,s(ms),proposals=proposals)
        o.ingest(quote,e.events[idx:],e)

    def test_real_l7_deny_049_parent_removes_descendants_and_credit(self):
        e,w,o=self.make(deny=True)
        self.step(e,o,T,proposals=(parent('C2D3B:DENY'),))
        for i in range(1,8):self.step(e,o,T+i*1000,100000+i*3500)
        self.assertGreater(e.reject_counts['AB_DENY_FUNDED_049_PARENT'],0)
        self.assertEqual(w.admitted_parent_windows,0)
        self.assertEqual(len(w.funded_entry_events),0)
        self.assertEqual(len(w.funded_close_events),0)
        self.assertEqual(len(e.positions),0)
        self.assertEqual(o.mismatch_count,0)

    def test_l7_delays_paid_child_until_new_quote_and_new_price(self):
        e,w,o=self.make(delay=5000)
        self.step(e,o,T,proposals=(parent('C2D3B:PAID'),))
        self.assertEqual(w.admitted_parent_windows,1)
        self.step(e,o,T+1000,bid=100000)
        self.step(e,o,T+4000,bid=100500)
        self.assertGreater(e.reject_counts['AB_DELAY_FUNDED_084_CHILD'],0)
        self.assertEqual(len(w.funded_entry_events),0)
        self.assertEqual(w.children_funded[next(iter(w.windows))],0)
        self.step(e,o,T+5000,bid=100800)
        self.assertEqual(len(w.funded_entry_events),1)
        child=e.positions[w.actual_live_child[next(iter(w.windows))]]
        self.assertEqual(child.entry_raw,100900)
        self.assertEqual(o.mismatch_count,0)

    def test_delayed_child_actual_exit_not_backfilled(self):
        e,w,o=self.make(delay=3000)
        self.step(e,o,T,proposals=(parent('C2D3B:PAID'),))
        self.step(e,o,T+1000,bid=100000)
        self.step(e,o,T+2000,bid=100000)
        self.assertEqual(w.children_funded[next(iter(w.windows))],0)
        self.step(e,o,T+3000,bid=100000)
        self.assertEqual(len(w.funded_entry_events),1)
        self.step(e,o,T+4000,bid=103000)
        self.assertEqual(len(w.funded_close_events),1)
        self.assertGreater(w.funded_close_events[0][5],0)
        self.assertEqual(o.mismatch_count,0)
        self.assertEqual(o.close_count,1)

    def test_disabled_ab_is_identical_to_original_funding_kernel(self):
        from v1_funded_core_033c import FundedEngine
        a,wa,oa=self.make()
        wb=Funded084L7Bridge()
        b=FundedEngine(a.limits,[wb],broker_contract_verified=True)
        for i in range(9):
            ms=T+i*1000;price=100000 if i<2 else 100000+1000*i
            prop=(parent('C2D3B:BASE'),) if i==0 else ()
            self.step(a,oa,ms,bid=price,proposals=prop)
            b.process_quote(q(ms,price),s(ms),proposals=prop)
        self.assertEqual(a.events,b.events)
        self.assertEqual(a.score(),b.score())
        self.assertEqual(oa.mismatch_count,0)


if __name__=='__main__':unittest.main()
