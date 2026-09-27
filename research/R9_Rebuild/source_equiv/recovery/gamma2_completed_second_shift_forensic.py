exec(open('/mnt/data/gamma2_recovery_jan_variants.py').read().split('def main():')[0])


def metric(v):
    v=np.asarray(v,float); gp=float(v[v>0].sum()); gl=float(v[v<0].sum())
    return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gp':gp,'gl':gl,'pf':gp/-gl if gl<0 else 999.}

@njit
def gen_shifted(sec, first_t, hb, lb, cb, m5, al, ash, cont_mode, liq_shift, feature_lead, timestamp_lag):
    # Forensic only: positive feature_lead exposes a later completed bar;
    # positive timestamp_lag backdates the executable event timestamp.
    cap=180000; X=np.empty((cap,5),np.float64); n=0
    state=0; level=0.; started=0; minute=-1; trades=0; cool=-1
    N=len(sec)
    for k in range(21,N):
        fk=k+feature_lead
        if fk>=N: break
        s=sec[k]; mn=s//60
        if mn!=minute:
            minute=mn; trades=0; state=0; level=0.; started=0
        if s<cool or trades>=5: continue
        if not np.isfinite(m5[k]) or m5[k]+1e-12<floor_session(s): continue
        newest=k-1+liq_shift; oldest=newest-19
        if oldest<0 or newest>=k: continue
        upper=-1e18; lower=1e18
        for q in range(oldest,newest+1):
            if hb[q]>upper: upper=hb[q]
            if lb[q]<lower: lower=lb[q]
        bid_hi=hb[fk]; bid_lo=lb[fk]; bid_cl=cb[fk]
        ask_hi=bid_hi+.20; ask_cl=bid_cl+.20
        if fk<4: continue
        start=cb[fk-4]; prev=start; travel=0.
        for q in range(fk-3,fk+1):
            v=cb[q]; travel+=abs(v-prev); prev=v
        disp=bid_cl-start; eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ask_hi>=upper+.10: state=1; level=upper; started=s
            elif bid_lo<=lower-.10: state=-1; level=lower; started=s
        if state==1:
            if ask_cl<=level-.15: state=2; started=s
            elif s-started>=2 and ask_cl>=level+.08 and disp>=.15 and eff>=.30:
                if cont_mode==1: state=0; level=0.; started=0
                elif cont_mode==2: state=0; level=0.; started=0; trades+=1; cool=s+1
                elif cont_mode==3: state=0; level=0.; started=0; trades+=1
                elif cont_mode==4: state=0; level=0.; started=0; cool=s+1
        elif state==-1:
            if bid_cl>=level+.15: state=-2; started=s
            elif s-started>=2 and bid_cl<=level-.08 and disp<=-.15 and eff>=.30:
                if cont_mode==1: state=0; level=0.; started=0
                elif cont_mode==2: state=0; level=0.; started=0; trades+=1; cool=s+1
                elif cont_mode==3: state=0; level=0.; started=0; trades+=1
                elif cont_mode==4: state=0; level=0.; started=0; cool=s+1
        elif state==2:
            if disp<=-.15 and eff>=.30:
                ti=max(0,k-timestamp_lag)
                X[n,0]=first_t[ti]; X[n,1]=-1; X[n,2]=level; X[n,3]=ash[k]; X[n,4]=first_t[fk]; n+=1
                trades+=1; cool=s+1; state=0; level=0.; started=0
        elif state==-2:
            if disp>=.15 and eff>=.30:
                ti=max(0,k-timestamp_lag)
                X[n,0]=first_t[ti]; X[n,1]=1; X[n,2]=level; X[n,3]=al[k]; X[n,4]=first_t[fk]; n+=1
                trades+=1; cool=s+1; state=0; level=0.; started=0
        if state!=0 and started>0 and s-started>20:
            state=0; level=0.; started=0
    return X[:n]
