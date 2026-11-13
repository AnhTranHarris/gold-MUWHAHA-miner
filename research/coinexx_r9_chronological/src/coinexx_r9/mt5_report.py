from __future__ import annotations
import csv
import html
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
ROW_RE = re.compile(r'<row\b([^>]*)>(.*?)</row>', re.S)
ROW_NUM_RE = re.compile(r'\br="(\d+)"')
CELL_RE = re.compile(r'<c\b([^>]*)>(.*?)</c>', re.S)
CELL_REF_RE = re.compile(r'\br="([A-Z]+)\d+"')
CELL_TYPE_RE = re.compile(r'\bt="([^"]+)"')
VALUE_RE = re.compile(r'<v>(.*?)</v>', re.S)
TEXT_RE = re.compile(r'<t(?:\s[^>]*)?>(.*?)</t>', re.S)
TRADE_TIME_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2} ")

class Mt5ReportError(ValueError):
    pass


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    out: list[str] = []
    try:
        fh = z.open("xl/sharedStrings.xml")
    except KeyError:
        return out
    with fh:
        for _, elem in ET.iterparse(fh, events=("end",)):
            if elem.tag == MAIN_NS + "si":
                out.append("".join(t.text or "" for t in elem.iter(MAIN_NS + "t")))
                elem.clear()
    return out


def _text_wrapper(binary_fh) -> io.TextIOWrapper:
    prefix = binary_fh.read(4)
    binary_fh.seek(0)
    if prefix.startswith(b"\xff\xfe"):
        enc = "utf-16le"
    elif prefix.startswith(b"\xfe\xff"):
        enc = "utf-16be"
    else:
        enc = "utf-8"
    return io.TextIOWrapper(binary_fh, encoding=enc, errors="strict", newline="")


def _decode_row(fragment: str, shared: list[str]) -> tuple[int, dict[str, str]] | None:
    m = ROW_RE.search(fragment)
    if not m:
        return None
    attrs, body = m.groups()
    rn = ROW_NUM_RE.search(attrs)
    if not rn:
        return None
    row_number = int(rn.group(1))
    cells: dict[str, str] = {}
    for cm in CELL_RE.finditer(body):
        cattrs, cbody = cm.groups()
        refm = CELL_REF_RE.search(cattrs)
        if not refm:
            continue
        col = refm.group(1)
        typem = CELL_TYPE_RE.search(cattrs)
        ctype = typem.group(1) if typem else ""
        vm = VALUE_RE.search(cbody)
        if ctype == "s":
            if not vm:
                continue
            idx = int(vm.group(1))
            if idx >= len(shared):
                raise Mt5ReportError(f"shared-string index {idx} out of range at {col}{row_number}")
            cells[col] = shared[idx]
        elif ctype == "inlineStr":
            tm = TEXT_RE.search(cbody)
            if tm:
                cells[col] = html.unescape(tm.group(1))
        elif vm:
            cells[col] = vm.group(1)
    return row_number, cells


def iter_sheet_rows(path: str | Path, *, chunk_chars: int = 2_000_000) -> Iterator[tuple[int, dict[str, str]]]:
    """Stream the first MT5 worksheet row-by-row without materializing its huge XML.

    MT5-generated XLSX reports can expand to >1 GB of UTF-16 worksheet XML. Parsing
    complete XML element trees is needlessly slow. This parser decodes bounded text
    chunks, retains an unfinished row across chunk boundaries, and yields each source
    row exactly once in worksheet order.
    """
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        with z.open("xl/worksheets/sheet1.xml") as raw:
            tf = _text_wrapper(raw)
            carry = ""
            while True:
                block = tf.read(chunk_chars)
                if not block:
                    break
                parts = (carry + block).split("</row>")
                carry = parts.pop()
                for part in parts:
                    start = part.rfind("<row")
                    if start < 0:
                        continue
                    decoded = _decode_row(part[start:] + "</row>", shared)
                    if decoded is not None:
                        yield decoded
            if "<row" in carry and "</row>" in carry:
                start = carry.rfind("<row")
                decoded = _decode_row(carry[start:], shared)
                if decoded is not None:
                    yield decoded


def iter_trade_sections(path: str | Path) -> Iterator[tuple[str, int, dict[str, str]]]:
    section: str | None = None
    for row_number, cells in iter_sheet_rows(path):
        a = cells.get("A", "")
        if a == "Orders":
            section = "orders"
            continue
        if a == "Deals":
            section = "deals"
            continue
        if section in ("orders", "deals") and TRADE_TIME_RE.match(a):
            yield section, row_number, cells


def extract_trade_sections(path: str | Path, orders_out: str | Path, deals_out: str | Path) -> tuple[int, int]:
    """Write ALL order/deal rows in source order. No date sampling or aggregation."""
    fields = list("ABCDEFGHIJKLMNO")
    orders_count = deals_count = 0
    with Path(orders_out).open("w", newline="", encoding="utf-8") as ofh, Path(deals_out).open("w", newline="", encoding="utf-8") as dfh:
        ow = csv.DictWriter(ofh, fieldnames=["source_row", *fields])
        dw = csv.DictWriter(dfh, fieldnames=["source_row", *fields])
        ow.writeheader(); dw.writeheader()
        for section, row_number, cells in iter_trade_sections(path):
            record = {"source_row": row_number, **{k: cells.get(k, "") for k in fields}}
            if section == "orders":
                ow.writerow(record); orders_count += 1
            else:
                dw.writerow(record); deals_count += 1
    return orders_count, deals_count
