"""Original JAN/FEB FULL index SHAs and native funded replay 50k raw quote crosscheck.

No March file access; no source future exit result arrays, no use of months as
strategy features. Full month source quote index creation is infrastructure,
NOT completion of original optimized V1 economic parity.
"""
import json,time,tempfile
from pathlib import Path
import numpy as np
from original_verified_quote_tape_index_033 import VerifiedNativeQuoteTape
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch

ROOT=Path('/mnt/data');PARENT=Path(__file__).parent
RULE=PARENT/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'
CONF={
 '01':('d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
      'e45f40c120fa235c4a25b56f87714318015579c3afb2b671e3f66f487796337c',9135062),
 '02':('ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
      '25cdc90b9ef72fa4cb7fc5022e36d8c3c0d58e2bc955de1319768106080007e9',7538339)
}

def main():
    all_checks=[];start=time.monotonic()
    for month,(source_sha,index_sha,source_count) in CONF.items():
        dname='JAN' if month=='01' else 'FEB'
        bin=ROOT/f'c2d3p_work/data/ORIGINAL_{dname}2026_TRUE_BIDASK_QUOTE_INDEX.bin'
        gz=ROOT/f'XAUUSD_DUKAS_2026_{month}_ticks.csv(3).gz'
        tape=VerifiedNativeQuoteTape(bin,expected_original_source_sha256=source_sha,
                                         expected_index_sha256=index_sha)
        assert tape.verify() and len(tape)==source_count
        for mode in ('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'):
            original=SegmentedRealQuoteResearch.start(mode,RULE)
            assert original.run_gzip_chunk(gz,expected_sha256=source_sha,max_new_quotes=50000)==50000
            indexed=SegmentedRealQuoteResearch.start(mode,RULE)
            assert tape.feed_next(indexed,max_new_quotes=25000)==25000
            with tempfile.TemporaryDirectory() as temp:
                snapshot=Path(temp)/'checkpoint.json'
                indexed.save_local_trusted_checkpoint(snapshot)
                indexed=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(snapshot,
                    expected_mode=mode,source_rules_path=RULE)
                assert tape.feed_next(indexed,max_new_quotes=25000)==25000
            assert indexed.funded_diagnostics()==original.funded_diagnostics()
            assert indexed.engine.events==original.engine.events
            assert indexed.feed.ordinal==original.feed.ordinal
            all_checks.append({'original_source':month,'source_frozen_gzip_sha256':source_sha,
                'exact_lossless_binary_sha256':index_sha,'source_month_quotes':source_count,
                'actual_quote_sample_first_50000':50000,'source_policy_chosen_before_replay':mode,
                'original_gzip_vs_exact_index_physical_account_match':True,
                'source_entries':indexed.feed.bridge.source_events,
                'paid_entries':indexed.feed.bridge.physical_callbacks,
                'funded_score':indexed.engine.score(),
                'checkpoint_midway':25000,'actual_broker_certified':False,
                'full_optimized_jan_feb_month_economics_certified':False})
            print(json.dumps({'month_source':month,'mode':mode,'true_quotes':50000,
                    'original_source_events':indexed.feed.bridge.source_events,
                    'paid_entries':indexed.feed.bridge.physical_callbacks,
                    'fully_match_after_checkpoint':True,'seconds':round(time.monotonic()-start,2)}),flush=True)
    dest=PARENT/'ORIGINAL_JAN_FEB_FULL_LOSSLESS_INDEX_AND_50K_NATIVE_L7_PARITY.json'
    dest.write_text(json.dumps({'quote_checks':all_checks,
          'strict_note':'full January and February tape built; only first 50000 quotes per tape funded replayed under each fixed month-blind source policy, not optimized monthly performance',
          'elapsed_s':round(time.monotonic()-start,2)},indent=2)+'\n')
if __name__=='__main__':main()
