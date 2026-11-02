"""H1V2-R2 paired BUY/SELL extreme hindsight labels with hard negative taxonomy.

As-of quote geometry is immutable X. Future teacher outcomes are SEPARATE
arrays. Four classes for each action: WRONG=0, NEUTRAL=1, WEAK_GOOD=2,
STRONG_GOOD=3. Original R9 close and 30s strict good are prerequisites.
STRONG_GOOD adds <=3000ms first favorable, net>=0.10, spread<=1.00.
No element of the future label arrays is a runtime feature.
"""
import json,hashlib,math
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2/results');OUT=Path('/mnt/data/h1v2_r2/results')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}
CLASSES={'WRONG':0,'NEUTRAL':1,'WEAK_GOOD':2,'STRONG_GOOD':3}

def run():
 docs=[]
 for m in ('01','02','06','07'):
  with np.load(ROOT/f'h1v2_{m}_causal_geometry_atlas.npz',allow_pickle=False) as a:
   X=a['X'].copy();y=a['y'].copy();ix=a['ix'].copy();source_rows=a['original_row'].copy();ts=a['ts'].copy()
  with np.load(ROOT/f'h1v2_dukascopy_{m}_oracle_labels.npz',allow_pickle=False) as lab:
   assert np.array_equal(lab['tick_index'][source_rows],ix)
   assert np.array_equal(lab['t'][source_rows],ts)
   code=lab['code'][source_rows].copy();net=lab['net'][source_rows].copy();first=lab['first_event_ms'][source_rows].copy()
  assert np.array_equal(y,np.where(code[:,0]==1,1,np.where(code[:,1]==1,2,0)))
  spread=X[:,99]
  strong=(code==1)&(net>=.10)&(first>=0)&(first<=3000)&(spread[:,None]<=1.00+1e-5)
  klass=np.where(code==-1,0,np.where(code==0,1,np.where(strong,3,2))).astype(np.int8)
  assert np.all(~(strong[:,0]&strong[:,1]))
  name=OUT/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz'
  np.savez_compressed(name,X=X,ts=ts,ix=ix,original_row=source_rows,y_original=y,side_class=klass,first_ms=first,net=net,
      status=np.array(['TEACHER_FUTURE_LABELS_NOT_CAUSAL_FEATURES']))
  with name.open('rb') as fh:sha=hashlib.file_digest(fh,'sha256').hexdigest()
  count=np.bincount(klass.ravel(),minlength=4)
  docs.append({'month':m,'rows':len(y),'class_count_2side':{k:int(count[v]) for k,v in CLASSES.items()},
      'strong_buy':int(np.sum(strong[:,0])),'strong_sell':int(np.sum(strong[:,1])),
      'strong_per_15000':int(np.sum(strong)),'strong_rate':float(np.mean(strong.any(axis=1))),
      'sha256':sha,'artifact':name.name})
  print(m,docs[-1]['class_count_2side'],'strong_buy_sell',docs[-1]['strong_buy'],docs[-1]['strong_sell'],flush=True)
 report={'scope':'ACTION_SPECIFIC_HINDSIGHT_TEACHER_CLASSES_NOT_PREDICTIVE','classes':CLASSES,
    'exact_teacher':'original H1V2 bid/ask tick-ordinal first favorable before adverse + positive R9 close <=30s',
    'strong_extra':'favorable first hit <=3000ms AND R9 net>=0.10 AND entry_spread<=1.0',
    'months':docs,'safety':'NEVER include code/net/first_ms/side_class in features. y is teacher future only. No full-month strong oracle schedule computed here.'}
 (OUT/'H1V2_R2_HARD_NEGATIVE_TEACHER_RECEIPT.json').write_text(json.dumps(report,indent=2))
 return report
if __name__=='__main__':run()
