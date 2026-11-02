"""H1V2: strictly OFFLINE, source-exact, four-month real-tick hindsight teacher.

No future labels enter causal features or a deployable policy. Underlying R9 entry:
BUY ask/exit bid; SELL bid/exit ask; stop 0.30 from opening liquidation
quote; trailing activation gross +0.10 -> 0.03 behind liquidation;
close at first quote >=30s or earlier stop; research fee $0.02.

H1V2 strict criterion: first executable +$0.10 net BEFORE the first
-$0.10 change from opening liquidation quote, observed <=30s; original
R9-style closing net strictly >0 and closing timestamp <=30s. All close
positions and quote indices are nonoverlapping within oracle schedule.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, time
import numpy as np
import pandas as pd
from numba import njit

MONTHS=('01','02','06','07')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
FEE=.02;HOLD_MS=30000

@njit(cache=True)
def _round_tick(x):
    return np.floor(x/.01+.5)*.01

@njit(cache=True)
def candidate_250ms(t,bid,ask,max_spread=1.50,warmup_ms=300000,gap_reset_ms=300000):
    """First observed quote of an occupied 250ms slot (causal), no synthetic fills.

    Never use the last quote in a bin: that needs knowledge of the NEXT quote
    to prove no more quotes will arrive inside the current bin.
    """
    ix=np.empty(len(t),np.int64);n=0
    first=t[0]
    for i in range(len(t)):
        if i and t[i]-t[i-1]>=gap_reset_ms: first=t[i]
        first_in_bin=(i==0 or t[i]//250!=t[i-1]//250)
        if not first_in_bin or t[i]-first<warmup_ms:continue
        if ask[i]<bid[i] or ask[i]-bid[i]>max_spread:continue
        ix[n]=i;n+=1
    return ix[:n]

@njit(cache=True)
def replay_buy_sell_30s(t,bid,ask,entries,fee=FEE):
    """Exact quote-ordinal R9-style stop/trail replay; offline future ONLY.

    We skip later quotes with equal ENTRY timestamp, matching ActivePath.update.
    Does not change the original external ActivePath implementation.
    """
    n=len(entries)
    code=np.zeros((n,2),np.int8)  # +1 correct, -1 wrong, 0 neutral
    value=np.full((n,2),np.nan,np.float32)
    first=np.zeros((n,2),np.int8)
    first_ms=np.full((n,2),-1,np.int32)
    out_ix=np.full((n,2),-1,np.int64)
    out_ms=np.full((n,2),-1,np.int32)
    for k in range(n):
        i=entries[k];t0=t[i]
        for option in range(2):
            side=1 if option==0 else -1
            enter=ask[i] if side==1 else bid[i]
            liq0=bid[i] if side==1 else ask[i]
            stop=_round_tick(liq0-side*.30)
            first_cause=0;cause_elapsed=-1
            for j in range(i+1,len(t)):
                if t[j]==t0:continue
                px=bid[j] if side==1 else ask[j]
                gross=(px-enter)*side
                net=gross-fee
                elapsed=t[j]-t0
                move=(px-liq0)*side
                if first_cause==0 and elapsed<=HOLD_MS:
                    if net>=.10-1e-9:
                        first_cause=1;cause_elapsed=elapsed
                    elif move<=-.10+1e-9:
                        first_cause=-1;cause_elapsed=elapsed
                stop_hit=(px<=stop+1e-10 if side==1 else px>=stop-1e-10)
                if not stop_hit and gross>=.10-1e-12:
                    s=_round_tick(px-side*.03)
                    if side==1:
                        if s>stop:stop=s
                    else:
                        if s<stop:stop=s
                if stop_hit or elapsed>=HOLD_MS:
                    value[k,option]=net
                    out_ix[k,option]=j
                    out_ms[k,option]=elapsed
                    first[k,option]=first_cause
                    first_ms[k,option]=cause_elapsed
                    if first_cause==1 and net>0 and elapsed<=HOLD_MS:
                        code[k,option]=1
                    elif first_cause==-1 or (stop_hit and net<0 and elapsed<=HOLD_MS):
                        code[k,option]=-1
                    break
    return code,value,first,first_ms,out_ix,out_ms


def schedule_oracle(entries,code,net,exit_ix):
    """Future-privileged optimal max-count *nonoverlapping* interval schedule.

    Primary objective: number of qualifying correct outcomes; secondary:
    executable positive net. It is a hindsight upper bound, NOT a policy.
    Action starts at observed index and next begins strictly after exit index.
    """
    entries=np.asarray(entries,dtype=np.int64)
    n=len(entries)
    if code.shape!=(n,2) or net.shape!=(n,2) or exit_ix.shape!=(n,2):
        raise ValueError('incompatible teacher arrays')
    next_eligible=np.full((n,2),n,np.int64)
    for option in (0,1):
        success=(code[:,option]==1)&np.isfinite(net[:,option])&(net[:,option]>0)&(exit_ix[:,option]>entries)
        next_eligible[success,option]=np.searchsorted(entries,exit_ix[success,option],side='right')
    count=np.zeros(n+1,np.int32)
    pnl=np.zeros(n+1,np.float64)
    take=np.full(n,-1,np.int8)
    for i in range(n-1,-1,-1):
        best_n=count[i+1];best_p=pnl[i+1];best=-1
        for option in (0,1):
            if next_eligible[i,option]==n and not (code[i,option]==1 and exit_ix[i,option]>entries[i]):continue
            if code[i,option]!=1 or not np.isfinite(net[i,option]) or net[i,option]<=0:continue
            j=next_eligible[i,option]
            v=int(count[j])+1;profit=pnl[j]+float(net[i,option])
            if v>best_n or (v==best_n and profit>best_p+1e-9):
                best_n=v;best_p=profit;best=option
        count[i]=best_n;pnl[i]=best_p;take[i]=best
    rows=[];sides=[];i=0
    while i<n:
        option=int(take[i])
        if option<0:i+=1;continue
        rows.append(i);sides.append(1 if option==0 else -1)
        i=int(next_eligible[i,option])
    sel=np.array(rows,dtype=np.int64);side=np.array(sides,dtype=np.int8)
    if len(sel)>1:
        chosen=(side==-1).astype(np.int64)
        assert np.all(entries[sel[1:]]>exit_ix[sel[:-1],chosen[:-1]])
    assert len(sel)==count[0]
    return sel,side,dict(trades=int(count[0]),sum_net=round(float(pnl[0]),4))


def read_ticks(path):
    df=pd.read_csv(path,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
    t=df.timestamp_ms_utc.to_numpy(dtype=np.int64,copy=True)
    b=df.bid_raw.to_numpy(dtype=np.float64,copy=True)/1000.
    a=df.ask_raw.to_numpy(dtype=np.float64,copy=True)/1000.
    if len(t)==0 or np.any(t[1:]<t[:-1]) or np.any(b>a) or not (np.isfinite(b).all() and np.isfinite(a).all()):
        raise ValueError('unusable raw quote chronology')
    return t,b,a


def digest(path):
    with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def run_month(month,raw_root,output,max_spread=1.50):
    if month not in MONTHS:raise ValueError(month)
    start=time.monotonic();raw=pathlib.Path(raw_root)/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    if not raw.is_file():raise FileNotFoundError(raw)
    out=pathlib.Path(output);out.mkdir(parents=True,exist_ok=True)
    t,b,a=read_ticks(raw)
    ix=candidate_250ms(t,b,a,max_spread=max_spread)
    print(f"H1V2 month={month} raw_ticks={len(t)} candidate_quotes={len(ix)} t={time.monotonic()-start:.1f}s",flush=True)
    code,net,first,first_ms,exit_ix,exit_ms=replay_buy_sell_30s(t,b,a,ix)
    print(f"H1V2 month={month} replay_done t={time.monotonic()-start:.1f}s",flush=True)
    sel,side,oracle=schedule_oracle(ix,code,net,exit_ix)
    print(f"H1V2 month={month} scheduled={oracle['trades']} t={time.monotonic()-start:.1f}s",flush=True)
    which=(side==-1).astype(np.int64)
    mn=math.ceil(.8*SYNTH[month]);received=int(oracle['trades']);good=(code==1).any(axis=1)
    metrics={'model':'H1V2','scientific_status':'OFFLINE_HINDSIGHT_ORACLE_NOT_FORESIGHT',
             'feed':'dukascopy','month':month,'raw_file':str(raw),'raw_sha256':digest(raw),
             'tick_count':int(len(t)),'max_spread':max_spread,'unique_250ms_candidates':int(len(ix)),
             'at_least_one_side_strict_good':int(good.sum()),'at_least_one_side_good_rate':float(good.mean()),
             'both_sides_good':int(((code==1).sum(axis=1)==2).sum()),
             'positive_buy':int((code[:,0]==1).sum()),'positive_sell':int((code[:,1]==1).sum()),
             'oracle_nonoverlapping':oracle,'synth_reference':SYNTH[month],
             'monthly_80pct_floor':mn,'oracle_count_pass_80pct':received>=mn,
             'oracle_count_vs_synth':received/SYNTH[month],
             'selected_first_favorable_ms_p50':float(np.median(first_ms[sel,which])) if len(sel) else None,
             'selected_first_favorable_ms_p90':float(np.percentile(first_ms[sel,which],90)) if len(sel) else None,
             'selected_net_p50':float(np.median(net[sel,which])) if len(sel) else None,
             'fee_per_trade':FEE,'hold_ms':HOLD_MS,
             'scientific_boundary':'future labels used to CHOOSE times and sides; upper bound not learnable policy; 30s exact quote exits; no slippage or live latency; no claim on Coinexx'}
    np.savez(out/f'h1v2_dukascopy_{month}_oracle_labels.npz',t=t[ix],tick_index=ix,
             code=code,net=net,first_event=first,first_event_ms=first_ms,exit_tick_index=exit_ix,
             exit_ms=exit_ms,selected_row=sel,selected_side=side)
    print(f"H1V2 month={month} npz_saved t={time.monotonic()-start:.1f}s",flush=True)
    metrics['teacher_labels_sha256']=digest(out/f'h1v2_dukascopy_{month}_oracle_labels.npz')
    metrics['elapsed_seconds']=round(time.monotonic()-start,2)
    (out/f'h1v2_dukascopy_{month}_receipt.json').write_text(json.dumps(metrics,indent=2))
    return metrics


def main():
    p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=MONTHS)
    p.add_argument('--raw-root',default='/mnt/data');p.add_argument('--output',default='/mnt/data/h1v2/results')
    p.add_argument('--max-spread',type=float,default=1.50)
    opts=p.parse_args();print(json.dumps(run_month(opts.month,opts.raw_root,opts.output,opts.max_spread),indent=2),flush=True)
if __name__=='__main__':main()
