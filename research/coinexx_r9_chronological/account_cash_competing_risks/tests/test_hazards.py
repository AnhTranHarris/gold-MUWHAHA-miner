"""Exact Aalen-Johansen risk-set and train/test cash-utility tests."""
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPO=ROOT.parents[0]
sys.path.insert(0,str(REPO/"src"))
sys.path.insert(0,str(ROOT/"src"))

from cash_risk_overlay import Episode,CAUSE_TARGET,CAUSE_STOP,CAUSE_TIMEOUT,CAUSE_GAP,CAUSE_EOF
from competing_hazards import (
    aalen_johansen, fit_context_tables,evaluate_frozen_table,
    context_key,cash_cvar95,HORIZONS_MS,
)


def episode(i,cause,event_ms,payoff=None,session=1,spread=20):
    return Episode(entry_ordinal=i,entry_time_msc=1_000_000+i*1000,
                   source_hour=10,session=session,side=1,
                   entry_price_cents=400000,entry_spread_cents=spread,
                   cause=cause,event_time_ms=event_ms,
                   overlay_net_cash=payoff)


class HazardTests(unittest.TestCase):
    def test_cause_specific_aj_with_informative_censor_count(self):
        es=[episode(1,CAUSE_TARGET,1000,1.79),
            episode(2,CAUSE_GAP,2500),
            episode(3,CAUSE_STOP,3000,-0.52),
            episode(4,CAUSE_TIMEOUT,30000,-0.14)]
        x=aalen_johansen(es)
        self.assertEqual([a.horizon_ms for a in x],list(HORIZONS_MS))
        self.assertAlmostEqual(x[0].cause_probability[CAUSE_TARGET],.25)
        self.assertAlmostEqual(x[0].survival,.75)
        self.assertAlmostEqual(x[1].cause_probability[CAUSE_STOP],.375)
        self.assertAlmostEqual(x[-1].cause_probability[CAUSE_TIMEOUT],.375)
        self.assertAlmostEqual(x[-1].survival,0.)
        self.assertAlmostEqual(sum(x[-1].cause_probability.values()),1.)

    def test_all_censored_is_not_reported_as_zero_risk(self):
        es=[episode(i,CAUSE_EOF,1000) for i in range(1,4)]
        final=aalen_johansen(es)[-1]
        self.assertEqual(final.survival,1.)
        self.assertEqual(sum(final.cause_probability.values()),0.)
        self.assertEqual(final.risk_set_at_horizon,0)

    def test_events_same_timestamp_before_censor(self):
        es=[episode(1,CAUSE_TARGET,0,2.0),
            episode(2,CAUSE_STOP,0,-1),
            episode(3,CAUSE_GAP,0)]
        x=aalen_johansen(es)[-1]
        self.assertAlmostEqual(x.cause_probability[CAUSE_TARGET],1/3)
        self.assertAlmostEqual(x.cause_probability[CAUSE_STOP],1/3)
        self.assertAlmostEqual(x.survival,1/3)

    def test_cash_is_winning_and_losing_trade_not_label_only(self):
        es=[episode(1,CAUSE_TARGET,1000,2.05),
            episode(2,CAUSE_STOP,3000,0.18),
            episode(3,CAUSE_TIMEOUT,30000,-0.56),
            episode(4,CAUSE_GAP,1500)]
        m=fit_context_tables(es,by="global",min_group_count=3,risk_lambda=.25,max_censor_fraction=.30)
        one=m["groups"]["all"]
        self.assertTrue(one["train_eligible"])
        self.assertAlmostEqual(one["mean_account_cash_by_cause"][CAUSE_STOP],0.18)
        self.assertEqual(one["censored_count"],1)
        self.assertIsNotNone(one["estimated_risk_adjusted_cash"])
        self.assertLessEqual(one["estimated_risk_adjusted_cash"],
                             one["estimated_net_cash_per_entry"])

    def test_default_abstains_when_quote_censoring_exceeds_ten_percent(self):
        rows=[episode(i,CAUSE_TARGET,1000,2.) for i in range(1,9)]
        rows += [episode(9,CAUSE_GAP,2000),episode(10,CAUSE_EOF,1000)]
        table=fit_context_tables(rows,by="global",min_group_count=3)
        self.assertFalse(table["groups"]["all"]["train_eligible"])
        self.assertIsNone(table["groups"]["all"]["estimated_net_cash_per_entry"])

    def test_no_future_cause_creates_entry_context_key(self):
        a=episode(1,CAUSE_TARGET,1000,1.8)
        b=episode(1,CAUSE_STOP,1000,-1.0)
        self.assertEqual(context_key(a),context_key(b))
        self.assertEqual(context_key(a,"hour"),context_key(b,"hour"))

    def test_train_only_table_and_later_evaluation(self):
        training=[episode(i,CAUSE_TARGET if i%2 else CAUSE_STOP,
                          1000 if i%2 else 3000,1.8 if i%2 else -.6)
                  for i in range(1,101)]
        later=[episode(i,CAUSE_STOP,2500,-.5) for i in range(150,160)]
        table=fit_context_tables(training,min_group_count=20)
        result=evaluate_frozen_table(table,later)
        self.assertEqual(result["all_evaluation_episodes"],10)
        self.assertEqual(result["matched_uncensored_count"],10)
        self.assertIsNotNone(result["mean_predicted_net_cash"])

    def test_sparse_context_fails_to_infer_value(self):
        m=fit_context_tables([episode(1,CAUSE_TARGET,1000,2)],min_group_count=20)
        one=next(iter(m["groups"].values()))
        self.assertFalse(one["train_eligible"])
        self.assertIsNone(one["estimated_net_cash_per_entry"])

    def test_loss_tail_sign(self):
        self.assertAlmostEqual(cash_cvar95([-2.,-1.,1.,3.]),2.)
        self.assertEqual(cash_cvar95([1.,2.]),0.)
        self.assertIsNone(cash_cvar95([]))

    def test_invalid_event_time_rejected(self):
        with self.assertRaises(ValueError):
            aalen_johansen([episode(1,CAUSE_TARGET,50000,2.0)])


if __name__=="__main__":
    unittest.main()
