"""Read-only GRID0272 checkpoint verifier. Never promotes a research candidate.
Uses unchanged January original Dukascopy CSV.gz and preserved GRID0272 NPZ/JSON.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import argparse
import hashlib, json, numpy as np, pandas as pd

parser = argparse.ArgumentParser(description='Read-only verification of previously preserved GRID0272 candidate, not a backtest')
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent,help='Extracted original GRID0272 ZIP directory')
parser.add_argument('--raw',type=Path,default=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'),help='Exact January original tick CSV.GZ')
parser.add_argument('--output',type=Path,default=None,help='Optional independent QA JSON output file (outside original archive)')
args=parser.parse_args()
ROOT=args.root
RAW=args.raw
STEM='cap256_hold1.0_interval125'
OUT=args.output or (ROOT/'GRID0272_RECOVERY_INDEPENDENT_READONLY_QA.json')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

m=json.loads((ROOT/'EXACT_SOURCE_QA_MANIFEST.json').read_text())
assert sha(RAW)==m['original_raw_tick_sha256'], 'canonical original data mismatch'
verified=[]
for item in m['original_source_file_hashes']:
    path=ROOT/item['path'];assert sha(path)==item['sha256'], path
    verified.append(item['path'])
a=np.load(ROOT/f'trades_{STEM}.npz',allow_pickle=False)
c=json.loads((ROOT/('original_composite_raw_250ms_fee20_q1190_'+STEM+'.json')).read_text())
df=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=df.timestamp_ms_utc.to_numpy(); ask=df.ask_raw.to_numpy(); bid=df.bid_raw.to_numpy()
assert len(t)==m['original_tick_count'], 'record count mismatch'
ei=a['entry_idx']; xi=a['exit_idx']; direction=a['direction']; pnl=a['net_cash']; names=a['source']
assert len(ei)==int(c['trades'])==len(xi)==len(pnl)
assert ((ei>=0)&(xi>=ei)&(xi<len(t))).all(),'invalid trade indices'
assert np.array_equal(a['entry_ms'],t[ei]),'entry timestamps do not match original ticks'
assert np.array_equal(a['exit_ms'],t[xi]),'exit timestamps do not match original ticks'
assert np.array_equal(a['entry_price_raw'],np.where(direction>0,ask[ei],bid[ei])),'entry price not executable original bid/ask'
exit_raw=np.where(direction>0,bid[xi],ask[xi]); expected=((exit_raw.astype(np.int64)-a['entry_price_raw'].astype(np.int64))*direction.astype(np.int64))/1000.0-0.20
errors=np.abs(expected-pnl);assert errors.max()<1e-9, f'bad modeled realized P&L: {errors.max()}'
assert abs(float(pnl.sum())-float(c['net']))<1e-8
loss=float(pnl[pnl<0].sum());gp=float(pnl[pnl>0].sum());assert abs(loss-c['gross_loss'])<1e-8
assert abs(gp-c['gross_profit'])<1e-8
assert abs(gp/-loss-c['pf'])<1e-8
# Compare all UTC daily and ISO-week realized close-date aggregates against preserved result dicts.
def bucket(which):
    d=defaultdict(list)
    for i,ms in enumerate(t[xi]):
        dt=datetime.fromtimestamp(int(ms)/1000,timezone.utc)
        key=dt.strftime('%Y-%m-%d') if which=='daily' else f'{dt.isocalendar().year}-W{dt.isocalendar().week:02d}'
        d[key].append(i)
    return d
checks={}
for which in ('daily','weekly'):
    b=bucket(which)
    stored=c[which]
    asserts=[]
    for k,v in stored.items():
        seq=pnl[b.get(k,[])]; net=float(seq.sum());
        check=(isinstance(v,dict) and abs(net-float(v.get('net',0)))<1e-7 and len(seq)==int(v.get('trades',-1)) and abs(float(seq[seq<0].sum())-float(v.get('gross_loss',0)))<1e-7 and abs(float(seq[seq>0].sum())-float(v.get('gross_profit',0)))<1e-7)
        asserts.append(check)
    checks[which]={'keys_reported':len(stored),'matched_net_keys':sum(asserts),'missing_bad':sorted(k for k,v in zip(stored,asserts) if not v)[:15]}
assert all(z['keys_reported']==z['matched_net_keys'] for z in checks.values()), 'daily/weekly aggregates mismatch'
# Preserve failed keys explicitly; zero error needed for accepted integrity audit, not research promotion.
report=dict(status='CHECKPOINT_QA_ONLY__NOT_RESEARCH_PROMOTION',repo_branch='delta-A-alpha',archived_original_files_sha_match=len(verified),original_raw_sha256=sha(RAW),ticks=len(t),ledger=STEM,trades=len(ei),net_cash=float(pnl.sum()),gross_profit=gp,gross_loss=loss,pf=gp/-loss,quote_pnl_max_abs_error=float(errors.max()),directional_buy_count=int((direction>0).sum()),sell_count=int((direction<0).sum()),daily_and_weekly=checks,source_cash={s:{'trades':int((names==s).sum()),'net':float(pnl[names==s].sum())} for s in np.unique(names)},known_unresolved=['Historical Watchdog source parent admission may use non-repriced upstream causal funding; no full end-to-end parent cash-equity loop certified','Global trade+heat account economic constraints still unverified','Original R9 OVERFIT per-trade 75pct and all R9 SYNTH daily/week targets not met','Archived GRID0271 63 negative trials retained without rerunning','No new Numba/STMR crashed scratchpad scripts verified beyond immutable ZIP'],trading_enabled=False,august_sealed=True)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('source_cash','known_unresolved')},indent=2))
