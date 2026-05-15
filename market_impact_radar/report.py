from __future__ import annotations

from datetime import date

from .models import Candidate, RadarResult, ScoredTheme
from .scoring import signal_tier


def render_markdown_report(result: RadarResult, report_date: str | None = None) -> str:
    report_date = report_date or date.today().isoformat()
    lines: list[str] = [
        f"# 跨市场传导日报 {report_date}",
        "",
        f"数据时间：{result.as_of or '未提供'}",
        "",
    ]

    lines.extend(_render_external_moves(result))
    lines.extend(_render_events(result))
    lines.extend(_render_signal_tiers(result.scored_themes))
    lines.extend(_render_candidates("四、A股候选 ETF", result.etf_candidates))
    lines.extend(_render_candidates("五、A股候选个股", result.stock_candidates))
    lines.extend(_render_risk_details(result.scored_themes))
    lines.extend(_render_risks(result.scored_themes))
    lines.extend(_render_intraday_playbook(result.scored_themes))
    lines.extend(_render_context(result))
    return "\n".join(lines).rstrip() + "\n"


def _render_external_moves(result: RadarResult) -> list[str]:
    lines = ["## 一、昨夜外盘核心异动", ""]
    if not result.group_signals:
        return lines + ["未识别到满足阈值的外盘共振信号。", ""]

    for index, signal in enumerate(result.group_signals[:8], 1):
        direction = "上涨" if signal.direction == "up" else "下跌"
        asset_text = "、".join(
            f"{move.asset.name} {move.asset.change_pct:+.1f}% / {move.asset.volume_ratio:.1f}x"
            for move in signal.assets[:5]
        )
        lines.append(
            f"{index}. {signal.group}{direction}共振：{asset_text}；"
            f"共振分 {signal.resonance_score:.0f}"
        )
    lines.append("")
    return lines


