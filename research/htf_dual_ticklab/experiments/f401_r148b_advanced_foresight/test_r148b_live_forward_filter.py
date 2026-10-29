import inspect
from r148b_live_forward_filter import apply_r148b_policy,MaturedRiskMonitor,R148BAdvancedForesightFilter

def test_no_truth_argument():
 assert 'truth' not in inspect.signature(R148BAdvancedForesightFilter.decision).parameters

def test_coinexx_rescue_and_hunt():
 a,r=apply_r148b_policy(base_action='VETO_NEW_UNFILLED_ORDER',rescue_score=.9,hunter_score=None,broker='coinexx');assert a=='RELEASE_TO_SEPARATE_EXECUTION_CHECK' and r=='R148_RESCUE'
 a,r=apply_r148b_policy(base_action='RELEASE_TO_SEPARATE_EXECUTION_CHECK',rescue_score=None,hunter_score=.99,broker='coinexx');assert a=='VETO_NEW_UNFILLED_ORDER' and r=='R148_RESIDUAL_HUNTER'

def test_failclosed_unknown_and_disabled():
 a,_=apply_r148b_policy(base_action='RELEASE_TO_SEPARATE_EXECUTION_CHECK',rescue_score=None,hunter_score=1,broker='other');assert a=='RELEASE_TO_SEPARATE_EXECUTION_CHECK'
 a,_=apply_r148b_policy(base_action='RELEASE_TO_SEPARATE_EXECUTION_CHECK',rescue_score=None,hunter_score=1,broker='dukascopy',override_enabled=False);assert a=='RELEASE_TO_SEPARATE_EXECUTION_CHECK'

def test_matured_monitor_is_past_only_and_can_disable():
 m=MaturedRiskMonitor(min_correct=100,max_correct_veto_rate=.02)
 for _ in range(100):m.observe_matured(original_correct=True,candidate_veto=True)
 assert not m.override_allowed and m.upper_wilson()>.02
