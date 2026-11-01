"""Stage 2A CCC: freeze strict source roots; never alter original submitted orders."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import hashlib,json,math
import numpy as np

# No class, teacher or matured label may be supplied by a realtime model score caller.
FAMILY_KEYS=('J2','L2','M2')

@dataclass(frozen=True)
class ActionClock:
    broker:str
    t0_ms:int
    t1_ms:int
    side:int
    ordinal:int
    pending:bool
    has_native_t1:bool
    original_q_veto:bool
    source_root_attested:bool
    family_hashes:Mapping[str,str]

@dataclass(frozen=True)
class CCCDecision:
    action:str
    score:float|None
    reason:str
    clock:str='T1'

class Stage2ACCC:
    """Independent three-expert teacher-free T0; failed contracts abstain.

    Causal features: source-native market only. Offline truth is inaccessible.
    A Stage2A rescue is research-only and applies only to *still-unsubmitted*
    intentions already vetoed by a separately certified source-clean R150Q.
    """
    def __init__(self,model_dir:Path):
        import joblib
        self.root=Path(model_dir)
        self.config=json.loads((self.root/'config.json').read_text())
        c=self.config
        if (c.get('status')!='RESEARCH_ONLY_UNAPPROVED' or
            c.get('orders_authorized') is not False or c.get('clock')!='T1' or
            c.get('runtime_teacher_free') is not True or
            c.get('q_source_exact') is not True):
            raise ValueError('ineligible model bundle or missing exact Q proof')
        if set(c['models'])!={'continuation','reliability','hard_negative'}:
            raise ValueError('three independent CCC experts required')
        self.models={}
        for key,name in c['models'].items():
            p=self.root/name
            if hashlib.sha256(p.read_bytes()).hexdigest()!=c['model_sha256'][key]:
                raise ValueError('model integrity failure')
            self.models[key]=joblib.load(p)
        self.threshold=float(c['rescue_cut'])
        self.min_expert=float(c['min_expert'])
        self.n_features=int(c['feature_count'])

    def score(self,*,clock:ActionClock,features:np.ndarray)->CCCDecision:
        def abstain(reason):return CCCDecision('ABSTAIN',None,reason)
        c=self.config
        if clock.broker!=c['broker'] or clock.side not in (-1,1):return abstain('broker or side invalid')
        if not(clock.pending and clock.has_native_t1 and clock.original_q_veto and clock.source_root_attested):
            return abstain('no certified unsubmitted original-Q-veto T1')
        if not(clock.t0_ms+15000<=clock.t1_ms<clock.t0_ms+16000):return abstain('T1 violation')
        if set(clock.family_hashes)!=set(FAMILY_KEYS):return abstain('family score root missing')
        if any(clock.family_hashes[k]!=c['family_archive_sha256'][k] for k in FAMILY_KEYS):
            return abstain('frozen family source mismatch')
        x=np.asarray(features,dtype=np.float32)
        if x.ndim!=1 or len(x)!=self.n_features or not np.isfinite(x).all():
            return abstain('malformed source market state')
        probs=[]
        for k in ('continuation','reliability','hard_negative'):
            p=float(self.models[k].predict_proba(x[None,:])[0,1]);
            if not math.isfinite(p) or not 0<=p<=1:return abstain('invalid posterior')
            probs.append(p)
        # Lower-envelope selective consensus, not a universal BAD-score average.
        mean=float(np.mean(probs));minimum=min(probs);spread=max(probs)-min(probs)
        if spread>float(c['max_disagreement']):return abstain('expert disagreement / OOD')
        if minimum<self.min_expert:return CCCDecision('PROTECT',minimum,'insufficient corroboration')
        if minimum>=self.threshold:
            return CCCDecision('RESCUE_RESEARCH_ONLY',minimum,'three-expert CCC; NOT an executable original t0 cancellation')
        return CCCDecision('PROTECT',minimum,'below frozen high-precision threshold')
