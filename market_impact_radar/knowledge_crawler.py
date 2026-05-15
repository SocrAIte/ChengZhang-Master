from __future__ import annotations

import csv
import html
import json
import re
import ssl
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPSHandler, ProxyHandler, Request, build_opener, urlopen


DEFAULT_SOURCES = {
    "nasdaq_listed": "http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
    "nasdaq_other": "http://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
    "twse_listed": "https://openapi.twse.com.tw/v1/opendata/t187ap03_L",
    "tpex_listed": "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O",
    "sse_stock_list": (
        "http://query.sse.com.cn/security/stock/getStockListData2.do?"
        "STOCK_TYPE=1&COMPANY_STATUS=2,4,5,7,8&STOCK_CODE=&REG_PROVINCE=&CSRC_CODE=&"
        "sqlId=COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L&isPagination=true&"
        "pageHelp.cacheSize=1&pageHelp.beginPage=1&pageHelp.pageSize=10000&"
        "pageHelp.pageNo=1&pageHelp.endPage=1"
    ),
    "szse_stock_list": (
        "http://www.szse.cn/api/report/ShowReport/data?"
        "SHOWTYPE=JSON&CATALOGID=1110&TABKEY=tab1&PAGENO={page}&random=0.1"
    ),
    "eastmoney_clist": "https://push2.eastmoney.com/api/qt/clist/get"
}

EASTMONEY_ENDPOINTS = [
    "https://push2.eastmoney.com/api/qt/clist/get",
    "https://82.push2.eastmoney.com/api/qt/clist/get",
    "http://82.push2.eastmoney.com/api/qt/clist/get",
    "http://58.push2.eastmoney.com/api/qt/clist/get",
    "http://57.push2.eastmoney.com/api/qt/clist/get",
    "http://77.push2.eastmoney.com/api/qt/clist/get",
    "http://16.push2.eastmoney.com/api/qt/clist/get",
    "https://48.push2.eastmoney.com/api/qt/clist/get",
    "https://33.push2.eastmoney.com/api/qt/clist/get",
    "http://push2.eastmoney.com/api/qt/clist/get"
]

A_SHARE_FIELDS = "f12,f14,f2,f3,f20,f21,f100,f102,f103"
A_SHARE_FS = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
ETF_FS = "b:MK0021,b:MK0022,b:MK0023,b:MK0024"
BOARD_FIELDS = "f12,f14,f3,f62"
CONCEPT_BOARD_FS = "m:90+t:3+f:!50"
INDUSTRY_BOARD_FS = "m:90+t:2+f:!50"
_PROXY_URL: str | None = None
_PROXY_MODE = "foreign"
DOMESTIC_PROXY_BYPASS_HOSTS = (
    "eastmoney.com",
    "sse.com.cn",
    "szse.cn",
    "cninfo.com.cn",
)


@dataclass(frozen=True)
class CrawlResult:
    generated_dir: Path
    enriched_mapping_path: Path | None
    counts: dict[str, int]
    errors: tuple[str, ...]


