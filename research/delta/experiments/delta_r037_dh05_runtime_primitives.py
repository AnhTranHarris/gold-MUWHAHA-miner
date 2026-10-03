from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
import numpy as np
from numba import njit

DAY_MS=86_400_000
TICK_RAW=10
STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000
UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'

VECTORS=(
('A03',.3,15,40,20,.15,.08,.12,.5,5),
('S05',.374062,15,9.099416,6.468982,.244588,.093793,.217011,.062661,5),
('S06',.217738,5,59.699117,23.47226,.029179,.145085,.041213,.673017,1),
('S09',.329294,15,41.910749,10.844137,.335024,.12735,.272984,.126644,1),
('S10',.26416,5,20.537168,19.210606,.108825,.077129,.088265,.644213,5),
('S16',.18608,5,31.219954,3.711492,.279091,.121753,.206212,.746067,5))

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):
            h.update(block)
    return h.hexdigest()

def atomic_write_json(path:Path,payload:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp_name=None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',encoding='utf-8',newline='\n',
            prefix=f'.{path.name}.',suffix='.tmp',dir=path.parent,delete=False
        ) as tmp:
            tmp_name=tmp.name
            json.dump(payload,tmp,indent=2)
            tmp.write('\n')
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name,path)
        tmp_name=None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass

def session_code(t):
    tod=t%DAY_MS
    ls=np.where(t>=UK_DST_START_2026_MS,7,8)*3_600_000
    le=ls+8*3_600_000+30*60_000
    ns=np.where(t>=US_DST_START_2026_MS,12,13)*3_600_000
    ne=ns+9*3_600_000
    il=(tod>=ls)&(tod<le)
    iny=(tod>=ns)&(tod<ne)
    return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,a,b):
    s=session_code(t)
    sp=P75_POINTS[s]*TICK_RAW
    mid2=a.astype(np.int64)+b.astype(np.int64)
    bid=((mid2-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
    return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,mid2,tf):
    bucket=t//tf
    st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    en=np.r_[st[1:],len(t)]
    return {
        'end_ms':((bucket[st]+1)*tf).astype(np.int64),
        'open':mid2[st].astype(np.int64),
        'close':mid2[en-1].astype(np.int64),
        'high':np.maximum.reduceat(mid2,st).astype(np.int64),
        'low':np.minimum.reduceat(mid2,st).astype(np.int64)
    }

def atr14(b):
    h,l,c=b['high'],b['low'],b['close']
    tr=(h-l).copy()
    if len(tr)>1:
        tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
    cs=np.r_[0,np.cumsum(tr,dtype=np.int64)]
    out=np.zeros(len(tr),dtype=np.float64)
    for i in range(13,len(tr)):
        out[i]=(cs[i+1]-cs[i-13])/14.0
    return out

def symmetric_swings(b,w=2):
    hi,lo,end=b['high'],b['low'],b['end_ms']
    rev=[]; side=[]; lev=[]
    for k in range(w,len(hi)-w):
        h=hi[k]; l=lo[k]
        ish=all(h>hi[k-j] and h>hi[k+j] for j in range(1,w+1))
        isl=all(l<lo[k-j] and l<lo[k+j] for j in range(1,w+1))
        reveal=int(end[k+w])
        if ish:
            rev.append(reveal); side.append(1); lev.append(int(h))
        if isl:
            rev.append(reveal); side.append(-1); lev.append(int(l))
    arr=np.asarray(rev,np.int64)
    order=np.argsort(arr,kind='stable')
    return arr[order],np.asarray(side,np.int8)[order],np.asarray(lev,np.int64)[order]

@njit(cache=True)
def bidx(end,tm):
    return np.searchsorted(end,tm,side='right')-1

@njit(cache=True)
def admit_r9_lifecycle(t,ask,bid,sig_i,sig_side,block_exit_tick):
    STOP=300
    TRAIL_ACT=100
    TRAIL_DIST=30
    n=sig_i.size
    admitted=0; rejected_occupied=0; rejected_latch=0; wins=0
    gp=0.; gl=0.; balance=100000.; peak=balance; maxdd=0.
    pos=0; entry=0; stop=0; entrysec=0; k=0; hold_sum=0.; closed_trades=0
    last_i=t.size-1

    for i in range(t.size):
        sec=int(t[i])//1000
        exited=False
        if pos!=0:
            ex=0
            do_exit=False
            if pos>0:
                if int(bid[i])<=stop:
                    ex=int(bid[i]); do_exit=True
            else:
                if int(ask[i])>=stop:
                    ex=int(ask[i]); do_exit=True
            if (not do_exit) and sec-entrysec>=30:
                ex=int(bid[i]) if pos>0 else int(ask[i])
                do_exit=True
            if do_exit:
                raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)
                exit_deal=raw-0.01
                if exit_deal>1e-12:
                    wins+=1
                if raw>0:
                    gp+=exit_deal
                else:
                    gl+=exit_deal
                balance+=exit_deal
                closed_trades+=1
                hold_sum+=sec-entrysec
                if balance>peak:
                    peak=balance
                dd=peak-balance
                if dd>maxdd:
                    maxdd=dd
                pos=0; entry=0; stop=0
                exited=True
            else:
                if pos>0 and int(bid[i])-entry>=TRAIL_ACT:
                    ns=int(bid[i])-TRAIL_DIST
                    if ns>stop:
                        stop=ns
                elif pos<0 and entry-int(ask[i])>=TRAIL_ACT:
                    ns=int(ask[i])+TRAIL_DIST
                    if ns<stop:
                        stop=ns

        while k<n and int(sig_i[k])==i:
            if pos!=0:
                rejected_occupied+=1
            elif exited and block_exit_tick:
                rejected_latch+=1
            else:
                pos=int(sig_side[k])
                entry=int(ask[i]) if pos>0 else int(bid[i])
                stop=int(bid[i])-STOP if pos>0 else int(ask[i])+STOP
                entrysec=sec
                admitted+=1
                balance-=0.01
                gl-=0.01
                if balance>peak:
                    peak=balance
                dd=peak-balance
                if dd>maxdd:
                    maxdd=dd
            k+=1

    if pos!=0:
        ex=int(bid[last_i]) if pos>0 else int(ask[last_i])
        raw=((ex-entry)/1000.0 if pos>0 else (entry-ex)/1000.0)
        exit_deal=raw-0.01
        if exit_deal>1e-12:
            wins+=1
        if raw>0:
            gp+=exit_deal
        else:
            gl+=exit_deal
        balance+=exit_deal
        closed_trades+=1
        hold_sum+=(int(t[last_i])//1000)-entrysec
        if balance>peak:
            peak=balance
        dd=peak-balance
        if dd>maxdd:
            maxdd=dd

    return admitted,rejected_occupied,rejected_latch,closed_trades,wins,gp,gl,gp+gl,maxdd,(hold_sum/closed_trades if closed_trades else 0.0)
