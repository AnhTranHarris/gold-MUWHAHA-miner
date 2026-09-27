exec(open('/mnt/data/gamma2_recovery_jan_variants.py').read().split('def main():')[0])

@njit
def gen_events(t,mid,sec_ids,hb,lb,cb,m5,al,ash,cont_mode,liq_shift):
    # columns: confirm_t, side, level, break_t, reclaim_t, break_j, reclaim_j, confirm_j
    cap=180000; E=np.empty((cap,8),np.float64); n=0
    state=0; level=0.; started=0; break_t=0; reclaim_t=0; break_j=-1; reclaim_j=-1
    minute=-1; trades=0; cool_until=-1; j=0
    for i in range(len(t)):
        s=t[i]//1000
        while j+1<len(sec_ids) and sec_ids[j+1]<=s: j+=1
        mn=s//60
        if mn!=minute:
            minute=mn; trades=0; state=0; level=0.; started=0; break_t=0; reclaim_t=0; break_j=-1; reclaim_j=-1
        if s<cool_until or trades>=5 or j<21: continue
        av=m5[j]
        if not np.isfinite(av) or av+1e-12<floor_session(s): continue
        newest=j-1+liq_shift; oldest=newest-19
        if oldest<0 or newest>=j: continue
        upper=-1e18; lower=1e18
        for q in range(oldest,newest+1):
            if hb[q]>upper: upper=hb[q]
            if lb[q]<lower: lower=lb[q]
        bid=mid[i]-H; ask=mid[i]+H
        oldestv=j-5
        if oldestv<0: continue
        prev=cb[oldestv]; start=prev; travel=0.
        for q in range(oldestv+1,j):
            v=cb[q]; travel+=abs(v-prev); prev=v
        travel+=abs(bid-prev); disp=bid-start; eff=abs(disp)/(travel+1e-9)
        if state==0:
            if ask>=upper+.10:
                state=1; level=upper; started=s; break_t=t[i]; break_j=j; reclaim_t=0; reclaim_j=-1
            elif bid<=lower-.10:
                state=-1; level=lower; started=s; break_t=t[i]; break_j=j; reclaim_t=0; reclaim_j=-1
        if state==1:
            if ask<=level-.15:
                state=2; started=s; reclaim_t=t[i]; reclaim_j=j
            elif s-started>=2 and ask>=level+.08 and disp>=.15 and eff>=.30:
                if cont_mode==1:
                    state=0; level=0.; started=0
                elif cont_mode==2:
                    state=0; level=0.; started=0; trades+=1; cool_until=s+1
                elif cont_mode==3:
                    state=0; level=0.; started=0; trades+=1
                elif cont_mode==4:
                    state=0; level=0.; started=0; cool_until=s+1
        elif state==-1:
            if bid>=level+.15:
                state=-2; started=s; reclaim_t=t[i]; reclaim_j=j
            elif s-started>=2 and bid<=level-.08 and disp<=-.15 and eff>=.30:
                if cont_mode==1:
                    state=0; level=0.; started=0
                elif cont_mode==2:
                    state=0; level=0.; started=0; trades+=1; cool_until=s+1
                elif cont_mode==3:
                    state=0; level=0.; started=0; trades+=1
                elif cont_mode==4:
                    state=0; level=0.; started=0; cool_until=s+1
        elif state==2:
            if disp<=-.15 and eff>=.30:
                E[n,0]=t[i]; E[n,1]=-1; E[n,2]=level; E[n,3]=break_t; E[n,4]=reclaim_t; E[n,5]=break_j; E[n,6]=reclaim_j; E[n,7]=j; n+=1
                trades+=1; cool_until=s+1; state=0; level=0.; started=0; break_t=0; reclaim_t=0; break_j=-1; reclaim_j=-1
        elif state==-2:
            if disp>=.15 and eff>=.30:
                E[n,0]=t[i]; E[n,1]=1; E[n,2]=level; E[n,3]=break_t; E[n,4]=reclaim_t; E[n,5]=break_j; E[n,6]=reclaim_j; E[n,7]=j; n+=1
                trades+=1; cool_until=s+1; state=0; level=0.; started=0; break_t=0; reclaim_t=0; break_j=-1; reclaim_j=-1
        if state!=0 and started>0 and s-started>20:
            state=0; level=0.; started=0; break_t=0; reclaim_t=0; break_j=-1; reclaim_j=-1
    return E[:n]

def metric(v):
    v=np.asarray(v,float); gp=float(v[v>0].sum()); gl=float(v[v<0].sum())
    return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gl':gl,'gp':gp,'pf':gp/-gl if gl<0 else 999.}

