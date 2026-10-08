import zipfile, datetime as dt, json, statistics, hashlib, os
import xml.etree.ElementTree as ET
from lxml import etree
from collections import defaultdict
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
SRC='/mnt/data/ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx'
OUT='/mnt/data/gamma02_jan_repro/r9_synth_feb_daily_weekly.json'

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for ch in iter(lambda:f.read(8*1024*1024),b''): h.update(ch)
    return h.hexdigest()

def stats(rows):
    p=[x['pnl'] for x in rows]; h=[x['hold_s'] for x in rows]
    w=[x for x in p if x>0]; l=[x for x in p if x<0]
    bal=peak=dd=0.0
    for v in p:
        bal += v; peak=max(peak,bal); dd=max(dd,peak-bal)
    gp=sum(w); gl=sum(l)
    return dict(net=sum(p),trades=len(p),gross_profit=gp,gross_loss=gl,
                pf=(gp/-gl if gl<0 else 999.0),wins=len(w),losses=len(l),breakeven=len(p)-len(w)-len(l),
                win=(len(w)/len(p) if p else 0.0),expectancy=(sum(p)/len(p) if p else 0.0),
                avg_hold_s=(sum(h)/len(h) if h else 0.0),balance_dd=dd)

def main():
    sha=sha256_file(SRC); trades=[]; entry=None
    feb_start=dt.datetime(2026,2,1); mar_start=dt.datetime(2026,3,1)
    with zipfile.ZipFile(SRC) as z:
        root=ET.parse(z.open('xl/sharedStrings.xml')).getroot()
        ss=[''.join(t.text or '' for t in si.iter(NS+'t')) for si in root.findall(NS+'si')]
        with z.open('xl/worksheets/sheet1.xml') as f:
            for _,row in etree.iterparse(f,events=('end',),tag=NS+'row',huge_tree=True):
                rn=int(row.get('r'))
                # trade-history section begins around this row in this exact authority workbook
                if rn<438783:
                    row.clear()
                    while row.getprevious() is not None: del row.getparent()[0]
                    continue
                vals={}
                for c in row:
                    if c.tag!=NS+'c': continue
                    col=''.join(ch for ch in c.get('r') if ch.isalpha())
                    if col not in ('A','D','E','I','J','K'): continue
                    v=c.find(NS+'v'); raw='' if v is None else (v.text or '')
                    if c.get('t')=='s' and raw!='': raw=ss[int(raw)]
                    vals[col]=raw
                tm=vals.get('A','')
                if tm.startswith('2026.03.'):
                    row.clear(); break
                typ=vals.get('E','')
                if typ=='in' and tm.startswith(('2026.01.','2026.02.')):
                    entry=(tm,vals.get('D',''),float(vals.get('I') or 0),float(vals.get('J') or 0))
                elif typ=='out' and entry and tm.startswith('2026.02.'):
                    p=float(vals.get('K') or 0)+entry[2]+entry[3]+float(vals.get('I') or 0)+float(vals.get('J') or 0)
                    ot=dt.datetime.strptime(entry[0],'%Y.%m.%d %H:%M:%S'); xt=dt.datetime.strptime(tm,'%Y.%m.%d %H:%M:%S')
                    trades.append({'entry':entry[0],'exit':tm,'pnl':p,'hold_s':(xt-ot).total_seconds(),'side':entry[1]})
                    entry=None
                elif typ=='out' and entry:
                    entry=None
                row.clear()
                while row.getprevious() is not None: del row.getparent()[0]
    daily=defaultdict(list); weekly=defaultdict(list)
    for tr in trades:
        x=dt.datetime.strptime(tr['exit'],'%Y.%m.%d %H:%M:%S')
        daily[x.date().isoformat()].append(tr)
        iso=x.isocalendar(); weekly[f'{iso.year}-W{iso.week:02d}'].append(tr)
    obj={
      'source':os.path.basename(SRC),'source_sha256':sha,'period':'February 2026 exits',
      'month':stats(trades),
      'daily':{k:stats(v) for k,v in sorted(daily.items())},
      'weekly':{k:stats(v) for k,v in sorted(weekly.items())}
    }
    with open(OUT,'w') as f: json.dump(obj,f,indent=2)
    print(json.dumps(obj,indent=2))
if __name__=='__main__': main()