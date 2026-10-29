import numpy as np, pytest, pathlib, sys
sys.path.insert(0,'/mnt/data')
from r147_live_shadow_wrapper import R147ForesightFilter,R147ContractError
class Core:
 def shadow_decision(self,**kw): return {'action':'VETO_NEW_UNFILLED_ORDER' if kw.get('risk',1)>0 else 'RELEASE_TO_SEPARATE_EXECUTION_CHECK'}
def test_shadow_never_overrides_core():
 f=R147ForesightFilter(Core())
 r=f.decision(common_state_153=np.zeros(153,np.float32),risk=1)
 assert r['action']=='VETO_NEW_UNFILLED_ORDER' and r['r147_override_active'] is False
def test_shape_failclosed():
 with pytest.raises(R147ContractError): R147ForesightFilter(Core()).decision(common_state_153=np.zeros(152),risk=1)
def test_nonfinite_failclosed():
 x=np.zeros(153);x[3]=np.nan
 with pytest.raises(R147ContractError): R147ForesightFilter(Core()).decision(common_state_153=x,risk=1)
def test_release_preserved():
 r=R147ForesightFilter(Core()).decision(common_state_153=np.zeros(153),risk=0)
 assert r['action']=='RELEASE_TO_SEPARATE_EXECUTION_CHECK'
