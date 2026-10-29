import io,zipfile,json,pathlib
import numpy as np
from r120_multiclock_geometry import ROOT,ORIG,PIN,load_source,build_states,sha256
from r120_htf_bridge import make_macro_native


def test_source_event_counts_and_causal_prefix():
 with zipfile.ZipFile(ORIG) as z:
  counts={'01':344037,'02':324582,'06':297035,'07':301280}
  for m,N in counts.items():
   v=np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz')))
   micro=np.load(ROOT/f'R120_{m}_MULTICLOCK_GEOMETRY.npy',mmap_mode='r')
   macro=np.load(ROOT/f'R120_{m}_COMPLETED_HTF_BRIDGE.npy',mmap_mode='r')
   a=np.load(ROOT/f'R120_{m}_UNSUPERVISED_PHASES.npy',mmap_mode='r')
   b=np.load(ROOT/f'R120_{m}_TENSOR_PHASES.npy',mmap_mode='r')
   assert N==len(v['t'])==micro.shape[0]==macro.shape[0]==len(a)==len(b)
   assert micro.shape[1]==92 and macro.shape[1]==36
   assert np.all(np.isfinite(micro)) and np.all(np.isfinite(macro))
   assert a.min()>=0 and a.max()<24 and b.min()>=0 and b.max()<288
   rec=json.loads((ROOT/f'R120_{m}_GEOMETRY_RECEIPT.json').read_text())
   htf=json.loads((ROOT/f'R120_{m}_HTF_RECEIPT.json').read_text())
   assert rec['feature_matrix_sha256']==sha256(ROOT/f'R120_{m}_MULTICLOCK_GEOMETRY.npy')
   assert htf['sha256']==sha256(ROOT/f'R120_{m}_COMPLETED_HTF_BRIDGE.npy')
   assert sum((v['truth']==c).sum() for c in [0,1,2])==N
  print('PASS 1,266,934 original event identity/feature matrices and 4-month SHA readback')

 # Nontrivial real January data, strict-prefix invariant for both micro and HTF features.
 d,orig=load_source('01');t=orig['t'][:80];s=orig['side'][:80]
 all_micro=build_states(*d,t,s)
 cut=t[-1]
 dpre=[a[:np.searchsorted(d[0],cut,side='left')] for a in d]
 pre_micro=build_states(*dpre,t,s)
 assert np.array_equal(all_micro,pre_micro)
 full_mac,_,_=make_macro_native(d[0],d[1],d[2],t,s)
 pre_mac,_,_=make_macro_native(dpre[0],dpre[1],dpre[2],t,s)
 assert np.array_equal(full_mac,pre_mac)
 print('PASS real 80-event prefix invariance for completed short/macro bars and session anchors')

if __name__=='__main__':test_source_event_counts_and_causal_prefix()