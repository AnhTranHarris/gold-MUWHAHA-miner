import json, heapq, numpy as np
import gamma02_ny17_quantum_minute_window_075 as w
import gamma02_funded_cap_equity_dd_028 as eq
from gamma02_083_heat_parent_ownership_084 import renewal_owned,metric,crossover,SYN

def build():
    D,pei,pxi,pd,src,mins,disp=w.prep();t,a,b=D[:3]
    me=(src==17)&(mins>=30)&(mins<=31)&(disp>=3.)
    ml=(src==17)&(mins>=33)&(mins<=39)&(disp>=5.)
    A=renewal_owned(t,a,b,pei[me],pxi[me],pd[me],500,250,0,1)
    B=renewal_owned(t,a,b,pei[ml],pxi[ml],pd[ml],1250,0,0,2)
    E=np.concatenate((A[0],B[0]));X=np.concatenate((A[1],B[1]));R=np.concatenate((A[2],B[2]));Dd=np.concatenate((A[3],B[3]));P=np.concatenate((A[4],B[4]));H=np.concatenate((A[5],B[5]));desk=np.concatenate((np.ones(len(A[0]),np.int8),np.full(len(B[0]),2,np.int8)))
    o=np.lexsort((np.arange(len(E)),E));return D,(E[o],X[o],R[o],Dd[o],P[o],H[o],desk[o])

def select_cap(A,cap):
    E,X,R,D,P,H,S=A; heap=[];keep=[];skips=0;maxopen=0
    for k in range(len(E)):
        now=int(E[k])
        while heap and heap[0][0]<=now:heapq.heappop(heap)
        if len(heap)>=cap:
            skips+=1;continue
        keep.append(k);heapq.heappush(heap,(int(X[k]),k));maxopen=max(maxopen,len(heap))
    q=np.asarray(keep,np.int64);return tuple(x[q] for x in A),skips,maxopen

def cluster(E):
    if len(E)==0:return dict(unique_ticks=0,cluster_fraction=0.,max_cluster=0)
    _,c=np.unique(E,return_counts=True);return dict(unique_ticks=int(len(c)),cluster_fraction=float(c[c>1].sum()/len(E)),max_cluster=int(c.max()))

def one(A,cap):
    B,sk,mo=select_cap(A,cap);E,X,R,D,P,H,S=B;m=metric(P,H);r=dict(cap=cap,**m,skips=sk,maxopen_event=mo,**cluster(E),early_trades=int(np.sum(S==1)),late_trades=int(np.sum(S==2)),early_net=float(P[S==1].sum()),late_net=float(P[S==2].sum()),crossover=crossover(m));r['all_metric_crossover']=all(r['crossover'].values());return r,B

def exact(D,B,r):
    t,a,b=D[:3];E,X,R,Dd,P,H,S=B;Q=eq.exact_equity_sweep(t,a,b,E,X,R,Dd,P);peak=100000.+Q[3];z=dict(r);z.update(balance_dd=float(Q[2]),equity_dd=float(Q[4]),equity_dd_pct_peak=float(Q[4]/peak*100),minimum_total_equity=float(100000.+Q[5]),maxopen_exact=int(Q[9]),pnl_reconstruction=float(Q[0]));return z

def main():
    D,A=build();caps=[32,64,96,128,160,192,256,320,384,448,512,576,640,704,768,896,1024,1152,1280,1400,1443]
    rows=[];cache={}
    for cap in caps:
        r,B=one(A,cap);rows.append(r);cache[cap]=B
        print(json.dumps({k:r[k] for k in ['cap','net','trades','pf','win','expectancy','avg_hold_s','early_trades','late_trades','unique_ticks','cluster_fraction','max_cluster','skips','all_metric_crossover']}),flush=True)
        json.dump({'candidate':'GAMMA02_083_GLOBAL_CHILD_CAP_087','rows':rows},open('/mnt/data/gamma02_083_global_child_cap_087.partial.json','w'),indent=2)
    valid=[r for r in rows if r['all_metric_crossover']];valid.sort(key=lambda q:(q['cap'],-q['net']))
    exact_rows=[]
    for r in valid[:4]:
        z=exact(D,cache[r['cap']],r);exact_rows.append(z);print('EXACT',json.dumps({k:z[k] for k in ['cap','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','equity_dd_pct_peak','minimum_total_equity','maxopen_exact','all_metric_crossover']}),flush=True)
    obj=dict(candidate='GAMMA02_083_GLOBAL_CHILD_CAP_087',admission='chronological first-come child admission; exit <= entry tick releases slot; no future ranking',rows=rows,valid_count=len(valid),minimum_all_metric_cap=valid[0] if valid else None,exact_rows=exact_rows)
    json.dump(obj,open('/mnt/data/gamma02_083_global_child_cap_087.json','w'),indent=2)
if __name__=='__main__':main()