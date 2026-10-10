"""Executable timeout/crash-resume safety contract around original complete source replay."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from recover_original_jan_feb_funded_replay_033 import (
    MODES,TOTAL,FILES,atomic_json,exclusive_mode,one_step,status_mode,verify_completed
)


def progress(root,mode,jan=0,feb=0,march=False,real_mode=None):
    d={'source_mode_selected_before_ingest':real_mode or mode,
       'all_quotes_processed':jan+feb,'read_positions':{'JAN':jan,'FEB':feb},
       'march_data_read':march,'live_month_switching':False,
       'original_native_source_proposals':0,'actually_closed_deals':0}
    atomic_json(root/(mode+'.progress.json'),d)
    (root/(mode+'.trusted-private-checkpoint.json')).write_text('TEST FIXTURE. NEVER UNPICKLE THIS FILE.')


class FaultRecoveryContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dir=Path(self.tmp.name)
        self.mode=MODES[0]
        # Ordinary unit fixtures are intentionally NOT real trusted pickle files.
        # Reconcile is tested separately with an authenticated-loader mock.
        self.reconcile_patch=patch('recover_original_jan_feb_funded_replay_033.reconcile_progress_from_trusted_local_checkpoint',
                                   side_effect=lambda workdir,mode,source_dir,rules:status_mode(workdir,mode))
        self.reconcile_patch.start()
    def tearDown(self):
        self.reconcile_patch.stop()
        self.tmp.cleanup()

    def test_missing_checkpoint_fails_closed(self):
        progress(self.dir,self.mode,jan=4)
        (self.dir/(self.mode+'.trusted-private-checkpoint.json')).unlink()
        with self.assertRaisesRegex(ValueError,'missing'): status_mode(self.dir,self.mode)

    def test_unstarted_is_not_claimed_complete(self):
        s=status_mode(self.dir,self.mode)
        self.assertFalse(s['complete'])
        self.assertEqual(s['reported_quotes'],0)

    def test_partial_source_ordinal_is_verified(self):
        progress(self.dir,self.mode,jan=700,feb=23)
        s=status_mode(self.dir,self.mode)
        self.assertEqual(s['reported_quotes'],723)
        self.assertEqual(s['february_quotes'],23)
        self.assertFalse(s['complete'])

    def test_forged_overflow_and_total_rejected(self):
        progress(self.dir,self.mode,jan=FILES['JAN']['quotes']+1)
        with self.assertRaises(ValueError):status_mode(self.dir,self.mode)
        progress(self.dir,self.mode,jan=5)
        d=json.loads((self.dir/(self.mode+'.progress.json')).read_text())
        d['all_quotes_processed']+=1
        atomic_json(self.dir/(self.mode+'.progress.json'),d)
        with self.assertRaises(ValueError):status_mode(self.dir,self.mode)

    def test_changed_mode_or_march_contamination_rejected(self):
        progress(self.dir,self.mode,real_mode=MODES[1])
        with self.assertRaises(ValueError):status_mode(self.dir,self.mode)
        progress(self.dir,self.mode,march=True)
        with self.assertRaises(ValueError):status_mode(self.dir,self.mode)

    def test_completed_run_cannot_process_same_16673401_quotes_twice(self):
        progress(self.dir,self.mode,jan=FILES['JAN']['quotes'],feb=FILES['FEB']['quotes'])
        with patch('recover_original_jan_feb_funded_replay_033.subprocess.run',side_effect=AssertionError('Must not run')):
            receipt=one_step(self.mode,workdir=self.dir,source_dir=self.dir,rules=self.dir/'dummy',quote_budget=10,time_budget=2)
        self.assertEqual(receipt['outcome'],'ALREADY_COMPLETE_NO_REPLAY')
        self.assertEqual(receipt['after']['reported_quotes'],TOTAL)

    def test_bounded_child_saves_only_committed_progress(self):
        progress(self.dir,self.mode,jan=13)
        def child(*a,**kw):
            self.assertEqual(kw['timeout'],3)
            progress(self.dir,self.mode,jan=20)
            return SimpleNamespace(returncode=0,stdout='ok',stderr='')
        with patch('recover_original_jan_feb_funded_replay_033.subprocess.run',side_effect=child):
            out=one_step(self.mode,workdir=self.dir,source_dir=self.dir,rules=self.dir/'dummy',quote_budget=10,time_budget=3)
        self.assertEqual(out['outcome'],'COMMITTED_CHILD')
        self.assertEqual(out['quotes_in_committed_progress'],7)
        self.assertEqual(json.loads((self.dir/(self.mode+'.last_child_receipt.json')).read_text())['after']['reported_quotes'],20)

    def test_timeout_does_not_advance_or_destroy_trusted_checkpoint(self):
        progress(self.dir,self.mode,jan=500)
        snapshot=(self.dir/(self.mode+'.trusted-private-checkpoint.json')).read_bytes()
        with patch('recover_original_jan_feb_funded_replay_033.subprocess.run',side_effect=subprocess.TimeoutExpired(cmd='quoted-original',timeout=3)):
            out=one_step(self.mode,workdir=self.dir,source_dir=self.dir,rules=self.dir/'dummy',quote_budget=10,time_budget=3)
        self.assertEqual(out['outcome'],'CHILD_TIMEOUT_RECOVER_LAST_ATOMIC_SNAPSHOT')
        self.assertEqual(out['after']['reported_quotes'],500)
        self.assertEqual((self.dir/(self.mode+'.trusted-private-checkpoint.json')).read_bytes(),snapshot)

    def test_recover_checkpoint_newer_than_stale_progress(self):
        self.reconcile_patch.stop()
        try:
            progress(self.dir,self.mode,jan=9)
            root=self.dir
            fake=SimpleNamespace(read_rows={str((root/v['name']).resolve()):(15 if k=='JAN' else 0)
                                                  for k,v in FILES.items()},
                 total_quotes=15,feed=SimpleNamespace(bridge=SimpleNamespace(source_events=3,physical_callbacks=1)),
                 engine=SimpleNamespace(closed=[],_last_quote=SimpleNamespace(time_ms=145),score=lambda:{'net':0}))
            with patch('original_monthblind_segmented_l7_replay_033.SegmentedRealQuoteResearch.resume_local_trusted_checkpoint',return_value=fake):
                from recover_original_jan_feb_funded_replay_033 import reconcile_progress_from_trusted_local_checkpoint
                s=reconcile_progress_from_trusted_local_checkpoint(root,self.mode,root,root/'rules')
            self.assertEqual(s['reported_quotes'],15)
            self.assertEqual(s['source_offers_reported'],3)
        finally:
            self.reconcile_patch.start()

    def test_disallow_unbounded_single_child(self):
        with self.assertRaises(ValueError):one_step(self.mode,workdir=self.dir,source_dir=self.dir,rules='',quote_budget=999999,time_budget=3)
        with self.assertRaises(ValueError):one_step(self.mode,workdir=self.dir,source_dir=self.dir,rules='',quote_budget=10,time_budget=99)

    def test_locks_reject_parallel_same_source_worker(self):
        with exclusive_mode(self.dir,self.mode):
            with self.assertRaises(RuntimeError):
                with exclusive_mode(self.dir,self.mode):pass

    def test_partial_run_cannot_be_stamped_verified(self):
        progress(self.dir,self.mode,jan=100)
        with self.assertRaisesRegex(ValueError,'Both original-source policies'):
            verify_completed(workdir=self.dir,source_dir=self.dir,rules=self.dir/'dummy',result_path=self.dir/'result.json')

    def test_completed_audit_is_not_allowed_to_change_saved_truth(self):
        for mode in MODES:progress(self.dir,mode,jan=FILES['JAN']['quotes'],feb=FILES['FEB']['quotes'])
        path=self.dir/'result.json'
        atomic_json(path,{'fixed_original_results':'ORIGINAL'})
        with patch('recover_original_jan_feb_funded_replay_033.audit',return_value={'different':'ATTEMPT'}):
            with self.assertRaisesRegex(ValueError,'DO NOT OVERWRITE'):
                verify_completed(workdir=self.dir,source_dir=self.dir,rules=self.dir/'dummy',result_path=path)
        self.assertEqual(json.loads(path.read_text()),{'fixed_original_results':'ORIGINAL'})


if __name__=='__main__':unittest.main()