def _render_events(result: RadarResult) -> list[str]:
    lines = ["## 二、跨市场冲击事件", ""]
    if not result.events:
        return lines + ["暂无可结构化的冲击事件。", ""]

    lines.extend(
        [
            "| 事件 | 等级 | 分数 | 触发资产 | A股映射 | 操作含义 |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    tier_names = {"strong": "强", "watch": "观察", "weak": "弱", "risk": "风险"}
    for event in result.events[:8]:
        lines.append(
            f"| {event.title} | {tier_names.get(event.tier, event.tier)} | {event.score:.0f} | "
            f"{'、'.join(event.trigger_assets)} | {'、'.join(event.themes)} | {event.action} |"
        )
    lines.append("")
    return lines


def _render_signal_tiers(scored_themes: tuple[ScoredTheme, ...]) -> list[str]:
    lines = ["## 三、今日信号分层", ""]
    if not scored_themes:
        return lines + ["暂无可映射到 A 股的主题。", ""]

    tiers = {
        "strong": ("强信号", "重点观察，但仍需竞价和开盘确认"),
        "watch": ("可观察", "信号较好，适合等待回踩或板块扩散"),
        "weak": ("弱观察", "只做跟踪，不作为优先方向"),
        "risk": ("风险/不追", "信号被风险折扣压制，优先防兑现"),
    }
    bucketed = {key: [] for key in tiers}
    for theme in scored_themes:
        bucketed[signal_tier(theme)].append(theme)

    for key, (title, hint) in tiers.items():
        themes = bucketed[key]
        lines.append(f"### {title}")
        lines.append("")
        lines.append(hint)
        lines.append("")
        if not themes:
            lines.append("无。")
            lines.append("")
            continue
        lines.extend(
            [
                "| 排名 | 方向 | 信号 | 分数 | 风险折扣 | 核心理由 |",
                "| --- | --- | --- | ---: | ---: | --- |",
            ]
        )
        for index, theme in enumerate(themes[:8], 1):
            direction = "受益" if theme.direction == "up" else "承压"
            reason = theme.reasons[0] if theme.reasons else ""
            lines.append(
                f"| {index} | {theme.theme} | {direction} | {theme.score:.0f} | "
                f"{theme.risk_discount:.0f} | {reason} |"
            )
        lines.append("")
    return lines


def _render_candidates(title: str, candidates: tuple[Candidate, ...]) -> list[str]:
    lines = [f"## {title}", ""]
    if not candidates:
        return lines + ["暂无候选。", ""]

    risk_header = "风险" if candidates[0].kind == "stock" else "备注"
    lines.extend(
        [
            f"| 排名 | 名称 | 主题 | 分数 | {risk_header} | 映射逻辑 |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for index, candidate in enumerate(candidates, 1):
        lines.append(
            f"| {index} | {candidate.name} | {candidate.theme} | "
            f"{candidate.score:.0f} | {candidate.risk} | {candidate.rationale} |"
        )
    lines.append("")
    return lines


def _render_risk_details(scored_themes: tuple[ScoredTheme, ...]) -> list[str]:
    lines = ["## 六、规则命中明细", ""]
    themes = [theme for theme in scored_themes if theme.risk_details]
    if not themes:
        return lines + ["暂无风险规则命中。", ""]

    for theme in themes[:8]:
        lines.append(f"### {theme.theme}：风险折扣 {theme.risk_discount:.0f}")
        lines.append("")
        lines.extend(["| 字段 | 数值 | 扣分 | 说明 |", "| --- | ---: | ---: | --- |"])
        for detail in theme.risk_details:
            value = detail.get("value", "")
            lines.append(
                f"| {detail.get('field', '')} | {value} | "
                f"{float(detail.get('penalty', 0)):+.0f} | {detail.get('message', '')} |"
            )
        lines.append("")
    return lines


def _render_risks(scored_themes: tuple[ScoredTheme, ...]) -> list[str]:
    lines = ["## 七、风险提示", ""]
    risks = []
    for theme in scored_themes[:10]:
        risks.extend(theme.risks)
    if not risks:
        risks.append("未发现明显提前反应或高开拥挤风险，但仍需等待竞价确认。")
    for risk in dict.fromkeys(risks):
        lines.append(f"- {risk}")
    lines.append("- 若相关 ETF 或核心个股高开超过 5%，优先等待 5-15 分钟回踩确认。")
    lines.append("- 若只有单一个股上涨、板块不扩散，应降低传导信号权重。")
    lines.append("")
    return lines


def _render_intraday_playbook(scored_themes: tuple[ScoredTheme, ...]) -> list[str]:
    lines = [
        "## 八、盘中验证条件",
        "",
        "| 情况 | 操作建议 |",
        "| --- | --- |",
        "| 高开 0%-2% | 可观察低吸，等待 ETF 和龙头同步确认 |",
        "| 高开 2%-5% | 等回踩分时均线，避免竞价后直接追 |",
        "| 高开 >5% | 不建议追高，防止利好兑现 |",
        "| 龙头高开低走 | ETF 与后排同步谨慎 |",
        "| 板块至少 5 只个股涨幅超过 5% | 说明传导扩散，信号可信度上升 |",
        "| ETF 放量下杀且龙头不回封 | 视为传导失败，放弃追击 |",
        "",
    ]
    if scored_themes:
        top = scored_themes[0]
        lines.extend(
            [
                f"优先验证：{top.theme}",
                "",
                "- 相关 ETF 高开不极端，且 9:35 前不跌破分时均线。",
                f"- {top.theme} 龙头不快速跳水，后排有扩散。",
                "- 若竞价无反应或开盘 15 分钟内缩量回落，降低信号等级。",
                "",
            ]
        )
    return lines


def _render_context(result: RadarResult) -> list[str]:
    market = result.context.get("market_environment", {})
    if not market:
        return []
    lines = ["## 九、市场环境", ""]
    summary = market.get("summary")
    if summary:
        lines.append(str(summary))
    lines.append(f"环境分：{float(market.get('score', 70)):.0f}")
    turnover = market.get("turnover_billion")
    if turnover is not None:
        lines.append(f"A股成交额：{float(turnover):.0f} 亿")
    trend = market.get("index_trend")
    if trend:
        lines.append(f"指数趋势：{trend}")
    lines.append("")
    return lines
