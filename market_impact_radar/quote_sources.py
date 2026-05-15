from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


YAHOO_SYMBOL_ALIASES = {
    "SOX": "^SOX",
    "BTC": "BTC-USD",
}


@dataclass(frozen=True)
class QuoteRecord:
    symbol: str
    source: str
    fetched_at: str
    price: float | None = None
    prev_close: float | None = None
    change_pct: float | None = None
    volume_ratio: float | None = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and self.price is not None and self.prev_close not in (None, 0)


def fetch_external_snapshot(
    symbols: Iterable[str],
    config: dict[str, Any],
    sources: Iterable[str] = ("yahoo",),
    max_source_diff_pct: float = 0.5,
    max_age_minutes: int = 180,
    alpha_vantage_key: str | None = None,
    polygon_key: str | None = None,
    proxy: str | None = None,
) -> dict[str, Any]:
    requested_sources = tuple(source.strip().lower() for source in sources if source.strip())
    if not requested_sources:
        raise ValueError("At least one quote source is required")

    now = _now_iso()
    source_clients = _build_sources(
        requested_sources,
        alpha_vantage_key=alpha_vantage_key,
        polygon_key=polygon_key,
        proxy=proxy,
    )
    records: list[QuoteRecord] = []
    for symbol in symbols:
        normalized = symbol.strip().upper()
        if not normalized:
            continue
        for client in source_clients:
            records.append(client.fetch(normalized, now))

    return consolidate_quote_records(
        records=records,
        config=config,
        requested_sources=requested_sources,
        fetched_at=now,
        max_source_diff_pct=max_source_diff_pct,
        max_age_minutes=max_age_minutes,
    )


def consolidate_quote_records(
    records: Iterable[QuoteRecord],
    config: dict[str, Any],
    requested_sources: Iterable[str],
    fetched_at: str,
    max_source_diff_pct: float = 0.5,
    max_age_minutes: int = 180,
) -> dict[str, Any]:
    catalog = {item["symbol"].upper(): item for item in config.get("external_assets", [])}
    by_symbol: dict[str, list[QuoteRecord]] = {}
    for record in records:
        by_symbol.setdefault(record.symbol.upper(), []).append(record)

    assets: list[dict[str, Any]] = []
    indices: list[dict[str, Any]] = []
    commodities: list[dict[str, Any]] = []
    quality_counts: dict[str, int] = {}

    for symbol, symbol_records in by_symbol.items():
        base = catalog.get(symbol, {"symbol": symbol})
        item = _consolidate_symbol(
            symbol=symbol,
            base=base,
            records=symbol_records,
            requested_sources=tuple(requested_sources),
            fetched_at=fetched_at,
            max_source_diff_pct=max_source_diff_pct,
            max_age_minutes=max_age_minutes,
        )
        quality_counts[item["data_status"]] = quality_counts.get(item["data_status"], 0) + 1
        asset_type = str(base.get("asset_type", "equity")).lower()
        if asset_type == "index":
            indices.append(item)
        elif asset_type in {"commodity", "crypto"}:
            commodities.append(item)
        else:
            assets.append(item)

    return {
        "as_of": fetched_at,
        "source_summary": {
            "sources": list(requested_sources),
            "fetched_at": fetched_at,
            "max_source_diff_pct": max_source_diff_pct,
            "max_age_minutes": max_age_minutes,
            "quality_counts": quality_counts,
        },
        "assets": assets,
        "indices": indices,
        "commodities": commodities,
    }


class YahooChartSource:
    name = "yahoo"

    def __init__(self, opener: urllib.request.OpenerDirector | None = None) -> None:
        self._opener = opener or urllib.request.build_opener()

    def fetch(self, symbol: str, fetched_at: str) -> QuoteRecord:
        provider_symbol = YAHOO_SYMBOL_ALIASES.get(symbol, symbol)
        encoded = urllib.parse.quote(provider_symbol, safe="")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=5d&interval=1d"
        try:
            payload = _read_json(url, self._opener)
            result = payload["chart"]["result"][0]
            meta = result.get("meta", {})
            price = _first_float(meta, "regularMarketPrice", "postMarketPrice", "preMarketPrice")
            prev_close = _first_float(meta, "previousClose", "chartPreviousClose")
            if prev_close in (None, 0):
                prev_close = _previous_close_from_quote(result, price)
            volume_ratio = _yahoo_volume_ratio(result)
            change_pct = _change_pct(price, prev_close)
            return QuoteRecord(
                symbol=symbol,
                source=self.name,
                fetched_at=fetched_at,
                price=price,
                prev_close=prev_close,
                change_pct=change_pct,
                volume_ratio=volume_ratio,
            )
        except Exception as exc:  # pragma: no cover - network failures are environment dependent.
            return QuoteRecord(symbol=symbol, source=self.name, fetched_at=fetched_at, error=str(exc))


