"""Adversarial original-source-invariant synthetic fixtures; H11 is a teacher only."""
import numpy as np,sys
sys.path.insert(0,'/mnt/data/R9V2_H9_CORRECT_SIDE_RESEARCH_20261105/src')
from h11_exclusive_direction_teacher import exclusive
A=np.array([[10,20],[40,21],[30,30],[-1,10],[20,-1],[-1,-1]],dtype=np.int32)
S=np.ones((6,2),dtype=bool)
R=exclusive(A,S)
assert np.array_equal(R,np.array([[True,False],[False,True],[False,False],[False,True],[True,False],[False,False]]))
assert not np.any(R.sum(axis=1)>1)
# Opposing side with earlier raw event retains priority even when its stage gate is false.
T=S.copy();T[1,1]=False;R2=exclusive(A,T);assert not R2[1].any()
# Current logic has to be invariant to swapping side direction and the quote ordinal ordering.
assert np.array_equal(exclusive(A[:,::-1],S[:,::-1]),R[:,::-1])
print('H11_EXCLUSIVE_4_ADVERSARIAL_TESTS_PASS')
