"""Tests of lossless quote index, rehash and physical L7 source replay equivalence."""
import unittest,tempfile,gzip,csv,hashlib,json
from pathlib import Path
from original_verified_quote_tape_index_033 import (construct_canonical_index,VerifiedNativeQuoteTape,DTYPE)
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch

RULE=Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'

class GenuineQuoteIndexTests(unittest.TestCase):
    def original(self,d,name='part'):
        t=1770000000000//3600000*3600000
        rows=[]
        for h in range(20):
            for j in range(12):
                at=t+h*3600000+j*300000
                bid=100000+h*350+j*25
                rows.append((at,bid+35,bid))
        p=Path(d)/(name+'.csv.gz')
        with gzip.open(p,'wt',newline='') as f:
            w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'));w.writerows(rows)
        return p,rows,hashlib.sha256(p.read_bytes()).hexdigest()

    def test_row_count_exact_all_triples_true_times_and_duplicate_ms(self):
        with tempfile.TemporaryDirectory() as d:
            gz,values,sha=self.original(d)
            loc=Path(d)/'verified.bin'
            m=construct_canonical_index(gz,loc,original_source_sha256=sha,read_chunksize=17)
            self.assertEqual(m['source_rows'],len(values))
            self.assertEqual(m['index_bytes'],len(values)*DTYPE.itemsize)
            tape=VerifiedNativeQuoteTape(loc,expected_original_source_sha256=sha)
            self.assertEqual(list(tape.rows(0,len(values))),values)
            self.assertEqual(list(tape.rows(7,4)),values[7:11])
            with self.assertRaises(FileExistsError):
                construct_canonical_index(gz,loc,original_source_sha256=sha)

    def test_first_chunk_then_trusted_resume_matches_original_gzip(self):
        with tempfile.TemporaryDirectory() as d:
            gz,values,sha=self.original(d)
            idx=Path(d)/'immutable.bin'
            construct_canonical_index(gz,idx,original_source_sha256=sha,read_chunksize=21)
            tape=VerifiedNativeQuoteTape(idx,expected_original_source_sha256=sha)
            for mode in ('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'):
                with self.subTest(mode=mode):
                    reference=SegmentedRealQuoteResearch.start(mode,RULE)
                    reference.run_gzip_chunk(gz,expected_sha256=sha,max_new_quotes=len(values))
                    run=SegmentedRealQuoteResearch.start(mode,RULE)
                    self.assertEqual(tape.feed_next(run,max_new_quotes=95),95)
                    check=Path(d)/('restart-'+mode+'.json');run.save_local_trusted_checkpoint(check)
                    run=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(check,
                        expected_mode=mode,source_rules_path=RULE)
                    self.assertEqual(tape.feed_next(run,max_new_quotes=200),len(values)-95)
                    self.assertEqual(run.funded_diagnostics(),reference.funded_diagnostics())
                    self.assertEqual(run.engine.events,reference.engine.events)
                    self.assertEqual(tape.feed_next(run,max_new_quotes=1000),0)
                    self.assertEqual(run.feed.ordinal,len(values)-1)

    def test_manifest_and_actual_disk_binary_sha_tampering_detected(self):
        with tempfile.TemporaryDirectory() as d:
            gz,values,sha=self.original(d)
            idx=Path(d)/'immutable.bin';construct_canonical_index(gz,idx,original_source_sha256=sha)
            with self.assertRaises(ValueError):
                VerifiedNativeQuoteTape(idx,expected_original_source_sha256='f'*64)
            orig=idx.read_bytes();idx.write_bytes(orig[:100]+bytes([orig[100]^1])+orig[101:])
            t=VerifiedNativeQuoteTape(idx,expected_original_source_sha256=sha)
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):list(t.rows(0,1))
            idx.write_bytes(orig)
            self.assertEqual(list(t.rows(0,1)),values[:1])

    def test_changed_raw_file_fails_before_any_index_creation(self):
        with tempfile.TemporaryDirectory() as d:
            gz,values,sha=self.original(d)
            with self.assertRaisesRegex(ValueError,'Original raw gz bytes changed'):
                construct_canonical_index(gz,Path(d)/'no.bin',original_source_sha256='f'*64)
            self.assertFalse((Path(d)/'no.bin').exists())

    def test_no_out_of_order_or_negative_bid_raw_permitted(self):
        with tempfile.TemporaryDirectory() as d:
            for name,rows in (('order',[(2000,100,90),(1000,100,90)]),
                              ('crossed',[(2000,90,100),(3000,100,90)])):
                gz=Path(d)/(name+'.csv.gz')
                with gzip.open(gz,'wt',newline='') as f:
                    w=csv.writer(f);w.writerow(('timestamp_ms_utc','ask_raw','bid_raw'));w.writerows(rows)
                with self.assertRaises(ValueError):
                    construct_canonical_index(gz,Path(d)/(name+'.bin'),original_source_sha256=hashlib.sha256(gz.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()

class QuoteReaderCodePinTests(unittest.TestCase):
    def test_index_reader_hash_is_part_of_trusted_replay_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            gz,_,sha=GenuineQuoteIndexTests().original(d)
            idx=Path(d)/'immutable.bin';construct_canonical_index(gz,idx,original_source_sha256=sha)
            tape=VerifiedNativeQuoteTape(idx,expected_original_source_sha256=sha)
            run=SegmentedRealQuoteResearch.start('JAN039_SOURCE_NATIVE',RULE)
            tape.feed_next(run,max_new_quotes=13)
            self.assertEqual(len(run.verified_input_files[tape.index_id+'#reader_source_sha256']),64)
            checkpoint=Path(d)/'snapshot.json';run.save_local_trusted_checkpoint(checkpoint)
            resumed=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(checkpoint,
                             expected_mode='JAN039_SOURCE_NATIVE',source_rules_path=RULE)
            resumed.verified_input_files[tape.index_id+'#reader_source_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'reader source changed'):
                tape.feed_next(resumed,max_new_quotes=3)
