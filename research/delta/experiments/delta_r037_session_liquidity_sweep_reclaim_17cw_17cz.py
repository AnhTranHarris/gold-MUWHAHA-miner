"""R037 17CW-17CZ: XAUUSD session-liquidity sweep/reclaim Stage-A harvest.

Preregistered lanes only:
- strict London sweep of locked Asia range, M5/M15;
- XAU Gold sweep depth >=5% of Asia range, M5/M15.

Closed-bar causal signals. No retuning, rescue, August, or MQL5.
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
PREREG="11805b3273a3ddc336114ee271aed15ac018bd07"
MAX_SPREAD=250; STOP=300; TRAIL_ACT=100; TRAIL_DIST=30; MAX_HOLD=30
ASIA_START=0; ASIA_END=6*H; LDN_START=7*H; LDN_END=10*H

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

def sweep_signals(t,ask,bid,z,min_frac):
    e,h,l,c=z['e'],z['h'],z['l'],z['c']
    ix=[]; sd=[]
    diag={'days_seen':0,'days_with_asia_range':0,'asia_ranges_zero':0,'high_sweep_reclaims':0,'low_sweep_reclaims':0,'spread_rejects':0,'duplicate_side_suppressed':0}
    day_values=np.unique(e//D)
    for day in day_values:
        day0=int(day*D)
        if day0+D<=START or day0>=END: continue
        diag['days_seen']+=1
        asia=(e>day0+ASIA_START)&(e<=day0+ASIA_END)
        if not np.any(asia): continue
        ah=int(np.max(h[asia])); al=int(np.min(l[asia])); rng=ah-al
        if rng<=0:
            diag['asia_ranges_zero']+=1; continue
        diag['days_with_asia_range']+=1
        depth=float(min_frac)*rng
        used_hi=False; used_lo=False
        ks=np.flatnonzero((e>day0+LDN_START)&(e<=day0+LDN_END)&(e>=START)&(e<=END))
        for k in ks:
            short_evt=(h[k]>ah+depth) and (c[k]<ah)
            long_evt=(l[k]<al-depth) and (c[k]>al)
            if short_evt and long_evt:
                continue
            if short_evt:
                if used_hi:
                    diag['duplicate_side_suppressed']+=1; continue
                j=int(np.searchsorted(t,int(e[k]),side='left'))
                if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
                    ix.append(j); sd.append(-1); diag['high_sweep_reclaims']+=1; used_hi=True
                elif j<len(t): diag['spread_rejects']+=1; used_hi=True
            elif long_evt:
                if used_lo:
                    diag['duplicate_side_suppressed']+=1; continue
                j=int(np.searchsorted(t,int(e[k]),side='left'))
                if j<len(t) and t[j]<END and ask[j]-bid[j]<=MAX_SPREAD:
                    ix.append(j); sd.append(1); diag['low_sweep_reclaims']+=1; used_lo=True
                elif j<len(t): diag['spread_rejects']+=1; used_lo=True
    order=np.argsort(np.asarray(ix,np.int64),kind='stable') if ix else np.array([],np.int64)
    return np.asarray(ix,np.int64)[order],np.asarray(sd,np.int8)[order],diag

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
    g={'minimum_trades_10':m['trades']>=10,'minimum_distinct_days_5':m['distinct_days']>=5,'direct_net_nonnegative':m['direct_net_usd']>=0}
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
    for name,tf,frac,fam in (
        ('17CW_ASIA_LONDON_SWEEP_M5',300_000,0.0,'R037-ASIA-LONDON-SWEEP-v1'),
        ('17CX_ASIA_LONDON_SWEEP_M15',900_000,0.0,'R037-ASIA-LONDON-SWEEP-v1'),
        ('17CY_XAUGOLD_SWEEP5_M5',300_000,0.05,'R037-XAUGOLD-SWEEP5-v1'),
        ('17CZ_XAUGOLD_SWEEP5_M15',900_000,0.05,'R037-XAUGOLD-SWEEP5-v1')):
        z=bars(t,bid,tf); ix,sd,diag=sweep_signals(t,ask,bid,z,frac); m,g=pack(ix,sd,t,ask,bid)
        configs[name]={'family':fam,'bar_ms':tf,'minimum_sweep_fraction':frac,'metrics':m,'gate':g,'diagnostics':diag}
    surv=[n for n,v in configs.items() if v['gate']['screen_pass']]
    surv.sort(key=lambda n:(configs[n]['metrics']['direct_net_usd'],configs[n]['metrics']['official_wins'],configs[n]['metrics']['trades']),reverse=True)
    out={'schema':'delta-r037-session-liquidity-sweep-reclaim-17cw-17cz-v1','status':'COMPLETE_FAST_CAUSAL_STAGE_A_SCREEN','unit':'R037_XAUUSD_SESSION_LIQUIDITY_SWEEP_RECLAIM_HARVEST_CHECKPOINT_17CW_17CZ','parent_checkpoint':'R037_HIGH_VALUE_STRUCTURAL_STATE_MACHINE_HARVEST_CHECKPOINT_17CS_17CV','prereg_commit':PREREG,'source_sha256':hs,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75','configs':configs,'finding':{'survivors':surv,'leader':surv[0] if surv else None,'decision':'ADVANCE_LEADER_TO_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'RETIRE_SESSION_SWEEP_FAMILIES_NO_STAGE_A_SURVIVOR','next':'R037_SESSION_SWEEP_LEADER_INDEPENDENT_LATER_JAN_VALIDATION' if surv else 'R037_NEXT_HIGH_VALUE_ENTRY_SOURCE_HARVEST'},'numeric_retuning':False,'post_result_rescue':False,'august_accessed':False,'mql5_authorized':False,'runtime_seconds':round(time.monotonic()-st,3)}
    atomic_json(x.output,out)
    print(json.dumps({'configs':{n:{'trades':v['metrics']['trades'],'days':v['metrics']['distinct_days'],'wins':v['metrics']['official_wins'],'net':v['metrics']['direct_net_usd'],'pass':v['gate']['screen_pass'],'diag':v['diagnostics']} for n,v in configs.items()},'finding':out['finding'],'runtime_seconds':out['runtime_seconds']},separators=(',',':')))

if __name__=='__main__': main()
