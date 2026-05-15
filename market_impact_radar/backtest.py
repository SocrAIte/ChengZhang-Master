from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


def compute_transmission_stats(
    history_path: str | Path,
    external_symbol: str | None = None,
    theme: str | None = None,
    threshold: float = 5.0,
    direction: str = "up",
) -> dict[str, Any]:
    rows = _select_rows(
        _load_rows(history_path),
        external_symbol=external_symbol,
        theme=theme,
        threshold=threshold,
        direction=direction,
    )
    return _stats_for_rows(rows, threshold=threshold, direction=direction)


def compute_batch_transmission_stats(
    history_path: str | Path,
    thresholds: tuple[float, ...] = (3.0, 5.0, 8.0),
    direction: str = "up",
    min_events: int = 3,
) -> list[dict[str, Any]]:
    rows = _load_rows(history_path)
    keys = sorted(
        {
            (row.get("external_symbol", "").upper(), row.get("a_share_theme", ""))
            for row in rows
            if row.get("external_symbol") and row.get("a_share_theme")
        }
    )

    results = []
    for external_symbol, theme in keys:
        for threshold in thresholds:
            selected = _select_rows(
                rows,
                external_symbol=external_symbol,
                theme=theme,
                threshold=threshold,
                direction=direction,
            )
            if len(selected) < min_events:
                continue
            stats = _stats_for_rows(selected, threshold=threshold, direction=direction)
            stats["external_symbol"] = external_symbol
            stats["theme"] = theme
            results.append(stats)

    return sorted(
        results,
        key=lambda item: (
            item["edge_score"],
            item["events"],
            item["avg_close_pct"],
        ),
        reverse=True,
    )


