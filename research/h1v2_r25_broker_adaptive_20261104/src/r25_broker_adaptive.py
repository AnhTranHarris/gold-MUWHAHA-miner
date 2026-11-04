"""R25 additive XAUUSD two-feed, source-ordinal-exact BROKER-ADAPTIVE ENTRY LAB.

Research only. Retains R24's ORIGINAL source epoch, first observed +100ms fill,
Bid/Ask, causal prefix extraction and exact dyadic FIRST passage engine;
adds a state-conditioned triple exit geometry and as-of quote-mark intensity.
All calls from a signal action to signal features use source ordinals <=signal.
Future price paths are used ONLY to produce offline labels, simulated exits,
and separate hindsight upper benchmarks. No MT5 broker dealing execution.
"""
from __future__ import annotations
import hashlib, json, sys
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from numba import njit
from scipy.special import softmax

ROOT=Path('/mnt/data')
HERE=Path(__file__).resolve().parent
RESEARCH_DIR=HERE.parent.parent
# Exact GitHub ancestor modules are version-pinned at branch f439e870....
# Prefer upstream research source in a cloned repo; local offline research
# workspace uses byte-exact frozen copies of the verified SHA-pinned modules.
sys.path.insert(0,str(HERE))
for ancestor in (
    RESEARCH_DIR/'h1v2_r23_hourly_causal_20261104/frozen_r24_archive/source',
    RESEARCH_DIR/'h1v2_r23h7_broker_session_ordinal_20261104/src',
):
    if ancestor.is_dir():sys.path.insert(0,str(ancestor))
import r24_firstpass_engine as r24
from r23h7_quote_grammar import quote_path_features, PATH_NAMES

SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
MONTHS=('01','02','06','07')
LANES=('SPREAD_RECLAIM_H15','CROSS_SCALE_H30','REGIME_RUNNER_H60')
H_MS=np.asarray([15000,30000,60000],dtype=np.int64)
STOP,TARGET,TIMEOUT,CENSORED,UNFILLED=0,1,2,3,4
FEE_RAW=20
DURATION_GAP_MS=15000
REGIME_NAMES=('QUOTE_CALM','SPREAD_EXHAUSTION','FAST_REPRICING','MARK_DIVERGENCE')

@dataclass(frozen=True)
class Window:
    source:str
    month:str
    day:int
    ordinal_origin:int
    t:np.ndarray
    b:np.ndarray
    a:np.ndarray
    signals:np.ndarray
    gapstarts:np.ndarray
    refq:np.ndarray
    ref_utc_ms:np.ndarray


def verify_gzip(source,month,pins):
    p=r24.source_file(source,month)
    with p.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=pins[p.name]['sha256']:
        raise RuntimeError(f'RAW_SOURCE_HASH_DRIFT {p.name} {actual}')
    return {'filename':p.name,'sha256':actual,'bytes':p.stat().st_size}


def day_window(source,mon,day,*,decision_ms=1000,spread_cap=6000,history_ms=28800000):
    """Use the original R24 source clock and actual bid/ask, with 8h prefix context.

    Refuses to pretend that an unloaded prior month exists. Records original
    month-wide quote ordinal offset, so local slice ordinals can be translated.
    """
    if source not in SOURCES or mon not in MONTHS:raise ValueError('source/month')
    start=int(datetime(2026,int(mon),day,tzinfo=timezone.utc).timestamp()*1000)
    end=start+86400000
    full_t,full_b,full_a=r24.raw_month(source,mon,verify=False)
    lo=int(np.searchsorted(full_t,start-history_ms,'left'))
    hi=int(np.searchsorted(full_t,end+75000,'right'))
    if lo>=hi:raise RuntimeError('EMPTY_SOURCE_DAY_WITH_CONTEXT')
    t=full_t[lo:hi].copy();b=full_b[lo:hi].copy();a=full_a[lo:hi].copy()
    candidates,gapstarts=r24.candidates(t,b,a,decision_ms=decision_ms,cap=spread_cap)
    signals=candidates[(t[candidates]>=start)&(t[candidates]<end)]
    qtime,qr=r24.calendar_reference(mon)
    take=(qtime>=start)&(qtime<end)
    if int(take.sum())!=96:raise AssertionError('SOURCE_REFERENCE_MISSING_96_QUARTERS')
    if signals.size and np.any(t[signals[1:]]<=t[signals[:-1]]):raise AssertionError('SOURCE_SIGNAL_ORDER')
    return Window(source,mon,day,lo,t,b,a,signals,gapstarts,qr[take],qtime[take])


