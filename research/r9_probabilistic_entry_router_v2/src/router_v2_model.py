#!/usr/bin/env python3
"""Bayesian + Neyman-Pearson BUY/SELL/WAIT router for R9 Entry Router v2.

The model is intentionally transparent and exportable to MQL5 later:
- quantile-binned Bayesian likelihoods for FAVORABLE / ADVERSE / TIMEOUT;
- context priors by side, session and dominant latent market state;
- SYNTH teacher can only weakly upweight already favorable REAL examples;
- regime/context-specific NP thresholds are calibrated on REAL bad outcomes;
- final action is BUY/SELL/WAIT by positive expected utility, never forced trade.
"""
from __future__ import annotations
import collections
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

CLASSES=('FAVORABLE','ADVERSE','TIMEOUT')
HORIZONS_MS=(1000,3000,5000,10000,15000,30000)
BARRIERS=('0.10','0.30','0.50')
TEACHER_WEIGHT_MAX=.10


def _softmax(logs:Dict[str,float])->Dict[str,float]:
    m=max(logs.values()); ex={k:math.exp(min(60.,v-m)) for k,v in logs.items()}; s=sum(ex.values()) or 1.
    return {k:v/s for k,v in ex.items()}


def _quantile(sorted_vals:Sequence[float],q:float)->float:
    if not sorted_vals:return 0.
    if len(sorted_vals)==1:return sorted_vals[0]
    pos=(len(sorted_vals)-1)*q;lo=int(math.floor(pos));hi=int(math.ceil(pos))
    if lo==hi:return sorted_vals[lo]
    w=pos-lo;return sorted_vals[lo]*(1-w)+sorted_vals[hi]*w


def _bin(x:float,edges:Sequence[float])->int:
    return sum(x>e for e in edges)


def binomial_tail(n:int,p:float,k:int)->float:
    if k<=0:return 1.
    if k>n:return 0.
    logs=[math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1)+j*math.log(p)+(n-j)*math.log1p(-p) for j in range(k,n+1)]
    m=max(logs);return min(1.,math.exp(m)*sum(math.exp(x-m) for x in logs))


def np_order_threshold(negative_scores:Sequence[float],alpha:float,delta:float=.05,min_neg:int=80)->Optional[float]:
    scores=sorted(map(float,negative_scores));n=len(scores)
    if n<min_neg:return None
    lo,hi=1,n+1
    while lo<hi:
        k=(lo+hi)//2
        if binomial_tail(n,1-alpha,k)<=delta:hi=k
        else:lo=k+1
    if lo>n:return None
    return scores[lo-1]


def dominant_state(f:Dict[str,float])->str:
    states=[(k[6:],v) for k,v in f.items() if k.startswith('state_')]
    return max(states,key=lambda kv:kv[1])[0] if states else 'unknown'


def session_name(f:Dict[str,float])->str:
    ss=[(k[8:],v) for k,v in f.items() if k.startswith('session_') and k!='session_code']
    return max(ss,key=lambda kv:kv[1])[0] if ss else 'off'


def context_key(f:Dict[str,float])->Tuple[int,str,str]:
    return int(round(f.get('side',0))),session_name(f),dominant_state(f)



class BayesianBarrierBank:
    """Auxiliary multi-horizon first-passage probabilities using the parent bins.

    Predicts P(+barrier before adverse stop by horizon) and P(adverse stop by horizon).
    This is entry-time foresight; target timestamps are only offline training labels.
    """
    def __init__(self,feature_names,edges,n_bins=5,temper=.12):
        self.feature_names=list(feature_names);self.edges=edges;self.n_bins=n_bins;self.temper=temper
        self.counts=collections.defaultdict(lambda:[0.,0.])
        self.tables=collections.defaultdict(lambda:[collections.defaultdict(lambda:[0.]*n_bins),collections.defaultdict(lambda:[0.]*n_bins)])
        self.fitted=False

    def _labels(self,e):
        entry=int(e.get('entry_ms',0) or 0);stop=e.get('adverse_stop_ms')
        stop=int(stop) if stop not in (None,'','None') else None
        out={}
        for h in HORIZONS_MS:
            out[f'adverse_{h}']=int(stop is not None and stop-entry<=h)
            for b in BARRIERS:
                t=e.get('target_'+b.replace('.','')+'_ms')
                t=int(t) if t not in (None,'','None') else None
                out[f'fav_{b}_{h}']=int(t is not None and t-entry<=h and (stop is None or t<stop))
        return out

    def fit(self,examples):
        for e in examples:
            labels=self._labels(e);f=e['features'];tw=1.0+(TEACHER_WEIGHT_MAX if int(e.get('teacher',0)) else 0.0)
            for key,y in labels.items():
                # Teacher may only weakly reinforce favorable REAL paths, never adverse/negative labels.
                w=tw if y==1 and key.startswith('fav_') else 1.0
                self.counts[key][y]+=w
                for n in self.feature_names:
                    b=_bin(float(f.get(n,0.0)),self.edges[n]);self.tables[key][y][n][b]+=w
        self.fitted=True;return self

    def probability(self,key,f):
        if not self.fitted:return 0.0
        c0,c1=self.counts[key];total=c0+c1
        if total<=0:return 0.0
        logs=[]
        for y,c in ((0,c0),(1,c1)):
            lp=math.log((c+2)/(total+4))
            denom=c+2*self.n_bins;acc=0.
            for n in self.feature_names:
                b=_bin(float(f.get(n,0.0)),self.edges[n]);acc+=math.log((self.tables[key][y][n][b]+2)/denom+1e-15)
            logs.append(lp+self.temper*acc)
        m=max(logs);p0=math.exp(logs[0]-m);p1=math.exp(logs[1]-m)
        return p1/(p0+p1)

    def predict(self,f):
        out={}
        for h in HORIZONS_MS:
            out[f'p_adverse_{h}']=self.probability(f'adverse_{h}',f)
            for b in BARRIERS:out[f'p_fav_{b}_{h}']=self.probability(f'fav_{b}_{h}',f)
        return out

