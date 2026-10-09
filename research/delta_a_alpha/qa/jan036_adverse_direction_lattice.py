"""Jan036: exploratory original-candidate tape + genuinely NEW, bounded, first-touch inverse microgrid.
Original L3 hourly source and original WD source admissions preserved except labeled throttle/lock.
NOT source-exact full L0–L7 funded-parent genealogy; excludes broker rejection/slippage/margin.
No date used as an execution feature; ALL exits and recovery entry observed tick only.
"""
from pathlib import Path
import json,time,sys
import numpy as np,pandas as pd
from numba import njit
RAW='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
NPZ='/mnt/data/daa_jan_risk_audit_033/JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz'
OUT=Path('/mnt/data/daa_jan_lattice_036')
@njit(cache=True)
def engine(t,a,b,E,X,R,D,S,per_quote,lock_impulse,lock_hold_ms,lock_min_open,lock_loss,rec_budget,rec_impulse,rec_lag5,rec_step,rec_tp,rec_sl,rec_hold,rec_spread,rec_trail):
    n=len(E);ie=np.argsort(E);ix=np.argsort(X);status=np.zeros(n,np.uint8)
    nl=np.zeros(8,np.int64);ns=np.zeros(8,np.int64);el=np.zeros(8,np.int64);es=np.zeros(8,np.int64);bal=np.zeros(8,np.float64)
    p=np.empty(n+40000,np.float64);s=np.empty(n+40000,np.int8);x=np.empty(n+40000,np.int64);ent=np.empty(n+40000,np.int64);z=0
    # new independently funded recovery positions: 0.01 lots EACH, bounded aggregate volume
    live=np.zeros(128,np.uint8);rd=np.zeros(128,np.int8);rp=np.zeros(128,np.int32);rt=np.zeros(128,np.int64);rmax=np.zeros(128,np.int32);rent=np.zeros(128,np.int64)
    wd=0;lasttick=-1;onsame=0;j=0;k=0;quote5=0;quote20=0;lockend=0
    lastentry=-1;lastgrid=-2147483648;lastgrid_direction=0;activeR=0;recwins=0;reclosses=0;recloss=0.;recgp=0.;cntlocks=0;denied=0
    peak=100000.;dd=0.;pk=0;tr=0;maxopen=0;maxwd=0;minfree=1e50
    for i in range(len(t)):
        ti=t[i];ask=int(a[i]);bid=int(b[i]);mid=(ask+bid)//2
        # monotonic event clock. Only last observed 5s/20s quotes, not future bars.
        while quote5+1<i and t[quote5+1]<=ti-5000:quote5+=1
        while quote20+1<i and t[quote20+1]<=ti-20000:quote20+=1
        age5=ti-t[quote5];age20=ti-t[quote20]
        diff5=mid-(int(a[quote5])+int(b[quote5]))//2 if age5>=3000 and age5<=15000 else 0
        diff20=mid-(int(a[quote20])+int(b[quote20]))//2 if age20>=15000 and age20<=45000 else 0
        # first-touch exact original exit (time ordering: close before new entries)
        while k<n and X[ix[k]]==i:
            u=ix[k];k+=1
            if status[u]!=1:continue
            g=int(S[u]);d=int(D[u]);ep=int(R[u]);px=bid if d>0 else ask
            pp=d*(px-ep)/1000.-.02
            p[z]=pp;s[z]=g;x[z]=i;ent[z]=int(E[u]);z+=1;bal[g]+=pp
            if d>0:nl[g]-=1;el[g]-=ep
            else:ns[g]-=1;es[g]-=ep
            if g==0:wd-=1
        # opposite-direction specialist precise quote-side exits (no stop-at-threshold fantasy)
        for r in range(rec_budget):
            if live[r]==0:continue
            direction=int(rd[r]);close=bid if direction>0 else ask
            raw=direction*(close-int(rp[r]))
            if raw>rmax[r]:rmax[r]=raw
            reversed_recently=(direction*diff5<=-rec_lag5 if rec_lag5>0 else False)
            trailing=(rec_trail>0 and rmax[r]>=rec_tp//2 and rmax[r]-raw>=rec_trail)
            if raw>=rec_tp or raw<=-rec_sl or ti>=rt[r]+rec_hold or trailing or reversed_recently:
                pp=raw/1000.-.02;p[z]=pp;s[z]=7;x[z]=i;ent[z]=rent[r];z+=1;bal[7]+=pp
                if pp>=0:recgp+=pp;recwins+=1
                else:recloss+=pp;reclosses+=1
                live[r]=0;activeR-=1
        # new lock from *observed* adverse change against held same-direction WD inventory
        dominance=(1 if nl[0]>=lock_min_open and nl[0]>=4*ns[0] else -1 if ns[0]>=lock_min_open and ns[0]>=4*nl[0] else 0)
        unreal=(nl[0]*bid-el[0]+es[0]-ns[0]*ask)/1000.-.02*wd
        if lock_impulse>0 and dominance and (diff20*dominance <= -lock_impulse) and unreal<=-lock_loss:
            if ti>=lockend:cntlocks+=1
            if lockend<ti+lock_hold_ms:lockend=ti+lock_hold_ms
        # Original source candidate entries, except per-quote cap & event-based lock
        while j<n and E[ie[j]]==i:
            u=ie[j];j+=1;g=int(S[u]);d=int(D[u]);ep=int(R[u]);admit=True
            if g==0:
                if lasttick!=i:onsame=0;lasttick=i
                if wd>=640 or onsame>=per_quote or ti<lockend:admit=False;denied+=1
                if admit:onsame+=1;wd+=1
            if admit:
                status[u]=1
                if d>0:nl[g]+=1;el[g]+=ep
                else:ns[g]+=1;es[g]+=ep
        # L6 independent inverse microgrid, requires genuine WD ownership & structural failure
        if rec_budget>0 and dominance and activeR<rec_budget and rec_step>0 and ask-bid<=rec_spread:
            direction=-dominance  # economic opposite to WD direction, not lot-scaling rescue
            if direction*diff20>=rec_impulse and direction*diff5>=rec_lag5 and i!=lastentry:
                # fresh adverse displacement rung; one per price level, never DCA
                cell=(mid//rec_step if direction>0 else (-mid)//rec_step)
                if direction!=lastgrid_direction:lastgrid=-2147483648;lastgrid_direction=direction
                if cell>lastgrid:
                    if lastgrid==-2147483648 or cell-lastgrid>=1:
                        for r in range(rec_budget):
                            if live[r]==0:
                                live[r]=1;rd[r]=direction;rp[r]=ask if direction>0 else bid;rent[r]=i
                                rt[r]=ti;rmax[r]=0;activeR+=1;lastentry=i;lastgrid=cell;break
            if activeR==0 and direction*diff20<rec_impulse//2:lastgrid=-2147483648
        elif activeR==0:lastgrid=-2147483648
        eq=100000.;opens=activeR
        for g in range(8):
            eq+=bal[g]+(nl[g]*bid-el[g]+es[g]-ns[g]*ask)/1000.-.02*(nl[g]+ns[g]);opens+=nl[g]+ns[g]
        for r in range(rec_budget):
            if live[r]:eq+=int(rd[r])*((bid if rd[r]>0 else ask)-int(rp[r]))/1000.-.02
        if eq>peak:peak=eq;pk=i
        if peak-eq>dd:dd=peak-eq;tr=i
        if opens>maxopen:maxopen=opens
        if wd>maxwd:maxwd=wd
    # Terminal flush recovery trades only: genuine executable last quote
    i=len(t)-1
    for r in range(rec_budget):
        if live[r]:
            close=int(b[i] if rd[r]>0 else a[i]);pp=int(rd[r])*(close-int(rp[r]))/1000.-.02
            p[z]=pp;s[z]=7;x[z]=i;ent[z]=rent[r];z+=1;bal[7]+=pp
    return p[:z],s[:z],x[:z],ent[:z],dd,maxopen,maxwd,cntlocks,denied,recwins,reclosses,pk,tr

def load():
    df=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    with np.load(NPZ) as z: E,X,R,D,S=[z[k].copy() for k in ('entry_index','exit_index','entry_price_raw','direction','source_id')]
    return df.timestamp_ms_utc.to_numpy(),df.ask_raw.to_numpy(),df.bid_raw.to_numpy(),E,X,R,D,S

def summarize(name,args,t,result):
    p,s,x,e,dd,mo,mw,locks,denied,rw,rl,pk,tr=result
    gp=float(p[p>0].sum());gl=float(p[p<0].sum())
    out={'name':name,'params':args,'net':round(float(p.sum()),3),'trades':len(p),'gross_loss':round(gl,3),'gross_profit':round(gp,3),'PF':round(gp/-gl,4) if gl<0 else None,'win_pct':round(100*np.mean(p>0),2),'equity_dd':round(dd,2),'maxopen':int(mo),'wd_max':int(mw),'lock_events':int(locks),'wd_rejected':int(denied),'recovery_trades':int((s==7).sum()),'recovery_net':round(float(p[s==7].sum()),3),'hourly_net':round(float(p[s==1].sum()),3),'risk_peak_tick':int(pk),'risk_trough_tick':int(tr)}
    from datetime import datetime,timezone
    times=pd.to_datetime(t[x],unit='ms',utc=True)
    ds=times.strftime('%Y-%m-%d');week=times.strftime('%G-W%V')
    out['daily']={str(d):{'net':round(float(p[ds==d].sum()),3),'trades':int((ds==d).sum())} for d in np.unique(ds)}
    out['weekly']={str(w):{'net':round(float(p[week==w].sum()),3),'trades':int((week==w).sum())} for w in np.unique(week)}
    return out

def main():
    t,a,b,E,X,R,D,S=load();print('LOADED',len(t),len(E),flush=True)
    # per_quote,lock_impulse,lock_hold_ms,lock_min_open,lock_loss,rec_budget,rec_impulse,rec_lag5,rec_step,rec_tp,rec_sl,rec_hold,rec_spread,rec_trail
    base=(384,0,0,128,1000,0,0,0,0,0,0,0,0,0)
    configs=[('lattice_base384',base),
    ('lock_4_30s', (384,4000,30000,128,1000,0,0,0,0,0,0,0,0,0)),
    ('lock_8_60s',(384,8000,60000,128,1000,0,0,0,0,0,0,0,0,0)),
    ('lock_12_90s',(384,12000,90000,128,1000,0,0,0,0,0,0,0,0,0)),
    ('lock_5_120s',(384,5000,120000,128,500,0,0,0,0,0,0,0,0,0)),
    ('inverse_8_fast',(384,0,0,128,1000,8,5000,1000,2000,6000,3000,60000,2400,0)),
    ('inverse_24_fast',(384,0,0,128,1000,24,5000,1000,2000,6000,3000,60000,2400,0)),
    ('inverse_24_trail',(384,0,0,128,1000,24,5000,1000,2000,9000,4000,120000,2400,2000)),
    ('inverse_48_trail',(384,0,0,128,1000,48,4000,1000,1500,8000,4000,120000,3000,2000)),
    ('lock8_inverse24',(384,8000,60000,128,1000,24,5000,1000,2000,6000,3000,60000,2400,0)),
    ('lock5_inverse48',(384,5000,120000,128,500,48,4000,1000,1500,8000,4000,120000,3000,2000)),
    ('lock12_inverse24',(384,12000,90000,128,1000,24,5000,1000,2000,9000,4000,120000,2400,2000))]
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--end',type=int,default=len(configs));cli=ap.parse_args()
    for name,arg in configs[cli.start:cli.end]:
        path=OUT/(name+'.json')
        if path.exists():print('SKIP',name,flush=True);continue
        start=time.monotonic();rs=engine(t,a,b,E,X,R,D,S,*arg)
        obj=summarize(name,arg,t,rs)
        if name=='lattice_base384':
            assert abs(obj['net']-93656.482)<.02,(name,obj['net'])
            assert abs(obj['equity_dd']-43224.84)<.08,(name,obj['equity_dd'])
        path.write_text(json.dumps(obj,indent=2)+'\n')
        print('CHECKPOINT',name,'net',obj['net'],'PF',obj['PF'],'trades',obj['trades'],'gross_loss',obj['gross_loss'],'DD',obj['equity_dd'],'rec',obj['recovery_trades'],obj['recovery_net'],'s',round(time.monotonic()-start,2),flush=True)
if __name__=='__main__':main()