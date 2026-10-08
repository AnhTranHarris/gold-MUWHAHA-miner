import sys,heapq,json
from collections import deque
import numpy as np
sys.path.insert(0,'/mnt/data/gamma02_jan_repro')
import feb_replay_jan_milestone_132a as F
import gamma02_campaign_heartbeat_019 as hb
OUT='/mnt/data/gamma02_jan_repro/feb_hb_online_cache_133b.npz'

def group_features(et,xt,p,key,windows,prefix,out):
    vals,inv=np.unique(key,return_inverse=True);order=np.argsort(inv,kind='stable');cuts=np.flatnonzero(np.diff(inv[order]))+1;groups=np.split(order,cuts)
    feats={W:{k:np.zeros(len(et),dtype=d) for k,d in [('n',np.int16),('mean',np.float32),('pf',np.float32),('win',np.float32),('net',np.float32),('dd',np.float32),('last',np.float32)]} for W in windows}
    for idxs in groups:
        pending=[];seq=0
        qs={W:deque() for W in windows};sums={W:0.0 for W in windows};gps={W:0.0 for W in windows};gls={W:0.0 for W in windows};wins={W:0 for W in windows}
        # dd approximation inside rolling window = peak-to-current of realized sequence recomputed on update only (window small)
        for i in idxs:
            now=int(et[i])
            while pending and pending[0][0]<=now:
                _,_,v=heapq.heappop(pending);v=float(v)
                for W in windows:
                    q=qs[W]
                    if len(q)>=W:
                        old=q.popleft();sums[W]-=old
                        if old>0:gps[W]-=old;wins[W]-=1
                        elif old<0:gls[W]-=old
                    q.append(v);sums[W]+=v
                    if v>0:gps[W]+=v;wins[W]+=1
                    elif v<0:gls[W]+=v
            for W in windows:
                q=qs[W];nn=len(q);f=feats[W];f['n'][i]=nn
                if nn:
                    f['net'][i]=sums[W];f['mean'][i]=sums[W]/nn;f['win'][i]=wins[W]/nn;f['pf'][i]=gps[W]/(-gls[W]) if gls[W]<0 else 999.;f['last'][i]=q[-1]
                    arr=np.asarray(q,float);bal=np.cumsum(arr);prior=np.r_[0.,bal[:-1]];peak=np.maximum.accumulate(prior);f['dd'][i]=float(np.max(peak-bal))
            heapq.heappush(pending,(int(xt[i]),seq,float(p[i])));seq+=1
    for W in windows:
        for k,v in feats[W].items():out[f'{prefix}{W}_{k}']=v

def main(ms=250):
    E=hb.heartbeat_events(F.DATA[:8],ms,4);et,xt,p,r,src=E;m=(et>=F.START)&(et<F.END);et,xt,p,r,src=[z[m] for z in E]
    idx=np.searchsorted(F.t,et);b10=((et//600000)%6).astype(np.int8);hour=src.astype(np.int8);d=np.zeros(len(et),np.int8)
    # infer direction from entry/exit mark not possible directly; derive using hb candidate generator aligned by re-running candidates
    ii,dd,ss,hold,tp,sl=hb.heartbeat_candidates(F.t,F.mid,F.h4,F.h1,F.m15,F.m5,int(ms),4)
    mm=(F.t[ii]>=F.START)&(F.t[ii]<F.END);ii=ii[mm];dd=dd[mm];ss=ss[mm]
    # heartbeat_events preserves candidate ordering after lifecycle grouping + stable entry-time sort; align by entry timestamps, source and occurrence sequence
    # robust direct alignment: build per (time,source) queues of candidate dirs
    from collections import defaultdict,deque as DQ
    q=defaultdict(DQ)
    for tt,s0,d0 in zip(F.t[ii],ss,dd):q[(int(tt),int(s0))].append(int(d0))
    for k,(tt,s0) in enumerate(zip(et,src)):
        d[k]=q[(int(tt),int(s0))].popleft()
    activity_count=(np.searchsorted(F.t,et,side='left')-np.searchsorted(F.t,et-60000,side='left')+1).astype(np.int32)
    act=np.select([activity_count<=200,activity_count<=500],[0,1],default=2).astype(np.int8)
    cell=(src.astype(np.int64)*100000+(b10.astype(np.int64))*10000+(F.h4[idx]+1).astype(np.int64)*2000+(F.h1[idx]+1).astype(np.int64)*400+(F.m15[idx]+1).astype(np.int64)*80+(F.m5[idx]+1).astype(np.int64)*16+(d+1).astype(np.int64)*4+act.astype(np.int64))
    macro=(src.astype(np.int64)*1000+(F.h4[idx]+1).astype(np.int64)*200+(F.h1[idx]+1).astype(np.int64)*40+(d+1).astype(np.int64)*8+act.astype(np.int64))
    out=dict(et=et,xt=xt,p=p.astype(np.float32),reason=r,src=src,idx=idx.astype(np.int64),d=d,b10=b10,act=act,activity_count=activity_count,cell=cell,macro=macro,ms=np.int32(ms))
    group_features(et,xt,p,src,[4,8,16,32],'src',out)
    group_features(et,xt,p,cell,[4,8,16],'cell',out)
    group_features(et,xt,p,macro,[8,16,32],'mac',out)
    np.savez_compressed(OUT,**out)
    print(json.dumps({'events':len(et),'net_all':float(p.sum()),'cells':int(np.unique(cell).size),'macro':int(np.unique(macro).size),'out':OUT},indent=2))
if __name__=='__main__':main()