from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Direction = str


@dataclass(frozen=True)
class ExternalAsset:
    symbol: str
    name: str
    market: str
    change_pct: float
    volume_ratio: float = 1.0
    asset_type: str = "equity"
    group: str | None = None
    themes: tuple[str, ...] = ()
    reason_tags: tuple[str, ...] = ()
    reason_summary: str = ""


@dataclass(frozen=True)
class AbnormalMove:
    asset: ExternalAsset
    direction: Direction
    move_score: float
    volume_score: float
    reason_multiplier: float
    strength: float


@dataclass(frozen=True)
class GroupSignal:
    group: str
    direction: Direction
    assets: tuple[AbnormalMove, ...]
    themes: tuple[str, ...]
    avg_change_pct: float
    avg_volume_ratio: float
    resonance_score: float
    strength: float
    reason_summaries: tuple[str, ...] = ()


@dataclass(frozen=True)
class ThemeMapping:
    theme: str
    industries: tuple[str, ...]
    etfs: tuple[str, ...]
    stocks: tuple[dict[str, Any], ...]
    clarity: float = 0.7


@dataclass(frozen=True)
class ScoredTheme:
    theme: str
    direction: Direction
    score: float
    signal_strength: float
    resonance_score: float
    historical_edge_score: float
    mapping_clarity_score: float
    market_environment_score: float
    risk_discount: float
    reasons: tuple[str, ...]
    risks: tuple[str, ...]
    mapping: ThemeMapping
    group_signal: GroupSignal
    risk_details: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class Candidate:
    kind: str
    name: str
    theme: str
    direction: Direction
    score: float
    rationale: str
    risk: str = ""


@dataclass(frozen=True)
class TransmissionEvent:
    event_id: str
    title: str
    direction: Direction
    group: str
    trigger_assets: tuple[str, ...]
    themes: tuple[str, ...]
    score: float
    tier: str
    reason: str
    action: str
    risks: tuple[str, ...]
    confirmations: tuple[str, ...]
    failure_signals: tuple[str, ...]


@dataclass(frozen=True)
class RadarResult:
    as_of: str
    abnormal_moves: tuple[AbnormalMove, ...]
    group_signals: tuple[GroupSignal, ...]
    scored_themes: tuple[ScoredTheme, ...]
    etf_candidates: tuple[Candidate, ...]
    stock_candidates: tuple[Candidate, ...]
    events: tuple[TransmissionEvent, ...] = ()
    context: dict[str, Any] = field(default_factory=dict)
