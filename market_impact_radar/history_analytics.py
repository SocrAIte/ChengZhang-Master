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


def build_data_quality_history(reports_dir: str | Path) -> dict[str, Any]:
    runs = _load_dashboard_runs(Path(reports_dir))
    data_status_counts: Counter = Counter()
    source_counts: Counter = Counter()
    missing_source_count = 0
    missing_fetched_at_count = 0
    fallback_count = 0
    themes: dict[str, dict[str, Any]] = {}

    for run_date, dashboard_data in runs:
        for signal in _signals(dashboard_data):
            theme = _theme_name(signal)
            data_status = _data_status(signal)
            sources = _source_values(signal)
            fetched_at = _fetched_values(signal)
            fallback_used = _fallback_used(signal)

            _count(data_status_counts, data_status)
            if sources:
                for source in sources:
                    _count(source_counts, source)
            else:
                missing_source_count += 1
                _count(source_counts, "Unknown Source")
            if not fetched_at:
                missing_fetched_at_count += 1
            if fallback_used:
                fallback_count += 1

            if _is_weak_data_status(data_status) or not sources or not fetched_at or fallback_used:
                bucket = themes.setdefault(theme, _weak_theme_bucket(theme))
                bucket["weak_signal_count"] += 1
                _count(bucket["data_status_counts"], data_status)
                _extend_unique(bucket["recent_dates"], [run_date])

    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs_count": len(runs),
        "date_range": _date_range([date for date, _ in runs]),
        "data_status_counts": dict(data_status_counts),
        "source_counts": dict(source_counts),
        "missing_source_count": missing_source_count,
        "missing_fetched_at_count": missing_fetched_at_count,
        "fallback_count": fallback_count,
        "themes_with_weak_data": _finalize_weak_themes(themes),
    }


def build_source_history(reports_dir: str | Path) -> dict[str, Any]:
    runs = _load_dashboard_runs(Path(reports_dir))
    sources: dict[str, dict[str, Any]] = {}
    for run_date, dashboard_data in runs:
        for signal in _signals(dashboard_data):
            source_values = _source_values(signal) or ["Unknown Source"]
            for source in source_values:
                bucket = sources.setdefault(source, _source_bucket(source))
                bucket["signal_count"] += 1
                _extend_unique(bucket["themes"], [_theme_name(signal)])
                _extend_unique(bucket["dates"], [run_date])
                _count(bucket["data_status_counts"], _data_status(signal))
                _count(bucket["risk_counts"], signal.get("risk_level"))
                _count(bucket["intraday_status_counts"], signal.get("intraday_status") or signal.get("status") or "not_checked")
                fetched_values = _fetched_values(signal)
                for fetched_at in fetched_values:
                    if not bucket["latest_fetched_at"] or fetched_at > bucket["latest_fetched_at"]:
                        bucket["latest_fetched_at"] = fetched_at
                if not _source_values(signal):
                    bucket["missing_source_count"] += 1
                if not fetched_values:
                    bucket["missing_fetched_at_count"] += 1
                if _fallback_used(signal):
                    bucket["fallback_count"] += 1
                if _is_weak_data_status(_data_status(signal)) or not _source_values(signal) or not fetched_values or _fallback_used(signal):
                    bucket["weak_signal_count"] += 1
                bucket["example_signals"].append(_source_example_signal(run_date, signal))

    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs_count": len(runs),
        "date_range": _date_range([date for date, _ in runs]),
        "sources": _finalize_sources(sources),
    }


