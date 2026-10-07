import sys,json,gc,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd

def build_events_stream(t,mid,h4,h1,start_hour=7,end_hour=15,step=50,max_levels=200):
    minute=t//60000
    starts=np.r_[0,np.nonzero(minute[1:]!=minute[:-1])[0]+1]
    ends=np.r_[starts[1:],len(t)]
    ev=[];dirs=[];hours=[];disps=[]
    for s,e in zip(starts,ends):
        h=int((t[s]//3600000)%24)
        if h<start_hour or h>end_hour:continue
        d=int(h4[s])
        if d==0 or int(h1[s])!=d:continue
        x=(mid[s:e].astype(np.int64)-int(mid[s]))*d
        run=np.maximum.accumulate(x)
        lev=np.minimum(np.maximum(run//step,0),max_levels).astype(np.int16)
        prev=0
        ch=np.nonzero(lev>np.r_[0,lev[:-1]])[0]
        for q in ch:
            L=int(lev[q])
            for z in range(prev+1,L+1):
                ev.append(s+int(q));dirs.append(d);hours.append(h);disps.append(z*step)
            prev=L
    return np.asarray(ev,np.int64),np.asarray(dirs,np.int8),np.asarray(hours,np.int8),np.asarray(disps,np.int32)

def decode(sc):
    vals=[]
    for _ in range(5):vals.append((sc%3)-1);sc//=3
    return tuple(reversed(vals))

def main():
    t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep()
    idx,dr,hr,disp=build_events_stream(t,mid,h4,h1)
    print('events',len(idx),flush=True)
    H4=h4[idx].astype(np.int16);H1=h1[idx].astype(np.int16);M15=m15[idx].astype(np.int16);M5=m5[idx].astype(np.int16);D=dr.astype(np.int16)
    sc=(((((H4+1)*3+(H1+1))*3+(M15+1))*3+(M5+1))*3+(D+1)).astype(np.int16)
    entry=np.where(dr>0,a[idx],b[idx]).astype(np.int64)
    rows=[]
    for hour in range(7,16):
        hm=(hr==hour); codes=np.unique(sc[hm])
        for hs in [15,30,60,120,300,600,900,1800]:
            ii=np.nonzero(hm)[0];j=np.searchsorted(t,t[idx[ii]]+hs*1000,side='left');j=np.minimum(j,len(t)-1)
            ex=np.where(dr[ii]>0,b[j],a[j]); pnl=((ex-entry[ii])*dr[ii])/1000.-0.02; c=sc[ii]
            for cd in codes:
                q=(c==cd);n=int(q.sum())
                if n<40:continue
                v=pnl[q];gp=float(v[v>0].sum());gl=float(v[v<=0].sum());st=decode(int(cd))
                rows.append(dict(hour=hour,h4=st[0],h1=st[1],m15=st[2],m5=st[3],direction=st[4],horizon_s=hs,n=n,net=float(v.sum()),mean=float(v.mean()),win=float(np.mean(v>0)),pf=float(gp/-gl if gl<0 else 999)))
        top=[x for x in rows if x['hour']==hour and x['horizon_s'] in (60,300,900,1800) and x['n']>=100];top.sort(key=lambda x:x['net'],reverse=True)
        print('TOP',hour,flush=True)
        for x in top[:12]:print(json.dumps(x),flush=True)
        json.dump({'events':len(idx),'completed_hour':hour,'rows':rows},open('/mnt/data/gamma02_london_overlap_markout_stream_001.partial.json','w'),indent=2)
    json.dump({'events':len(idx),'rows':rows},open('/mnt/data/gamma02_london_overlap_markout_stream_001.json','w'),indent=2)
if __name__=='__main__':main()