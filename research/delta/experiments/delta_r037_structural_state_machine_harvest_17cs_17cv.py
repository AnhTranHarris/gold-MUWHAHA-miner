"""R037 17CS-17CV: fast causal structural-state-machine harvest.

Preregistered families only:
- 123NB: confirmed width-3 1-2-3 reversal neckline break.
- MSnR-DBO: rolling A/V double-breakout staircase, breakout-before-level-update.

Research-only. No parameter rescue, August, or MQL5.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

D=86_400_000; H=3_600_000; TICK=10; SCALE=1000
START=1_767_225_600_000; END=1_768_737_600_000
USD=1_772_953_200_000; UKD=1_774_746_000_000
P75=np.array([20,20,21,21],np.int64)
SHA="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
PREREG="0f5e4299eab2e76ead38ad63a5a1376a62de8dc1"
MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def atomic_json(p:Path,o:dict)->None:
    p.parent.mkdir(parents=True,exist_ok=True); tmp=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=p.parent,prefix='.'+p.name+'.',suffix='.tmp',delete=False) as f:
            tmp=f.name; json.dump(o,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p); tmp=None
    finally:
        if tmp:
            try: os.unlink(tmp)
            except FileNotFoundError: pass

def session_code(t):
    tod=t%D; ls=np.where(t>=UKD,7,8)*H; ns=np.where(t>=USD,12,13)*H
    london=(tod>=ls)&(tod<ls+30_600_000); ny=(tod>=ns)&(tod<ns+32_400_000)
    return np.where(london&ny,2,np.where(london,1,np.where(ny,3,0))).astype(np.int8)

def p75(t,a,b):
    sp=P75[session_code(t)]*TICK; mid2=a+b
    bid=((mid2-sp+TICK)//(2*TICK))*TICK
    return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,x,tf):
    q=t//tf; st=np.r_[0,np.flatnonzero(q[1:]!=q[:-1])+1]; en=np.r_[st[1:],len(t)]
    return {
        'e':((q[st]+1)*tf).astype(np.int64),
        'o':x[st].astype(np.int64),
        'c':x[en-1].astype(np.int64),
        'h':np.maximum.reduceat(x,st).astype(np.int64),
        'l':np.minimum.reduceat(x,st).astype(np.int64),
    }

def confirmed_pivots(z,w=3):
    h,l,e=z['h'],z['l'],z['e']; ev=[]
    for k in range(w,len(h)-w):
        ph=all(h[k]>h[k-j] and h[k]>h[k+j] for j in range(1,w+1))
        pl=all(l[k]<l[k-j] and l[k]<l[k+j] for j in range(1,w+1))
        reveal=int(e[k+w])
        if ph: ev.append((reveal,k,1,int(h[k])))
        if pl: ev.append((reveal,k,-1,int(l[k])))
    ev.sort(key=lambda x:(x[0],x[1],-x[2]))
    return ev

def sig_123(t,ask,bid,z,w=3):
    piv=confirmed_pivots(z,w); e,c=z['e'],z['c']; by_reveal={}
    for x in piv: by_reveal.setdefault(x[0],[]).append(x)
    recent=[]; active=None; ix=[]; sd=[]
    d={'pivots':len(piv),'structures':0,'invalidations':0,'neckline_breaks':0,'spread_rejects':0}
    for k in range(len(e)):
        tm=int(e[k])
        if tm<START: continue
        if tm>END: break
        if active is not None and k>active['armed_bar']:
            side=active['side']; p1=active['p1']; neck=active['neck']
            invalid=(side>0 and c[k]<p1) or (side<0 and c[k]>p1)
            broken=(side>0 and c[k]>neck) or (side<0 and c[k]<neck)
            if invalid:
                d['invalidations']+=1; active=None
            elif broken:
                j=int(np.searchsorted(t,tm,side='left'))
                if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
                    ix.append(j); sd.append(side); d['neckline_breaks']+=1
                elif j<len(t): d['spread_rejects']+=1
                active=None
        for _,pk,ps,pv in by_reveal.get(tm,[]):
            if recent and recent[-1][1]==ps:
                if (ps>0 and pv>=recent[-1][2]) or (ps<0 and pv<=recent[-1][2]):
                    recent[-1]=(pk,ps,pv)
                continue
            recent.append((pk,ps,pv))
            if len(recent)>3: recent=recent[-3:]
            if len(recent)==3:
                a,b_,cc=recent
                if a[1]==-1 and b_[1]==1 and cc[1]==-1 and cc[2]>a[2]:
                    active={'side':1,'p1':a[2],'neck':b_[2],'armed_bar':k}; d['structures']+=1
                elif a[1]==1 and b_[1]==-1 and cc[1]==1 and cc[2]<a[2]:
                    active={'side':-1,'p1':a[2],'neck':b_[2],'armed_bar':k}; d['structures']+=1
    return np.asarray(ix,np.int64),np.asarray(sd,np.int8),d

def sig_msnr(t,ask,bid,z,scan=120):
    e,o,c=z['e'],z['o'],z['c']; ix=[]; sd=[]
    A=[]; V=[]
    d={'a_levels':0,'v_levels':0,'a_pair_slides':0,'v_pair_slides':0,'a_restarts':0,'v_restarts':0,'a_expiries':0,'v_expiries':0,'double_a_breakouts':0,'double_v_breakouts':0,'spread_rejects':0}
    for k in range(1,len(e)):
        tm=int(e[k])
        if tm<START: continue
        if tm>END: break
        if A and k-A[0][0]>scan: A=[]; d['a_expiries']+=1
        if V and k-V[0][0]>scan: V=[]; d['v_expiries']+=1
        broke_a=len(A)==2 and c[k]>A[0][1]
        broke_v=len(V)==2 and c[k]<V[0][1]
        if broke_a:
            j=int(np.searchsorted(t,tm,side='left'))
            if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
                ix.append(j); sd.append(1); d['double_a_breakouts']+=1
            elif j<len(t): d['spread_rejects']+=1
            A=[]
        if broke_v:
            j=int(np.searchsorted(t,tm,side='left'))
            if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
                ix.append(j); sd.append(-1); d['double_v_breakouts']+=1
            elif j<len(t): d['spread_rejects']+=1
            V=[]
        prev_green=c[k-1]>o[k-1]; prev_red=c[k-1]<o[k-1]
        cur_green=c[k]>o[k]; cur_red=c[k]<o[k]
        newA=prev_green and cur_red
        newV=prev_red and cur_green
        if newA:
            lv=int(c[k-1]); d['a_levels']+=1
            if len(A)==0: A=[(k-1,lv)]
            elif len(A)==1:
                if lv<A[0][1]: A=[A[0],(k-1,lv)]
                else: A=[(k-1,lv)]; d['a_restarts']+=1
            else:
                if lv<A[1][1]: A=[A[1],(k-1,lv)]; d['a_pair_slides']+=1
                else: A=[(k-1,lv)]; d['a_restarts']+=1
        if newV:
            lv=int(c[k-1]); d['v_levels']+=1
            if len(V)==0: V=[(k-1,lv)]
            elif len(V)==1:
                if lv>V[0][1]: V=[V[0],(k-1,lv)]
                else: V=[(k-1,lv)]; d['v_restarts']+=1
            else:
                if lv>V[1][1]: V=[V[1],(k-1,lv)]; d['v_pair_slides']+=1
                else: V=[(k-1,lv)]; d['v_restarts']+=1
    return np.asarray(ix,np.int64),np.asarray(sd,np.int8),d

@njit(cache=True)
def qt(x): return ((int(x)+5)//10)*10

@njit(cache=True)
def eval_trades(ix,sd,t,a,b):
    busy=-1; tr=bs=sr=days_n=lg=sh=w=0; gp=gl=net=0.; stp=mh=endn=0
    days=np.empty(ix.size,np.int64); u=0
    for z in range(ix.size):
        i=int(ix[z]); s=int(sd[z])
        if i<=busy: bs+=1; continue
        if a[i]-b[i]>MAX_SPREAD: sr+=1; continue
        tr+=1; lg+=s>0; sh+=s<0; days[u]=t[i]//D; u+=1
        entry=a[i] if s>0 else b[i]
        stop=qt(b[i]-STOP if s>0 else a[i]+STOP)
        sec=t[i]//1000; raw=0.; reason=2; last=i
        for k in range(i+1,t.size):
            aa=a[k]; bb=b[k]; last=k
            if s>0 and bb<=stop: raw=(bb-entry)/SCALE; reason=0; break
            if s<0 and aa>=stop: raw=(entry-aa)/SCALE; reason=0; break
            if t[k]//1000-sec>=MAX_HOLD: raw=((bb-entry) if s>0 else (entry-aa))/SCALE; reason=1; break
            fav=(bb-entry) if s>0 else (entry-aa)
            if fav>=TRAIL_ACT:
                ns=qt(bb-TRAIL_DIST if s>0 else aa+TRAIL_DIST)
                if (s>0 and ns>stop) or (s<0 and ns<stop): stop=ns
        after_entry=raw-.01; net+=after_entry-.01; w+=after_entry>1e-12
        if raw>0: gp+=after_entry
        else: gl+=after_entry
        stp+=reason==0; mh+=reason==1; endn+=reason==2; busy=last
    if u:
        x=np.sort(days[:u]); days_n=1
        for k in range(1,x.size): days_n+=x[k]!=x[k-1]
    return tr,bs,sr,days_n,lg,sh,w,gp,gl,net,stp,mh,endn

def pack(ix,sd,t,a,b):
    q=eval_trades(ix,sd,t,a,b)
    m={'signals':int(len(ix)),'trades':int(q[0]),'busy_skips':int(q[1]),'spread_rejects':int(q[2]),'distinct_days':int(q[3]),'long':int(q[4]),'short':int(q[5]),'official_wins':int(q[6]),'gross_profit':round(float(q[7]),2),'gross_loss':round(float(q[8]),2),'direct_net_usd':round(float(q[9]),2),'exit_reasons':{'STOP':int(q[10]),'MAX_HOLD':int(q[11]),'END':int(q[12])}}
    g={'minimum_trades_20':m['trades']>=20,'minimum_distinct_days_5':m['distinct_days']>=5,'direct_net_nonnegative':m['direct_net_usd']>=0}
    g['screen_pass']=all(g.values())
    return m,g

def main():
    st=time.monotonic(); ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); x=ap.parse_args()
    hs=sha256_file(x.source)
    if hs!=SHA: raise SystemExit(f'SHA mismatch {hs}')
    d=pd.read_csv(x.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    d=d[(d.timestamp_ms_utc>=START)&(d.timestamp_ms_utc<END)]
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709 or np.any(t[1:]<t[:-1]): raise SystemExit('chronology mismatch')
    ask,bid=p75(t,d.ask_raw.to_numpy(np.int64),d.bid_raw.to_numpy(np.int64))
    configs={}
    for name,fam,tf in (
        ('17CS_123NB_M1','R037-123NB-v1',60_000),('17CT_123NB_M5','R037-123NB-v1',300_000),
        ('17CU_MSNR_DBO_M1','R037-MSnR-DBO-v1',60_000),('17CV_MSNR_DBO_M5','R037-MSnR-DBO-v1',300_000)):
        z=bars(t,bid,tf)
        if fam=='R037-123NB-v1': ix,sd,diag=sig_123(t,ask,bid,z,3)
        else: ix,sd,diag=sig_msnr(t,ask,bid,z,120)
        m,g=pack(ix,sd,t,ask,bid)
        configs[name]={'family':fam,'bar_ms':tf,'metrics':m,'gate':g,'diagnostics':diag}
    surv=[n for n,v in configs.items() if v['gate']['screen_pass']]
    surv.sort(key=lambda n:(configs[n]['metrics']['direct_net_usd'],configs[n]['metrics']['official_wins'],configs[n]['metrics']['trades']),reverse=True)
    out={'schema':'delta-r037-structural-state-machine-harvest-17cs-17cv-v1','status':'COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN','unit':'R037_HIGH_VALUE_STRUCTURAL_STATE_MACHINE_HARVEST_CHECKPOINT_17CS_17CV','parent_checkpoint':'R037_XECTSB_LEADER_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17CR','prereg_commit':PREREG,'source_sha256':hs,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75','configs':configs,'finding':{'survivors':surv,'leader':surv[0] if surv else None,'decision':'ADVANCE_LEADER_TO_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'RETIRE_BOTH_STRUCTURAL_FAMILIES_NO_STAGE_A_SURVIVOR','next':'R037_STRUCTURAL_LEADER_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST'},'numeric_retuning':False,'post_result_rescue':False,'august_accessed':False,'mql5_authorized':False,'runtime_seconds':round(time.monotonic()-st,3)}
    atomic_json(x.output,out)
    print(json.dumps({'configs':{n:{'trades':v['metrics']['trades'],'days':v['metrics']['distinct_days'],'wins':v['metrics']['official_wins'],'net':v['metrics']['direct_net_usd'],'pass':v['gate']['screen_pass'],'diag':v['diagnostics']} for n,v in configs.items()},'finding':out['finding'],'runtime_seconds':out['runtime_seconds']},separators=(',',':')))

if __name__=='__main__': main()
