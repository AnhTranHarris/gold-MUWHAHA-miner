"""V19 shadow-only source-causal policy contracts (synthetic quotes only)."""
import unittest
from causal_cycle_policy_v19 import (
    R9V19TwoLegCausalTrail,CycleResearchSettings,R9Micro180CycleShadow
)
from coinexx_r9.models import Tick

def q(ord,sec,bid=10000,ask=10020):
    return Tick(ordinal=ord,time_s=sec,time_msc=sec*1000,bid_u=bid,ask_u=ask)

class V19Tests(unittest.TestCase):
    def test_completed_atr_choice_is_frozen_at_entry(self):
        a=R9V19TwoLegCausalTrail();a.atr.atr_u=1000.;a._start_minute_cycle(q(1,60000))
        a._open_trade(q(2,60001),1)
        self.assertEqual(a.active_trail,25)
        a.atr.atr_u=100.;a._manage_position(q(3,60002,10100,10120))
        self.assertEqual(a.active_trail,25)
        self.assertEqual(a.cfg.trail_pips,3)

    def test_lower_volatility_uses_original_three_cent_trail(self):
        a=R9V19TwoLegCausalTrail();a.atr.atr_u=250.;a._start_minute_cycle(q(1,60000))
        a._open_trade(q(2,60001),-1)
        self.assertEqual(a.active_trail,3)

    def test_only_one_opposite_rearm_is_eligible(self):
        a=R9V19TwoLegCausalTrail();a.last_position_side=1
        a._arm_opposite_after_exit()
        self.assertEqual((a.pending_mode,a.rearms),(-1,1))
        a._arm_opposite_after_exit()
        self.assertEqual(a.pending_mode,0)

    def test_no_order_or_micro180_override(self):
        sh=R9Micro180CycleShadow()
        r=sh.observe(q(1,60000),micro180_open=False)
        self.assertTrue(r["research_only"])
        self.assertFalse(r["modify_live_orders"])
        self.assertFalse(r["override_micro180_orders"])

    def test_original_source_ordinals_must_advance(self):
        sh=R9Micro180CycleShadow()
        sh.observe(q(1,60000))
        with self.assertRaisesRegex(ValueError,"ordinals"):
            sh.observe(q(1,60000))

    def test_inventory_collision_diagnostic_only(self):
        sh=R9Micro180CycleShadow()
        sh.policy.atr.atr_u=900.
        sh.observe(q(1,60000))
        sh.policy._open_trade(q(2,60000),1)
        r=sh.observe(q(3,60001),micro180_open=True,micro180_entry_side=-1)
        self.assertTrue(r["same_symbol_inventory_collision"])
        self.assertFalse(r["override_micro180_orders"])

if __name__=="__main__":unittest.main()
