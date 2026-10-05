import sys,time,json
from pathlib import Path
import numpy as np,pandas as pd
from numba import njit
sys.path.insert(0,'/mnt/data')
import r9b_screen_rebuilt_20261005 as R

@njit
def baseline_events(t,mid,sec_ids,s1d,s1e,s1r,s1t,atr,sess):
    maxn=100000
    et=np.empty(maxn,np.int64); es=np.empty(maxn,np.int8); pnl=np.empty(maxn,np.float64); pnl[:]=np.nan; n=0
    minute=-1; buy=0.; sell=0.; pending=0; rearms=0; pos=0; entry=0.; stop=0.; opent=0; last_event=0; rearm_pending=0; sec_idx=-1; last_sec=-1
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec!=last_sec:
            while sec_idx+1<len(sec_ids) and sec_ids[sec_idx+1]<sec: sec_idx+=1
            last_sec=sec
        mn=tt//60000
        if mn!=minute:
            minute=mn; rearms=0; pending=2
            buy=np.round((p+.15)*100.)/100.; sell=np.round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos!=0:
            exited=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop): ex=bid if pos>0 else ask; exited=True
            elif tt-opent>=30000: ex=bid if pos>0 else ask; exited=True
            else:
                if pos>0 and bid-entry>=.10:
                    cand=bid-.03
                    if cand>stop+.005: stop=cand
                elif pos<0 and entry-ask>=.10:
                    cand=ask+.03
                    if cand<stop-.005: stop=cand
            if exited:
                pnl[n-1]=(ex-entry)*pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000==minute and rearms<3:
                rearms+=1; pending=-last_event if last_event!=0 else 0
            else: pending=0
            continue
        if pending==0 or sec_idx<10: continue
        av=atr[sec_idx]
        if not(av>0): continue
        ss=sess[sec_idx]; floor=2.5
        if ss==1: floor=2.
        elif ss==2 or ss==3: floor=1.75
        if av+1e-12<floor: continue
        side=0
        if (pending==2 or pending==1) and ask>=buy: side=1
        elif (pending==2 or pending==-1) and bid<=sell: side=-1
        if side==0: continue
        dd=s1d[sec_idx]; ee=s1e[sec_idx]; rr=s1r[sec_idx]; tr=s1t[sec_idx]
        if not(ee>=.70 and rr>=.50 and tr<=9): continue
        if side>0 and dd<.15: continue
        if side<0 and dd>-.15: continue
        if n>=maxn: break
        et[n]=tt; es[n]=side; n+=1
        entry=ask if side>0 else bid; stop=bid-.30 if side>0 else ask+.30; pos=side; opent=tt; pending=0; last_event=side
    return et[:n],es[:n],pnl[:n]

@njit
def fixed_score(t,mid,event_t,event_side,sec_ids,so,sh,sl,sc,sn,cont_thr,fade_thr,strong):
    N=len(event_t)
    pp=np.empty(N,np.float64); state=np.empty(N,np.int8); hold=np.empty(N,np.float64); m=np.zeros(N,np.uint8)
    for q in range(N):
        tt=event_t[q]; side=event_side[q]; j=np.searchsorted(sec_ids,tt//1000)-1
        if j<0: continue
        aligned=(sc[j]-so[j])*side; r1=sh[j]-sl[j]; n1=sn[j]; trade=0; st=0
        if aligned<=cont_thr and ((not strong) or r1+1e-12>=.285): trade=side; st=1
        elif aligned>=fade_thr and ((not strong) or n1>=5): trade=-side; st=-1
        if trade==0: continue
        i=np.searchsorted(t,tt)
        if i>=len(t): continue
        p=mid[i]; bid=p-.10; ask=p+.10; entry=ask if trade>0 else bid; stop=bid-5. if trade>0 else ask+5.; ex=np.nan; exit_t=tt; end=tt+120000; k=i
        while k<len(t) and t[k]<=end:
            p=mid[k]; bid=p-.10; ask=p+.10
            if (trade>0 and bid<=stop) or (trade<0 and ask>=stop): ex=bid if trade>0 else ask; exit_t=t[k]; break
            if trade>0 and bid-entry>=.01:
                cand=bid-.01
                if cand>stop+.005: stop=cand
            elif trade<0 and entry-ask>=.01:
                cand=ask+.01
                if cand<stop-.005: stop=cand
            k+=1
        if not np.isfinite(ex):
            k=np.searchsorted(t,end)
            if k>=len(t): k=len(t)-1
            p=mid[k]; ex=p-.10 if trade>0 else p+.10; exit_t=t[k]
        pp[q]=(ex-entry)*trade; state[q]=st; hold[q]=(exit_t-tt)/1000.; m[q]=1
    z=m==1
    return pp[z],state[z],hold[z]

def metrics(name,p,st,h):
    gp=float(p[p>0].sum()); gl=float(p[p<0].sum())
    eq=np.cumsum(p); peak=np.maximum.accumulate(np.r_[0.,eq]); dd=float(np.max(peak[1:]-eq)) if len(eq) else 0.
    return dict(name=name,trades=int(len(p)),net=float(p.sum()),gp=gp,gl=gl,pf=float(gp/(-gl)) if gl<0 else None,win=float((p>0).mean()),dd=dd,avg_hold=float(h.mean()),cont=int((st==1).sum()),fade=int((st==-1).sum()))

t0=time.time()
t,mid=R.load_ticks(1); z=R.build_features(t,mid); sec=z['sec_ids']
sess=np.array([R.session_for_sec(int(s)) for s in sec],np.int8); sn=(z['sec_last_ix']-z['sec_first_ix']+1).astype(np.int64)
et,es,bp=baseline_events(t,mid,sec,z['s1_disp'],z['s1_eff'],z['s1_rng'],z['s1_turns'],z['atrsec'],sess)
bg=bp[np.isfinite(bp)]; base=metrics('BASE_R9',bg,np.zeros(len(bg),np.int8),np.zeros(len(bg))); base['events']=len(et)
rows=[]
for args in [('DOC_BASE',-.255,.275,False),('DOC_STRONG',-.255,.275,True),('LO250',-.250,.275,True),('LO260',-.260,.275,True),('HI270',-.255,.270,True),('HI280',-.255,.280,True),('DEF',-.290,.310,True)]:
    p,st,h=fixed_score(t,mid,et,es,sec,z['sec_open'],z['sec_high'],z['sec_low'],z['sec_close'],sn,args[1],args[2],args[3])
    rows.append(metrics(args[0],p,st,h))
out={'status':'COMPLETE_FRESH_JAN_FIXED_ENTRY_REBUILD','baseline':base,'rows':rows,'elapsed_s':time.time()-t0}
Path('/mnt/data/SA100_S1_FIXED_ENTRY_JAN_REBUILD01.json').write_text(json.dumps(out,indent=2))
pd.DataFrame(rows).to_csv('/mnt/data/SA100_S1_FIXED_ENTRY_JAN_REBUILD01.csv',index=False)
print(json.dumps(out,indent=2))
