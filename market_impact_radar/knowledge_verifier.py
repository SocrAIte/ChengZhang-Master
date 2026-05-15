from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .knowledge_crawler import (
    A_SHARE_FIELDS,
    A_SHARE_FS,
    ETF_FS,
    fetch_eastmoney_clist,
    fetch_official_a_share_stocks,
    fetch_taiwan_symbols,
    fetch_us_symbols,
    set_proxy,
)


def verify_knowledge_graph(
    mapping_path: str | Path,
    generated_dir: str | Path = "data/generated",
    refresh_apis: bool = False,
    timeout: int = 20,
    proxy: str | None = None,
    proxy_mode: str = "foreign",
) -> dict[str, Any]:
    mapping = _load_json(mapping_path)
    universes, source_summary = load_verification_universes(
        generated_dir=generated_dir,
        refresh_apis=refresh_apis,
        timeout=timeout,
        proxy=proxy,
        proxy_mode=proxy_mode,
    )
    report = verify_mapping(mapping, universes)
    report["mapping"] = str(mapping_path)
    report["verified_at"] = _now_iso()
    report["source_summary"] = source_summary
    return report


def load_verification_universes(
    generated_dir: str | Path,
    refresh_apis: bool = False,
    timeout: int = 20,
    proxy: str | None = None,
    proxy_mode: str = "foreign",
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    generated = Path(generated_dir)
    errors: list[str] = []
    set_proxy(proxy, proxy_mode)
    universes = {
        "us_symbols": _cached_rows(generated / "us_symbols.json"),
        "taiwan_symbols": _cached_rows(generated / "taiwan_symbols.json"),
        "a_share_stocks": _cached_rows(generated / "a_share_stocks.json"),
        "official_a_share_stocks": _cached_rows(generated / "official_a_share_stocks.json"),
        "eastmoney_board_members": _cached_rows(generated / "eastmoney_board_members.json"),
        "china_etfs": _cached_rows(generated / "china_etfs.json"),
    }
    if refresh_apis:
        _replace_if_available(universes, "us_symbols", errors, lambda: fetch_us_symbols(timeout))
        _replace_if_available(universes, "taiwan_symbols", errors, lambda: fetch_taiwan_symbols(timeout))
        _replace_if_available(universes, "official_a_share_stocks", errors, lambda: fetch_official_a_share_stocks(timeout))
        _replace_if_available(universes, "a_share_stocks", errors, lambda: fetch_eastmoney_clist(A_SHARE_FS, A_SHARE_FIELDS, timeout))
        _replace_if_available(universes, "china_etfs", errors, lambda: fetch_eastmoney_clist(ETF_FS, A_SHARE_FIELDS, timeout))

    counts = {name: len(rows) for name, rows in universes.items()}
    return universes, {
        "mode": "api+cache" if refresh_apis else "cache",
        "generated_dir": str(generated),
        "counts": counts,
        "errors": errors,
    }


def verify_mapping(mapping: dict[str, Any], universes: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    indexes = _build_indexes(universes)
    issues: list[dict[str, Any]] = []
    external_results = _verify_external_assets(mapping, indexes, issues)
    theme_results = _verify_theme_mappings(mapping, indexes, issues)
    _verify_theme_references(mapping, issues)
    return {
        "quality_counts": _quality_counts(issues),
        "issues": issues,
        "external_assets": external_results,
        "theme_mappings": theme_results,
    }


def _verify_external_assets(
    mapping: dict[str, Any],
    indexes: dict[str, set[str]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results = []
    for asset in mapping.get("external_assets", []):
        symbol = str(asset.get("symbol", "")).upper()
        market = str(asset.get("market", "")).upper()
        asset_type = str(asset.get("asset_type", "equity"))
        status = "unchecked"
        verified_by = ""
        if market == "US" and asset_type in {"equity", "etf"}:
            status = "ok" if symbol in indexes["us_symbols"] else "missing"
            verified_by = "nasdaq"
        elif market == "TW" and asset_type in {"equity", "etf"}:
            status = "ok" if symbol in indexes["taiwan_symbols"] else "missing"
            verified_by = "twse/tpex"
        elif asset_type in {"commodity", "crypto", "index"}:
            status = "unchecked"
            verified_by = "not-covered-by-symbol-api"
        else:
            verified_by = "no-api"

        if status == "missing":
            issues.append(_issue("medium", "external_asset_missing", symbol, f"{symbol} not found in {verified_by} universe"))
        results.append({"symbol": symbol, "market": market, "status": status, "verified_by": verified_by})
    return results


def _verify_theme_mappings(
    mapping: dict[str, Any],
    indexes: dict[str, set[str]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results = []
    for theme, config in mapping.get("theme_mappings", {}).items():
        stocks = config.get("stocks", [])
        etfs = config.get("etfs", [])
        stock_checks = [_verify_a_share_stock(item, indexes) for item in stocks]
        etf_checks = [_verify_china_etf(item, indexes) for item in etfs]
        missing_stocks = [item for item in stock_checks if item["status"] == "missing"]
        coded_stocks = [item for item in stock_checks if item["status"] == "coded"]
        missing_etfs = [item for item in etf_checks if item["status"] == "missing"]
        if not stocks and not etfs:
            issues.append(_issue("high", "empty_theme_mapping", theme, "theme has no ETF or stock mappings"))
        for item in missing_stocks[:8]:
            issues.append(_issue("medium", "theme_stock_unverified", theme, f"{item['name']} not found in A-share universe"))
        for item in missing_etfs[:8]:
            issues.append(_issue("low", "theme_etf_unverified", theme, f"{item['name']} not found in China ETF universe"))
        status = "ok" if not missing_stocks and not missing_etfs and (stocks or etfs) else "warning"
        results.append(
            {
                "theme": theme,
                "status": status,
                "stocks_checked": len(stock_checks),
                "stocks_missing": len(missing_stocks),
                "stocks_coded_unverified": len(coded_stocks),
                "etfs_checked": len(etf_checks),
                "etfs_missing": len(missing_etfs),
            }
        )
    return results


def _verify_theme_references(mapping: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    known_themes = set(mapping.get("theme_mappings", {}))
    for asset in mapping.get("external_assets", []):
        for theme in asset.get("themes", []):
            if theme not in known_themes:
                issues.append(_issue("high", "external_theme_missing", str(asset.get("symbol", "")), f"theme {theme} is not in theme_mappings"))
    for group, config in mapping.get("market_groups", {}).items():
        for theme in config.get("themes", []):
            if theme not in known_themes:
                issues.append(_issue("high", "market_group_theme_missing", group, f"theme {theme} is not in theme_mappings"))


def _verify_a_share_stock(item: Any, indexes: dict[str, set[str]]) -> dict[str, str]:
    name, code = _mapping_name_code(item)
    keys = {code, _norm(name)}
    if any(key and key in indexes["a_share_stocks"] for key in keys):
        status = "ok"
    elif _looks_like_a_share_code(code):
        status = "coded"
    else:
        status = "missing"
    return {"name": name, "code": code, "status": status}


def _verify_china_etf(item: Any, indexes: dict[str, set[str]]) -> dict[str, str]:
    name, code = _mapping_name_code(item)
    normalized_name = _norm(name)
    status = "missing"
    if code and code in indexes["china_etfs"]:
        status = "ok"
    elif normalized_name and any(normalized_name in etf or etf in normalized_name for etf in indexes["china_etfs"]):
        status = "ok"
    return {"name": name, "code": code, "status": status}


def _build_indexes(universes: dict[str, list[dict[str, Any]]]) -> dict[str, set[str]]:
    a_share_rows = (
        universes.get("a_share_stocks", [])
        + universes.get("official_a_share_stocks", [])
        + universes.get("eastmoney_board_members", [])
    )
    return {
        "us_symbols": {_norm_symbol(row.get("symbol")) for row in universes.get("us_symbols", [])},
        "taiwan_symbols": {_norm_symbol(row.get("symbol")) for row in universes.get("taiwan_symbols", [])},
        "a_share_stocks": _name_code_index(a_share_rows),
        "china_etfs": _name_code_index(universes.get("china_etfs", [])),
    }


def _name_code_index(rows: list[dict[str, Any]]) -> set[str]:
    values = set()
    for row in rows:
        for key in ("code", "symbol"):
            value = str(row.get(key, "")).strip()
            if value:
                values.add(value.upper())
        name = _norm(row.get("name"))
        if name:
            values.add(name)
    return values


def _mapping_name_code(item: Any) -> tuple[str, str]:
    if isinstance(item, dict):
        return str(item.get("name", "")).strip(), str(item.get("code", "")).strip().upper()
    return str(item).strip(), ""


def _quality_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0}
    for issue in issues:
        severity = str(issue.get("severity", "low"))
        counts[severity] = counts.get(severity, 0) + 1
    counts["total"] = len(issues)
    return counts


def _replace_if_available(
    universes: dict[str, list[dict[str, Any]]],
    key: str,
    errors: list[str],
    fetcher: Any,
) -> None:
    try:
        rows = fetcher()
    except Exception as exc:  # pragma: no cover - depends on network stability.
        errors.append(f"{key}: {exc}")
        return
    if rows:
        universes[key] = rows


def _cached_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def _issue(severity: str, kind: str, target: str, message: str) -> dict[str, str]:
    return {"severity": severity, "kind": kind, "target": target, "message": message}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _norm_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm(value: Any) -> str:
    return "".join(ch for ch in str(value or "").upper() if ch.isalnum())


def _looks_like_a_share_code(value: str) -> bool:
    return len(value) == 6 and value.isdigit()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
