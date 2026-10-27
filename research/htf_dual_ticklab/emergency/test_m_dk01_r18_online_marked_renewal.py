import pytest
from m_dk01_r18_online_marked_renewal import (NativeQuote, MarkedRenewalState,
    SourceClockError, FrozenRiskPolicy, count_original_veto)
E=1700000000000
Q=[NativeQuote(E-140000,0,1800000,1800250),
   NativeQuote(E-900,1,1800200,1800250),
   NativeQuote(E-600,2,1800300,1800250+300),
   NativeQuote(E,3,1800300,1800570)]

def run(quotes=Q,side=1):
    state=MarkedRenewalState()
    for q in quotes: state.observe(q)
    x=quotes[-1]
    return state.asof(event_msc=x.time_msc,original_quote_ordinal=x.ordinal,side=side)

def test_native_integer_division():
    f=run();assert f['source_bid']==1800.3 and f['source_ask']==1800.57

def test_frozen_stream_determinism():
    assert run()==run()

def test_quote_future_invariance():
    base=run();future=Q+[NativeQuote(E+10,4,1900000,1900500)]
    state=MarkedRenewalState()
    for q in future:
        state.observe(q)
        if q.ordinal==3:
            before=state.asof(event_msc=E,original_quote_ordinal=3,side=1)
    assert before==base
    with pytest.raises(SourceClockError):state.asof(event_msc=E,original_quote_ordinal=3,side=1)

def test_same_millisecond_next_ordinal_cannot_retroactively_veto():
    state=MarkedRenewalState()
    for q in Q:state.observe(q)
    earlier=state.asof(event_msc=E,original_quote_ordinal=3,side=1)
    state.observe(NativeQuote(E,4,1900000,1900500))
    with pytest.raises(SourceClockError):state.asof(event_msc=E,original_quote_ordinal=3,side=1)
    assert earlier['source_bid']==1800.3

def test_direction_symmetry():
    x=run(side=1);y=run(side=-1)
    assert x['decay_2000ms_bid_ask_polarity']==-y['decay_2000ms_bid_ask_polarity']
    assert x['decay_2000ms_spread_stress']==y['decay_2000ms_spread_stress']

def test_marked_bid_only_and_ask_only():
    f=run()
    assert f['decay_2000ms_bid_only']>0 and f['decay_2000ms_ask_only']>0

def test_non_monotone_fails_closed():
    s=MarkedRenewalState()
    s.observe(Q[0])
    with pytest.raises(SourceClockError):s.observe(Q[0])
    with pytest.raises(SourceClockError):s.observe(NativeQuote(E-140000,-1,1800000,1800250))

def test_invalid_price_fails_closed():
    with pytest.raises(SourceClockError):MarkedRenewalState().observe(NativeQuote(E,0,1000,500))

def test_broker_separation():
    with pytest.raises(ValueError):MarkedRenewalState(broker='coinexx')

def test_warmup_non_ready_if_short_history():
    x=run([Q[-1]])
    assert x['warmup_2min']==0.
    assert run()['warmup_2min']==0.  # sparse/dealer-gap history is not warm
    q=[NativeQuote(E-200000+i*3000,i,1800000+i,1800250+i) for i in range(68)]
    assert run(quotes=q)['warmup_2min']==1.

def test_finite_and_high_order_decrements():
    f=run()
    assert all(abs(v) < 1e8 for v in f.values())
    assert f['renewal_burst_ratio'] > 0

def test_guard_defers_score_not_mature():
    p=FrozenRiskPolicy(.91,.95,.65)
    d={'opposite':.96,'neutral':.99,'correct':.09}
    assert p.decide(d,quote_warm=False,decision_msc=E,score_observed_through_msc=E)=='KEEP_UNSCORED'
    assert p.decide(d,quote_warm=True,original_order_already_filled=True,decision_msc=E,score_observed_through_msc=E)=='FILLED_UNTOUCHABLE'
    assert p.decide(d,quote_warm=True,decision_msc=E,score_observed_through_msc=E)=='VETO_NEW_UNFILLED_ORDER'

def test_correct_guard_overrides_veto():
    p=FrozenRiskPolicy(.91,.95,.65)
    assert p.decide({'opposite':1.,'neutral':1.,'correct':.66},quote_warm=True,decision_msc=E,score_observed_through_msc=E)=='KEEP_RIGHT_GUARD'

def test_invalid_score_no_veto():
    p=FrozenRiskPolicy(.91,.95,.65)
    assert p.decide({'opposite':float('nan'),'neutral':1.,'correct':0.},quote_warm=True,decision_msc=E,score_observed_through_msc=E)=='KEEP_UNSCORED'

def test_unique_veto_no_double_count_and_classes():
    a=count_original_veto([0,1,2,0,1,2],[True]*6,[True,True,False,False,False,True]); assert a=={
    'total':6,'right_total':2,'bad_total':4,'unique_bad':2,'extra_right':1,
    'overlap_bad':2,'overlap_right':1,'unique_opposite':1,'unique_neutral':1}

def test_denominator_mismatch_rejected():
    with pytest.raises(ValueError):count_original_veto([0,1],[True],[False])

def test_session_gap_flushes_old_quote_excitation():
    state=MarkedRenewalState()
    for q in Q: state.observe(q)
    state.observe(NativeQuote(E+601000,4,1800300,1800570))
    f=state.asof(event_msc=E+601000,original_quote_ordinal=4,side=1)
    assert f["warmup_2min"]==0. and f["decay_2000ms_bid_only"]==0.

def test_do_not_allow_unbounded_model_thresholds_to_be_called_model_evidence():
    p=FrozenRiskPolicy(.91,.95,.65)
    assert p.decide({"opposite":0.,"neutral":0.,"correct":0.},quote_warm=True,decision_msc=E,score_observed_through_msc=E)=="KEEP_NEW_ORDER_CANDIDATE"

def test_model_timestamp_watermark_cannot_look_ahead():
    p=FrozenRiskPolicy(.9,.9,.5)
    z={"opposite":1.,"neutral":0.,"correct":0.}
    assert p.decide(z,quote_warm=True,decision_msc=E,score_observed_through_msc=E+1)=="KEEP_UNSCORED"
    assert p.decide(z,quote_warm=True)=="KEEP_UNSCORED"

def test_calibration_threshold_domain_guard():
    with pytest.raises(ValueError):FrozenRiskPolicy(1.1,.9,.5)
    with pytest.raises(ValueError):FrozenRiskPolicy(.9,float("nan"),.5)

def test_source_native_integer_ticks_required():
    with pytest.raises(SourceClockError):MarkedRenewalState().observe(NativeQuote(E,0,1800.2,1800.5))
