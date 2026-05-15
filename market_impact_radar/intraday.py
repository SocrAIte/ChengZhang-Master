from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import load_json
from .models import RadarResult, ScoredTheme
from .scoring import signal_tier


def evaluate_intraday(result: RadarResult, snapshot_path: str | Path) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    theme_payloads = snapshot.get("themes", {})
    evaluations = []
    for theme in result.scored_themes:
        payload = theme_payloads.get(theme.theme, {})
        evaluations.append(_evaluate_theme(theme, payload))
    return {
        "as_of": snapshot.get("as_of", ""),
        "evaluations": evaluations,
    }


def render_intraday_report(evaluation: dict[str, Any]) -> str:
    lines = [
        f"# 盘中验证报告 {evaluation.get('as_of', '')}",
        "",
        "| 主题 | 早盘层级 | 早盘分数 | 状态 | 操作 | 验证理由 |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    status_names = {
        "confirmed": "确认",
        "downgraded": "降级",
        "failed": "失败",
        "watch": "观察",
        "missing": "缺数据",
    }
    tier_names = {
        "strong": "强信号",
        "watch": "可观察",
        "weak": "弱观察",
        "risk": "风险/不追",
    }
    for row in evaluation.get("evaluations", []):
        lines.append(
            f"| {row['theme']} | {tier_names.get(row['pre_tier'], row['pre_tier'])} | "
            f"{row['pre_score']:.0f} | {status_names.get(row['status'], row['status'])} | "
            f"{row['action']} | {'；'.join(row['reasons'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _evaluate_theme(theme: ScoredTheme, payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {
            "theme": theme.theme,
            "pre_tier": signal_tier(theme),
            "pre_score": theme.score,
            "status": "missing",
            "action": "缺少盘中数据，保持早盘判断但不新增仓位",
            "reasons": ["未提供该主题盘中快照"],
        }

    etf_current = _float(payload.get("etf_current_pct"))
    etf_open_gap = _float(payload.get("etf_open_gap_pct"))
    etf_above_vwap = bool(payload.get("etf_above_vwap", False))
    leader_current = _float(payload.get("leader_current_pct"))
    leader_fade = bool(payload.get("leader_fade", False))
    stocks_over_5 = int(payload.get("stocks_over_5pct_count", 0) or 0)
    volume_ratio = _float(payload.get("volume_ratio"), 1.0)

    reasons = []
    if etf_above_vwap:
        reasons.append("ETF站上分时均线")
    else:
        reasons.append("ETF未站上分时均线")
    reasons.append(f"ETF当前 {etf_current:+.1f}%")
    reasons.append(f"龙头当前 {leader_current:+.1f}%")
    reasons.append(f"涨超5%个股 {stocks_over_5} 只")
    reasons.append(f"成交放大 {volume_ratio:.1f}x")

    failed = leader_fade or etf_current <= -0.5 or (not etf_above_vwap and stocks_over_5 <= 1)
    confirmed = (
        etf_current > 0
        and etf_above_vwap
        and not leader_fade
        and (stocks_over_5 >= 5 or volume_ratio >= 1.5)
    )
    overheated = etf_open_gap > 5.0

    if failed:
        return _row(theme, "failed", "传导失败或明显转弱，放弃追击", reasons)
    if confirmed and not overheated:
        return _row(theme, "confirmed", "传导确认，可按早盘计划等待回踩或分批观察", reasons)
    if confirmed and overheated:
        return _row(theme, "downgraded", "传导确认但高开过热，只等回踩不追高", reasons)
    if theme.risk_discount >= 18:
        return _row(theme, "downgraded", "盘中未充分确认，维持风险降级", reasons)
    return _row(theme, "watch", "继续观察，等待板块扩散或龙头确认", reasons)


def _row(theme: ScoredTheme, status: str, action: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "theme": theme.theme,
        "pre_tier": signal_tier(theme),
        "pre_score": theme.score,
        "status": status,
        "action": action,
        "reasons": reasons,
    }


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)
