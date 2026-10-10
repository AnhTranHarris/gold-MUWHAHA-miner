import sys,os,json,time
import numpy as np
from pathlib import Path
r=Path('/mnt/data/feb041');o=Path('/mnt/data/feb042')
os.environ['DAA_JAN039_RESEARCH_DIR']=str(r)
os.environ['DAA_JAN039_EQUITY_HELPERS']=str(r/'original/source')
sys.path[:0]=[str(r),'/mnt/data/jan040_commit',str(r/'original/source')]
import feb041_legacy_engine as m
from jan039_reference_replay import first_profitable_exit
z=np.load(r/'FEB041_EXPANDED_L3_50MS_PROPOSALS.npz')
for k in 'EXRDPHSCON':setattr(m,k,z[k].copy())
z.close()
valid=(m.t[m.E]>=1769904000000)&(m.t[m.E]<1772323200000)
for k in 'EXRDPHSCON':setattr(m,k,getattr(m,k)[valid])
m.total=len(m.E);qsp=(m.a[m.E].astype(np.int64)-m.b[m.E])/1000.
i=np.searchsorted(m.t,m.t[m.E]-20000,'left');m.imp20=((m.a[m.E].astype(np.int64)+m.b[m.E])-(m.a[i].astype(np.int64)+m.b[i]))/2000.
phase=(m.t[m.E]//600000)%6;rules=json.load(open(r/'JAN038_SELECTED_EXACT.json'))['signal_gating_source_phase_pairs'];excluded=np.zeros(m.total,bool)
for s,ph in rules:excluded|=(m.S==s)&(phase==ph)
origx=m.X.copy();origp=m.P.copy();outx=origx.copy();outp=origp.copy()
sc27=np.where((m.S==27)&(~excluded)&(qsp<=3)&(m.D<0))[0];sc26=np.where((m.S==26)&(qsp<=3)&(m.D<0))[0]
for phases,take in [((2,3),50.),((0,),60.),((4,),35.)]:
 ii=sc27[np.isin(phase[sc27],phases)]
 if len(ii):a,b=first_profitable_exit(m.a,m.b,m.E,origx,m.R,m.D,ii,take);outx[ii]=a;outp[ii]=b
if len(sc26):
 a,b=first_profitable_exit(m.a,m.b,m.E,origx,m.R,m.D,sc26,35.);outx[sc26]=a;outp[sc26]=b
np.savez_compressed(o/'FEB042_JAN039_PREPARED_PROPOSALS.npz',E=m.E,X=outx,R=m.R,D=m.D,P=outp,H=m.H,S=m.S,C=m.C,O=m.O,N=m.N,phase=phase,excluded=excluded,spread=qsp,imp20=m.imp20)
print('PREPARED',m.total,len(sc27),len(sc26),'src_counts',[(int(s),int((m.S==s).sum())) for s in np.unique(m.S)],flush=True)