def build_theme_source_matrix(reports_dir: str | Path) -> dict[str, Any]:
    runs = _load_dashboard_runs(Path(reports_dir))
    themes: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, Any]] = {}
    matrix: dict[tuple[str, str], dict[str, Any]] = {}

    for run_date, dashboard_data in runs:
        for signal in _signals(dashboard_data):
            theme = _theme_name(signal)
            source_values = _source_values(signal) or ["Unknown Source"]
            fetched_values = _fetched_values(signal)
            data_status = _data_status(signal)
            fallback_used = _fallback_used(signal)
            weak_signal = _is_weak_data_status(data_status) or not _source_values(signal) or not fetched_values or fallback_used

            theme_bucket = themes.setdefault(theme, _matrix_theme_bucket(theme))
            theme_bucket["signal_count"] += 1
            _extend_unique(theme_bucket["dates"], [run_date])
            _extend_unique(theme_bucket["sources"], source_values)
            _count(theme_bucket["data_status_counts"], data_status)
            if not _source_values(signal):
                theme_bucket["missing_source_count"] += 1
            if not fetched_values:
                theme_bucket["missing_fetched_at_count"] += 1
            if fallback_used:
                theme_bucket["fallback_count"] += 1
            if weak_signal:
                theme_bucket["weak_signal_count"] += 1
            _update_latest_fetched(theme_bucket, fetched_values)

            for source in source_values:
                source_bucket = sources.setdefault(source, _matrix_source_bucket(source))
                source_bucket["signal_count"] += 1
                _extend_unique(source_bucket["themes"], [theme])
                _extend_unique(source_bucket["dates"], [run_date])
                _count(source_bucket["data_status_counts"], data_status)
                if not fetched_values:
                    source_bucket["missing_fetched_at_count"] += 1
                if fallback_used:
                    source_bucket["fallback_count"] += 1
                if weak_signal:
                    source_bucket["weak_signal_count"] += 1
                _update_latest_fetched(source_bucket, fetched_values)

                cell = matrix.setdefault((theme, source), _matrix_cell_bucket(theme, source))
                cell["signal_count"] += 1
                _extend_unique(cell["dates"], [run_date])
                _count(cell["data_status_counts"], data_status)
                if not fetched_values:
                    cell["missing_fetched_at_count"] += 1
                if fallback_used:
                    cell["fallback_count"] += 1
                if weak_signal:
                    cell["weak_signal_count"] += 1
                _update_latest_fetched(cell, fetched_values)
                example = _source_example_signal(run_date, signal)
                example["source"] = source
                cell["example_signals"].append(example)

    matrix_rows = _finalize_matrix_cells(matrix)
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs_count": len(runs),
        "date_range": _date_range([date for date, _ in runs]),
        "themes": _finalize_matrix_themes(themes),
        "sources": _finalize_matrix_sources(sources),
        "matrix": matrix_rows,
        "weak_cells": _weak_cells(matrix_rows),
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


def _weak_theme_bucket(theme: str) -> dict[str, Any]:
    return {
        "theme": theme,
        "weak_signal_count": 0,
        "recent_dates": [],
        "data_status_counts": Counter(),
    }


def _source_bucket(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "signal_count": 0,
        "themes": [],
        "dates": [],
        "latest_fetched_at": None,
        "data_status_counts": Counter(),
        "risk_counts": Counter(),
        "intraday_status_counts": Counter(),
        "fallback_count": 0,
        "missing_source_count": 0,
        "missing_fetched_at_count": 0,
        "weak_signal_count": 0,
        "example_signals": [],
    }


def _matrix_theme_bucket(theme: str) -> dict[str, Any]:
    return {
        "theme": theme,
        "signal_count": 0,
        "sources": [],
        "dates": [],
        "missing_source_count": 0,
        "missing_fetched_at_count": 0,
        "fallback_count": 0,
        "weak_signal_count": 0,
        "data_status_counts": Counter(),
        "latest_fetched_at": None,
    }


def _matrix_source_bucket(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "signal_count": 0,
        "themes": [],
        "dates": [],
        "missing_fetched_at_count": 0,
        "fallback_count": 0,
        "weak_signal_count": 0,
        "data_status_counts": Counter(),
        "latest_fetched_at": None,
    }


