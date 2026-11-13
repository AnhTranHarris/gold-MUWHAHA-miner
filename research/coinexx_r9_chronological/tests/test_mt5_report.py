import tempfile, unittest, zipfile
from pathlib import Path
from coinexx_r9.mt5_report import extract_trade_sections

class Mt5ReportTests(unittest.TestCase):
    def test_streams_all_order_and_deal_rows_in_source_order(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);root=Path(td.name);p=root/'r.xlsx'
        shared=['Orders','2026.01.02 01:00:00','Deals','XAUUSD','buy','in','out']
        ss='''<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'''+''.join(f'<si><t>{x}</t></si>' for x in shared)+'</sst>'
        sheet='''<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
        <row r="1"><c r="A1" t="s"><v>0</v></c></row>
        <row r="2"><c r="A2" t="s"><v>1</v></c><c r="C2" t="s"><v>3</v></c><c r="D2" t="s"><v>4</v></c></row>
        <row r="3"><c r="A3" t="s"><v>2</v></c></row>
        <row r="4"><c r="A4" t="s"><v>1</v></c><c r="C4" t="s"><v>3</v></c><c r="D4" t="s"><v>4</v></c><c r="E4" t="s"><v>5</v></c></row>
        <row r="5"><c r="A5" t="s"><v>1</v></c><c r="C5" t="s"><v>3</v></c><c r="D5" t="s"><v>4</v></c><c r="E5" t="s"><v>6</v></c></row>
        </sheetData></worksheet>'''
        with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('xl/sharedStrings.xml',ss);z.writestr('xl/worksheets/sheet1.xml',sheet)
        o=root/'orders.csv';d=root/'deals.csv';oc,dc=extract_trade_sections(p,o,d)
        self.assertEqual((oc,dc),(1,2))
        self.assertEqual(o.read_text().splitlines()[1].split(',')[0],'2')
        self.assertEqual([x.split(',')[0] for x in d.read_text().splitlines()[1:]],['4','5'])
