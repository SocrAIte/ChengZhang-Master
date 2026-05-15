from __future__ import annotations

import unittest

from market_impact_radar.knowledge_crawler import (
    build_external_asset_candidates,
    build_theme_candidates,
    parse_nasdaq_listed,
    parse_nasdaq_other,
)
from market_impact_radar.knowledge_verifier import build_daily_check_result, suggest_mapping_fixes, verify_mapping


class KnowledgeCrawlerTest(unittest.TestCase):
    def test_parse_nasdaq_listed(self) -> None:
        text = (
            "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
            "NVDA|NVIDIA Corporation - Common Stock|Q|N|N|100|N|N\n"
            "TEST|Test Issue|Q|Y|N|100|N|N\n"
            "File Creation Time: 0514202618:03|||||||\n"
        )

        rows = parse_nasdaq_listed(text)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symbol"], "NVDA")
        self.assertEqual(rows[0]["asset_type"], "equity")

    def test_parse_nasdaq_other(self) -> None:
        text = (
            "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\n"
            "GLD|SPDR Gold Shares|P|GLD|Y|100|N|GLD\n"
        )

        rows = parse_nasdaq_other(text)

        self.assertEqual(rows[0]["symbol"], "GLD")
        self.assertEqual(rows[0]["asset_type"], "etf")

    def test_build_candidates_from_keywords(self) -> None:
        mapping = {"external_assets": [{"symbol": "MU"}]}
        rules = {
            "theme_keywords": {"AI算力": ["NVIDIA", "GPU", "AI服务器"], "存储芯片": ["Micron"]},
            "external_symbol_hints": {"AI算力": ["NVDA"]},
            "risk_by_market_cap_cny": [{"lt": 999999999999999, "risk": "中"}],
        }
        external = [{"symbol": "NVDA", "name": "NVIDIA Corporation", "market": "US"}]
        stocks = [{"code": "000001", "name": "算力科技", "industry": "AI服务器", "market_cap": 20000000000}]
        etfs = [{"code": "510000", "name": "人工智能ETF"}]

        external_candidates = build_external_asset_candidates(mapping, rules, external)
        theme_candidates = build_theme_candidates(rules, stocks, etfs, [])

        self.assertEqual(external_candidates[0]["symbol"], "NVDA")
        self.assertIn("AI算力", theme_candidates)
        self.assertEqual(theme_candidates["AI算力"]["stocks"][0]["name"], "算力科技")

    def test_verify_mapping_reports_missing_references(self) -> None:
        mapping = {
            "external_assets": [
                {"symbol": "NVDA", "market": "US", "asset_type": "equity", "themes": ["AI算力"]},
                {"symbol": "FAKE", "market": "US", "asset_type": "equity", "themes": ["不存在主题"]},
            ],
            "market_groups": {"AI链": {"themes": ["AI算力", "不存在主题"]}},
            "theme_mappings": {
                "AI算力": {
                    "etfs": ["人工智能ETF"],
                    "stocks": [{"name": "工业富联", "code": "601138"}],
                }
            },
        }
        universes = {
            "us_symbols": [{"symbol": "NVDA"}],
            "taiwan_symbols": [],
            "a_share_stocks": [{"code": "601138", "name": "工业富联"}],
            "official_a_share_stocks": [],
            "china_etfs": [{"code": "515070", "name": "人工智能ETF"}],
        }

        report = verify_mapping(mapping, universes)

        kinds = {issue["kind"] for issue in report["issues"]}
        self.assertIn("external_asset_missing", kinds)
        self.assertIn("external_theme_missing", kinds)
        self.assertIn("market_group_theme_missing", kinds)
        self.assertEqual(report["theme_mappings"][0]["stocks_missing"], 0)

    def test_verify_mapping_treats_manual_a_share_code_as_coded(self) -> None:
        mapping = {
            "external_assets": [],
            "market_groups": {},
            "theme_mappings": {
                "储能": {
                    "stocks": [{"name": "阳光电源", "code": "300274"}],
                    "etfs": [],
                }
            },
        }
        universes = {
            "us_symbols": [],
            "taiwan_symbols": [],
            "a_share_stocks": [],
            "official_a_share_stocks": [],
            "eastmoney_board_members": [],
            "china_etfs": [],
        }

        report = verify_mapping(mapping, universes)

        self.assertEqual(report["theme_mappings"][0]["stocks_missing"], 0)
        self.assertEqual(report["theme_mappings"][0]["stocks_coded_unverified"], 1)

    def test_verify_mapping_honors_external_asset_overrides(self) -> None:
        mapping = {
            "verification_overrides": {
                "external_assets": {
                    "SSNLF": {
                        "status": "ok",
                        "verified_by": "manual_exception/otc",
                        "alias": "005930.KS",
                    }
                }
            },
            "external_assets": [
                {"symbol": "SSNLF", "market": "US", "asset_type": "equity", "themes": ["存储芯片"]},
            ],
            "market_groups": {},
            "theme_mappings": {"存储芯片": {"stocks": [], "etfs": ["芯片ETF"]}},
        }
        universes = {
            "us_symbols": [],
            "taiwan_symbols": [],
            "a_share_stocks": [],
            "official_a_share_stocks": [],
            "eastmoney_board_members": [],
            "china_etfs": [{"name": "芯片ETF"}],
        }

        report = verify_mapping(mapping, universes)

        self.assertFalse(any(issue["kind"] == "external_asset_missing" for issue in report["issues"]))
        self.assertEqual(report["external_assets"][0]["status"], "ok")
        self.assertEqual(report["external_assets"][0]["alias"], "005930.KS")

    def test_daily_check_result_fails_when_thresholds_exceeded(self) -> None:
        report = {
            "quality_counts": {"high": 1, "medium": 0, "low": 0, "total": 1},
            "source_summary": {"mode": "cache"},
            "issues": [{"severity": "high", "kind": "missing", "target": "X", "message": "bad"}],
        }

        result = build_daily_check_result(report, max_high=0, max_medium=0)

        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["quality_counts"]["high"], 1)

    def test_suggest_mapping_fixes_builds_theme_stub_once(self) -> None:
        report = {
            "verified_at": "2026-05-15T00:00:00+00:00",
            "issues": [
                {
                    "severity": "high",
                    "kind": "external_theme_missing",
                    "target": "AVGO",
                    "message": "theme 交换机 is not in theme_mappings",
                },
                {
                    "severity": "high",
                    "kind": "market_group_theme_missing",
                    "target": "AI网络链",
                    "message": "theme 交换机 is not in theme_mappings",
                },
                {
                    "severity": "medium",
                    "kind": "external_asset_missing",
                    "target": "SSNLF",
                    "message": "SSNLF not found in nasdaq universe",
                },
            ],
        }

        suggestions = suggest_mapping_fixes(report)

        self.assertEqual(suggestions["summary"]["suggestions"], 2)
        self.assertEqual(suggestions["suggestions"][0]["target"], "交换机")
        self.assertEqual(suggestions["suggestions"][1]["kind"], "add_external_asset_override_or_alias")


if __name__ == "__main__":
    unittest.main()