def _matrix_cell_bucket(theme: str, source: str) -> dict[str, Any]:
    return {
        "theme": theme,
        "source": source,
        "signal_count": 0,
        "data_status_counts": Counter(),
        "missing_fetched_at_count": 0,
        "fallback_count": 0,
        "weak_signal_count": 0,
        "latest_fetched_at": None,
        "dates": [],
        "example_signals": [],
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


def _finalize_weak_themes(themes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bucket in themes.values():
        recent_dates = sorted(bucket["recent_dates"], reverse=True)
        rows.append(
            {
                "theme": bucket["theme"],
                "weak_signal_count": bucket["weak_signal_count"],
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
                "data_status_counts": dict(bucket["data_status_counts"]),
            }
        )
    rows.sort(key=lambda row: (-row["weak_signal_count"], row["theme"]))
    return rows


def _finalize_matrix_themes(themes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bucket in themes.values():
        recent_dates = sorted(bucket["dates"], reverse=True)
        sources = sorted(bucket["sources"])
        rows.append(
            {
                "theme": bucket["theme"],
                "signal_count": bucket["signal_count"],
                "source_count": len(sources),
                "sources": sources,
                "missing_source_count": bucket["missing_source_count"],
                "missing_fetched_at_count": bucket["missing_fetched_at_count"],
                "fallback_count": bucket["fallback_count"],
                "weak_signal_count": bucket["weak_signal_count"],
                "data_status_counts": dict(bucket["data_status_counts"]),
                "latest_fetched_at": bucket["latest_fetched_at"],
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
            }
        )
    rows.sort(key=lambda row: (-row["weak_signal_count"], -row["signal_count"], row["theme"]))
    return rows


def _finalize_matrix_sources(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bucket in sources.values():
        recent_dates = sorted(bucket["dates"], reverse=True)
        themes = sorted(bucket["themes"])
        rows.append(
            {
                "source": bucket["source"],
                "signal_count": bucket["signal_count"],
                "theme_count": len(themes),
                "themes": themes,
                "missing_fetched_at_count": bucket["missing_fetched_at_count"],
                "fallback_count": bucket["fallback_count"],
                "weak_signal_count": bucket["weak_signal_count"],
                "data_status_counts": dict(bucket["data_status_counts"]),
                "latest_fetched_at": bucket["latest_fetched_at"],
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
            }
        )
    rows.sort(key=lambda row: (-row["signal_count"], row["source"]))
    return rows


def _finalize_matrix_cells(matrix: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bucket in matrix.values():
        recent_dates = sorted(bucket["dates"], reverse=True)
        examples = sorted(bucket["example_signals"], key=lambda item: item["date"], reverse=True)[:3]
        rows.append(
            {
                "theme": bucket["theme"],
                "source": bucket["source"],
                "signal_count": bucket["signal_count"],
                "data_status_counts": dict(bucket["data_status_counts"]),
                "missing_fetched_at_count": bucket["missing_fetched_at_count"],
                "fallback_count": bucket["fallback_count"],
                "weak_signal_count": bucket["weak_signal_count"],
                "latest_fetched_at": bucket["latest_fetched_at"],
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
                "example_signals": examples,
            }
        )
    rows.sort(key=lambda row: (-row["weak_signal_count"], -row["signal_count"], row["theme"], row["source"]))
    return rows


def _weak_cells(matrix_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for cell in matrix_rows:
        reasons = _matrix_weak_reasons(cell)
        if not reasons:
            continue
        rows.append(
            {
                "theme": cell["theme"],
                "source": cell["source"],
                "reason": ", ".join(reasons),
                "weak_signal_count": cell["weak_signal_count"],
                "missing_fetched_at_count": cell["missing_fetched_at_count"],
                "fallback_count": cell["fallback_count"],
                "data_status_counts": cell["data_status_counts"],
                "recent_dates": cell["recent_dates"],
            }
        )
    rows.sort(key=lambda row: (-row["weak_signal_count"], -row["missing_fetched_at_count"], row["theme"], row["source"]))
    return rows


def _matrix_weak_reasons(cell: dict[str, Any]) -> list[str]:
    reasons = []
    source = str(cell.get("source") or "")
    counts = cell.get("data_status_counts") if isinstance(cell.get("data_status_counts"), dict) else {}
    weak_statuses = [status for status in counts if str(status).lower() in {"missing", "missing_data", "partial", "stale", "failed", "unknown"}]
    if source == "Unknown Source":
        reasons.append("Missing source")
    if cell.get("missing_fetched_at_count"):
        reasons.append("Missing fetched_at")
    if weak_statuses:
        reasons.append("Partial, stale, missing, failed, or unknown data")
    if cell.get("fallback_count"):
        reasons.append("Fallback used")
    return reasons


def _update_latest_fetched(bucket: dict[str, Any], fetched_values: list[str]) -> None:
    for fetched_at in fetched_values:
        if not bucket["latest_fetched_at"] or fetched_at > bucket["latest_fetched_at"]:
            bucket["latest_fetched_at"] = fetched_at


def _finalize_sources(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for bucket in sources.values():
        dates = sorted(bucket["dates"])
        recent_dates = sorted(bucket["dates"], reverse=True)
        examples = sorted(bucket["example_signals"], key=lambda item: item["date"], reverse=True)[:5]
        rows.append(
            {
                "source": bucket["source"],
                "signal_count": bucket["signal_count"],
                "themes": sorted(bucket["themes"]),
                "dates": dates,
                "recent_dates": recent_dates[:5],
                "last_seen": recent_dates[0] if recent_dates else None,
                "latest_fetched_at": bucket["latest_fetched_at"],
                "data_status_counts": dict(bucket["data_status_counts"]),
                "risk_counts": dict(bucket["risk_counts"]),
                "intraday_status_counts": dict(bucket["intraday_status_counts"]),
                "fallback_count": bucket["fallback_count"],
                "missing_source_count": bucket["missing_source_count"],
                "missing_fetched_at_count": bucket["missing_fetched_at_count"],
                "weak_signal_count": bucket["weak_signal_count"],
                "example_signals": examples,
            }
        )
    rows.sort(key=lambda row: (-row["signal_count"], row["source"]))
    return rows


def _source_example_signal(run_date: str, signal: dict[str, Any]) -> dict[str, Any]:
    fetched_values = _fetched_values(signal)
    return {
        "date": run_date,
        "theme": _theme_name(signal),
        "strength": signal.get("strength") or "unknown",
        "score": signal.get("score"),
        "risk_level": signal.get("risk_level") or "unknown",
        "intraday_status": signal.get("intraday_status") or signal.get("status") or "not_checked",
        "data_status": _data_status(signal),
        "fetched_at": fetched_values[0] if fetched_values else None,
        "fallback_used": signal.get("fallback_used"),
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


def _source_values(signal: dict[str, Any]) -> list[str]:
    return [str(item).strip() for item in _as_list(signal.get("sources") or signal.get("source")) if str(item).strip()]


def _fetched_values(signal: dict[str, Any]) -> list[str]:
    return [str(item).strip() for item in _as_list(signal.get("fetched_at") or signal.get("fetchedAt")) if str(item).strip()]


def _data_status(signal: dict[str, Any]) -> str:
    value = signal.get("data_status")
    return str(value).strip() if value not in (None, "") else "unknown"


def _fallback_used(signal: dict[str, Any]) -> bool:
    value = signal.get("fallback_used")
    return value is True or str(value).strip().lower() == "true"


def _is_weak_data_status(value: Any) -> bool:
    return str(value or "unknown").strip().lower() in {"missing", "missing_data", "partial", "stale", "failed", "unknown"}


def _first_existing(values: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = values.get(key)
        if value not in (None, ""):
            return value
    return None
