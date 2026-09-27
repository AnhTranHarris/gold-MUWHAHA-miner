exec(open('/mnt/data/gamma2_recovery_jan_variants.py').read().split('def main():')[0])

def met2(v):
    v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum())
    return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gp':gp,'gl':gl,'pf':gp/-gl if gl<0 else 999.}

@njit
def gen_bar_leak(sec,first_t,hb,lb,cb,m5,al,ash,cont_mode,allow_samebar_chain,signal_mode,liq_shift):
    # Deliberately forensic: full OHLC of bar j can drive state while signal timestamp can be first tick of same bar.
    cap=180000;X=np.empty((cap,4),np.float64);n=0
    state=0;level=0.;started=0;minute=-1;trades=0;cool=-1
    for j in range(21,len(sec)):
        s=sec[j];mn=s//60
        if mn!=minute:
            minute=mn;trades=0;state=0;level=0.;started=0
        if s<cool or trades>=5: continue
        if not np.isfinite(m5[j]) or m5[j]+1e-12<floor_session(s): continue
        newest=j-1+liq_shift; oldest=newest-19
        if oldest<0 or newest>=j: continue
        upper=-1e18;lower=1e18
        for q in range(oldest,newest+1):
            if hb[q]>upper: upper=hb[q]
            if lb[q]<lower: lower=lb[q]
        # full current bar is now (improperly) visible
        ask_hi=hb[j]+.20; ask_lo=lb[j]+.20; ask_cl=cb[j]+.20
        bid_hi=hb[j]; bid_lo=lb[j]; bid_cl=cb[j]
        # 5s velocity ending current full bar
        if j<4: continue
        start=cb[j-4]; prev=start; travel=0.
        for q in range(j-3,j+1):
            v=cb[q];travel+=abs(v-prev);prev=v
        disp=bid_cl-start;eff=abs(disp)/(travel+1e-9)
        oldstate=state
        if state==0:
            if ask_hi>=upper+.10: state=1;level=upper;started=s
            elif bid_lo<=lower-.10: state=-1;level=lower;started=s
            if not allow_samebar_chain and state!=0: continue
        if state==1:
            # R8 compares current Ask tick, but bar helper might have used close/min/max; test close and low via signal_mode flags later not here
            if ask_cl<=level-.15:
                state=2;started=s
                if not allow_samebar_chain: continue
            elif s-started>=2 and ask_cl>=level+.08 and disp>=.15 and eff>=.30:
                if cont_mode==1: state=0;level=0.;started=0
                elif cont_mode==2: state=0;level=0.;started=0;trades+=1;cool=s+1
                elif cont_mode==3: state=0;level=0.;started=0;trades+=1
                elif cont_mode==4: state=0;level=0.;started=0;cool=s+1
        elif state==-1:
            if bid_cl>=level+.15:
                state=-2;started=s
                if not allow_samebar_chain: continue
            elif s-started>=2 and bid_cl<=level-.08 and disp<=-.15 and eff>=.30:
                if cont_mode==1: state=0;level=0.;started=0
                elif cont_mode==2: state=0;level=0.;started=0;trades+=1;cool=s+1
                elif cont_mode==3: state=0;level=0.;started=0;trades+=1
                elif cont_mode==4: state=0;level=0.;started=0;cool=s+1
        if state==2 and oldstate==2:
            if disp<=-.15 and eff>=.30:
                sig=first_t[j] if signal_mode==0 else (sec[j]*1000 if signal_mode==1 else (first_t[j+1] if j+1<len(first_t) else first_t[j]))
                X[n,0]=sig;X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
        elif state==-2 and oldstate==-2:
            if disp>=.15 and eff>=.30:
                sig=first_t[j] if signal_mode==0 else (sec[j]*1000 if signal_mode==1 else (first_t[j+1] if j+1<len(first_t) else first_t[j]))
                X[n,0]=sig;X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
        if state!=0 and started>0 and s-started>20: state=0;level=0.;started=0
    return X[:n]

