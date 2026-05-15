from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from .trading_calendar import TradingCalendars


EASTMONEY_QUOTE_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
EASTMONEY_CLIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
EASTMONEY_CLIST_URLS = (
    "https://push2.eastmoney.com/api/qt/clist/get",
    "https://82.push2.eastmoney.com/api/qt/clist/get",
    "http://82.push2.eastmoney.com/api/qt/clist/get",
    "http://58.push2.eastmoney.com/api/qt/clist/get",
    "http://57.push2.eastmoney.com/api/qt/clist/get",
    "http://77.push2.eastmoney.com/api/qt/clist/get",
    "http://16.push2.eastmoney.com/api/qt/clist/get",
    "https://48.push2.eastmoney.com/api/qt/clist/get",
    "https://33.push2.eastmoney.com/api/qt/clist/get",
    "http://push2.eastmoney.com/api/qt/clist/get",
)
SINA_MARKET_CENTER_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"


@dataclass(frozen=True)
class AShareQuote:
    symbol: str
    name: str
    source: str
    fetched_at: str
    price: float | None = None
    prev_close: float | None = None
    open_price: float | None = None
    change_pct: float | None = None
    open_gap_pct: float | None = None
    amount: float | None = None
    volume: float | None = None
    data_status: str = "ok"
    quality_warnings: tuple[str, ...] = ()


def fetch_a_share_snapshot(
    watchlist: dict[str, Any],
    source: str = "eastmoney",
    calendars: TradingCalendars | None = None,
    proxy: str | None = None,
) -> dict[str, Any]:
    if source != "eastmoney":
        raise ValueError(f"Unsupported A-share source: {source}")

    fetched_at = _now_iso()
    symbols = sorted(_symbols_from_watchlist(watchlist))
    source_errors = []
    try:
        quotes = fetch_eastmoney_quotes(symbols, fetched_at=fetched_at, proxy=proxy)
    except Exception as exc:  # pragma: no cover - depends on network stability.
        source_errors.append(f"quotes: {exc}")
        quotes = tuple(_missing_quote(symbol, fetched_at, f"quotes: {exc}") for symbol in symbols)
    quote_map = {quote.symbol: quote for quote in quotes}
    try:
        breadth_quotes = fetch_eastmoney_market_quotes(fetched_at=fetched_at, proxy=proxy)
    except Exception as exc:  # pragma: no cover - depends on network stability.
        source_errors.append(f"market_breadth/eastmoney: {exc}")
        try:
            breadth_quotes = fetch_sina_market_quotes(fetched_at=fetched_at, proxy=proxy)
        except Exception as fallback_exc:  # pragma: no cover - depends on network stability.
            source_errors.append(f"market_breadth/sina: {fallback_exc}")
            breadth_quotes = ()
    snapshot = build_a_share_snapshot(
        watchlist=watchlist,
        quote_map=quote_map,
        market_quotes=breadth_quotes,
        fetched_at=fetched_at,
        calendars=calendars or TradingCalendars(),
        source=source,
    )
    if source_errors:
        snapshot["source_summary"]["errors"] = source_errors
    return snapshot


def build_a_share_snapshot(
    watchlist: dict[str, Any],
    quote_map: dict[str, AShareQuote],
    market_quotes: Iterable[AShareQuote],
    fetched_at: str,
    calendars: TradingCalendars | None = None,
    source: str = "eastmoney",
) -> dict[str, Any]:
    calendar = calendars or TradingCalendars()
    as_of = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    context = calendar.build_context(as_of)
    market_quotes_tuple = tuple(market_quotes)
    market_breadth = summarize_market_breadth(market_quotes_tuple)
    themes = {}
    for theme, payload in watchlist.get("themes", {}).items():
        themes[theme] = _build_theme_snapshot(theme, payload, quote_map)

    quality_counts: dict[str, int] = {}
    for quote in tuple(quote_map.values()) + market_quotes_tuple:
        quality_counts[quote.data_status] = quality_counts.get(quote.data_status, 0) + 1

    return {
        "as_of": fetched_at,
        "source_summary": {
            "source": source,
            "fetched_at": fetched_at,
            "quality_counts": quality_counts,
        },
        "trading_day_context": context,
        "market_breadth": market_breadth,
        "themes": themes,
        "quotes": [_quote_to_dict(quote) for quote in sorted(quote_map.values(), key=lambda item: item.symbol)],
    }


def summarize_market_breadth(quotes: Iterable[AShareQuote]) -> dict[str, Any]:
    rows = [quote for quote in quotes if quote.data_status == "ok" and quote.change_pct is not None]
    amount = sum(float(quote.amount or 0.0) for quote in rows)
    source = rows[0].source if rows else ""
    return {
        "source": source,
        "data_status": "ok" if rows else "missing",
        "turnover_billion": round(amount / 100_000_000, 2),
        "up_count": sum(1 for quote in rows if float(quote.change_pct or 0.0) > 0),
        "down_count": sum(1 for quote in rows if float(quote.change_pct or 0.0) < 0),
        "unchanged_count": sum(1 for quote in rows if float(quote.change_pct or 0.0) == 0),
        "stocks_over_5pct_count": sum(1 for quote in rows if float(quote.change_pct or 0.0) >= 5.0),
        "sample_size": len(rows),
    }


