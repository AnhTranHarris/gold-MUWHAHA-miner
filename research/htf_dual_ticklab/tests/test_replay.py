import gzip
import json
from pathlib import Path
import pytest
from htf_ticklab.feeds import Quote, FeedQuality, read_ticks
from htf_ticklab.bars import CandleStream
from htf_ticklab.engine import BrokerConfig, Replay
from htf_ticklab.strategies import NoTrades
from htf_ticklab.cli import main


def gz(tmp_path,name,text):
    p=tmp_path/name
    with gzip.open(p,'wt') as f:f.write(text)
    return p


def test_two_broker_feed_normalization(tmp_path):
    coin=gz(tmp_path,'c.csv.gz','time,time_msc,bid,ask,last,volume,volume_real,flags\n1767315600,1767315600480,4324.37,4327.44,0,0,0,134\n')
    duk=gz(tmp_path,'d.csv.gz','timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume\n1767308400596,4327902,4323698,0.00012,0.00012\n')
    a=list(read_ticks(coin,'coinexx',FeedQuality()))[0]
    b=list(read_ticks(duk,'dukascopy',FeedQuality()))[0]
    assert (a.bid,a.ask,a.ms)==(4324.37,4327.44,1767315600480)
    assert (b.bid,b.ask,b.ms)==(4323.698,4327.902,1767308400596)
    assert b.ask_volume==0.00012 and a.flags==134


def test_duplicate_ms_retained_and_reversals_rejected(tmp_path):
    header='timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume\n'
    fmt=lambda t:f'{t},4327902,4323698,0.1,0.2\n'
    good=gz(tmp_path,'same.csv.gz',header+fmt(1767308400500)+fmt(1767308400500))
    qual=FeedQuality();assert len(list(read_ticks(good,'dukascopy',qual)))==2
    assert qual.duplicates_ms==1
    bad=gz(tmp_path,'reversed.csv.gz',header+fmt(1767308400600)+fmt(1767308400500))
    with pytest.raises(ValueError,match='timestamp reversal'):
        list(read_ticks(bad,'dukascopy',FeedQuality()))


def test_crossed_quote_is_rejected(tmp_path):
    bad=gz(tmp_path,'crossed.csv.gz','timestamp_ms_utc,ask_raw,bid_raw,ask_volume,bid_volume\n1767308400596,4323000,4324000,0.1,0.1\n')
    with pytest.raises(ValueError,match='invalid quote'):
        list(read_ticks(bad,'dukascopy',FeedQuality()))


def test_only_completed_candle_visible_and_no_gap_filling():
    c=CandleStream((5,15))
    q=lambda ms,p:Quote(ms,p,p+.2,'coinexx')
    assert c.update(q(1767315600100,10))==[]
    assert c.update(q(1767315604100,12))==[]
    bars=c.update(q(1767315615000,13))
    assert len(bars)==2
    s5=next(x for x in bars if x.seconds==5)
    assert (s5.bid_open,s5.bid_high,s5.bid_close,s5.ticks)==(10,12,12,2)
    # No fabricated 5s or 10s bars in the quote gap.
    assert len(c.last_closed)==2

class Once:
    def __init__(self):self.done=False
    def on_bar(self,bar,q,sim):pass
    def on_tick(self,q,sim):
        if not self.done:
            sim.request_entry(1,.01,stop_distance=1.0,target_distance=2.0)
            self.done=True


def test_market_buy_ask_and_stop_bid_with_latency_and_fees():
    cfg=BrokerConfig(name='coinexx',initial_balance=100,order_latency_ms=100,
                     commission_per_lot_side=1.0)
    sim=Replay(cfg,Once(),(5,15,))
    q=lambda ms,bid,ask:Quote(ms,bid,ask,'coinexx')
    sim.on_quote(q(1767315600000,100,100.2)) # request queued
    assert sim.position is None
    sim.on_quote(q(1767315600050,100.1,100.3)) # too early
    assert sim.position is None
    sim.on_quote(q(1767315600100,100.2,100.4)) # fill 100.4 ask
    assert sim.position.entry==100.4
    sim.on_quote(q(1767315600200,99.3,99.6)) # stop at 99.4 crossed; exit at 99.3 bid
    t=sim.trades[0]
    assert t['entry_price']==100.4 and t['exit_price']==99.3
    assert t['net_pnl']==pytest.approx(-1.12) # 0.01*100oz, fees .01 each
    assert sim.balance==pytest.approx(98.88)
    assert sim.max_dd>0


