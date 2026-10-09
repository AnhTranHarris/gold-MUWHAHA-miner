"""Experimental L6-compatible *overlay* hypotheses: observed adverse funded position + elapsed time + completed M5 & H1 reversal permission.
NOT fully coupled source-feedback, NOT an MT5 signal, no date switch, fixed 0.01 lot, 1 recovery per predecessor, L7 baseline quote capacity/rate check.
"""
from pathlib import Path
import json,heapq
import numpy as np
import sys
sys.path.insert(0,'/mnt/data/feb046')
from recovery_experiments import T,A,B,L,N,exits,q_metrics
F=Path('/mnt/data/feb046')

def candidates(delay,th,source_set=(22,25),side='opposite'):
    which=np.flatnonzero(np.isin(L['S'],source_set))
    ee=L['E'][which]; idx=np.searchsorted(T,T[ee]+delay*1000,side='left')
    good=idx<L['X'][which]
    which=which[good];idx=idx[good];d=-L['D'][which] if side=='opposite' else L['D'][which]
    origin=L['R'][which]
    mark=np.where(L['D'][which]>0,B[idx],A[idx])
    good=(mark-origin)*L['D'][which]/1000.<=-th
    which=which[good];idx=idx[good];d=d[good]
    # Completed *previous* M5 and H1 bars, not current unfinished candle
    five=T[idx]//300000;hour=T[idx]//3600000
    p5=np.searchsorted(T,five*300000,side='left')-1
    q5=np.searchsorted(T,(five-1)*300000,side='left')-1
    p1=np.searchsorted(T,hour*3600000,side='left')-1
    q1=np.searchsorted(T,(hour-1)*3600000,side='left')-1
    s5=(A[p5]+B[p5]).astype('int64')-(A[q5]+B[q5]).astype('int64')
    s1=(A[p1]+B[p1]).astype('int64')-(A[q1]+B[q1]).astype('int64')
    good=(p5>=0)&(q5>=0)&(q1>=0)&((s5*d)>0)&((s1*d)>0)
    good &= (A[idx]-B[idx])<=3000
    idx=idx[good];d=d[good];which=which[good]
    ix=np.argsort(idx,kind='stable');return idx[ix],d[ix],which[ix]

def scenario(delay,adverse,tp,sl,hold=240,cap=1536,own_cap=16,rate=10,source_set=(22,25)):
    E,D,preds=candidates(delay,adverse,source_set)
    X,P=exits(T,A,B,E,D,tp,sl,hold)
    base=np.cumsum(np.bincount(L['E'],minlength=N)-np.bincount(L['X'],minlength=N))
    sec,count=np.unique(T[L['E']]//1000,return_counts=True);rmap=dict(zip(sec,count));used={};heap=[];EE=[];XX=[];DD=[];PP=[];ncap=nrate=nself=0
    for j,e in enumerate(E):
        while heap and heap[0]<=e:heapq.heappop(heap)
        sid=int(T[e]//1000)
        if base[e]+len(heap)>=cap:ncap+=1;continue
        if len(heap)>=own_cap:nself+=1;continue
        if rmap.get(sid,0)+used.get(sid,0)>=rate:nrate+=1;continue
        if EE and e==EE[-1]:continue
        EE.append(e);XX.append(X[j]);DD.append(D[j]);PP.append(P[j]);used[sid]=used.get(sid,0)+1;heapq.heappush(heap,int(X[j]))
    EE=np.array(EE,dtype=np.int64);XX=np.array(XX,dtype=np.int64);DD=np.array(DD,dtype=np.int8);PP=np.array(PP)
    RR=np.where(DD>0,A[EE],B[EE]);assert not len(EE) or np.max(abs(PP-(np.where(DD>0,B[XX],A[XX])-RR)*DD/1000.+.02))<1e-9
    both={k:np.r_[L[k],z] for k,z in [('E',EE),('X',XX),('R',RR),('D',DD),('P',PP)]}
    result=q_metrics(both,exact=False)
    result.update(candidates=len(E),l6_trades=len(EE),l6_net=round(float(PP.sum()),3),l6_gross_loss=round(float(PP[PP<0].sum()),3),deny_cap=ncap,deny_rate=nrate,deny_recovery_cap=nself)
    return both,result

if __name__=='__main__':
   rows=[]
   for delay in (60,180,300):
    for adv in (3,6,10):
     for tp,sl in ((3,2),(6,3)):
      led,score=scenario(delay,adv,tp,sl)
      row=dict(config=dict(delay=delay,adverse=adv,tp=tp,sl=sl),**score)
      rows.append(row);print('L6',json.dumps(row),flush=True)
   rows.sort(key=lambda x:x['net'],reverse=True)
   for r in rows[:3]:
     c=r['config'];led,z=scenario(c['delay'],c['adverse'],c['tp'],c['sl']);r.update(q_metrics(led,exact=True));print('EXACT',json.dumps(r),flush=True)
   (F/'STRUCTURAL_RECOVERY_SCREEN.json').write_text(json.dumps(rows,indent=2))