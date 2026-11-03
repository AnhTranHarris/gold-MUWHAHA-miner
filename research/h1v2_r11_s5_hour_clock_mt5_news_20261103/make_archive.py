from __future__ import annotations
from pathlib import Path
import hashlib,json,zipfile,csv,io,sys
ROOT=Path('/mnt/data/r11s5_work')
SOURCE=Path('/mnt/data')
ARCHIVE=ROOT/'R11S5_FOUR_MONTH_2880_HOUR_120_DAY_SESSIONS_NEWS_SOURCE_EXACT_20261103.zip'
files={}
for p in sorted((ROOT/'src').glob('*.py')):files['src/'+p.name]=p
for p in sorted((ROOT/'tests').glob('test_*.py')):files['tests/'+p.name]=p
for p in sorted((ROOT/'mql5').glob('*.mq5')):files['mql5/'+p.name]=p
for p in sorted((ROOT/'outputs').rglob('*')):
    if p.is_file():files['outputs/'+p.relative_to(ROOT/'outputs').as_posix()]=p
files['FULL_SOURCE_EXACT_REPRODUCTION_CONTRACT.md']=ROOT/'FULL_SOURCE_EXACT_REPRODUCTION_CONTRACT.md'
for p in ['R11S4_ALL_2880_COMPLETE_UTC_HOURLY_SOURCE_QUOTA_RESULTS.csv',
          'R11S4_ALL_120_COMPLETE_UTC_DAILY_SOURCE_QUOTA_RESULTS.csv',
          'R11S4_ALL_246_ABSOLUTELY_IMPOSSIBLE_ORIGINAL_HOURLY_R9_QUOTA_WITNESSES.csv',
          'R11S4_ALL_14_ABSOLUTELY_IMPOSSIBLE_ORIGINAL_DAILY_R9_QUOTA_WITNESSES.csv']:
    files['original_input_readonly/'+p]=SOURCE/p
sha=lambda data:hashlib.sha256(data).hexdigest()
members={}
for arc,p in files.items():
    b=p.read_bytes()
    members[arc]={'sha256':sha(b),'bytes':len(b)}
manifest={
 'scientific_status':'COMPLETE_ALL_2880_HOUR_CONTEXT_JOIN;_NO_NEWS_SOURCE;_NO_FRESH_CAUSAL_TICK_MODEL_FIT',
 'owner_goal':'four independent 2026 source months, every day 24h, per-hour highest safe initial 15s/30s entry hindsight against R9 hourly source quotas',
 'run_source_parent':'carson/h1v2-r11-s4-exact-optimal-hour-day-month-20261103 SHA 897ae6217874296fbc065089e5e138a0ec0bb43b',
 'historical_r9_v2_src_sha':'ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0',
 'original_hour_csv_sha':'cfabfecd9ea57d05d806eb16922f20789e0ea75a77111785d0de565fc6c64542',
 'original_day_csv_sha':'300fddb83b563e439b2006957513242c3b732ba60495d176222b001475e6557a',
 'tested_commands':['PYTHONPATH=src pytest -q tests  # 15 PASSED','python -m compileall -q src tests # PASS',
                    'PYTHONPATH=src python -u src/run_hourly_clock.py --months 2026-01 2026-02 2026-06 2026-07 --out outputs'],
 'checks':{'monthly_hour_counts':{'2026-01':744,'2026-02':672,'2026-06':720,'2026-07':744},
           'monthly_day_counts':{'2026-01':31,'2026-02':28,'2026-06':30,'2026-07':31},
           'hour_rows':2880,'day_chunks':120,'reported_strict_hindsight_15fav30safe':145401,
           'r9_active_utc_hours':1917,'hour_mathematically_impossible_under_immutable_contract':246,
           'mt5_news_events_joined':None,'actual_broker_trade_permission':'UNKNOWN_NOT_EXPORTED',
           'mql5_compiled_on_terminal':False},
 'next_task':'Owner runs MQL5 calendar export once per exact server-time historical month; supply verified broker offset calendar, then re-run NEWS join; no fabricated calendar events and no prior-model overwrite.',
 'number_of_member_files':len(members),
 'members':members}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for arc,p in files.items():
        zi=zipfile.ZipInfo(arc,date_time=(2026,11,3,12,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
    zi=zipfile.ZipInfo('COMPLETE_SHA256_MEMBER_MANIFEST.json',date_time=(2026,11,3,12,0,0))
    zi.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(zi,manifest_bytes,compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    rep=json.loads(z.read('COMPLETE_SHA256_MEMBER_MANIFEST.json'))
    assert set(z.namelist())==set(members)|{'COMPLETE_SHA256_MEMBER_MANIFEST.json'}
    for arc,m in rep['members'].items():
        b=z.read(arc)
        assert sha(b)==m['sha256'] and len(b)==m['bytes'],arc
    for mon,want in [('2026-01',744),('2026-02',672),('2026-06',720),('2026-07',744)]:
        path=f'outputs/{mon}/{mon}_ALL_HOURS_R11S5_CLOCK_AND_NEWS.csv'
        rows=list(csv.DictReader(io.StringIO(z.read(path).decode())))
        assert len(rows)==want
        assert all(x['mt5_high_events_in_hour']=='UNKNOWN' for x in rows)
print(json.dumps({'archive':str(ARCHIVE),'outer_sha256':sha(ARCHIVE.read_bytes()),'bytes':ARCHIVE.stat().st_size,
     'member_count':len(members)+1,'exact_member_sha_verified':len(members),'crc':'PASS',
     'original_4month_source_records':'PRESERVED_WITHOUT_MODIFICATION',
     'all_2880_original_hour_rows':'PRESERVED_WITH_ADDED_DST_CLOCK_AND_EXPLICIT_NEWS_UNKNOWN',
     'all_120_day_chunks':'PRESERVED'},indent=2))
