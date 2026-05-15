from __future__ import annotations

from typing import Any

from .io import load_theme_mappings
from .models import Candidate, GroupSignal, ScoredTheme


DEFAULT_SCORING_RULES: dict[str, Any] = {
    "score_weights": {
        "signal_strength": 0.20,
        "resonance_score": 0.20,
        "historical_edge": 0.20,
        "mapping_clarity": 0.15,
        "market_environment": 0.15,
    },
    "tier_thresholds": {
        "strong": 80,
        "watch": 65,
        "weak": 50,
        "risk_discount_risk": 18,
    },
    "risk_cap": 45,
    "stock_risk_penalty": {"低": 0, "中": 3, "中高": 5, "高": 7, "极高": 10},
    "crowding_penalty": {
        "low": 0,
        "medium": 4,
        "high": 10,
        "extreme": 16,
        "低": 0,
        "中": 4,
        "高": 10,
        "极高": 16,
    },
}


def score_themes(
    group_signals: tuple[GroupSignal, ...],
    config: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> tuple[ScoredTheme, ...]:
    context = context or {}
    rules = _rules(context)
    weights = rules.get("score_weights", DEFAULT_SCORING_RULES["score_weights"])
    weight_total = sum(float(value) for value in weights.values()) or 1.0
    mappings = load_theme_mappings(config)
    best_by_theme_direction: dict[tuple[str, str], ScoredTheme] = {}

    for signal in group_signals:
        for theme in signal.themes:
            mapping = mappings.get(theme)
            if mapping is None:
                continue

            historical_edge_score = _historical_edge_score(
                context.get("historical_edges", {}).get(theme, {}),
                rules,
            )
            mapping_clarity_score = max(0.0, min(100.0, mapping.clarity * 100.0))
            market_environment_score = float(context.get("market_environment", {}).get("score", 70.0))
            risk_discount, risks, risk_details = _risk_discount(theme, signal.direction, context, rules)

            positive_score = (
                signal.strength * float(weights.get("signal_strength", 0))
                + signal.resonance_score * float(weights.get("resonance_score", 0))
                + historical_edge_score * float(weights.get("historical_edge", 0))
                + mapping_clarity_score * float(weights.get("mapping_clarity", 0))
                + market_environment_score * float(weights.get("market_environment", 0))
            ) / weight_total
            final_score = max(0.0, min(100.0, positive_score - risk_discount))

            candidate = ScoredTheme(
                theme=theme,
                direction=signal.direction,
                score=round(final_score, 2),
                signal_strength=signal.strength,
                resonance_score=signal.resonance_score,
                historical_edge_score=round(historical_edge_score, 2),
                mapping_clarity_score=round(mapping_clarity_score, 2),
                market_environment_score=round(market_environment_score, 2),
                risk_discount=round(risk_discount, 2),
                reasons=tuple(_theme_reasons(signal, theme, context)),
                risks=tuple(risks),
                mapping=mapping,
                group_signal=signal,
                risk_details=tuple(risk_details),
            )
            key = (candidate.theme, candidate.direction)
            current = best_by_theme_direction.get(key)
            if current is None or candidate.score > current.score:
                best_by_theme_direction[key] = candidate

    return tuple(sorted(best_by_theme_direction.values(), key=lambda item: item.score, reverse=True))


def build_candidates(
    scored_themes: tuple[ScoredTheme, ...],
    max_etfs: int = 10,
    max_stocks: int = 15,
    rules: dict[str, Any] | None = None,
) -> tuple[tuple[Candidate, ...], tuple[Candidate, ...]]:
    rules = _merge_rules(rules or {})
    risk_penalty = rules.get("stock_risk_penalty", DEFAULT_SCORING_RULES["stock_risk_penalty"])
    etfs: dict[str, Candidate] = {}
    stocks: dict[str, Candidate] = {}

    for theme in scored_themes:
        direction_text = "受益" if theme.direction == "up" else "承压"
        asset_names = "、".join(move.asset.name for move in theme.group_signal.assets[:4])
        rationale = f"{theme.group_signal.group}{direction_text}: {asset_names}"

        for etf in theme.mapping.etfs:
            _keep_best(
                etfs,
                Candidate(
                    kind="ETF",
                    name=etf,
                    theme=theme.theme,
                    direction=theme.direction,
                    score=theme.score,
                    rationale=rationale,
                    risk="ETF波动相对个股更低，仍需看高开和溢价",
                ),
            )

        for stock in theme.mapping.stocks:
            risk = str(stock.get("risk", "中"))
            elasticity = float(stock.get("elasticity", 0.7))
            stock_score = theme.score * (0.76 + elasticity * 0.24) - float(risk_penalty.get(risk, 4.0))
            role = str(stock.get("role", theme.theme))
            _keep_best(
                stocks,
                Candidate(
                    kind="stock",
                    name=str(stock["name"]),
                    theme=theme.theme,
                    direction=theme.direction,
                    score=round(max(0.0, min(100.0, stock_score)), 2),
                    rationale=f"{rationale}; {role}",
                    risk=risk,
                ),
            )

    etf_list = tuple(sorted(etfs.values(), key=lambda item: item.score, reverse=True)[:max_etfs])
    stock_list = tuple(sorted(stocks.values(), key=lambda item: item.score, reverse=True)[:max_stocks])
    return etf_list, stock_list


def signal_tier(theme: ScoredTheme, rules: dict[str, Any] | None = None) -> str:
    thresholds = _merge_rules(rules or {}).get("tier_thresholds", DEFAULT_SCORING_RULES["tier_thresholds"])
    if theme.risk_discount >= float(thresholds.get("risk_discount_risk", 18)) and theme.score < float(thresholds.get("strong", 80)):
        return "risk"
    if theme.score >= float(thresholds.get("strong", 80)):
        return "strong"
    if theme.score >= float(thresholds.get("watch", 65)):
        return "watch"
    if theme.score >= float(thresholds.get("weak", 50)):
        return "weak"
    return "risk"


def _keep_best(candidates: dict[str, Candidate], candidate: Candidate) -> None:
    current = candidates.get(candidate.name)
    if current is None or candidate.score > current.score:
        candidates[candidate.name] = candidate


def _historical_edge_score(edge: dict[str, Any], rules: dict[str, Any]) -> float:
    settings = rules.get("historical_edge_score", {})
    if not edge:
        return float(settings.get("default_score", 60.0))

    win_rate = _float(edge.get("win_rate"), 0.55)
    avg_close = _float(edge.get("avg_close_pct"))
    avg_high = _float(edge.get("avg_high_pct"), avg_close)
    max_drawdown = abs(_float(edge.get("max_drawdown_pct")))
    fade_rate = _float(edge.get("gap_fade_rate"), 0.35)

    score = win_rate * float(settings.get("win_rate_weight", 68.0))
    score += max(
        0.0,
        min(
            float(settings.get("avg_close_cap", 20.0)),
            (avg_close + float(settings.get("avg_close_shift", 1.0)))
            * float(settings.get("avg_close_multiplier", 8.0)),
        ),
    )
    score += max(
        0.0,
        min(float(settings.get("avg_high_cap", 12.0)), avg_high * float(settings.get("avg_high_multiplier", 2.0))),
    )
    score -= max(0.0, fade_rate - float(settings.get("fade_baseline", 0.35))) * float(settings.get("fade_penalty_multiplier", 22.0))
    score -= max(0.0, max_drawdown - float(settings.get("drawdown_free_pct", 3.0))) * float(settings.get("drawdown_penalty_multiplier", 2.0))
    return max(0.0, min(100.0, score))


def _risk_discount(
    theme: str,
    direction: str,
    context: dict[str, Any],
    rules: dict[str, Any],
) -> tuple[float, list[str], list[dict[str, Any]]]:
    risks: list[str] = []
    details: list[dict[str, Any]] = []
    discount = 0.0
    previous = context.get("a_share_previous_moves", {}).get(theme, {})
    auction = context.get("auction", {}).get(theme, {})
    market = context.get("market_environment", {})
    risk_rules = rules.get("risk_rules", {})

    field_map = {
        "previous_change_pct": previous.get("change_pct"),
        "three_day_change_pct": previous.get("three_day_change_pct"),
        "five_day_change_pct": previous.get("five_day_change_pct"),
        "consecutive_up_days": previous.get("consecutive_up_days"),
        "limit_up_count": previous.get("limit_up_count"),
        "turnover_ratio": previous.get("turnover_ratio"),
        "volume_ratio": previous.get("volume_ratio"),
        "etf_premium_pct": previous.get("etf_premium_pct"),
        "main_fund_flow_pct": previous.get("main_fund_flow_pct"),
        "northbound_flow_pct": previous.get("northbound_flow_pct"),
        "auction_open_gap_pct": auction.get("open_gap_pct"),
        "leader_open_gap_pct": auction.get("leader_open_gap_pct"),
        "market_score": market.get("score"),
        "market_turnover_billion": market.get("turnover_billion"),
        "market_up_down_ratio": market.get("up_down_ratio"),
    }
    for field, value in field_map.items():
        penalty, hit = _rule_penalty(
            theme=theme,
            direction=direction,
            field=field,
            value=_float(value, None),
            specs=risk_rules.get(field, []),
        )
        if hit:
            risks.append(hit["message"])
            details.append(hit)
        discount += penalty

    if _float(auction.get("open_gap_pct")) > 2.0 and _float(auction.get("matched_amount_ratio"), 1.0) < 0.8:
        hit = _manual_hit("auction_matched_amount_ratio", 5.0, f"{theme}竞价高开但撮合量不足，需防虚高开", auction.get("matched_amount_ratio"))
        risks.append(hit["message"])
        details.append(hit)
        discount += hit["penalty"]

    crowding = str(previous.get("crowding", "")).lower()
    crowding_penalty = float(rules.get("crowding_penalty", {}).get(crowding, 0.0))
    if crowding_penalty:
        message = f"{theme}拥挤度高" if crowding_penalty >= 10 else f"{theme}拥挤度中等"
        hit = _manual_hit("crowding", crowding_penalty, message, crowding)
        risks.append(hit["message"])
        details.append(hit)
        discount += crowding_penalty

    leader_status = str(previous.get("leader_status", "")).lower()
    leader_rule = rules.get("leader_status_penalty", {}).get(leader_status)
    if leader_rule:
        message = str(leader_rule.get("message", "")).format(theme=theme)
        hit = _manual_hit("leader_status", float(leader_rule.get("penalty", 0.0)), message, leader_status)
        risks.append(hit["message"])
        details.append(hit)
        discount += hit["penalty"]

    index_trend = str(market.get("index_trend", "")).lower()
    trend_rule = rules.get("index_trend_penalty", {}).get(index_trend)
    if trend_rule:
        message = str(trend_rule.get("message", "")).format(theme=theme)
        hit = _manual_hit("index_trend", float(trend_rule.get("penalty", 0.0)), message, index_trend)
        risks.append(hit["message"])
        details.append(hit)
        discount += hit["penalty"]

    risk_cap = float(rules.get("risk_cap", 45.0))
    capped_discount = min(risk_cap, discount)
    if capped_discount < discount:
        details.append(
            {
                "field": "risk_cap",
                "value": risk_cap,
                "penalty": round(capped_discount - discount, 2),
                "raw_penalty": round(discount, 2),
                "message": f"风险折扣封顶为 {risk_cap:.0f} 分",
            }
        )
    return capped_discount, risks, details


def _rule_penalty(
    theme: str,
    direction: str,
    field: str,
    value: float | None,
    specs: list[dict[str, Any]],
) -> tuple[float, dict[str, Any] | None]:
    if value is None:
        return 0.0, None
    for spec in specs:
        if spec.get("direction") and spec.get("direction") != direction:
            continue
        if _matches_threshold(value, spec):
            penalty = float(spec.get("penalty", 0.0))
            message = str(spec.get("message", "")).format(theme=theme, value=value)
            return penalty, _manual_hit(field, penalty, message, value)
    return 0.0, None


def _manual_hit(field: str, penalty: float, message: str, value: Any) -> dict[str, Any]:
    return {
        "field": field,
        "value": value,
        "penalty": round(float(penalty), 2),
        "message": message,
    }


def _matches_threshold(value: float, spec: dict[str, Any]) -> bool:
    if "gte" in spec and value < float(spec["gte"]):
        return False
    if "gt" in spec and value <= float(spec["gt"]):
        return False
    if "lte" in spec and value > float(spec["lte"]):
        return False
    if "lt" in spec and value >= float(spec["lt"]):
        return False
    return any(key in spec for key in ("gte", "gt", "lte", "lt"))


def _theme_reasons(signal: GroupSignal, theme: str, context: dict[str, Any]) -> list[str]:
    direction_text = "上涨" if signal.direction == "up" else "下跌"
    asset_text = "、".join(f"{move.asset.name}{move.asset.change_pct:+.1f}%" for move in signal.assets[:5])
    reasons = [
        f"{signal.group}出现{direction_text}共振：{asset_text}",
        f"板块共振分 {signal.resonance_score:.0f}，平均放量 {signal.avg_volume_ratio:.1f}x",
    ]

    edge = context.get("historical_edges", {}).get(theme, {})
    if edge:
        reasons.append(
            "历史传导："
            f"胜率 {float(edge.get('win_rate', 0)) * 100:.1f}%，"
            f"平均开盘 {float(edge.get('avg_open_pct', 0)):+.1f}%，"
            f"平均收盘 {float(edge.get('avg_close_pct', 0)):+.1f}%"
        )
    if signal.reason_summaries:
        reasons.append("; ".join(signal.reason_summaries[:2]))
    return reasons


def _rules(context: dict[str, Any]) -> dict[str, Any]:
    return _merge_rules(context.get("scoring_rules", {}))


def _merge_rules(overrides: dict[str, Any]) -> dict[str, Any]:
    return _deep_merge(DEFAULT_SCORING_RULES, overrides)


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _float(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
