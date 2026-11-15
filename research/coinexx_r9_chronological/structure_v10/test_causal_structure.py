"""No external datasets needed. Synthetic observations verify causality only."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_structure import CausalMarketStructure


def tick(ms,mid=10000,spread=4):
    return SimpleNamespace(time_msc=ms,time_s=ms//1000,
                           bid_u=mid-spread//2,ask_u=mid+spread//2,
                           spread_points=spread,ordinal=ms)


def step(engine,second,price):
    engine.on_quote(tick(second*1000,price))
    engine.on_quote(tick(second*1000+400,price))


def seeded():
    eng=CausalMarketStructure()
    # 5s high at 10..14s; two FULL following 5s bars must finish before zone.
    levels=[10000,10012,10080,10015,10005,10002]
    for second in range(25):
        step(eng,second,levels[second//5])
    return eng


class StructureCausalityTests(unittest.TestCase):
    def test_pivot_cannot_appear_before_two_right_bars_close(self):
        eng=seeded()
        self.assertFalse(any(z.kind=="RESISTANCE" for z in eng.zones))
        step(eng,25,10002)
        r=[z for z in eng.zones if z.kind=="RESISTANCE"]
        self.assertTrue(r)
        self.assertAlmostEqual(r[0].center,10080)
        self.assertGreaterEqual(r[0].confirmed_ms,25000)

    def test_executable_buy_break_and_two_second_acceptance(self):
        eng=seeded()
        for s in range(25,30):step(eng,s,10002)
        step(eng,30,10120)
        a=eng.snapshot(tick(30400,10120))
        self.assertEqual(a.pattern,"BREAKOUT_PROBE")
        self.assertEqual(a.breakout_side,1)
        step(eng,31,10120)
        step(eng,32,10120)
        self.assertEqual(eng.breakout["phase"],"ACCEPTED")
        self.assertEqual(eng.snapshot(tick(32400,10120)).pattern,"BREAKOUT_ACCEPTED")

    def test_false_break_takes_no_future_quote(self):
        eng=seeded()
        for s in range(25,30):step(eng,s,10002)
        step(eng,30,10120)
        eng.on_quote(tick(30800,9990))
        self.assertEqual(eng.breakout["phase"],"FAILED")
        self.assertEqual(eng.snapshot(tick(30800,9990)).pattern,"FAILED_BREAKOUT")

    def test_same_millisecond_source_order(self):
        e=CausalMarketStructure()
        e.on_quote(tick(1000,10000))
        e.on_quote(tick(1000,10020))
        self.assertEqual(e.active[1000].n,2)
        with self.assertRaises(ValueError):
            e.on_quote(tick(999,10000))

    def test_gap_is_not_fake_completed_bars(self):
        e=CausalMarketStructure()
        step(e,0,10000)
        e.on_quote(tick(10000,10000))
        self.assertEqual(len(e.closed[1000]),1)
        self.assertEqual(e.snapshot(tick(10000,10000)).pattern,"UNKNOWN_STALE")
        self.assertGreater(e.counters["quote_gap_reset"],0)

    def test_zone_merges_and_bounded_memory(self):
        e=CausalMarketStructure(zone_cap=8)
        for i in range(100):
            e._add_zone("RESISTANCE",5000,10000+i*100,5000*(i+1))
        self.assertLessEqual(len(e.zones),8)
        before=len(e.zones)
        e._add_zone("RESISTANCE",5000,e.zones[-1].center+1,520000)
        self.assertEqual(len(e.zones),before)
        self.assertGreaterEqual(max(z.touches for z in e.zones),2)

    def test_suggest_only_never_orders(self):
        e=CausalMarketStructure()
        e.on_quote(tick(1000))
        snapshot=e.snapshot(tick(1000))
        self.assertEqual(e.entry_advice(snapshot,1),"UNCLASSIFIED_OPPORTUNITY")
        self.assertEqual(e.hold_advice(snapshot,1,"test"),"HOLD_STRUCTURE_OBSERVE")

    def test_invalid_source_spread_rejected(self):
        e=CausalMarketStructure()
        with self.assertRaises(ValueError):
            e.on_quote(SimpleNamespace(time_msc=1000,bid_u=100,ask_u=90))


if __name__=="__main__":
    unittest.main()
