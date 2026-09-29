"""BETA031 standalone numeric manifest inference, no sklearn/LightGBM dependency.
Research-only numerical formula, NOT an MQL5 trading EA or broker execution.
Requires causal 59 input features, per-event regime and milliseconds already built.
"""
import json
import numpy as np

class DurationOwner:
    def __init__(self,manifest):
        self.cfg=manifest if isinstance(manifest,dict) else json.load(open(manifest))
        c=self.cfg
        assert c['feature_count']==63
        self.mu=np.asarray(c['scaler_mean'],dtype=np.float64)
        self.sigma=np.asarray(c['scaler_scale'],dtype=np.float64)
        assert np.all(self.sigma>0)
        self.duration={int(i):np.asarray(v,dtype=np.float64) for i,v in c['duration_sorted_seconds'].items()}

    @staticmethod
    def age_event_clock(t_ms,state):
        t=np.asarray(t_ms,dtype=np.int64)
        s=np.asarray(state,dtype=np.int8)
        age=np.zeros(len(t),dtype=np.float64)
        gap=np.zeros(len(t),dtype=np.float64)
        changed=np.zeros(len(t),dtype=bool)
        if not len(t):return age,gap,changed
        start=t[0]
        for i in range(1,len(t)):
            gap[i]=max(0.,(t[i]-t[i-1])/1000.)
            if s[i]!=s[i-1] or gap[i]>180:
                start=t[i];changed[i]=True
            age[i]=max(0.,(t[i]-start)/1000.)
        return age,gap,changed

    def score(self,X59,t_ms,state):
        X=np.nan_to_num(np.asarray(X59,dtype=np.float64),nan=0.,posinf=20.,neginf=-20.)
        X=np.clip(X,-20,20)
        age,gap,changed=self.age_event_clock(t_ms,state)
        state=np.asarray(state,dtype=np.int8)
        sv=np.zeros(len(age),dtype=np.float64)
        for i,arr in self.duration.items():
            k=(state==i)
            if len(arr)<5:sv[k]=0.5
            else:
                idx=np.searchsorted(arr,age[k],side='left')
                sv[k]=np.clip((len(arr)-idx)/len(arr),0.05,1.)
        D=np.column_stack((np.log1p(age),np.log1p(np.minimum(gap,180)),changed.astype(float),sv))
        Z=(np.column_stack((X,D))-self.mu)/self.sigma
        g=self.cfg['global']
        global_score=Z@np.asarray(g['coef'])+g['intercept']
        state_score=np.zeros(len(global_score),dtype=np.float64)
        for i in range(4):
            k=(state==i)
            e=self.cfg['states'][str(i)]
            state_score[k]=Z[k]@np.asarray(e['coef'])+e['intercept']
        weight=np.clip(0.10+0.65*sv-0.35*changed.astype(float),0.05,0.75)
        return (1-weight)*global_score+weight*state_score

    def inverse_side(self,X59,t_ms,state):
        return self.score(X59,t_ms,state)>self.cfg['selected_threshold']
