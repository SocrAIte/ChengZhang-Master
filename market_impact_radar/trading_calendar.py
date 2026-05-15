from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


MARKET_TIMEZONES = {
    "CN": "Asia/Shanghai",
    "US": "America/New_York",
    "JP": "Asia/Tokyo",
    "TW": "Asia/Taipei",
}

MARKET_CLOSE_TIMES = {
    "CN": time(15, 0),
    "US": time(16, 0),
    "JP": time(15, 30),
    "TW": time(13, 30),
}

DEFAULT_HOLIDAYS = {
    "CN": {
        "2026-01-01",
        "2026-02-16",
        "2026-02-17",
        "2026-02-18",
        "2026-02-19",
        "2026-02-20",
        "2026-04-06",
        "2026-05-01",
        "2026-05-04",
        "2026-05-05",
        "2026-06-19",
        "2026-09-25",
        "2026-10-01",
        "2026-10-02",
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
    },
    "US": {
        "2026-01-01",
        "2026-01-19",
        "2026-02-16",
        "2026-04-03",
        "2026-05-25",
        "2026-06-19",
        "2026-07-03",
        "2026-09-07",
        "2026-11-26",
        "2026-12-25",
    },
    "JP": {
        "2026-01-01",
        "2026-01-02",
        "2026-01-12",
        "2026-02-11",
        "2026-02-23",
        "2026-03-20",
        "2026-04-29",
        "2026-05-04",
        "2026-05-05",
        "2026-05-06",
        "2026-07-20",
        "2026-08-11",
        "2026-09-21",
        "2026-09-22",
        "2026-09-23",
        "2026-10-12",
        "2026-11-03",
        "2026-11-23",
        "2026-12-31",
    },
    "TW": {
        "2026-01-01",
        "2026-02-16",
        "2026-02-17",
        "2026-02-18",
        "2026-02-19",
        "2026-02-20",
        "2026-02-27",
        "2026-04-03",
        "2026-04-06",
        "2026-05-01",
        "2026-06-19",
        "2026-09-25",
        "2026-10-09",
    },
}


@dataclass(frozen=True)
class TradingCalendars:
    holidays: dict[str, set[str]] = field(default_factory=lambda: {key: set(value) for key, value in DEFAULT_HOLIDAYS.items()})

    def is_trading_day(self, market: str, day: date) -> bool:
        market_key = market.upper()
        return day.weekday() < 5 and day.isoformat() not in self.holidays.get(market_key, set())

    def next_trading_day(self, market: str, day: date) -> date:
        current = day
        while not self.is_trading_day(market, current):
            current += timedelta(days=1)
        return current

    def previous_trading_day(self, market: str, day: date) -> date:
        current = day
        while not self.is_trading_day(market, current):
            current -= timedelta(days=1)
        return current

    def market_close_utc(self, market: str, session_date: date) -> datetime:
        market_key = market.upper()
        zone = ZoneInfo(MARKET_TIMEZONES[market_key])
        close_time = MARKET_CLOSE_TIMES[market_key]
        local_close = datetime.combine(session_date, close_time, zone)
        return local_close.astimezone(timezone.utc)

    def map_external_session_to_a_share_day(self, external_market: str, session_date: date) -> date:
        close_utc = self.market_close_utc(external_market, session_date)
        china_day_at_close = close_utc.astimezone(ZoneInfo(MARKET_TIMEZONES["CN"])).date()
        return self.next_trading_day("CN", china_day_at_close)

    def build_context(self, as_of: datetime, external_sessions: dict[str, date] | None = None) -> dict:
        china_now = as_of.astimezone(ZoneInfo(MARKET_TIMEZONES["CN"]))
        cn_day = china_now.date()
        context = {
            "as_of": china_now.isoformat(),
            "a_share_trade_day": self.next_trading_day("CN", cn_day).isoformat(),
            "is_a_share_trading_day": self.is_trading_day("CN", cn_day),
            "external_sessions": {},
        }
        for market, session_day in (external_sessions or {}).items():
            context["external_sessions"][market.upper()] = {
                "session_date": session_day.isoformat(),
                "is_market_trading_day": self.is_trading_day(market, session_day),
                "market_close_utc": self.market_close_utc(market, session_day).isoformat(),
                "mapped_a_share_trade_day": self.map_external_session_to_a_share_day(market, session_day).isoformat(),
            }
        return context
