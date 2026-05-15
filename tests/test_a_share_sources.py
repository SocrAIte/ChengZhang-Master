from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

from market_impact_radar import a_share_sources as sources
from market_impact_radar.a_share_sources import AShareQuote, build_a_share_snapshot, summarize_market_breadth
from market_impact_radar.trading_calendar import TradingCalendars
from market_impact_radar.validation import validate_file


ROOT = Path(__file__).resolve().parents[1]


class TradingCalendarTest(unittest.TestCase):
    def test_us_close_utc_respects_daylight_saving_time(self) -> None:
        calendars = TradingCalendars()

        self.assertEqual(calendars.market_close_utc("US", date(2026, 1, 15)).hour, 21)
        self.assertEqual(calendars.market_close_utc("US", date(2026, 7, 15)).hour, 20)

    def test_external_session_maps_to_next_a_share_trading_day(self) -> None:
        calendars = TradingCalendars(
            holidays={
                "CN": {"2026-05-15"},
                "US": set(),
                "JP": {"2026-05-15"},
                "TW": set(),
            }
        )

        self.assertEqual(
            calendars.map_external_session_to_a_share_day("US", date(2026, 5, 14)),
            date(2026, 5, 18),
        )
        self.assertFalse(calendars.is_trading_day("JP", date(2026, 5, 15)))

    def test_calendar_context_marks_a_share_closed(self) -> None:
        calendars = TradingCalendars(holidays={"CN": {"2026-05-15"}, "US": set(), "JP": set(), "TW": set()})
        context = calendars.build_context(
            datetime(2026, 5, 15, 1, 30, tzinfo=timezone.utc),
            external_sessions={"US": date(2026, 5, 14)},
        )

        self.assertFalse(context["is_a_share_trading_day"])
        self.assertEqual(context["a_share_trade_day"], "2026-05-18")
        self.assertEqual(context["external_sessions"]["US"]["mapped_a_share_trade_day"], "2026-05-18")


class AShareSourcesTest(unittest.TestCase):
    def test_build_a_share_snapshot_from_quotes(self) -> None:
        watchlist = {
            "themes": {
                "AI算力": {
                    "etf": {"symbol": "515070", "name": "人工智能ETF"},
                    "leader": {"symbol": "601138", "name": "工业富联"},
                    "members": [
                        {"symbol": "601138"},
                        {"symbol": "300308"},
                        {"symbol": "300502"},
                    ],
                }
            }
        }
        quotes = {
            "515070": AShareQuote("515070", "人工智能ETF", "test", "2026-05-15T01:45:00+00:00", change_pct=1.2, open_gap_pct=0.8),
            "601138": AShareQuote("601138", "工业富联", "test", "2026-05-15T01:45:00+00:00", change_pct=4.5, open_gap_pct=1.2, amount=20_000_000),
            "300308": AShareQuote("300308", "中际旭创", "test", "2026-05-15T01:45:00+00:00", change_pct=6.2, amount=30_000_000),
            "300502": AShareQuote("300502", "新易盛", "test", "2026-05-15T01:45:00+00:00", change_pct=5.1, amount=40_000_000),
        }

        snapshot = build_a_share_snapshot(
            watchlist=watchlist,
            quote_map=quotes,
            market_quotes=quotes.values(),
            fetched_at="2026-05-15T01:45:00+00:00",
        )

        self.assertEqual(snapshot["themes"]["AI算力"]["data_status"], "ok")
        self.assertEqual(snapshot["themes"]["AI算力"]["stocks_over_5pct_count"], 2)
        self.assertEqual(snapshot["market_breadth"]["up_count"], 4)

    def test_market_breadth_counts(self) -> None:
        breadth = summarize_market_breadth(
            [
                AShareQuote("000001", "A", "test", "now", change_pct=5.1, amount=100_000_000),
                AShareQuote("000002", "B", "test", "now", change_pct=-1.0, amount=200_000_000),
                AShareQuote("000003", "C", "test", "now", change_pct=0.0, amount=300_000_000),
                AShareQuote("000004", "D", "test", "now", change_pct=None, amount=400_000_000, data_status="missing"),
            ]
        )

        self.assertEqual(breadth["turnover_billion"], 6.0)
        self.assertEqual(breadth["source"], "test")
        self.assertEqual(breadth["data_status"], "ok")
        self.assertEqual(breadth["up_count"], 1)
        self.assertEqual(breadth["down_count"], 1)
        self.assertEqual(breadth["unchanged_count"], 1)
        self.assertEqual(breadth["stocks_over_5pct_count"], 1)

    def test_sina_market_rows_parse_js_like_payload(self) -> None:
        payload = '[{symbol:"sh600000",code:"600000",name:"PF Bank",trade:"10.20",settlement:"10.00",open:"10.10",changepercent:"2.00",volume:1000,amount:20400}]'

        rows = sources._parse_sina_market_rows(payload)
        quote = sources._quote_from_sina_row(rows[0], "2026-05-15T01:45:00+00:00")

        self.assertEqual(quote.symbol, "600000")
        self.assertEqual(quote.source, "sina")
        self.assertEqual(quote.change_pct, 2.0)
        self.assertAlmostEqual(quote.open_gap_pct or 0.0, 1.0)

    def test_fetch_a_share_snapshot_falls_back_to_sina_breadth(self) -> None:
        watchlist = {
            "themes": {
                "AI": {
                    "etf": {"symbol": "515070"},
                    "leader": {"symbol": "601138"},
                    "members": [{"symbol": "601138"}],
                }
            }
        }
        quote = AShareQuote(
            "515070",
            "ETF",
            "eastmoney",
            "2026-05-15T01:45:00+00:00",
            price=1.0,
            prev_close=0.99,
            change_pct=1.0,
        )
        leader = AShareQuote(
            "601138",
            "Leader",
            "eastmoney",
            "2026-05-15T01:45:00+00:00",
            price=10.0,
            prev_close=9.5,
            change_pct=5.2,
        )
        breadth = AShareQuote(
            "600000",
            "PF Bank",
            "sina",
            "2026-05-15T01:45:00+00:00",
            price=10.2,
            prev_close=10.0,
            change_pct=2.0,
            amount=100_000_000,
        )

        with patch.object(sources, "fetch_eastmoney_quotes", return_value=(quote, leader)):
            with patch.object(sources, "fetch_eastmoney_market_quotes", side_effect=OSError("closed")):
                with patch.object(sources, "fetch_sina_market_quotes", return_value=(breadth,)):
                    snapshot = sources.fetch_a_share_snapshot(watchlist)

        self.assertEqual(snapshot["market_breadth"]["source"], "sina")
        self.assertEqual(snapshot["market_breadth"]["up_count"], 1)
        self.assertIn("market_breadth/eastmoney", snapshot["source_summary"]["errors"][0])

    def test_schema_validation_accepts_a_share_snapshot_sample(self) -> None:
        validate_file(ROOT / "data" / "a_share_snapshot.sample.json", "a_share_snapshot.schema.json")


if __name__ == "__main__":
    unittest.main()
