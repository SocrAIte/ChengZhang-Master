from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from .a_share_sources import fetch_a_share_snapshot
from .dashboard import render_dashboard_from_data
from .dashboard_contract import build_dashboard_data as build_dashboard_contract_data
from .dashboard_contract import validate_dashboard_data
from .history_index import write_daily_history_index
from .intraday import evaluate_intraday, summarize_intraday_evaluation
from .io import load_json, load_mappings, write_text
from .knowledge_review import write_knowledge_review_html
from .knowledge_verifier import suggest_mapping_fixes, verify_knowledge_graph
from .models import Candidate, ScoredTheme, TransmissionEvent
from .pipeline import run_report_pipeline
from .quote_sources import fetch_external_snapshot


@dataclass(frozen=True)
class DailyRunOptions:
    run_date: str | None = None
    output_root: str | Path = "reports/daily"
    mapping_path: str | Path = "data/mappings.json"
    external_path: str | Path | None = None
    context_path: str | Path | None = None
    historical_edges_path: str | Path | None = None
    scoring_rules_path: str | Path | None = "data/scoring_rules.json"
    a_share_watchlist_path: str | Path = "data/a_share_watchlist.sample.json"
    a_share_snapshot_path: str | Path | None = None
    generated_dir: str | Path = "data/generated"
    sources: tuple[str, ...] = ("yahoo",)
    symbols: tuple[str, ...] = ()
    max_source_diff_pct: float = 0.5
    max_age_minutes: int = 180
    alpha_vantage_key: str | None = None
    polygon_key: str | None = None
    proxy: str | None = None
    skip_a_share: bool = False
    skip_knowledge: bool = False


def run_daily(options: DailyRunOptions) -> dict[str, Any]:
    run_date = options.run_date or date.today().isoformat()
    generated_at = _now_iso()
    output_dir = Path(options.output_root) / run_date
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "run_date": run_date,
        "generated_at": generated_at,
        "output_dir": str(output_dir),
        "status": "ok",
        "warnings": [],
        "steps": {},
        "outputs": {
            "run_summary": str(output_dir / "run_summary.json"),
            "dashboard_data": str(output_dir / "dashboard_data.json"),
            "dashboard_html": str(output_dir / "dashboard.html"),
            "knowledge_review_html": str(output_dir / "knowledge_review.html"),
        },
    }
    dashboard_data: dict[str, Any] = {
        "run_date": run_date,
        "generated_at": generated_at,
        "status": "ok",
        "warnings": [],
        "market_context": {},
        "events": [],
        "scored_themes": [],
        "etf_candidates": [],
        "stock_candidates": [],
        "intraday_evaluation": None,
        "knowledge_verification": None,
    }
    knowledge_review_payload: dict[str, Any] | None = {"status": "not_available", "issues": [], "suggestions": []}
    knowledge_review_suggestions: dict[str, Any] | list[Any] | None = None

    try:
        external_path, external_step = _prepare_external_snapshot(options, output_dir)
        summary["steps"]["external"] = external_step
        _apply_step_status(summary, external_step)

        result = run_report_pipeline(
            str(external_path),
            str(options.mapping_path),
            str(options.context_path) if options.context_path else None,
            str(options.historical_edges_path) if options.historical_edges_path else None,
            str(options.scoring_rules_path) if options.scoring_rules_path else None,
        )
        summary["steps"]["pipeline"] = {
            "status": "ok",
            "as_of": result.as_of,
            "events": len(result.events),
            "scored_themes": len(result.scored_themes),
            "etf_candidates": len(result.etf_candidates),
            "stock_candidates": len(result.stock_candidates),
        }
        dashboard_data.update(_build_dashboard_data(result))

        intraday_evaluation = None
        if options.skip_a_share:
            summary["steps"]["a_share"] = {"status": "skipped"}
            summary["steps"]["intraday"] = {"status": "skipped"}
        else:
            a_share_path, a_share_step = _prepare_a_share_snapshot(options, output_dir)
            summary["steps"]["a_share"] = a_share_step
            _apply_step_status(summary, a_share_step)
            if a_share_path:
                intraday_evaluation = evaluate_intraday(result, a_share_path)
                dashboard_data["market_context"] = load_json(a_share_path).get("trading_day_context", {})
                summary["steps"]["intraday"] = {
                    "status": "ok",
                    "as_of": intraday_evaluation.get("as_of", ""),
                    "summary": summarize_intraday_evaluation(intraday_evaluation),
                }
            else:
                summary["steps"]["intraday"] = {"status": "skipped"}
        dashboard_data["intraday_evaluation"] = intraday_evaluation

        if options.skip_knowledge:
            summary["steps"]["knowledge"] = {"status": "skipped"}
            knowledge_review_payload = {
                "status": "skipped",
                "quality_counts": {"high": 0, "medium": 0, "low": 0, "total": 0},
                "issues": [],
                "suggestions": [],
            }
        else:
            knowledge = _verify_knowledge(options)
            knowledge_suggestions = suggest_mapping_fixes(knowledge)
            knowledge_status = _knowledge_status(knowledge)
            summary["steps"]["knowledge"] = {
                "status": knowledge_status,
                "quality_counts": knowledge.get("quality_counts", {}),
                "source_summary": knowledge.get("source_summary", {}),
            }
            _apply_step_status(summary, summary["steps"]["knowledge"])
            knowledge_review_payload = knowledge
            knowledge_review_suggestions = knowledge_suggestions
            dashboard_data["knowledge_verification"] = _knowledge_dashboard_subset(knowledge, knowledge_suggestions)
    except Exception as exc:
        summary["status"] = "error"
        summary.setdefault("errors", []).append(str(exc))
        dashboard_data["status"] = "error"
        dashboard_data["errors"] = list(summary.get("errors", []))

    summary["warnings"] = _collect_warnings(summary)
    dashboard_data["status"] = summary["status"]
    dashboard_data["warnings"] = list(summary["warnings"])
    dashboard_data["outputs"] = dict(summary["outputs"])
    dashboard_data["run_summary"] = _summary_for_dashboard(summary)
    dashboard_data = build_dashboard_contract_data(dashboard_data)
    contract_issues = validate_dashboard_data(dashboard_data)
    if contract_issues:
        has_errors = any(issue.get("level") == "error" for issue in contract_issues)
        summary["steps"]["dashboard_contract"] = {
            "status": "partial" if has_errors else "ok",
            "issues": contract_issues,
        }
        summary["warnings"].extend(_contract_issue_messages(contract_issues))
        if has_errors and summary["status"] != "error":
            summary["status"] = "partial"
        dashboard_data["run"]["status"] = summary["status"]
        dashboard_data["run"]["warnings"] = list(summary["warnings"])
    try:
        write_knowledge_review_html(output_dir, knowledge_review_payload, knowledge_review_suggestions)
    except Exception as exc:
        summary["warnings"].append(f"knowledge review render failed: {exc}")
        dashboard_data["run"]["warnings"] = list(summary["warnings"])
    _write_json(summary["outputs"]["run_summary"], summary)
    _write_json(summary["outputs"]["dashboard_data"], dashboard_data)
    write_text(summary["outputs"]["dashboard_html"], render_dashboard_from_data(dashboard_data))
    try:
        index_outputs = write_daily_history_index(options.output_root)
        summary["outputs"]["history_index_json"] = str(index_outputs["index_json"])
        summary["outputs"]["history_index_html"] = str(index_outputs["index_html"])
    except Exception as exc:
        summary["warnings"].append(f"history index update failed: {exc}")
    _write_json(summary["outputs"]["run_summary"], summary)
    return summary


