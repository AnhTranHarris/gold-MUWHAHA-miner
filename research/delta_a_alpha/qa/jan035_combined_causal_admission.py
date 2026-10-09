"""Unit035: causal fixed-original-source-candidate-tape sensitivity tests.
NOT original V1 full physically recomputed parent/child genealogy. NO normalized spread.
Source January archival 131E original opportunities and exact Dukascopy tick Bid/Ask.
At WD ticket entry, allow/deny based solely on prior/current quotes and physical funded state.
No forced exits, no lot scaling, no future outcomes in admission. All other layers unchanged.
"""
import numpy as np,pandas as pd,json,sys,time,hashlib,os,datetime
from numba import njit
from pathlib import Path
ROOT=Path('/mnt/data/daa_jan_combined_035'); TAPE='/mnt/data/daa_jan_risk_audit_033/JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz'
RAW='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
@njit(cache=True)
def run(t,a,b,E,X,R,D,S,lag5,lag15,lag60,per_tick,wd_cap,adverse5,adverse15,spreadmax,trend_bias,heat_lim,heat_peroz,retain_tape):
    # Original quote-indexed trade candidates, no recalculation of parent stream.
    n=len(E); ie=np.argsort(E);ix=np.argsort(X); status=np.zeros(n,np.uint8)
    nl=np.zeros(8,np.int64);ns=np.zeros(8,np.int64);el=np.zeros(8,np.int64);es=np.zeros(8,np.int64);bal=np.zeros(8,np.float64)
    outp=np.empty(n,np.float64);outs=np.empty(n,np.int8);outx=np.empty(n,np.int64);oute=np.empty(n,np.int64);nn=0
    k=0;j=0;wdlive=0;rejected=np.zeros(9,np.int64);maxopen=0
    last=-1;onsame=0;peak=100000.;dd=0.;trough_i=0;peak_i=0;wdmax=0
    for i in range(t.size):
        bid=int(b[i]);ask=int(a[i]);mid=(bid+ask)//2
        while k<n and X[ix[k]]==i:
            u=ix[k];k+=1
            if status[u]!=1: continue
            d=int(D[u]);g=int(S[u]);ep=int(R[u]);px=bid if d>0 else ask
            pnl=d*(px-ep)/1000.-.02
            bal[g]+=pnl;outp[nn]=pnl;outs[nn]=g;outx[nn]=i;oute[nn]=int(E[u]);nn+=1
            if d>0:nl[g]-=1;el[g]-=ep
            else:ns[g]-=1;es[g]-=ep
            if g==0:wdlive-=1
        while j<n and E[ie[j]]==i:
            u=ie[j];j+=1;g=int(S[u]);d=int(D[u]);ep=int(R[u]);admit=True
            if g==0:
                if i!=last:onsame=0;last=i
                if wd_cap>0 and wdlive>=wd_cap:rejected[0]+=1;admit=False
                elif per_tick>0 and onsame>=per_tick:rejected[1]+=1;admit=False
                elif spreadmax>0 and ask-bid>spreadmax:rejected[2]+=1;admit=False
                elif adverse5>0 and lag5[u]!=-2147483648 and d*int(lag5[u]) < -adverse5:rejected[3]+=1;admit=False
                elif adverse15>0 and lag15[u]!=-2147483648 and d*int(lag15[u]) < -adverse15:rejected[4]+=1;admit=False
                elif trend_bias>0 and lag5[u]!=-2147483648 and lag15[u]!=-2147483648 and d*int(lag5[u]) < 0 and d*int(lag15[u]) < 0 and (onsame >=trend_bias):rejected[5]+=1;admit=False
                elif heat_lim>0 or heat_peroz>0:
                    unreal=(nl[0]*bid-el[0]+es[0]-ns[0]*ask)/1000.-.02*wdlive
                    if heat_lim>0 and unreal < -heat_lim:rejected[6]+=1;admit=False
                    elif heat_peroz>0 and wdlive * max(1,abs(int(lag15[u])) if lag15[u]!=-2147483648 else 1000)/1000. > heat_peroz:rejected[7]+=1;admit=False
                if admit:wdlive+=1;onsame+=1
            if admit:
                status[u]=1
                if d>0:nl[g]+=1;el[g]+=ep
                else:ns[g]+=1;es[g]+=ep
        eq=100000.;op=0
        for g in range(8):
            eq+=bal[g]+(nl[g]*bid-el[g]+es[g]-ns[g]*ask)/1000.-.02*(nl[g]+ns[g]);op+=nl[g]+ns[g]
        if eq>peak:peak=eq;peak_i=i
        if peak-eq>dd:dd=peak-eq;trough_i=i
        if op>maxopen:maxopen=op
        if wdlive>wdmax:wdmax=wdlive
    if retain_tape:
        return outp[:nn],outs[:nn],outx[:nn],oute[:nn],dd,maxopen,wdmax,rejected,peak_i,trough_i
    return outp[:nn],outs[:nn],outx[:nn],oute[:nn],dd,maxopen,wdmax,rejected,peak_i,trough_i

