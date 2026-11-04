import sys
import numpy as np

from r23h24_competing_hazard import prefix_features,build_cause_training,build_held_training,build_wait_training

def fixture():
 n=25
 x=np.zeros((n,47),np.float32);x[:,0]=1;x[:,1]=100;x[:,5]=np.arange(n)
 t=np.arange(n,dtype=np.int64)*1000
 l=np.full((n,2,3),2,np.int8)
 l[0,:,0]=1;l[1,:,0]=0;l[2,:,1]=3
 held=np.ones((n,2,3),np.int8);held[0,:,0]=0;held[2,:,0]=2
 return {'x':x,'t':t,'l':l,'f':np.arange(n,dtype=np.int32),'held':held}

def test_prefix_feature_uses_only_current_snapshot():
 a=fixture();fx=prefix_features(a['x'],a['t']);assert fx.shape==(25,57)
 old=fx[0].copy();a['x'][1:]+=99999
 assert np.allclose(prefix_features(a['x'][:1],a['t'][:1])[0],old)

def test_stage2_only_if_stage1_event_free():
 a=fixture();x,y=build_cause_training(a,np.arange(25,dtype=np.int32))
 assert x.shape[1]==59
 assert len(y)==2*(25+23+24)
 assert (y==3).sum()==2

def test_held_censor_is_not_classified_as_safe():
 a=fixture();x,y=build_held_training(a,np.arange(25,dtype=np.int32))
 assert x.shape[1]==59 and set(np.unique(y))=={0,1}
 assert len(y)==2*(3*25-1)

def test_wait_supervised_label_only_and_missing_lag_rejected():
 a=fixture();x,y=build_wait_training(a,np.arange(25,dtype=np.int32))
 assert x.shape[1]==57 and len(y)==15