def _prepare_external_snapshot(options: DailyRunOptions, output_dir: Path) -> tuple[Path, dict[str, Any]]:
    if options.external_path:
        snapshot_path = Path(options.external_path)
        snapshot = load_json(snapshot_path)
        status = _snapshot_status(snapshot)
        return snapshot_path, {
            "status": status,
            "mode": "provided",
            "path": str(snapshot_path),
            "quality": _snapshot_quality(snapshot),
        }

    config = load_mappings(options.mapping_path)
    symbols = options.symbols or tuple(str(item["symbol"]).upper() for item in config.get("external_assets", []))
    snapshot = fetch_external_snapshot(
        symbols=symbols,
        config=config,
        sources=options.sources,
        max_source_diff_pct=options.max_source_diff_pct,
        max_age_minutes=options.max_age_minutes,
        alpha_vantage_key=options.alpha_vantage_key,
        polygon_key=options.polygon_key,
        proxy=options.proxy,
    )
    snapshot_path = output_dir / "external_snapshot.json"
    _write_json(snapshot_path, snapshot)
    return snapshot_path, {
        "status": _snapshot_status(snapshot),
        "mode": "fetched",
        "path": str(snapshot_path),
        "quality": _snapshot_quality(snapshot),
    }


def _prepare_a_share_snapshot(options: DailyRunOptions, output_dir: Path) -> tuple[Path | None, dict[str, Any]]:
    if options.a_share_snapshot_path:
        snapshot_path = Path(options.a_share_snapshot_path)
        snapshot = load_json(snapshot_path)
        return snapshot_path, {
            "status": _snapshot_status(snapshot),
            "mode": "provided",
            "path": str(snapshot_path),
            "quality": _snapshot_quality(snapshot),
        }

    watchlist = load_json(options.a_share_watchlist_path)
    snapshot = fetch_a_share_snapshot(watchlist=watchlist, proxy=options.proxy)
    snapshot_path = output_dir / "a_share_snapshot.json"
    _write_json(snapshot_path, snapshot)
    return snapshot_path, {
        "status": _snapshot_status(snapshot),
        "mode": "fetched",
        "path": str(snapshot_path),
        "quality": _snapshot_quality(snapshot),
    }


def _verify_knowledge(options: DailyRunOptions) -> dict[str, Any]:
    return verify_knowledge_graph(
        mapping_path=options.mapping_path,
        generated_dir=options.generated_dir,
        refresh_apis=False,
        proxy=options.proxy,
    )


