"""Recover V1 January Gamma source proposals (NOT a certified MT5 EA).
Proposal outcomes generated for simulation ONLY; admissibility later uses funded exits.
"""
import sys,os,time,json
from pathlib import Path
import numpy as np
SOURCE=Path('/mnt/data/jan_research/032/source');sys.path.insert(0,str(SOURCE));os.chdir(SOURCE)
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
import gamma02_ny17_quantum_minute_window_075 as w
from gamma02_083_heat_parent_ownership_084 import renewal_owned
import gamma02_dynamic_watchdog_router_119 as wd
import gamma02_m1_density as gmd
stt=time.monotonic();t,a,b,mid,h4,h1,m15,m5=J.DATA[:8];start,end=J.DATA[-2:]
def pp():return wd.prep_month(1)
gmd.prep=pp
D,pei,pxi,pd,src,mins,disp=w.prep();print('PARENTS',len(pei),'elapsed',round(time.monotonic()-stt,1),flush=True)
DAY=86400000
pt=t[pei];lm=wd.local_minute(pt);lh=lm//60;lmin=lm%60
target=(pt>=start)&(pt<end);macro=(h4[pei]!=0)&(h4[pei]==h1[pei])&(pd==h4[pei]);base=target&macro&(lh>=12)&(lh<=13)
sig=((h4[pei]+1)*81+(h1[pei]+1)*27+(m15[pei]+1)*9+(m5[pei]+1)*3+(pd+1)).astype(np.int16)
keys=np.stack((pt//DAY,lh,lmin//10,sig),axis=1)
cells=np.unique(keys[np.nonzero(base)[0]],axis=0)
print('CELLS',len(cells),flush=True)
parts=[];cellparts=[];ownparts=[]; seqparts=[];parentparts=[];p0s=[];pends=[];pcell=[];parent_id=0;groups=0
for cell_id,key in enumerate(cells):
 day,hh,b10,sc=[int(x) for x in key]
 jj=np.nonzero(base&(keys[:,0]==day)&(keys[:,1]==hh)&(keys[:,2]==b10)&(keys[:,3]==sc))[0]
 if not len(jj):continue
 q=int([1190,1190,1190,1190,1190,1100][b10])
 A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2)
 E,X,R,Dd,P,H,O=A[:7]
 if not len(E):continue
 # For candidate children, ownership and ordinal are physical-family identifiers.
 # Cross-parent chronological admission happens in the later portfolio engine.
 ords=np.zeros(len(E),np.int32);by=np.zeros(len(jj),np.int32)
 for k,o in enumerate(O):o=int(o);ords[k]=by[o];by[o]+=1
 parts.append((E,X,R,Dd,P,H));cellparts.append(np.full(len(E),cell_id,np.int32));ownparts.append(O+parent_id);seqparts.append(ords)
 p0s.extend(pei[jj].tolist());pends.extend(pxi[jj].tolist());pcell.extend([cell_id]*len(jj));parent_id+=len(jj);groups+=1
 if groups%50==0:print('GROUPS',groups,'wd proposals',sum(len(q[0]) for q in parts),'elapsed',round(time.monotonic()-stt,1),flush=True)
wdarr=[np.concatenate([z[k] for z in parts]) for k in range(6)]; W=len(wdarr[0]);print('ALL WD candidates',W,'parents',parent_id,'elapsed',round(time.monotonic()-stt,1),flush=True)
# Original supporting L3 hourly, distinct Asia/London session cells and cold-start.
cov=J.build_coverage();cold=J.build_coldstart(50,450,64);rules=[L.build_rule(k,l,stx,cap) for k,l,n,stx,cap in L.LEAN]
supps=[cov,cold,*rules]; labels=['L3_hourly','L3_cold','L3_asia','L3_london','L3_overlap','L3_ny']; print('SUPP',[(k,len(q[0])) for k,q in zip(labels,supps)],flush=True)
# The original supplemental de-dup and 512 cap are NOT an assumed global broker cap.
sources=[];dat=[];cids=[];owners=[];seqs=[]
for j,q in enumerate(supps):
 dat.append(q);sources.append(np.full(len(q[0]),j+1,np.int8));cids.append(np.full(len(q[0]),-1,np.int32));owners.append(np.full(len(q[0]),-1,np.int32));seqs.append(np.full(len(q[0]),-1,np.int32))
dat.append(wdarr);sources.append(np.zeros(W,np.int8));cids.append(np.concatenate(cellparts));owners.append(np.concatenate(ownparts));seqs.append(np.concatenate(seqparts))
A=[np.concatenate([p[k] for p in dat]) for k in range(6)]
S=np.concatenate(sources);C=np.concatenate(cids);O=np.concatenate(owners);N=np.concatenate(seqs)
# Original supplemental source priority on collision, WD follows original supplemental source.
order=np.lexsort((np.arange(len(S)),S,A[0]))
E,X,R,Dd,P,H=[z[order] for z in A]; S,C,O,N=[z[order] for z in (S,C,O,N)]
assert np.all(E<=X); assert not np.any((E<0)|(X>=len(t)))
# Exact recorded-side pnl reconciliation, modest float error expected.
actual=((np.where(Dd>0,b[X],a[X]).astype(np.int64)-R)*Dd)/1000.-.02
assert np.max(np.abs(actual-P))<0.05,(np.max(np.abs(actual-P)),np.argmax(np.abs(actual-P)))
np.savez_compressed('/mnt/data/jan_research/JAN037_ORIGINAL_SOURCE_PROPOSALS.npz',E=E,X=X,R=R,D=Dd,P=P,H=H,S=S,C=C,O=O,N=N,parent_start=np.asarray(p0s,np.int64),parent_end=np.asarray(pends,np.int64),parent_cell=np.asarray(pcell,np.int32))
print('PREP_DONE',json.dumps(dict(ticks=len(t),wd_candidates=W,all_candidates=len(E),parent_candidates=parent_id,cells=len(cells),seconds=round(time.monotonic()-stt,1))),flush=True)
