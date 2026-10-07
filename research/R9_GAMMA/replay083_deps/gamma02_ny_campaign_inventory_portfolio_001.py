import sys,json,time,numpy as np
from numba import njit
sys.path.insert(0,"/mnt/data")
import gamma02_m1_density as gmd

@njit(cache=True)
def build_perm_extension_events(t,mid,h4,h1,m15,m5,perm_mode, step_raw=50, max_events_min=200):
    cap=4000000
    idxs=np.empty(cap,np.int64); dirs=np.empty(cap,np.int8); hrs=np.empty(cap,np.int8)
    sess=np.empty(cap,np.int8); disps=np.empty(cap,np.int32)
    n=0;cur_min=np.int64(-1);anchor=0;last_ext=0;events=0;lastd=0
    for i in range(t.size):
        ti=t[i];midx=int(mid[i]);minute=(ti//60000)*60000
        if minute!=cur_min:
            cur_min=minute;anchor=midx;last_ext=0;events=0;lastd=0;continue
        hr=int((ti//3600000)%24)
        if hr<16 or hr>18:continue
        d=gmd.permit(perm_mode,h4[i],h1[i],m15[i],m5[i])
        if d==0:continue
        if lastd!=0 and d!=lastd:
            anchor=midx;last_ext=0;events=0
        lastd=d
        disp=(midx-anchor)*d
        if disp<=last_ext or events>=max_events_min:continue
        next_step=((last_ext//step_raw)+1)*step_raw
        while disp>=next_step and events<max_events_min:
            last_ext=next_step;next_step+=step_raw;events+=1
            if n>=cap:return idxs[:n],dirs[:n],hrs[:n],sess[:n],disps[:n]
            idxs[n]=i;dirs[n]=d;hrs[n]=hr;sess[n]=gmd.c.sess_fixed(ti);disps[n]=last_ext;n+=1
    return idxs[:n],dirs[:n],hrs[:n],sess[:n],disps[:n]


@njit(cache=True)
def precompute_outcomes(t,a,b,ev_idx,ev_dir,tp_raw,sl_raw,hold_ms):
    n=ev_idx.size
    exit_t=np.empty(n,np.int64); pnl=np.empty(n,np.float64); reason=np.empty(n,np.int8)
    for k in range(n):
        i0=int(ev_idx[k]); d=int(ev_dir[k]); e=int(a[i0] if d>0 else b[i0])
        endt=t[i0]+hold_ms
        j=i0+1
        ex=e; rs=3
        while j<t.size:
            if t[j]>=endt:
                ex=int(b[j] if d>0 else a[j]); rs=3; break
            px=int(b[j] if d>0 else a[j])
            if d>0:
                if tp_raw>0 and px>=e+tp_raw:
                    ex=px;rs=1;break
                if sl_raw>0 and px<=e-sl_raw:
                    ex=px;rs=2;break
            else:
                if tp_raw>0 and px<=e-tp_raw:
                    ex=px;rs=1;break
                if sl_raw>0 and px>=e+sl_raw:
                    ex=px;rs=2;break
            j+=1
        if j>=t.size:
            j=t.size-1; ex=int(b[j] if d>0 else a[j]);rs=3
        exit_t[k]=t[j]
        pnl[k]=((ex-e)*d)/1000.0-0.02
        reason[k]=rs
    return exit_t,pnl,reason


@njit(cache=True)
def cap_select(ev_times,exit_t,pnl,reason,source,cap):
    active_end=np.zeros(512,np.int64)
    n=ev_times.size
    acc_exit=np.empty(n,np.int64);acc_pnl=np.empty(n,np.float64);acc_src=np.empty(n,np.int8);acc_reason=np.empty(n,np.int8)
    accepted=0;skips=0;maxopen=0
    for k in range(n):
        now=ev_times[k]
        open_n=0
        for z in range(cap):
            if active_end[z]!=0 and active_end[z]<=now:active_end[z]=0
            if active_end[z]!=0:open_n+=1
        if open_n>=cap:
            skips+=1;continue
        q=-1
        for z in range(cap):
            if active_end[z]==0:q=z;break
        if q<0:
            skips+=1;continue
        active_end[q]=exit_t[k]
        acc_exit[accepted]=exit_t[k];acc_pnl[accepted]=pnl[k];acc_src[accepted]=source[k];acc_reason[accepted]=reason[k]
        accepted+=1
        if open_n+1>maxopen:maxopen=open_n+1
    return acc_exit[:accepted],acc_pnl[:accepted],acc_src[:accepted],acc_reason[:accepted],skips,maxopen


SIG16={(-1,-1,-1,-1,-1),(1,1,1,-1,1),(1,1,-1,1,1)}
SIG17={(-1,-1,-1,-1,-1),(1,1,-1,-1,1)}
SIG18={(-1,-1,-1,-1,-1)}

def make_sig_spec(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,edisp,hour,step,tp,sl,hold_ms,allowed):
    base=(eh==hour)&(ess==4)&((edisp%step)==0)
    p=np.nonzero(base)[0]
    idx=ei[p]; dr=ed[p]
    keep=np.zeros(idx.size,dtype=np.bool_)
    for k,i in enumerate(idx):
        sig=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(dr[k]))
        if sig in allowed: keep[k]=True
    idx=idx[keep];dr=dr[keep]
    times=t[idx]
    exits,pnl,reason=precompute_outcomes(t,a,b,idx,dr,tp,sl,hold_ms)
    src=np.full(times.size,hour,dtype=np.int8)
    return times,exits,pnl,reason,src

def summarize(exit_t,pnl,src,reason,skips,maxopen):
    order=np.argsort(exit_t,kind="stable")
    p=pnl[order];s=src[order]
    bal=np.cumsum(p)
    if p.size:
        prior=np.r_[0.0,bal[:-1]]
        peak=np.maximum.accumulate(prior)
        bdd=float(np.max(peak-bal))
    else:bdd=0.0
    gp=float(p[p>0].sum());gl=float(p[p<=0].sum())
    out=dict(net=float(p.sum()),gp=gp,gl=gl,trades=int(p.size),wins=int((p>0).sum()),
             skips=int(skips),maxopen=int(maxopen),balance_dd=bdd,
             pf=float(gp/-gl if gl<0 else 999),exp=float(p.mean() if p.size else 0),
             win=float(np.mean(p>0) if p.size else 0))
    out["sources"]={}
    for h in np.unique(s):
        q=p[s==h];g=float(q[q>0].sum());l=float(q[q<=0].sum())
        out["sources"][str(int(h))]=dict(net=float(q.sum()),trades=int(q.size),
            pf=float(g/-l if l<0 else 999),exp=float(q.mean() if q.size else 0))
    return out

def run(cap):
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep()
    ei,ed,eh,ess,edisp=build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200)
    # 16 UTC inventory: 10 min, no fixed TP, $12 stop
    s16=make_sig_spec(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,edisp,16,50,0,12000,600000,SIG16)
    # 17 UTC primary campaign: 30 min, $80 TP / $20 SL
    s17=make_sig_spec(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,edisp,17,50,80000,20000,1800000,SIG17)
    # 18 UTC fast harvest: 15 sec, $4/$4
    s18=make_sig_spec(t,a,b,h4,h1,m15,m5,ei,ed,eh,ess,edisp,18,50,4000,4000,15000,SIG18)
    specs=[s16,s17,s18]
    arrays=[]
    for q in range(5):
        arrays.append(np.concatenate([s[q] for s in specs]))
    order=np.argsort(arrays[0],kind="stable")
    arrays=[x[order] for x in arrays]
    ae,ap,asrc,ar,sk,mo=cap_select(*arrays,int(cap))
    out=summarize(ae,ap,asrc,ar,sk,mo)
    out["cap"]=int(cap)
    return out

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--cap",type=int,default=64)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    st=time.time();obj=run(args.cap);obj["elapsed_s"]=round(time.time()-st,3)
    with open(args.out,"w") as f:json.dump(obj,f,indent=2)
    print(json.dumps(obj))