@dataclass
class ModelPrediction:
    posterior:Dict[str,float]
    expected_net:float
    cvar_penalty:float
    utility:float
    context:Tuple[int,str,str]
    np_threshold:Optional[float]
    np_pass:bool
    horizons:Dict[str,float]


class BayesianCompetingRiskModel:
    def __init__(self,n_bins:int=5,likelihood_temper:float=.20,tail_lambda:float=.20,
                 np_alpha:float=.10,np_delta:float=.05,min_context:int=40):
        self.n_bins=n_bins;self.likelihood_temper=likelihood_temper;self.tail_lambda=tail_lambda
        self.np_alpha=np_alpha;self.np_delta=np_delta;self.min_context=min_context
        self.feature_names:List[str]=[];self.edges:Dict[str,List[float]]={}
        self.count=collections.Counter();self.feature_counts={c:collections.defaultdict(lambda:[0.]*n_bins) for c in CLASSES}
        self.context_counts=collections.defaultdict(lambda:collections.Counter())
        self.net_by_class=collections.defaultdict(list);self.net_by_context=collections.defaultdict(lambda:collections.defaultdict(list))
        self.np_thresholds={};self.global_np_threshold=None;self.fitted=False;self.calibrated=False;self.barrier_bank=None

    def _prepare_features(self,examples):
        names=sorted(set().union(*(set(e['features']) for e in examples)))
        # Explicitly exclude non-runtime metadata if accidentally present.
        names=[n for n in names if n not in ('teacher','future','label','net','exit_ms')]
        self.feature_names=names
        for n in names:
            vals=sorted(float(e['features'].get(n,0.0)) for e in examples)
            self.edges[n]=[_quantile(vals,q) for q in (0.2,0.4,0.6,0.8)][:self.n_bins-1]

    def fit(self,examples:Sequence[dict],teacher_weight:float=.10):
        if self.fitted:raise ValueError('fit once')
        if not examples:raise ValueError('no examples')
        teacher_weight=min(max(0.,teacher_weight),TEACHER_WEIGHT_MAX)
        self._prepare_features(examples)
        for e in examples:
            c=e['class'];f=e['features'];net=float(e['net']);teacher=int(e.get('teacher',0))
            if c not in CLASSES:raise ValueError('bad class')
            w=1.0+(teacher_weight if c=='FAVORABLE' and teacher else 0.0)
            self.count[c]+=w
            ctx=context_key(f);self.context_counts[ctx][c]+=w
            self.net_by_class[c].append(net);self.net_by_context[ctx][c].append(net)
            for n in self.feature_names:
                b=_bin(float(f.get(n,0.0)),self.edges[n]);self.feature_counts[c][n][b]+=w
        if any(self.count[c]<10 for c in CLASSES):raise ValueError(f'insufficient classes {self.count}')
        self.barrier_bank=BayesianBarrierBank(self.feature_names,self.edges,self.n_bins).fit(examples)
        self.fitted=True;return self

    def _class_prior(self,c:str,ctx)->float:
        local=self.context_counts.get(ctx)
        # hierarchical shrinkage: local context contributes only when sufficiently populated.
        g=sum(self.count.values());global_p=(self.count[c]+2)/(g+2*len(CLASSES))
        if not local:return global_p
        n=sum(local.values());lp=(local[c]+2)/(n+2*len(CLASSES))
        w=n/(n+100.0)
        return (1-w)*global_p+w*lp

    def posterior(self,f:Dict[str,float])->Dict[str,float]:
        if not self.fitted:raise ValueError('unfitted')
        ctx=context_key(f);logs={}
        for c in CLASSES:
            logs[c]=math.log(self._class_prior(c,ctx)+1e-15)
            denom=self.count[c]+2*self.n_bins
            acc=0.
            for n in self.feature_names:
                b=_bin(float(f.get(n,0.0)),self.edges[n])
                acc+=math.log((self.feature_counts[c][n][b]+2)/denom+1e-15)
            logs[c]+=self.likelihood_temper*acc
        return _softmax(logs)

    @staticmethod
    def _mean(xs):return sum(xs)/len(xs) if xs else 0.
    @staticmethod
    def _cvar10(xs):
        if not xs:return 0.
        a=sorted(xs);n=max(1,int(math.ceil(.10*len(a))));return sum(a[:n])/n

    def expected_utility(self,f:Dict[str,float],posterior:Optional[Dict[str,float]]=None)->Tuple[float,float]:
        p=posterior or self.posterior(f);ctx=context_key(f)
        exp=0.
        for c in CLASSES:
            local=self.net_by_context.get(ctx,{}).get(c,[])
            values=local if len(local)>=self.min_context else self.net_by_class[c]
            exp+=p[c]*self._mean(values)
        all_local=[]
        if ctx in self.net_by_context:
            for c in CLASSES:all_local.extend(self.net_by_context[ctx].get(c,[]))
        all_global=[]
        for c in CLASSES:all_global.extend(self.net_by_class[c])
        tail=self._cvar10(all_local if len(all_local)>=self.min_context else all_global)
        penalty=self.tail_lambda*abs(min(0.,tail))*p['ADVERSE']
        # Short-horizon barrier profile nudges the entry decision without replacing the 30s class posterior.
        bonus=0.0
        if self.barrier_bank is not None:
            hp=self.barrier_bank.predict(f)
            bonus=.05*hp.get('p_fav_0.10_5000',0.)+.08*hp.get('p_fav_0.30_15000',0.)-.10*hp.get('p_adverse_5000',0.)
        return exp-penalty+bonus,penalty

    def calibration_score(self,f:Dict[str,float])->float:
        p=self.posterior(f);eu,_=self.expected_utility(f,p)
        # high is good: expected net plus posterior separation.
        return eu + .15*(p['FAVORABLE']-p['ADVERSE'])

    def calibrate_np(self,calibration_examples:Sequence[dict]):
        if not self.fitted:raise ValueError('fit first')
        grouped=collections.defaultdict(list);global_bad=[]
        for e in calibration_examples:
            if float(e['net'])>=0:continue
            score=self.calibration_score(e['features']);ctx=context_key(e['features'])
            grouped[ctx].append(score);global_bad.append(score)
        self.global_np_threshold=np_order_threshold(global_bad,self.np_alpha,self.np_delta,max(80,self.min_context))
        self.np_thresholds={}
        for ctx,scores in grouped.items():
            th=np_order_threshold(scores,self.np_alpha,self.np_delta,max(40,self.min_context))
            if th is not None:self.np_thresholds[ctx]=th
        self.calibrated=self.global_np_threshold is not None
        return self.calibrated

    def predict(self,f:Dict[str,float])->ModelPrediction:
        p=self.posterior(f);eu,pen=self.expected_utility(f,p);ctx=context_key(f)
        th=self.np_thresholds.get(ctx,self.global_np_threshold)
        score=eu+.15*(p['FAVORABLE']-p['ADVERSE'])
        np_pass=bool(self.calibrated and th is not None and score>th)
        horizons=self.barrier_bank.predict(f) if self.barrier_bank is not None else {}
        return ModelPrediction(p,eu,pen,eu,ctx,th,np_pass,horizons)

    def route(self,buy_features:Dict[str,float],sell_features:Dict[str,float],min_utility:float=0.0)->Tuple[str,dict]:
        pb=self.predict(buy_features);ps=self.predict(sell_features)
        choices=[('BUY',pb),('SELL',ps)]
        action,p=max(choices,key=lambda x:x[1].utility)
        if not p.np_pass or p.utility<=min_utility:
            action='WAIT'
        return action,{
            'BUY':pb.__dict__,'SELL':ps.__dict__,'selected':action,
            'selected_utility':0.0 if action=='WAIT' else p.utility,
        }

    def export(self)->dict:
        return {
            'n_bins':self.n_bins,'likelihood_temper':self.likelihood_temper,'tail_lambda':self.tail_lambda,
            'np_alpha':self.np_alpha,'np_delta':self.np_delta,'feature_names':self.feature_names,'edges':self.edges,
            'class_counts':dict(self.count),'np_global':self.global_np_threshold,
            'np_contexts':{'|'.join(map(str,k)):v for k,v in self.np_thresholds.items()},
            'teacher_runtime_feature':False,'teacher_weight_cap':TEACHER_WEIGHT_MAX,
            'fitted':self.fitted,'np_calibrated':self.calibrated,'horizons_ms':HORIZONS_MS,'barriers':BARRIERS,
        }


__all__=['BayesianCompetingRiskModel','BayesianBarrierBank','ModelPrediction','np_order_threshold','context_key','dominant_state','session_name','HORIZONS_MS','BARRIERS']
