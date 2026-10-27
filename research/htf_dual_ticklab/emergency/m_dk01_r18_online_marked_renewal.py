"""M-DK-01 R18 | native Dukascopy Level-I marked quote renewal, UNAPPROVED.

A source-native online causal *feature producer* and frozen-probability arbitration
contract. NOT a fitted model, an executable order, or evidence of market edge.
No executed volume, order book, future outcome, current teacher or market orders.

Input bid_1000/ask_1000 use the exact original Dukascopy integer quote unit;
convert with /1000 (not multiplication by .001). One instance per native stream.
Call asof() at the exact original event (timestamp, ordinal) while streaming;
a later asof cannot time travel to an earlier source event.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import exp, isfinite, log
from typing import Mapping

HALF_LIVES_MS = (500, 2000, 10000, 30000, 120000)
MARKS = ("bid_up", "bid_down", "ask_up", "ask_down", "bid_only",
         "ask_only", "joint", "spread_widen", "spread_narrow", "quote")


@dataclass(frozen=True)
class NativeQuote:
    time_msc: int
    ordinal: int
    bid_1000: int
    ask_1000: int


class SourceClockError(ValueError):
    """Original native UTC timestamp/quote ordinal cannot be reconciled."""


@dataclass
class MarkedRenewalState:
    broker: str = "dukascopy"
    half_lives_ms: tuple[int, ...] = HALF_LIVES_MS
    last: NativeQuote | None = None
    first_msc: int | None = None
    last_bid_msc: int | None = None
    last_ask_msc: int | None = None
    last_positive_mid_msc: int | None = None
    last_negative_mid_msc: int | None = None
    updates: int = 0
    session_restart_after_ms: int = 600000
    intensities: dict[int, dict[str, float]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.broker != "dukascopy":
            raise ValueError("M-DK-01 specialist requires isolated native Dukascopy source")
        if not self.half_lives_ms or any(h <= 0 for h in self.half_lives_ms):
            raise ValueError("positive observation half-lives required")
        if len(set(self.half_lives_ms)) != len(self.half_lives_ms):
            raise ValueError("duplicate half-life")
        if not self.intensities:
            self.intensities = {h: {mark: 0.0 for mark in MARKS}
                                for h in self.half_lives_ms}

    def observe(self, q: NativeQuote) -> None:
        if not isinstance(q.time_msc, int) or not isinstance(q.ordinal, int):
            raise SourceClockError("source timestamps and ordinal must be integers")
        if q.ordinal < 0 or q.time_msc <= 0 or not isinstance(q.bid_1000, int) or not isinstance(q.ask_1000, int):
            raise SourceClockError("invalid original source clock/price integer fields")
        if q.bid_1000 <= 0 or q.ask_1000 < q.bid_1000:
            raise SourceClockError("invalid native bid/ask integer prices")
        if self.last is not None and (q.time_msc, q.ordinal) <= (self.last.time_msc, self.last.ordinal):
            raise SourceClockError("non-monotonic original quote ordinal")
        elapsed = 0 if self.last is None else q.time_msc - self.last.time_msc
        # Stale dealer quote after a source gap is not a continuous live stream.
        if self.last is not None and elapsed > self.session_restart_after_ms:
            self.last = None
            self.first_msc = None
            self.last_bid_msc = None
            self.last_ask_msc = None
            self.last_positive_mid_msc = None
            self.last_negative_mid_msc = None
            self.updates = 0
            for rates in self.intensities.values():
                for mark in MARKS:
                    rates[mark] = 0.0
            elapsed = 0
        for h in self.half_lives_ms:
            d = exp(-log(2.0) * elapsed / h)
            for mark in MARKS:
                self.intensities[h][mark] *= d
        marks = {"quote"}
        if self.last is not None:
            db = q.bid_1000 - self.last.bid_1000
            da = q.ask_1000 - self.last.ask_1000
            if db > 0: marks.add("bid_up")
            if db < 0: marks.add("bid_down")
            if da > 0: marks.add("ask_up")
            if da < 0: marks.add("ask_down")
            if db and da: marks.add("joint")
            elif db: marks.add("bid_only")
            elif da: marks.add("ask_only")
            ds = (q.ask_1000-q.bid_1000)-(self.last.ask_1000-self.last.bid_1000)
            if ds > 0: marks.add("spread_widen")
            elif ds < 0: marks.add("spread_narrow")
            if db: self.last_bid_msc = q.time_msc
            if da: self.last_ask_msc = q.time_msc
            if db+da > 0: self.last_positive_mid_msc = q.time_msc
            if db+da < 0: self.last_negative_mid_msc = q.time_msc
        else:
            self.first_msc = q.time_msc
            self.last_bid_msc = q.time_msc
            self.last_ask_msc = q.time_msc
        for h in self.half_lives_ms:
            for mark in marks:
                self.intensities[h][mark] += 1.0
        self.last = q
        self.updates += 1

    def asof(self, *, event_msc: int, original_quote_ordinal: int, side: int) -> dict[str, float]:
        """Fail-closed if original event quote is not the last observed quote."""
        if side not in (-1, 1):
            raise ValueError("original side must be -1/+1")
        if self.last is None or (self.last.time_msc, self.last.ordinal) != (event_msc, original_quote_ordinal):
            raise SourceClockError("exact original event quote not yet observed, or future quote was consumed")
        assert self.first_msc is not None
        f: dict[str, float] = {
            "side": float(side),
            "spread": (self.last.ask_1000-self.last.bid_1000)/1000,
            "observation_age_s": (event_msc-self.first_msc)/1000,
            "warmup_2min": float(event_msc-self.first_msc >= 120000 and self.updates >= 64),
            "source_bid": self.last.bid_1000/1000,
            "source_ask": self.last.ask_1000/1000,
        }
        for label, t in (("bid", self.last_bid_msc), ("ask", self.last_ask_msc),
                         ("positive_mid", self.last_positive_mid_msc),
                         ("negative_mid", self.last_negative_mid_msc)):
            f["age_"+label+"_s"] = -1.0 if t is None else (event_msc-t)/1000
        for h in self.half_lives_ms:
            rates = self.intensities[h]
            k = f"decay_{h}ms_"
            den = max(1.0, rates["quote"])
            for mark in MARKS:
                f[k+mark] = rates[mark]
            f[k+"bid_ask_polarity"] = side * (
                rates["bid_up"] + rates["ask_up"] - rates["bid_down"]-rates["ask_down"]) / den
            f[k+"single_side_asymmetry"] = side * (rates["bid_only"]-rates["ask_only"]) / den
            f[k+"spread_stress"] = (rates["spread_widen"]-rates["spread_narrow"]) / den
            f[k+"joint_fraction"] = rates["joint"]/den
            f[k+"per_second_renewal"] = rates["quote"] * log(2.0)/(h/1000)
        short, long = self.half_lives_ms[0], self.half_lives_ms[-1]
        f["renewal_burst_ratio"] = (
            f[f"decay_{short}ms_per_second_renewal"] /
            max(1e-8, f[f"decay_{long}ms_per_second_renewal"]))
        if not all(isfinite(v) for v in f.values()):
            raise ValueError("invalid non-finite native quote state")
        return f


@dataclass(frozen=True)
class FrozenRiskPolicy:
    """Thresholds must be selected on CAL and frozen before VAL; no fitting here."""
    opposite_cut: float
    neutral_cut: float
    correct_guard_cut: float

    def __post_init__(self) -> None:
        if any(not isfinite(c) or not 0 <= c <= 1 for c in (
            self.opposite_cut, self.neutral_cut, self.correct_guard_cut
        )):
            raise ValueError("frozen CAL threshold must be a finite probability")

    def decide(self, scores: Mapping[str, float], *, quote_warm: bool,
               decision_msc: int | None = None, score_observed_through_msc: int | None = None,
               original_order_already_filled: bool = False) -> str:
        """Decides admission of a NEW unfilled order ONLY; no retrospective t0 veto."""
        if original_order_already_filled:
            return "FILLED_UNTOUCHABLE"
        if not quote_warm or decision_msc is None or score_observed_through_msc is None:
            return "KEEP_UNSCORED"
        if score_observed_through_msc > decision_msc or score_observed_through_msc < 0:
            return "KEEP_UNSCORED"
        required = ("opposite", "neutral", "correct")
        if any(k not in scores or not isfinite(scores[k]) or not 0 <= scores[k] <= 1 for k in required):
            return "KEEP_UNSCORED"
        if scores["correct"] >= self.correct_guard_cut:
            return "KEEP_RIGHT_GUARD"
        if scores["opposite"] >= self.opposite_cut or scores["neutral"] >= self.neutral_cut:
            return "VETO_NEW_UNFILLED_ORDER"
        return "KEEP_NEW_ORDER_CANDIDATE"


def count_original_veto(labels: list[int], proposed_veto: list[bool],
                        parent_veto: list[bool]) -> dict[str, int]:
    """Audit diagnostic event masks; never provide labels to the live model."""
    if not (len(labels) == len(proposed_veto) == len(parent_veto)):
        raise ValueError("original event denominator/mask length mismatch")
    if any(x not in (0, 1, 2) for x in labels):
        raise ValueError("unknown original three-class label")
    out = {"total": len(labels), "right_total": labels.count(0),
           "bad_total": len(labels)-labels.count(0), "unique_bad": 0,
           "extra_right": 0, "overlap_bad": 0, "overlap_right": 0,
           "unique_opposite": 0, "unique_neutral": 0}
    for label, vote, parent in zip(labels, proposed_veto, parent_veto):
        if not vote: continue
        if parent:
            out["overlap_right" if label == 0 else "overlap_bad"] += 1
        elif label == 0:
            out["extra_right"] += 1
        else:
            out["unique_bad"] += 1
            out["unique_opposite" if label == 1 else "unique_neutral"] += 1
    return out
