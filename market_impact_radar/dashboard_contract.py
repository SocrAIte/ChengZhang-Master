from __future__ import annotations

from typing import Any


DASHBOARD_SCHEMA_VERSION = "1.0"


def build_dashboard_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    return normalize_dashboard_data(raw_data)


def normalize_dashboard_data(data: dict[str, Any] | None) -> dict[str, Any]:
    source = data if isinstance(data, dict) else {}
    return {
        "schema_version": str(source.get("schema_version") or DASHBOARD_SCHEMA_VERSION),
        "run": _normalize_run(source),
        "market_context": _normalize_market_context(source.get("market_context")),
        "summary": _normalize_summary(source),
        "signals": _normalize_signals(source),
        "knowledge": _normalize_knowledge(source),
        "outputs": _normalize_outputs(source),
    }


def validate_dashboard_data(data: dict[str, Any]) -> list[dict[str, str]]:
    if not isinstance(data, dict):
        return [_issue("error", "$", "dashboard_data must be a dict")]

    issues: list[dict[str, str]] = []
    if "schema_version" not in data:
        issues.append(_issue("warning", "schema_version", "missing schema_version"))
    elif str(data.get("schema_version")) != DASHBOARD_SCHEMA_VERSION:
        issues.append(_issue("warning", "schema_version", f"unsupported schema_version {data.get('schema_version')}"))

    _expect_type(data, "run", dict, issues)
    _expect_type(data, "summary", dict, issues)
    _expect_type(data, "knowledge", dict, issues)
    _expect_type(data, "outputs", dict, issues)

    signals = data.get("signals")
    if not isinstance(signals, list):
        issues.append(_issue("error", "signals", "signals must be a list"))
        return issues

    for index, item in enumerate(signals):
        field = f"signals[{index}]"
        if not isinstance(item, dict):
            issues.append(_issue("error", field, "signal item must be a dict"))
            continue
        if not item.get("theme"):
            issues.append(_issue("warning", f"{field}.theme", "missing theme"))
        if "intraday_status" not in item:
            issues.append(_issue("warning", f"{field}.intraday_status", "missing intraday_status; defaults to not_checked"))
        if "risk_level" not in item:
            issues.append(_issue("warning", f"{field}.risk_level", "missing risk_level; defaults to unknown"))
    return issues


def _normalize_run(source: dict[str, Any]) -> dict[str, Any]:
    run = _safe_dict(source.get("run"))
    run_summary = _safe_dict(source.get("run_summary"))
    return {
        "date": run.get("date") or source.get("run_date") or run_summary.get("run_date"),
        "generated_at": run.get("generated_at") or source.get("generated_at") or run_summary.get("generated_at"),
        "status": str(run.get("status") or source.get("status") or run_summary.get("status") or "unknown"),
        "warnings": _as_list(run.get("warnings") or source.get("warnings") or run_summary.get("warnings")),
    }


def _normalize_market_context(value: Any) -> dict[str, Any]:
    context = _safe_dict(value)
    sessions = context.get("foreign_market_context")
    if isinstance(sessions, list):
        foreign_market_context = [_safe_dict(item) for item in sessions]
    else:
        foreign_market_context = [
            {"market": market, **_safe_dict(payload)}
            for market, payload in _safe_dict(context.get("external_sessions")).items()
        ]
    return {
        "a_share_trading_day": context.get("a_share_trading_day") or context.get("a_share_trade_day"),
        "is_a_share_trading_day": context.get("is_a_share_trading_day"),
        "foreign_market_context": foreign_market_context,
        "sources": _as_list(context.get("sources") or context.get("source")),
        "fetched_at": _as_list(context.get("fetched_at") or context.get("updated_at")),
    }


