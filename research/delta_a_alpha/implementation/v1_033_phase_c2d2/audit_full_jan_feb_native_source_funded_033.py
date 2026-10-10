"""C2D3Q independent funded-ledger audit over FINISHED source-native Jan+Feb runs.

Executable audit authority: actual original source-generated event and the
current physically funded Bid/Ask L7 engine saved in trusted local checkpoints.
Not a reconstruction from source-performance summaries. Only original true
JAN/FEB quote indexes are permitted, with immutable original raw source hashes.
The historical selection parameters are frozen, no execution month switching.

Never pass untrusted checkpoint paths: trusted resume uses restricted local
pickle from this program's previously created checkpoint on this machine.
"""
from __future__ import annotations
import json, hashlib, math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from original_monthblind_segmented_l7_replay_033 import SegmentedRealQuoteResearch, runtime_signature
from original_verified_quote_tape_index_033 import VerifiedNativeQuoteTape
from run_original_jan_feb_indexed_funded_economics_033 import FILES

MODES=('JAN039_SOURCE_NATIVE','FEB045_SOURCE_NATIVE')
EXPECTED_QUOTE_TOTAL=sum(f['quotes'] for f in FILES.values())
EXPECTED_SOURCE_ENTRIES=272_931+173_885


def ledger_monthly(closes):
    """Post-settlement evaluation: never enters execution engine."""
    out=defaultdict(lambda:dict(trades=0,net=0.,gross_profit=0.,gross_loss=0.))
    for c in closes:
        key=datetime.fromtimestamp(c.time_ms/1000,timezone.utc).strftime('%Y-%m')
        m=out[key];m['trades']+=1;m['net']+=c.net_usd
        m['gross_profit']+=max(c.net_usd,0.)
        m['gross_loss']+=min(c.net_usd,0.)
    return {k:dict(trades=v['trades'],net=round(v['net'],6),
                   gross_profit=round(v['gross_profit'],6),
                   gross_loss=round(v['gross_loss'],6),
                   profit_factor=(round(v['gross_profit']/(-v['gross_loss']),9)
                                  if v['gross_loss']<0 else None))
            for k,v in sorted(out.items())}


def validate_closed_account(run):
    score=run.engine.score(); cl=run.engine.closed
    assert run.total_quotes==EXPECTED_QUOTE_TOTAL, 'Not a complete original Jan+Feb real quote run'
    assert run.feed.bridge.source_events==EXPECTED_SOURCE_ENTRIES, 'Original native JAN037/FEB041 event mismatch'
    assert run.feed.bridge.physical_callbacks==len(cl)+len(run.engine.positions), 'Paid/closed/open account mismatch'
    assert not run.engine.positions, 'Open positions at February end must be disclosed before economics freeze'
    assert score['month_blind'] is True, 'Month switch introduced into execution'
    assert score['combined_max_orders_sec']<=10, 'L7 combined order budget breached'
    assert score['funded_recovery_count']==0, 'Unexpected recovery branch funded'
    assert score['model']=='DETERMINISTIC_BIDASK_IDEALIZED_RESEARCH_KERNEL_NOT_V1_SOURCE_PARITY', 'Account model provenance changed'
    assert len(set(c.position_id for c in cl))==len(cl), 'Position closed twice'
    assert all(math.isfinite(c.net_usd) and c.exit_raw>0 for c in cl), 'Invalid settled Bid/Ask exit'
    assert all(a.time_ms<=b.time_ms for a,b in zip(cl,cl[1:])), 'Non-monotonic exit settlement'
    net=math.fsum(c.net_usd for c in cl)
    gp=math.fsum(max(c.net_usd,0.) for c in cl)
    gl=math.fsum(min(c.net_usd,0.) for c in cl)
    assert math.isclose(net,score['net'],abs_tol=0.001),'Realized net mismatch'
    assert math.isclose(gp,score['gross_profit'],abs_tol=0.001),'Gross profit mismatch'
    assert math.isclose(gl,score['gross_loss'],abs_tol=0.001),'Gross loss mismatch'
    if gl<0:assert math.isclose(gp/-gl,score['profit_factor'],abs_tol=1e-6),'Profit factor mismatch'
    m=ledger_monthly(cl)
    assert set(m)=={'2026-01','2026-02'}, 'Actual funded close left JAN/FEB source months'
    assert sum(v['trades'] for v in m.values())==len(cl),'Month deal count mismatch'
    assert math.isclose(sum(v['net'] for v in m.values()),net,abs_tol=0.001),'Month PnL mismatch'
    return score,m


