"""One-pass intact original Coinexx 2026 Jan-Sep cash ladder policy comparison.

The original R9 state machine and original source ZIP receipts are authoritative.
No raw dataset reconstruction/output. Only compact JSON monthly/report summary.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, os, sys, time, zipfile
from datetime import datetime,timezone
from pathlib import Path
from collections import Counter, defaultdict

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from on_policy_cash_replay import ManagedR9,QuoteRegime,ResearchCash

CHECK_FIELDS=('entry_ordinal','exit_ordinal','entry_time_msc','exit_time_msc',
              'side','entry_price_u','exit_price_u','net_price_u','reason')

def verify_month(original, start, month, z, receipt):
    member=f'candidate_closes_2026_{month}.csv.gz'
    with gzip.GzipFile(fileobj=io.BytesIO(z.read(member))) as f:
        rows=csv.DictReader(io.TextIOWrapper(f,encoding='utf-8'))
        expected=receipt['source_months'][month]['entries']
        monthtrades=original.trades[start:]
        if len(monthtrades)!=expected:
            raise AssertionError(f'{month}: baseline count mismatch {len(monthtrades)} != {expected}')
        for n,(r,tr) in enumerate(zip(rows,monthtrades,strict=True)):
            for k in CHECK_FIELDS:
                actual=getattr(tr,k)
                wanted=int(r[k]) if k!='reason' else r[k]
                if actual!=wanted:
                    raise AssertionError(f'{month}: baseline trade {n} field {k}: {actual} != {wanted}')
    return expected

def source_sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for v in iter(lambda:f.read(2**22),b''):h.update(v)
    return h.hexdigest()

def summarize_original(sim,cash):
    per_month=defaultdict(float);per_month_n=defaultdict(int)
    daily=defaultdict(float);hour=defaultdict(float)
    vals=[];dur=[];gross=0.;equity=0.;peak=0.;max_dd=0.
    for tr in sim.trades:
        net=tr.net_price_u/100.*cash.k-cash.cost
        vals.append(net);dur.append(tr.exit_time_msc-tr.entry_time_msc)
        period=datetime.fromtimestamp(tr.entry_time_msc/1000,timezone.utc).strftime('%Y-%m')
        per_month[period]+=net;per_month_n[period]+=1
        daily[tr.entry_time_msc//86400000]+=net
        hour[tr.entry_time_msc//3600000]+=net
        gross+=max(0.,-net)
        equity+=net;peak=max(peak,equity);max_dd=max(max_dd,peak-equity)
    n=len(vals);w=sorted(vals)[:max(1,int(.05*n))];d=sorted(dur)
    return dict(mode='original',trades=n,net_cash=round(sum(vals),5),
         net_per_trade=round(sum(vals)/n,6),active_entry_hours=len(hour),
         net_per_active_entry_hour=round(sum(vals)/max(1,len(hour)),5),
         mean_hold_sec=round(sum(dur)/1000/n,5),p95_hold_sec=d[int(.95*(n-1))]/1000,
         p99_hold_sec=d[int(.99*(n-1))]/1000,
         win_fraction=round(sum(v>0 for v in vals)/n,6),
         target_ge_0_5=sum(v>=.5-1e-9 for v in vals),
         target_ge_1_75=sum(v>=1.75-1e-9 for v in vals),
         loss_le_minus_2=sum(v<=-2 for v in vals),
         gross_realized_losses=round(gross,5),
         closed_trade_cvar95_loss=round(-sum(w)/len(w),6),
         max_account_peak_drawdown_cash_no_governor=round(max_dd,5),
         monthly_net={m:round(v,5) for m,v in sorted(per_month.items())},
         monthly_trades=dict(per_month_n),
         source_hour_cash_negative_count=sum(v<0 for v in hour.values()),
         source_hour_cash_positive_count=sum(v>0 for v in hour.values()),
         source_day_cash_negative_count=sum(v<0 for v in daily.values()),
         source_day_cash_positive_count=sum(v>0 for v in daily.values()),
         rearm_count=int(sim.stats['rearms']),
         note='Exact original v1.90 python core (not complete MT5 v1.94 broker/account simulation)')

class SharedMarketATR:
    """Read-only reference to original ATR, to avoid duplicating quote work.

    Independent positions/rearms remain separate; only common input prices and
    completed bar history are shared, using the exact original code.
    """
    def __init__(self,ref):self.ref=ref
    def update(self,t):pass
    @property
    def ready(self):return self.ref.ready
    @property
    def atr_u(self):return self.ref.atr_u


def reuse_only_identical_market_context(control, *arms):
    for arm in arms:
        arm.micro=control.micro
        arm.second_builder=control.second_builder
        arm._push_second=lambda t:None
        arm.atr=SharedMarketATR(control.atr)


def run(args):
    cash=ResearchCash(args.k,args.c,args.start_capital,args.governor)
    original=R9HybridGateBaseline(R9Config())
    reg=QuoteRegime()
    harvest=ManagedR9(R9Config(),cash,'cash_harvest',reg)
    experiment=ManagedR9(R9Config(),cash,'regime_probe',reg)
    governed_baseline=(ManagedR9(R9Config(),cash,'original',reg)
                      if args.governor else None)
    if governed_baseline is not None:
        reuse_only_identical_market_context(original,harvest,experiment,governed_baseline)
    else:
        reuse_only_identical_market_context(original,harvest,experiment)
    # Real-MQL5 v1.94 account governor is not present in original v1.90 source.
    # This optional scenario never modifies the baseline parity control.
    original_count=0;ord_offset=0;receipts=[];by_month=[]
    with zipfile.ZipFile(args.receipt) as z:
        frozen=json.loads(z.read('source_receipt.json'))
        for mm in args.months:
            path=args.data/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
            if not path.is_file():raise FileNotFoundError(path)
            sha=source_sha(path)
            wanted=frozen['source_months'][mm]['source_sha256']
            if sha!=wanted:raise ValueError(f'ORIGINAL SHA256 ERROR {mm}')
            mon_start=time.monotonic();rows=0
            for tick in iter_coinexx_ticks(path,strict=True,ordinal_offset=ord_offset):
                reg.update(tick)
                original.on_tick(tick)
                harvest.on_tick(tick)
                experiment.on_tick(tick)
                if governed_baseline is not None:
                    governed_baseline.on_tick(tick)
                rows+=1
                if args.max_rows and rows>=args.max_rows:break
            completed= (rows==frozen['source_months'][mm]['rows'])
            if completed:
                matched=verify_month(original,original_count,mm,z,frozen)
            else:
                matched=None
            original_count=len(original.trades)
            ord_offset+=rows
            r=dict(month=mm,source_sha256=sha,rows=rows,baseline_full_ledger_parity=bool(completed and matched is not None),
                   baseline_month_trades=matched,
                   cash_harvest_trades=len(harvest.trades),
                   experimental_regime_trades=len(experiment.trades),
                   elapsed_seconds=round(time.monotonic()-mon_start,1))
            by_month.append(r)
            receipts.append(dict(month=mm,sha256=sha,rows=rows))
            print('MONTH '+json.dumps(r,sort_keys=True),flush=True)
            data=dict(classification='COINEXX_SOURCE_EXACT_QUOTE_MODEL_NOT_ACTUAL_BROKER_FILLS',
               original_ledger_pinned_source_sha=True,all_processed_months_full_parity=all(v['baseline_full_ledger_parity'] for v in by_month),
               source_receipts=receipts,by_month=by_month,
               account_assumptions={'cash_per_1_xau':cash.k,'additional_roundtrip_cost':cash.cost,
                         'starting_capital':cash.initial_capital,'account_governor_scenario':cash.governor},
               baseline=summarize_original(original,cash),cash_harvest=harvest.report(),
               regime_probe=experiment.report())
            # A risk-governor experiment must compare all three arms under
            # the SAME governor. The full source-exact baseline remains
            # ungoverned and separate solely for frozen-ledger parity.
            key_base='baseline'
            if governed_baseline is not None:
                data['governed_original']=governed_baseline.report()
                key_base='governed_original'
            base_n=data[key_base]['trades']
            for key in ('cash_harvest','regime_probe'):
                if data[key]['trades'] and base_n:
                    data[key]['trade_retention_vs_comparable_baseline']=round(data[key]['trades']/base_n,6)
                    data[key]['net_cash_delta_vs_comparable_baseline']=round(data[key]['net_cash']-data[key_base]['net_cash'],5)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(data,indent=2,sort_keys=True))
            if not completed:break
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',type=Path,default=Path('/mnt/data'))
    p.add_argument('--receipt',type=Path,default=Path('/mnt/data/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip'))
    p.add_argument('--months',nargs='+',default=[f'{x:02d}' for x in range(1,10)])
    p.add_argument('--k',type=float,default=1.)
    p.add_argument('--c',type=float,default=.20)
    p.add_argument('--start-capital',type=float,default=100_000.)
    p.add_argument('--governor',action='store_true')
    p.add_argument('--max-rows',type=int,default=0)
    p.add_argument('--output',type=Path,default=Path('/mnt/data/r9_variable_horizon_scores.json'))
    args=p.parse_args()
    run(args)