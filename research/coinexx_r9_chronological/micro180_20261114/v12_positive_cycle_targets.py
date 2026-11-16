"""Strict positive A/B/C cycle ENTRY TARGETS from existing R9-Coinexx merge.

Used ONLY in offline training/evaluation, NEVER imported by the execution EA.
C family can require taking a loss on the FIRST leg to reach a positive
COMPLETE cycle; distinguish positive_trade from positive_cycle_precursor.
All other reference outcomes remain unlabeled BACKGROUND, not claimed losing
examples or known counterfactuals. Original net, costs and source remain read-only.
"""
from __future__ import annotations

import csv
import gzip
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class PositiveEntryTarget:
    minute: int
    teacher_second: int
    leg: int
    side: int
    mapped_quote_ms: int
    mapped_bid_ask_entry_cents: int
    family: str
    original_trade_net_usd: Decimal
    mapped_trade_quote_net_usd: Decimal
    positive_individual_exit: bool


def _rows(path: Path) -> Iterator[dict[str, str]]:
    with gzip.open(path, "rt", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {
            "entry_time_broker", "leg", "side", "net_usd", "quote_net",
            "equote_ms", "elag_ms", "xlag_ms", "q_entry_u",
        }
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("Existing source is not the original merged R9-Coinexx CSV")
        yield from reader


def read_positive_targets(path: Path) -> tuple[list[PositiveEntryTarget], dict]:
    """Full reference scan; return ONLY valid, positive complete A/B/C cycles.

    Source quotes are future outcomes here solely because this is a SUPERVISION
    and independent scoring utility. Do not import into live signal code.
    """
    all_cycles: dict[int, dict[int, dict]] = {}
    seen = 0
    original_net = Decimal("0")
    for row in _rows(path):
        seen += 1
        original_net += Decimal(row["net_usd"])
        dt = datetime.fromisoformat(row["entry_time_broker"]).replace(tzinfo=timezone.utc)
        sec = int(dt.timestamp())
        minute = sec // 60
        leg = int(row["leg"])
        side = 1 if row["side"].lower() == "buy" else -1
        if leg not in (1, 2) or side not in (1, -1):
            raise ValueError("Invalid source leg/side")
        q_text = row["quote_net"].strip()
        q = Decimal(q_text) if q_text else Decimal("NaN")
        d = {
            "sec": sec, "minute": minute, "leg": leg, "side": side,
            "net": Decimal(row["net_usd"]), "quote_net": q,
            "entry_ms": int(row["equote_ms"]),
            "entry_u": int(row["q_entry_u"]),
            "valid": 0 <= int(row["elag_ms"]) <= 2000
                     and 0 <= int(row["xlag_ms"]) <= 2000
                     and q.is_finite(),
        }
        bucket = all_cycles.setdefault(minute, {})
        if leg in bucket:
            raise ValueError("Duplicate original source minute/leg")
        bucket[leg] = d

    targets: list[PositiveEntryTarget] = []
    counts = {"A": 0, "B": 0, "C": 0}
    selected_net = Decimal("0")
    selected_quote_net = Decimal("0")
    for minute, legs in all_cycles.items():
        first = legs.get(1)
        second = legs.get(2)
        if first is None:
            raise ValueError("Orphan second leg in original R9 source")
        if second is None:
            family = "A"
        elif first["net"] > 0 and second["net"] > 0:
            family = "B"
        elif first["net"] <= 0 and second["net"] > 0:
            family = "C"
        else:
            continue
        group = tuple(legs.values())
        if not all(x["valid"] for x in group):
            continue
        net = sum((x["net"] for x in group), Decimal("0"))
        quote_net = sum((x["quote_net"] for x in group), Decimal("0"))
        if net <= 0 or quote_net <= 0:
            continue
        counts[family] += 1
        selected_net += net
        selected_quote_net += quote_net
        for x in group:
            targets.append(PositiveEntryTarget(
                minute=x["minute"], teacher_second=x["sec"],
                leg=x["leg"], side=x["side"],
                mapped_quote_ms=x["entry_ms"],
                mapped_bid_ask_entry_cents=x["entry_u"],
                family=family,
                original_trade_net_usd=x["net"],
                mapped_trade_quote_net_usd=x["quote_net"],
                positive_individual_exit=x["net"] > 0 and x["quote_net"] > 0,
            ))
    result = {
        "original_rows": seen,
        "original_net_usd_preserved": str(original_net),
        "positive_complete_cycles_by_family": counts,
        "positive_first_leg_targets": sum(x.leg == 1 for x in targets),
        "positive_second_leg_targets": sum(x.leg == 2 for x in targets),
        "positive_target_legs": len(targets),
        "selected_original_cycle_net_usd": str(selected_net),
        "selected_quote_cycle_net_usd": str(selected_quote_net),
        "contains_C_initial_loss_as_recovery_precursor": any(
            x.family == "C" and x.leg == 1 and not x.positive_individual_exit
            for x in targets
        ),
        "training_labels_are_not_online_features": True,
    }
    return targets, result