def _normalize_summary(source: dict[str, Any]) -> dict[str, int]:
    provided = _safe_dict(source.get("summary"))
    if provided:
        return {
            "strong_signals": _int(provided.get("strong_signals")),
            "confirmed": _int(provided.get("confirmed")),
            "downgraded": _int(provided.get("downgraded")),
            "failed": _int(provided.get("failed")),
            "missing_data": _int(provided.get("missing_data")),
            "knowledge_issues": _int(provided.get("knowledge_issues")),
        }

    evaluations = [_safe_dict(item) for item in _as_list(_safe_dict(source.get("intraday_evaluation")).get("evaluations"))]
    status_counts: dict[str, int] = {}
    for row in evaluations:
        status = str(row.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    knowledge = _safe_dict(source.get("knowledge") or source.get("knowledge_verification"))
    knowledge_counts = _safe_dict(knowledge.get("quality_counts"))
    return {
        "strong_signals": sum(1 for event in _as_list(source.get("events")) if _safe_dict(event).get("tier") == "strong"),
        "confirmed": status_counts.get("confirmed", 0),
        "downgraded": status_counts.get("downgraded", 0),
        "failed": status_counts.get("failed", 0),
        "missing_data": status_counts.get("missing", 0),
        "knowledge_issues": _int(knowledge_counts.get("total") or len(_as_list(knowledge.get("issues")))),
    }


def _normalize_signals(source: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(source.get("signals"), list):
        return [_normalize_signal(_safe_dict(item)) for item in source["signals"]]

    external_by_symbol = {
        str(_safe_dict(item).get("symbol") or ""): _safe_dict(item)
        for item in _as_list(source.get("external_assets"))
    }
    intraday_by_theme = {
        str(_safe_dict(item).get("theme") or ""): _safe_dict(item)
        for item in _as_list(_safe_dict(source.get("intraday_evaluation")).get("evaluations"))
    }
    etfs = _candidates_by_theme(source.get("etf_candidates"))
    stocks = _candidates_by_theme(source.get("stock_candidates"))
    signals = []
    for item in _as_list(source.get("scored_themes")):
        theme = _safe_dict(item)
        theme_name = theme.get("theme")
        triggers = [str(symbol) for symbol in _as_list(theme.get("trigger_assets"))]
        assets = [external_by_symbol.get(symbol, {}) for symbol in triggers]
        statuses = sorted({str(asset.get("data_status")) for asset in assets if asset.get("data_status")})
        sources = sorted({str(asset.get("source")) for asset in assets if asset.get("source")})
        fetched_at = sorted({str(asset.get("fetched_at")) for asset in assets if asset.get("fetched_at")})
        intraday = intraday_by_theme.get(str(theme_name), {})
        risks = _as_list(theme.get("risks")) + [
            str(detail.get("message"))
            for detail in (_safe_dict(detail) for detail in _as_list(theme.get("risk_details")))
            if detail.get("message")
        ]
        mapping = _safe_dict(theme.get("mapping"))
        signals.append(
            _normalize_signal(
                {
                    "theme": theme_name,
                    "strength": theme.get("signal_strength"),
                    "score": theme.get("score"),
                    "external_triggers": triggers,
                    "a_share_mapping_reason": _as_list(theme.get("reasons")) or _as_list(mapping.get("industries")),
                    "etf_candidates": etfs.get(str(theme_name), _as_list(mapping.get("etfs"))),
                    "stock_candidates": stocks.get(str(theme_name), _stock_names(mapping.get("stocks"))),
                    "intraday_status": intraday.get("status") or "not_checked",
                    "risk_level": _risk_level(risks, intraday),
                    "risks": risks,
                    "data_status": ",".join(statuses) if statuses else "unknown",
                    "sources": sources,
                    "fetched_at": fetched_at,
                }
            )
        )
    return signals


def _normalize_signal(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "theme": item.get("theme"),
        "strength": item.get("strength") if item.get("strength") is not None else "unknown",
        "score": item.get("score"),
        "external_triggers": _as_list(item.get("external_triggers")),
        "a_share_mapping_reason": _as_list(item.get("a_share_mapping_reason")),
        "etf_candidates": _as_list(item.get("etf_candidates")),
        "stock_candidates": _as_list(item.get("stock_candidates")),
        "intraday_status": str(item.get("intraday_status") or "not_checked"),
        "risk_level": str(item.get("risk_level") or "unknown"),
        "risks": _as_list(item.get("risks")),
        "data_status": str(item.get("data_status") or "unknown"),
        "sources": _as_list(item.get("sources")),
        "fetched_at": _as_list(item.get("fetched_at")),
    }


def _normalize_knowledge(source: dict[str, Any]) -> dict[str, Any]:
    knowledge = _safe_dict(source.get("knowledge") or source.get("knowledge_verification"))
    issues = _as_list(knowledge.get("issues"))
    suggestions = _as_list(knowledge.get("suggestions"))
    counts = _safe_dict(knowledge.get("quality_counts"))
    if not knowledge:
        status = "unknown"
    else:
        status = str(knowledge.get("status") or ("issues" if _int(counts.get("total") or len(issues)) else "ok"))
    return {
        "status": status,
        "issues": issues,
        "suggestions": suggestions,
    }


def _normalize_outputs(source: dict[str, Any]) -> dict[str, Any]:
    outputs = _safe_dict(source.get("outputs") or _safe_dict(source.get("run_summary")).get("outputs"))
    return {
        "report_md": outputs.get("report_md"),
        "dashboard_html": outputs.get("dashboard_html"),
    }


def _candidates_by_theme(value: Any) -> dict[str, list[str]]:
    by_theme: dict[str, list[str]] = {}
    for item in _as_list(value):
        row = _safe_dict(item)
        theme = str(row.get("theme") or "")
        name = str(row.get("name") or "")
        if theme and name:
            by_theme.setdefault(theme, []).append(name)
    return by_theme


def _stock_names(value: Any) -> list[str]:
    names = []
    for item in _as_list(value):
        if isinstance(item, dict):
            names.append(str(item.get("name") or item.get("code") or ""))
        else:
            names.append(str(item))
    return [name for name in names if name]


def _risk_level(risks: list[Any], intraday: dict[str, Any]) -> str:
    status = str(intraday.get("status") or "")
    if status in {"failed", "downgraded", "missing"}:
        return status
    return "flagged" if risks else "watch"


def _expect_type(data: dict[str, Any], field: str, expected_type: type, issues: list[dict[str, str]]) -> None:
    if not isinstance(data.get(field), expected_type):
        issues.append(_issue("error", field, f"{field} must be a {expected_type.__name__}"))


def _issue(level: str, field: str, message: str) -> dict[str, str]:
    return {"level": level, "field": field, "message": message}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
