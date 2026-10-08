import numpy as np,json,heapq,itertools,datetime
B0=np.load('/mnt/data/gamma02_jan_repro/feb_baseline_components_133b.npz');B={k:B0[k] for k in B0.files};B0.close()
E=B['WD_E'];X=B['WD_X'];P=B['WD_P'];
# stable groups by exact market tick index
u, starts, counts=np.unique(E,return_index=True,return_counts=True)
groups=[]
for gi,(s,c) in enumerate(zip(starts,counts)):
 ix=np.arange(s,s+c,dtype=np.int64); groups.append((int(E[s]),int(np.max(X[ix])),float(np.mean(P[ix])),float(np.sum(P[ix])),ix))

def pf(a):
 a=np.asarray(a,float); gl=a[a<0].sum();gp=a[a>0].sum();return float(gp/-gl if gl<0 else 999.)
def metrics(ix):
 pp=P[ix];o=np.argsort(X[ix],kind='stable');p=pp[o];gp=p[p>0].sum();gl=p[p<0].sum();bal=peak=dd=0
 for v in p:bal+=v;peak=max(peak,bal);dd=max(dd,peak-bal)
 return dict(net=float(p.sum()),trades=len(p),gl=float(gl),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),exp=float(np.mean(p)),dd=float(dd))
def route(fw,sw,off,on,onpf,slowfloor,lowq,strongthr,midq):
 pending=[];hist=[];state=True;sel=[];seq=0;stats={'deactivate':0,'reactivate':0,'groups':0,'shadow_updates':0,'skipped_groups':0,'partial_groups':0}
 for entry,exit_,mean,total,ix in groups:
  while pending and pending[0][0]<=entry:
   _,_,m=heapq.heappop(pending);hist.append(m);stats['shadow_updates']+=1
  if len(hist)>=fw:
   fast=np.asarray(hist[-fw:]); fm=float(fast.mean()); fp=pf(fast)
   slow=np.asarray(hist[-sw:]) if len(hist)>=sw else np.asarray(hist); sm=float(slow.mean()) if len(slow) else 0.
   old=state
   if state:
    if fm<off or (len(slow)>=sw and sm<slowfloor):state=False
   else:
    if fm>=on and fp>=onpf and (len(slow)<sw or sm>=slowfloor):state=True
   if old and not state:stats['deactivate']+=1
   if (not old) and state:stats['reactivate']+=1
  else: fm=999.
  if state:
   quota=len(ix)
   if len(hist)>=fw:
    if fm<strongthr: quota=min(lowq,len(ix))
    elif midq>0: quota=min(midq,len(ix))
   if quota<len(ix):stats['partial_groups']+=1
   sel.extend(ix[:quota].tolist());stats['groups']+=1
  else:stats['skipped_groups']+=1
  heapq.heappush(pending,(exit_,seq,mean));seq+=1
 return np.asarray(sel,np.int64),stats
rows=[]
for fw,sw,off,on,onpf,slowfloor,lowq,strongthr,midq in itertools.product(
 [4,8],[16],[0.,0.5],[1.,1.5],[1.,1.5],[0.],[64,128],[2.,3.],[0,256]):
 if on<off:continue
 ix,stats=route(fw,sw,off,on,onpf,slowfloor,lowq,strongthr,midq);s=metrics(ix);rows.append(dict(fw=fw,sw=sw,off=off,on=on,onpf=onpf,slowfloor=slowfloor,lowq=lowq,strongthr=strongthr,midq=midq,stats=stats,**s))
# Pareto-ish sorted: prioritize positive net, low gl, pf, keep many trades
rows.sort(key=lambda r:(r['pf'],r['net'],-abs(r['gl']),r['trades']),reverse=True)
json.dump({'rows':rows},open('/mnt/data/gamma02_jan_repro/wd_shadow_router_screen_133i.json','w'),indent=2)
# Print high net and high PF candidates separately
print('TOP_PF')
for r in rows[:40]:print(json.dumps({k:r[k] for k in ['fw','sw','off','on','onpf','slowfloor','lowq','strongthr','midq','net','trades','gl','pf','win','exp','dd','stats']}))
print('TOP_NET_MIN_PF2')
q=[r for r in rows if r['pf']>=2]
q.sort(key=lambda r:(r['net'],r['pf']),reverse=True)
for r in q[:40]:print(json.dumps({k:r[k] for k in ['fw','sw','off','on','onpf','slowfloor','lowq','strongthr','midq','net','trades','gl','pf','win','exp','dd','stats']}))