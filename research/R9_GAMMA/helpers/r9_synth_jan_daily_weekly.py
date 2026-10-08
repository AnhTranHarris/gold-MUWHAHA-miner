import zipfile, datetime as dt, json, hashlib, os, statistics
import xml.etree.ElementTree as ET
from lxml import etree
from collections import defaultdict

NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
XLSX='/mnt/data/ReportTester-871471_jan2026_jul2026_R9_ticklog_synth(4).xlsx'
OUT='/mnt/data/gamma02_jan_repro/r9_synth_jan_daily_weekly.json'

def summarize(rows):
    pnl=[r['pnl'] for r in rows]
    gp=sum(x for x in pnl if x>0); gl=sum(x for x in pnl if x<0)
    bal=peak=dd=0.0
    for x in pnl:
        bal+=x; peak=max(peak,bal); dd=max(dd,peak-bal)
    holds=[r['hold_s'] for r in rows]
    return {
        'net':sum(pnl),'trades':len(pnl),'gross_profit':gp,'gross_loss':gl,
        'pf': gp/(-gl) if gl<0 else 999.0,
        'wins':sum(x>0 for x in pnl),'losses':sum(x<0 for x in pnl),'breakeven':sum(x==0 for x in pnl),
        'win':sum(x>0 for x in pnl)/len(pnl) if pnl else 0.0,
        'expectancy':sum(pnl)/len(pnl) if pnl else 0.0,
        'avg_hold_s':sum(holds)/len(holds) if holds else 0.0,
        'balance_dd':dd,
    }

sha=hashlib.sha256(open(XLSX,'rb').read()).hexdigest()
tr=[]; entry=None
with zipfile.ZipFile(XLSX) as z:
    root=ET.parse(z.open('xl/sharedStrings.xml')).getroot()
    ss=[''.join(t.text or '' for t in si.iter(NS+'t')) for si in root.findall(NS+'si')]
    with z.open('xl/worksheets/sheet1.xml') as f:
        for _,row in etree.iterparse(f,events=('end',),tag=NS+'row',huge_tree=True):
            rn=int(row.get('r'))
            if rn<438783:
                row.clear()
                while row.getprevious() is not None: del row.getparent()[0]
                continue
            vals={}
            for c in row:
                if c.tag!=NS+'c': continue
                ref=c.get('r'); col=''.join(ch for ch in ref if ch.isalpha())
                if col not in {'A','D','E','I','J','K'}: continue
                v=c.find(NS+'v'); raw='' if v is None else v.text
                if c.get('t')=='s' and raw!='': raw=ss[int(raw)]
                vals[col]=raw
            tm=vals.get('A','')
            if tm.startswith('2026.02.'): break
            if vals.get('E')=='in':
                entry=(tm,vals.get('D',''),float(vals.get('I') or 0),float(vals.get('J') or 0))
            elif vals.get('E')=='out' and entry:
                p=float(vals.get('K') or 0)+entry[2]+entry[3]+float(vals.get('I') or 0)+float(vals.get('J') or 0)
                ot=dt.datetime.strptime(entry[0],'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
                xt=dt.datetime.strptime(tm,'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
                tr.append({'entry':entry[0],'exit':tm,'side':entry[1],'pnl':p,'hold_s':(xt-ot).total_seconds()})
                entry=None
            row.clear()
            while row.getprevious() is not None: del row.getparent()[0]

by_day=defaultdict(list); by_week=defaultdict(list)
for r in tr:
    xt=dt.datetime.strptime(r['exit'],'%Y.%m.%d %H:%M:%S')
    by_day[xt.strftime('%Y-%m-%d')].append(r)
    y,w,_=xt.isocalendar(); by_week[f'{y}-W{w:02d}'].append(r)
obj={
    'source':os.path.basename(XLSX),'source_sha256':sha,'period':'January 2026 exits',
    'month':summarize(tr),
    'daily':{k:summarize(v) for k,v in sorted(by_day.items())},
    'weekly':{k:summarize(v) for k,v in sorted(by_week.items())},
}
with open(OUT,'w') as f: json.dump(obj,f,indent=2)
print(json.dumps(obj,indent=2))