def pick_ts(E, mode, first_t, last_t):
    bj=E[:,5].astype(np.int64); rj=E[:,6].astype(np.int64); cj=E[:,7].astype(np.int64)
    bt=E[:,3].astype(np.int64); rt=E[:,4].astype(np.int64); ct=E[:,0].astype(np.int64)
    # source-like choices only; indexes clipped for last month boundary.
    if mode=='break_tick': return bt
    if mode=='break_first': return first_t[bj]
    if mode=='break_last': return last_t[bj]
    if mode=='break_next_first': return first_t[np.minimum(bj+1,len(first_t)-1)]
    if mode=='break_next_last': return last_t[np.minimum(bj+1,len(last_t)-1)]
    if mode=='break_plus2_first': return first_t[np.minimum(bj+2,len(first_t)-1)]
    if mode=='break_plus2_last': return last_t[np.minimum(bj+2,len(last_t)-1)]
    if mode=='reclaim_tick': return rt
    if mode=='reclaim_first': return first_t[rj]
    if mode=='reclaim_last': return last_t[rj]
    if mode=='reclaim_next_first': return first_t[np.minimum(rj+1,len(first_t)-1)]
    if mode=='reclaim_next_last': return last_t[np.minimum(rj+1,len(last_t)-1)]
    if mode=='confirm_tick': return ct
    if mode=='confirm_first': return first_t[cj]
    if mode=='confirm_last': return last_t[cj]
    if mode=='confirm_next_first': return first_t[np.minimum(cj+1,len(first_t)-1)]
    raise ValueError(mode)

def build_X(E, sig, align_mode, sec, al, ash):
    side=E[:,1].astype(np.int8)
    if align_mode=='signal': js=np.searchsorted(sec,sig//1000,side='left'); js=np.clip(js,0,len(sec)-1)
    elif align_mode=='break': js=E[:,5].astype(np.int64)
    elif align_mode=='reclaim': js=E[:,6].astype(np.int64)
    else: js=E[:,7].astype(np.int64)
    ac=np.where(side>0,al[js],ash[js]).astype(float)
    return np.column_stack([sig.astype(float),side.astype(float),E[:,2],ac])

def score(r):
    # dimensionless source-equivalence distance, no optimization meaning.
    return (abs(r['trades']-TARGET[0])/TARGET[0] + abs(r['winners']-TARGET[1])/TARGET[1] +
            abs(r['net']-TARGET[3])/10000. + abs(r['gl']-TARGET[4])/10000.)

def main2():
    d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False); a=d.ask_raw.to_numpy(np.float64)/1000.; b=d.bid_raw.to_numpy(np.float64)/1000.; mid=(a+b)*.5; mb=mid-H
    sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb); last_t=t[last_ix]
    e5,r5,a5=aggregate(sec,h,l,c,300); m5=map_completed(sec,e5,a5); al=np.zeros(len(sec),np.int8); ash=np.zeros(len(sec),np.int8)
    for tf in (60,180,300,600,1200):
        e,r,a2=aggregate(sec,h,l,c,tf); rr=map_completed(sec,e,r); aa=map_completed(sec,e,a2); ok=np.isfinite(aa); al+=((rr>0)&ok).astype(np.int8); ash+=((rr<0)&ok).astype(np.int8)
    modes=['break_tick','break_first','break_last','break_next_first','break_next_last','break_plus2_first','break_plus2_last','reclaim_tick','reclaim_first','reclaim_last','reclaim_next_first','reclaim_next_last','confirm_tick','confirm_first','confirm_last','confirm_next_first']
    rows=[]
    for lv,cm in [(0,2),(0,3),(-1,2),(-1,3)]:
        E=gen_events(t,mid,sec,h,l,c,m5,al,ash,cm,lv)
        for tm in modes:
            sig=pick_ts(E,tm,first_t,last_t)
            for am in ('signal','confirm'):
                X=build_X(E,sig,am,sec,al,ash); O=replay(t,mid,X); ix=nonoverlap(X,O); q=O[ix]
                m=metric(q[:,0]); m.update(label=f'lv{lv}_cont{cm}_{tm}_align{am}',raw=int(len(E)))
                if len(ix):
                    m['retro_share']=float(np.mean(sig[ix] < E[ix,0])); m['mean_retro_ms']=float(np.mean(E[ix,0]-sig[ix]))
                else: m['retro_share']=0.;m['mean_retro_ms']=0.
                m['trade_delta']=m['trades']-TARGET[0];m['winner_delta']=m['winners']-TARGET[1];m['net_delta']=m['net']-TARGET[3];m['gl_delta']=m['gl']-TARGET[4];m['score']=score(m);rows.append(m)
                print(json.dumps(m),flush=True)
    out={'target':{'trades':TARGET[0],'winners':TARGET[1],'win':TARGET[2],'net':TARGET[3],'gl':TARGET[4]},'rows':rows,'best':sorted(rows,key=lambda x:x['score'])[:40],'august_accessed':False}
    Path('/mnt/data/GAMMA2_DISCRETE_TIMESTAMP_SEMANTICS.json').write_text(json.dumps(out,indent=2,sort_keys=True))
    print('BEST')
    for x in out['best'][:20]: print(json.dumps(x))
if __name__=='__main__': main2()
