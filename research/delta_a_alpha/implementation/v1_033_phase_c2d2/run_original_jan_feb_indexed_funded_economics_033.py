"""DAA033 C2D3Q: genuine complete sequential Jan+Feb original quote-funded replay.

Uses ONLY verified full original January and February true BidAsk binary quote indexes
from reproducible source .csv.gz; no month-related strategy selection. The original
entire JAN037/JAN038/JAN039 or FEB045/FEB047 chosen mode is locked at startup.

Each run is bounded via --max-new-quotes to avoid chat/job timeout. The existing
trusted-only atomic checkpoint records original source quote and funded state.
Profit, gross loss, drawdown, daily/weekly/monthly diagnostics are AFTER-TRADE
scorecards, never features or feedback to market decision logic.

Never open an untrusted pickle snapshot. These are local generated research files.
"""
from __future__ import annotations
import argparse,hashlib,json,os,time
from pathlib import Path
from original_verified_quote_tape_index_033 import VerifiedNativeQuoteTape
from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch,ALLOWED_MODES

FILES={
 'JAN':{'raw':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','binary':'e45f40c120fa235c4a25b56f87714318015579c3afb2b671e3f66f487796337c','name':'ORIGINAL_JAN2026_TRUE_BIDASK_QUOTE_INDEX.bin','quotes':9135062},
 'FEB':{'raw':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','binary':'25cdc90b9ef72fa4cb7fc5022e36d8c3c0d58e2bc955de1319768106080007e9','name':'ORIGINAL_FEB2026_TRUE_BIDASK_QUOTE_INDEX.bin','quotes':7538339}}

def execute(*,mode:str,work_dir,source_dir,original_rules,limit:int,chunk:int=50000):
    if mode not in ALLOWED_MODES:raise ValueError('Unknown original fixed source mode')
    if limit<=0 or chunk<=0 or chunk>limit:raise ValueError('Choose finite quote budget')
    folder=Path(work_dir);folder.mkdir(parents=True,exist_ok=True)
    root=Path(source_dir)
    checkpoint=folder/f'{mode}.trusted-private-checkpoint.json'
    progress=folder/f'{mode}.progress.json'
    rules=Path(original_rules)
    run=(SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(checkpoint,
             expected_mode=mode,source_rules_path=rules)
         if checkpoint.exists() else SegmentedRealQuoteResearch.start(mode,rules))
    total_before=run.total_quotes
    spent=0;finished=False
    started=time.monotonic()
    for name,required in FILES.items():
        loc=root/required['name']
        tape=VerifiedNativeQuoteTape(loc,expected_original_source_sha256=required['raw'],
                                        expected_index_sha256=required['binary'])
        if len(tape)!=required['quotes']:raise ValueError('Source count mismatch')
        done=run.read_rows.get(tape.index_id,0)
        if done>=len(tape):continue
        while spent<limit and done<len(tape):
            count=min(chunk,limit-spent,len(tape)-done)
            n=tape.feed_next(run,max_new_quotes=count)
            if n!=count:raise ValueError('Quote ingest count shortfall')
            spent+=n;done+=n
            run.save_local_trusted_checkpoint(checkpoint)
            score=run.engine.score()
            snapshot={'schema':'DAA033-C2D3Q-monthblind-real-source-funded-economics-progress-v1',
                'source_mode_selected_before_ingest':mode,'all_quotes_processed':run.total_quotes,
                'original_native_source_proposals':run.feed.bridge.source_events,
                'paid_source_entries':run.feed.bridge.physical_callbacks,
                'actually_closed_deals':len(run.engine.closed),
                'score_from_only_funded_account':score,
                'read_positions':{k:run.read_rows.get(str((root/v['name']).resolve()),0) for k,v in FILES.items()},
                'last_index_month_source':name,'last_quote_epoch_ms':run.engine._last_quote.time_ms if run.engine._last_quote else None,
                'source_jan_feb_sha256':{k:{'raw':v['raw'],'binary':v['binary']} for k,v in FILES.items()},
                'march_data_read':False,'live_month_switching':False,
                'is_original_full_eight_layer_V1_certified':False,
                'model':'IDEALIZED_BIDASK_SOURCE_ONLY_L3_WITH_FUNDED_L7_OTHER_OPTIMIZED_SOURCE_ROLES_INCOMPLETE'}
            temp=progress.with_name(progress.name+'.part')
            temp.write_text(json.dumps(snapshot,indent=2)+'\n');os.replace(temp,progress)
            print(json.dumps({'mode':mode,'source':name,'source_quotes':done,
                'total_quotes':run.total_quotes,'new_this_run':spent,
                'source_offers':run.feed.bridge.source_events,'paid':run.feed.bridge.physical_callbacks,
                'closed':len(run.engine.closed),'net':score.get('net'),
                'dd':score.get('max_equity_dd'),'open':score.get('open_positions'),
                'elapsed_s':round(time.monotonic()-started,2)}),flush=True)
        if spent>=limit:break
    finished=all(run.read_rows.get(str((root/record['name']).resolve()),0)==record['quotes'] for record in FILES.values())
    return {'new_processed':spent,'prior_processed':total_before,'now_total':run.total_quotes,'both_full_months_complete':finished,
            'mode':mode,'progress_file':str(progress),'checkpoint':str(checkpoint)}

if __name__=='__main__':
  p=argparse.ArgumentParser();p.add_argument('--mode',choices=sorted(ALLOWED_MODES),required=True)
  p.add_argument('--work-dir',default='/mnt/data/c2d3q_work/full')
  p.add_argument('--source-dir',default='/mnt/data/c2d3p_work/data')
  p.add_argument('--rules',default=str(Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'))
  p.add_argument('--max-new-quotes',type=int,default=200000)
  p.add_argument('--chunk',type=int,default=50000)
  a=p.parse_args();print('END',json.dumps(execute(mode=a.mode,work_dir=a.work_dir,
   source_dir=a.source_dir,original_rules=a.rules,limit=a.max_new_quotes,chunk=a.chunk)),flush=True)
