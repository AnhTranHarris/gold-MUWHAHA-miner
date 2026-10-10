"""Execute ACTUAL original Jan032 heartbeat generator against original JAN037 E/S/D research archive.

Original authority: JAN037 bundle research/jan037_expand_l3.py (actual 50ms original
call and S=src+10), full gamma02_campaign_heartbeat_019.py from 032_source.
No future X/R/P/H in runtime candidate generator; original archived ESD only oracle.
"""
import sys,time,hashlib,zipfile,io,json
from pathlib import Path
import numpy as np
BASE=Path('/mnt/data/c2d3l_work')
sys.path.insert(0,str(BASE/'032_source'))
import stmr_base as c
# The original JAN037/prepare_jan037.py explicitly bypasses synthetic source
# materialize in favor of executable genuine Dukascopy ask,bid arrays.
c.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import gamma02_m1_density as gmd
import gamma02_campaign_heartbeat_019 as hb
Z='/mnt/data/bootstrap_inputs/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip'
RAW='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
EXPECTED_RAW='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
P='research/JAN037_EXPANDED_L3_50MS_PROPOSALS.npz'
source_sha='3ddb58c2096cf33ffc092335cfae8bc3ee78d828901423f1466f3024593016d4'
expand_sha='e2c8869cbfdb287e8d1503a6db584a4da9cdb1e01762e62526cb88ec0b150ab0'

def main():
 start=time.time()
 for p,sha in [(BASE/'032_source/gamma02_campaign_heartbeat_019.py',source_sha),(BASE/'research/jan037_expand_l3.py',expand_sha)]:
  if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:raise AssertionError('Unaltered source sha '+str(p))
 with open(RAW,'rb') as f:
  if hashlib.file_digest(f,'sha256').hexdigest()!=EXPECTED_RAW:raise AssertionError('original Jan quote checksum')
 data=gmd.prep();t,a,b,mid,h4,h1,m15,m5=data[:8]
 print('source original quote arrays',len(t),'elapsed',round(time.time()-start,1),flush=True)
 # Exactly original Jan037 expansion: HB.heartbeat_candidates(...,50,4).
 idx,dr,src,hold,tp,sl=hb.heartbeat_candidates(t,mid,h4,h1,m15,m5,50,4)
 with zipfile.ZipFile(Z) as z:
  source=z.read(P)
 with np.load(io.BytesIO(source),allow_pickle=False) as x:
  E=x['E'];S=x['S'];D=x['D']
 # Jan037 jan037_expand_l3.py constructs original L3 src+10.
 sel=S>=17
 frozen=np.stack([E[sel],S[sel],D[sel].astype(np.int64)],axis=1)
 produced=np.stack([idx,src+10,dr.astype(np.int64)],axis=1)
 # Compare sorted occurrence multiset. Frozen source filtered by original terminal
 # outcome availability, so classify any discrepancy before designing a fix.
 order=np.lexsort((produced[:,2],produced[:,1],produced[:,0]));produced=produced[order]
 ord2=np.lexsort((frozen[:,2],frozen[:,1],frozen[:,0]));frozen=frozen[ord2]
 a=np.ascontiguousarray(produced);bb=np.ascontiguousarray(frozen)
 ka=a.view(np.dtype((np.void,a.dtype.itemsize*a.shape[1]))).ravel()
 kb=bb.view(np.dtype((np.void,bb.dtype.itemsize*bb.shape[1]))).ravel()
 common=np.intersect1d(ka,kb,assume_unique=False)
 print('generated',len(a),'archived',len(bb),'matching_unique',len(common),'elapsed',round(time.time()-start,1),flush=True)
 keys=[tuple(map(int,row)) for row in a];refkeys=[tuple(map(int,row)) for row in bb]
 from collections import Counter
 s1=Counter(keys);s2=Counter(refkeys)
 left=s1-s2;right=s2-s1
 extra=sum(left.values());missing=sum(right.values())
 print('GENERATED_NOT_IN_FROZEN',extra,'ARCHIVED_NOT_GENERATED',missing)
 print('first generated extra',list(left.items())[:7]);print('first archived missing',list(right.items())[:7]);print('source groups', {int(s):int((src==s).sum()) for s in np.unique(src)})
 report={'source':'Unmodified Jan032 gamma02_campaign_heartbeat_019.heartbeat_candidates + original jan037_expand_l3.py',
 'original_source_sha256':source_sha,'original_expand_script_sha256':expand_sha,
 'raw_january_sha256':EXPECTED_RAW,'source_member_sha256':hashlib.sha256(source).hexdigest(),
 'genuine_quotes':len(t),'original_period_ms':50,'group_code':4,
 'original_generated':len(a),'frozen_research_events':len(bb),
 'generated_not_frozen':extra,'frozen_not_generated':missing,
 'generated_first_extras':[(list(k),int(v)) for k,v in list(left.items())[:8]],
 'frozen_first_misses':[(list(k),int(v)) for k,v in list(right.items())[:8]],
 'source_counts_generated':{str(int(s+10)):int((src==s).sum()) for s in np.unique(src)},
 'claimed_exact_parity':extra==0 and missing==0,'full_native_funded_parity':False,
 'original_frozen_exit_fields_never_used_as_entry_features':True,'seconds':round(time.time()-start,2)}
 (BASE/'JAN037_ORIGINAL_HEARTBEAT_GENERATOR_PARITY.json').write_text(json.dumps(report,indent=2)+'\n')
 print('AUDIT',json.dumps(report,indent=2)[:1500])

if __name__=='__main__':main()
