"""Lean R150 T1 research classifier: frozen specialist consensus + FEB risk cuts.

This code does not cancel original t0 orders, submit orders, or certify a live
emitter. It only rates independently pending shadow intents with true native T1.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import json, math
import numpy as np

@dataclass(frozen=True)
class FamilyScore:
    guardian:float
    opposite:float
    neutral:float
    asof_ms:int
    archive_sha256:str

@dataclass(frozen=True)
class NativeT1:
    t0_ms:int
    t1_ms:int
    side:int
    original_ordinal:int
    pending:bool
    native_quote_found:bool
    reason:str

@dataclass(frozen=True)
class Decision:
    action:str
    reason:str
    clock:str
    score_guardian:float|None=None
    score_opposite:float|None=None
    score_neutral:float|None=None
    proposed_class:str|None=None

TERMINAL=('submitted_ms','filled_ms','cancelled_ms','expired_ms')

def independently_prove_t1(*,t0_ms:int,side:int,original_ordinal:int,
                             native_time_ms:np.ndarray,bid:np.ndarray,ask:np.ndarray,
                             lifecycle:Mapping[str,int])->NativeT1:
    """Find first real quote in [t0+15s,t0+16s), prove independent intent state.

    This validates supplied source values, not the external provenance of the
    native tick logger or lifecycle writer. Supply trusted broker feed sources.
    """
    def fail(reason,t1=-1,quote=False):
        return NativeT1(int(t0_ms),int(t1),int(side),int(original_ordinal),False,quote,reason)
    if side not in (-1,1) or original_ordinal<0:return fail('invalid source identity')
    t=np.asarray(native_time_ms);b=np.asarray(bid);a=np.asarray(ask)
    if (t.ndim!=1 or len(t)==0 or not np.issubdtype(t.dtype,np.integer) or
        b.shape!=t.shape or a.shape!=t.shape or np.any(np.diff(t)<0) or
        not np.isfinite(b).all() or not np.isfinite(a).all() or
        np.any(b<=0) or np.any(a<b)):
        return fail('native quotes invalid or absent')
    i=int(np.searchsorted(t,t0_ms+15000,side='left'))
    if i==len(t) or int(t[i])>=t0_ms+16000:return fail('no real native T1 quote')
    t1=int(t[i])
    if not {'created_ms','t0_ms','side','ordinal',*TERMINAL}.issubset(lifecycle):return fail('independent intent ledger absent',t1,True)
    if (int(lifecycle['t0_ms'])!=t0_ms or int(lifecycle['side'])!=side or
        int(lifecycle['ordinal'])!=original_ordinal):
        return fail('shadow intent/source identity mismatch',t1,True)
    created=int(lifecycle['created_ms'])
    if not (t0_ms<=created<=t1):return fail('intent not created by T1',t1,True)
    for field in TERMINAL:
        v=int(lifecycle[field])
        if v!=-1 and v<=t1:return fail('intent no longer pending at T1',t1,True)
    return NativeT1(int(t0_ms),t1,int(side),int(original_ordinal),True,True,'verified independent pending T1')

class R150Filter:
    """Broker-specific, research-only lean consensus; no fitted P2 runtime bloat."""
    def __init__(self,root:Path,broker:str):
        root=Path(root);self.broker=broker
        if broker not in ('coinexx','dukascopy'):raise ValueError('unknown broker')
        cfg=json.loads((root/'config.json').read_text())
        if (cfg.get('status')!='RESEARCH_ONLY_UNAPPROVED' or cfg.get('clock')!='T1' or
            cfg.get('broker')!=broker or cfg.get('variant')!='raw_jlm' or
            cfg.get('orders_authorized') is not False):
            raise ValueError('incompatible or unauthorized model bundle')
        self.cuts=cfg['cuts'];self.pins=cfg['family_archive_sha256']
    def decide(self,*,family:Mapping[str,FamilyScore],proof:NativeT1)->Decision:
        def abstain(s):return Decision('ABSTAIN',s,'T1')
        if not isinstance(proof,NativeT1) or not proof.native_quote_found or not proof.pending:
            return abstain('no independently pending, native T1 action')
        if not (proof.t0_ms+15000<=proof.t1_ms<proof.t0_ms+16000):return abstain('T1 clock violation')
        if proof.side not in (-1,1):return abstain('invalid side')
        if set(family)!=set(('J2','L2','M2')):return abstain('J2/L2/M2 required; N2 forbidden at T1')
        for k,v in family.items():
            vals=(v.guardian,v.opposite,v.neutral)
            if not all(math.isfinite(float(x)) and 0<=float(x)<=1 for x in vals):return abstain('invalid family probability')
            if v.archive_sha256!=self.pins[k]:return abstain('frozen family archive pin mismatch')
            if v.asof_ms>=proof.t1_ms:return abstain('future family as-of time')
        s={h:float(np.mean([getattr(family[f],h) for f in ('J2','L2','M2')]))
           for h in ('guardian','opposite','neutral')}
        hour=(proof.t1_ms//3600000)%24
        session='ny_neutral_13_15' if 13<=hour<15 else 'other'
        cut=self.cuts.get(f'{proof.side}|{session}')
        if cut is None:return abstain('unsupported FEB calibration group')
        kwargs=dict(score_guardian=s['guardian'],score_opposite=s['opposite'],score_neutral=s['neutral'])
        if s['guardian']>=cut['guardian_floor']:
            return Decision('PROTECT','guardian correct-risk protection','T1',**kwargs)
        o=s['opposite']>cut['opposite_cut'];n=s['neutral']>cut['neutral_cut']
        if o or n:
            return Decision('SHADOW_VETO','February-frozen original-class cutoff','T1',
                            proposed_class='BOTH' if o and n else 'OPPOSITE' if o else 'NEUTRAL',**kwargs)
        return Decision('PROTECT','class veto evidence below frozen cut','T1',**kwargs)
