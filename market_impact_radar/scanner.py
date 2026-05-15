from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any, Iterable

from .models import AbnormalMove, ExternalAsset, GroupSignal


DEFAULT_SETTINGS = {
    "equity_move_pct": 3.0,
    "index_move_pct": 1.2,
    "commodity_move_pct": 1.5,
    "crypto_move_pct": 3.0,
    "volume_ratio": 1.4,
}


def identify_abnormal_moves(
    assets: Iterable[ExternalAsset],
    config: dict[str, Any],
) -> tuple[AbnormalMove, ...]:
    settings = {**DEFAULT_SETTINGS, **config.get("scanner_settings", {})}
    reason_weights = config.get("reason_weights", {})
    moves: list[AbnormalMove] = []

    for asset in assets:
        threshold = _threshold_for_asset(asset, settings)
        abs_change = abs(asset.change_pct)
        has_move = abs_change >= threshold
        has_volume = asset.volume_ratio >= settings["volume_ratio"] and abs_change >= threshold * 0.6
        if not has_move and not has_volume:
            continue

        direction = "up" if asset.change_pct >= 0 else "down"
        move_score = min(100.0, 35.0 + (abs_change / threshold) * 35.0)
        volume_score = min(100.0, 35.0 + max(asset.volume_ratio - 1.0, 0.0) * 42.0)
        reason_multiplier = _reason_multiplier(asset.reason_tags, reason_weights)
        strength = min(100.0, (move_score * 0.72 + volume_score * 0.28) * reason_multiplier)
        moves.append(
            AbnormalMove(
                asset=asset,
                direction=direction,
                move_score=round(move_score, 2),
                volume_score=round(volume_score, 2),
                reason_multiplier=round(reason_multiplier, 3),
                strength=round(strength, 2),
            )
        )

    return tuple(sorted(moves, key=lambda item: item.strength, reverse=True))


def build_group_signals(
    moves: Iterable[AbnormalMove],
    config: dict[str, Any],
) -> tuple[GroupSignal, ...]:
    market_groups = config.get("market_groups", {})
    grouped: dict[tuple[str, str], list[AbnormalMove]] = defaultdict(list)

    for move in moves:
        group = move.asset.group or move.asset.symbol
        grouped[(group, move.direction)].append(move)

    signals: list[GroupSignal] = []
    for (group, direction), group_moves in grouped.items():
        group_config = market_groups.get(group, {})
        min_members = int(group_config.get("min_members", 2))
        allow_single = len(group_moves) >= 1 and (
            min_members <= 1 or max(move.strength for move in group_moves) >= 78
        )
        if len(group_moves) < min_members and not allow_single:
            continue

        avg_abs_change = mean(abs(move.asset.change_pct) for move in group_moves)
        avg_volume = mean(move.asset.volume_ratio for move in group_moves)
        avg_strength = mean(move.strength for move in group_moves)
        count_factor = 1.0 + 0.22 * (len(group_moves) - 1)
        volume_factor = min(1.45, 0.82 + avg_volume * 0.18)
        group_weight = float(group_config.get("resonance_weight", 1.0))
        resonance_score = min(
            100.0,
            avg_abs_change * 8.0 * count_factor * volume_factor * group_weight,
        )
        strength = min(100.0, avg_strength * 0.55 + resonance_score * 0.45)

        themes = set(group_config.get("themes", []))
        reason_summaries = []
        for move in group_moves:
            themes.update(move.asset.themes)
            if move.asset.reason_summary:
                reason_summaries.append(f"{move.asset.name}: {move.asset.reason_summary}")

        signals.append(
            GroupSignal(
                group=group,
                direction=direction,
                assets=tuple(sorted(group_moves, key=lambda item: abs(item.asset.change_pct), reverse=True)),
                themes=tuple(sorted(themes)),
                avg_change_pct=round(mean(move.asset.change_pct for move in group_moves), 2),
                avg_volume_ratio=round(avg_volume, 2),
                resonance_score=round(resonance_score, 2),
                strength=round(strength, 2),
                reason_summaries=tuple(reason_summaries),
            )
        )

    return tuple(sorted(signals, key=lambda item: item.strength, reverse=True))


def _threshold_for_asset(asset: ExternalAsset, settings: dict[str, float]) -> float:
    asset_type = asset.asset_type.lower()
    if asset_type == "index":
        return float(settings["index_move_pct"])
    if asset_type == "commodity":
        return float(settings["commodity_move_pct"])
    if asset_type == "crypto":
        return float(settings["crypto_move_pct"])
    return float(settings["equity_move_pct"])


def _reason_multiplier(reason_tags: Iterable[str], reason_weights: dict[str, float]) -> float:
    weights = [float(reason_weights.get(tag, 1.0)) for tag in reason_tags]
    if not weights:
        return 1.0
    return max(0.55, min(1.2, mean(weights)))
