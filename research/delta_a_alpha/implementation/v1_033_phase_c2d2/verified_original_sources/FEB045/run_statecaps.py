from pathlib import Path
import sys,json
import numpy as np
R=Path('/mnt/data/feb044_work');PTH=Path('/mnt/data/feb045');sys.path[:0]=[str(R),str(PTH)];import feb044_screen as h;import engine_statecaps as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(h.m,k).copy())
m.total=h.m.total;m.imp20=h.imp;m.prior10=h.prior
s=m.S;ph=h.phase;r=h.prior
reject=((s==19)&np.isin(ph,[0,1,5])) | ((s==17)&np.isin(ph,[1,5])) | ((s==25)&(r>=12)&(r<16)) | ((s==19)&(ph==4)) | ((s==21)&(r>=4)&(r<6)) | ((s==23)&(r>=12)&(r<16))
allowed=h.base_allowed.copy()&~reject;allowed|=(s==22)&(r>=24)&(r<48);allowed|=(s==24)&(r>=0)&(r<12);allowed|=(s==26)&(r>=8)&(r<16)
keep_sources=[17,19,21,22,23,24,25,26,27];bit=sum(1<<(src-10) for src in range(17,29) if src not in keep_sources)
params={**h.params,'source22cap':768,'source27cap':64,'phase3cap':448,'phase4cap':448,'phase5cap':128,'l3_excluded_hours':bit}
h.exits(phase25={1:10,2:10,5:10});m.X=h.m.X.copy();m.P=h.m.P.copy()
base=(allowed | (s<17))&~np.isin(s,[0,2,3,4,6,27]);order=[
(s==25)&(ph==2)&(r>=8)&(r<10),
(s==25)&(ph==1)&(r>=16)&(r<20),
(s==23)&(ph==1)&(r>=8)&(r<10),
(s==17)&(ph==3)&(r>=6)&(r<8),
(s==17)&(ph==4)&(r>=6)&(r<8),
(s==19)&(r>=2)&(r<4)&(m.D*h.imp>=1)&(m.D*h.imp<2),
(s==25)&(ph==3)&(r>=16)&(r<20),
(s==23)&(ph==2)&(r>=16)&(r<20),
(s==17)&(ph==2)&(r>=6)&(r<8),
(s==25)&(ph==4)&(r>=20)&(r<24)]
log=[]
for cut in [8,9]:
 deny=np.zeros_like(base)
 for p in order[:cut]:deny|=p
 m.spread=np.where(~(base&~deny),np.inf,h.spr)
 for c22 in [192,256,320,384,448,512]:
  for c25 in [192,256,320,384,448,512]:
   out,ld=m.run(**params,s22_state_cap=c22,s25_state_cap=c25)
   z={k:out[k] for k in ['net','gl','pf','trades','maxopen','event_eq_dd_lb']};z.update(cut=cut,cap22=c22,cap25=c25)
   log.append(z);print('STATE',z,flush=True)
 Path('/mnt/data/feb045/statecaps_screens.json').write_text(json.dumps(log,indent=2))
