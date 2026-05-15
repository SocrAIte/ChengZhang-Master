from __future__ import annotations

from datetime import date

from .models import Candidate, RadarResult, ScoredTheme, TransmissionEvent
from .scoring import signal_tier


TIER_NAMES = {
    "strong": "强信号",
    "watch": "可观察",
    "weak": "弱观察",
    "risk": "风险/不追",
}


def render_review_template(result: RadarResult, report_date: str | None = None) -> str:
    report_date = report_date or date.today().isoformat()
    lines = [
        f"# 收盘复盘模板 {report_date}",
        "",
        "## 一、早盘事件复盘",
        "",
    ]
    lines.extend(_render_event_review(result.events))
    lines.extend(_render_theme_review(result.scored_themes))
    lines.extend(_render_candidate_review("三、ETF候选复盘", result.etf_candidates))
    lines.extend(_render_candidate_review("四、个股候选复盘", result.stock_candidates))
    lines.extend(_render_lessons())
    return "\n".join(lines).rstrip() + "\n"


def _render_event_review(events: tuple[TransmissionEvent, ...]) -> list[str]:
    if not events:
        return ["暂无事件。", ""]
    lines = [
        "| 事件 | 早盘等级 | 早盘分数 | 映射主题 | 收盘结论 | 是否确认 | 备注 |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for event in events[:10]:
        lines.append(
            f"| {event.title} | {TIER_NAMES.get(event.tier, event.tier)} | {event.score:.0f} | "
            f"{'、'.join(event.themes)} |  |  |  |"
        )
    lines.append("")
    return lines


def _render_theme_review(scored_themes: tuple[ScoredTheme, ...]) -> list[str]:
    lines = [
        "## 二、主题表现复盘",
        "",
        "| 主题 | 早盘层级 | 早盘分数 | 开盘涨幅 | 最高涨幅 | 收盘涨幅 | 最大回撤 | 高开低走 | 复盘结论 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for theme in scored_themes[:12]:
        tier = signal_tier(theme)
        lines.append(
            f"| {theme.theme} | {TIER_NAMES.get(tier, tier)} | {theme.score:.0f} |  |  |  |  |  |  |"
        )
    lines.append("")
    return lines


def _render_candidate_review(title: str, candidates: tuple[Candidate, ...]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| 候选 | 主题 | 早盘分数 | 开盘 | 最高 | 收盘 | 是否跑赢主题 | 是否适合开盘买 | 备注 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for candidate in candidates[:12]:
        lines.append(
            f"| {candidate.name} | {candidate.theme} | {candidate.score:.0f} |  |  |  |  |  |  |"
        )
    lines.append("")
    return lines


def _render_lessons() -> list[str]:
    return [
        "## 五、规则校准",
        "",
        "| 问题 | 今日观察 | 是否需要改规则 | 调整建议 |",
        "| --- | --- | --- | --- |",
        "| 外盘强但A股不跟 |  |  |  |",
        "| A股提前反应后兑现 |  |  |  |",
        "| 高开追涨是否亏损 |  |  |  |",
        "| ETF与个股谁更有效 |  |  |  |",
        "| 哪个映射关系需要降权 |  |  |  |",
        "",
    ]
