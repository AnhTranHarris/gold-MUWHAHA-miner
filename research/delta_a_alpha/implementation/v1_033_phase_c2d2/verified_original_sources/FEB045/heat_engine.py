"""January V1 original-source physically accepted CHILD genealogy prototype.
Re-simulates physical portfolio exits, global single account capacity and unlocks
from ONLY broker-admitted and already-closed children. Each child exit is original
actual Dukascopy tick first passage, not a new stop/TP. Source proposals can still
contain precomputed hypothetical renewal paths -> NOT FULL V1/MT5 CERTIFICATION.
Strict: rejected child breaks that parent's later child sequence; no hypothetical
closed loss/profit enters unlocking. No calendar identity in deployed conditions.
"""
import csv, heapq, json, time, sys, os
from pathlib import Path
import numpy as np,pandas as pd
PATH=Path(os.environ.get('DAA_JAN039_RESEARCH_DIR', '/mnt/data/jan_research'));CACHE=PATH/'FEB041_ORIGINAL_SOURCE_PROPOSALS.npz'
with np.load(CACHE) as z: K={k:z[k].copy() for k in z.files}
E,X,R,D,P,H,S,C,O,N=[K[k] for k in 'EXRDPHSCON']
sys.path.insert(0,os.environ.get('DAA_FEB043_ORIGINAL_SOURCE_DIR','/mnt/data/feb041/original/source'))
import stmr_janjul as j
t,a,b,_,_=j.load_month(2,10)
spread=(a[E].astype(np.int64)-b[E])/1000
im20idx=np.searchsorted(t,t[E]-20000,side='left');imp20=((a[E].astype(np.int64)+b[E])-(a[im20idx].astype(np.int64)+b[im20idx]))/2000
num_p=len(K['parent_start']); num_c=int(C.max()+1); total=len(E)
print('READY',len(t),'quotes',total,'proposals',num_p,'parents',num_c,'WD cells',flush=True)
# lower cap intentionally enforces ONE account budget instead of independent WD & supplements.
def run(maxopen=128,wdcap=64,per_quote=2,spread_max=5.0,sidecap=80,impulse_lock=0.,childhold=60.,unlock=4,cooldown_ms=0,scout_budget=1,cap_cell=16,slippage=0.,per_second=15,initial_balance=100000.,margin_leverage=500.,reserve_ratio=.20,l3_min_mom=-1e10,l3_max_mom=1e10,l3_excluded_hours=0,phase5cap=512,phase4cap=512,phase2cap=512,phase3cap=512,phase0cap=512,source26cap=512,source22cap=4096,source27cap=4096,source25cap=4096,s25phase1cap=4096,s25phase34cap=4096,heat_global=1e12,heat_s22=1e12,heat_s25=1e12,heat_s27=1e12,shock_usd=0.,same_source_min_gap=0.,source_cooldown_ms=0,source_maxopen_extra=4096,soft_heat_margin=0.):
    open_heap=[] # (exit_tick, entry_arridx)
    src_n=np.zeros((64,2),np.int32); src_entry=np.zeros((64,2),np.float64)
    last_src_price=np.full((64,2),-1.0,np.float64);last_src_time=np.full((64,2),-10**15,np.int64)
    cohort_n=np.zeros(2,np.int32);cohort_entry=np.zeros(2,np.float64)

    status=np.zeros(num_p,np.int8) # 0 unseen, 1 allowed, 2 denied family
    next_ord=np.zeros(num_p,np.int32)
    first=np.zeros(num_c,np.int8);streak=np.zeros(num_c,np.int16)
    admitted_scouts=np.zeros(num_c,np.int16);scout_since=np.full(num_c,-10**15,np.int64)
    acct=initial_balance;nl=ns=0;sumlong=sumshort=0.;nw=0;wlong=wshort=0;wel=wesh=0.;cellopen=np.zeros((num_c,2),np.int32)
    o_e=[];o_x=[];o_r=[];o_d=[];o_p=[];o_s=[];o_o=[];o_c=[]
    denied=np.zeros(15,np.int64);phase5_open=0;phase4_open=0;phase2_open=0;phase3_open=0;phase0_open=0;source26_open=0;source22_open=0;source27_open=0;source25_open=0;s25phase1_open=0;s25phase34_open=0;o_phase=[]; opening=closing=0;balpeak=acct;bdd=0.;approxpeak=acct;approxdd=0.;maxcount=0
    last_tick=-1;n_tick=0;last_second=-1;n_second=0
    for idx in range(total):
        ei=int(E[idx]);ti=int(t[ei]);direction=int(D[idx]);owner=int(O[idx]);cell=int(C[idx]);src=int(S[idx]);ep=int(R[idx]);ep_f=ep/1000.
        # Physical child endings only; actual ledger PnL uses true quote on original stopping tick.
        while open_heap and open_heap[0][0]<=ei:
            xi,j=heapq.heappop(open_heap); pnl=o_p[j];ss=o_s[j];dd=o_d[j];r=o_r[j];cc=o_c[j]
            acct+=pnl;closing+=1
            direction_idx=1 if dd>0 else 0
            src_n[ss,direction_idx]-=1; src_entry[ss,direction_idx]-=r
            if ss in (22,25,27):cohort_n[direction_idx]-=1;cohort_entry[direction_idx]-=r
            if ss==26:source26_open-=1
            if ss==22:source22_open-=1
            if ss==27:source27_open-=1
            if ss==25:source25_open-=1
            if ss==25 and o_phase[j]==1:s25phase1_open-=1
            if ss==25 and o_phase[j] in (3,4):s25phase34_open-=1
            if ss==27 and o_phase[j]==0:phase0_open-=1
            if ss==27 and o_phase[j]==5:phase5_open-=1
            if ss==27 and o_phase[j]==4:phase4_open-=1
            if ss==27 and o_phase[j]==2:phase2_open-=1
            if ss==27 and o_phase[j]==3:phase3_open-=1
            if dd>0:nl-=1;sumlong-=r
            else:ns-=1;sumshort-=r
            if ss==0:
                nw-=1
                if dd>0:wlong-=1;wel-=r;cellopen[cc,1]-=1
                else:wshort-=1;wesh-=r;cellopen[cc,0]-=1
                if pnl>0 and (t[xi]-t[o_e[j]])/1000<=childhold:streak[cc]+=1
                else:streak[cc]=0
            if acct>balpeak:balpeak=acct
            bdd=max(bdd,balpeak-acct)
        if ei!=last_tick:last_tick=ei;n_tick=0
        sec=ti//1000
        if sec!=last_second:last_second=sec;n_second=0
        allowed=True
        if src>=17 and ((l3_excluded_hours>>(src-10))&1):denied[11]+=1;allowed=False
        elif src>=17 and (direction*imp20[idx]<l3_min_mom):denied[12]+=1;allowed=False
        elif src>=17 and (direction*imp20[idx]>l3_max_mom):denied[13]+=1;allowed=False
        elif spread[idx]>spread_max:denied[0]+=1;allowed=False
        elif nl+ns>=maxopen:denied[1]+=1;allowed=False
        elif (nl if direction>0 else ns)>=sidecap:denied[2]+=1;allowed=False
        elif n_tick>=per_quote:denied[3]+=1;allowed=False
        elif n_second>=per_second:denied[4]+=1;allowed=False
        elif src==0 and nw>=wdcap:denied[5]+=1;allowed=False
        elif src==0 and cellopen[cell,1 if direction>0 else 0]>=cap_cell:denied[6]+=1;allowed=False
        elif src==0 and impulse_lock>0 and imp20[idx]*direction<=-impulse_lock:denied[7]+=1;allowed=False
        # Admitted entries only: combined current portfolio drawdown/heat,
        # stressed-direction risk, source-owned budget, and finite equal-lot grid cells.
        if src>=17:
            side_i=1 if direction>0 else 0
            cur_bid=int(b[ei]);cur_ask=int(a[ei]);shock=shock_usd*1000
            # Quote-side stressed adverse loss, one direction at a time;
            # two-sided stress uses max long/down versus short/up, not both moving adversely.
            src_floats=np.maximum(0.,(src_entry[:,1]-src_n[:,1]*(cur_bid-shock))/1000.)+np.maximum(0.,(src_n[:,0]*(cur_ask+shock)-src_entry[:,0])/1000.)
            stressed_l=max(0.,(sumlong-nl*(cur_bid-shock))/1000.)
            stressed_s=max(0.,(ns*(cur_ask+shock)-sumshort)/1000.)
            if max(stressed_l,stressed_s)>=heat_global:allowed=False;denied[14]+=1
            if src_floats[src]>=({22:heat_s22,25:heat_s25,27:heat_s27}.get(src,1e12)):allowed=False;denied[14]+=1
            if src_n[src].sum()>=source_maxopen_extra:allowed=False;denied[14]+=1
            if same_source_min_gap>0 and last_src_price[src,side_i]>=0 and abs(ep-last_src_price[src,side_i])<same_source_min_gap*1000:allowed=False;denied[14]+=1
            if source_cooldown_ms>0 and ti-last_src_time[src,side_i]<source_cooldown_ms:allowed=False;denied[14]+=1
        if src==25 and (ti//600000)%6 in (3,4) and s25phase34_open>=s25phase34cap:denied[14]+=1;allowed=False
        if src==25 and (ti//600000)%6==1 and s25phase1_open>=s25phase1cap:denied[14]+=1;allowed=False
        if src==25 and source25_open>=source25cap:denied[14]+=1;allowed=False
        if src==26 and source26_open>=source26cap:denied[14]+=1;allowed=False
        if src==22 and source22_open>=source22cap:denied[14]+=1;allowed=False
        if src==27 and source27_open>=source27cap:denied[14]+=1;allowed=False
        if src==27 and ((ti//600000)%6==0 and phase0_open>=phase0cap or (ti//600000)%6==5 and phase5_open>=phase5cap or (ti//600000)%6==4 and phase4_open>=phase4cap or (ti//600000)%6==2 and phase2_open>=phase2cap or (ti//600000)%6==3 and phase3_open>=phase3cap):
            denied[14]+=1;allowed=False
        # Original parent family is admitted based exclusively on realized funded children.
        if src==0:
            seq=int(N[idx])
            if status[owner]==2 or seq!=next_ord[owner]:denied[8]+=1;continue
            if status[owner]==0:
                if first[cell]==0:
                    # Initial scout is earned only if its FIRST CHILD passes all risk checks.
                    pass
                elif streak[cell]<unlock:
                    if not (scout_budget>admitted_scouts[cell] and ti-scout_since[cell]>=cooldown_ms):
                        status[owner]=2;denied[9]+=1;continue
                if not allowed:
                    # Another parent may try to become scout: unsuccessful parent excluded.
                    status[owner]=2;continue
            elif not allowed:
                status[owner]=2;continue
        if not allowed:continue
        mid=(int(a[ei])+int(b[ei]))/2000.
        floatp=(nl*int(b[ei])-sumlong+sumshort-ns*int(a[ei]))/1000.-.02*(nl+ns)
        equity=acct+floatp
        margin=(nl+ns+1)*mid/margin_leverage
        if equity<=0 or equity-margin<reserve_ratio*equity:
            denied[10]+=1
            if src==0:status[owner]=2
            continue
        if src==0:
            if status[owner]==0:
                status[owner]=1
                if first[cell]==0:first[cell]=1
                elif streak[cell]<unlock:
                    admitted_scouts[cell]+=1;scout_since[cell]=ti
            next_ord[owner]+=1
        # Slip is charged against quote-side executable profit, not used to select future events.
        pnl=float(P[idx])-slippage;rr=ep
        jj=len(o_e);o_e.append(ei);o_x.append(int(X[idx]));o_r.append(rr);o_d.append(direction);o_p.append(pnl);o_s.append(src);o_o.append(owner);o_c.append(cell);o_phase.append((ti//600000)%6)
        side_i=1 if direction>0 else 0
        src_n[src,side_i]+=1;src_entry[src,side_i]+=rr
        last_src_price[src,side_i]=rr;last_src_time[src,side_i]=ti
        if src in (22,25,27):cohort_n[side_i]+=1;cohort_entry[side_i]+=rr
        if src==26:source26_open+=1
        if src==22:source22_open+=1
        if src==27:source27_open+=1
        if src==25:source25_open+=1
        if src==25 and o_phase[-1]==1:s25phase1_open+=1
        if src==25 and o_phase[-1] in (3,4):s25phase34_open+=1
        if src==27 and o_phase[-1]==0:phase0_open+=1
        if src==27 and o_phase[-1]==5:phase5_open+=1
        if src==27 and o_phase[-1]==4:phase4_open+=1
        if src==27 and o_phase[-1]==2:phase2_open+=1
        if src==27 and o_phase[-1]==3:phase3_open+=1
        heapq.heappush(open_heap,(int(X[idx]),jj)); opening+=1;n_tick+=1;n_second+=1
        if direction>0:nl+=1;sumlong+=rr
        else:ns+=1;sumshort+=rr
        if src==0:
            nw+=1
            if direction>0:wlong+=1;wel+=rr;cellopen[cell,1]+=1
            else:wshort+=1;wesh+=rr;cellopen[cell,0]+=1
        maxcount=max(maxcount,nl+ns)
        # entry-point equity DD diagnostic; exact full-tick DD computed for selected ledgers.
        eq=acct+(nl*int(b[ei])-sumlong+sumshort-ns*int(a[ei]))/1000.-.02*(nl+ns)
        approxpeak=max(approxpeak,eq);approxdd=max(approxdd,approxpeak-eq)
    while open_heap:
        xi,j=heapq.heappop(open_heap);acct+=o_p[j]
        balpeak=max(balpeak,acct);bdd=max(bdd,balpeak-acct)
    p=np.asarray(o_p);ss=np.asarray(o_s);gp=float(p[p>0].sum());gl=float(p[p<0].sum());trades=len(p)
    out={'net':round(float(p.sum()),3),'trades':trades,'gp':round(gp,3),'gl':round(gl,3),'pf':round(gp/-gl,4) if gl<0 else 999.,'win_pct':round(float(np.mean(p>0)*100),2) if trades else 0,'bal_dd':round(bdd,2),'event_eq_dd_lb':round(approxdd,2),'maxopen':maxcount,'wd_trades':int((ss==0).sum()),'wd_net':round(float(p[ss==0].sum()),2),'L3_net':round(float(p[ss!=0].sum()),2),'denied':denied.tolist(),'scouts':admitted_scouts.tolist()}
    led={'E':np.asarray(o_e,np.int64),'X':np.asarray(o_x,np.int64),'R':np.asarray(o_r,np.int32),'D':np.asarray(o_d,np.int8),'P':p,'S':ss}
    return out,led

def daily_and_exact(led,scenario):
    import datetime
    pp=led['P'];ee=led['E'];xx=led['X'];ss=led['S']
    exit_days=pd.to_datetime(t[xx],unit='ms',utc=True).strftime('%Y-%m-%d');weeks=pd.to_datetime(t[xx],unit='ms',utc=True).strftime('%G-W%V')
    daily={d:{'net':round(float(pp[exit_days==d].sum()),2),'trades':int(np.sum(exit_days==d)),'gross_loss':round(float(pp[(exit_days==d)&(pp<0)].sum()),2)} for d in np.unique(exit_days)}
    weekly={d:{'net':round(float(pp[weeks==d].sum()),2),'trades':int(np.sum(weeks==d))} for d in np.unique(weeks)}
    # Existing, source-certified exact tick-path evaluator, not an entry-sampled proxy.
    sys.path.insert(0,os.environ.get('DAA_JAN039_EQUITY_HELPERS',str(PATH/'032/source')))
    import gamma02_funded_cap_equity_dd_028 as eq
    r=eq.exact_equity_sweep(t,a,b,led['E'],led['X'],led['R'],led['D'],pp)
    scenario.update(equity_dd=float(r[4]),maxopen_full=int(r[9]),score_net_recon=float(r[0]),daily=daily,weekly=weekly)
    return scenario

if __name__=='__main__':
    out=[];start=time.monotonic()
    configurations=[]
    for maxopen in [16,32,64,128,256]:
      for wdcap in [8,16,32,64,128,256]:
       if wdcap>maxopen:continue
       for per_quote in [1,2,4,8]:
        configurations.append(dict(maxopen=maxopen,wdcap=wdcap,per_quote=per_quote,sidecap=maxopen,cap_cell=max(4,wdcap//4),spread_max=6,per_second=50))
    for k,params in enumerate(configurations):
        o,_=run(**params);o['id']=k;o['params']=params;out.append(o)
        if k%20==0:print('SCREEN',k,'of',len(configurations),o['net'],o['pf'],'elapsed',round(time.monotonic()-start,1),flush=True)
    out.sort(key=lambda x:(x['net'],x['pf']),reverse=True)
    (PATH/'JAN037_FUNDED_SCREEN.json').write_text(json.dumps(out,indent=2))
    print('TOP5',json.dumps(out[:5]),flush=True)
    print('TOTAL',len(out),'seconds',round(time.monotonic()-start,1),flush=True)
