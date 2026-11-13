from __future__ import annotations
import csv
import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO
from .models import Tick, parse_price_units

BROKER_REQUIRED = ("time", "time_msc", "bid", "ask", "last", "volume", "volume_real", "flags")
LOGGER_REQUIRED = ("time_msc", "time", "bid", "ask", "last", "tick_volume", "volume_real", "flags")

class DataIntegrityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TickFileVerification:
    schema: str
    rows: int
    first_time_msc: int | None
    last_time_msc: int | None
    same_millisecond_adjacent_rows: int


def _open_text(path: str | Path) -> TextIO:
    p = Path(path)
    if p.suffix.lower() == ".gz":
        return gzip.open(p, "rt", encoding="utf-8-sig", newline="")
    return p.open("r", encoding="utf-8-sig", newline="")


def detect_schema(fieldnames: list[str] | None) -> str:
    names = tuple(fieldnames or ())
    if all(x in names for x in BROKER_REQUIRED):
        return "broker_export"
    if all(x in names for x in LOGGER_REQUIRED):
        return "r9_tick_logger"
    raise DataIntegrityError(f"Unsupported Coinexx tick schema: {names}")


def _column_map(header: list[str]) -> tuple[str, dict[str, int]]:
    schema = detect_schema(header)
    pos = {name: i for i, name in enumerate(header)}
    return schema, pos


def verify_coinexx_tick_file(path: str | Path, *, strict: bool = True) -> TickFileVerification:
    """Fast full-file source validation without constructing millions of Tick objects.

    This pass still parses every market row and validates the same chronology and quote
    invariants as :func:`iter_coinexx_ticks`. It does not sort, aggregate, sample, or
    deduplicate. Equal millisecond timestamps are counted and left in source order.
    """
    rows = 0
    first: int | None = None
    last: int | None = None
    same_msc = 0
    prev = -1
    with _open_text(path) as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise DataIntegrityError("empty Coinexx tick file") from exc
        schema, pos = _column_map(header)
        required_max = max(pos[k] for k in (BROKER_REQUIRED if schema == "broker_export" else LOGGER_REQUIRED))
        for ordinal, row in enumerate(reader, start=1):
            if len(row) <= required_max:
                raise DataIntegrityError(f"row {ordinal}: truncated row has {len(row)} columns")
            try:
                time_s = int(row[pos["time"]])
                time_msc = int(row[pos["time_msc"]])
                bid_u = parse_price_units(row[pos["bid"]])
                ask_u = parse_price_units(row[pos["ask"]])
                parse_price_units(row[pos["last"]] or "0")
                volume_key = "volume" if schema == "broker_export" else "tick_volume"
                int(float(row[pos[volume_key]] or "0"))
                volume_real_text = row[pos["volume_real"]] or "0"
                float(volume_real_text)  # numeric validation only; exact source text is retained below.
                int(row[pos["flags"]] or "0")
            except (TypeError, ValueError, IndexError) as exc:
                raise DataIntegrityError(f"row {ordinal}: invalid numeric field: {exc}") from exc
            if time_msc < prev:
                raise DataIntegrityError(f"row {ordinal}: nonmonotonic time_msc {time_msc} < {prev}")
            if time_s != time_msc // 1000:
                raise DataIntegrityError(f"row {ordinal}: time/time_msc mismatch {time_s} != {time_msc // 1000}")
            if bid_u <= 0 or ask_u <= 0 or ask_u < bid_u:
                if strict:
                    raise DataIntegrityError(
                        f"row {ordinal}: invalid quote bid={row[pos['bid']]} ask={row[pos['ask']]}"
                    )
            if first is None:
                first = time_msc
            if prev == time_msc:
                same_msc += 1
            prev = time_msc
            last = time_msc
            rows += 1
    return TickFileVerification(schema, rows, first, last, same_msc)


def iter_coinexx_ticks(
    path: str | Path,
    *,
    preserve_logger_extras: bool = False,
    strict: bool = True,
    ordinal_offset: int = 0,
) -> Iterator[Tick]:
    """Stream Coinexx ticks in exact file order.

    The iterator never sorts and never deduplicates. Equal time_msc values are legal and
    remain ordered by source row. A backward timestamp is always fatal. In strict mode,
    malformed or crossed quotes are fatal instead of being silently discarded.
    """
    with _open_text(path) as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise DataIntegrityError("empty Coinexx tick file") from exc
        schema, pos = _column_map(header)
        prev_msc = -1
        volume_key = "volume" if schema == "broker_export" else "tick_volume"
        extras_names = ()
        if preserve_logger_extras and schema == "r9_tick_logger":
            market_fields = set(LOGGER_REQUIRED)
            extras_names = tuple((i, name) for i, name in enumerate(header) if name not in market_fields)
        required_max = max(pos[k] for k in (BROKER_REQUIRED if schema == "broker_export" else LOGGER_REQUIRED))
        for local_ordinal, row in enumerate(reader, start=1):
            ordinal = ordinal_offset + local_ordinal
            if len(row) <= required_max:
                raise DataIntegrityError(f"row {ordinal}: truncated row has {len(row)} columns")
            try:
                time_msc = int(row[pos["time_msc"]])
                time_s = int(row[pos["time"]])
                bid_u = parse_price_units(row[pos["bid"]])
                ask_u = parse_price_units(row[pos["ask"]])
                last_u = parse_price_units(row[pos["last"]] or "0")
                volume = int(float(row[pos[volume_key]] or "0"))
                volume_real = row[pos["volume_real"]] or "0"
                float(volume_real)  # numeric validation without replacing the source representation.
                flags = int(row[pos["flags"]] or "0")
            except (TypeError, ValueError, IndexError) as exc:
                raise DataIntegrityError(f"row {ordinal}: invalid numeric field: {exc}") from exc

            if time_msc < prev_msc:
                raise DataIntegrityError(
                    f"row {ordinal}: nonmonotonic time_msc {time_msc} < {prev_msc}"
                )
            if time_s != time_msc // 1000:
                raise DataIntegrityError(
                    f"row {ordinal}: time/time_msc mismatch {time_s} != {time_msc // 1000}"
                )
            if bid_u <= 0 or ask_u <= 0 or ask_u < bid_u:
                msg = f"row {ordinal}: invalid quote bid={row[pos['bid']]} ask={row[pos['ask']]}"
                if strict:
                    raise DataIntegrityError(msg)
                prev_msc = time_msc
                continue

            extras = {name: row[i] if i < len(row) else "" for i, name in extras_names}
            yield Tick(
                ordinal=ordinal,
                time_s=time_s,
                time_msc=time_msc,
                bid_u=bid_u,
                ask_u=ask_u,
                last_u=last_u,
                volume=volume,
                volume_real=volume_real,
                flags=flags,
                source_extras=extras,
            )
            prev_msc = time_msc
