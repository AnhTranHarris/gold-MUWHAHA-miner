import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cash_ladder import (CashLadderSpec,AccountSnapshot,CurrentPosition,
                         ConditionalEvidence,VariableCashHorizonPolicy)


def acct(eq=100.0,peak=100.0,spent=0.,budget=4.0):
    return AccountSnapshot(100.0,peak,eq,spent,budget)


def pos(side=1,bid=100.70,ask=100.90,entry=100.0,sl=99.3,age=7,
        minstop=.05,staleness=0,cost=.20):
    return CurrentPosition(side,entry,bid,ask,sl,1.0,cost,age,
                           staleness,minstop)


class PolicyChecks(unittest.TestCase):
    def test_buy_liquidation_realizes_net_half_dollar(self):
        p=VariableCashHorizonPolicy()
        result=p.decide(pos(),acct())
        self.assertEqual(result.action,'CLOSE_NOW')
        self.assertAlmostEqual(result.observed_liquidation_net_cash,.50)

    def test_sell_liquidation_uses_ask(self):
        z=pos(side=-1,bid=99.10,ask=99.30,sl=100.5)
        result=VariableCashHorizonPolicy().decide(z,acct())
        self.assertEqual(result.action,'CLOSE_NOW')
        self.assertAlmostEqual(result.observed_liquidation_net_cash,.50)

    def test_net_stretch_close(self):
        z=pos(bid=101.96,ask=102.16)
        result=VariableCashHorizonPolicy().decide(z,acct())
        self.assertEqual(result.action,'CLOSE_NOW')
        self.assertGreater(result.observed_liquidation_net_cash,1.75)

    def test_unverified_auc_cannot_extend_holding(self):
        e=ConditionalEvidence(.75,.15,.20,False)
        z=pos(bid=100.90,ask=101.10,age=2)
        r=VariableCashHorizonPolicy().decide(z,acct(),e)
        self.assertEqual(r.action,'CLOSE_NOW')

    def test_out_of_window_p5_cannot_hold_60secs(self):
        e=ConditionalEvidence(.75,.15,.20,True)
        z=pos(bid=100.90,ask=101.10,age=60)
        r=VariableCashHorizonPolicy().decide(z,acct(),e)
        self.assertEqual(r.action,'CLOSE_NOW')

    def test_validated_early_runner_tightens_and_locks_floor(self):
        e=ConditionalEvidence(.75,.15,.20,True)
        z=pos(bid=100.90,ask=101.10,age=2)
        r=VariableCashHorizonPolicy().decide(z,acct(),e)
        self.assertEqual(r.action,'TIGHTEN_STOP')
        self.assertAlmostEqual(r.hypothetical_stop_price,100.70)
        self.assertAlmostEqual(z.net_cash(r.hypothetical_stop_price),.50)

    def test_illegal_broker_stop_forces_available_cash_harvest(self):
        e=ConditionalEvidence(.75,.15,.20,True)
        z=pos(bid=100.80,ask=101.,age=2,minstop=.20)
        r=VariableCashHorizonPolicy().decide(z,acct(),e)
        self.assertEqual(r.action,'CLOSE_NOW')

    def test_account_10pct_stays_tighter_than_25pct(self):
        z=pos(bid=100.0,ask=100.2)
        r=VariableCashHorizonPolicy().decide(z,acct(eq=89.0))
        self.assertEqual(r.action,'CLOSE_NOW')
        self.assertIn('10%',r.reason)

    def test_capital_floor_is_also_explicitly_checked(self):
        z=pos(bid=100.0,ask=100.2)
        r=VariableCashHorizonPolicy().decide(z,acct(eq=74.0))
        self.assertEqual(r.action,'CLOSE_NOW')
        self.assertIn('25%',r.reason)

    def test_hard_two_dollar_loss(self):
        z=pos(bid=98.15,ask=98.35,age=3)
        r=VariableCashHorizonPolicy().decide(z,acct())
        self.assertEqual(r.action,'CLOSE_NOW')
        self.assertLess(r.observed_liquidation_net_cash,-2.0)

    def test_peak_to_current_drawdown_too(self):
        ctrl=VariableCashHorizonPolicy()
        evidence=ConditionalEvidence(.75,.15,.20,True)
        first=ctrl.decide(pos(bid=101.15,ask=101.35,age=2),acct(),evidence)
        self.assertIn(first.action,('TIGHTEN_STOP','HOLD'))
        second=ctrl.decide(pos(bid=99.0,ask=99.2,age=3),acct(),evidence)
        self.assertEqual(second.action,'CLOSE_NOW')
        self.assertIn('peak-to-current',second.reason)

    def test_do_not_widen_original_stop_to_two_dollars(self):
        z=pos(bid=99.99,ask=100.19,age=3,sl=99.30)
        policy=VariableCashHorizonPolicy()
        result=policy.decide(z,acct())
        self.assertEqual(result.action,'HOLD')
        self.assertEqual(result.hypothetical_stop_price,None)
        self.assertLess(abs(z.net_cash(z.original_or_current_stop_price)),2.0)

    def test_gross_daily_budget_preserved(self):
        z=pos(bid=99.99,ask=100.19,sl=99.30)
        p=VariableCashHorizonPolicy()
        self.assertEqual(p.entry_permitted(z,acct(spent=3.5,budget=4.0)).action,'BLOCK_ENTRY')
        self.assertEqual(p.entry_permitted(z,acct(spent=0,budget=4.0)).action,'HOLD')

    def test_emergency_horizon_not_30s(self):
        z=pos(bid=100.0,ask=100.2,age=31)
        r=VariableCashHorizonPolicy().decide(z,acct())
        self.assertEqual(r.action,'HOLD')
        r=VariableCashHorizonPolicy().decide(pos(bid=100.0,ask=100.2,age=121),acct())
        self.assertEqual(r.action,'CLOSE_NOW')

    def test_no_stale_model_prices(self):
        r=VariableCashHorizonPolicy().decide(pos(bid=100.0,ask=100.2,staleness=3000),acct())
        self.assertEqual(r.action,'CLOSE_NOW')

    def test_parameter_guards(self):
        with self.assertRaises(ValueError):
            CashLadderSpec(min_net_profit=2.0,stretch_net_profit=1.75)
        with self.assertRaises(ValueError):
            ConditionalEvidence(.8,.7,.2,True)


if __name__=='__main__':
    unittest.main()