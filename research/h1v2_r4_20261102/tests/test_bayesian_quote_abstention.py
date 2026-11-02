import numpy as np
from bayesian_quote_abstention import cells,fit,score
from four_month_competing_risks import wilson

def toy(n,success=0):
 b=np.zeros((n,100),np.float32);b[:,99]=.7
 p=np.zeros((n,30),np.float32);m=np.zeros((n,92),np.float32)
 k=np.zeros((n,2),np.uint8);k[:success,0]=3
 t=np.arange(n,dtype=np.int64)*60000
 return b,p,m,k,t

def test_wilson_requires_support():
 assert wilson(1,1)<.8
 assert wilson(8,10)<.8
 assert wilson(150,150)>.8

def test_bayes_prior_train_only_and_july_remains_unseen():
 d={'01':toy(30,3),'02':toy(30,3),'06':toy(30,3),'07':toy(30,30)}
 a=fit(d,('01','02','06'),'coarse',100)
 assert abs(a[1][3]-(9/(30*2*3+4)))<.02
 baseline=score(d['07'],a,'coarse','07')
 d['07']=(d['07'][0],d['07'][1],d['07'][2],np.zeros_like(d['07'][3]),d['07'][4])
 b=fit(d,('01','02','06'),'coarse',100)
 assert np.array_equal(a[0],b[0]) and np.array_equal(a[1],b[1])
 assert baseline['posterior_max_strong']==score(d['07'],b,'coarse','07')['posterior_max_strong']

def test_coarse_fine_regime_indices_bounded():
 d=toy(6)
 assert np.max(cells(d,'coarse')[0])<81
 assert np.max(cells(d,'fine')[0])<729
