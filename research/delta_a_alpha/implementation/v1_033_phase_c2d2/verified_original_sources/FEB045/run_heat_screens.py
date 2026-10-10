import os,sys,json,time,itertools
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/feb044_work');sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
import feb044_screen as h
import heat_engine as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(h.m,k).copy())
m.total=h.m.total;m.imp20=h.imp
s=m.S;p=h.phase;r=h.prior
reject=((s==19)&np.isin(p,[0,1,5])) | ((s==17)&np.isin(p,[1,5])) | ((s==25)&(r>=12)&(r<16)) | ((s==19)&(p==4)) | ((s==21)&(r>=4)&(r<6)) | ((s==23)&(r>=12)&(r<16))
allowed=h.base_allowed.copy()&~reject
allowed|=(s==22)&(r>=24)&(r<48);allowed|=(s==24)&(r>=0)&(r<12);allowed|=(s==26)&(r>=8)&(r<16)
keep_sources=[17,19,21,22,23,24,25,26,27]
bit=sum(1<<(src-10) for src in range(17,29) if src not in keep_sources)
params={**h.params,'source22cap':768,'source27cap':64,'phase3cap':448,'phase4cap':448,'phase5cap':128,'l3_excluded_hours':bit}
m.spread=np.where((s>=17)&~allowed,np.inf,h.spr)
h.exits()
for k in ['X','P']:setattr(m,k,getattr(h.m,k).copy())

def run(name,over):
 t0=time.time();o,ld=m.run(**{**params,**over});o['name']=name;o['over']=over;o['secs']=round(time.time()-t0,2);print('SCREEN',name,o['net'],o['gl'],o['pf'],o['trades'],o['event_eq_dd_lb'],o['maxopen'],o['secs'],flush=True);return o,ld
if __name__=='__main__':
 out=[];best=[]
 cases=[('baseline',{})]
 # independently sensitive to global headroom, directional stress and distinct source equity concentration
 for shock in [0,3,8,15]:
  for hg in [2000,4000,6000,8500,12000,20000]:cases.append((f'global_{shock}_{hg}',dict(heat_global=hg,shock_usd=shock)))
 for source in [25,22,27]:
  for lim in [200,500,1000,2000,4000,8000]:cases.append((f'source_{source}_{lim}',{'heat_s%d'%source:lim}))
 for gap in [.25,.5,1.,2.,4.,8.]:cases.append((f'gap_{gap}',dict(same_source_min_gap=gap)))
 for delay in [50,200,1000,5000]:cases.append((f'cool_{delay}',dict(source_cooldown_ms=delay)))
 for cap in [128,256,384,512]:cases.append((f'srccap_{cap}',dict(source_maxopen_extra=cap)))
 for i,(name,over) in enumerate(cases):
  o,ld=run(name,over);out.append(o)
  if o['net']>192000 and o['trades']>=11000:best.append((o['name'],o['net'],o['gl'],o['event_eq_dd_lb']))
  if i%10==0:Path('/mnt/data/feb045/screen_heat.json').write_text(json.dumps(out,indent=2))
 Path('/mnt/data/feb045/screen_heat.json').write_text(json.dumps(out,indent=2));print('TOP',sorted(best,key=lambda a:(-abs(a[2]), a[1]),reverse=True)[:15],flush=True)