@njit(cache=False)
def _asof_decayed_marks(t,b,a,signals):
    """Exp kernels applied to level-I QUOTE revisions, not fictional L2 volume.

    Each 64-quote causal prefix is integrated across multiple decays; no
    future quote ordinal, candle OHLC or later same-ms revision is visited.
    """
    out=np.zeros((len(signals),12),dtype=np.float32)
    tau=np.array([250.0,2000.0,15000.0],dtype=np.float64)
    for i in range(len(signals)):
        s=signals[i]
        if s<1:continue
        k=64 if s>=64 else s
        tiny=1.e-6
        acc_bid=np.zeros(3,np.float64)
        acc_ask=np.zeros(3,np.float64)
        sum_bid=np.zeros(3,np.float64)
        sum_ask=np.zeros(3,np.float64)
        now=t[s]
        for j in range(s-k+1,s+1):
            db=b[j]-b[j-1];da=a[j]-a[j-1]
            age=now-t[j]
            if age<0:raise ValueError('FORWARD_MARK_AT_SIGNAL')
            for m in range(3):
                w=np.exp(-age/tau[m])
                acc_bid[m]+=np.sign(db)*w
                acc_ask[m]+=np.sign(da)*w
                sum_bid[m]+=abs(db)*w
                sum_ask[m]+=abs(da)*w
        for m in range(3):
            out[i,m]=acc_bid[m]/(1.0+sum_bid[m]/100.0)
            out[i,m+3]=acc_ask[m]/(1.0+sum_ask[m]/100.0)
            out[i,m+6]=(acc_bid[m]-acc_ask[m])/(1+abs(acc_bid[m])+abs(acc_ask[m]))
            out[i,m+9]=(sum_bid[m]+sum_ask[m])/(1.0+(now-t[s-k])/1000.0)
    return out


def asof_features(w):
    """Only original past R24+R23H7 and R25 decayed quote-mark features."""
    s=w.signals
    if not len(s):return np.empty((0,len(r24.FEATURE_NAMES)+16+12),np.float32)
    x=r24.extract_features(w.t,w.b,w.a,s,w.gapstarts,w.source)
    g=quote_path_features(w.t,w.b,w.a,s)
    d=_asof_decayed_marks(w.t,w.b,w.a,s)
    ans=np.ascontiguousarray(np.column_stack((x,g,d)),dtype=np.float32)
    if not np.isfinite(ans).all():raise AssertionError('NONFINITE_ASOF_FEATURE')
    return ans


def quote_geometry(w,x):
    """As-of broker adaptive 15/30/60 risk variants.

    Target = net source quoted-price units above fee, converted after fill to
    liquidating Bid (BUY) / Ask (SELL); STOP is adverse liquidation excursion
    from the first LIQUIDATION quote, NOT from the entry deal quote.
    """
    if len(x)!=len(w.signals):raise AssertionError('FEATURE_SHAPE')
    spread=(w.a[w.signals].astype(np.int64)-w.b[w.signals].astype(np.int64))
    n=len(spread)
    b15=np.abs(x[:,r24.FEATURE_NAMES.index('bid_move_15s')]).astype(np.float64)
    a15=np.abs(x[:,r24.FEATURE_NAMES.index('ask_move_15s')]).astype(np.float64)
    quote15=x[:,r24.FEATURE_NAMES.index('quotes_15s')].astype(np.float64)
    rv15=x[:,r24.FEATURE_NAMES.index('abs_bid_rv_15s')].astype(np.float64)
    range_proxy=np.maximum.reduce((np.full(n,100.),b15,a15,rv15*np.sqrt(np.maximum(quote15,1))))
    tp=np.empty((n,3),dtype=np.int32);st=np.empty((n,3),dtype=np.int32)
    configs=((100,0.35,0.30,100,0.20,0.20),(150,0.80,0.50,100,0.30,0.30),(250,1.50,0.65,150,0.50,0.45))
    for k,(base_t,mult_s,mult_r,base_stop,stop_s,stop_r) in enumerate(configs):
        tp[:,k]=np.clip(np.maximum.reduce((np.full(n,base_t),mult_s*spread,mult_r*range_proxy)),base_t,20000).astype(np.int32)
        st[:,k]=np.clip(np.maximum.reduce((np.full(n,base_stop),stop_s*spread,stop_r*range_proxy)),base_stop,10000).astype(np.int32)
    return tp,st


