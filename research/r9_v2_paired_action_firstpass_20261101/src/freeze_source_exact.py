#!/usr/bin/env python3
"""Create independently recoverable full-file binary checkpoints, SHA-256 manifests.
Never replaces or modifies original XAUUSD ticks, legacy R9/v2 code, or baseline ledgers.
"""
from __future__ import annotations
import zipfile,json,hashlib,datetime as dt,math
from pathlib import Path
ROOT=Path('/mnt/data/r9_v2_counterfactual_action_20261101')
OUT=ROOT/'checkpoints';OUT.mkdir(exist_ok=True)
BASELINE_ROOT='carson/r9-v2-hindsight-teacher-eight-source-training-20261101'

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def freeze():
    records=[]
    src_files=list(sorted((ROOT/'src').glob('*.py')))+list(sorted((ROOT/'tests').glob('*.py')))
    if (ROOT/'docs'/'CONTINUATION_FULL_RESEARCH_LOG.md').exists():src_files.append(ROOT/'docs'/'CONTINUATION_FULL_RESEARCH_LOG.md')
    if (ROOT/'README.md').exists():src_files.append(ROOT/'README.md')
    for source in ['coinexx','dukascopy']:
        for month in ['01','02','06','07']:
            names=[f'{source}_{month}_paired_counterfactual.npz',f'{source}_{month}_causal_asof.npz',
                   f'{source}_{month}_paired_receipt.json',f'{source}_{month}_features_receipt.json',
                   f'{source}_{month}_new_paired_action_student.txt',f'{source}_{month}_paired_action_student.json']
            files=[(ROOT/'results'/n,f'results/{n}') for n in names]+[(x,'source/'+x.relative_to(ROOT).as_posix()) for x in src_files]
            for file,arc in files:
                assert file.is_file(),file
            manifest={'source':source,'month':month,'archive_purpose':'COMPLETE_PAIRED_ACTION_EVENT_TEACHER_AND_STUDENT',
              'status':'NO_APPROVED_POLICY', 'lineage_base_branch':BASELINE_ROOT,
              'original_v2_source_unchanged':True,'full_calendar_source_month':True,
              'contains_only_this_source_month_labels':True,'files':{arc:{'bytes':f.stat().st_size,'sha256':sha(f)} for f,arc in files}}
            name=f'R9_V2_PAIRED_ACTION_{source.upper()}_2026_{month}_FULL_CHECKPOINT.zip'
            dest=OUT/name
            with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
                for f,arc in files:z.write(f,arc)
                z.writestr('SOURCE_EXACT_MANIFEST.json',json.dumps(manifest,indent=2))
            with zipfile.ZipFile(dest) as z:
                assert z.testzip() is None
                for arc,v in manifest['files'].items():assert hashlib.sha256(z.read(arc)).hexdigest()==v['sha256']
            receipts=json.loads((ROOT/'results'/f'{source}_{month}_paired_receipt.json').read_text())
            model=json.loads((ROOT/'results'/f'{source}_{month}_paired_action_student.json').read_text())
            records.append({'source':source,'month':month,'zip_name':name,'zip_bytes':dest.stat().st_size,'zip_sha256':sha(dest),
                            'source_tick_sha256':receipts['source_tick_sha256'],'original_event_count':receipts['baseline_entries'],
                            'exact_lifecycle_replay_mismatch':receipts['baseline_replay_discrepancies'],
                            'hindsight_either_action_good':receipts['any_side_strict_good_count'],
                            'heldout_selected':model['check_selected_nonoverlapping'],
                            'heldout_good_rate':model['check_survival'],
                            'heldout_net':model['check_net'],
                            'approved':False})
    index={'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'research_type':'CAUSAL_PAIRED_ACTION_FROZEN_BASELINE_EVENT_STUDENT',
      'source_months':8,'original_entry_events':sum(x['original_event_count'] for x in records),
      'total_pair_actions':2*sum(x['original_event_count'] for x in records),
      'all_exact_replays':all(x['exact_lifecycle_replay_mismatch']==0 for x in records),
      'any_approved':False,'records':records}
    (ROOT/'results'/'RECOVERY_INDEX.json').write_text(json.dumps(index,indent=2))
    return index
if __name__=='__main__':
    r=freeze();print(json.dumps({'source_months':r['source_months'],'original_entry_events':r['original_entry_events'],
                                 'total_pair_actions':r['total_pair_actions'],'all_exact_replays':r['all_exact_replays'],
                                 'checkpoint_bytes':[x['zip_bytes'] for x in r['records']]},indent=2))
