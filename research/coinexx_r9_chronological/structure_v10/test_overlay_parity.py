"""V9 source-exact decision preservation without market-data downloads."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
for q in (ROOT/"src",ROOT/"variable_cash_horizon_20261114",
          ROOT/"dual_basket_20261114",ROOT/"micro180_20261114",P):
    sys.path.insert(0,str(q))
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from v9_volume_router import VolumePreservingMicroV9
from structure_overlay import StructureShadowV10


class V9PreservationTests(unittest.TestCase):
    def test_shadow_changes_no_entries_exits_or_lifecycle(self):
        config=R9Config(use_regime_gate=False)
        a=VolumePreservingMicroV9(config,ResearchCash(governor=False))
        b=StructureShadowV10(config,ResearchCash(governor=False))
        count=0
        for second in range(190):
            for fraction in (0,400,800):
                ms=second*1000+fraction
                bid=200000+7*second+(fraction//400)*2
                tick=Tick(ordinal=count,time_s=second,time_msc=ms,
                          bid_u=bid,ask_u=bid+4)
                a.on_tick(tick)
                b.on_tick(tick)
                count+=1
        self.assertGreater(len(a.entries),0,"Must exercise actual V9 opening path")
        self.assertEqual(
            [(x["ordinal"],x["side"],x["price_u"]) for x in a.entries],
            [(x["ordinal"],x["side"],x["price_u"]) for x in b.entries])
        self.assertEqual(a.trades,b.trades)
        self.assertEqual(a.position,b.position)
        self.assertEqual(a.stats,b.stats)
        self.assertTrue(all(x["v10_shadow_only"] for x in b.entries))
        self.assertEqual(b.report()["structure_v10"]["mode"],
                         "SHADOW_NO_ORDER_OR_EXIT_EFFECT")


if __name__=="__main__":
    unittest.main()
