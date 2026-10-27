from pathlib import Path
import pytest
from r34_demo_shadow_bridge import (DemoShadowBridge,PendingIntent,NativeQuote,OriginalR17Packet,
                                   R17_ARCHIVE_SHA,ContractError)
ROOT=Path(__file__).parent
T=1_780_000_000_000

def setup(broker='coinexx'):
 g=DemoShadowBridge(ROOT,broker=broker)
 i=PendingIntent(intent_id='A01',broker=broker,symbol='XAUUSD',account_mode='DEMO',t0_msc=T,side=1)
 g.add_intent(i)
 q=NativeQuote(broker=broker,time_msc=T+15002,ordinal=44,bid=4500.,ask=4500.25,source_registered=True)
 g.ingest_native_quote(q)
 p=OriginalR17Packet(broker=broker,intent_id='A01',feature_asof_msc=q.time_msc,
   source_quote_ordinal=q.ordinal,source_sha256=R17_ARCHIVE_SHA,source_prefix_verified=True,
   published_htf_bars_verified=True,prior_labels_matured_asof_verified=True,
   base_r16=False,opposite=.6,neutral=.3,right_guard=.25)
 return g,i,q,p
@pytest.mark.parametrize('broker',['coinexx','dukascopy'])
def test_real_original_frozen_weight_inference_both_brokers(broker):
 g,_,_,p=setup(broker);a=g.evaluate('A01',asof_source=p,order_currently_filled=False)
 assert a['action'] in ('SHADOW_WOULD_VETO','SHADOW_WOULD_RELEASE')
 assert not a['veto_is_effective_on_broker'] and not a['has_order_send']
@pytest.mark.parametrize('broker',['coinexx','dukascopy'])
def test_filled_position_immutable(broker):
 g,_,_,p=setup(broker);a=g.evaluate('A01',asof_source=p,order_currently_filled=True)
 assert a['action']=='ORIGINAL_FILLED_OR_NOT_PENDING_IMMUTABLE'
@pytest.mark.parametrize('broker',['coinexx','dukascopy'])
def test_status_must_be_new_pending_unfilled(broker):
 g,_,_,p=setup(broker);a=g.evaluate('A01',asof_source=p,order_currently_filled=False,order_terminal_status='FILLED')
 assert a['action']=='ORIGINAL_FILLED_OR_NOT_PENDING_IMMUTABLE'
@pytest.mark.parametrize('change',['source_sha256','source_prefix_verified','published_htf_bars_verified','prior_labels_matured_asof_verified','feature_asof_msc','source_quote_ordinal','broker','intent_id'])
def test_unverified_source_and_future_quote_abstain(change):
 from dataclasses import replace
 g,_,q,p=setup()
 kwargs={'source_sha256':'BAD','source_prefix_verified':False,'published_htf_bars_verified':False,
 'prior_labels_matured_asof_verified':False,'feature_asof_msc':q.time_msc+1,'source_quote_ordinal':q.ordinal+1,
 'broker':'dukascopy','intent_id':'different'}
 a=g.evaluate('A01',asof_source=replace(p,**{change:kwargs[change]}),order_currently_filled=False)
 assert a['action']=='UPSTREAM_R17_ASOF_SOURCE_UNVERIFIED__NO_FILTER_ACTION'
@pytest.mark.parametrize('broker',['coinexx','dukascopy'])
def test_no_genuine_quote_abstain(broker):
 g,_,_,p=setup(broker)
 g.first_quote.clear()
 assert g.evaluate('A01',asof_source=p,order_currently_filled=False)['action']=='NO_T15_GENUINE_QUOTE__NO_FILTER_ACTION'
@pytest.mark.parametrize('wrong_quote',[(14999,43),(16000,43)])
def test_outside_quote_not_counted(wrong_quote):
 g=DemoShadowBridge(ROOT,broker='coinexx');g.add_intent(PendingIntent('A01','coinexx','XAUUSD','DEMO',T,1))
 off,ordinal=wrong_quote
 g.ingest_native_quote(NativeQuote('coinexx',T+off,ordinal,4500,4501,True))
 assert 'A01' not in g.first_quote
@pytest.mark.parametrize('mode',['LIVE','REAL','CONTEST'])
def test_live_mode_rejected(mode):
 g=DemoShadowBridge(ROOT,broker='coinexx')
 with pytest.raises(ContractError):g.add_intent(PendingIntent('A01','coinexx','XAUUSD',mode,T,1))
def test_replayed_quote_same_millisecond_rejected():
 g,_,q,p=setup()
 with pytest.raises(ContractError):g.ingest_native_quote(q)
def test_wrong_broker_on_quote_rejected():
 g,_,q,p=setup()
 from dataclasses import replace
 with pytest.raises(ContractError):g.ingest_native_quote(replace(q,broker='dukascopy'))
def test_wrong_broker_intent_rejected():
 g=DemoShadowBridge(ROOT,broker='coinexx')
 with pytest.raises(ContractError):g.add_intent(PendingIntent('A01','dukascopy','XAUUSD','DEMO',T,1))
def test_source_quote_capture_first_not_later():
 g,_,q,p=setup()
 g.ingest_native_quote(NativeQuote('coinexx',T+15040,45,4500.1,4500.2,True))
 assert g.first_quote['A01'].ordinal==44