def load():
    a=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    z=np.load(TAPE); E=z['entry_index'];X=z['exit_index'];R=z['entry_price_raw'];D=z['direction'];S=z['source_id']
    t=a.timestamp_ms_utc.to_numpy();aa=a.ask_raw.to_numpy();bb=a.bid_raw.to_numpy()
    return t,aa,bb,E,X,R,D,S

def lagged(t,a,b,E,lag):
    mid=(a.astype(np.int64)+b.astype(np.int64))//2
    j=np.searchsorted(t,t[E]-lag,side='right')-1
    good=(j>=0)&(t[E]-t[np.maximum(j,0)]<=max(120000,lag*3))
    d=np.full(E.size,-2147483648,np.int32);d[good]=(mid[E[good]]-mid[j[good]]).astype(np.int32)
    return d

def main():
    t,a,b,E,X,R,D,S=load()
    print('loaded',len(t),len(E),flush=True)
    l5=lagged(t,a,b,E,5000);l15=lagged(t,a,b,E,15000);l60=lagged(t,a,b,E,60000)
    opts=[]
    # (name,same-tick,WD max, adverse5,adverse15,spreadmax,trendbias,heat_lim,heat_peroz)
    opts += [('base',9999,640,0,0,0,0,0,0)]
    for cap in [64,96,128,192,256,384,512]:opts.append((f'cap{cap}',cap,640,0,0,0,0,0,0))
    for cap in [128,192,256,384,512]:
        for h5 in [1000,3000,6000,12000]:opts.append((f'cap{cap}_adv5_{h5}',cap,640,h5,0,0,0,0,0))
        for h15 in [1500,4000,8000]:opts.append((f'cap{cap}_adv15_{h15}',cap,640,0,h15,0,0,0,0))
        for tb in [8,32,96]:opts.append((f'cap{cap}_tb{tb}',cap,640,0,0,0,tb,0,0))
        for spread in [1250,2000,3000]:opts.append((f'cap{cap}_spr{spread}',cap,640,0,0,spread,0,0,0))
        for heat in [500,2000,5000]:opts.append((f'cap{cap}_heat{heat}',cap,640,0,0,0,0,heat,0))
        for stress in [2000,5000,10000]:opts.append((f'cap{cap}_stress{stress}',cap,640,0,0,0,0,0,stress))
    # Novel combinations: entry-known adverse impulse + spread + floating heat (no liquidation)
    for cap in [128,192,256,384,512]:
        for adv in [1500,4000,8000]:
            for spr in [1500,2500,4000]:opts.append((f'combo_cap{cap}_adv{adv}_sp{spr}',cap,640,adv,0,spr,0,0,0))
            for h in [500,2500]:opts.append((f'combo_cap{cap}_adv{adv}_heat{h}',cap,640,adv,0,0,0,h,0))
        for hs in [2000,5000]:
            for spr in [2000,4000]:opts.append((f'combo_cap{cap}_heat{hs}_sp{spr}',cap,640,0,0,spr,0,hs,0))
    summary=[]
    for ix,opt in enumerate(opts):
        name,cap,mx,v5,v15,sp,tb,heat,stress=opt
        st=time.monotonic()
        p,s,x,e,dd,mo,wdm,rej,pk,tr=run(t,a,b,E,X,R,D,S,l5,l15,l60,cap,mx,v5,v15,sp,tb,heat,stress,True)
        gp=float(p[p>0].sum());gl=float(p[p<0].sum()); net=float(p.sum())
        result={'scenario':name,'same_tick_cap':cap,'wd_position_cap':mx,'adverse_5s_raw':v5,'adverse_15s_raw':v15,'spread_ceiling_raw':sp,'opposite_microtrend_max_same_tick':tb,'wd_floating_loss_admission_limit_usd':heat,'wd_lag15_stress_budget_usd':stress,'net':round(net,3),'trades':len(p),'gp':round(gp,3),'gross_loss':round(gl,3),'pf':round(gp/-gl if gl<0 else 999.,4),'wins':int((p>0).sum()),'dd':round(float(dd),2),'max_open':int(mo),'max_wd_open':int(wdm),'wd_net':round(float(p[s==0].sum()),3),'hourly_net':round(float(p[s==1].sum()),3),'rejected':rej.tolist(),'run_s':round(time.monotonic()-st,2)}
        (ROOT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        summary.append(result)
        if name=='base': assert abs(net-93425.311)<.02 and abs(dd-56921.6)<.11,(net,dd)
        if ix%20==0:print('CHECKPOINT',ix+1,'/',len(opts),name,result['net'],result['trades'],result['gross_loss'],result['pf'],result['dd'],flush=True)
    (ROOT/'SCREEN_ALL.json').write_text(json.dumps(summary,indent=2)+'\n')
    pd.DataFrame(summary).to_csv(ROOT/'SCREEN_ALL.csv',index=False)
    good=sorted(summary,key=lambda z:(z['net']>60000 and z['trades']>=20000 and z['gross_loss']>-15000,z['net']/max(1,z['dd']),z['net']),reverse=True)
    print('TOP15',json.dumps([{k:o[k] for k in ('scenario','net','trades','gross_loss','pf','dd')} for o in good[:15]]),flush=True)
if __name__=='__main__':main()