def test_broker_margin_and_spread_rejections():
    cfg=BrokerConfig(name='dukascopy',initial_balance=100,leverage=2,max_spread_price=0.2,
                     order_latency_ms=0)
    sim=Replay(cfg,Once(),(5,15,))
    sim.on_quote(Quote(1767308400000,100,100.1,'dukascopy'))
    sim.on_quote(Quote(1767308401000,100,100.4,'dukascopy'))
    assert sim.rejections['spread']==1
    assert not sim.trades


def test_output_checkpoint_guard(tmp_path):
    src=gz(tmp_path,'test.csv.gz','time,time_msc,bid,ask,last,volume,volume_real,flags\n1767315600,1767315600000,100,100.2,0,0,0,134\n')
    out=tmp_path/'output.json'
    main(['--broker','coinexx','--input',str(src),'--output',str(out),'--allow-unregistered-input'])
    data=json.loads(out.read_text());assert data['source']['quality']['total']==1
    with pytest.raises(SystemExit,match='output exists'):
        main(['--broker','coinexx','--input',str(src),'--output',str(out),'--allow-unregistered-input'])


def test_insufficient_margin_denies_order():
    cfg=BrokerConfig(name='coinexx',initial_balance=100,leverage=0.5,
                     max_spread_price=1,order_latency_ms=0)
    sim=Replay(cfg,Once(),(5,15))
    sim.on_quote(Quote(1767315600000,100,100.1,'coinexx'))
    sim.on_quote(Quote(1767315601000,100,100.1,'coinexx'))
    assert sim.rejections['insufficient_margin']==1
    assert sim.position is None


def test_short_entry_on_bid_and_exit_on_ask():
    class ShortOnce(Once):
        def on_tick(self,q,sim):
            if not self.done:
                sim.request_entry(-1,0.01,stop_distance=1.0);self.done=True
    sim=Replay(BrokerConfig(name='dukascopy',order_latency_ms=0),ShortOnce(),(5,15))
    sim.on_quote(Quote(1767308400000,100.0,100.2,'dukascopy'))
    sim.on_quote(Quote(1767308400100,99.9,100.1,'dukascopy'))
    assert sim.position.entry==99.9
    sim.on_quote(Quote(1767308400200,100.9,101.0,'dukascopy'))
    assert sim.trades[0]['exit_price']==101.0
    assert sim.trades[0]['net_pnl']==pytest.approx(-1.1)


def test_completed_bar_aggregates_no_future_ticks():
    bars=CandleStream((5,15,45,60))
    start=1767315600000
    outputs=[]
    for sec in range(0,65):
        outputs.extend(bars.update(Quote(start+sec*1000,100+sec/100,101+sec/100,'coinexx')))
    out15=[b for b in outputs if b.seconds==15]
    out45=[b for b in outputs if b.seconds==45]
    assert len(out15)==4 and len(out45)==1
    assert out15[0].ticks==15 and out15[0].bid_close==pytest.approx(100.14)
    assert out45[0].ticks==45 and out45[0].bid_close==pytest.approx(100.44)
    assert all(b.end_ms<=start+64000 for b in outputs)


def test_unregistered_source_rejected(tmp_path):
    src=gz(tmp_path,'unregistered.csv.gz','time,time_msc,bid,ask,last,volume,volume_real,flags\n1767315600,1767315600000,100,100.2,0,0,0,134\n')
    out=tmp_path/'report.json'
    with pytest.raises(SystemExit,match='source absent'):
        main(['--broker','coinexx','--input',str(src),'--output',str(out)])
    assert not out.exists()


def test_corrupted_registered_bytes_fail_sha():
    from htf_ticklab.source_registry import REGISTERED,verify
    name='XAUUSD_DUKAS_2026_01_ticks.csv.gz'
    assert verify(name,'dukascopy',REGISTERED[name].sha256) is not None
    with pytest.raises(ValueError,match='SHA-256 MISMATCH'):
        verify(name,'dukascopy','0'*64)


def test_period_metrics_and_trade_ledger(tmp_path):
    src=gz(tmp_path,'fixture.csv.gz','time,time_msc,bid,ask,last,volume,volume_real,flags\n1767315600,1767315600000,100,100.2,0,0,0,134\n')
    out=tmp_path/'out.json'
    main(['--broker','coinexx','--input',str(src),'--output',str(out),'--allow-unregistered-input'])
    data=json.loads(out.read_text())
    assert data['source']['source_verified'] is False
    assert data['trade_ledger_sha256']
    assert out.with_name('out_trades.csv').exists()
    assert data['periods']['hour']==[]