def crawl_and_enrich(
    mapping_path: str | Path,
    rules_path: str | Path,
    generated_dir: str | Path = "data/generated",
    enriched_mapping_path: str | Path | None = "data/mappings.enriched.json",
    timeout: int = 20,
    sleep_seconds: float = 0.2,
    max_board_constituents: int = 80,
    max_stocks_per_theme: int = 80,
    use_eastmoney: bool = True,
    proxy: str | None = None,
    proxy_mode: str = "foreign",
) -> CrawlResult:
    set_proxy(proxy, proxy_mode)
    generated = Path(generated_dir)
    generated.mkdir(parents=True, exist_ok=True)
    mapping = _load_json(mapping_path)
    rules = _load_json(rules_path)
    errors: list[str] = []

    us_assets = _safe_fetch("US symbol directory", errors, lambda: fetch_us_symbols(timeout))
    us_assets = us_assets or _load_cached_rows(generated / "us_symbols.json")
    tw_assets = _safe_fetch("TWSE/TPEx listed companies", errors, lambda: fetch_taiwan_symbols(timeout))
    tw_assets = tw_assets or _load_cached_rows(generated / "taiwan_symbols.json")
    a_stocks = []
    a_etfs = []
    boards = []
    if use_eastmoney:
        a_stocks = _safe_fetch("A-share stocks", errors, lambda: fetch_eastmoney_clist(A_SHARE_FS, A_SHARE_FIELDS, timeout))
        a_stocks = a_stocks or _load_cached_rows(generated / "a_share_stocks.json")
        a_etfs = _safe_fetch("China ETFs", errors, lambda: fetch_eastmoney_clist(ETF_FS, A_SHARE_FIELDS, timeout))
        a_etfs = a_etfs or _load_cached_rows(generated / "china_etfs.json")
        boards = _safe_fetch("Eastmoney boards", errors, lambda: fetch_eastmoney_boards(timeout))
        boards = boards or _load_cached_rows(generated / "eastmoney_boards.json")
    sse_stocks = _safe_fetch("SSE stock list", errors, lambda: fetch_sse_stocks(timeout))
    szse_stocks = _safe_fetch("SZSE stock list", errors, lambda: fetch_szse_stocks(timeout))
    official_a_stocks = _dedupe_by_code(sse_stocks + szse_stocks)
    official_a_stocks = official_a_stocks or _load_cached_rows(generated / "official_a_share_stocks.json")
    if not a_stocks:
        a_stocks = official_a_stocks
    else:
        a_stocks = _dedupe_by_code(a_stocks + official_a_stocks)
    board_members = []
    for board in boards[:max_board_constituents]:
        code = str(board.get("code", ""))
        if not code.startswith("BK"):
            continue
        time.sleep(sleep_seconds)
        members = _safe_fetch(
            f"Eastmoney board {code}",
            errors,
            lambda code=code: fetch_eastmoney_clist(f"b:{code}", A_SHARE_FIELDS, timeout),
        )
        if not members:
            members = [
                row for row in _load_cached_rows(generated / "eastmoney_board_members.json")
                if row.get("board_code") == code
            ]
        for member in members:
            member["board_code"] = code
            member["board_name"] = board.get("name", "")
        board_members.extend(members)

    universes = {
        "us_symbols": us_assets,
        "taiwan_symbols": tw_assets,
        "a_share_stocks": a_stocks,
        "official_a_share_stocks": official_a_stocks,
        "china_etfs": a_etfs,
        "eastmoney_boards": boards,
        "eastmoney_board_members": board_members
    }
    for name, rows in universes.items():
        _write_json(generated / f"{name}.json", rows)

    external_candidates = build_external_asset_candidates(mapping, rules, us_assets + tw_assets)
    theme_candidates = build_theme_candidates(rules, a_stocks, a_etfs, board_members)
    _write_json(generated / "external_asset_candidates.json", external_candidates)
    _write_json(generated / "theme_candidates.json", theme_candidates)

    output_path = Path(enriched_mapping_path) if enriched_mapping_path else None
    if output_path:
        enriched = merge_generated_mapping(
            mapping,
            external_candidates,
            theme_candidates,
            max_stocks_per_theme=max_stocks_per_theme,
        )
        _write_json(output_path, enriched)

    counts = {name: len(rows) for name, rows in universes.items()}
    counts["external_asset_candidates"] = len(external_candidates)
    counts["themes_with_candidates"] = len(theme_candidates)
    return CrawlResult(generated, output_path, counts, tuple(errors))


def fetch_us_symbols(timeout: int = 20) -> list[dict[str, Any]]:
    listed = _fetch_text(DEFAULT_SOURCES["nasdaq_listed"], timeout)
    other = _fetch_text(DEFAULT_SOURCES["nasdaq_other"], timeout)
    return parse_nasdaq_listed(listed) + parse_nasdaq_other(other)


