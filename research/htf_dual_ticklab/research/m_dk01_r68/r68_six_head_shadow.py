"""Frozen six-head Python shadow decision adapter — no MT5 orders, no hindsight inference.
The actual LightGBM original source model files are archived separately and SHA pinned.
A 25s decision is valid ONLY for an intent that has never been submitted.
"""
import hashlib
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import lightgbm as lgb

FROZEN_MODELS=[
("r49_cx_bad","R49_coinexx_JAN60_TRAIN_JAN20_CAL_BAD_MODEL.txt","9136900d09f5b7c88350fd1f8bf7825d02a99f6b5e06c99b6e3527cce84604bd",.9718667268753052),
("r49_dk_tri","R49_dukascopy_JAN60_TRAIN_JAN20_CAL_3CLASS_MODEL.txt","75f67517adb51f71188407057149a7ee4066bc48c420cd6a39730e8bd2f94def",.9738302230834961),
("r61_cx","R61_coinexx_01_bad_1023.txt","18d1da0bb91498bb7481de7a5203aa31205cafecad65b4431945ff0becacc890",.9657679504539772),
("r64_dk","R64_DUKASCOPY_JAN60_BAD_1023_70.txt","49b44df4deebcfc3a940be591bba2c3215594cfb174c021b6e1ec95f179842bb",.9652514532328956),
("r65_cx_good","R65_coinexx_guardian.txt","bf7be6d032503e366b7d7f066ba33196da0712ba984adc12f1eff15657c8e5d4",.9352894183913729),
("r65_dk_good","R65_dukascopy_guardian.txt","0ad434f1a0e400244d6c1228cc5f76cfd8bd9ee501a4f4b7c5cd5180dbedfa9d",.9389653578059575),
]

@dataclass(frozen=True)
class Decision:
    action:str
    votes:int
    reason:str

def file_sha256(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

class SixHeadShadow:
    def __init__(self,r49_dir,r61_dir,r64_dir):
        dirs=[Path(r49_dir)]*2+[Path(r61_dir)]+[Path(r64_dir)]*3
        self.models=[]
        for (name,fn,sha,cut),parent in zip(FROZEN_MODELS,dirs):
            path=parent/fn
            if file_sha256(path)!=sha:raise ValueError("frozen source SHA mismatch: "+name)
            m=lgb.Booster(model_file=str(path))
            if m.num_feature()!=283:raise ValueError("expected 283 source-native features")
            self.models.append((m,cut))
    def votes(self,X):
        X=np.asarray(X,dtype=np.float32)
        if X.ndim!=2 or X.shape[1]!=283 or not np.isfinite(X).all():
            raise ValueError("invalid as-of 283-feature array")
        p=[np.asarray(m.predict(X,num_threads=1)) for m,_ in self.models]
        scores=[
            p[0].astype(np.float32),
            (p[1][:,1]+p[1][:,2]).astype(np.float32),
            p[2].astype(np.float32),
            p[3].astype(np.float32),
            np.clip(p[2],1e-8,1)*(1-.90*np.clip(p[4],1e-8,1)),
            np.clip(p[3],1e-8,1)*(1-.90*np.clip(p[5],1e-8,1)),
        ]
        return np.column_stack([s>=cut for s,(_,cut) in zip(scores,self.models)]).sum(axis=1)
    def decide(self,*,t0_ms,quote25_ms,now_ms,feature_watermark_ms,side,features,ever_submitted,source15_20_ok):
        if ever_submitted:return Decision("ABSTAIN",0,"previously submitted order")
        if side not in (-1,1):return Decision("ABSTAIN",0,"invalid original side")
        if quote25_ms is None or not (t0_ms+25000<=quote25_ms<t0_ms+26000):
            return Decision("ABSTAIN",0,"no actual t0+25..26s native quote")
        if not source15_20_ok:return Decision("ABSTAIN",0,"missing original 15s/20s quote")
        if feature_watermark_ms>quote25_ms or quote25_ms>now_ms:
            return Decision("ABSTAIN",0,"future data watermark")
        if features is None:return Decision("ABSTAIN",0,"missing source features")
        x=np.asarray(features,dtype=np.float32)
        if x.shape!=(283,) or not np.isfinite(x).all():
            return Decision("ABSTAIN",0,"missing or corrupted source state")
        v=int(self.votes(x.reshape(1,-1))[0])
        return Decision("VETO_SHADOW" if v>=2 else "PASS_SHADOW",v,"research-only shadow output; no OrderSend")
