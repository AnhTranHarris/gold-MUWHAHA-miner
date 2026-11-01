#!/usr/bin/env python3
"""Repair DEV teacher labels for Duka UTC -> Coinexx broker-native minute.
Prices, features, prices, and outcomes remain bit-for-bit except teacher column.
Teacher is privileged training-only. Retain a no-overwrite safety copy.
"""
import csv,datetime as dt,gzip,os,shutil,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from four_month_train import read_teacher

def fix(file,teacher):
    file=Path(file)
    assert file.name.startswith('dukascopy_')
    month=file.name.split('_')[1]
    offset=120 if month in ('01','02') else 180
    backup=file.with_name(file.stem+'.teacher_clock_pre_repair.gz')
    if backup.exists():raise RuntimeError('backup exists; refusing second repair')
    shutil.copy2(file,backup)
    temp=file.with_name(file.name+'.repair.tmp')
    count=matches=0
    with gzip.open(backup,'rt',newline='') as f,gzip.open(temp,'wt',newline='') as out:
      reader=csv.DictReader(f);writer=csv.DictWriter(out,fieldnames=reader.fieldnames);writer.writeheader()
      for r in reader:
        broker=int(r['utc_ms'])+offset*60_000
        minute=dt.datetime.fromtimestamp(broker/1000,dt.timezone.utc).strftime('%Y.%m.%d %H:%M')
        flag=int(teacher.get((minute,int(r['side'])),0)>0)
        matches+=flag;count+=1;r['teacher']=flag
        writer.writerow(r)
    os.replace(temp,file)
    return {'file':file.name,'count':count,'teacher_matches_corrected':matches,'backup':backup.name}
if __name__=='__main__':
  teacher=read_teacher(sys.argv[1]);out=[]
  for path in sys.argv[2:]:out.append(fix(path,teacher))
  print(json.dumps(out,indent=2))
