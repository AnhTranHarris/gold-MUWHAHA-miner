"""Unfitted specialist policy contracts; these labels never submit orders."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_structure import StructureSnapshot
from specialist_policy import HierarchicalPolicy


def snapshot(**kw):
    values=dict(time_msc=1000,pattern="TREND_CONTINUATION",
                regime="DIRECTIONAL",micro_direction=1,parent_direction=1,
                nested="ALIGNED",change_alarm=False,directional_change=1,
                breakout_side=0,breakout_phase="NONE",
                support=(9950.,9960.,1),resistance=(10050.,10060.,2),
                quote_gap_ms=0)
    values.update(kw)
    return StructureSnapshot(**values)


class SpecialistTests(unittest.TestCase):
    def setUp(self):self.router=HierarchicalPolicy()

    def test_breakout_probe_waits_before_acceptance(self):
        x=self.router.propose(snapshot(pattern="BREAKOUT_PROBE",
             breakout_side=1,breakout_phase="PROBE"),1,10000,10004)
        self.assertEqual((x.specialist,x.proposal),
                         ("BREAKOUT_INITIATION","WAIT_CONFIRM"))

    def test_breakout_acceptance_and_frozen_stop(self):
        x=self.router.propose(snapshot(pattern="BREAKOUT_ACCEPTED",
             breakout_side=1,breakout_phase="ACCEPTED"),1,10000,10004)
        self.assertEqual(x.proposal,"STRUCTURAL_CANDIDATE")
        self.assertEqual(x.structural_stop,9950.)
        invalid=self.router.review(x,snapshot(),1,9949,9953)
        self.assertEqual(invalid.action,"THESIS_INVALIDATED")

    def test_retest_requires_confirmation(self):
        x=self.router.propose(snapshot(pattern="BREAKOUT_RETEST",
             breakout_side=1,breakout_phase="RETEST"),1,10000,10004)
        self.assertEqual(x.proposal,"WAIT_REJECTION")
        y=self.router.propose(snapshot(pattern="RETEST_RESUMPTION",
             breakout_side=1,breakout_phase="RETEST_CONFIRMED"),1,10000,10004)
        self.assertEqual(y.proposal,"STRUCTURAL_CANDIDATE")

    def test_exhaustion_is_observation_not_blind_entry(self):
        s=snapshot(pattern="EXHAUSTION_WARNING")
        plan=self.router.propose(s,1,10000,10004)
        self.assertEqual(plan.specialist,"TREND_EXHAUSTION")
        self.assertEqual(plan.proposal,"WAIT_IMPULSE_RENEWAL")
        self.assertEqual(self.router.review(plan,s,1,10000,10004).action,"DEFEND")

    def test_nested_countertrend_distinguished(self):
        x=self.router.propose(snapshot(pattern="NESTED_PULLBACK",
                                      parent_direction=-1,micro_direction=1),
                              1,10000,10004)
        self.assertEqual(x.specialist,"NESTED_COUNTERTREND")
        self.assertEqual(x.proposal,"WAIT_PARENT_RESOLUTION")

    def test_confirmed_reversal_has_separate_specialist(self):
        x=self.router.propose(snapshot(pattern="REVERSAL_CONFIRMED",
                                      parent_direction=-1,micro_direction=1),
                              1,10000,10004)
        self.assertEqual(x.specialist,"STRUCTURAL_REVERSAL")

    def test_unverified_range_edge_never_blindly_enters(self):
        x=self.router.propose(snapshot(pattern="CONSOLIDATION",
                         micro_direction=0,parent_direction=0),
                         1,9963,9967)
        self.assertEqual(x.specialist,"RANGE_BOUNDARY")
        self.assertEqual(x.proposal,"WAIT_REJECTION")

    def test_failed_breakout_defense_overrides_trend(self):
        x=self.router.propose(snapshot(pattern="FAILED_BREAKOUT",
                              breakout_side=1,breakout_phase="FAILED"),
                              1,10000,10004)
        self.assertEqual(x.proposal,"AVOID_UNTIL_NEW_SETUP")

    def test_missing_quotes_does_not_create_entry(self):
        x=self.router.propose(snapshot(pattern="UNKNOWN_STALE",
                                      quote_gap_ms=5000),1,10000,10004)
        self.assertEqual(x.proposal,"WAIT")


if __name__=="__main__":unittest.main()