def fetch_eastmoney_quotes(
    symbols: Iterable[str],
    fetched_at: str,
    proxy: str | None = None,
) -> tuple[AShareQuote, ...]:
    secids = ",".join(_eastmoney_secid(symbol) for symbol in symbols)
    if not secids:
        return ()
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f12,f14,f2,f3,f5,f6,f17,f18",
        "secids": secids,
    }
    payload = _read_json(EASTMONEY_QUOTE_URL, params, proxy)
    rows = payload.get("data", {}).get("diff") or []
    return tuple(_quote_from_eastmoney_row(row, fetched_at) for row in rows)


def fetch_eastmoney_market_quotes(
    fetched_at: str,
    proxy: str | None = None,
    page_size: int = 100,
    max_pages: int = 70,
) -> tuple[AShareQuote, ...]:
    quotes: list[AShareQuote] = []
    for page in range(1, max_pages + 1):
        params = {
            "pn": str(page),
            "pz": str(page_size),
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f12,f14,f2,f3,f5,f6,f17,f18",
        }
        payload = _read_json_from_urls(EASTMONEY_CLIST_URLS, params, proxy)
        rows = payload.get("data", {}).get("diff") or []
        if not rows:
            break
        quotes.extend(_quote_from_eastmoney_row(row, fetched_at) for row in rows)
        if len(rows) < page_size:
            break
    return tuple(quotes)


def fetch_sina_market_quotes(
    fetched_at: str,
    proxy: str | None = None,
    page_size: int = 80,
    max_pages: int = 80,
) -> tuple[AShareQuote, ...]:
    quotes: list[AShareQuote] = []
    for page in range(1, max_pages + 1):
        params = {
            "page": str(page),
            "num": str(page_size),
            "sort": "changepercent",
            "asc": "0",
            "node": "hs_a",
            "symbol": "",
            "_s_r_a": "page",
        }
        payload = _read_text(SINA_MARKET_CENTER_URL, params, proxy)
        rows = _parse_sina_market_rows(payload)
        if not rows:
            break
        quotes.extend(_quote_from_sina_row(row, fetched_at) for row in rows)
        if len(rows) < page_size:
            break
    return tuple(quotes)


def _build_theme_snapshot(theme: str, payload: dict[str, Any], quote_map: dict[str, AShareQuote]) -> dict[str, Any]:
    etf_quote = _quote_for_payload(payload.get("etf", {}), quote_map)
    leader_quote = _quote_for_payload(payload.get("leader", {}), quote_map)
    member_quotes = [_quote_for_payload(item, quote_map) for item in payload.get("members", [])]
    member_quotes = [quote for quote in member_quotes if quote is not None]

    etf_open_gap = _value(etf_quote.open_gap_pct if etf_quote else None)
    etf_current = _value(etf_quote.change_pct if etf_quote else None)
    leader_current = _value(leader_quote.change_pct if leader_quote else None)
    leader_gap = _value(leader_quote.open_gap_pct if leader_quote else None)
    return {
        "etf_symbol": payload.get("etf", {}).get("symbol", ""),
        "leader_symbol": payload.get("leader", {}).get("symbol", ""),
        "etf_open_gap_pct": etf_open_gap,
        "etf_current_pct": etf_current,
        "etf_above_vwap": etf_current >= 0,
        "leader_current_pct": leader_current,
        "leader_open_gap_pct": leader_gap,
        "leader_fade": leader_gap >= 2.0 and leader_current < leader_gap - 2.0,
        "stocks_over_5pct_count": sum(1 for quote in member_quotes if _value(quote.change_pct) >= 5.0),
        "volume_ratio": 1.0,
        "data_status": _theme_status((etf_quote, leader_quote), member_quotes),
    }


def _theme_status(required_quotes: tuple[AShareQuote | None, ...], member_quotes: list[AShareQuote]) -> str:
    quotes = [quote for quote in required_quotes if quote is not None] + member_quotes
    if not quotes or any(quote is None for quote in required_quotes):
        return "missing"
    if any(quote.data_status != "ok" for quote in quotes):
        return "partial"
    return "ok"


def _quote_for_payload(payload: dict[str, Any], quote_map: dict[str, AShareQuote]) -> AShareQuote | None:
    symbol = str(payload.get("symbol", "")).strip()
    return quote_map.get(symbol)


