"""MICRO180 V16: independent full-population R9-to-real-quote entry bridge.

Train on ORIGINAL R9 SYNTH entry events joined offline to REAL Coinexx
TickLogger quote-clock features. Unlike V13/V15, does not select winners.
At inference it NEVER reads teacher timestamps/outcomes. Model decisions on the
FIRST received quote of each second schedule execution on the first quote of
NEXT second, at its observed BUY Ask / SELL Bid. State/stop/rearm is the frozen
V14/V15 independent research harness; no live MT5 orders.
"""
from __future__ import annotations
from datetime import datetime,timezone
from dataclasses import replace
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
import csv,gzip,hashlib,math
import numpy as np
from v14_causal_synthetic_wave_entry import (
    CausalSyntheticWaveEntry, Quote, EntryState, first_passage_probability)

MERGED_SHA='9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5'
FEATURE_NAMES=(
  'second','side','hour','spread_cents','atr_cents','barrier_margin_cents',
  'minute_displacement_cents','signed_ret3','signed_ret10','signed_ret30',
  'signed_ret60','signed_ret180','signed_ret300','eff10','eff30',
  'sigma_1s','signed_kalman_velocity','latent_barrier_margin','touch_forecast',
  'observed_minute_higap','observed_minute_logap','prior_m1_close_slope',
  'prior_5m_displacement','prior_m1_range','minute_observed_quote_count',
  'clock_log_rate','minute_extrema_asymmetry',
)

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def all_teacher_targets(merged:Path)->dict:
    if sha256(merged)!=MERGED_SHA:
        raise ValueError('R9 merged reference SHA-256 mismatch: immutable source required')
    out={};count=[0,0]
    with gzip.open(merged,'rt',newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sec=int(datetime.fromisoformat(r['entry_time_broker']).replace(tzinfo=timezone.utc).timestamp())
            leg=int(r['leg']);side=1 if r['side'].lower()=='buy' else -1
            minute=sec//60
            key=(minute,leg)
            if key in out:raise ValueError('Ambiguous original R9 minute/leg target')
            out[key]={'minute':minute,'leg':leg,'side':side,'teacher_second':sec,
                      'mapped_ms':int(r['equote_ms']),'price_cents':int(r['q_entry_u'])}
            count[leg-1]+=1
    if count!=[192487,79865]:raise ValueError(f'Unexpected complete R9 entry counts: {count}')
    return out

def clock_priors(targets:dict, train_months=('2026-01','2026-02','2026-03','2026-04')) ->dict:
    counts={k:np.ones(60,dtype=np.float64)*0.5 for k in [(1,1),(1,-1),(2,1),(2,-1)]}
    months=set(train_months)
    for t in targets.values():
        month=datetime.fromtimestamp(t['teacher_second'],timezone.utc).strftime('%Y-%m')
        if month in months:counts[t['leg'],t['side']][t['teacher_second']%60]+=1
    priors={}
    for leg in (1,2):
        both=counts[leg,1]+counts[leg,-1]
        priors['first' if leg==1 else 'second']=(both/both.sum()).tolist()
        for side in (-1,1):priors[f'{leg}_{side}']=(counts[leg,side]/counts[leg,side].sum()).tolist()
    return priors

class V16CausalBridge(CausalSyntheticWaveEntry):
    def __init__(self,priors,first_model=None,second_model=None,*,threshold=0.50,
                 require_touch_gate=False):
        super().__init__({'first':priors['first'],'second':priors['second']},
                         shadow=False,score_threshold=threshold,
                         require_touch_gate=require_touch_gate)
        self.side_clock=priors
        self.models={1:first_model,2:second_model}
        self.decision_log=[]
        self.feature_only=False

    def _past(self,sec:int,span:int):
        return self._observed(sec,span)

    def _eff(self,span:int)->float:
        arr=list(self.closed_seconds)[-(span+1):]
        if len(arr)<max(5,span//2):return 0.0
        travel=sum(abs(arr[j][1]-arr[j-1][1]) for j in range(1,len(arr)))
        return abs(arr[-1][1]-arr[0][1])/(travel+1e-9)

    def features(self,q:Quote,leg:int,side:int)->np.ndarray:
        sec=q.second;age=sec%60;mid=q.mid
        prior=self.side_clock[f'{leg}_{side}'][age]
        prev={k:self._past(sec,k) for k in (3,10,30,60,180,300)}
        rets=[side*(mid-(prev[k] if prev[k] is not None else mid))
              for k in (3,10,30,60,180,300)]
        sigma=self._sigma();vel=side*self.filter.vel
        execprice=q.ask_cents if side==1 else q.bid_cents
        barrier=self.minute_start_mid+side*15
        barrier_margin=side*(execprice-barrier)
        latent=float(self.filter.pos if self.filter.pos is not None else mid)
        latent_margin=side*(latent+side*q.spread/2-barrier)
        p_touch=first_passage_probability(max(0.,-latent_margin),vel,sigma,max(1,59-age))
        last=self.closed_m1[-1] if self.closed_m1 else None
        prevm1=self.closed_m1[-2] if len(self.closed_m1)>1 else None
        slope=side*(last[3]-prevm1[3]) if last and prevm1 else 0.
        m5=side*(last[3]-self.closed_m1[0][0]) if len(self.closed_m1)>=5 else 0.
        m1_range=(last[1]-last[2]) if last else 0.
        up=max(0.,self.m1_high-self.minute_start_mid)
        down=max(0.,self.minute_start_mid-self.m1_low)
        asym=side*(up-down)/(up+down+max(1.,sigma))
        return np.asarray((
          age,side,(sec//3600)%24,q.spread,
          q.completed_m5_atr_cents or 0.,barrier_margin,
          side*(mid-self.minute_start_mid),*rets,
          self._eff(10),self._eff(30),sigma,vel,latent_margin,p_touch,
          side*(mid-self.m1_high),side*(mid-self.m1_low),
          slope,m5,m1_range,math.log1p(self.minute_tick_count),
          math.log(max(1e-8,60*prior)),asym
        ),dtype=np.float32)

    def _score(self,q:Quote,leg:int,side:int)->EntryState:
        x=self.features(q,leg,side)
        model=self.models[leg]
        if model is None:score=0.0
        else:score=float(model.predict(x.reshape(1,-1),num_threads=1)[0])
        return EntryState(q.time_msc,q.minute,q.second%60,leg,side,
                          self.side_clock[f'{leg}_{side}'][q.second%60],
                          0.,'causal_latent_path',
                          float(x[8]),float(x[10]),float(x[12]),float(x[16]),
                          float(x[21]),float(-x[5]),float(x[18]),q.spread,
                          q.completed_m5_atr_cents,score)

    def observe(self,q:Quote)->list:
        # Entry model reads only its own historical quote-state, not the target map.
        return self.on_quote(replace(q,session_m5_atr_floor_cents=1e99) if self.feature_only else q)


def cents(value:str)->int:
    return int((Decimal(value)*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
