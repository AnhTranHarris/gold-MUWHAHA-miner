"""True raw January Dukascopy gzip chunk/restart parity, full digest and one funded L7."""
from pathlib import Path
import hashlib,json,tempfile,sys,time
sys.path.insert(0,str(Path(__file__).parent))
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch

SOURCE=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
ORIG='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
RULE=Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'

def main():
    t=time.monotonic()
    with SOURCE.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==ORIG
    scores={}
    for mode in ('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE'):
        direct=SegmentedRealQuoteResearch.start(mode,RULE)
        assert direct.run_gzip_chunk(SOURCE,expected_sha256=ORIG,max_new_quotes=4000)==4000
        partial=SegmentedRealQuoteResearch.start(mode,RULE)
        assert partial.run_gzip_chunk(SOURCE,expected_sha256=ORIG,max_new_quotes=2000)==2000
        with tempfile.TemporaryDirectory() as d:
            snap=Path(d)/'partial_checkpoint.json'
            partial.save_local_trusted_checkpoint(snap)
            resumed=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(
                       snap,expected_mode=mode,source_rules_path=RULE)
            assert resumed.run_gzip_chunk(SOURCE,expected_sha256=ORIG,max_new_quotes=2000)==2000
            assert resumed.funded_diagnostics()==direct.funded_diagnostics()
            assert resumed.engine.events==direct.engine.events
            assert resumed.feed.ordinal==direct.feed.ordinal
            scores[mode]={'original_quote_count':4000,'restart_at_quote':2000,
                'fully_matched_including_events':True,'funded_score':resumed.funded_diagnostics()}
    out={'unmodified_original_DUKAS_Jan2026_source_SHA256':ORIG,
         'source_quotes':4000,'research_modes':scores,'calendar_month_as_runtime_feature':False,
         'fully_funded_Jan_Feb_portfolio_ready':False,'elapsed_seconds':round(time.monotonic()-t,3)}
    dest=Path(__file__).parent/'JAN_TRUE_GZ_CHUNKED_L7_RESTART_PARITY_033.json'
    dest.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'actual_genuine_quotes':4000,'two_modes':list(scores),'restart_parity':True,'seconds':out['elapsed_seconds']}))

if __name__=='__main__':main()
