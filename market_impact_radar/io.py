from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import ExternalAsset, ThemeMapping


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def load_mappings(path: str | Path) -> dict[str, Any]:
    config = load_json(path)
    config.setdefault("external_assets", [])
    config.setdefault("theme_mappings", {})
    config.setdefault("market_groups", {})
    config.setdefault("reason_weights", {})
    config.setdefault("scanner_settings", {})
    return config


def load_theme_mappings(config: dict[str, Any]) -> dict[str, ThemeMapping]:
    theme_mappings: dict[str, ThemeMapping] = {}
    for theme, raw in config.get("theme_mappings", {}).items():
        theme_mappings[theme] = ThemeMapping(
            theme=theme,
            industries=tuple(raw.get("industries", [])),
            etfs=tuple(raw.get("etfs", [])),
            stocks=tuple(raw.get("stocks", [])),
            clarity=float(raw.get("clarity", 0.7)),
        )
    return theme_mappings


def load_external_snapshot(
    path: str | Path,
    config: dict[str, Any],
) -> tuple[str, tuple[ExternalAsset, ...]]:
    snapshot = load_json(path)
    catalog = {
        item["symbol"].upper(): item for item in config.get("external_assets", [])
    }

    raw_assets = []
    for key in ("assets", "indices", "commodities"):
        raw_assets.extend(snapshot.get(key, []))

    assets = []
    for raw in raw_assets:
        symbol = str(raw["symbol"]).upper()
        base = catalog.get(symbol, {})
        merged = {**base, **raw}
        fetched_at = str(merged.get("fetched_at", snapshot.get("as_of", "")))
        quality_warnings = [str(item) for item in merged.get("quality_warnings", [])]
        data_status = str(merged.get("data_status", "ok"))
        max_age_minutes = snapshot.get("source_summary", {}).get("max_age_minutes")
        if max_age_minutes and data_status == "ok" and _is_stale(fetched_at, int(max_age_minutes)):
            data_status = "stale"
            quality_warnings.append(f"fetched_at older than {int(max_age_minutes)} minutes")
        assets.append(
            ExternalAsset(
                symbol=symbol,
                name=str(merged.get("name", symbol)),
                market=str(merged.get("market", "")),
                change_pct=float(merged.get("change_pct", 0.0)),
                volume_ratio=float(merged.get("volume_ratio", 1.0)),
                price=_optional_float(merged.get("price")),
                prev_close=_optional_float(merged.get("prev_close")),
                source=str(merged.get("source", "manual")),
                fetched_at=fetched_at,
                data_status=data_status,
                quality_warnings=tuple(quality_warnings),
                source_details=tuple(merged.get("source_details", [])),
                asset_type=str(merged.get("asset_type", "equity")),
                group=merged.get("group"),
                themes=tuple(merged.get("themes", [])),
                reason_tags=tuple(merged.get("reason_tags", [])),
                reason_summary=str(merged.get("reason_summary", "")),
            )
        )
    return str(snapshot.get("as_of", "")), tuple(assets)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _is_stale(fetched_at: str, max_age_minutes: int) -> bool:
    if max_age_minutes <= 0:
        return False
    try:
        parsed = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)
    return age.total_seconds() > max_age_minutes * 60