def _build_dashboard_data(result: Any) -> dict[str, Any]:
    return {
        "as_of": result.as_of,
        "external_data_quality": result.context.get("external_data_quality", {}),
        "external_assets": [asdict(asset) for asset in result.external_assets],
        "events": [_event_to_dict(event) for event in result.events],
        "scored_themes": [_theme_to_dict(theme) for theme in result.scored_themes],
        "etf_candidates": [_candidate_to_dict(candidate) for candidate in result.etf_candidates],
        "stock_candidates": [_candidate_to_dict(candidate) for candidate in result.stock_candidates],
    }


def _event_to_dict(event: TransmissionEvent) -> dict[str, Any]:
    return asdict(event)


def _theme_to_dict(theme: ScoredTheme) -> dict[str, Any]:
    return {
        "theme": theme.theme,
        "direction": theme.direction,
        "score": theme.score,
        "signal_strength": theme.signal_strength,
        "resonance_score": theme.resonance_score,
        "historical_edge_score": theme.historical_edge_score,
        "mapping_clarity_score": theme.mapping_clarity_score,
        "market_environment_score": theme.market_environment_score,
        "risk_discount": theme.risk_discount,
        "reasons": list(theme.reasons),
        "risks": list(theme.risks),
        "risk_details": list(theme.risk_details),
        "mapping": asdict(theme.mapping),
        "trigger_group": theme.group_signal.group,
        "trigger_assets": [move.asset.symbol for move in theme.group_signal.assets],
    }


def _candidate_to_dict(candidate: Candidate) -> dict[str, Any]:
    return asdict(candidate)


def _knowledge_dashboard_subset(
    knowledge: dict[str, Any],
    suggestions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    suggestions = suggestions if suggestions is not None else suggest_mapping_fixes(knowledge)
    return {
        "quality_counts": knowledge.get("quality_counts", {}),
        "source_summary": knowledge.get("source_summary", {}),
        "issues": knowledge.get("issues", [])[:50],
        "suggestions": suggestions.get("suggestions", [])[:50],
        "mapping": knowledge.get("mapping", ""),
        "verified_at": knowledge.get("verified_at", ""),
    }


def _snapshot_quality(snapshot: dict[str, Any]) -> dict[str, Any]:
    source_summary = snapshot.get("source_summary", {})
    quality_counts = dict(source_summary.get("quality_counts", {}))
    if not quality_counts:
        quality_counts = _count_data_statuses(snapshot)
    return {
        "quality_counts": quality_counts,
        "errors": list(source_summary.get("errors", [])),
        "source_summary": source_summary,
        "market_breadth_status": snapshot.get("market_breadth", {}).get("data_status", ""),
    }


def _snapshot_status(snapshot: dict[str, Any]) -> str:
    quality = _snapshot_quality(snapshot)
    counts = quality.get("quality_counts", {})
    has_bad_counts = any(status != "ok" and int(count or 0) > 0 for status, count in counts.items())
    has_errors = bool(quality.get("errors"))
    has_missing_breadth = quality.get("market_breadth_status") in {"missing", "partial", "stale", "divergent"}
    return "partial" if has_bad_counts or has_errors or has_missing_breadth else "ok"


def _count_data_statuses(snapshot: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for key in ("assets", "indices", "commodities", "quotes"):
        rows.extend(item for item in snapshot.get(key, []) if isinstance(item, dict))
    for payload in snapshot.get("themes", {}).values():
        if isinstance(payload, dict):
            rows.append(payload)
    for row in rows:
        status = str(row.get("data_status", "ok"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _knowledge_status(knowledge: dict[str, Any]) -> str:
    counts = knowledge.get("quality_counts", {})
    return "partial" if int(counts.get("high", 0) or 0) or int(counts.get("medium", 0) or 0) else "ok"


def _apply_step_status(summary: dict[str, Any], step: dict[str, Any]) -> None:
    if summary.get("status") == "error":
        return
    if step.get("status") == "partial":
        summary["status"] = "partial"


def _summary_for_dashboard(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_date": summary.get("run_date", ""),
        "generated_at": summary.get("generated_at", ""),
        "status": summary.get("status", ""),
        "warnings": summary.get("warnings", []),
        "steps": summary.get("steps", {}),
        "outputs": summary.get("outputs", {}),
        "errors": summary.get("errors", []),
    }


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def _collect_warnings(summary: dict[str, Any]) -> list[str]:
    warnings = list(summary.get("warnings", []))
    for name, step in summary.get("steps", {}).items():
        if not isinstance(step, dict):
            continue
        status = str(step.get("status", ""))
        if status == "partial":
            warnings.append(f"{name} completed with partial data")
        elif status == "skipped":
            warnings.append(f"{name} was skipped")
    warnings.extend(str(item) for item in summary.get("errors", []))
    return warnings


def _contract_issue_messages(issues: list[dict[str, str]]) -> list[str]:
    return [
        f"dashboard_data {issue.get('level', 'warning')}: {issue.get('field', '')} {issue.get('message', '')}".strip()
        for issue in issues
    ]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
