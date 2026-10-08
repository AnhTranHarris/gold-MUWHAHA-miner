import pandas as pd,json,hashlib,tarfile,io
from pathlib import Path
p=Path('/mnt/data/daa_january_full_execution_024')
rows=[];daily=[];weekly=[];flags=[]
for cap in (16,64,128,256):
    for var in ('baseline','aware'):
        m=json.loads((p/f'{var}_cap{cap}_selected_score.json').read_text())
        df=pd.read_csv(p/f'{var}_cap{cap}_selected_daily.csv');wf=pd.read_csv(p/f'{var}_cap{cap}_selected_weekly.csv')
        trades=pd.read_csv(p/f'{var}_cap{cap}_selected_trades.csv')
        assert len(trades)==m['trades']
        assert abs(trades.net.sum()-m['net'])<1e-6
        assert trades.entry_idx.nunique()==len(trades)
        assert (trades.exit_idx>=trades.entry_idx).all()
        assert abs(((trades.exit_quote_raw-trades.entry_quote_raw)*trades.direction/1000-.02)-trades.net).max()<1e-9
        assert 0<=m['max_open']<=cap
        dd=df.copy();dd['cap']=cap;dd['variant']=var;daily.append(dd)
        ww=wf.copy();ww['cap']=cap;ww['variant']=var;weekly.append(ww)
        rows.append({'cap':cap,'variant':var,'trades':m['trades'],'net':m['net'],'gross_profit':m['gross_profit'],'gross_loss':m['gross_loss'],'pf':m['profit_factor'],'win_pct':m['win_rate']*100,'expectancy':m['expectancy'],'balance_dd':m['balance_drawdown_exact'],'full_equity_dd':m['full_tick_equity_dd'],'min_total_equity':m['min_total_equity'],'max_open':m['max_open'],'positive_days':int((df.net>0).sum()),'active_days':len(df),'positive_weeks':int((wf.net>0).sum()),'active_weeks':len(wf),'mean_trades_per_active_day':m['trades']/len(df),'top_day_net_share_pct':df.net.max()/m['net']*100,'quote_parity_error':m['raw_quote_pnl_parity_max_abs']})
        flags.append({'cap':cap,'variant':var,'quote_recon':'PASS','monotonic_execution':'PASS','one_entry_per_tick':'PASS','cap':'PASS','label':'PROTOTYPE_NOT_ORIGINAL_131E'})
res=pd.DataFrame(rows);res.to_csv(p/'comparison_monthly.csv',index=False)
pd.concat(daily,ignore_index=True).to_csv(p/'comparison_daily.csv',index=False)
pd.concat(weekly,ignore_index=True).to_csv(p/'comparison_weekly.csv',index=False)
(Path(p/'QA_FLAGS_024.json')).write_text(json.dumps(flags,indent=2))
r9={'2026-01':{'synth':{'net':41520.82,'trades':27980,'gross_loss':-2071.61,'profit_factor':21.042778,'win_rate_pct':87.130093},'real':{'net':-6651.62,'trades':31915,'gross_loss':-10436.90,'profit_factor':0.362682,'win_rate_pct':43.700454}},'source':'canonical R9 REAL/SYNTH Jan–Jul tester deal ledger; not a V1 comparison simulation'}
(p/'R9_REFERENCE_ONLY.json').write_text(json.dumps(r9,indent=2))
print('QA PASS:',len(flags),'replays, exact quote/PnL parity, unique tick entry, global cap, forward exits')
print(res[['cap','variant','net','trades','gross_loss','pf','win_pct','full_equity_dd','positive_days','positive_weeks']].round(2).to_string(index=False))