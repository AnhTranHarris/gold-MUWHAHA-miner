"""Independent original FEB044+FEB045 vector rule oracle vs online source policy.

Input exact FEB042 archive original prepared proposal arrays, not future outcomes.
This is source-stage policy parity only, not physical L7 funded economics.
"""
from __future__ import annotations
from pathlib import Path
import sys,zipfile,io,json,hashlib,os,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from feb045_source_native_context_033 import original_quality_allows
ROOT=Path(os.environ.get('DAA_FEB_ARCHIVE_DIR', '/mnt/data/feb_source_phase'))
ARCHIVE=ROOT/'FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip'

def run():
    with zipfile.ZipFile(ARCHIVE) as z:
        with np.load(io.BytesIO(z.read('FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz'))) as p:
            s=p['S'].copy().astype(np.int64);phase=p['phase'].copy().astype(np.int64)
            direc=p['D'].copy().astype(np.int64);imp=p['imp20'].copy()
        with np.load(io.BytesIO(z.read('FEB042/FEB042_CAUSAL_ENTRY_FEATURES.npz'))) as f:
            prior=f['prior10_range'].copy()
    baseline=np.isin(s,[17,21,23,25]) | ((s==27)&(prior>=16)&(prior<32)) | ((s==22)&(prior>=0)&(prior<4)) | ((s==19)&(prior>=0)&(prior<8)) | ((s==24)&(prior>=0)&(prior<4))
    baseline &= ~(((s==25)&(phase==0)) | ((s==23)&(phase==5)) | ((s==21)&(phase==0)))
    reject=((s==19)&np.isin(phase,[0,1,5])) | ((s==17)&np.isin(phase,[1,5])) | ((s==25)&(prior>=12)&(prior<16)) | ((s==19)&(phase==4)) | ((s==21)&(prior>=4)&(prior<6)) | ((s==23)&(prior>=12)&(prior<16))
    allowed=baseline&~reject
    allowed|=((s==22)&(prior>=24)&(prior<48)) | ((s==24)&(prior>=0)&(prior<12)) | ((s==26)&(prior>=8)&(prior<16))
    base=allowed&~np.isin(s,[0,2,3,4,6,27])
    pockets=[
      (s==25)&(phase==2)&(prior>=8)&(prior<10),
      (s==25)&(phase==1)&(prior>=16)&(prior<20),
      (s==23)&(phase==1)&(prior>=8)&(prior<10),
      (s==17)&(phase==3)&(prior>=6)&(prior<8),
      (s==17)&(phase==4)&(prior>=6)&(prior<8),
      (s==19)&(prior>=2)&(prior<4)&(direc*imp>=1)&(direc*imp<2),
      (s==25)&(phase==3)&(prior>=16)&(prior<20),
      (s==23)&(phase==2)&(prior>=16)&(prior<20),
      (s==17)&(phase==2)&(prior>=6)&(prior<8),
      (s==25)&(phase==4)&(prior>=20)&(prior<24)
    ]
    ref=base & ~np.logical_or.reduce(pockets[:9])
    online=np.fromiter((original_quality_allows(int(s[i]),int(phase[i]),float(prior[i]),float(direc[i]*imp[i]),cut=9) for i in range(len(s))),dtype=np.bool_,count=len(s))
    bad=np.flatnonzero(ref!=online)
    result={"classification":"ORIGINAL_FEB042_044_045_SOURCE_MASK_ONLY_NOT_V1_ECONOMIC_OR_FUNDED_PARITY",
            "exact_source_proposals":len(s),"frozen_source_permitted":int(ref.sum()),
            "native_online_permitted":int(online.sum()),"event_mask_mismatch":len(bad),
            "reference_mask_sha256":hashlib.sha256(ref.astype('u1').tobytes()).hexdigest(),
            "online_mask_sha256":hashlib.sha256(online.astype('u1').tobytes()).hexdigest(),
            "by_source":[{'source':int(src),'all':int((s==src).sum()),'admitted':int(np.sum(ref&(s==src)))} for src in np.unique(s)],
            "source_fitted_on":"February outcomes; no month labels in live decision",
            "note":"Original source tape decisions only; no endogenous physical portfolio funded regeneration."}
    if len(bad): result['first_mismatch']=int(bad[0]);raise AssertionError(result)
    return result

if __name__=='__main__':
    data=run();print(json.dumps(data,indent=2));
    (Path(__file__).parent/'FEB045_SOURCE_MASK_PARITY_033.json').write_text(json.dumps(data,indent=2)+'\n')