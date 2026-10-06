from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Bounded DELTA-B event/microstructure correlation probe."
    )
    p.add_argument("--ticks", required=True, help="Dukascopy monthly .csv.gz")
    p.add_argument("--events", required=True, help="Frozen DELTA-B compact event CSV")
    p.add_argument("--start", required=True, help="UTC YYYY-MM-DDTHH:MM")
    p.add_argument("--end", required=True, help="UTC YYYY-MM-DDTHH:MM exclusive")
    p.add_argument("--window-min", type=int, default=30)
    p.add_argument("--release-min", type=int, default=5)
    p.add_argument("--control-start", default="12:30", help="UTC HH:MM")
    p.add_argument("--control-end", default="16:00", help="UTC HH:MM exclusive")
    p.add_argument("--out", required=True, help="JSON output")
    return p.parse_args()


def dt_utc(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)


def hhmm(s: str) -> int:
    h, m = map(int, s.split(":"))
    return h * 60 + m


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    vx = sum(x * x for x in dx)
    vy = sum(y * y for y in dy)
    if vx <= 0 or vy <= 0:
        return None
    return sum(x * y for x, y in zip(dx, dy)) / math.sqrt(vx * vy)


def load_events(path: str, start_ms: int, end_ms: int) -> list[tuple[int, int, str]]:
    out = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["currency"] != "USD" or row["impact"] not in {"Medium", "High"}:
                continue
            t = datetime.strptime(
                f"{row['date_gmt']} {row['time_gmt']}",
                "%a %b %d %Y %H:%M",
            ).replace(tzinfo=timezone.utc)
            ms = int(t.timestamp() * 1000)
            if start_ms - 3_600_000 <= ms < end_ms + 3_600_000:
                out.append((ms, 3 if row["impact"] == "High" else 2, row["event"]))
    out.sort()
    return out


def classify_minute(
    minute_ms: int,
    events: list[tuple[int, int, str]],
    window_min: int,
    release_min: int,
) -> tuple[int, str]:
    best_sev = 0
    best_phase = "NORMAL"
    phase_rank = {"NORMAL": 0, "PRE": 1, "POST": 2, "RELEASE": 3}
    for ems, sev, _ in events:
        d = (minute_ms - ems) / 60_000.0
        if -window_min <= d < 0:
            phase = "PRE"
        elif 0 <= d < release_min:
            phase = "RELEASE"
        elif release_min <= d <= window_min:
            phase = "POST"
        else:
            continue
        if sev > best_sev or (
            sev == best_sev and phase_rank[phase] > phase_rank[best_phase]
        ):
            best_sev = sev
            best_phase = phase
    return best_sev, best_phase


def summarize(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "mean": None, "median": None}
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "median": median(values),
    }


def main() -> int:
    ns = parse_args()
    start = dt_utc(ns.start)
    end = dt_utc(ns.end)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    control_start = hhmm(ns.control_start)
    control_end = hhmm(ns.control_end)
    events = load_events(ns.events, start_ms, end_ms)

    # minute -> [count, spread_sum, abs_path, first, last, min, max]
    minutes: dict[int, list[float]] = {}
    last_mid = None
    last_minute = None
    rows = 0

    with gzip.open(ns.ticks, "rt", newline="") as f:
        for row in csv.DictReader(f):
            ts = int(row["timestamp_ms_utc"])
            if ts < start_ms:
                continue
            if ts >= end_ms:
                break

            ask = int(row["ask_raw"]) / 1000.0
            bid = int(row["bid_raw"]) / 1000.0
            mid = (ask + bid) / 2.0
            spread = ask - bid
            minute = ts // 60_000

            a = minutes.get(minute)
            if a is None:
                a = minutes[minute] = [0, 0.0, 0.0, mid, mid, mid, mid]
            a[0] += 1
            a[1] += spread
            if last_mid is not None and last_minute == minute:
                a[2] += abs(mid - last_mid)
            a[4] = mid
            a[5] = min(a[5], mid)
            a[6] = max(a[6], mid)

            last_mid = mid
            last_minute = minute
            rows += 1

    records = []
    for minute, a in sorted(minutes.items()):
        dt = datetime.fromtimestamp(minute * 60, tz=timezone.utc)
        tod = dt.hour * 60 + dt.minute
        sev, phase = classify_minute(
            minute * 60_000,
            events,
            ns.window_min,
            ns.release_min,
        )
        count, spread_sum, abs_path, first, last, low, high = a
        records.append(
            {
                "severity": sev,
                "phase": phase,
                "core_control": control_start <= tod < control_end,
                "ticks": float(count),
                "avg_spread": spread_sum / count,
                "abs_path": abs_path,
                "range": high - low,
                "abs_disp": abs(last - first),
            }
        )

    metrics = ["ticks", "avg_spread", "abs_path", "range", "abs_disp"]
    core = [r for r in records if r["core_control"]]
    normal = [r for r in core if r["severity"] == 0]
    eventish = [r for r in core if r["severity"] > 0]

    comparison = {}
    for m in metrics:
        n = [r[m] for r in normal]
        e = [r[m] for r in eventish]
        nsum = summarize(n)
        esum = summarize(e)
        ratio = None
        if nsum["mean"] not in (None, 0) and esum["mean"] is not None:
            ratio = esum["mean"] / nsum["mean"]
        comparison[m] = {"normal": nsum, "event": esum, "mean_ratio": ratio}

    severity = [float(r["severity"]) for r in core]
    correlations = {
        m: pearson(severity, [r[m] for r in core])
        for m in metrics
    }

    phase_counts = defaultdict(int)
    for r in records:
        phase_counts[f"{r['severity']}:{r['phase']}"] += 1

    out = {
        "schema": "delta-b-db001-event-microstructure-probe-v1",
        "source_ticks": str(ns.ticks),
        "source_events": str(ns.events),
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "rows_scanned": rows,
        "minute_count": len(records),
        "event_count_in_scope": len(events),
        "event_window_min": ns.window_min,
        "release_min": ns.release_min,
        "control_utc": [ns.control_start, ns.control_end],
        "phase_counts": dict(sorted(phase_counts.items())),
        "core_comparison": comparison,
        "severity_correlations": correlations,
        "claim_boundary": (
            "Diagnostic correlation only. Event proximity is not a causal direction signal "
            "and this probe does not measure trade profitability."
        ),
    }
    Path(ns.out).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows_scanned": rows,
        "minutes": len(records),
        "events": len(events),
        "out": ns.out,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
