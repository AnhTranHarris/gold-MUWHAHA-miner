from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import r24_firstpass_engine as engine
import r24_fit_hazard_month as fit
import r24_predict_replay_fullcalendar as policy

def test_competing_and_wait_causality_boundary():
 # Future labels are supervised-only; an as-of model must receive features,
 # side and horizon only, never true event or original future teacher side.
 assert 'future_selected_side' not in engine.FEATURE_NAMES
 assert 'R9_SYNTH_original_quarter_reference' not in engine.FEATURE_NAMES
 assert 'event' not in engine.FEATURE_NAMES
 assert fit.MODEL_EXTRA==('side_buy1_sellminus1','horizon_seconds')

def test_wait_10s_target_label_and_current_good_rejection():
 t=np.arange(0,21000,1000,dtype=np.int64)
 z=np.full((len(t),2,3),0,np.int8)
 z[5,0,0]=1;z[16,1,0]=1
 w=fit.future_wait_label(z,t)
 assert w[0]==1 and w[4]==1 and w[5]==0 and w[6]==1 and w[17]==0

def test_replay_1_position_real_delay_utc_bucket():
 n=6;pr=np.zeros((n,2,3,5),np.float32);pr[:,:,:,:]=0.01
 pr[:,0,0,1]=0.9;pr[:,0,0,0]=0.04
 w=np.zeros(n,np.float32)
 y=np.zeros((n,2,3),np.int8);y[:,0,0]=1
 signal=np.arange(0,n*1000,1000,dtype=np.int64)+int(1800000000000)
 fill=signal+120
 event=np.column_stack((fill+3000,fill+3000))
 timeout=np.column_stack((fill+15000,fill+30000,fill+60000))
 qfirst=int(signal[0]//900000)
 # All successive signals before first exit MUST be busy-skipped.
 z=policy.replay_one_position(pr,w,y,signal,fill,event,timeout,qfirst,1,0.5,0.8,0.,0.)
 assert z[0][0]==2,(z[0],z[5])
 assert z[1][0]==2 and len(z[5])==2

def test_wait_policy_and_missing_fill_fail_closed():
 n=2;pr=np.full((n,2,3,5),0.01,np.float32);pr[:,0,0,1]=0.9;pr[:,0,0,0]=0.05
 z=np.full((n,2,3),4,np.int8)
 t=np.asarray([1800000000000,1800000010000],np.int64)
 fill=np.asarray([-1,1800000010120],np.int64)
 event=np.full((n,2),-1,np.int64);timeout=np.full((n,3),-1,np.int64)
 qfirst=int(t[0]//900000)
 result=policy.replay_one_position(pr,np.zeros(n,np.float32),z,t,fill,event,timeout,qfirst,1,.5,.8,0.,0.)
 assert int(result[0][0])==0 and len(result[5])==0
