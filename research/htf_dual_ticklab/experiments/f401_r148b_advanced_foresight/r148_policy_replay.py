from pathlib import Path
import numpy as np, json
R=Path('/mnt/data/R147_COMMON');O=Path('/mnt/data/R148_RESULTS')
CFG={
 'coinexx':dict(rescue=0.8021619915962219,hunter=0.9432624578475952,expect=(454376,9998)),
 'dukascopy':dict(rescue=0.7198813557624817,hunter=0.928738534450531,expect=(505659,9998)),
}
def replay(broker):
 c=CFG[broker];B=G=0;rows=[]
 for m in ('01','02','06','07'):
  meta=np.load(R/f'{broker}_{m}_meta.npy',mmap_mode='r');y=meta[:,0].astype(np.int8);v=meta[:,1].astype(bool);base=np.load(R/f'{broker}_{m}_r24_teacher.npy',mmap_mode='r')[:,1].astype(bool);rs=np.load(O/f'R148B_{broker}_RESCUE_SCORE_{m}.npy',mmap_mode='r');hs=np.load(O/f'R148B_{broker}_HUNTER_SCORE_{m}.npy',mmap_mode='r');enh=(base&~(base&(rs>=c['rescue'])))|((~base)&v&(hs>=c['hunter']));bb=int(np.sum(enh&(y!=0)));gg=int(np.sum(enh&(y==0)));B+=bb;G+=gg;rows.append([m,bb,gg])
 assert (B,G)==c['expect'],(broker,B,G,c['expect'])
 return {'broker':broker,'bad':B,'correct_lost':G,'rows':rows}
if __name__=='__main__':
 out=[replay('coinexx'),replay('dukascopy')];print(json.dumps(out,indent=2))
