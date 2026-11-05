from source import *
import sys,json
source=sys.argv[1];mon=sys.argv[2]
t,b,a=source_month(source,mon)
print('SOURCE',source,mon,'rows',len(t),flush=True)
ids=source_candidates(t,b,a,mon,source)
print('CANDIDATES',len(ids),flush=True)
# 250000 equally spaced first 1s signals over the month, without outcome preselection
sample=ids[np.linspace(0,len(ids)-1,min(250000,len(ids)),dtype=np.int64)]
f=sample_features(t,b,a,sample)
for k in ('spread','mid500','mid2000','mid6000','mid15000','count500','count2000','count6000','count15000'):
 v=np.asarray(f[k]);print(k,'p10,p25,p50,p75,p90,p99',np.quantile(v,[.1,.25,.5,.75,.9,.99]).round(2).tolist(),flush=True)
s=f['spread'];m=f['mid2000']/2;absvol=np.abs(f['mid6000']/2)
print('2s move vs spread frac >0.5,1,2,4',[(abs(m)>s*x).mean() for x in (.5,1,2,4)])
print('6s move vs spread frac >0.5,1,2,4',[(absvol>s*x).mean() for x in (.5,1,2,4)])
