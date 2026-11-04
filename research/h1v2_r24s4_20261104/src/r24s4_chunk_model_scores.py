"""Deliver byte-exact full R24S4 output when a single large score ZIP is unavailable.

All chunk identities and original P .npy SHA are in independent manifest; shard
concatenation reconstructs the ORIGINAL complete float32 source prediction file.
Never quantize, threshold, downsample or summarize source probabilities.
"""
from pathlib import Path
import hashlib,zipfile,json,sys
ROOT=Path('/mnt/data/h1v2_r24s4_entry_specialists')

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def run(source,mon,block=27_000_000):
 src=ROOT/'results'/source/mon;dest=ROOT/'archives';dest.mkdir(exist_ok=True)
 f=src/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy'
 n=f.stat().st_size;digest=sha(f);parts=[]
 with open(f,'rb') as read:
  k=0
  while True:
   piece=read.read(block)
   if not piece:break
   name=f'R24S4_{source}_{mon}_EXACT_FLOAT32_HAZARD_SCORE_BYTES_PART_{k:03d}.bin'
   p=dest/name;p.write_bytes(piece)
   parts.append({'name':name,'length':len(piece),'sha256':sha(p),'offset':k*block})
   k+=1
 assert sum(p['length'] for p in parts)==n
 small=dest/f'R24S4_{source}_{mon}_SMALL_CORE_MODELS_COMPLETE_CALENDARS_VERIFIER.zip'
 with zipfile.ZipFile(small,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f0 in sorted(src.iterdir()):
   if f0.name.endswith('_ALL_SELECTIONS_POSITIVE_AND_NEGATIVE.npz'):continue
   if f0.name.endswith('_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy'):continue
   if f0.is_file():z.write(f0,arcname=f0.name)
  for f0 in [ROOT/'src/r24s4_broker_hazard_specialist.py',ROOT/'src/r24s4_validate_and_archive_exact.py',ROOT/'src/r24s4_chunk_model_scores.py',ROOT/'src/run_r24s4_all_broker_months.sh',ROOT/'tests/test_r24s4_early_entry_contracts.py',ROOT/'R24S4_FAILURES_CORRECTIONS_APPEND_ONLY.txt']:
   z.write(f0,arcname='source_and_tests/'+f0.name)
 with zipfile.ZipFile(small) as z:
  assert z.testzip() is None
 manifest={'source':source,'month':mon,'format':'BYTE_EXACT_CONTIGUOUS_RAW_NPY_SHARDS','original_file_name':f.name,'original_size':n,'original_sha256':digest,'small_core_zip':{'name':small.name,'sha256':sha(small),'bytes':small.stat().st_size},'parts':parts,
 'reconstruct':'Concatenate .bin shards in ascending PART sequence to reproduce original exact .npy bytes; sha256 must equal original_sha256; do not alter float32 score precision','no_future_oracle_used_for_inference':True}
 out=dest/f'R24S4_{source}_{mon}_BYTE_EXACT_SCORE_SHARD_MANIFEST.json';out.write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'source':source,'month':mon,'small_core':manifest['small_core_zip'],'score_parts':len(parts),'original_prob_bytes':n,'digest':digest},indent=2))
 return manifest
if __name__=='__main__':run(sys.argv[1],sys.argv[2])
