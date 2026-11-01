"""Independent, non-training Stage2A precursor: F395 originals vs J2/L2/M2 and P2/Q2.
This does not assert original R150Q parity. No learning, no mutation of sources.
"""
from __future__ import annotations
import io, zipfile, json, hashlib
from contextlib import ExitStack
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data')
F395=BASE/'F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip'
FILES={'J2':BASE/'F401_R150W_J2_CHUNKED_REBUILD_COMPLETE_UNAPPROVED_20261031.zip','L2':BASE/'F401_R150W_L2_CHUNKED_REBUILD_COMPLETE_UNAPPROVED_20261031.zip','M2':BASE/'F401_R150W_M2_48D_CHUNKED_REBUILD_COMPLETE_UNAPPROVED_20261031.zip'}
P2=BASE/'F401_R150W_P2_Q2_FROZEN_EXPOSED_RESEARCH_UNAPPROVED_20261031.zip'
result={'classification':'ORIGINAL_IDENTITY_JOIN_ONLY_NOT_R150Q','cells':{},'summary':{'original':0,'correct':0,'opposite':0,'neutral':0,'valid_jlm':0,'proxy_q2_bad':0,'proxy_q2_good':0}}
with ExitStack() as stack:
    a=stack.enter_context(zipfile.ZipFile(F395));p=stack.enter_context(zipfile.ZipFile(P2))
    zips={k:stack.enter_context(zipfile.ZipFile(f)) for k,f in FILES.items()}
    for broker in ('coinexx','dukascopy'):
        for mon in ('01','02','06','07'):
            key=f'{broker}_{mon}'
            with np.load(io.BytesIO(a.read(f'F395_S14_{key}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as org:
                t=org['t'].copy(); side=org['side'].copy(); truth=org['truth'].copy(); order=org['original_index'].copy()
            assert np.array_equal(order,np.arange(len(order))) and np.isin(truth,(0,1,2)).all()
            valid=np.ones(len(t),bool)
            model_roots={}
            for fam,z in zips.items():
                with np.load(io.BytesIO(z.read(f'combined/R150W_{fam}_{key}_SCORES.npz'))) as ar:
                    assert np.array_equal(t,ar['t']) and np.array_equal(side,ar['side']),(key,fam)
                    valid &= ar['valid']
                    for k in ['guardian','opposite','neutral']:
                        sc=ar[k];assert sc.shape==(len(t),) and np.all(np.isfinite(sc))
                    model_roots[fam]=int(ar['valid'].sum())
            with np.load(io.BytesIO(p.read(f'results/masks/{key}_q2_jlm_SHADOW_MASK.npz'))) as ar:
                assert np.array_equal(order,ar['ordinal'])
                mask=ar['mask']
            assert (mask&~valid).sum()==0
            c={'n_original':len(t),'correct':int(np.sum(truth==0)),'opposite':int(np.sum(truth==1)),'neutral':int(np.sum(truth==2)),'valid_jlm':int(valid.sum()),'q2_not_q_bad':int(np.sum(mask&(truth!=0))),'q2_not_q_correct_lost':int(np.sum(mask&(truth==0))),
                'event_t_side_identity_sha256':hashlib.sha256(t.tobytes()+side.tobytes()+order.tobytes()).hexdigest(),'source_F395_truth_sha256':hashlib.sha256(truth.tobytes()).hexdigest(),'q2_proxy_mask_sha256':hashlib.sha256(np.packbits(mask).tobytes()).hexdigest(),'family_valid':model_roots}
            result['cells'][key]=c
            for target,source in [('original','n_original'),('correct','correct'),('opposite','opposite'),('neutral','neutral'),('valid_jlm','valid_jlm'),('proxy_q2_bad','q2_not_q_bad'),('proxy_q2_good','q2_not_q_correct_lost')]:result['summary'][target]+=c[source]
            print(key,c['n_original'],c['valid_jlm'],c['q2_not_q_bad'],c['q2_not_q_correct_lost'],flush=True)
assert result['summary']['original']==2574251 and result['summary']['correct']==1208071 and result['summary']['opposite']==1064545 and result['summary']['neutral']==301635
assert result['summary']['valid_jlm']==2334814
(BASE/'r150_stage2a_ccc/ORIGINAL_F395_J2_L2_M2_P2Q2_JOIN_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS original event+truth+score identity 8/8; R150Q NOT PRESENT; totals:',result['summary'])
