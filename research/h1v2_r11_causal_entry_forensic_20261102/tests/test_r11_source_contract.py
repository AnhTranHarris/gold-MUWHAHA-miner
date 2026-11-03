"""R11 additive source-admission, mark, and fail-closed policy adversarial tests."""
import numpy as np
import pytest
from r11_entry_admission import candidate_mask,compare_source,H1V2_ORIGINAL,V5_SHADOW,original_candidate_parity
from r11_quote_marks import quote_marks,observed_prefix_state,MARK_NAMES
from r11_policy import ActionEvidence,AdmissionPolicy,decide

def test_mixed_bid_ask_marks_are_never_zero():
    t=np.array([0,1,2,3,4],np.int64)
    b=np.array([100,100.1,100,100.1,100],float)
    a=np.array([100.2,100.1,100.2,100.3,100.2],float)
    m,g=quote_marks(t,b,a)
    assert m.tolist()==[0,7,8,5,6]
    assert g.tolist()==[True,False,False,False,False]
    assert MARK_NAMES[7]=="BID_UP_ASK_DOWN"

def test_gap_epoch_resets_mark_and_preserves_same_ms_ordinal():
    t=np.array([0,1,1,16002,16002],np.int64)
    b=np.array([100,100.1,100,101,101.1],float);a=b+.2
    marks,epochs=quote_marks(t,b,a)
    assert marks.tolist()==[0,5,6,0,5]
    assert epochs.tolist()==[True,False,False,True,False]

def test_h1v2_vs_v5_gap_universe_diverges_after_20s_gap():
    t=np.r_[np.arange(0,305000,5000,dtype=np.int64),325001]
    b=np.ones(len(t))*100;a=b+.2
    h=candidate_mask(t,b,a,H1V2_ORIGINAL)
    v=candidate_mask(t,b,a,V5_SHADOW)
    assert h[-1] and not v[-1]
    assert h[t.tolist().index(300000)] and v[t.tolist().index(300000)]
    r=compare_source(t,b,a)
    assert r["original_only"]>=1 and r["intersection"]>=1

def test_h1v2_original_contract_hard_boundary_and_spread():
    t=np.arange(0,301000,5000,dtype=np.int64)
    b=np.ones(len(t))*100;a=b+.2
    def original_reference(t,b,a,max_spread=1.50,warmup_ms=300000,gap_reset_ms=300000):
        first=t[0];rows=[]
        for i in range(len(t)):
            if i and t[i]-t[i-1]>=gap_reset_ms:first=t[i]
            if (i==0 or t[i]//250!=t[i-1]//250) and t[i]-first>=warmup_ms and 0<=a[i]-b[i]<=max_spread:
                rows.append(i)
        return np.array(rows,np.int64)
    assert original_candidate_parity(t,b,a,original_reference)>=1
    a[-1]=b[-1]+2.
    assert not candidate_mask(t,b,a,H1V2_ORIGINAL)[-1]

def test_asof_features_future_mutation_cannot_change_prefix():
    t=np.array([0,25,50,75,100,125,150],np.int64)
    b=np.array([100,100.1,100,100.2,100.1,100.15,100.4],float);a=b+.2
    x=observed_prefix_state(t,b,a,np.array([3],np.int64))
    altered_b=b.copy();altered_b[4:]=[99,102,98]
    altered_a=altered_b+.2
    assert np.array_equal(x,observed_prefix_state(t,altered_b,altered_a,np.array([3],np.int64)))

def test_same_timestamp_later_source_quote_not_in_prefix():
    t=np.array([0,1,1,1,2],np.int64)
    b=np.array([100,100.1,100.5,99.6,100.4],float);a=b+.2
    x=observed_prefix_state(t,b,a,np.array([1],np.int64))
    b[2:]=[900,800,700];a=b+.2
    assert np.array_equal(x,observed_prefix_state(t,b,a,np.array([1],np.int64)))

def _e(side,**kwargs):
    d=dict(side=side,p_correct_lower=.90,p_bad_upper=.08,expected_net_lower=.12,
           cvar_loss_upper=.10,independent_blocks=55,
           source_verified=True,model_verified=True,calibrated_chronologically=True)
    d.update(kwargs);return ActionEvidence(**d)

def test_eligible_second_side_not_masked_by_ineligible_first():
    buy=_e("BUY",expected_net_lower=.50,p_bad_upper=.30)
    sell=_e("SELL",expected_net_lower=.04)
    assert decide(buy,sell,spread=.2,quote_epoch_ready=True)=="SELL"

def test_any_missing_approval_fails_closed():
    assert decide(_e("BUY",source_verified=False),None,.2,True)=="WAIT"
    assert decide(_e("BUY",calibrated_chronologically=False),None,.2,True)=="WAIT"
    assert decide(_e("BUY"),None,.2,False)=="WAIT"
    assert decide(_e("BUY"),None,2.0,True)=="WAIT"
    assert decide(_e("BUY",expected_net_lower=-.1),None,.2,True)=="WAIT"

def test_equal_qualified_value_abstains():
    assert decide(_e("BUY"),_e("SELL"),.2,True)=="WAIT"
