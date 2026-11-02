import numpy as np
from fitted_quote_excitation import next_marks,fit_poisson,predict

def test_equal_ms_future_ordinals_and_horizon():
    t=np.array([0,0,0,100,250,251,900,1200],np.int64)
    marks=np.array([1,2,0,3,4,5,6,1],np.uint8)
    got=next_marks(t,marks,np.array([0,1,4],np.int64),horizon_ms=250)
    assert got[0].tolist()==[0,1,1,1,0,0]
    assert got[1].tolist()==[0,0,1,1,0,0]
    assert got[2].tolist()==[0,0,0,0,1,0]

def test_cross_coefficient_nonnegative_and_causal():
    rng=np.random.default_rng(11)
    X=rng.poisson(1,(120,18)).astype('float32');Y=rng.poisson(1,(120,6))
    c=fit_poisson(X,Y,'self',iterations=20)
    assert c.shape==(6,19) and np.all(c>=0)
    assert np.all(predict(X,c)>0)
    assert np.all(c[0,np.setdiff1d(np.arange(19),[0,1,7,13])]==0)

def test_future_quote_mutation_cannot_change_asof_intensity_basis():
    from marked_quote_sequences import extract,mark_quotes
    from fitted_quote_excitation import next_marks
    ts=np.array([0,40,40,40,100,200,400,900,1200],np.int64)
    bid=np.array([100.,100.1,100.2,100.1,100.0,100.3,100.2,100.4,100.1])
    ask=bid+.4
    decision_ix=np.array([2],np.int64)
    before=extract(ts,bid,ask,decision_ix,mark_quotes(bid,ask))
    alternate=bid.copy();alternate[3:]+=np.array([2.,-2.,-2.,3.,-1.,1.])
    after=extract(ts,alternate,alternate+.4,decision_ix,mark_quotes(alternate,alternate+.4))
    assert np.array_equal(before,after), 'future quote contamination in causal marks'
    y1=next_marks(ts,mark_quotes(bid,ask),decision_ix)
    y2=next_marks(ts,mark_quotes(alternate,alternate+.4),decision_ix)
    assert not np.array_equal(y1,y2), 'future outcome should change independently of as-of features'
