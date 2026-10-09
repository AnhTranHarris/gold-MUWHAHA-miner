import sys,json,time,itertools
from pathlib import Path
import numpy as np
R=Path('/mnt/data/feb044_work');sys.path[:0]=[str(R),'/mnt/data/feb045'];import feb044_screen as h;import heat_engine as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(h.m,k).copy())
m.total=h.m.total;m.imp20=h.imp
s=m.S;ph=h.phase;r=h.prior
reject=((s==19)&np.isin(ph,[0,1,5])) | ((s==17)&np.isin(ph,[1,5])) | ((s==25)&(r>=12)&(r<16)) | ((s==19)&(ph==4)) | ((s==21)&(r>=4)&(r<6)) | ((s==23)&(r>=12)&(r<16))
allowed=h.base_allowed.copy()&~reject;allowed|=(s==22)&(r>=24)&(r<48);allowed|=(s==24)&(r>=0)&(r<12);allowed|=(s==26)&(r>=8)&(r<16)
keep_sources=[17,19,21,22,23,24,25,26,27];bit=sum(1<<(src-10) for src in range(17,29) if src not in keep_sources)
params={**h.params,'source22cap':768,'source27cap':64,'phase3cap':448,'phase4cap':448,'phase5cap':128,'l3_excluded_hours':bit}
h.exits(phase25={1:10,2:10,5:10});m.X=h.m.X.copy();m.P=h.m.P.copy()
base=(allowed | (s<17))&~np.isin(s,[0,2,3,4,6,27])
P={
 's25_p2_rng8_10':(s==25)&(ph==2)&(r>=8)&(r<10),
 's25_p1_rng16_20':(s==25)&(ph==1)&(r>=16)&(r<20),
 's23_p1_rng8_10':(s==23)&(ph==1)&(r>=8)&(r<10),
 's17_p3_rng6_8':(s==17)&(ph==3)&(r>=6)&(r<8),
 's17_p4_rng6_8':(s==17)&(ph==4)&(r>=6)&(r<8),
 's19_rng2_4_imp1_2':(s==19)&(r>=2)&(r<4)&(m.D*h.imp>=1)&(m.D*h.imp<2),
 's25_p3_rng16_20':(s==25)&(ph==3)&(r>=16)&(r<20),
 's23_p2_rng16_20':(s==23)&(ph==2)&(r>=16)&(r<20),
 's17_p2_rng6_8':(s==17)&(ph==2)&(r>=6)&(r<8),
 's25_p4_rng20_24':(s==25)&(ph==4)&(r>=20)&(r<24),
}
order=list(P);out=[]
combos=[[],order[:1],order[:2],order[:3],order[:4],order[:5],order[:6],order[:7],order[:8],order[:9],order[:10],
 [order[i] for i in [0,1,2,3,4,5,7]],
 [order[i] for i in [0,1,2,3,4,7]],
 [order[i] for i in [0,1,2,3,4,6,7]],
 [order[i] for i in [0,1,2,3,4,5,6,7]]]
for heat,shock in [(1e12,0),(6500,0),(8500,3),(10000,3),(7500,0)]:
 for combo in combos:
  d=np.zeros_like(base)
  for key in combo:d|=P[key]
  m.spread=np.where(~(base&~d),np.inf,h.spr)
  o,ld=m.run(**params,heat_global=heat,shock_usd=shock)
  z={k:o[k] for k in ['net','gl','pf','trades','maxopen','event_eq_dd_lb']};z.update(heat=heat,shock=shock,denied=combo)
  out.append(z); print('PKT',len(out),z['net'],z['gl'],z['pf'],z['trades'],z['event_eq_dd_lb'],z['heat'],len(combo),flush=True)
  with open('/mnt/data/feb045/pocket_screens.jsonl','a') as f:f.write(json.dumps(z)+'\n')
print('DONE',len(out))