@njit(cache=False)
def _label_six(t,b,a,signal,fill,tp,st,first_gap,size,bmax,bmin,amax,amin):
    """Frozen R24 first-crossing dyadic search, dynamic target/stop per lane.

    Future quote access is confined to THIS OFFLINE LABELER. Outputs include
    exact source quote exit ordinal, not an idealized t_fill + H reservation.
    """
    n=len(signal)
    codes=np.full((n,2,3),UNFILLED,np.int8)
    exits=np.full((n,2,3),-1,np.int32)
    retnet=np.full((n,2,3),np.nan,np.float32)
    for i in range(n):
        f=fill[i]
        if f<0:continue
        for hidx in range(3):
            deadline=t[f]+H_MS[hidx]
            rb=np.searchsorted(t,deadline,side='right')
            cap=rb
            if first_gap[i]<cap:cap=first_gap[i]
            if cap<f+1:cap=f+1
            close_idx=np.searchsorted(t,deadline,side='left')
            quote_censored=(first_gap[i]<=close_idx or close_idx>=len(t))
            if close_idx<len(t) and t[close_idx]-deadline>DURATION_GAP_MS:
                quote_censored=True
            for side in range(2):
                target=int(tp[i,hidx]);stop=int(st[i,hidx])
                if side==0:
                    hit,cause=r24.first_crossing(bmax,bmin,size,f+1,cap,int(a[f])+FEE_RAW+target,int(b[f])-stop)
                else:
                    hit,rawcause=r24.first_crossing(amax,amin,size,f+1,cap,int(a[f])+stop,int(b[f])-FEE_RAW-target)
                    cause=0 if rawcause==1 else (1 if rawcause==0 else -1)
                if hit>=0 and t[hit]<=deadline:
                    codes[i,side,hidx]=np.int8(cause)
                    exits[i,side,hidx]=np.int32(hit)
                elif quote_censored:
                    codes[i,side,hidx]=CENSORED
                else:
                    codes[i,side,hidx]=TIMEOUT
                    exits[i,side,hidx]=np.int32(close_idx)
                e=exits[i,side,hidx]
                if e>=0:
                    if side==0:retnet[i,side,hidx]=np.float32(b[e]-a[f]-FEE_RAW)
                    else:retnet[i,side,hidx]=np.float32(b[f]-a[e]-FEE_RAW)
    return codes,exits,retnet


def offline_labels(w,tp,st,lag_ms=100,fill_cap=6000):
    if len(tp)!=len(w.signals) or tp.shape!=st.shape or tp.shape[1]!=3:raise ValueError('GEOMETRY_SHAPE')
    f=r24.fill_after(w.t,w.b,w.a,w.signals,lag=lag_ms,fillcap=fill_cap,stale=1000)
    n=len(f);gap=np.flatnonzero(np.diff(w.t)>DURATION_GAP_MS).astype(np.int32)+1
    if len(gap):
        at=np.searchsorted(gap,np.maximum(f,0)+1,side='left')
        ng=np.full(n,len(w.t),np.int32)
        valid=at<len(gap)
        ng[valid]=gap[at[valid]]
    else:ng=np.full(n,len(w.t),np.int32)
    size,bmax,bmin,amax,amin=r24.build_tree(w.b,w.a)
    codes,exits,net=_label_six(w.t,w.b,w.a,w.signals,f,tp,st,ng,size,bmax,bmin,amax,amin)
    if not np.all((codes>=0)&(codes<=4)):raise AssertionError('INVALID_FUTURE_LABEL')
    if np.any((codes==TARGET)&(net<=0)):raise AssertionError('TARGET_NOT_NET_POSITIVE')
    return {'fill':f,'cause':codes,'exit':exits,'net':net}


def hindsight_cardinality(w,labels):
    """Future-selected first-target ceiling; never a causal policy result.

    Earliest-exit greedily selects disjoint *source observed* intervals across
    ALL 6 side×horizon geometry lanes. Bound conditional on THIS universe.
    """
    f=labels['fill'];c=labels['cause'];exits=labels['exit']
    i,side,lan=np.where(c==TARGET)
    if not len(i):return np.empty((0,5),np.int64)
    ft=w.t[f[i]];et=w.t[exits[i,side,lan]]
    order=np.lexsort((i,ft,et))
    chosen=[];last=-np.iinfo(np.int64).max
    for j in order:
        if ft[j]>last:
            chosen.append((i[j],side[j],lan[j],f[i[j]],exits[i[j],side[j],lan[j]]))
            last=int(et[j])
    arr=np.asarray(chosen,dtype=np.int64).reshape((-1,5))
    if len(arr)>1:
        start=w.t[arr[:,3]];end=w.t[arr[:,4]]
        if np.any(start[1:]<=end[:-1]):raise AssertionError('HINDSIGHT_OVERLAP')
    return arr


def action_features(x,tp,st,source):
    """Six projected action choices formed from immutable causal prefix rows."""
    if x.shape[0]!=tp.shape[0]:raise ValueError('ROWS')
    n=len(x);p=x.shape[1]
    out=np.empty((n*6,p+5),dtype=np.float32)
    s=np.repeat(np.arange(n),6)
    out[:,:p]=x[s]
    out[:,p]=np.tile([1.,1.,1.,-1.,-1.,-1.],n)
    out[:,p+1]=np.tile(H_MS.astype(np.float32)/1000.0,2*n)
    out[:,p+2]=np.tile(tp,(1,2)).reshape(-1)
    out[:,p+3]=np.tile(st,(1,2)).reshape(-1)
    out[:,p+4]=(out[:,p+2]/(100.0+np.maximum(out[s,p] if False else out[:,1],0)))
    return out


