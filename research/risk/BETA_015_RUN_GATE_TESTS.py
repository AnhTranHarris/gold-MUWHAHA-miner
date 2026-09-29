import unittest
from BETA_015_RESEARCH_RUN_GATE import config_sha256,assert_new_funded_replay_manifest
from BETA_015_PROP_POLICY_V1 import PolicyViolation
class TestRunGate(unittest.TestCase):
    def get_valid(self):
        return {'prop_policy':{'policy_id':'BETA_015_PROP_V1','config_sha256':config_sha256(),'tick_by_tick_guard':True,'single_account':True,'fixed_lots':.01,'initial_cash_usd':100000,'commission_per_roundtrip_usd':.02,'news_gate_status':'NOT_EVALUATED','owner_mql5_authorization':False,'source_data_through_month':'2026-01'},'funded_account':{'terminal_breach':True,'post_terminal_new_trades':0,'post_terminal_deposits':0,'max_open_lots':.01},'shadow_counterfactual':{'mixed_into_funded_totals':False},'independent_accounting_qa_passed':True}
    def test_valid(self):self.assertTrue(assert_new_funded_replay_manifest(self.get_valid()))
    def test_no_policy(self):
        v=self.get_valid();del v['prop_policy']
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_august(self):
        v=self.get_valid();v['prop_policy']['source_data_through_month']='2026-08'
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_post_stop_trading(self):
        v=self.get_valid();v['funded_account']['post_terminal_new_trades']=1
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_mixed_shadow(self):
        v=self.get_valid();v['shadow_counterfactual']['mixed_into_funded_totals']=True
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_missing_qa(self):
        v=self.get_valid();v['independent_accounting_qa_passed']=False
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_wrong_commission(self):
        v=self.get_valid();v['prop_policy']['commission_per_roundtrip_usd']=.20
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
    def test_reject_changed_profile_hash(self):
        v=self.get_valid();v['prop_policy']['config_sha256']='fake'
        with self.assertRaises(PolicyViolation):assert_new_funded_replay_manifest(v)
if __name__=='__main__':unittest.main(verbosity=2)