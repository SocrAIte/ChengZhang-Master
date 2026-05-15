from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

from .io import load_json


def summarize_review_result(path: str | Path) -> dict[str, Any]:
    payload = load_json(path)
    themes = payload.get("themes", [])
    candidates = payload.get("candidates", [])

    theme_summary = _summarize_items(themes, key_field="theme")
    candidate_summary = _summarize_items(candidates, key_field="name")
    return {
        "date": payload.get("date", ""),
        "theme_summary": theme_summary,
        "candidate_summary": candidate_summary,
        "events": payload.get("events", []),
        "lessons": payload.get("lessons", []),
        "historical_edges": _review_edges(theme_summary),
    }


def render_review_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# 收盘复盘结果汇总 {summary.get('date', '')}",
        "",
        "## 主题结果",
        "",
        "| 主题 | 样本 | 胜率 | 确认率 | 平均开盘 | 平均最高 | 平均收盘 | 最大回撤 | 高开回落 | 适合开盘买 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary.get("theme_summary", []):
        lines.append(_summary_row(row, "name"))

    lines.extend(["", "## 候选结果", ""])
    lines.extend(
        [
            "| 候选 | 样本 | 胜率 | 确认率 | 平均开盘 | 平均最高 | 平均收盘 | 最大回撤 | 高开回落 | 适合开盘买 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary.get("candidate_summary", []):
        lines.append(_summary_row(row, "name"))

    lessons = summary.get("lessons", [])
    if lessons:
        lines.extend(["", "## 规则校准观察", ""])
        for lesson in lessons:
            lines.append(f"- {lesson}")

    return "\n".join(lines).rstrip() + "\n"


def write_review_summary(path: str | Path, summary: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".json":
        target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        target.write_text(render_review_summary_markdown(summary), encoding="utf-8")


def write_review_edges(path: str | Path, summary: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": summary.get("date", ""),
        "source": "review_result",
        "historical_edges": summary.get("historical_edges", {}),
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _summarize_items(items: list[dict[str, Any]], key_field: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        key = str(item.get(key_field, ""))
        if not key:
            continue
        grouped.setdefault(key, []).append(item)

    rows = []
    for name, group in grouped.items():
        close_returns = [_float(item.get("close_pct")) for item in group]
        open_returns = [_float(item.get("open_pct")) for item in group]
        high_returns = [_float(item.get("high_pct")) for item in group]
        low_returns = [_float(item.get("low_pct")) for item in group]
        confirmed = [_bool(item.get("confirmed")) for item in group if "confirmed" in item]
        gap_fades = [_bool(item.get("gap_fade")) for item in group if "gap_fade" in item]
        early_buy = [_bool(item.get("early_buy_suitable")) for item in group if "early_buy_suitable" in item]

        rows.append(
            {
                "name": name,
                "events": len(group),
                "win_rate": _rate(value > 0 for value in close_returns),
                "confirm_rate": _rate(confirmed) if confirmed else 0.0,
                "avg_open_pct": round(mean(open_returns), 4),
                "avg_high_pct": round(mean(high_returns), 4),
                "avg_low_pct": round(mean(low_returns), 4),
                "avg_close_pct": round(mean(close_returns), 4),
                "max_drawdown_pct": round(min(low_returns), 4),
                "gap_fade_rate": _rate(gap_fades) if gap_fades else 0.0,
                "early_buy_suitable_rate": _rate(early_buy) if early_buy else 0.0,
            }
        )

    return sorted(rows, key=lambda item: (item["win_rate"], item["avg_close_pct"]), reverse=True)


def _review_edges(theme_summary: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    edges = {}
    for row in theme_summary:
        edges[row["name"]] = {
            "events": row["events"],
            "win_rate": row["win_rate"],
            "avg_open_pct": row["avg_open_pct"],
            "avg_high_pct": row["avg_high_pct"],
            "avg_low_pct": row["avg_low_pct"],
            "avg_close_pct": row["avg_close_pct"],
            "max_drawdown_pct": row["max_drawdown_pct"],
            "gap_fade_rate": row["gap_fade_rate"],
            "confirm_rate": row["confirm_rate"],
            "early_buy_suitable_rate": row["early_buy_suitable_rate"],
        }
    return edges


def _summary_row(row: dict[str, Any], name_field: str) -> str:
    return (
        f"| {row[name_field]} | {row['events']} | {row['win_rate'] * 100:.1f}% | "
        f"{row['confirm_rate'] * 100:.1f}% | {row['avg_open_pct']:+.2f}% | "
        f"{row['avg_high_pct']:+.2f}% | {row['avg_close_pct']:+.2f}% | "
        f"{row['max_drawdown_pct']:+.2f}% | {row['gap_fade_rate'] * 100:.1f}% | "
        f"{row['early_buy_suitable_rate'] * 100:.1f}% |"
    )


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _bool(value: Any) -> bool:
    return bool(value)


def _rate(values: Any) -> float:
    values = list(values)
    if not values:
        return 0.0
    return round(sum(1 for value in values if value) / len(values), 4)
