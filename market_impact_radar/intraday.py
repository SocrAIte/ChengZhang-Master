from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import load_json
from .models import RadarResult, ScoredTheme
from .scoring import signal_tier


def evaluate_intraday(result: RadarResult, snapshot_path: str | Path) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    theme_payloads = snapshot.get("themes", {})
    market_breadth = _normalize_market_breadth(snapshot.get("market_breadth", {}))
    evaluations = []
    for theme in result.scored_themes:
        payload = theme_payloads.get(theme.theme, {})
        evaluations.append(_evaluate_theme(theme, payload, market_breadth))
    return {
        "as_of": snapshot.get("as_of", ""),
        "market_breadth": market_breadth,
        "evaluations": evaluations,
    }


def render_intraday_report(evaluation: dict[str, Any]) -> str:
    breadth = evaluation.get("market_breadth", {})
    summary = summarize_intraday_evaluation(evaluation)
    lines = [
        f"# 盘中验证报告 {evaluation.get('as_of', '')}",
        "",
        f"**盘中状态：{summary['headline']}**",
        "",
        _render_market_breadth_line(breadth),
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


def summarize_intraday_evaluation(evaluation: dict[str, Any]) -> dict[str, Any]:
    rows = list(evaluation.get("evaluations", []))
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", ""))
        counts[status] = counts.get(status, 0) + 1

    risk_rows = [
        row
        for row in rows
        if row.get("status") in {"failed", "downgraded", "missing"} and row.get("pre_tier") in {"strong", "watch"}
    ]
    failed_rows = [row for row in rows if row.get("status") == "failed"]
    downgraded_rows = [row for row in rows if row.get("status") == "downgraded"]
    confirmed_rows = [row for row in rows if row.get("status") == "confirmed"]
    missing_rows = [row for row in rows if row.get("status") == "missing"]
    breadth = evaluation.get("market_breadth", {})
    pressure = breadth.get("pressure", "missing")

    if failed_rows or any(row.get("pre_tier") in {"strong", "watch"} for row in risk_rows):
        severity = "high"
    elif downgraded_rows or pressure in {"weak", "missing"}:
        severity = "medium"
    else:
        severity = "low"

    headline = (
        f"确认 {len(confirmed_rows)} / 降级 {len(downgraded_rows)} / "
        f"失败 {len(failed_rows)} / 缺数据 {len(missing_rows)}"
    )
    return {
        "severity": severity,
        "headline": headline,
        "counts": counts,
        "market_pressure": pressure,
        "risk_themes": [str(row.get("theme", "")) for row in risk_rows[:6]],
        "confirmed_themes": [str(row.get("theme", "")) for row in confirmed_rows[:6]],
        "failed_themes": [str(row.get("theme", "")) for row in failed_rows[:6]],
        "downgraded_themes": [str(row.get("theme", "")) for row in downgraded_rows[:6]],
    }


def _evaluate_theme(theme: ScoredTheme, payload: dict[str, Any], market_breadth: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        return {
            "theme": theme.theme,
            "pre_tier": signal_tier(theme),
            "pre_score": theme.score,
            "status": "missing",
            "action": "缺少盘中数据，保持早盘判断但不新增仓位",
            "reasons": ["未提供该主题盘中快照"],
        }

    data_status = str(payload.get("data_status", "ok"))
    if data_status != "ok":
        return _row(
            theme,
            "missing",
            "盘中数据不完整，不做确认或加仓判断",
            [f"主题快照状态 {data_status}"],
        )

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
    reasons.append(_market_breadth_reason(market_breadth))

    failed = leader_fade or etf_current <= -0.5 or (not etf_above_vwap and stocks_over_5 <= 1)
    confirmed = (
        etf_current > 0
        and etf_above_vwap
        and not leader_fade
        and (stocks_over_5 >= 5 or volume_ratio >= 1.5)
    )
    overheated = etf_open_gap > 5.0
    market_pressure = market_breadth.get("pressure", "missing")

    if failed:
        return _row(theme, "failed", "传导失败或明显转弱，放弃追击", reasons)
    if confirmed and market_pressure == "weak":
        return _row(theme, "downgraded", "主题有确认迹象，但全市场宽度偏弱，只观察不追高", reasons)
    if confirmed and market_pressure == "missing":
        return _row(theme, "downgraded", "主题有确认迹象，但市场宽度缺失，降低确认等级", reasons)
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


def _normalize_market_breadth(payload: dict[str, Any]) -> dict[str, Any]:
    data_status = str(payload.get("data_status") or ("ok" if payload else "missing"))
    up_count = int(payload.get("up_count", 0) or 0)
    down_count = int(payload.get("down_count", 0) or 0)
    stocks_over_5 = int(payload.get("stocks_over_5pct_count", 0) or 0)
    sample_size = int(payload.get("sample_size", 0) or 0)
    pressure = "missing"
    if data_status == "ok" and sample_size > 0:
        if down_count >= up_count * 1.3 and stocks_over_5 < 100:
            pressure = "weak"
        elif up_count >= down_count * 1.2 and stocks_over_5 >= 100:
            pressure = "supportive"
        else:
            pressure = "neutral"
    return {
        "source": payload.get("source", ""),
        "data_status": data_status,
        "pressure": pressure,
        "turnover_billion": _float(payload.get("turnover_billion")),
        "up_count": up_count,
        "down_count": down_count,
        "unchanged_count": int(payload.get("unchanged_count", 0) or 0),
        "stocks_over_5pct_count": stocks_over_5,
        "sample_size": sample_size,
    }


def _market_breadth_reason(payload: dict[str, Any]) -> str:
    if payload.get("pressure") == "missing":
        return "全市场宽度缺失"
    return (
        f"市场宽度 {payload.get('pressure')}：上涨 {payload.get('up_count')} 家，"
        f"下跌 {payload.get('down_count')} 家，涨超5% {payload.get('stocks_over_5pct_count')} 家"
    )


def _render_market_breadth_line(payload: dict[str, Any]) -> str:
    if not payload or payload.get("pressure") == "missing":
        return "市场宽度：缺失，盘中确认等级自动保守处理。"
    return (
        f"市场宽度：{payload.get('pressure')}，来源 {payload.get('source') or 'unknown'}，"
        f"成交额 {payload.get('turnover_billion'):.2f} 亿，"
        f"上涨 {payload.get('up_count')} 家，下跌 {payload.get('down_count')} 家，"
        f"涨超5% {payload.get('stocks_over_5pct_count')} 家。"
    )


def _float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)