def set_proxy(proxy: str | None, proxy_mode: str = "foreign") -> None:
    global _PROXY_MODE, _PROXY_URL
    _PROXY_URL = proxy.strip() if proxy else None
    _PROXY_MODE = proxy_mode


def fetch_taiwan_symbols(timeout: int = 20) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for market, url in (("TWSE", DEFAULT_SOURCES["twse_listed"]), ("TPEx", DEFAULT_SOURCES["tpex_listed"])):
        payload = _fetch_json(url, timeout)
        for item in payload if isinstance(payload, list) else []:
            code = _first_value(item, ["公司代號", "股票代號", "有價證券代號", "Code"])
            name = _first_value(item, ["公司簡稱", "公司名稱", "有價證券名稱", "Name"])
            industry = _first_value(item, ["產業別", "Industry"])
            if code and name:
                suffix = ".TW" if market == "TWSE" else ".TWO"
                rows.append({
                    "symbol": f"{code}{suffix}",
                    "code": code,
                    "name": name,
                    "market": market,
                    "industry": industry,
                    "source": url
                })
    return rows


def fetch_official_a_share_stocks(timeout: int = 20) -> list[dict[str, Any]]:
    return _dedupe_by_code(fetch_sse_stocks(timeout) + fetch_szse_stocks(timeout))


def fetch_sse_stocks(timeout: int = 20) -> list[dict[str, Any]]:
    payload = _fetch_json(DEFAULT_SOURCES["sse_stock_list"], timeout)
    raw_rows = payload.get("result", []) if isinstance(payload, dict) else []
    rows = []
    for item in raw_rows:
        code = _first_value(item, ["A_STOCK_CODE", "SECURITY_CODE_A", "SECURITY_CODE", "stockCode"])
        name = _first_value(item, ["SECURITY_ABBR_A", "COMPANY_ABBR", "SECURITY_ABBR", "stockName"])
        industry = _first_value(item, ["CSRC_CODE_DESC", "CSRC_CODE", "industry"])
        if code and name:
            rows.append({
                "code": code,
                "name": name,
                "market": "SSE",
                "industry": industry,
                "source": "sse"
            })
    return rows


def fetch_szse_stocks(timeout: int = 20) -> list[dict[str, Any]]:
    rows = []
    seen_codes = set()
    for page in range(1, 301):
        payload = _fetch_json(DEFAULT_SOURCES["szse_stock_list"].format(page=page), timeout)
        raw_rows: list[dict[str, Any]] = []
        if isinstance(payload, list):
            for block in payload:
                if isinstance(block, dict) and isinstance(block.get("data"), list):
                    raw_rows.extend(block["data"])
        elif isinstance(payload, dict) and isinstance(payload.get("data"), list):
            raw_rows.extend(payload["data"])
        if not raw_rows:
            break
        before_count = len(rows)
        for item in raw_rows:
            code = _first_value(item, ["agdm", "zqdm", "A股代码", "证券代码"])
            name = _strip_html(_first_value(item, ["agjc", "zqjc", "A股简称", "证券简称"]))
            industry = _strip_html(_first_value(item, ["sshymc", "行业", "所属行业"]))
            if code and name and code not in seen_codes:
                rows.append({
                    "code": code,
                    "name": name,
                    "market": "SZSE",
                    "industry": industry,
                    "source": "szse"
                })
                seen_codes.add(code)
        if len(rows) == before_count or len(raw_rows) < 20:
            break
    return rows


def fetch_eastmoney_clist(fs: str, fields: str, timeout: int = 20, page_size: int = 100) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    total = None
    while total is None or len(rows) < total:
        params = {
            "pn": page,
            "pz": page_size,
            "po": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "dect": 1,
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fs": fs,
            "fields": fields,
            "_": int(time.time() * 1000)
        }
        payload = _fetch_first_json(EASTMONEY_ENDPOINTS, params, timeout)
        data = payload.get("data") if isinstance(payload, dict) else None
        if not data:
            break
        diff = data.get("diff") or []
        total = int(data.get("total") or len(diff))
        if not diff:
            break
        rows.extend(_normalize_eastmoney_row(row) for row in diff)
        if len(rows) >= total:
            break
        page += 1
    return rows


