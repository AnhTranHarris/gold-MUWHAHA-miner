import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from fitted_slot_excitation import _states,design_matrix,fit_nonnegative_ridge,stabilize,TAUS_MS

def test_state_is_strictly_prior_slot():
 t=np.array([0,250,500],np.int64);c=np.zeros((3,6),np.float32);c[0,0]=2;c[1,1]=1;X=_states(t,c,TAUS_MS)
 assert np.all(X[0]==0);assert X[1,0]>0 and X[1,1]==0;assert X[2,1]>0

def test_fit_nonnegative_and_stabilize_subcritical():
 rng=np.random.default_rng(3);s=np.abs(rng.normal(size=(200,30)));sess=np.arange(200)%7;X,scale=design_matrix(s,sess);Y=np.abs(rng.normal(size=(200,6)));C=fit_nonnegative_ridge(X,Y,ridge=10.,iterations=2000)
 assert np.all(C>=0);Cs,r0,r1,k,B=stabilize(C,scale,.95);assert np.all(Cs>=0) and r1<=.9500001
