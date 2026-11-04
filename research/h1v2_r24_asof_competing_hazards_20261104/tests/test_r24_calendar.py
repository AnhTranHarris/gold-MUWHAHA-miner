import sys, tempfile, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'calendar'))
from r24_mt5_calendar_contract import *

def test_missing_calendar_fails_closed():
 try:normalize_economic_calendar('/tmp/nope_status.tsv','/tmp/nope_events.tsv','/tmp/nope_offsets.tsv')
 except FileNotFoundError:pass
 else:raise AssertionError('must not create missing news=0')
 assert calendar_quarter_diagnostic(None,0)['impact_state']=='UNKNOWN_UNVERIFIED_MT5_EXPORT'

def test_status_incomplete_rejected():
 with tempfile.TemporaryDirectory() as d:
  p=pathlib.Path(d)/'STATUS.tsv';p.write_text('key\tvalue\ncalendar_export_status\tINCOMPLETE_PROVIDER_ERROR_FAIL_CLOSED\n')
  try:normalize_economic_calendar(p,'none','none')
  except CalendarSourceUnavailable:pass
  else:raise AssertionError('no false complete')

def test_observed_server_dst_mapping_requires_exact_source_offset():
 with tempfile.TemporaryDirectory() as z:
  p=pathlib.Path(z)
  status=p/'s.tsv';status.write_text('key\tvalue\nresearch_contract\tR24_PRESERVATION_ONLY_NOT_EXECUTABLE_TRADING_POLICY\nhistorical_schedule_asof_revisions\tUNKNOWN_PROVIDER_DB_CAN_BE_RETROSPECTIVE\ncalendar_export_status\tCOMPLETE_RETROSPECTIVE_METADATA_UNVERIFIED_POINT_IN_TIME\n')
  off=p/'offset.tsv';off.write_text('start_server\tend_server\tutc_offset_seconds\tevidence_sha256\n2026.01.01 00:00:00\t2026.02.01 00:00:00\t7200\t'+'a'*64+'\n')
  events=p/'event.tsv';events.write_text('currency_filter\tcalendar_value_id\tevent_id\tserver_scheduled_time\tevent_importance\tevent_time_mode\tevent_name\nUSD\t123\t44\t2026.01.12 16:00:00\tCALENDAR_IMPORTANCE_HIGH\tCALENDAR_TIMEMODE_DATETIME\tTest\n')
  v=normalize_economic_calendar(status,events,off)
  assert len(v)==1 and v[0]['scheduled_utc']=='2026-01-12T14:00:00+00:00'
  assert not v[0]['model_asof_news_feature_admissible']
