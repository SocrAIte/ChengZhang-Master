from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backtest import (
    compute_batch_transmission_stats,
    compute_transmission_stats,
    render_batch_stats_markdown,
    write_batch_stats_csv,
    write_historical_edges_json,
)
from .a_share_sources import fetch_a_share_snapshot
from .dashboard import render_dashboard_html
from .intraday import evaluate_intraday, render_intraday_report
from .io import load_json, load_mappings, write_text
from .knowledge_crawler import crawl_and_enrich
from .pipeline import run_report_pipeline
from .quote_sources import fetch_external_snapshot
from .report import render_markdown_report
from .review import render_review_template
from .review_feedback import summarize_review_result, write_review_edges, write_review_summary
from .validation import validate_file


DEFAULT_MAPPING = "data/mappings.json"
DEFAULT_RULES = "data/theme_rules.json"
DEFAULT_SCORING_RULES = "data/scoring_rules.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="跨市场传导雷达")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch-external", help="从真实外盘行情源生成外盘快照")
    fetch_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="映射配置 JSON，用来补全名称、市场、主题和分组")
    fetch_parser.add_argument("--symbols", help="逗号分隔代码；不填则抓取 mappings 里的全部外盘资产")
    fetch_parser.add_argument("--sources", default="yahoo", help="逗号分隔行情源：yahoo,alphavantage,polygon")
    fetch_parser.add_argument("--output", required=True, help="输出 external snapshot JSON")
    fetch_parser.add_argument("--max-source-diff-pct", type=float, default=0.5, help="多源涨跌幅最大允许差异，单位百分点")
    fetch_parser.add_argument("--max-age-minutes", type=int, default=180, help="行情快照最大可接受年龄；超过后报告降级")
    fetch_parser.add_argument("--alpha-vantage-key", help="Alpha Vantage API key；也可用 ALPHAVANTAGE_API_KEY")
    fetch_parser.add_argument("--polygon-key", help="Polygon API key；也可用 POLYGON_API_KEY")
    fetch_parser.add_argument("--proxy", help="HTTP/HTTPS 代理，例如 http://127.0.0.1:10793")

    a_share_parser = subparsers.add_parser("fetch-a-share", help="从A股行情源生成竞价/盘中验证快照")
    a_share_parser.add_argument("--watchlist", required=True, help="A股主题 ETF/龙头/成分股观察池 JSON")
    a_share_parser.add_argument("--source", default="eastmoney", choices=["eastmoney"], help="A股行情源")
    a_share_parser.add_argument("--output", required=True, help="输出 A股盘中快照 JSON")
    a_share_parser.add_argument("--proxy", help="HTTP/HTTPS 代理，例如 http://127.0.0.1:10793")

    report_parser = subparsers.add_parser("report", help="生成开盘前传导日报")
    report_parser.add_argument("--external", required=True, help="外盘快照 JSON")
    report_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="映射配置 JSON")
    report_parser.add_argument("--context", help="A股环境与风险上下文 JSON")
    report_parser.add_argument("--historical-edges", help="批量回测生成的 historical_edges JSON")
    report_parser.add_argument("--scoring-rules", default=DEFAULT_SCORING_RULES, help="评分规则 JSON")
    report_parser.add_argument("--no-validate", action="store_true", help="跳过输入 JSON schema 校验")
    report_parser.add_argument("--output", help="输出 Markdown 文件")
    report_parser.add_argument("--date", help="报告日期，默认使用本机日期")

    intraday_parser = subparsers.add_parser("intraday-validate", help="用盘中快照验证早盘传导信号")
    intraday_parser.add_argument("--external", required=True, help="外盘快照 JSON")
    intraday_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="映射配置 JSON")
    intraday_parser.add_argument("--context", help="A股环境与风险上下文 JSON")
    intraday_parser.add_argument("--historical-edges", help="批量回测生成的 historical_edges JSON")
    intraday_parser.add_argument("--scoring-rules", default=DEFAULT_SCORING_RULES, help="评分规则 JSON")
    intraday_parser.add_argument("--intraday", required=True, help="盘中验证快照 JSON")
    intraday_parser.add_argument("--no-validate", action="store_true", help="跳过输入 JSON schema 校验")
    intraday_parser.add_argument("--output", help="输出 Markdown 文件；不填则打印到终端")

    dashboard_parser = subparsers.add_parser("dashboard", help="生成静态 HTML 看板")
    dashboard_parser.add_argument("--external", required=True, help="外盘快照 JSON")
    dashboard_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="映射配置 JSON")
    dashboard_parser.add_argument("--context", help="A股环境与风险上下文 JSON")
    dashboard_parser.add_argument("--historical-edges", help="批量回测生成的 historical_edges JSON")
    dashboard_parser.add_argument("--scoring-rules", default=DEFAULT_SCORING_RULES, help="评分规则 JSON")
    dashboard_parser.add_argument("--intraday", help="可选：盘中验证快照 JSON")
    dashboard_parser.add_argument("--no-validate", action="store_true", help="跳过输入 JSON schema 校验")
    dashboard_parser.add_argument("--output", required=True, help="输出 HTML 文件")
    dashboard_parser.add_argument("--date", help="看板日期，默认使用本机日期")

    backtest_parser = subparsers.add_parser("backtest", help="计算单个隔夜传导统计")
    backtest_parser.add_argument("--history", required=True, help="历史 CSV")
    backtest_parser.add_argument("--external-symbol", help="外盘代码，例如 MU")
    backtest_parser.add_argument("--theme", help="A股主题，例如 存储芯片")
    backtest_parser.add_argument("--threshold", type=float, default=5.0, help="外盘触发阈值")
    backtest_parser.add_argument("--direction", choices=["up", "down"], default="up")

    batch_parser = subparsers.add_parser("backtest-batch", help="批量计算外盘到A股主题传导统计")
    batch_parser.add_argument("--history", required=True, help="历史 CSV")
    batch_parser.add_argument("--thresholds", default="3,5,8", help="逗号分隔阈值，例如 3,5,8")
    batch_parser.add_argument("--direction", choices=["up", "down"], default="up")
    batch_parser.add_argument("--min-events", type=int, default=3, help="最少样本数")
    batch_parser.add_argument("--output", help="输出文件，支持 .md 或 .csv；不填则打印 JSON")
    batch_parser.add_argument("--edges-output", help="额外输出 historical_edges JSON，供日报评分读取")

    review_parser = subparsers.add_parser("review-template", help="生成收盘复盘模板")
    review_parser.add_argument("--external", required=True, help="外盘快照 JSON")
    review_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="映射配置 JSON")
    review_parser.add_argument("--context", help="A股环境与风险上下文 JSON")
    review_parser.add_argument("--historical-edges", help="批量回测生成的 historical_edges JSON")
    review_parser.add_argument("--scoring-rules", default=DEFAULT_SCORING_RULES, help="评分规则 JSON")
    review_parser.add_argument("--no-validate", action="store_true", help="跳过输入 JSON schema 校验")
    review_parser.add_argument("--output", required=True, help="输出 Markdown 文件")
    review_parser.add_argument("--date", help="复盘日期，默认使用本机日期")

    review_summary_parser = subparsers.add_parser("review-summarize", help="汇总收盘复盘结果并生成反馈")
    review_summary_parser.add_argument("--review", required=True, help="收盘复盘结果 JSON")
    review_summary_parser.add_argument("--output", required=True, help="输出汇总文件，支持 .md 或 .json")
    review_summary_parser.add_argument("--edges-output", help="额外输出 historical_edges JSON")
    review_summary_parser.add_argument("--no-validate", action="store_true", help="跳过输入 JSON schema 校验")

    validate_parser = subparsers.add_parser("validate-json", help="校验输入 JSON 是否符合 schema")
    validate_parser.add_argument("--file", required=True, help="待校验 JSON 文件")
    validate_parser.add_argument(
        "--schema",
        required=True,
        choices=[
            "external_snapshot.schema.json",
            "a_share_context.schema.json",
            "historical_edges.schema.json",
            "review_result.schema.json",
            "scoring_rules.schema.json",
            "intraday_snapshot.schema.json",
            "a_share_snapshot.schema.json",
        ],
        help="schema 文件名",
    )

    crawl_parser = subparsers.add_parser("crawl-knowledge", help="爬取公开市场列表并扩容知识图谱")
    crawl_parser.add_argument("--mapping", default=DEFAULT_MAPPING, help="原始映射配置 JSON")
    crawl_parser.add_argument("--rules", default=DEFAULT_RULES, help="主题关键词规则 JSON")
    crawl_parser.add_argument("--generated-dir", default="data/generated", help="爬取结果输出目录")
    crawl_parser.add_argument("--output", default="data/mappings.enriched.json", help="扩容后的映射 JSON")
    crawl_parser.add_argument("--timeout", type=int, default=20, help="单个请求超时时间")
    crawl_parser.add_argument("--sleep", type=float, default=0.2, help="板块明细请求间隔秒数")
    crawl_parser.add_argument("--max-board-constituents", type=int, default=80, help="最多拉取多少个东方财富板块成分")
    crawl_parser.add_argument("--max-stocks-per-theme", type=int, default=80, help="每个主题最多合入多少只A股")
    crawl_parser.add_argument("--skip-eastmoney", action="store_true", help="跳过东方财富源，只抓交易所/美股/台股基础列表")
    crawl_parser.add_argument("--proxy", help="HTTP/HTTPS 代理，例如 http://127.0.0.1:10793")
    crawl_parser.add_argument(
        "--proxy-mode",
        choices=["foreign", "all"],
        default="foreign",
        help="代理模式：foreign=国内源直连、海外源走代理；all=全部走代理",
    )

    args = parser.parse_args()
    if args.command == "fetch-external":
        config = load_mappings(args.mapping)
        symbols = _symbols_from_fetch_args(args, config)
        snapshot = fetch_external_snapshot(
            symbols=symbols,
            config=config,
            sources=tuple(item.strip() for item in args.sources.split(",") if item.strip()),
            max_source_diff_pct=args.max_source_diff_pct,
            max_age_minutes=args.max_age_minutes,
            alpha_vantage_key=args.alpha_vantage_key,
            polygon_key=args.polygon_key,
            proxy=args.proxy,
        )
        write_text(args.output, json.dumps(snapshot, ensure_ascii=False, indent=2))
        print(f"External snapshot written to {Path(args.output)}")
        return 0

    if args.command == "fetch-a-share":
        watchlist = load_json(args.watchlist)
        snapshot = fetch_a_share_snapshot(watchlist=watchlist, source=args.source, proxy=args.proxy)
        write_text(args.output, json.dumps(snapshot, ensure_ascii=False, indent=2))
        print(f"A-share snapshot written to {Path(args.output)}")
        return 0

    if args.command == "report":
        _validate_report_inputs(args)
        result = run_report_pipeline(
            args.external,
            args.mapping,
            args.context,
            args.historical_edges,
            args.scoring_rules,
        )
        report = render_markdown_report(result, args.date)
        if args.output:
            write_text(args.output, report)
            print(f"Report written to {Path(args.output)}")
        else:
            print(report)
        return 0

    if args.command == "intraday-validate":
        _validate_report_inputs(args)
        result = _run_pipeline_from_args(args)
        evaluation = evaluate_intraday(result, args.intraday)
        report = render_intraday_report(evaluation)
        if args.output:
            write_text(args.output, report)
            print(f"Intraday validation written to {Path(args.output)}")
        else:
            print(report)
        return 0

    if args.command == "dashboard":
        _validate_report_inputs(args)
        result = _run_pipeline_from_args(args)
        intraday_evaluation = evaluate_intraday(result, args.intraday) if args.intraday else None
        html = render_dashboard_html(result, args.date, intraday_evaluation)
        write_text(args.output, html)
        print(f"Dashboard written to {Path(args.output)}")
        return 0

    if args.command == "backtest":
        stats = compute_transmission_stats(
            args.history,
            external_symbol=args.external_symbol,
            theme=args.theme,
            threshold=args.threshold,
            direction=args.direction,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    if args.command == "backtest-batch":
        thresholds = tuple(float(item.strip()) for item in args.thresholds.split(",") if item.strip())
        stats = compute_batch_transmission_stats(
            args.history,
            thresholds=thresholds,
            direction=args.direction,
            min_events=args.min_events,
        )
        if args.output:
            output = Path(args.output)
            if output.suffix.lower() == ".csv":
                write_batch_stats_csv(output, stats)
            else:
                write_text(output, render_batch_stats_markdown(stats))
            print(f"Batch backtest written to {output}")
        else:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        if args.edges_output:
            write_historical_edges_json(args.edges_output, stats)
            print(f"Historical edges written to {Path(args.edges_output)}")
        return 0

    if args.command == "review-template":
        _validate_report_inputs(args)
        result = run_report_pipeline(
            args.external,
            args.mapping,
            args.context,
            args.historical_edges,
            args.scoring_rules,
        )
        write_text(args.output, render_review_template(result, args.date))
        print(f"Review template written to {Path(args.output)}")
        return 0

    if args.command == "review-summarize":
        if not args.no_validate:
            validate_file(args.review, "review_result.schema.json")
        summary = summarize_review_result(args.review)
        write_review_summary(args.output, summary)
        print(f"Review summary written to {Path(args.output)}")
        if args.edges_output:
            write_review_edges(args.edges_output, summary)
            print(f"Review edges written to {Path(args.edges_output)}")
        return 0

    if args.command == "validate-json":
        validate_file(args.file, args.schema)
        print(f"{args.file} passed {args.schema}")
        return 0

    if args.command == "crawl-knowledge":
        result = crawl_and_enrich(
            mapping_path=args.mapping,
            rules_path=args.rules,
            generated_dir=args.generated_dir,
            enriched_mapping_path=args.output,
            timeout=args.timeout,
            sleep_seconds=args.sleep,
            max_board_constituents=args.max_board_constituents,
            max_stocks_per_theme=args.max_stocks_per_theme,
            use_eastmoney=not args.skip_eastmoney,
            proxy=args.proxy,
            proxy_mode=args.proxy_mode,
        )
        print(json.dumps({"counts": result.counts, "errors": result.errors}, ensure_ascii=False, indent=2))
        print(f"Generated data: {result.generated_dir}")
        if result.enriched_mapping_path:
            print(f"Enriched mapping: {result.enriched_mapping_path}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _validate_report_inputs(args: argparse.Namespace) -> None:
    if args.no_validate:
        return
    validate_file(args.external, "external_snapshot.schema.json")
    if args.context:
        validate_file(args.context, "a_share_context.schema.json")
    if args.historical_edges:
        validate_file(args.historical_edges, "historical_edges.schema.json")
    if args.scoring_rules:
        validate_file(args.scoring_rules, "scoring_rules.schema.json")
    if getattr(args, "intraday", None):
        validate_file(args.intraday, "intraday_snapshot.schema.json")


def _run_pipeline_from_args(args: argparse.Namespace):
    return run_report_pipeline(
        args.external,
        args.mapping,
        args.context,
        args.historical_edges,
        args.scoring_rules,
    )


def _symbols_from_fetch_args(args: argparse.Namespace, config: dict) -> tuple[str, ...]:
    if args.symbols:
        return tuple(item.strip().upper() for item in args.symbols.split(",") if item.strip())
    return tuple(str(item["symbol"]).upper() for item in config.get("external_assets", []))


if __name__ == "__main__":
    raise SystemExit(main())