# Alternative: use full bar low/high for reclaim, not close, then close displacement for confirm.
@njit
def gen_bar_leak_extreme_reclaim(sec,first_t,hb,lb,cb,m5,al,ash,cont_mode,signal_mode,liq_shift):
    cap=180000;X=np.empty((cap,4),np.float64);n=0
    state=0;level=0.;started=0;minute=-1;trades=0;cool=-1
    for j in range(21,len(sec)):
        s=sec[j];mn=s//60
        if mn!=minute: minute=mn;trades=0;state=0;level=0.;started=0
        if s<cool or trades>=5:continue
        if not np.isfinite(m5[j]) or m5[j]+1e-12<floor_session(s):continue
        newest=j-1+liq_shift;oldest=newest-19
        if oldest<0 or newest>=j:continue
        upper=-1e18;lower=1e18
        for q in range(oldest,newest+1):
            if hb[q]>upper:upper=hb[q]
            if lb[q]<lower:lower=lb[q]
        ask_hi=hb[j]+.20; ask_lo=lb[j]+.20; ask_cl=cb[j]+.20
        bid_hi=hb[j]; bid_lo=lb[j]; bid_cl=cb[j]
        start=cb[j-4];prev=start;travel=0.
        for q in range(j-3,j+1):v=cb[q];travel+=abs(v-prev);prev=v
        disp=bid_cl-start;eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ask_hi>=upper+.10:state=1;level=upper;started=s
            elif bid_lo<=lower-.10:state=-1;level=lower;started=s
        if state==1:
            if ask_lo<=level-.15:state=2;started=s
            elif s-started>=2 and ask_hi>=level+.08 and disp>=.15 and eff>=.30:
                if cont_mode==1:state=0;level=0.;started=0
                elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
                elif cont_mode==3:state=0;level=0.;started=0;trades+=1
                elif cont_mode==4:state=0;level=0.;started=0;cool=s+1
        elif state==-1:
            if bid_hi>=level+.15:state=-2;started=s
            elif s-started>=2 and bid_lo<=level-.08 and disp<=-.15 and eff>=.30:
                if cont_mode==1:state=0;level=0.;started=0
                elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
                elif cont_mode==3:state=0;level=0.;started=0;trades+=1
                elif cont_mode==4:state=0;level=0.;started=0;cool=s+1
        elif state==2:
            if disp<=-.15 and eff>=.30:
                sig=first_t[j] if signal_mode==0 else (sec[j]*1000 if signal_mode==1 else (first_t[j+1] if j+1<len(first_t) else first_t[j]))
                X[n,0]=sig;X[n,1]=-1;X[n,2]=level;X[n,3]=ash[j];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
        elif state==-2:
            if disp>=.15 and eff>=.30:
                sig=first_t[j] if signal_mode==0 else (sec[j]*1000 if signal_mode==1 else (first_t[j+1] if j+1<len(first_t) else first_t[j]))
                X[n,0]=sig;X[n,1]=1;X[n,2]=level;X[n,3]=al[j];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
        if state!=0 and started>0 and s-started>20:state=0;level=0.;started=0
    return X[:n]

def main3():
 d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);a=d.ask_raw.to_numpy(np.float64)/1000.;b=d.bid_raw.to_numpy(np.float64)/1000.;mid=(a+b)*.5;mb=mid-H
 sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb);e5,r5,a5=aggregate(sec,h,l,c,300);m5=map_completed(sec,e5,a5);al=np.zeros(len(sec),np.int8);ash=np.zeros(len(sec),np.int8)
 for tf in (60,180,300,600,1200):
  e,r,a2=aggregate(sec,h,l,c,tf);rr=map_completed(sec,e,r);aa=map_completed(sec,e,a2);ok=np.isfinite(aa);al+=((rr>0)&ok).astype(np.int8);ash+=((rr<0)&ok).astype(np.int8)
 rows=[]
 for lv in (0,-1):
  for cm in (0,1,2,3,4):
   for chain in (0,1):
    for sm in (0,1,2):
     X=gen_bar_leak(sec,first_t,h,l,c,m5,al,ash,cm,chain,sm,lv);O=replay(t,mid,X);ix=nonoverlap(X,O);q=O[ix];m=met2(q[:,0]);m.update(label=f'close_lv{lv}_cont{cm}_chain{chain}_sig{sm}',raw=len(X),trade_delta=m['trades']-TARGET[0],winner_delta=m['winners']-TARGET[1],net_delta=m['net']-TARGET[3],gl_delta=m['gl']-TARGET[4]);rows.append(m)
   for sm in (0,1,2):
    X=gen_bar_leak_extreme_reclaim(sec,first_t,h,l,c,m5,al,ash,cm,sm,lv);O=replay(t,mid,X);ix=nonoverlap(X,O);q=O[ix];m=met2(q[:,0]);m.update(label=f'extreme_lv{lv}_cont{cm}_sig{sm}',raw=len(X),trade_delta=m['trades']-TARGET[0],winner_delta=m['winners']-TARGET[1],net_delta=m['net']-TARGET[3],gl_delta=m['gl']-TARGET[4]);rows.append(m)
 def dist(r):return abs(r['trades']-TARGET[0])/TARGET[0]+abs(r['winners']-TARGET[1])/TARGET[1]+abs(r['net']-TARGET[3])/10000+abs(r['gl']-TARGET[4])/10000
 out={'target':TARGET,'best':sorted(rows,key=dist)[:30],'rows':rows}
 Path('/mnt/data/GAMMA2_SAME_SECOND_OHLC_FORENSIC.json').write_text(json.dumps(out,indent=2))
 for r in out['best'][:25]: print(json.dumps(r))
if __name__=='__main__':main3()