def _quote_from_eastmoney_row(row: dict[str, Any], fetched_at: str) -> AShareQuote:
    symbol = str(row.get("f12", "")).strip()
    price = _safe_float(row.get("f2"))
    prev_close = _safe_float(row.get("f18"))
    open_price = _safe_float(row.get("f17"))
    warnings = []
    status = "ok"
    if price is None or prev_close in (None, 0):
        status = "missing"
        warnings.append("missing price or prev_close")
    return AShareQuote(
        symbol=symbol,
        name=str(row.get("f14", symbol)),
        source="eastmoney",
        fetched_at=fetched_at,
        price=price,
        prev_close=prev_close,
        open_price=open_price,
        change_pct=_safe_float(row.get("f3")),
        open_gap_pct=_change_pct(open_price, prev_close),
        volume=_safe_float(row.get("f5")),
        amount=_safe_float(row.get("f6")),
        data_status=status,
        quality_warnings=tuple(warnings),
    )


def _quote_from_sina_row(row: dict[str, Any], fetched_at: str) -> AShareQuote:
    raw_symbol = str(row.get("code") or row.get("symbol") or "").strip()
    symbol = raw_symbol[-6:] if len(raw_symbol) >= 6 else raw_symbol
    price = _safe_float(row.get("trade"))
    prev_close = _safe_float(row.get("settlement"))
    open_price = _safe_float(row.get("open"))
    warnings = []
    status = "ok"
    if price is None or prev_close in (None, 0):
        status = "missing"
        warnings.append("missing price or prev_close")
    return AShareQuote(
        symbol=symbol,
        name=str(row.get("name", symbol)),
        source="sina",
        fetched_at=fetched_at,
        price=price,
        prev_close=prev_close,
        open_price=open_price,
        change_pct=_safe_float(row.get("changepercent")),
        open_gap_pct=_change_pct(open_price, prev_close),
        volume=_safe_float(row.get("volume")),
        amount=_safe_float(row.get("amount")),
        data_status=status,
        quality_warnings=tuple(warnings),
    )


def _quote_to_dict(quote: AShareQuote) -> dict[str, Any]:
    return {
        "symbol": quote.symbol,
        "name": quote.name,
        "source": quote.source,
        "fetched_at": quote.fetched_at,
        "price": quote.price,
        "prev_close": quote.prev_close,
        "open_price": quote.open_price,
        "change_pct": quote.change_pct,
        "open_gap_pct": quote.open_gap_pct,
        "amount": quote.amount,
        "volume": quote.volume,
        "data_status": quote.data_status,
        "quality_warnings": list(quote.quality_warnings),
    }


def _symbols_from_watchlist(watchlist: dict[str, Any]) -> set[str]:
    symbols: set[str] = set()
    for payload in watchlist.get("themes", {}).values():
        for key in ("etf", "leader"):
            symbol = str(payload.get(key, {}).get("symbol", "")).strip()
            if symbol:
                symbols.add(symbol)
        for member in payload.get("members", []):
            symbol = str(member.get("symbol", "")).strip()
            if symbol:
                symbols.add(symbol)
    return symbols


def _eastmoney_secid(symbol: str) -> str:
    clean = symbol.strip()
    market = "1" if clean.startswith(("5", "6", "9")) else "0"
    return f"{market}.{clean}"


def _read_json(url: str, params: dict[str, str], proxy: str | None) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "market-impact-radar/0.1"})
    opener = _opener(proxy)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with opener.open(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - depends on network stability.
            last_error = exc
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))
    raise last_error or RuntimeError("unknown eastmoney error")


def _read_text(url: str, params: dict[str, str], proxy: str | None) -> str:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={
            "User-Agent": "Mozilla/5.0 market-impact-radar/0.1",
            "Referer": "https://finance.sina.com.cn/",
        },
    )
    opener = _opener(proxy)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with opener.open(request, timeout=20) as response:
                return response.read().decode("gbk", errors="replace")
        except Exception as exc:  # pragma: no cover - depends on network stability.
            last_error = exc
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))
    raise last_error or RuntimeError("unknown sina error")


def _read_json_from_urls(urls: Iterable[str], params: dict[str, str], proxy: str | None) -> dict[str, Any]:
    errors = []
    for url in urls:
        try:
            return _read_json(url, params, proxy)
        except Exception as exc:  # pragma: no cover - depends on network stability.
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def _parse_sina_market_rows(payload: str) -> list[dict[str, Any]]:
    text = payload.strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        normalized = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', text)
        normalized = re.sub(r",\s*([}\]])", r"\1", normalized)
        parsed = json.loads(normalized)
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _opener(proxy: str | None) -> urllib.request.OpenerDirector:
    if not proxy:
        return urllib.request.build_opener()
    return urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_float(value: Any) -> float | None:
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _change_pct(price: float | None, prev_close: float | None) -> float | None:
    if price is None or prev_close in (None, 0):
        return None
    return (price - prev_close) / prev_close * 100.0


def _value(value: float | None) -> float:
    return 0.0 if value is None else float(value)


def _missing_quote(symbol: str, fetched_at: str, warning: str) -> AShareQuote:
    return AShareQuote(
        symbol=symbol,
        name=symbol,
        source="eastmoney",
        fetched_at=fetched_at,
        data_status="missing",
        quality_warnings=(warning,),
    )
