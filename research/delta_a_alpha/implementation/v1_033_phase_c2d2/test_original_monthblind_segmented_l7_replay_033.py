"""Replay determinism, source fidelity, held funds, protected archive inputs."""
import tempfile,unittest,gzip,csv,hashlib
from pathlib import Path
from dataclasses import replace
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch
from v1_funded_core_033c import Limits

P=Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'

class DeterministicRestartContracts(unittest.TestCase):
    def records(self):
        # A truly observed four-period source history, then exact NY heartbeat
        # state depends on prior quote history, not future arbitrary profits.
        t=1780000000000 //3600000*3600000
        out=[]
        for h in range(20):
            for j in range(9):
                ms=t+h*3600000+j*300000
                bid=100000+h*1000+j*100
                out.append((ms,bid+50,bid))
        return out

    def launch(self,mode):
        return SegmentedRealQuoteResearch.start(mode,P,funding=Limits(
            max_orders_per_second=10,max_orders_per_tick=1,max_spread_usd=1,
            max_open=64,max_same_direction=64,max_per_source_open=64))

    def test_save_resume_exactly_same_ledger_as_uninterrupted(self):
        for mode in ('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as d:
                src=self.records()
                uninterrupted=self.launch(mode)
                for x in src:uninterrupted.on_quote(*x)
                partial=self.launch(mode)
                for x in src[:80]:partial.on_quote(*x)
                check=Path(d)/'checkpoint.json'
                partial.save_local_trusted_checkpoint(check)
                copy=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(
                    check,expected_mode=mode,source_rules_path=P)
                for x in src[80:]:copy.on_quote(*x)
                self.assertEqual(copy.funded_diagnostics(),uninterrupted.funded_diagnostics())
                self.assertEqual(copy.engine.events,uninterrupted.engine.events)
                self.assertEqual(copy.feed.bridge.entry_context.observed_quotes,len(src))

    def test_archive_hash_guard_and_exact_gzip_resume(self):
        with tempfile.TemporaryDirectory() as d:
            data=self.records()
            file=Path(d)/'ticks.csv.gz'
            with gzip.open(file,'wt',newline='') as f:
                w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'))
                w.writerows(data)
            sha=hashlib.sha256(file.read_bytes()).hexdigest()
            a=self.launch('JAN039_SOURCE_NATIVE')
            with self.assertRaises(ValueError):a.run_gzip_chunk(file,expected_sha256='0'*64,max_new_quotes=30)
            self.assertEqual(a.total_quotes,0)
            self.assertEqual(a.run_gzip_chunk(file,expected_sha256=sha,max_new_quotes=61),61)
            path=Path(d)/'trusted-local-checkpoint.json'
            a.save_local_trusted_checkpoint(path)
            b=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(path,
                 expected_mode='JAN039_SOURCE_NATIVE',source_rules_path=P)
            self.assertEqual(b.run_gzip_chunk(file,expected_sha256=sha,max_new_quotes=77),77)
            self.assertEqual(b.run_gzip_chunk(file,expected_sha256=sha,max_new_quotes=10000),len(data)-138)
            c=self.launch('JAN039_SOURCE_NATIVE')
            for x in data:c.on_quote(*x)
            self.assertEqual(b.funded_diagnostics(),c.funded_diagnostics())
            self.assertEqual(b.read_rows[str(file.resolve())],len(data))

    def test_wrong_policy_or_rules_hash_never_restore(self):
        with tempfile.TemporaryDirectory() as d:
            x=self.launch('JAN039_SOURCE_NATIVE')
            x.on_quote(*self.records()[0])
            p=Path(d)/'trusted.json';x.save_local_trusted_checkpoint(p)
            with self.assertRaises(ValueError):
                SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(p,
                 expected_mode='FEB045_SOURCE_NATIVE',source_rules_path=P)
            with self.assertRaises(ValueError):
                SegmentedRealQuoteResearch.start('MODE_FROM_FUTURE_PROFIT',P)

    def test_reporting_day_week_month_never_routes_quotes(self):
        x=self.launch('JAN039_SOURCE_NATIVE')
        self.assertFalse(x.funded_diagnostics()['month_used_to_select_trades'])
        for row in self.records():x.on_quote(*row)
        self.assertEqual(x.total_quotes,len(self.records()))
        self.assertFalse(x.funded_diagnostics()['actual_broker_verified'])
        self.assertFalse(x.funded_diagnostics()['full_original_V1_economic_equivalence'])

    def test_l7_enforces_hard_original_one_tick_and_ten_per_sec(self):
        for mode in ('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    SegmentedRealQuoteResearch.start(mode,P,funding=Limits(max_orders_per_tick=2))
                with self.assertRaises(ValueError):
                    SegmentedRealQuoteResearch.start(mode,P,funding=Limits(max_orders_per_second=11))

if __name__=='__main__':unittest.main()

class PaidPositionCheckpointContracts(unittest.TestCase):
    def test_trusted_checkpoint_retains_actual_funded_positions_then_real_exit(self):
        from v1_funded_core_033c import Quote,Structure
        p=SegmentedRealQuoteResearch.start('JAN039_SOURCE_NATIVE',P,
            funding=Limits(max_orders_per_second=10,max_orders_per_tick=1,max_spread_usd=1))
        t=16*3600000
        for i,bid in enumerate((100000,101000)):
            q=Quote(t+i,bid+50,bid)
            s=Structure('NY',1,1,1,-1,q.time_ms-1,'ORIGINAL_JAN037_L3_SOURCE_HOUR_16',
                completed_bar_end_ms=(q.time_ms-1,)*4)
            p.feed.bridge.observe_raw_bidask(i,q,(1,1,1,-1))
            p.engine.process_quote(q,s)
        self.assertEqual(len(p.engine.positions),1)
        self.assertEqual(p.feed.bridge.physical_callbacks,1)
        with tempfile.TemporaryDirectory() as d:
            loc=Path(d)/'account_checkpoint.json'
            p.save_local_trusted_checkpoint(loc)
            restored=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(
                loc,expected_mode='JAN039_SOURCE_NATIVE',source_rules_path=P)
            self.assertEqual(set(restored.engine.positions),set(p.engine.positions))
            self.assertEqual(restored.feed.bridge.physical_callbacks,1)
            q=Quote(t+2000,137050,137000)
            for r in (p,restored):r.engine.process_quote(q,None)
            self.assertEqual(p.engine.events,restored.engine.events)
            self.assertEqual(p.engine.closed,restored.engine.closed)
            self.assertGreater(p.engine.closed[0].net_usd,35)
            self.assertEqual(len(restored.engine.positions),0)

class IntegrityGuardTests(unittest.TestCase):
    def test_original_gz_in_place_overwrite_is_rejected_after_first_chunk(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'quotes.csv.gz'
            with gzip.open(p,'wt',newline='') as f:
                w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'))
                w.writerows([(120000,100050,100000),(120001,100150,100100)])
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            run=SegmentedRealQuoteResearch.start('JAN039_SOURCE_NATIVE',P)
            self.assertEqual(run.run_gzip_chunk(p,expected_sha256=sha,max_new_quotes=1),1)
            with gzip.open(p,'wt',newline='') as f:
                w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'))
                w.writerows([(120000,100050,100000),(120001,999999,100100)])
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                run.run_gzip_chunk(p,expected_sha256=sha,max_new_quotes=1)
            self.assertEqual(run.total_quotes,1)

    def test_modified_checkpoint_payload_and_source_fingerprint_rejected(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            src=SegmentedRealQuoteResearch.start('JAN039_SOURCE_NATIVE',P)
            p=Path(d)/'snapshot.json';src.save_local_trusted_checkpoint(p)
            j=json.loads(p.read_text())
            j['runtime_code_SHA256']='0'*64;p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'Runtime source files differ'):
                SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(p,
                    expected_mode='JAN039_SOURCE_NATIVE',source_rules_path=P)
            src.save_local_trusted_checkpoint(p);j=json.loads(p.read_text())
            j['payload_base85']='XXX'+j['payload_base85'][3:];p.write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'Checkpoint corrupt'):
                SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(p,
                    expected_mode='JAN039_SOURCE_NATIVE',source_rules_path=P)

class SourceFileBoundaryTest(unittest.TestCase):
    def test_prior_quote_context_and_physical_account_survive_across_files(self):
        with tempfile.TemporaryDirectory() as d:
            loc=Path(d)
            allrows=DeterministicRestartContracts().records()
            a,b=allrows[:90],allrows[90:]
            sources=[]
            for n,part in (('prior',a),('next',b)):
                path=loc/(n+'.csv.gz')
                with gzip.open(path,'wt',newline='') as f:
                    w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'));w.writerows(part)
                sources.append((path,hashlib.sha256(path.read_bytes()).hexdigest(),len(part)))
            direct=SegmentedRealQuoteResearch.start('FEB045_SOURCE_NATIVE',P)
            for row in allrows:direct.on_quote(*row)
            staged=SegmentedRealQuoteResearch.start('FEB045_SOURCE_NATIVE',P)
            self.assertEqual(staged.run_gzip_chunk(sources[0][0],expected_sha256=sources[0][1],max_new_quotes=1000),90)
            check=loc/'local-trusted.json';staged.save_local_trusted_checkpoint(check)
            staged=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(check,
                expected_mode='FEB045_SOURCE_NATIVE',source_rules_path=P)
            self.assertEqual(staged.run_gzip_chunk(sources[1][0],expected_sha256=sources[1][1],max_new_quotes=1000),len(b))
            self.assertEqual(staged.total_quotes,len(allrows))
            self.assertEqual(staged.funded_diagnostics(),direct.funded_diagnostics())
            with self.assertRaises(ValueError):
                staged.run_gzip_chunk(sources[0][0],expected_sha256=sources[0][1],max_new_quotes=1)