def fetch_eastmoney_boards(timeout: int = 20) -> list[dict[str, Any]]:
    boards = []
    for fs, kind in ((CONCEPT_BOARD_FS, "concept"), (INDUSTRY_BOARD_FS, "industry")):
        for row in fetch_eastmoney_clist(fs, BOARD_FIELDS, timeout):
            row["kind"] = kind
            boards.append(row)
    return boards


def parse_nasdaq_listed(text: str) -> list[dict[str, Any]]:
    rows = []
    for row in _pipe_rows(text):
        symbol = row.get("Symbol", "").strip()
        name = row.get("Security Name", "").strip()
        if not symbol or symbol.startswith("File Creation Time"):
            continue
        if row.get("Test Issue", "N") == "Y":
            continue
        rows.append({
            "symbol": symbol,
            "name": name,
            "market": "US",
            "exchange": "NASDAQ",
            "asset_type": "etf" if row.get("ETF") == "Y" else "equity"
        })
    return rows


def parse_nasdaq_other(text: str) -> list[dict[str, Any]]:
    exchange_map = {"A": "NYSE American", "N": "NYSE", "P": "NYSE Arca", "Z": "BATS"}
    rows = []
    for row in _pipe_rows(text):
        symbol = row.get("ACT Symbol", "").strip()
        name = row.get("Security Name", "").strip()
        if not symbol or symbol.startswith("File Creation Time"):
            continue
        if row.get("Test Issue", "N") == "Y":
            continue
        rows.append({
            "symbol": symbol,
            "name": name,
            "market": "US",
            "exchange": exchange_map.get(row.get("Exchange"), row.get("Exchange", "")),
            "asset_type": "etf" if row.get("ETF") == "Y" else "equity"
        })
    return rows


