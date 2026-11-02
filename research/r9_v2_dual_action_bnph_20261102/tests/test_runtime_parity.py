import sys,zipfile,io
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from live_dual_router import ExactQuoteState,DualObservedRouter
from source_exact import load
from router_v2_dataset import iter_ticks
from router_v2_features import Quote

def test_runtime_dual_wait_when_no_policy():
    rr=DualObservedRouter()
    for i in range(12000):
        rr.on_quote(Quote(i*250,100+.02*np.sin(i*.1),100.2+.02*np.sin(i*.1)))
    assert rr.count['decision_events']>0 and rr.count['selected_research_actions']==0

def test_causal_quote_feature_prefix_equals_original_offline_source():
    # Full original exact source, not a paraphrase. First 30 baseline timestamps.
    d=load('coinexx','01')
    p='/mnt/data/v2_direction_audit/R9_V2_PAIRED_ACTION_COINEXX_2026_01_FULL_CHECKPOINT.zip'
    with zipfile.ZipFile(p) as z:
        with np.load(io.BytesIO(z.read('results/coinexx_01_paired_counterfactual.npz'))) as lab:
            idx=lab['matched'][:30]
    ticks='/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz'
    state=ExactQuoteState()
    checkpoints={int(i):j for j,i in enumerate(idx)}
    largest=int(idx[-1]);hit=0
    for k,q in enumerate(iter_ticks(ticks,'coinexx')):
        if k>largest:break
        state.append(q)
        if k in checkpoints:
            j=checkpoints[k]
            actual=state.vector(float(d['X'][j,6]),float(d['X'][j,7]))
            np.testing.assert_allclose(actual,d['X'][j],atol=2.e-3,rtol=4.e-4)
            hit+=1
    assert hit==30

def test_frozen_real_model_scores_both_but_remains_fail_closed():
    from live_dual_router import FrozenDualPolicy
    root=Path(__file__).resolve().parents[1]
    p=FrozenDualPolicy(root/'models/coinexx_01_triple_action.txt',
                       root/'models/coinexx_01_policy_data.npz')
    x=load('coinexx','01')['X'][10]
    bb,ss=p.evaluate(x)
    assert bb.side==1 and ss.side==-1
    assert 0<=bb.p_correct<=1 and 0<=ss.p_correct<=1
    assert p.action(x,0.2)==(0,'FAIL_CLOSED_RESEARCH_ONLY')