def one_position_replay(w,labels,choice,*,include_attempts=False):
    """Chronological causal-selected single position, fail closed on gap.

    choice: (n,2) [chosen action index in 0..5 or -1 for WAIT, risk score]
    where 0..2 are BUY H15/30/60; 3..5 SELL H15/30/60.
    """
    n=len(w.signals)
    if choice.shape!=(n,2):raise ValueError('ACTION_SHAPE')
    trades=[];busy_through=-2**62;blocked=0;attempts=0
    for i in range(n):
        now=int(w.t[w.signals[i]])
        if now<=busy_through:continue
        act=int(choice[i,0]);
        if act<0:continue
        if act>5:raise ValueError('INVALID_ACTION')
        side=act//3;lan=act%3;attempts+=1
        f=int(labels['fill'][i]);
        if f<0:
            blocked+=1
            busy_through=now+1100
            if include_attempts:trades.append({'signal_index':i,'source_ordinal':w.ordinal_origin+int(w.signals[i]),'signal_utc_ms':now,'fill_utc_ms':None,'action':act,'status':UNFILLED})
            continue
        code=int(labels['cause'][i,side,lan]);e=int(labels['exit'][i,side,lan]);
        if code==CENSORED or e<0:
            busy_through=2**62-1
        else:
            busy_through=int(w.t[e])
        record={'signal_index':i,'source_signal_ordinal':w.ordinal_origin+int(w.signals[i]),
                'signal_utc_ms':now,'fill_source_ordinal':w.ordinal_origin+f,
                'fill_utc_ms':int(w.t[f]),'action':act,'side':side,'lane':lan,
                'source_exit_ordinal':w.ordinal_origin+e if e>=0 else -1,
                'exit_utc_ms':int(w.t[e]) if e>=0 else None,'status':code,
                'net_source_price_raw':float(labels['net'][i,side,lan]),
                'predicted_risk_score':float(choice[i,1])}
        trades.append(record)
    return trades,{'attempts':attempts,'unfilled':blocked,'completed':sum(r.get('status') in (STOP,TARGET,TIMEOUT) for r in trades),'unknown':sum(r.get('status')==CENSORED for r in trades)}


def hourly_quarter_report(w,trades):
    """Preserves ALL 96 quarters, 24 hours and one full UTC day of references.

    Volume means FILLED completed or censored positions, never rejected orders.
    Correctness denominator completed known STOP/TARGET/TIMEOUT, not censored.
    """
    qr=w.refq;qt=w.ref_utc_ms;start=int(qt[0]);
    filled=np.zeros(96,np.int32);win=np.zeros(96,np.int32);loss=np.zeros(96,np.int32);cens=np.zeros(96,np.int32)
    net=np.zeros(96,np.float64)
    for r in trades:
        if not r.get('fill_utc_ms'):continue
        q=(r['fill_utc_ms']-start)//900000
        if 0<=q<96:
            q=int(q);filled[q]+=1
            if r['status']==TARGET:win[q]+=1
            if r['status']==STOP or r['status']==TIMEOUT:loss[q]+=1
            if r['status']==CENSORED:cens[q]+=1
            if np.isfinite(r['net_source_price_raw']):net[q]+=r['net_source_price_raw']
    qreports=[]
    for k in range(96):
        completed=int(win[k]+loss[k]);ref=int(qr[k]);
        p=win[k]/completed if completed else None
        qreports.append({'utc_quarter_ms':int(qt[k]),'r9_synth_reference':ref,
            'filled':int(filled[k]),'tp_first':int(win[k]),'stopped_or_timed':int(loss[k]),'censored':int(cens[k]),
            'precision_completed':p,'volume_pass':bool(ref>0 and filled[k]>=ref),
            'joint_80_and_volume':bool(ref>0 and filled[k]>=ref and p is not None and p>=.8),
            'known_net_source_price_raw':round(float(net[k]),4)})
    hs=[]
    for h in range(24):
        sl=slice(h*4,h*4+4);ref=int(qr[sl].sum());N=int(filled[sl].sum());g=int(win[sl].sum());bad=int(loss[sl].sum());cp=g/(g+bad) if g+bad else None
        hs.append({'utc_hour_ms':int(qt[h*4]),'r9_synth_reference':ref,'filled':N,
                   'tp_first':g,'stopped_or_timed':bad,'censored':int(cens[sl].sum()),
                   'precision_completed':cp,'volume_pass':bool(ref>0 and N>=ref),
                   'joint_80_and_volume':bool(ref>0 and N>=ref and cp is not None and cp>=.8),
                   'known_net_source_price_raw':round(float(net[sl].sum()),4)})
    return qreports,hs
