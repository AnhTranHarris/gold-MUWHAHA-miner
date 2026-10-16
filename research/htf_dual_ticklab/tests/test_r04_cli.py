"""R04 CLI activation and output schema regression."""
import csv
import gzip
import json
import pytest
from htf_ticklab.cli import main, atomic_trades_csv

def fixture(tmp_path):
    source=tmp_path/'test.csv.gz'
    with gzip.open(source,'wt',encoding='utf-8') as stream:
        stream.write('time,time_msc,bid,ask,last,volume,volume_real,flags\n')
        stream.write('1767315600,1767315600000,100,100.20,0,0,0,134\n')
    return source

def test_r04_is_default_off_and_explicit_cost_required(tmp_path):
    src=fixture(tmp_path)
    output=tmp_path/'single.json'
    with pytest.raises(SystemExit,match='explicit positive commission and slippage'):
        main(['--broker','coinexx','--input',str(src),'--output',str(output),
              '--allow-unregistered-input','--strategy','six-specialist-r04'])
    assert not output.exists()
    main(['--broker','coinexx','--input',str(src),'--output',str(output),
          '--allow-unregistered-input','--strategy','six-specialist-r04',
          '--commission-per-lot-side','3.5','--slippage-price','0.10'])
    report=json.loads(output.read_text())
    assert report['strategy_id']=='six-specialist-r04'
    assert report['trades']==0
    assert report['source']['source_verified'] is False

def test_trade_ledger_retains_entry_specialist(tmp_path):
    target=tmp_path/'ledger.csv'
    atomic_trades_csv(target,[{
        'entry_ms':1,'exit_ms':2,'side':1,'lots':.01,
        'entry_price':101.,'exit_price':102.,
        'gross_pnl':1.,'net_pnl':.93,'reason':'target',
        'entry_fee':.035,'exit_fee':.035,'broker':'coinexx',
        'entry_reason':'arbiter:r03_six_specialists:pulse_continuation'}])
    with target.open(newline='') as stream:
        row=list(csv.DictReader(stream))[0]
    assert row['entry_reason'].endswith('pulse_continuation')
    assert row['net_pnl']=='0.93'
