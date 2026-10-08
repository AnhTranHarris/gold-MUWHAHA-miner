import json,heapq,datetime as dt
from collections import defaultdict,deque
import numpy as np
import crossmonth_micro_ensemble_133c as M
BASE=M.BASE

def bucket(ts_ms):
    h=int((ts_ms//3600000)%24)
    if h<7:return 0
    if h<13:return 1
    if h<17:return 2
    if h<21:return 3
    return 4

def build_streams(config_idx=3):
    p=M.CONFIGS[config_idx]; gov=M.MicroGov(p); out={}
    for mon,m in [('feb',2),('mar',3)]:
        D=M.N.load_month(m); B=M.load_npz(f'{BASE}/{mon}_baseline_components_133b.npz')
        G=M.learner(mon,D,p,gov,1024)
        np.savez_compressed(f'{BASE}/{mon}_learner_D_stream_133c.npz',E=G[0],X=G[1],R=G[2],D=G[3],P=G[4],H=G[5])
        out[mon]=M.stats(G[4])
    open(f'{BASE}/learner_D_stream_stats_133c.json','w').write(json.dumps(out,indent=2))
    return out

def load_stream(mon):
    z=np.load(f'{BASE}/{mon}_learner_D_stream_133c.npz'); Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q

def pf(a):
    a=np.asarray(a,float);gp=a[a>0].sum();gl=a[a<0].sum();return float(gp/-gl if gl<0 else 999.)

class GateState:
    def __init__(self):
        self.pending=[];self.seq=0;self.g=deque(maxlen=256);self.s=defaultdict(lambda:deque(maxlen=128));self.active=defaultdict(lambda:True)

def gate(Q,t,st,p):
    E,X,R,D,P,H=Q; keep=[]
    for k in range(len(E)):
        now=int(t[E[k]])
        while st.pending and st.pending[0][0]<=now:
            _,_,sess,v=heapq.heappop(st.pending);st.g.append(v);st.s[sess].append(v)
        sess=bucket(now); sh=st.s[sess]; gh=st.g
        hist=sh if len(sh)>=p['min_session'] else gh
        on=st.active[sess]
        if len(hist)>=p['fw']:
            f=np.asarray(list(hist)[-p['fw']:],float); fm=float(f.mean()); fp=pf(f)
            slow=np.asarray(list(hist)[-min(len(hist),p['sw']):],float); sm=float(slow.mean())
            loss=float(np.sum(f[f<0]))
            if on and (fm<p['off_mean'] or fp<p['off_pf'] or loss<p['off_loss'] or sm<p['slow_off']):on=False
            elif (not on) and fm>=p['on_mean'] and fp>=p['on_pf'] and sm>=p['slow_on']:on=True
        st.active[sess]=on
        # shadow outcome always scheduled regardless of funding
        heapq.heappush(st.pending,(int(t[X[k]]),st.seq,sess,float(P[k])));st.seq+=1
        if on:keep.append(k)
    kk=np.asarray(keep,np.int64);return tuple(z[kk] for z in Q),st

def eval_param(p):
    st=GateState();wdstate=None;out={}
    for mon,m in [('feb',2),('mar',3)]:
        D=M.N.load_month(m);B=M.load_npz(f'{BASE}/{mon}_baseline_components_133b.npz');wd,wdstate=M.route_wd(B,D[0],wdstate,703)
        G=load_stream(mon); GG,st=gate(G,D[0],st,p);NAT=M.native(mon);COV=M.q(B,'COV');COLD=M.q(B,'COLD');bench=json.load(open(f'{BASE}/r9_synth_{mon}_daily_weekly.json'))
        Q=M.merge(wd,[NAT,GG,COV,COLD],1024);s=M.score(D,Q,bench)
        out[mon]={'score':s,'gate_stream':M.stats(GG[4]),'raw_stream':M.stats(G[4]),'native':M.stats(NAT[4]),'wd':M.stats(wd[4])}
    return out

PARAMS=[
 dict(name='G1',fw=4,sw=32,min_session=8,off_mean=0.,off_pf=.9,off_loss=-20.,slow_off=-.25,on_mean=.5,on_pf=1.1,slow_on=0.),
 dict(name='G2',fw=8,sw=32,min_session=8,off_mean=0.,off_pf=.9,off_loss=-40.,slow_off=-.25,on_mean=.5,on_pf=1.1,slow_on=0.),
 dict(name='G3',fw=8,sw=64,min_session=8,off_mean=.25,off_pf=1.,off_loss=-40.,slow_off=0.,on_mean=.75,on_pf=1.2,slow_on=.1),
 dict(name='G4',fw=4,sw=32,min_session=4,off_mean=.25,off_pf=1.,off_loss=-20.,slow_off=0.,on_mean=.75,on_pf=1.25,slow_on=.1),
 dict(name='G5',fw=16,sw=64,min_session=8,off_mean=0.,off_pf=.8,off_loss=-80.,slow_off=-.25,on_mean=.25,on_pf=1.,slow_on=0.),
 dict(name='G6',fw=8,sw=32,min_session=4,off_mean=.5,off_pf=1.,off_loss=-30.,slow_off=0.,on_mean=1.,on_pf=1.3,slow_on=.2),
 dict(name='G7',fw=4,sw=16,min_session=4,off_mean=0.,off_pf=.8,off_loss=-15.,slow_off=-.25,on_mean=.25,on_pf=1.,slow_on=0.),
 dict(name='G8',fw=8,sw=64,min_session=16,off_mean=0.,off_pf=.8,off_loss=-50.,slow_off=-.5,on_mean=.5,on_pf=1.1,slow_on=-.1),
]
if __name__=='__main__':
    import sys
    if '--build' in sys.argv: print(json.dumps(build_streams(),indent=2))
    else:
        rows=[]
        for p in PARAMS:
            r=eval_param(p);rows.append({'params':p,'feb':r['feb'],'mar':r['mar']})
            print(json.dumps({'name':p['name'],'feb':{k:r['feb']['score'][k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks']},'mar':{k:r['mar']['score'][k] for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks']},'fg':r['feb']['gate_stream'],'mg':r['mar']['gate_stream']}),flush=True)
        open(f'{BASE}/expert_gate_133c.json','w').write(json.dumps({'candidate':'EXPERT_GATE_133C','rows':rows},indent=2))