from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from market_impact_radar.backtest import (
    build_historical_edges,
    compute_batch_transmission_stats,
    compute_transmission_stats,
)
from market_impact_radar.dashboard import render_dashboard_html
from market_impact_radar.intraday import evaluate_intraday, render_intraday_report
from market_impact_radar.io import load_mappings
from market_impact_radar.models import ExternalAsset
from market_impact_radar.pipeline import run_report_pipeline
from market_impact_radar.quote_sources import QuoteRecord, consolidate_quote_records
from market_impact_radar.report import render_markdown_report
from market_impact_radar.review_feedback import summarize_review_result
from market_impact_radar.review import render_review_template
from market_impact_radar.scanner import identify_abnormal_moves
from market_impact_radar.validation import validate_file


ROOT = Path(__file__).resolve().parents[1]


class PipelineTest(unittest.TestCase):
    def test_report_pipeline_generates_candidates(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
        )

        self.assertTrue(result.group_signals)
        self.assertTrue(result.events)
        self.assertTrue(result.scored_themes)
        self.assertTrue(result.etf_candidates)
        self.assertTrue(result.stock_candidates)
        self.assertGreater(result.scored_themes[0].score, 50)
        self.assertTrue(any(theme.risk_details for theme in result.scored_themes))

    def test_markdown_report_contains_core_sections(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
        )
        report = render_markdown_report(result, "2026-05-14")

        self.assertIn("跨市场传导日报", report)
        self.assertIn("数据来源与拉取时间", report)
        self.assertIn("昨夜外盘核心异动", report)
        self.assertIn("跨市场冲击事件", report)
        self.assertIn("今日信号分层", report)
        self.assertIn("A股候选 ETF", report)
        self.assertIn("规则命中明细", report)
        self.assertIn("风险提示", report)

    def test_backtest_transmission_stats(self) -> None:
        stats = compute_transmission_stats(
            ROOT / "data" / "sample_transmission_history.csv",
            external_symbol="MU",
            theme="存储芯片",
            threshold=5,
        )

        self.assertEqual(stats["events"], 8)
        self.assertGreater(stats["win_rate"], 0)
        self.assertLessEqual(stats["win_rate"], 1)
        self.assertGreater(stats["avg_open_pct"], 0)
        self.assertIn("avg_high_pct", stats)
        self.assertIn("edge_score", stats)

    def test_batch_transmission_stats(self) -> None:
        stats = compute_batch_transmission_stats(
            ROOT / "data" / "sample_transmission_history.csv",
            thresholds=(3, 5),
            min_events=3,
        )

        self.assertTrue(stats)
        first = stats[0]
        self.assertIn("external_symbol", first)
        self.assertIn("theme", first)
        self.assertIn("edge_score", first)

    def test_build_historical_edges(self) -> None:
        stats = compute_batch_transmission_stats(
            ROOT / "data" / "sample_transmission_history.csv",
            thresholds=(3, 5),
            min_events=3,
        )
        edges = build_historical_edges(stats)

        self.assertIn("historical_edges", edges)
        self.assertIn("存储芯片", edges["historical_edges"])
        self.assertIn("per_external_edges", edges)

    def test_review_template_contains_tables(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
        )
        review = render_review_template(result, "2026-05-14")

        self.assertIn("收盘复盘模板", review)
        self.assertIn("早盘事件复盘", review)
        self.assertIn("规则校准", review)

    def test_schema_validation_accepts_samples(self) -> None:
        validate_file(ROOT / "data" / "sample_external_snapshot.json", "external_snapshot.schema.json")
        validate_file(ROOT / "data" / "sample_a_share_context.json", "a_share_context.schema.json")
        validate_file(ROOT / "data" / "review_result.sample.json", "review_result.schema.json")
        validate_file(ROOT / "data" / "intraday_snapshot.sample.json", "intraday_snapshot.schema.json")

    def test_review_result_summary(self) -> None:
        summary = summarize_review_result(ROOT / "data" / "review_result.sample.json")

        self.assertIn("theme_summary", summary)
        self.assertIn("historical_edges", summary)
        self.assertIn("HBM", summary["historical_edges"])

    def test_pipeline_accepts_scoring_rules(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
            scoring_rules_path=str(ROOT / "data" / "scoring_rules.json"),
        )

        self.assertTrue(result.scored_themes)

    def test_intraday_validation_marks_confirmed_and_failed(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
            scoring_rules_path=str(ROOT / "data" / "scoring_rules.json"),
        )
        evaluation = evaluate_intraday(result, ROOT / "data" / "intraday_snapshot.sample.json")
        statuses = {row["status"] for row in evaluation["evaluations"]}
        report = render_intraday_report(evaluation)

        self.assertIn("confirmed", statuses)
        self.assertIn("failed", statuses)
        self.assertIn("盘中验证报告", report)
        self.assertIn("市场宽度", report)

    def test_intraday_validation_accepts_a_share_snapshot_shape(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
            scoring_rules_path=str(ROOT / "data" / "scoring_rules.json"),
        )

        evaluation = evaluate_intraday(result, ROOT / "data" / "a_share_snapshot.sample.json")

        self.assertEqual(evaluation["market_breadth"]["pressure"], "supportive")
        self.assertIn("AI算力", {row["theme"] for row in evaluation["evaluations"]})

    def test_intraday_validation_does_not_confirm_partial_theme_data(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
            scoring_rules_path=str(ROOT / "data" / "scoring_rules.json"),
        )
        snapshot = {
            "as_of": "2026-05-15T09:45:00+08:00",
            "market_breadth": {
                "source": "sina",
                "data_status": "ok",
                "turnover_billion": 8000,
                "up_count": 3500,
                "down_count": 1200,
                "unchanged_count": 100,
                "stocks_over_5pct_count": 250,
                "sample_size": 4800,
            },
            "themes": {
                "AI算力": {
                    "data_status": "partial",
                    "etf_current_pct": 2.0,
                    "etf_above_vwap": True,
                    "leader_current_pct": 5.0,
                    "leader_fade": False,
                    "stocks_over_5pct_count": 8,
                    "volume_ratio": 2.0,
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_path = Path(tmpdir) / "intraday.json"
            snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            evaluation = evaluate_intraday(result, snapshot_path)
        by_theme = {row["theme"]: row for row in evaluation["evaluations"]}

        self.assertEqual(by_theme["AI算力"]["status"], "missing")
        self.assertIn("数据不完整", by_theme["AI算力"]["action"])

    def test_dashboard_html_contains_core_sections(self) -> None:
        result = run_report_pipeline(
            str(ROOT / "data" / "sample_external_snapshot.json"),
            str(ROOT / "data" / "mappings.json"),
            str(ROOT / "data" / "sample_a_share_context.json"),
            scoring_rules_path=str(ROOT / "data" / "scoring_rules.json"),
        )
        evaluation = evaluate_intraday(result, ROOT / "data" / "intraday_snapshot.sample.json")
        html = render_dashboard_html(result, "2026-05-14", evaluation)

        self.assertIn("跨市场传导雷达", html)
        self.assertIn("规则命中明细", html)
        self.assertIn("盘中验证", html)

    def test_quote_consolidation_marks_divergent_sources(self) -> None:
        config = load_mappings(ROOT / "data" / "mappings.json")
        snapshot = consolidate_quote_records(
            records=[
                QuoteRecord("MU", "yahoo", "2026-05-14T07:30:00+00:00", price=105, prev_close=100, change_pct=5),
                QuoteRecord("MU", "alphavantage", "2026-05-14T07:30:00+00:00", price=108, prev_close=100, change_pct=8),
            ],
            config=config,
            requested_sources=("yahoo", "alphavantage"),
            fetched_at="2026-05-14T07:30:00+00:00",
            max_source_diff_pct=0.5,
            max_age_minutes=0,
        )

        self.assertEqual(snapshot["assets"][0]["data_status"], "divergent")

    def test_scanner_skips_bad_quote_quality(self) -> None:
        asset = ExternalAsset(
            symbol="MU",
            name="美光",
            market="US",
            change_pct=8.2,
            volume_ratio=2.0,
            asset_type="equity",
            group="存储链",
            themes=("存储芯片",),
            data_status="stale",
            quality_warnings=("fetched_at older than max age",),
        )

        self.assertEqual(identify_abnormal_moves((asset,), {}), ())


if __name__ == "__main__":
    unittest.main()
