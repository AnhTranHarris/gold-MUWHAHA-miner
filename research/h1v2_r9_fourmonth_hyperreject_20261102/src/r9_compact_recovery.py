"""Portable full decision-list recovery of every admitted R9 hyperreject signal.

Keep only rows above the LOWEST frozen research cutoff (up to 25% of every
month). ALL nine evaluated threshold decisions are exactly reconstructible;
not an unconditional future-exact oracle selection. Verify replay parity.
"""
from __future__ import annotations
import json,math,pathlib
import numpy as np
from r9_checkpoint_replay import BLOCK,chunk_path,_replay_ordinal_selected,OUT,R8,H1,sha,SYNTH

def compact(mode,month):
 full=json.loads((OUT/f'R9_{mode}_{month}_FULL_REPLAY.json').read_text())
 meta=json.loads((OUT/f'R9_{mode}_FIT.json').read_text())
 n=full['candidate_count'];block_count=math.ceil(n/BLOCK)
 threshold=min(meta['frozen_thresholds'].values())
 rows=[];scores=[];sides=[];hashes={}
 for i in range(block_count):
  p=chunk_path(mode,month,i)
  if sha(p)!=full['score_block_sha256'][str(i)]:raise ValueError('scored block hash changed')
  with np.load(p) as z:
   st=int(z['start']); sc=z['score']; side=z['side']
   selected=np.flatnonzero(sc>=threshold)
   rows.append((selected+st).astype(np.int32));scores.append(sc[selected]);sides.append(side[selected])
  hashes[str(i)]=sha(p)
 rr=np.concatenate(rows);ss=np.concatenate(scores);side=np.concatenate(sides)
 assert len(rr)==len(ss)==len(side) and (np.diff(rr)>0).all()
 teacher=H1/f'h1v2_dukascopy_{month}_oracle_labels.npz'
 receipt=json.loads((H1/f'h1v2_dukascopy_{month}_receipt.json').read_text())
 if sha(teacher)!=receipt['teacher_labels_sha256']:raise ValueError('original label archive SHA mismatch')
 with np.load(teacher) as z:
  ix=z['tick_index'].copy();cl=z['code'].copy();ex=z['exit_tick_index'].copy();net=z['net'].copy()
 for fraction,cut in meta['frozen_thresholds'].items():
  eligible=np.flatnonzero(ss>=cut);ri=rr[eligible];si=side[eligible]
  result=full['fractions'][fraction]
  if len(ri)!=result['candidate_count']:raise ValueError('count mismatch '+fraction)
  c=cl[ri,si]
  d,good,neutral,bad,unc,pnl=_replay_ordinal_selected(ri,si,ix,ex,net,cl)
  assert (d,good,neutral,bad,unc)==(result['nonoverlapping_count'],result['realized_strict_good'],result['realized_neutral'],result['realized_bad'],result['unscorable_source_boundary'])
  if round(pnl,2)!=result['research_modeled_net']:raise ValueError('net source parity mismatch')
 outfile=OUT/f'R9_{mode}_{month}_REPLAY_SELECTED_TOP25.npz'
 np.savez_compressed(outfile,row=rr,score=ss,side=side,lower_inclusion_cutoff=np.array(threshold),raw_eligible_count=np.array(n))
 receipt={'mode':mode,'month':month,'all_eligible_rows_scored':n,'preserved_ranked_rows':len(rr),
 'preserved_top_fraction':len(rr)/n,'full_month_replay_verified_all_thresholds':True,
 'replay_score_archive_sha256':sha(outfile),'score_block_sha256':hashes,
 'original_full_replay_sha256':sha(OUT/f'R9_{mode}_{month}_FULL_REPLAY.json'),
 'original_source_teacher':'H1V2 original 250ms candidate ordinal and quote-exact R9 exit matrices',
 'status':'RESEARCH_ONLY_MONTH_COMPLETE_IN_SAMPLE_OR_LOMO_AS_EXPLICIT'}
 (OUT/f'R9_{mode}_{month}_COMPACT_RECOVERY_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
 print('COMPACT VERIFIED',mode,month,len(rr),'/',n,'SHA',receipt['replay_score_archive_sha256'],flush=True)
 return receipt

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--mode',default='all4',choices=['all4','lomo07']);p.add_argument('--month',required=True)
 a=p.parse_args();compact(a.mode,a.month)