class AlphaVantageSource:
    name = "alphavantage"

    def __init__(self, api_key: str, opener: urllib.request.OpenerDirector | None = None) -> None:
        self._api_key = api_key
        self._opener = opener or urllib.request.build_opener()

    def fetch(self, symbol: str, fetched_at: str) -> QuoteRecord:
        query = urllib.parse.urlencode(
            {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self._api_key,
            }
        )
        url = f"https://www.alphavantage.co/query?{query}"
        try:
            payload = _read_json(url, self._opener)
            quote = payload.get("Global Quote", {})
            if not quote:
                raise ValueError(payload.get("Note") or payload.get("Information") or "empty Global Quote")
            price = _safe_float(quote.get("05. price"))
            prev_close = _safe_float(quote.get("08. previous close"))
            change_pct = _percent_string_to_float(quote.get("10. change percent"))
            if change_pct is None:
                change_pct = _change_pct(price, prev_close)
            return QuoteRecord(
                symbol=symbol,
                source=self.name,
                fetched_at=fetched_at,
                price=price,
                prev_close=prev_close,
                change_pct=change_pct,
            )
        except Exception as exc:  # pragma: no cover - network failures are environment dependent.
            return QuoteRecord(symbol=symbol, source=self.name, fetched_at=fetched_at, error=str(exc))


class PolygonSource:
    name = "polygon"

    def __init__(self, api_key: str, opener: urllib.request.OpenerDirector | None = None) -> None:
        self._api_key = api_key
        self._opener = opener or urllib.request.build_opener()

    def fetch(self, symbol: str, fetched_at: str) -> QuoteRecord:
        try:
            encoded = urllib.parse.quote(symbol, safe="")
            prev_url = f"https://api.polygon.io/v2/aggs/ticker/{encoded}/prev?adjusted=true&apiKey={self._api_key}"
            trade_url = f"https://api.polygon.io/v2/last/trade/{encoded}?apiKey={self._api_key}"
            prev_payload = _read_json(prev_url, self._opener)
            trade_payload = _read_json(trade_url, self._opener)
            prev_results = prev_payload.get("results") or []
            if not prev_results:
                raise ValueError("empty previous close")
            prev_close = _safe_float(prev_results[0].get("c"))
            price = _safe_float((trade_payload.get("results") or {}).get("p"))
            return QuoteRecord(
                symbol=symbol,
                source=self.name,
                fetched_at=fetched_at,
                price=price,
                prev_close=prev_close,
                change_pct=_change_pct(price, prev_close),
            )
        except Exception as exc:  # pragma: no cover - network failures are environment dependent.
            return QuoteRecord(symbol=symbol, source=self.name, fetched_at=fetched_at, error=str(exc))


def _build_sources(
    names: tuple[str, ...],
    alpha_vantage_key: str | None,
    polygon_key: str | None,
    proxy: str | None,
) -> list[Any]:
    opener = _opener(proxy)
    clients = []
    for name in names:
        if name == "yahoo":
            clients.append(YahooChartSource(opener))
        elif name == "alphavantage":
            key = alpha_vantage_key or os.environ.get("ALPHAVANTAGE_API_KEY")
            if not key:
                raise ValueError("Alpha Vantage requires --alpha-vantage-key or ALPHAVANTAGE_API_KEY")
            clients.append(AlphaVantageSource(key, opener))
        elif name == "polygon":
            key = polygon_key or os.environ.get("POLYGON_API_KEY")
            if not key:
                raise ValueError("Polygon requires --polygon-key or POLYGON_API_KEY")
            clients.append(PolygonSource(key, opener))
        else:
            raise ValueError(f"Unsupported quote source: {name}")
    return clients


