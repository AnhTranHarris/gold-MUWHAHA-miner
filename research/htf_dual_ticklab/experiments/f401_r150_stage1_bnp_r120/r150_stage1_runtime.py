"""F401-R150 Stage1 — causal multi-clock conditioned research-only T1 expert.

NOT the final R150. Keeps independent R120 regime and J/L/M family signals,
with held-back February group thresholds. No original truth, teacher, matured
class, order state derived from hindsight, or future quote enters inference.
N2 is deliberately a separate still-unsubmitted T2 module.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,math
from pathlib import Path
from typing import Mapping
import numpy as np
import joblib

PINS={
 'J2':'11d1d3c995e750cf69b53c578bbaacf1f12879e999bb8372eb2dd6e43f4fc71a',
 'L2':'4744d8b99748d0324d85ca2d42b4e631bf6b7fff8956f3bc7343e0c4067cb971',
 'M2':'e716762a77c33b7726d48d1b683e01d9073991f6492d8e65e46fe67244b2d4e5',
 'R120':'6deefed410ec1946741c88b21252c103347d2e1ae7f4617e4788dbb54211418f'}
HEADS=('guardian','opposite','neutral')

@dataclass(frozen=True)
class Phase:
    index:int
    asof_ms:int
    source_sha256:str

@dataclass(frozen=True)
class Specialist:
    guardian:float
    opposite:float
    neutral:float
    asof_ms:int
    archive_sha256:str
    valid:bool=True

@dataclass(frozen=True)
class NativeDecision:
    t0_ms:int
    t1_ms:int
    side:int
    pending:bool
    native_quote_found:bool

@dataclass(frozen=True)
class ShadowDecision:
    action:str
    reason:str
    scores:dict[str,float]|None=None
    proposed_class:str|None=None

class Stage1RegimeExpert:
    """Source-gated score-only DK probe; not a ready whole-system veto."""
    def __init__(self, directory:Path):
        directory=Path(directory)
        cfg=json.loads((directory/'stage1_frozen.json').read_text())
        if cfg.get('broker')!='dukascopy' or cfg.get('status')!='RESEARCH_ONLY_UNAPPROVED':
            raise ValueError('unrecognized model bundle')
        if cfg['parents']!=PINS or cfg['clock']!='T1' or cfg.get('orders_authorized') is not False:
            raise ValueError('invalid source or clock configuration')
        self.cuts=cfg['cuts'];self.models={}
        for head in HEADS:
            fn=directory/cfg['model_files'][head]
            if hashlib.sha256(fn.read_bytes()).hexdigest()!=cfg['model_sha256'][head]:
                raise ValueError('frozen model bytes changed')
            self.models[head]=joblib.load(fn)
    def _score_t1_with_proof(self, *, proof:NativeDecision, phase:Phase,
                 families:Mapping[str,Specialist])->ShadowDecision:
        def stop(reason):return ShadowDecision('ABSTAIN',reason)
        if not isinstance(proof,NativeDecision) or not proof.native_quote_found or not proof.pending:
            return stop('no genuine pending T1 decision')
        if not (proof.t0_ms+15000<=proof.t1_ms<proof.t0_ms+16000) or proof.side not in (-1,1):
            return stop('invalid quote decision clock or side')
        if not isinstance(phase,Phase) or not(0<=phase.index<24) or phase.asof_ms>proof.t0_ms or phase.source_sha256!=PINS['R120']:
            return stop('missing/invalid original R120 pre-t0 market phase')
        if set(families)!=set(('J2','L2','M2')):return stop('T1 requires J/L/M only: N2 forbidden')
        raw=[]
        for f in ('J2','L2','M2'):
            v=families[f]
            if not v.valid or v.archive_sha256!=PINS[f] or v.asof_ms>=proof.t1_ms:
                return stop('unfrozen or future family score')
            vals=(v.guardian,v.opposite,v.neutral)
            if not all(math.isfinite(z) and 0<=z<=1 for z in vals):
                return stop('invalid class specialist probabilities')
            raw.extend(vals)
        z=np.array(raw,dtype=np.float32).reshape(3,3)
        hour=(proof.t0_ms//3_600_000)%24
        x=np.concatenate((z.ravel(),z.std(axis=0),
                          [proof.side,float(np.sin(2*np.pi*np.float32(hour)/24)),float(np.cos(2*np.pi*np.float32(hour)/24)),phase.index])).astype(np.float32).reshape(1,16)
        # Guardian model is the original frozen scores-only P2 control;
        # only opposite/neutral heads consume the new R120 regime column.
        scores={h:float(self.models[h].predict_proba(x[:,:15] if h=='guardian' else x)[:,1][0]) for h in HEADS}
        session='13_15' if 13<=hour<15 else 'other'
        group=f'{proof.side}|{session}'
        cut=self.cuts.get(group)
        if cut is None:return stop('Feb class-risk calibration group missing')
        if scores['guardian']>=cut['guardian_floor']:
            return ShadowDecision('PROTECT','independent CORRECT guardian',scores)
        if scores['opposite']>cut['opposite'] or scores['neutral']>cut['neutral']:
            o=scores['opposite']>cut['opposite'];n=scores['neutral']>cut['neutral']
            return ShadowDecision('SHADOW_VETO','February-frozen class-specific risk cap',scores,
                                  'BOTH' if o and n else 'OPPOSITE' if o else 'NEUTRAL')
        return ShadowDecision('PROTECT','insufficient risk evidence',scores)

    def score_native(self, *, t0_ms:int, side:int, ordinal:int,
                     quote_t_ms:np.ndarray, quote_bid:np.ndarray, quote_ask:np.ndarray,
                     intent_lifecycle:Mapping[str,int], phase:Phase,
                     families:Mapping[str,Specialist])->ShadowDecision:
        """Only public decision ingress: independently derive real quote and intent clock.

        Family scores/phase require the already frozen source publishers. Source
        archive checks are provenance pins, not proof of the market feed itself.
        """
        from r150lean.runtime import independently_prove_t1
        p=independently_prove_t1(t0_ms=t0_ms,side=side,original_ordinal=ordinal,
                                native_time_ms=quote_t_ms,bid=quote_bid,ask=quote_ask,
                                lifecycle=intent_lifecycle)
        proof=NativeDecision(int(p.t0_ms),int(p.t1_ms),int(p.side),bool(p.pending),bool(p.native_quote_found))
        return self._score_t1_with_proof(proof=proof,phase=phase,families=families)