def render_batch_stats_markdown(stats: list[dict[str, Any]]) -> str:
    lines = [
        "# 隔夜传导批量回测",
        "",
        "| 外盘代码 | A股主题 | 阈值 | 样本 | 胜率 | 平均开盘 | 平均最高 | 平均收盘 | 最大回撤 | 高开回落 | 边际分 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in stats:
        lines.append(
            f"| {row['external_symbol']} | {row['theme']} | {row['threshold']:.1f}% | "
            f"{row['events']} | {row['win_rate'] * 100:.1f}% | "
            f"{row['avg_open_pct']:+.2f}% | {row['avg_high_pct']:+.2f}% | "
            f"{row['avg_close_pct']:+.2f}% | {row['max_drawdown_pct']:+.2f}% | "
            f"{row['gap_fade_rate'] * 100:.1f}% | {row['edge_score']:.0f} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_historical_edges(stats: list[dict[str, Any]]) -> dict[str, Any]:
    best_by_theme: dict[str, dict[str, Any]] = {}
    per_external_edges: dict[str, dict[str, Any]] = {}

    for row in stats:
        theme = str(row.get("theme", ""))
        if not theme:
            continue
        edge = _edge_payload(row)
        key = f"{row.get('external_symbol')}|{theme}|{row.get('threshold')}"
        per_external_edges[key] = edge
        current = best_by_theme.get(theme)
        if current is None or edge["edge_score"] > current["edge_score"]:
            best_by_theme[theme] = edge

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "historical_edges": best_by_theme,
        "per_external_edges": per_external_edges,
    }


def write_historical_edges_json(path: str | Path, stats: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(build_historical_edges(stats), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_batch_stats_csv(path: str | Path, stats: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not stats:
        target.write_text("", encoding="utf-8")
        return
    fieldnames = [
        "external_symbol",
        "theme",
        "threshold",
        "direction",
        "events",
        "win_rate",
        "avg_open_pct",
        "avg_high_pct",
        "avg_low_pct",
        "avg_close_pct",
        "max_drawdown_pct",
        "gap_fade_rate",
        "edge_score",
    ]
    with target.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in stats:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _edge_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_symbol": row.get("external_symbol"),
        "threshold": row.get("threshold"),
        "direction": row.get("direction"),
        "events": row.get("events", 0),
        "win_rate": row.get("win_rate", 0.0),
        "avg_open_pct": row.get("avg_open_pct", 0.0),
        "avg_high_pct": row.get("avg_high_pct", 0.0),
        "avg_low_pct": row.get("avg_low_pct", 0.0),
        "avg_close_pct": row.get("avg_close_pct", 0.0),
        "max_drawdown_pct": row.get("max_drawdown_pct", 0.0),
        "gap_fade_rate": row.get("gap_fade_rate", 0.0),
        "edge_score": row.get("edge_score", 0.0),
    }


def _select_rows(
    rows: list[dict[str, str]],
    external_symbol: str | None,
    theme: str | None,
    threshold: float,
    direction: str,
) -> list[dict[str, str]]:
    selected = []
    for row in rows:
        if external_symbol and row.get("external_symbol", "").upper() != external_symbol.upper():
            continue
        if theme and row.get("a_share_theme") != theme:
            continue

        change = float(row.get("external_change_pct", 0) or 0)
        if direction == "up" and change < threshold:
            continue
        if direction == "down" and change > -abs(threshold):
            continue
        selected.append(row)
    return selected


def _stats_for_rows(
    selected: list[dict[str, str]],
    threshold: float,
    direction: str,
) -> dict[str, Any]:
    if not selected:
        return {
            "threshold": threshold,
            "direction": direction,
            "events": 0,
            "win_rate": 0.0,
            "avg_open_pct": 0.0,
            "avg_high_pct": 0.0,
            "avg_low_pct": 0.0,
            "avg_close_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "gap_fade_rate": 0.0,
            "edge_score": 0.0,
        }

    open_returns = [_float(row.get("a_open_pct_next")) for row in selected]
    high_returns = [_float(row.get("a_high_pct_next")) for row in selected]
    low_returns = [_float(row.get("a_low_pct_next")) for row in selected]
    close_returns = [_float(row.get("a_close_pct_next")) for row in selected]
    wins = [value > 0 for value in close_returns]
    fades = [
        open_value > 0 and close_value < open_value
        for open_value, close_value in zip(open_returns, close_returns)
    ]

    win_rate = sum(wins) / len(wins)
    avg_close = mean(close_returns)
    gap_fade_rate = sum(fades) / len(fades)
    max_drawdown = min(low_returns)
    edge_score = _edge_score(
        events=len(selected),
        win_rate=win_rate,
        avg_close_pct=avg_close,
        avg_high_pct=mean(high_returns),
        max_drawdown_pct=max_drawdown,
        gap_fade_rate=gap_fade_rate,
    )

    return {
        "threshold": round(threshold, 4),
        "direction": direction,
        "events": len(selected),
        "win_rate": round(win_rate, 4),
        "avg_open_pct": round(mean(open_returns), 4),
        "avg_high_pct": round(mean(high_returns), 4),
        "avg_low_pct": round(mean(low_returns), 4),
        "avg_close_pct": round(avg_close, 4),
        "max_drawdown_pct": round(max_drawdown, 4),
        "gap_fade_rate": round(gap_fade_rate, 4),
        "edge_score": round(edge_score, 2),
    }


def _edge_score(
    events: int,
    win_rate: float,
    avg_close_pct: float,
    avg_high_pct: float,
    max_drawdown_pct: float,
    gap_fade_rate: float,
) -> float:
    sample_score = min(15.0, events * 2.0)
    score = sample_score
    score += win_rate * 45.0
    score += max(0.0, min(20.0, (avg_close_pct + 1.0) * 7.0))
    score += max(0.0, min(10.0, avg_high_pct * 1.5))
    score -= max(0.0, gap_fade_rate - 0.35) * 18.0
    score -= max(0.0, abs(max_drawdown_pct) - 3.0) * 1.5
    return max(0.0, min(100.0, score))


def _float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def _load_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
