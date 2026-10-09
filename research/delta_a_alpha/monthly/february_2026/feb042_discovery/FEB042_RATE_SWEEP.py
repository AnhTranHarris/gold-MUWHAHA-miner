exec(open('/mnt/data/feb042/screen7.py').read().split('res=[];t0=')[0])
# Evaluate fully fixed 512 cap, Feb-selected known source mix and first-passage TP.
source_set=[17,21,23,25,27];allowed=np.zeros(m.total,bool)
for s in source_set:allowed|=(m.S==s)&((prior>=16)&(prior<32) if s==27 else True)
bit=sum(1<<(s-10) for s in range(17,29) if s not in source_set)
m.spread=np.where(ex|((m.S>=17)&~allowed),np.inf,spr)
for s,threshold in {21:20,23:15,25:20,27:30}.items():
 k=ths.tolist().index(float(threshold));flag=raw['S'][sel]==s;inds=sel[flag];m.X[inds]=xx[flag,k];m.P[inds]=pp[flag,k]
out=[]
for rate in [1,2,3,4,5,6,7,8,9,10,12,15]:
 q=params.copy();q.update(maxopen=512,sidecap=512,per_second=rate,l3_excluded_hours=bit)
 z,L=m.run(**q)
 row={k:z[k] for k in ['net','trades','gl','pf','event_eq_dd_lb','maxopen']};row['rate']=rate;out.append(row);print('RATE',row,flush=True)
(w/'FEB042_RATE_SCREEN8.json').write_text(json.dumps(out,indent=2))