"""C2D3P lossless original Dukascopy quote index; no trading strategy.

Preserves original timestamp_ms_utc (int64), ask_raw (int32), bid_raw (int32)
from full-source-SHA-approved genuine compressed monthly Dukascopy CSV rows.
No candle, interpolation, midpoint replacement, reordering, tick dedupe or
missing-observation fabrication. The index allows next-quote O(1) resume.

The accepted policy consumes only ordered raw quote triples. Daily/weekly/month
labels on evaluation artifacts NEVER route an order or switch a mechanism.
"""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator
import numpy as np,pandas as pd
from v1_funded_core_033c import Quote
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch

DTYPE=np.dtype([('timestamp_ms_utc','<i8'),('ask_raw','<i4'),('bid_raw','<i4')])
MANIFEST='DAA033-lossless-DUKAS-BidAsk-true-quote-index-v1'
COLUMNS=('timestamp_ms_utc','ask_raw','bid_raw')

def digest_file(p):
    with Path(p).open('rb') as h:return hashlib.file_digest(h,'sha256').hexdigest()


def construct_canonical_index(original_gzip_path,binary_path,*,original_source_sha256,read_chunksize=250000):
    """Single causal read of ORIGINAL authenticated compressed raw source file."""
    gz=Path(original_gzip_path);dst=Path(binary_path)
    if read_chunksize<1:raise ValueError('Need finite chunk size')
    if digest_file(gz)!=original_source_sha256:raise ValueError('Original raw gz bytes changed')
    if dst.exists() or Path(str(dst)+'.json').exists():
        raise FileExistsError('Original indexed tape is immutable: choose unused name')
    dst.parent.mkdir(parents=True,exist_ok=True)
    tmp=dst.with_name(dst.name+'.part')
    count=0;first=None;last=-1
    try:
        with tmp.open('wb') as stream:
            for frame in pd.read_csv(gz,compression='gzip',usecols=list(COLUMNS),
                           dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'},chunksize=read_chunksize):
                if tuple(frame.columns)!=COLUMNS:
                    frame=frame.loc[:,COLUMNS]
                rows=np.empty(len(frame),dtype=DTYPE)
                for col in COLUMNS:rows[col]=frame[col].to_numpy()
                t=rows['timestamp_ms_utc'];a=rows['ask_raw'];b=rows['bid_raw']
                if len(rows)==0:continue
                if last>int(t[0]) or np.any(t[1:]<t[:-1]):
                    raise ValueError('Original quote chronology is not monotonic')
                if np.any(a<b) or np.any(b<=0):
                    raise ValueError('Original source contains non-executable quote')
                if first is None:first=int(t[0])
                last=int(t[-1]);count+=len(rows)
                rows.tofile(stream)
            stream.flush();os.fsync(stream.fileno())
        sha=digest_file(tmp)
        manifest={'schema':MANIFEST,'source_sha256':original_source_sha256,
              'source_rows':count,'first_time_ms':first,'last_time_ms':last,
              'index_sha256':sha,'index_bytes':tmp.stat().st_size,
              'dtype_fields':list(COLUMNS),'dtype_itemsize':DTYPE.itemsize,
              'original_gzip_file_name':gz.name,
              'input_sha_verified_before_index':True,
              'real_quote_order_unchanged':True,'month_as_execution_feature':False}
        if count==0 or tmp.stat().st_size!=count*DTYPE.itemsize:
            raise ValueError('Invalid index row count/size')
        mtemp=Path(str(dst)+'.json.part')
        with mtemp.open('w') as out:
            json.dump(manifest,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
        os.replace(tmp,dst)
        os.replace(mtemp,Path(str(dst)+'.json'))
        return manifest
    finally:
        if tmp.exists():tmp.unlink()


class VerifiedNativeQuoteTape:
    def __init__(self,binary_path,*,expected_original_source_sha256,expected_index_sha256=None):
        p=Path(binary_path)
        man=json.loads(Path(str(p)+'.json').read_text())
        if man.get('schema')!=MANIFEST or man.get('source_sha256')!=expected_original_source_sha256:
            raise ValueError('Original source provenance manifest mismatch')
        if expected_index_sha256 is not None and expected_index_sha256!=man['index_sha256']:
            raise ValueError('Frozen expected index digest mismatch')
        self.path=p
        self.manifest=man
        self.index_id=str(p.resolve())
        self._valid_digest=None
        self._last_validated_mtime=None

    def verify(self):
        p=self.path
        if not p.is_file() or p.stat().st_size!=self.manifest['index_bytes']:
            raise ValueError('Indexed original quote tape changed size')
        # Recheck digest before EVERY separately resumed chunk for source fidelity.
        actual=digest_file(p)
        if actual!=self.manifest['index_sha256']:
            raise ValueError('Indexed BidAsk quote SHA256 mismatch')
        return True

    def __len__(self):return int(self.manifest['source_rows'])

    def rows(self,start:int,count:int):
        self.verify()
        if start<0 or count<0 or start>len(self):raise ValueError('Invalid original quote offset')
        m=np.memmap(self.path,dtype=DTYPE,mode='r',shape=(len(self),))
        stop=min(len(self),start+count)
        for r in m[start:stop]:
            yield int(r['timestamp_ms_utc']),int(r['ask_raw']),int(r['bid_raw'])

    def feed_next(self,run:SegmentedRealQuoteResearch,*,max_new_quotes:int)->int:
        if max_new_quotes<=0:raise ValueError('Need bounded quote budget')
        key=self.index_id
        # Snapshot must also pin the exact external indexed-tape reader logic;
        # the core L7 runtime signature separately pins every engine operator.
        reader_key=key+'#reader_source_sha256'
        reader_hash=digest_file(__file__)
        prior_reader=run.verified_input_files.get(reader_key)
        if prior_reader is not None and prior_reader!=reader_hash:
            raise ValueError('Quote index reader source changed since checkpoint')
        prior=run.verified_input_files.get(key)
        if prior is not None and prior!=self.manifest['index_sha256']:
            raise ValueError('Cannot change original quote index mid-run')
        if run.previous_input_name and run.previous_input_name!=key and key in run.read_rows:
            raise ValueError('Cannot replay prior original indexed file after next one')
        next_ord=run.read_rows.get(key,0)
        consumed=0
        for row in self.rows(next_ord,max_new_quotes):
            run.on_quote(*row)
            consumed+=1
        run.verified_input_files[key]=self.manifest['index_sha256']
        run.verified_input_files[reader_key]=reader_hash
        run.read_rows[key]=next_ord+consumed
        run.previous_input_name=key
        return consumed
