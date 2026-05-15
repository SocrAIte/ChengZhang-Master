from __future__ import annotations

import unittest

from market_impact_radar.knowledge_crawler import (
    build_external_asset_candidates,
    build_theme_candidates,
    parse_nasdaq_listed,
    parse_nasdaq_other,
)


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


if __name__ == "__main__":
    unittest.main()
