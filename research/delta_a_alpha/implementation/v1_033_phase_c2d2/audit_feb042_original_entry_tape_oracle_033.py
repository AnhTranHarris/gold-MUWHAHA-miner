"""All authentic E,S,D original source offers, streaming quote identity, no future P/L.

Read only FEB042 original source entry tuple E,S,D. Genuine observed quote Bid/Ask
from original Jan-tail + February. Never inspect X/R/P/H/C/O/N during replay.
"""
import hashlib, json, os, sys, time
from collections import Counter
from pathlib import Path
import zipfile
from io import BytesIO
import pandas as pd
import numpy as np
from original_jan037_feb041_entry_tape_oracle_033 import (OriginalSourceEntryTapeOracle,
    ARCHIVE_MEMBER, ORIGINAL_MEMBER_SHA256)
ROOT=Path(os.environ.get('DAA_RAW_SOURCE_ROOT','/mnt/data'))
ARCHIVE=Path(os.environ.get('DAA_FEB042_ARCHIVE','/mnt/data/feb_source_phase/FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip'))
OUT=Path(__file__).with_name('FEB042_ORIGINAL_ENTRY_ONLY_ORACLE_PARITY_033.json')
JAN=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
FEB=ROOT/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
SHAS=('d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d')

def raw(path,expected):
    with path.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=expected: raise ValueError(f'wrong original tick archive SHA: {path}')
    a=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
      dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    return [a[k].to_numpy() for k in ('timestamp_ms_utc','ask_raw','bid_raw')]

def main():
    before=time.time()
    oracle=OriginalSourceEntryTapeOracle.from_frozen_archive(ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as z: member=z.read(ARCHIVE_MEMBER)
    with np.load(BytesIO(member),allow_pickle=False) as d:
        # independent ONLY entry known tuple; do not materialize future X/P/H
        E=d['E'];S=d['S'];D=d['D']
    jt,ja,jb=raw(JAN,SHAS[0]);ft,fa,fb=raw(FEB,SHAS[1]);
    warm=3900880
    T=np.r_[jt[-warm:],ft];A=np.r_[ja[-warm:],fa];B=np.r_[jb[-warm:],fb]
    if len(T)!=11439219 or len(E)!=234698: raise AssertionError('Original upstream tape mismatch')
    sample_hash=hashlib.sha256();n=0;side=Counter();by_source=Counter();source_mismatch=0;all_keys=set();dupe_key=0
    # Advance only to actual source event quote indices; no skipped event permitted.
    for quote_idx in np.unique(E):
        qi=int(quote_idx)
        offers=oracle.on_observed_quote(qi,int(T[qi]),int(B[qi]),int(A[qi]))
        for obj in offers:
            bad=obj.quote_ordinal!=int(E[n]) or obj.source!=int(S[n]) or obj.side!=int(D[n]) or obj.offer_ordinal!=n
            source_mismatch+=int(bad)
            sample_hash.update(int(obj.quote_ordinal).to_bytes(8,'little',signed=True))
            sample_hash.update(int(obj.source).to_bytes(2,'little',signed=True))
            sample_hash.update(int(obj.side).to_bytes(1,'little',signed=True))
            by_source[obj.source]+=1;side[obj.side]+=1
            if obj.source_event_key in all_keys:dupe_key+=1
            all_keys.add(obj.source_event_key)
            n+=1
    oracle.assert_exhausted()
    ref=hashlib.sha256()
    for i in range(len(E)):
        ref.update(int(E[i]).to_bytes(8,'little',signed=True))
        ref.update(int(S[i]).to_bytes(2,'little',signed=True))
        ref.update(int(D[i]).to_bytes(1,'little',signed=True))
    report={'classification':'ORIGINAL_ENTRY_SOURCE_TAPE_RECONSTRUCTION_ONLY_NOT_GENERATOR_NOT_FUNDED',
      'authority':'Original FEB042/prepare.py and original FEB042_JAN039_PREPARED_PROPOSALS.npz, entry E/S/D only',
      'source_member_sha256':ORIGINAL_MEMBER_SHA256,'genuine_raw_shas':list(SHAS),
      'continuous_bidask_quotes':len(T),'jan_warmup_quotes':warm,'february_quotes':len(ft),
      'original_source_offers':len(E),'observed_source_offers':n,
      'unique_real_quote_ordinals':oracle.observed_unique_offer_quotes,
      'same_quote_additional_offers':oracle.same_tick_extra_count,
      'maximum_proposals_per_real_quote':oracle.max_offers_in_quote,
      'actual_source_id_direction_mismatches':source_mismatch,'duplicate_event_identity_keys':dupe_key,
      'full_original_ESD_digest':ref.hexdigest(),'online_reconstructed_ESD_digest':sample_hash.hexdigest(),
      'source_counts':{str(s):v for s,v in sorted(by_source.items())},'direction_counts':{str(s):v for s,v in sorted(side.items())},
      'no_calendar_month_branch_in_oracle':True,'deployable_month_blind_classifier':False,'funded_order_generation_enabled':False,
      'full_proposal_generator_source_available':False,
      'elapsed_seconds':round(time.time()-before,2)}
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if source_mismatch or dupe_key or sample_hash.digest()!=ref.digest():raise AssertionError('Original entry event mismatch')

if __name__=='__main__':main()
