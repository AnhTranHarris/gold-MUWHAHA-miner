# Extract exact January trade metrics from the authoritative MT5 R9 SYNTH .xlsx
# Uses streaming OOXML because full workbook import is >1 GB uncompressed.
import zipfile,datetime as dt,json,statistics,hashlib,os
import xml.etree.ElementTree as ET
from lxml import etree
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def extract(path,out):
    sha=hashlib.sha256(open(path,'rb').read()).hexdigest();tr=[];entry=None
    with zipfile.ZipFile(path) as z:
        root=ET.parse(z.open('xl/sharedStrings.xml')).getroot()
        ss=[''.join(t.text or '' for t in si.iter(NS+'t')) for si in root.findall(NS+'si')]
        with z.open('xl/worksheets/sheet1.xml') as f:
            for _,row in etree.iterparse(f,events=('end',),tag=NS+'row',huge_tree=True):
                rn=int(row.get('r'))
                if rn<438783:
                    row.clear()
                    while row.getprevious() is not None:del row.getparent()[0]
                    continue
                vals={}
                for c in row:
                    if c.tag!=NS+'c':continue
                    col=c.get('r')[0]
                    if col not in 'ADEIJK':continue
                    v=c.find(NS+'v');raw='' if v is None else v.text
                    if c.get('t')=='s' and raw!='':raw=ss[int(raw)]
                    vals[col]=raw
                tm=vals.get('A','')
                if tm.startswith('2026.02.'):break
                if vals.get('E')=='in':
                    entry=(tm,vals.get('D',''),float(vals.get('I') or 0),float(vals.get('J') or 0))
                elif vals.get('E')=='out' and entry:
                    p=float(vals.get('K') or 0)+entry[2]+entry[3]+float(vals.get('I') or 0)+float(vals.get('J') or 0)
                    ot=dt.datetime.strptime(entry[0],'%Y.%m.%d %H:%M:%S');xt=dt.datetime.strptime(tm,'%Y.%m.%d %H:%M:%S')
                    tr.append((p,(xt-ot).total_seconds(),entry[1]));entry=None
                row.clear()
                while row.getprevious() is not None:del row.getparent()[0]
    n=[x[0] for x in tr];w=[x for x in n if x>0];l=[x for x in n if x<0];h=[x[1] for x in tr]
    bal=peak=dd=0.
    for p in n:bal+=p;peak=max(peak,bal);dd=max(dd,peak-bal)
    obj=dict(candidate='GAMMA02_JAN_R9_SYNTH_BENCHMARK_029',source_file=os.path.basename(path),source_sha256=sha,
      net=sum(n),gross_profit=sum(w),gross_loss=sum(l),profit_factor=sum(w)/-sum(l),trades=len(n),wins=len(w),losses=len(l),
      breakeven=len(n)-len(w)-len(l),win_rate_strict_positive=len(w)/len(n),expectancy=sum(n)/len(n),
      average_winner=sum(w)/len(w),average_loser=sum(l)/len(l),largest_win=max(n),largest_loss=min(n),
      closed_trade_balance_dd=dd,avg_hold_s=sum(h)/len(h),median_hold_s=statistics.median(h),min_hold_s=min(h),max_hold_s=max(h))
    open(out,'w').write(json.dumps(obj,indent=2));print(json.dumps(obj,indent=2))
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('xlsx');a.add_argument('--out',required=True);z=a.parse_args();extract(z.xlsx,z.out)
