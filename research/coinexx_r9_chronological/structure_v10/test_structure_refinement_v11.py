"""V11 protective structural reference tests: synthetic ONLY; no tick copies."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
for p in (ROOT/"src",ROOT/"variable_cash_horizon_20261114",
          ROOT/"dual_basket_20261114",ROOT/"micro180_20261114",HERE):
    sys.path.insert(0,str(p))

from causal_structure import StructureSnapshot
from structure_refinement_v11 import (ProtectedZoneBank, RefinedStructure,
    InvalidationObserver, freeze_thesis, FrozenStructuralThesis)
from structure_overlay_v11 import StructureShadowV11
from v9_volume_router import VolumePreservingMicroV9
from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash


def t(ms,bid=10000,ask=None,ordinal=1):
    return SimpleNamespace(time_msc=ms,time_s=ms//1000,bid_u=bid,
                           ask_u=bid+4 if ask is None else ask,ordinal=ordinal)


class ZoneBankTests(unittest.TestCase):
    def test_s5_churn_cannot_displace_h1_m15_h4(self):
        s=RefinedStructure()
        for tf in (300000,900000,3600000,14400000):
            for i in range(36):
                s.bank.add(tf,"SUPPORT",10000+i*150,10,4,1_000_000+i*100)
        before={k:tuple(z.key for z in v)
                for k,v in s.bank.buckets.items()}
        for i in range(2000):
            s._add_zone("SUPPORT",5000,10000+i*20,2_000_000+i*200)
        after={k:tuple(z.key for z in v)
               for k,v in s.bank.buckets.items()}
        self.assertEqual(before,after)
        for tf,cap in ((300000,12),(900000,12),(3600000,16),(14400000,16)):
            self.assertEqual(len(s.bank.buckets[tf]),cap)

    def test_expiry_respects_parent_timeframe(self):
        s=ProtectedZoneBank()
        s.add(14400000,"RESISTANCE",10100,20,4,10_000)
        s.add(300000,"RESISTANCE",10100,20,4,10_000)
        later=10_000+3*86_400_000
        levels=s.active(later)
        self.assertEqual([z.tf_ms for z in levels],[14400000])

    def test_merge_preserves_original_confirmation_date(self):
        s=ProtectedZoneBank()
        a=s.add(900000,"SUPPORT",10000,30,4,1000)
        b=s.add(900000,"SUPPORT",10003,30,4,2000)
        self.assertEqual(a.key,b.key)
        self.assertEqual(b.confirmed_ms,1000)
        self.assertEqual(b.last_confirmed_ms,2000)
        self.assertEqual(b.confirmations,2)

    def test_wrong_side_support_never_qualifies_buy(self):
        s=ProtectedZoneBank()
        s.add(300000,"SUPPORT",10050,10,4,1000)
        self.assertIsNone(s.frozen_reference(1,10000,10004,2000))
        s.add(300000,"SUPPORT",9980,10,4,1000)
        ref=s.frozen_reference(1,10000,10004,2000)
        self.assertIsNotNone(ref)
        self.assertLess(ref[4],ref[2])
        self.assertLess(ref[3],10000)

    def test_wrong_side_resistance_never_qualifies_sell(self):
        s=ProtectedZoneBank()
        s.add(300000,"RESISTANCE",9960,10,4,1000)
        self.assertIsNone(s.frozen_reference(-1,10000,10004,2000))
        s.add(900000,"RESISTANCE",10025,10,4,1000)
        ref=s.frozen_reference(-1,10000,10004,2000)
        self.assertIsNotNone(ref)
        self.assertGreater(ref[4],ref[3])
        self.assertGreater(ref[2],10004)

    def test_frozen_level_does_not_mutate_with_zone_merge(self):
        s=RefinedStructure()
        s.bank.add(300000,"SUPPORT",9980,10,4,1000)
        s.now_ms=2000
        orig=freeze_thesis(s,1,t(2000))
        self.assertTrue(orig.anchored)
        first=orig.invalidation_level
        s.bank.add(300000,"SUPPORT",9977,12,4,3000)
        self.assertEqual(orig.invalidation_level,first)

    def test_no_stale_micro_backup_from_an_ancient_zone(self):
        s=ProtectedZoneBank()
        ancient=SimpleNamespace(id=1,kind="SUPPORT",confirmed_ms=500,
                   last_ms=500,low=9978,high=9982,sources=("S5",),touches=99)
        self.assertIsNone(s.frozen_reference(1,10000,10004,300_000,
                                            [ancient]))

    def test_spatial_gap_rejects_nearest_wrong_side(self):
        s=ProtectedZoneBank()
        s.add(900000,"SUPPORT",9995,1,4,1000)
        # near-zone upper boundary is too close to Bid for 2*spread gap
        self.assertIsNone(s.frozen_reference(1,10000,10004,2000))

    def test_local_reference_span_cap(self):
        s=RefinedStructure()
        s.bank.add(14400000,"SUPPORT",8000,20,4,1000)
        s.now_ms=2000
        t0=freeze_thesis(s,1,t(2000))
        self.assertFalse(t0.anchored)


class InvalidationTests(unittest.TestCase):
    def setUp(self):
        self.thesis=FrozenStructuralThesis(1,1000,10000,10004,
                                          "M5:1",300000,9978,9982,9976)

    def test_no_per_quote_false_confirmation(self):
        s=InvalidationObserver(self.thesis)
        for m in (1000,1100,1200,1300):
            self.assertNotEqual(s.observe(t(m,9970)),
                                "CONFIRMED_INVALIDATION")
        self.assertEqual(s.consecutive_closed,0)

    def test_two_closed_seconds_confirm_with_liquidation_bid(self):
        s=InvalidationObserver(self.thesis)
        self.assertEqual(s.observe(t(1000,9970)),"BREACH_PENDING_CLOSED_CONFIRMATION")
        self.assertEqual(s.observe(t(2000,9970)),"BREACH_PENDING_CLOSED_CONFIRMATION")
        self.assertEqual(s.observe(t(3000,9970)),"CONFIRMED_INVALIDATION")

    def test_recovery_resets_consecutive_confirmations(self):
        s=InvalidationObserver(self.thesis)
        for ms,bid in ((1000,9970),(2000,9970),(2400,10000),
                       (3000,10000),(4000,9970),(5000,9970)):
            s.observe(t(ms,bid))
        self.assertFalse(s.confirmed)

    def test_quote_gap_resets_pending_confirmation(self):
        s=InvalidationObserver(self.thesis)
        s.observe(t(1000,9970))
        self.assertEqual(s.observe(t(10000,9970)),"QUOTE_GAP_RESET")
        self.assertEqual(s.observe(t(11000,9970)),
                         "BREACH_PENDING_CLOSED_CONFIRMATION")
        self.assertFalse(s.confirmed)

    def test_short_uses_ask_for_invalidation(self):
        sell=FrozenStructuralThesis(-1,1000,10004,10000,
                                    "M15:1",900000,10020,10030,10035)
        s=InvalidationObserver(sell)
        for ms in (1000,2000,3000):
            s.observe(t(ms,9990,ask=10036))
        self.assertTrue(s.confirmed)

    def test_unanchored_is_uncertainty_not_false_exit(self):
        s=InvalidationObserver(FrozenStructuralThesis(1,1000,10000,
                               10004,None,None,None,None,None))
        self.assertEqual(s.observe(t(2000,9900)),"NO_VALID_STRUCTURAL_STOP")


class EvidenceTests(unittest.TestCase):
    def test_unresolved_subtypes_preserve_original_unknown_primary(self):
        s=RefinedStructure()
        s.on_quote(t(1000))
        snap=s.snapshot(t(1000))
        p=s.profile(snap,1)
        self.assertEqual(p.primary,"UNKNOWN")
        self.assertEqual(p.subtype,"INSUFFICIENT_MICRO_EVIDENCE")
        self.assertEqual(snap.pattern,"UNKNOWN")

    def test_original_v9_events_unchanged_under_v11(self):
        c=R9Config(use_regime_gate=False)
        original=VolumePreservingMicroV9(c,ResearchCash(governor=False))
        refined=StructureShadowV11(c,ResearchCash(governor=False))
        for sec in range(190):
            for index,part in enumerate((0,400,800)):
                ms=sec*1000+part
                bid=200000+7*sec+2*index
                quote=Tick(ordinal=sec*3+index,time_s=sec,time_msc=ms,
                           bid_u=bid,ask_u=bid+4)
                original.on_tick(quote)
                refined.on_tick(quote)
        self.assertGreater(len(original.entries),0)
        self.assertEqual(original.trades,refined.trades)
        self.assertEqual(original.position,refined.position)
        self.assertEqual(original.stats,refined.stats)
        self.assertEqual(
          [(x["ordinal"],x["side"],x["price_u"]) for x in original.entries],
          [(x["ordinal"],x["side"],x["price_u"]) for x in refined.entries])
        self.assertEqual(
          len(refined.entries),
          sum(refined.report()["structure_v11"]["v11_entry_subtypes"].values()))
        self.assertTrue(all(x["v11_shadow_only"] for x in refined.entries))


if __name__=="__main__":unittest.main()