def build_external_asset_candidates(
    mapping: dict[str, Any],
    rules: dict[str, Any],
    assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_symbols = {item.get("symbol") for item in mapping.get("external_assets", [])}
    symbol_hints = {
        symbol.upper(): theme
        for theme, symbols in rules.get("external_symbol_hints", {}).items()
        for symbol in symbols
    }
    candidates = []
    for asset in assets:
        symbol = str(asset.get("symbol", "")).upper()
        if not _is_external_equity_candidate(asset) and symbol not in symbol_hints:
            continue
        searchable = " ".join(str(asset.get(key, "")) for key in ("symbol", "name", "industry", "exchange"))
        themes = set()
        if symbol in symbol_hints:
            themes.add(symbol_hints[symbol])
        themes.update(_match_themes(searchable, rules))
        if not themes or symbol in existing_symbols:
            continue
        candidates.append({
            "symbol": asset.get("symbol"),
            "name": asset.get("name") or asset.get("symbol"),
            "market": asset.get("market", "US"),
            "asset_type": "equity",
            "group": _group_for_themes(themes),
            "themes": sorted(themes),
            "source": "crawler"
        })
    return candidates


def build_theme_candidates(
    rules: dict[str, Any],
    a_stocks: list[dict[str, Any]],
    a_etfs: list[dict[str, Any]],
    board_members: list[dict[str, Any]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    result: dict[str, dict[str, list[dict[str, Any]]]] = {}
    merged_stocks = _dedupe_by_code(a_stocks + board_members)
    for stock in merged_stocks:
        searchable = " ".join(str(stock.get(key, "")) for key in ("name", "industry", "concepts", "board_name", "code"))
        for theme in _match_themes(searchable, rules):
            result.setdefault(theme, {"stocks": [], "etfs": []})["stocks"].append({
                "name": stock.get("name"),
                "code": stock.get("code"),
                "role": _role_for_stock(stock),
                "elasticity": 0.58,
                "risk": _risk_for_stock(stock, rules),
                "source": "crawler"
            })
    for etf in a_etfs:
        searchable = " ".join(str(etf.get(key, "")) for key in ("name", "industry", "concepts"))
        for theme in _match_themes(searchable, rules):
            result.setdefault(theme, {"stocks": [], "etfs": []})["etfs"].append({
                "name": etf.get("name"),
                "code": etf.get("code"),
                "source": "crawler"
            })
    for values in result.values():
        values["stocks"] = _dedupe_stock_candidates(values["stocks"])
        values["etfs"] = _dedupe_etf_candidates(values["etfs"])
    return result


def merge_generated_mapping(
    mapping: dict[str, Any],
    external_candidates: list[dict[str, Any]],
    theme_candidates: dict[str, dict[str, list[dict[str, Any]]]],
    max_stocks_per_theme: int = 80,
) -> dict[str, Any]:
    enriched = json.loads(json.dumps(mapping, ensure_ascii=False))
    existing_symbols = {item.get("symbol") for item in enriched.get("external_assets", [])}
    for candidate in external_candidates:
        if candidate.get("symbol") not in existing_symbols:
            enriched.setdefault("external_assets", []).append(candidate)
            existing_symbols.add(candidate.get("symbol"))
    theme_mappings = enriched.setdefault("theme_mappings", {})
    for theme, candidates in theme_candidates.items():
        theme_config = theme_mappings.setdefault(theme, {"industries": [], "etfs": [], "stocks": [], "clarity": 0.55})
        existing_etfs = set(theme_config.get("etfs", []))
        for etf in candidates.get("etfs", []):
            name = etf.get("name")
            if name and name not in existing_etfs:
                theme_config.setdefault("etfs", []).append(name)
                existing_etfs.add(name)
        existing_stocks = {stock.get("name") for stock in theme_config.get("stocks", [])}
        for stock in candidates.get("stocks", []):
            name = stock.get("name")
            if not name or name in existing_stocks:
                continue
            theme_config.setdefault("stocks", []).append({
                "name": name,
                "role": stock.get("role", theme),
                "elasticity": stock.get("elasticity", 0.58),
                "risk": stock.get("risk", "中"),
                "source": "crawler",
                "code": stock.get("code")
            })
            existing_stocks.add(name)
            if len(theme_config["stocks"]) >= max_stocks_per_theme:
                break
    enriched["generated_note"] = "Generated candidates are keyword/board matches and should be reviewed before live trading."
    return enriched


def _fetch_text(url: str, timeout: int) -> str:
    referer = "https://quote.eastmoney.com/"
    if "sse.com.cn" in url:
        referer = "http://www.sse.com.cn/assortment/stock/list/share/"
    elif "szse.cn" in url:
        referer = "http://www.szse.cn/market/product/stock/list/index.html"
    elif "twse.com.tw" in url or "tpex.org.tw" in url:
        referer = "https://www.twse.com.tw/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
        "Connection": "close",
        "Referer": referer
    }
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            request = Request(url, headers=headers)
            context = ssl._create_unverified_context() if url.startswith("https://") else None
            if _should_use_proxy(url):
                handlers: list[Any] = [ProxyHandler({"http": _PROXY_URL, "https": _PROXY_URL})]
                if context:
                    handlers.append(HTTPSHandler(context=context))
                opener = build_opener(*handlers)
                response_context = opener.open(request, timeout=timeout)
            else:
                response_context = urlopen(request, timeout=timeout, context=context)
            with response_context as response:
                return response.read().decode("utf-8-sig", errors="replace")
        except Exception as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _should_use_proxy(url: str) -> bool:
    if not _PROXY_URL:
        return False
    if _PROXY_MODE == "all":
        return True
    host = (urlparse(url).hostname or "").lower()
    return not any(host == domain or host.endswith(f".{domain}") for domain in DOMESTIC_PROXY_BYPASS_HOSTS)


def _fetch_json(url: str, timeout: int) -> Any:
    text = _fetch_text(url, timeout).strip()
    if text and not text.startswith("{") and not text.startswith("[") and "(" in text:
        text = text.split("(", 1)[1].rsplit(")", 1)[0]
    return json.loads(text)


def _fetch_first_json(endpoints: list[str], params: dict[str, Any], timeout: int) -> Any:
    query = urlencode(params)
    last_error: Exception | None = None
    for endpoint in endpoints:
        try:
            return _fetch_json(f"{endpoint}?{query}", timeout)
        except Exception as exc:
            last_error = exc
            time.sleep(0.3)
    assert last_error is not None
    raise last_error


def _pipe_rows(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if "|" in line]
    return list(csv.DictReader(lines, delimiter="|"))


def _normalize_eastmoney_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": str(row.get("f12", "")),
        "name": str(row.get("f14", "")),
        "last_price": _number_or_none(row.get("f2")),
        "change_pct": _number_or_none(row.get("f3")),
        "market_cap": _number_or_none(row.get("f20")),
        "float_market_cap": _number_or_none(row.get("f21")),
        "industry": _clean_dash(row.get("f100")),
        "region": _clean_dash(row.get("f102")),
        "concepts": _clean_dash(row.get("f103"))
    }


def _number_or_none(value: Any) -> float | None:
    if value in (None, "-", ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_dash(value: Any) -> str:
    return "" if value in (None, "-") else _strip_html(str(value))


def _strip_html(value: str) -> str:
    text = html.unescape(value)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_cached_rows(path: str | Path) -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return []
    return payload if isinstance(payload, list) else []


def _safe_fetch(label: str, errors: list[str], fetcher: Any) -> list[dict[str, Any]]:
    try:
        return fetcher()
    except Exception as exc:
        errors.append(f"{label}: {exc}")
        return []


def _first_value(item: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""


def _match_themes(text: str, rules: dict[str, Any]) -> set[str]:
    text_lower = text.lower()
    matched = set()
    for theme, keywords in rules.get("theme_keywords", {}).items():
        for keyword in keywords:
            if str(keyword).lower() in text_lower:
                matched.add(theme)
                break
    return matched


def _is_external_equity_candidate(asset: dict[str, Any]) -> bool:
    if asset.get("asset_type") != "equity":
        return False
    name = str(asset.get("name", "")).lower()
    symbol = str(asset.get("symbol", ""))
    noisy_name_tokens = [
        " etf",
        "fund",
        "warrant",
        "rights",
        "units",
        "note due",
        "preferred",
        "depositary share",
        "leverage shares",
        "2x long",
        "2x short",
        "3x long",
        "3x short",
    ]
    if any(token in name for token in noisy_name_tokens):
        return False
    noisy_symbol_suffixes = ("W", "R", "U")
    if len(symbol) >= 5 and symbol.endswith(noisy_symbol_suffixes):
        return False
    return True


def _group_for_themes(themes: set[str]) -> str:
    first = sorted(themes)[0]
    return f"{first}链"


def _role_for_stock(stock: dict[str, Any]) -> str:
    for key in ("board_name", "industry", "concepts"):
        value = str(stock.get(key, "")).strip()
        if value:
            return value[:32]
    return "爬虫候选"


def _risk_for_stock(stock: dict[str, Any], rules: dict[str, Any]) -> str:
    cap = stock.get("market_cap")
    if cap is None:
        return "中"
    for rule in rules.get("risk_by_market_cap_cny", []):
        if cap < float(rule.get("lt", 0)):
            return str(rule.get("risk", "中"))
    return "中"


def _dedupe_by_code(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in rows:
        code = str(row.get("code", ""))
        if not code:
            continue
        current = merged.setdefault(code, {})
        current.update({key: value for key, value in row.items() if value not in (None, "")})
    return list(merged.values())


def _dedupe_stock_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("name") or row.get("code"))
        if key and key not in result:
            result[key] = row
    return sorted(result.values(), key=lambda item: (item.get("risk", "中"), item.get("name", "")))


def _dedupe_etf_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("name") or row.get("code"))
        if key and key not in result:
            result[key] = row
    return sorted(result.values(), key=lambda item: item.get("name", ""))
