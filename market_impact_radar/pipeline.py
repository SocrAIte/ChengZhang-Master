from __future__ import annotations

from typing import Any

from .events import generate_events
from .io import load_external_snapshot, load_json, load_mappings
from .models import RadarResult
from .scanner import build_group_signals, identify_abnormal_moves
from .scoring import build_candidates, score_themes


def run_report_pipeline(
    external_path: str,
    mapping_path: str,
    context_path: str | None = None,
    historical_edges_path: str | None = None,
    scoring_rules_path: str | None = None,
) -> RadarResult:
    config = load_mappings(mapping_path)
    as_of, assets = load_external_snapshot(external_path, config)
    context: dict[str, Any] = load_json(context_path) if context_path else {}
    if historical_edges_path:
        generated_edges = load_json(historical_edges_path)
        edges = generated_edges.get("historical_edges", generated_edges)
        context.setdefault("historical_edges", {}).update(edges)
    if scoring_rules_path:
        context["scoring_rules"] = load_json(scoring_rules_path)
    context["external_data_quality"] = _summarize_external_data_quality(assets)
    abnormal_moves = identify_abnormal_moves(assets, config)
    group_signals = build_group_signals(abnormal_moves, config)
    scored_themes = score_themes(group_signals, config, context)
    etf_candidates, stock_candidates = build_candidates(scored_themes, rules=context.get("scoring_rules"))
    events = generate_events(scored_themes)
    return RadarResult(
        as_of=as_of,
        external_assets=assets,
        abnormal_moves=abnormal_moves,
        group_signals=group_signals,
        scored_themes=scored_themes,
        etf_candidates=etf_candidates,
        stock_candidates=stock_candidates,
        events=events,
        context=context,
    )


def _summarize_external_data_quality(assets: tuple) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    sources = set()
    fetched_times = []
    issues = []
    for asset in assets:
        status = getattr(asset, "data_status", "ok") or "ok"
        statuses[status] = statuses.get(status, 0) + 1
        if getattr(asset, "source", ""):
            sources.add(asset.source)
        if getattr(asset, "fetched_at", ""):
            fetched_times.append(asset.fetched_at)
        if status != "ok" or getattr(asset, "quality_warnings", ()):
            issues.append(
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "status": status,
                    "warnings": list(asset.quality_warnings),
                    "source": asset.source,
                    "fetched_at": asset.fetched_at,
                }
            )
    return {
        "statuses": statuses,
        "sources": sorted(sources),
        "fetched_at_min": min(fetched_times) if fetched_times else "",
        "fetched_at_max": max(fetched_times) if fetched_times else "",
        "issues": issues,
        "ok": all(status == "ok" for status in statuses),
    }