def audit(workdir, sourcedir, rules):
    root=Path(sourcedir)
    manifest={}
    for k,f in FILES.items():
        path=root/f['name']; t=VerifiedNativeQuoteTape(path,
            expected_original_source_sha256=f['raw'],expected_index_sha256=f['binary'])
        assert len(t)==f['quotes']
        manifest[k]={'records':len(t),'original_raw_source_sha256':f['raw'],
                     'binary_quote_source_sha256':f['binary'],'bytes':path.stat().st_size}
    out={'schema':'DAA033-C2D3Q-full-original-native-JAN-FEB-funded-ab-ledger-v1',
         'source_program':'audit_full_jan_feb_native_source_funded_033.py',
         'full_original_bidask_quotes':EXPECTED_QUOTE_TOTAL,
         'native_50ms_generated_source_offers_expected':EXPECTED_SOURCE_ENTRIES,
         'raw_quote_index_source_manifest':manifest,
         'time_control':'No execution strategy mode depends on month. Close-date grouping AFTER settlement only.',
         'original_source_whole_8_layer_v1_completed':False,
         'actual_coinexx_mt5_broker_verified':False,
         'starting_idealized_usd_balance':100000.,
         'march_data_opened':False,
         'january_pre_T0_december2025_history_present':False,
         'source_code_runtime_sha256':runtime_signature(),
         'run_modes':{}}
    for mode in MODES:
        file=Path(workdir)/(mode+'.trusted-private-checkpoint.json')
        run=SegmentedRealQuoteResearch.resume_local_trusted_checkpoint(
            file,expected_mode=mode,source_rules_path=rules)
        for k,f in FILES.items():
            key=str((root/f['name']).resolve())
            assert run.read_rows.get(key)==f['quotes'],'Original source file not fully consumed'
        score, monthly=validate_closed_account(run)
        sources=defaultdict(lambda:dict(closed=0,net=0.))
        for close in run.engine.closed:
            s=sources[close.source];s['closed']+=1;s['net']+=close.net_usd
        bysrc={k:dict(closed=v['closed'],net=round(v['net'],6)) for k,v in sorted(sources.items())}
        di=run.funded_diagnostics()['realized_diagnostic_periods_only']
        out['run_modes'][mode]={
            'checkpoint_file_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
            'exact_original_quote_count':run.total_quotes,
            'source_generated_event_count':run.feed.bridge.source_events,
            'actual_physically_funded_entries':run.feed.bridge.physical_callbacks,
            'physically_closed_deals':len(run.engine.closed),
            'realized_account_score':score,
            'utc_realized_close_months':monthly,
            'utc_realized_close_week_count':len(di.get('weekly',{})),
            'utc_realized_close_day_count':len(di.get('daily',{})),
            'by_actual_funded_original_source':bysrc,
            'no_open_positions':not bool(run.engine.positions),
            'is_this_only_source_family':True,
            'full_original_V1_Jan039_Feb045_Feb047_parity':False}
    return out


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--work-dir',default='/mnt/data/c2d3q_work/full')
    p.add_argument('--source-dir',default='/mnt/data/c2d3p_work/data')
    p.add_argument('--rules',default=str(Path(__file__).parent/'verified_original_sources/JAN038/JAN038_SELECTED_EXACT.json'))
    p.add_argument('--output',default='/mnt/data/c2d3q_work/JAN_FEB_16673401_FULL_FUNDED_NATIVE_AB_SOURCE_ECONOMICS_033.json')
    args=p.parse_args(); result=audit(args.work_dir,args.source_dir,args.rules)
    dst=Path(args.output);temp=dst.with_suffix(dst.suffix+'.tmp')
    temp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');temp.replace(dst)
    print(json.dumps({m:{'trades':j['physically_closed_deals'],'net':j['realized_account_score']['net'],
           'max_equity_dd':j['realized_account_score']['max_equity_dd'],
           'monthly':j['utc_realized_close_months']} for m,j in result['run_modes'].items()},indent=2))
    print('ARTIFACT',dst)
if __name__=='__main__':main()
