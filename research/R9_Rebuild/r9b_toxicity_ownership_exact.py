import sys, json, time
sys.path.insert(0,'/mnt/data')
import numpy as np
from numba import njit
import r9b_screen as R

@njit(cache=True)
def allow_tox(atr,session,disp,rng,turns):
    # Frozen depth-4 / min-leaf-1500 Jan-Mar tree, keep predicted clipped-PnL >= -0.17526659364804825
    if atr <= 14.155770:
        if session <= 1:
            if atr <= 4.964402:
                return disp > 1.042500
            return True
        else:
            if rng <= 2.980750:
                return atr > 11.730434
            return False
    else:
        if atr <= 24.628465:
            return turns <= 4.5
        return True

@njit(cache=True)
def sim(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec,align_long,align_short,consume_reject):
    maxtr=max(50000,len(t)//20)
    pnl=np.empty(maxtr,np.float64); hold=np.empty(maxtr,np.float64); mfe=np.empty(maxtr,np.float64); mae=np.empty(maxtr,np.float64)
    ntr=0; sec_idx=-1; last_sec=-1; minute=-1; buy_lvl=0.; sell_lvl=0.; pending=0; rearms=0
    pos=0; entry=0.; stop=0.; opent=0; maxfav=0.; maxadv=0.; last_pos=0; rearm_pending=0; rejected=0
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec!=last_sec:
            while sec_idx+1<len(sec_ids) and sec_ids[sec_idx+1] < sec: sec_idx+=1
            last_sec=sec
        mn=tt//60000
        if mn!=minute:
            minute=mn; rearms=0; pending=2
            buy_lvl=round((p+.15)*100.)/100.; sell_lvl=round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos!=0:
            fav=(bid-entry) if pos>0 else (entry-ask); adv=(entry-bid) if pos>0 else (ask-entry)
            if fav>maxfav: maxfav=fav
            if adv>maxadv: maxadv=adv
            exd=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop): ex=bid if pos>0 else ask; exd=True
            elif tt-opent>=30000: ex=bid if pos>0 else ask; exd=True
            else:
                if pos>0 and bid-entry>=.10:
                    cand=bid-.03
                    if cand>stop+.005: stop=cand
                elif pos<0 and entry-ask>=.10:
                    cand=ask+.03
                    if cand<stop-.005: stop=cand
            if exd:
                pnl[ntr-1]=(ex-entry)*pos; hold[ntr-1]=(tt-opent)/1000.; mfe[ntr-1]=maxfav; mae[ntr-1]=maxadv
                last_pos=pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000==minute and rearms<3: rearms+=1; pending=-last_pos
            else: pending=0
            continue
        if pending==0 or sec_idx<10: continue
        av=atrsec[sec_idx]
        if not np.isfinite(av): continue
        ss=R.session_for_sec(sec_ids[sec_idx]); floor=2.5
        if ss==1: floor=2.0
        elif ss==2 or ss==3: floor=1.75
        if av+1e-12<floor: continue
        side=0
        if (pending==2 or pending==1) and ask>=buy_lvl: side=1
        elif (pending==2 or pending==-1) and bid<=sell_lvl: side=-1
        if side==0: continue
        dd=s1_disp[sec_idx]; ee=s1_eff[sec_idx]; rr=s1_rng[sec_idx]; tr=s1_turns[sec_idx]
        if not(ee>=.70 and rr>=.50 and tr<=9): continue
        if side>0 and dd<.15: continue
        if side<0 and dd>-.15: continue
        disp_al=dd*side
        if not allow_tox(av,ss,disp_al,rr,tr):
            rejected+=1
            if consume_reject==1: pending=0
            continue
        if ntr>=maxtr: break
        entry=ask if side>0 else bid; stop=bid-.30 if side>0 else ask+.30; pos=side; opent=tt; pending=0; maxfav=0.; maxadv=0.
        pnl[ntr]=np.nan;hold[ntr]=np.nan;mfe[ntr]=np.nan;mae[ntr]=np.nan;ntr+=1
    g=np.isfinite(pnl[:ntr]);return pnl[:ntr][g],hold[:ntr][g],mfe[:ntr][g],mae[:ntr][g],rejected

def met(p,h,mf,ma):
    gp=float(p[p>0].sum());gl=float(p[p<0].sum());eq=np.cumsum(p);peak=np.maximum.accumulate(np.r_[0.,eq])[:-1];dd=peak-eq
    return dict(trades=len(p),net=float(p.sum()),gp=gp,gl=gl,pf=gp/-gl if gl<0 else 999,win=float((p>0).mean()),avg_hold=float(h.mean()),maxdd=float(dd.max()) if len(dd) else 0,rejected=None)

def run(m,consume=1):
    arr=R.load_build(m);p,h,mf,ma,r=sim(*arr,consume);x=met(p,h,mf,ma);x['rejected']=int(r);return x
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('--month',type=int,required=True);ap.add_argument('--consume',type=int,default=1);a=ap.parse_args();t=time.time();x=run(a.month,a.consume);x['elapsed']=time.time()-t;print(json.dumps(x,indent=2))