def _consolidate_symbol(
    symbol: str,
    base: dict[str, Any],
    records: list[QuoteRecord],
    requested_sources: tuple[str, ...],
    fetched_at: str,
    max_source_diff_pct: float,
    max_age_minutes: int,
) -> dict[str, Any]:
    ok_records = [record for record in records if record.ok]
    warnings = [f"{record.source}: {record.error}" for record in records if record.error]
    status = "ok"

    if not ok_records:
        status = "missing"
    elif len(ok_records) < len(requested_sources):
        status = "missing"
    elif _is_stale(fetched_at, max_age_minutes):
        status = "stale"
    elif _has_source_divergence(ok_records, max_source_diff_pct):
        status = "divergent"

    if status == "missing" and not warnings:
        warnings.append("missing quote source")
    if status == "stale":
        warnings.append(f"fetched_at older than {max_age_minutes} minutes")
    if status == "divergent":
        warnings.append(f"multi-source change_pct divergence exceeds {max_source_diff_pct:.2f} pct")

    primary = _primary_record(ok_records, requested_sources)
    source_details = [
        {
            "source": record.source,
            "fetched_at": record.fetched_at,
            "price": record.price,
            "prev_close": record.prev_close,
            "change_pct": record.change_pct,
            "volume_ratio": record.volume_ratio,
            "error": record.error,
        }
        for record in records
    ]
    item = {
        "symbol": symbol,
        "name": base.get("name", symbol),
        "market": base.get("market", ""),
        "asset_type": base.get("asset_type", "equity"),
        "source": ",".join(record.source for record in ok_records) if ok_records else ",".join(requested_sources),
        "fetched_at": fetched_at,
        "change_pct": round(float(primary.change_pct), 4) if primary and primary.change_pct is not None else 0.0,
        "volume_ratio": round(float(primary.volume_ratio), 4) if primary and primary.volume_ratio is not None else 1.0,
        "data_status": status,
        "quality_warnings": warnings,
        "source_details": source_details,
    }
    if primary and primary.price is not None:
        item["price"] = primary.price
    if primary and primary.prev_close is not None:
        item["prev_close"] = primary.prev_close
    return item


def _primary_record(records: list[QuoteRecord], requested_sources: tuple[str, ...]) -> QuoteRecord | None:
    if not records:
        return None
    priority = {source: index for index, source in enumerate(requested_sources)}
    return sorted(records, key=lambda record: priority.get(record.source, 999))[0]


def _has_source_divergence(records: list[QuoteRecord], max_source_diff_pct: float) -> bool:
    changes = [float(record.change_pct) for record in records if record.change_pct is not None]
    return bool(changes) and (max(changes) - min(changes) > max_source_diff_pct)


def _is_stale(fetched_at: str, max_age_minutes: int) -> bool:
    if max_age_minutes <= 0:
        return False
    try:
        fetched = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - fetched.astimezone(timezone.utc)
    return age.total_seconds() > max_age_minutes * 60


def _read_json(url: str, opener: urllib.request.OpenerDirector) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "market-impact-radar/0.1"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with opener.open(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network failures are environment dependent.
            last_error = exc
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))
    raise last_error or RuntimeError("unknown quote source error")


def _opener(proxy: str | None) -> urllib.request.OpenerDirector:
    if not proxy:
        return urllib.request.build_opener()
    return urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {
                "http": proxy,
                "https": proxy,
            }
        )
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _first_float(payload: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _safe_float(payload.get(key))
        if value is not None:
            return value
    return None


def _previous_close_from_quote(result: dict[str, Any], price: float | None) -> float | None:
    closes = ((result.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    clean_closes = [_safe_float(value) for value in closes]
    clean_closes = [value for value in clean_closes if value is not None]
    if not clean_closes:
        return None
    if price is not None and len(clean_closes) >= 2 and abs(clean_closes[-1] - price) < 1e-9:
        return clean_closes[-2]
    return clean_closes[-1]


def _yahoo_volume_ratio(result: dict[str, Any]) -> float | None:
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    volumes = [_safe_float(value) for value in quote.get("volume", [])]
    volumes = [value for value in volumes if value is not None and value > 0]
    if len(volumes) < 2:
        return None
    recent = volumes[-1]
    baseline = sum(volumes[:-1]) / len(volumes[:-1])
    if baseline <= 0:
        return None
    return min(10.0, recent / baseline)


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _percent_string_to_float(value: Any) -> float | None:
    if value is None:
        return None
    return _safe_float(str(value).strip().rstrip("%"))


def _change_pct(price: float | None, prev_close: float | None) -> float | None:
    if price is None or prev_close in (None, 0):
        return None
    return (price - prev_close) / prev_close * 100.0
