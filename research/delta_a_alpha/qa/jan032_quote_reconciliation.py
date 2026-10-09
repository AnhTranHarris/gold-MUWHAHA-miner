"""QA and comparative scorecard on the literal original January 131E source run.
Counts and results are classified as ORIGINAL_SOURCE_CHAIN_REPLAY with raw Bid/Ask, not broker-funded parity.
"""
from pathlib import Path
import csv,json,datetime,math,statistics,collections,hashlib,gzip
D=Path(__file__).resolve().parent;OUT=D/'output'
raw=json.loads((OUT/'JAN032_ORIGINAL_RAW_L35_C640.json').read_text());p75=json.loads((OUT/'JAN032_ORIGINAL_P75_L35_C640.json').read_text());r9=json.loads((D/'r9_synth_jan_daily_weekly.json').read_text())
cols=['period','date','raw_net','raw_trades','raw_gross_profit','raw_gross_loss','raw_pf','raw_win_pct','raw_expectancy','p75_net','p75_trades','p75_gross_loss','r9_synth_net','r9_synth_trades','r9_synth_gross_profit','r9_synth_gross_loss_131d','r9_synth_pf_131d','r9_synth_win_pct_131d','raw_minus_r9_net','raw_minus_r9_trades','raw_over_r9_net','raw_beat_r9_net','raw_positive']
def weekly_daily(kind):
    rows=[]
    for k,rr in r9[kind].items():
        x=raw[kind].get(k,{});h=p75[kind].get(k,{})
        def v(o,key):return float(o.get(key,0.))
        net=v(x,'net');rrn=v(rr,'net')
        o={'period':kind,'date':k,'raw_net':round(net,3),'raw_trades':int(x.get('trades',0)),'raw_gross_profit':round(v(x,'gross_profit'),3),'raw_gross_loss':round(v(x,'gross_loss'),3),'raw_pf':round(v(x,'pf'),4),'raw_win_pct':round(100*v(x,'win'),2),'raw_expectancy':round(v(x,'expectancy'),4),'p75_net':round(v(h,'net'),2),'p75_trades':int(h.get('trades',0)),'p75_gross_loss':round(v(h,'gross_loss'),2),'r9_synth_net':round(rrn,2),'r9_synth_trades':int(rr.get('trades',0)),'r9_synth_gross_profit':round(v(rr,'gross_profit'),2),'r9_synth_gross_loss_131d':round(v(rr,'gross_loss'),2),'r9_synth_pf_131d':round(v(rr,'pf'),4),'r9_synth_win_pct_131d':round(100*v(rr,'win'),2),'raw_minus_r9_net':round(net-rrn,3),'raw_minus_r9_trades':int(x.get('trades',0))-int(rr.get('trades',0)),'raw_over_r9_net':round(net/rrn,5) if rrn else None,'raw_beat_r9_net':net>=rrn,'raw_positive':net>0}
        rows.append(o)
    with (OUT/f'JAN032_RAW_VS_R9_{kind.upper()}.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    return rows
DAYS=weekly_daily('daily');WEEKS=weekly_daily('weekly')

def pearson(xs,ys):
    mx=statistics.mean(xs);my=statistics.mean(ys)
    a=sum((x-mx)*(y-my) for x,y in zip(xs,ys));b=sum((x-mx)**2 for x in xs);c=sum((y-my)**2 for y in ys)
    return a/math.sqrt(b*c) if b>0 and c>0 else None

def source_quote_audit(mode):
    file=OUT/f'JAN032_ORIGINAL_{mode}_L35_C640_EXECUTIONS.csv'
    seen=set();dupticks=0;trades=0;maxerr=0.;badchrono=0;nonprofit=0;tot=0;earliest=None;latest=None
    for row in csv.DictReader(file.open()):
        trades+=1;ei=int(row['entry_index']);xi=int(row['exit_index']);ent=int(row['entry_side_price']);ex=int(row['exit_side_price']);d=int(row['direction']);p=float(row['pnl_usd']);t0=int(row['entry_ms']);t1=int(row['exit_ms']);
        expected=d*(ex-ent)/1000-.02
        maxerr=max(maxerr,abs(expected-p));
        if xi<=ei or t1<=t0:badchrono+=1
        if ei in seen:dupticks+=1
        seen.add(ei);tot+=p
        if earliest is None or t0<earliest:earliest=t0
        if latest is None or t1>latest:latest=t1
    return {'mode':mode,'trades':trades,'unique_entry_ticks':len(seen),'duplicate_entry_tick_events':dupticks,'max_pnl_reconciliation_error_usd':maxerr,'nonfuture_exit_errors':badchrono,'ledger_net_usd':round(tot,4),'first_entry_utc':datetime.datetime.fromtimestamp(earliest/1000,datetime.timezone.utc).isoformat() if earliest else None,'last_exit_utc':datetime.datetime.fromtimestamp(latest/1000,datetime.timezone.utc).isoformat() if latest else None}
qraw=source_quote_audit('RAW');qp75=source_quote_audit('P75');
source_can={'R9_SYNTH_CANONICAL_MT5':{'net':41520.82,'trades':27980,'gross_profit':43592.43,'gross_loss':-2071.61,'pf':21.042778,'win_pct':87.130093},'R9_SYNTH_ARCHIVED_131D':r9['month']}
checks={
 'archived_p75_exact_net':abs(p75['net']-194425.92)<1e-3,
 'archived_p75_exact_trade_count':p75['trades']==80929,
 'archived_p75_exact_equity_dd':abs(p75['equity_dd']-57139.2)<1e-3,
 'raw_quote_pnl_reconciles':qraw['max_pnl_reconciliation_error_usd']<0.00001 and abs(qraw['ledger_net_usd']-raw['net'])<.01,
 'raw_exit_after_entry':qraw['nonfuture_exit_errors']==0,
 'r9_131d_day_sums':abs(sum(x['r9_synth_net'] for x in DAYS)-41520.82)<.01 and sum(x['r9_synth_trades'] for x in DAYS)==27980,
 'raw_day_sums':abs(sum(x['raw_net'] for x in DAYS)-raw['net'])<.02 and sum(x['raw_trades'] for x in DAYS)==raw['trades'],
 'raw_week_sums':abs(sum(x['raw_net'] for x in WEEKS)-raw['net'])<.02 and sum(x['raw_trades'] for x in WEEKS)==raw['trades'],
}
raw_30=next(x for x in DAYS if x['date']=='2026-01-30')
report={
 'status':'ORIGINAL_JANUARY_131E_SOURCE_RAW_BID_ASK_REPLAY_VERIFIED_NOT_FULL_PHYSICAL_V1_CERTIFICATION',
 'source_data':'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',
 'source_sha256':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 'quote_count':9135062,
 'archived_P75_source_replay':{k:p75[k] for k in ('net','trades','gross_loss','pf','win','equity_dd','maxopen','wd_net','wd_trades')},
 'raw_BidAsk_same_source_mechanics':{k:raw[k] for k in ('net','trades','gross_profit','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','wd_net','wd_trades','positive_days','beat_days','positive_weeks','beat_weeks')},
 'r9_benchmark_sources':source_can,
 'raw_vs_r9_month':{'net_difference':raw['net']-41520.82,'trade_count_delta':raw['trades']-27980,'pf_delta':raw['pf']-21.042778,'win_pct_delta':raw['win']*100-87.130093},
 'raw_vs_r9_daily':{'beat_net_days':sum(x['raw_beat_r9_net'] for x in DAYS),'positive_days':sum(x['raw_positive'] for x in DAYS),'total':len(DAYS),'pearson_net_all_days':pearson([x['raw_net'] for x in DAYS],[x['r9_synth_net'] for x in DAYS]),'pearson_net_excluding_jan30':pearson([x['raw_net'] for x in DAYS[:-1]],[x['r9_synth_net'] for x in DAYS[:-1]]),'pearson_trades_all_days':pearson([x['raw_trades'] for x in DAYS],[x['r9_synth_trades'] for x in DAYS])},
 'raw_vs_r9_weekly':{'beat_net_weeks':sum(x['raw_beat_r9_net'] for x in WEEKS),'positive_weeks':sum(x['raw_positive'] for x in WEEKS),'total':len(WEEKS)},
 'jan30_raw':{'net':raw_30['raw_net'],'trades':raw_30['raw_trades'],'gross_loss':raw_30['raw_gross_loss'],'share_of_month_net':raw_30['raw_net']/raw['net'],'share_of_month_trades':raw_30['raw_trades']/raw['trades']},
 'qa':checks,'ledger_check':qraw,'p75_ledger_check':qp75,
 'fidelity_warnings':['Original source uses normalized P75 spread for historical benchmark; raw override uses Dukascopy as provided and may change entries, states, parent campaigns, not only reprice identical trades.','Original 131E parent scout and successive child funding decisions partly depend on potential realized children before downstream capacity enforcement; physical funded-chain parity not proven.','Original Jan1 file lacks Dec2025 HTF completed history; five-minute arbitrary deployment readiness not certified.','Research lot 0.01=1 ounce with $0.02 fee, hypothetical $100k equity and no broker-specific leverage/swap/slippage/stopout certification.','January already researched; no claim of an untouched statistical blind test.','R9 131D daily/weekly gross metrics differ from newer canonical MT5 cashflow-gross metrics despite same net and trades; canonical governs monthly gross PF.']}
(OUT/'JAN032_RAW_SOURCE_QA_AND_CORRELATION.json').write_text(json.dumps(report,indent=2))
print('QA',checks)
print('AUDIT',qraw)
print('MONTH_RAW',round(raw['net'],2),raw['trades'],'profit_on_JAN30_pct',round(100*raw_30['raw_net']/raw['net'],1),'trades_JAN30_pct',round(100*raw_30['raw_trades']/raw['trades'],1))
print('CORR',report['raw_vs_r9_daily'])
for x in WEEKS:print('WEEK',x['date'],'RAW',x['raw_net'],'R9',x['r9_synth_net'],'TRADES',x['raw_trades'],x['r9_synth_trades'])