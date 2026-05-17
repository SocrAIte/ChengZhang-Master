from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .dashboard_contract import normalize_dashboard_data


HISTORY_SCHEMA_VERSION = "1.0"
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def build_theme_history(reports_dir: str | Path) -> dict[str, Any]:
    runs = _load_dashboard_runs(Path(reports_dir))
    themes: dict[str, dict[str, Any]] = {}
    for run_date, dashboard_data in runs:
        seen_in_run: set[str] = set()
        for signal in _signals(dashboard_data):
            theme = _theme_name(signal)
            item = themes.setdefault(theme, _theme_bucket(theme))
            item["signal_count"] += 1
            seen_in_run.add(theme)
            _add_score(item, signal.get("score"))
            _count(item["strength_counts"], signal.get("strength"))
            _count(item["risk_counts"], signal.get("risk_level"))
            _count(item["intraday_status_counts"], signal.get("intraday_status") or signal.get("status") or "not_checked")
            _count(item["data_status_counts"], signal.get("data_status"))
            _extend_unique(item["external_triggers"], _as_list(signal.get("external_triggers")))
            item["etf_candidate_count"] += len(_as_list(signal.get("etf_candidates")))
            item["stock_candidate_count"] += len(_as_list(signal.get("stock_candidates")))
            _extend_unique(item["recent_dates"], [run_date])
        for theme in seen_in_run:
            themes[theme]["runs_seen"] += 1

    theme_rows = [_finalize_theme_bucket(bucket) for bucket in themes.values()]
    theme_rows.sort(key=lambda row: (-row["signal_count"], -(row["max_score"] or -1), row["theme"]))
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs_count": len(runs),
        "date_range": _date_range([date for date, _ in runs]),
        "themes": theme_rows,
    }


def build_candidate_history(reports_dir: str | Path) -> dict[str, Any]:
    runs = _load_dashboard_runs(Path(reports_dir))
    etfs: dict[tuple[str, str | None], dict[str, Any]] = {}
    stocks: dict[tuple[str, str | None], dict[str, Any]] = {}
    for run_date, dashboard_data in runs:
        for signal in _signals(dashboard_data):
            theme = _theme_name(signal)
            for candidate in _as_list(signal.get("etf_candidates")):
                _add_candidate(etfs, candidate, theme, run_date)
            for candidate in _as_list(signal.get("stock_candidates")):
                _add_candidate(stocks, candidate, theme, run_date)
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs_count": len(runs),
        "etf_candidates": _finalize_candidates(etfs),
        "stock_candidates": _finalize_candidates(stocks),
    }


def normalize_candidate(candidate: Any) -> dict[str, Any]:
    if isinstance(candidate, dict):
        name = _first_existing(candidate, ("name", "label", "title", "symbol", "ticker", "code")) or "unknown"
        code = _first_existing(candidate, ("code", "ticker", "symbol"))
        return {"name": str(name), "code": str(code) if code else None}
    if candidate is None or candidate == "":
        return {"name": "unknown", "code": None}
    return {"name": str(candidate), "code": None}


def _load_dashboard_runs(reports_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    if not reports_dir.exists():
        return []
    runs: list[tuple[str, dict[str, Any]]] = []
    for run_dir in sorted((path for path in reports_dir.iterdir() if path.is_dir() and _DATE_RE.match(path.name)), key=lambda path: path.name):
        path = run_dir / "dashboard_data.json"
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(payload, dict):
            continue
        runs.append((run_dir.name, normalize_dashboard_data(payload)))
    return runs


def _signals(dashboard_data: dict[str, Any]) -> list[dict[str, Any]]:
    signals = dashboard_data.get("signals")
    return [item for item in signals if isinstance(item, dict)] if isinstance(signals, list) else []


def _theme_name(signal: dict[str, Any]) -> str:
    value = signal.get("theme")
    return str(value).strip() if value not in (None, "") else "Unknown Theme"


def _theme_bucket(theme: str) -> dict[str, Any]:
    return {
        "theme": theme,
        "signal_count": 0,
        "runs_seen": 0,
        "scores": [],
        "strength_counts": Counter(),
        "risk_counts": Counter(),
        "intraday_status_counts": Counter(),
        "data_status_counts": Counter(),
        "external_triggers": [],
        "etf_candidate_count": 0,
        "stock_candidate_count": 0,
        "recent_dates": [],
    }


def _finalize_theme_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    scores = bucket.pop("scores")
    recent_dates = sorted(bucket["recent_dates"], reverse=True)
    return {
        "theme": bucket["theme"],
        "signal_count": bucket["signal_count"],
        "runs_seen": bucket["runs_seen"],
        "avg_score": round(sum(scores) / len(scores), 2) if scores else None,
        "max_score": round(max(scores), 2) if scores else None,
        "strength_counts": dict(bucket["strength_counts"]),
        "risk_counts": dict(bucket["risk_counts"]),
        "intraday_status_counts": dict(bucket["intraday_status_counts"]),
        "data_status_counts": dict(bucket["data_status_counts"]),
        "external_triggers": bucket["external_triggers"][:20],
        "etf_candidate_count": bucket["etf_candidate_count"],
        "stock_candidate_count": bucket["stock_candidate_count"],
        "recent_dates": recent_dates[:5],
        "last_seen": recent_dates[0] if recent_dates else None,
    }


def _add_candidate(store: dict[tuple[str, str | None], dict[str, Any]], candidate: Any, theme: str, run_date: str) -> None:
    normalized = normalize_candidate(candidate)
    key = (normalized["name"], normalized["code"])
    item = store.setdefault(key, {"name": normalized["name"], "code": normalized["code"], "appearances": 0, "themes": [], "recent_dates": []})
    item["appearances"] += 1
    _extend_unique(item["themes"], [theme])
    _extend_unique(item["recent_dates"], [run_date])


def _finalize_candidates(store: dict[tuple[str, str | None], dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in store.values():
        recent_dates = sorted(item["recent_dates"], reverse=True)
        rows.append(
            {
                "name": item["name"],
                "code": item["code"],
                "appearances": item["appearances"],
                "themes": sorted(item["themes"]),
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
            }
        )
    rows.sort(key=lambda row: (-row["appearances"], row["name"]))
    return rows


def _date_range(dates: list[str]) -> dict[str, str | None]:
    if not dates:
        return {"start": None, "end": None}
    return {"start": min(dates), "end": max(dates)}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _add_score(bucket: dict[str, Any], value: Any) -> None:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return
    bucket["scores"].append(score)


def _count(counter: Counter, value: Any) -> None:
    key = str(value).strip() if value not in (None, "") else "unknown"
    counter[key] += 1


def _extend_unique(values: list[Any], additions: list[Any]) -> None:
    for item in additions:
        if item in (None, ""):
            continue
        label = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False, sort_keys=True)
        if label not in values:
            values.append(label)


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _first_existing(values: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = values.get(key)
        if value not in (None, ""):
            return value
    return None
