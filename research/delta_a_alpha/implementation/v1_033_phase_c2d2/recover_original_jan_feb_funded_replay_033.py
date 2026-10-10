"""DAA033 C2D3R: crash-resilient autonomous supervisor of ORIGINAL L7 replay.

SOURCE AUTHORITY: run_original_jan_feb_indexed_funded_economics_033.py,
original_monthblind_segmented_l7_replay_033.py, and the original verified
JAN/FEB indexed bid/ask quotes. Never change a source policy, use a calendar
month to route it, or create fills from original frozen outcome ledgers.

Commands are idempotent: --status never unpickles, --step runs one bounded child
in a separate process, --loop repeats bounded children outside the chat UI,
and --verify independently audits both completed physically funded ledgers.
The existing trusted-local checkpoint owns transaction recovery. Never open a
checkpoint downloaded from strangers: underlying legacy engine uses pickle.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from run_original_jan_feb_indexed_funded_economics_033 import FILES
from audit_full_jan_feb_native_source_funded_033 import audit

MODES=('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE')
TOTAL=sum(v['quotes'] for v in FILES.values())
HERE=Path(__file__).resolve().parent
DEFAULT_WORK=Path('/mnt/data/c2d3q_work/full')
DEFAULT_INDEX=Path('/mnt/data/c2d3p_work/data')
DEFAULT_RULES=Path('/mnt/data/c2d3p_work/repo/verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json')
DEFAULT_RESULT=Path('/mnt/data/c2d3q_work/JAN_FEB_16673401_FULL_FUNDED_NATIVE_AB_SOURCE_ECONOMICS_033.json')
# Original complete research-account checkpoints and independently reconciled
# ledger, pinned BEFORE ever loading an exported/restored pickle into Python.
# This does NOT authenticate arbitrary partial / externally supplied snapshots.
PINNED_COMPLETE_CHECKPOINTS={
 'JAN039_SOURCE_NATIVE':'49e8bbd2002de3accc8a0afc9c09a249e52a0e3f67e961ccef9ce9870c121ad6',
 'FEB045_SOURCE_NATIVE':'4e84faa44cef1b46c3e7e3785ec830ff55d20622513ddd6c9a35a47b697b2d97'}
PINNED_COMPLETE_RESULT='71fc6a164b6d3d0c194f925a5afd5a7cc8bf812968f823999083176ffc325730'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def verify_pinned_final_export_files(workdir):
    """Prove restored Library FINAL checkpoints have exact original local bytes.

    Must be called before deserializing previously exported complete snapshots.
    This is a safe SHA check, not a license to unpickle any other Library file.
    """
    for mode,digest in PINNED_COMPLETE_CHECKPOINTS.items():
        p=Path(workdir)/(mode+'.trusted-private-checkpoint.json')
        if not p.is_file() or sha(p)!=digest:
            raise ValueError('Completed research ledger checkpoint differs from pinned accepted source: '+mode)
    return True


def status_mode(workdir,mode):
    if mode not in MODES: raise ValueError('Unapproved source-policy mode')
    root=Path(workdir)
    progress=root/(mode+'.progress.json')
    ckpt=root/(mode+'.trusted-private-checkpoint.json')
    if not progress.exists():
        if ckpt.exists():
            return {'mode':mode,'status':'CHECKPOINT_ONLY_RECOVERABLE','reported_quotes':None,
                    'checkpoint_exists':True,'complete':False}
        return {'mode':mode,'status':'NOT_STARTED','reported_quotes':0,
                'checkpoint_exists':False,'complete':False}
    d=json.loads(progress.read_text())
    if d.get('source_mode_selected_before_ingest')!=mode or d.get('march_data_read') is not False or d.get('live_month_switching') is not False:
        raise ValueError('Invalid or month-contaminated progress source')
    positions=d.get('read_positions',{})
    if set(positions)!={'JAN','FEB'}:raise ValueError('Missing original source quote ordinal')
    for k,v in FILES.items():
        if not isinstance(positions[k],int) or not 0<=positions[k]<=v['quotes']:
            raise ValueError('Original quote position out of bounds')
    seen=sum(positions.values())
    if d.get('all_quotes_processed')!=seen:raise ValueError('Partial source ledger counter disagreement')
    if seen>0 and not ckpt.exists():raise ValueError('Source progress exists but trusted checkpoint is missing')
    claimed_complete=seen==TOTAL
    return {'mode':mode,'status':'COMPLETE_CLAIM_REQUIRES_AUDIT' if claimed_complete else 'PARTIAL',
            'reported_quotes':seen,'january_quotes':positions['JAN'],'february_quotes':positions['FEB'],
            'checkpoint_exists':ckpt.exists(),'complete':claimed_complete,
            'source_offers_reported':d.get('original_native_source_proposals'),
            'funded_deals_reported':d.get('actually_closed_deals')}


def atomic_json(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.part')
    with tmp.open('w') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


@contextmanager
def exclusive_mode(workdir,mode):
    """Kernel-managed advisory lock, released even on process termination.

    Linux/macOS uses flock, Windows uses msvcrt.locking. Never delete a live
    lockfile: removing lockfiles breaks inode-based mutual exclusion.
    """
    p=Path(workdir);p.mkdir(parents=True,exist_ok=True)
    f=(p/(mode+'.replay.lock')).open('a+b')
    try:
        if os.name=='nt':
            import msvcrt
            f.seek(0);f.write(b'1');f.flush();f.seek(0)
            try:msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            except OSError as e:raise RuntimeError('Another replay worker holds this source mode') from e
        else:
            import fcntl
            try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as e:raise RuntimeError('Another replay worker holds this source mode') from e
        yield
    finally:
        if os.name=='nt':
            try:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            except (OSError,UnboundLocalError):pass
        else:
            import fcntl
            fcntl.flock(f.fileno(),fcntl.LOCK_UN)
        f.close()


def reconcile_progress_from_trusted_local_checkpoint(workdir,mode,source_dir,rules):
    """Recover when child crashed AFTER checkpoint but BEFORE progress JSON.

    Only the original locally generated snapshot may be loaded. The existing
    loader authenticates original JAN038 rules, all source-code SHA fingerprints,
    compressed payload integrity, expected policy, and decoded account type.
    Never use this helper on uploaded or downloaded checkpoints.
    """
    ckpt=Path(workdir)/(mode+'.trusted-private-checkpoint.json')
    if not ckpt.exists():return status_mode(workdir,mode)
    from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch
    run=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(
        ckpt,expected_mode=mode,source_rules_path=rules)
    root=Path(source_dir)
    pos={name:run.read_rows.get(str((root/f['name']).resolve()),0)
         for name,f in FILES.items()}
    if (any(not isinstance(pos[k],int) or not 0<=pos[k]<=FILES[k]['quotes']
            for k in FILES) or sum(pos.values())!=run.total_quotes):
        raise ValueError('Trusted checkpoint quote ordinals contradict source tape')
    progress=Path(workdir)/(mode+'.progress.json')
    old=None
    if progress.exists():
        try:old=status_mode(workdir,mode)
        except (ValueError,KeyError,json.JSONDecodeError):old=None
    if old and old['reported_quotes']==run.total_quotes and all(
       old[{'JAN':'january_quotes','FEB':'february_quotes'}[k]]==pos[k] for k in FILES):
        return old
    if old and old['reported_quotes'] is not None and old['reported_quotes']>run.total_quotes:
        raise ValueError('Progress file claims future quotes beyond authenticated checkpoint')
    snap={'schema':'DAA033-C2D3Q-monthblind-real-source-funded-economics-progress-v1',
         'source_mode_selected_before_ingest':mode,'all_quotes_processed':run.total_quotes,
         'original_native_source_proposals':run.feed.bridge.source_events,
         'paid_source_entries':run.feed.bridge.physical_callbacks,
         'actually_closed_deals':len(run.engine.closed),
         'score_from_only_funded_account':run.engine.score(),
         'read_positions':pos,
         'last_index_month_source':'FEB' if pos['FEB'] else 'JAN',
         'last_quote_epoch_ms':(run.engine._last_quote.time_ms
                               if run.engine._last_quote else None),
         'source_jan_feb_sha256':{k:{'raw':v['raw'],'binary':v['binary']}
                                       for k,v in FILES.items()},
         'march_data_read':False,'live_month_switching':False,
         'is_original_full_eight_layer_V1_certified':False,
         'model':'IDEALIZED_BIDASK_SOURCE_ONLY_L3_WITH_FUNDED_L7_OTHER_OPTIMIZED_SOURCE_ROLES_INCOMPLETE'}
    atomic_json(progress,snap)
    return status_mode(workdir,mode)

def one_step(mode,*,workdir,source_dir,rules,quote_budget=25000,time_budget=12.0):
    """One independently restartable CHILD invocation, never a long chat call."""
    if mode not in MODES:raise ValueError('Unknown source mode')
    if not 1<=quote_budget<=50000:raise ValueError('Use 1..50000 genuine quotes per bounded child')
    if not 2<=time_budget<=20:raise ValueError('Use a two-to-twenty-second hard child timeout')
    with exclusive_mode(workdir,mode):
        claimed=status_mode(workdir,mode)
        if claimed['complete']:
            expected=PINNED_COMPLETE_CHECKPOINTS[mode]
            p=Path(workdir)/(mode+'.trusted-private-checkpoint.json')
            if sha(p)!=expected:
                raise ValueError('Completed source-funded checkpoint changed: refuse untrusted pickle')
        before=reconcile_progress_from_trusted_local_checkpoint(workdir,mode,source_dir,rules)
        if before['complete']:
            return {'mode':mode,'outcome':'ALREADY_COMPLETE_NO_REPLAY','before':before,'after':before}
        driver=HERE/'run_original_jan_feb_indexed_funded_economics_033.py'
        if not driver.is_file():raise FileNotFoundError('Required original runner absent')
        cmd=[sys.executable,str(driver),'--mode',mode,'--work-dir',str(workdir),
             '--source-dir',str(source_dir),'--rules',str(rules),
             '--max-new-quotes',str(quote_budget),'--chunk',str(min(quote_budget,10000))]
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=time_budget,check=False)
            outcome='COMMITTED_CHILD' if p.returncode==0 else 'FAILED_CHILD_CHECK_SNAPSHOT'
            error=p.stderr[-2000:] if p.returncode else ''
        except subprocess.TimeoutExpired:
            outcome='CHILD_TIMEOUT_RECOVER_LAST_ATOMIC_SNAPSHOT';error='Timeout killed child. Previous atomic checkpoint remains the only trusted resume boundary.'
        after=reconcile_progress_from_trusted_local_checkpoint(workdir,mode,source_dir,rules)
        if outcome=='COMMITTED_CHILD' and (after['reported_quotes'] or 0)==(before['reported_quotes'] or 0):
            outcome='NO_NEW_COMMITTED_QUOTES_REFUSE_INFINITE_RETRY'
            error='Child exited without advancing authenticated source; inspect original driver and checkpoint'
        receipt={'mode':mode,'outcome':outcome,'before':before,'after':after,
                 'quotes_in_committed_progress':(after['reported_quotes'] or 0)-(before['reported_quotes'] or 0),
                 'child_time_budget_seconds':time_budget,'error':error}
        atomic_json(Path(workdir)/(mode+'.last_child_receipt.json'),receipt)
        return receipt


def verify_completed(*,workdir,source_dir,rules,result_path):
    """No re-trading; load only trusted local completed snapshots and audit EVERY close."""
    status={m:status_mode(workdir,m) for m in MODES}
    if not all(v['complete'] for v in status.values()):
        raise ValueError('Both original-source policies must consume all 16,673,401 quotes first')
    verify_pinned_final_export_files(workdir)
    result=audit(workdir,source_dir,rules)
    expected=Path(result_path)
    if expected.exists():
        preserved=json.loads(expected.read_text())
        if preserved!=result:raise ValueError('Completed economic ledger differs from saved source-native truth: DO NOT OVERWRITE')
    else:
        atomic_json(expected,result)
    if sha(expected)!=PINNED_COMPLETE_RESULT:
        raise ValueError('Funded audit result JSON digest differs from pinned source-grade complete ledger')
    receipt={'schema':'DAA033-C2D3R-verified-complete-source-native-paid-ledgers',
             'truth_artifact_sha256':sha(expected),'full_true_bidask_quotes':TOTAL,
             'modes':{k:{'trades':v['physically_closed_deals'],'realized_net':v['realized_account_score']['net'],
                         'quote_equity_dd':v['realized_account_score']['max_equity_dd'],
                         'checkpoint_sha256':v['checkpoint_file_sha256']}
                      for k,v in result['run_modes'].items()},
             'march_opened':False,'full_original_V1_optimized_parity':False,
             'executed_original_decision_month_switch':False}
    atomic_json(Path(workdir)/'C2D3R_VERIFIED_COMPLETE.json',receipt)
    return receipt


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['status','step','loop','verify'])
    p.add_argument('--mode',choices=MODES,default='JAN039_SOURCE_NATIVE')
    p.add_argument('--work-dir',type=Path,default=DEFAULT_WORK)
    p.add_argument('--source-dir',type=Path,default=DEFAULT_INDEX)
    p.add_argument('--rules',type=Path,default=DEFAULT_RULES)
    p.add_argument('--result',type=Path,default=DEFAULT_RESULT)
    p.add_argument('--quote-budget',type=int,default=25000)
    p.add_argument('--child-seconds',type=float,default=12.0)
    p.add_argument('--max-steps',type=int,default=0,help='0 loops to completion OUTSIDE chat; each step bounded')
    args=p.parse_args(argv)
    if args.command=='status':
        output={m:status_mode(args.work_dir,m) for m in MODES}
    elif args.command=='verify':
        output=verify_completed(workdir=args.work_dir,source_dir=args.source_dir,rules=args.rules,result_path=args.result)
    elif args.command=='step':
        output=one_step(args.mode,workdir=args.work_dir,source_dir=args.source_dir,rules=args.rules,
                        quote_budget=args.quote_budget,time_budget=args.child_seconds)
    else:
        steps=0;output={}
        for mode in MODES:
            while not status_mode(args.work_dir,mode)['complete']:
                if args.max_steps and steps>=args.max_steps:
                    print(json.dumps({'status':'BOUNDED_LOOP_PAUSED','steps':steps,'resume_command':'loop'}));return 0
                r=one_step(mode,workdir=args.work_dir,source_dir=args.source_dir,rules=args.rules,
                           quote_budget=args.quote_budget,time_budget=args.child_seconds)
                steps+=1
                if r['outcome'] not in ('ALREADY_COMPLETE_NO_REPLAY','COMMITTED_CHILD','CHILD_TIMEOUT_RECOVER_LAST_ATOMIC_SNAPSHOT'):
                    raise RuntimeError('Worker failed; no changes to source policy. '+r['error'])
                print(json.dumps({'step':steps,'mode':mode,'outcome':r['outcome'],'read_quotes':r['after']['reported_quotes']}),flush=True)
        output=verify_completed(workdir=args.work_dir,source_dir=args.source_dir,rules=args.rules,result_path=args.result)
    print(json.dumps(output,sort_keys=True))
    return 0

if __name__=='__main__':sys.exit(main())
