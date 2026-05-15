from __future__ import annotations

from collections import defaultdict

from .models import ScoredTheme, TransmissionEvent
from .scoring import signal_tier


def generate_events(scored_themes: tuple[ScoredTheme, ...]) -> tuple[TransmissionEvent, ...]:
    grouped: dict[tuple[str, str], list[ScoredTheme]] = defaultdict(list)
    for theme in scored_themes:
        grouped[(theme.group_signal.group, theme.direction)].append(theme)

    events = []
    for index, ((group, direction), themes) in enumerate(grouped.items(), 1):
        ordered = sorted(themes, key=lambda item: item.score, reverse=True)
        best = ordered[0]
        tier = signal_tier(best)
        direction_text = "上涨" if direction == "up" else "下跌"
        theme_names = tuple(theme.theme for theme in ordered[:6])
        trigger_assets = tuple(
            f"{move.asset.name}{move.asset.change_pct:+.1f}%"
            for move in best.group_signal.assets[:6]
        )
        reason_parts = list(best.group_signal.reason_summaries[:2])
        if not reason_parts and best.reasons:
            reason_parts.append(best.reasons[0])

        events.append(
            TransmissionEvent(
                event_id=f"EVT-{index:03d}",
                title=f"{group}{direction_text}冲击",
                direction=direction,
                group=group,
                trigger_assets=trigger_assets,
                themes=theme_names,
                score=round(best.score, 2),
                tier=tier,
                reason="；".join(reason_parts) if reason_parts else "外盘价格和成交量触发异常",
                action=_action_for_tier(tier, direction),
                risks=tuple(dict.fromkeys(risk for theme in ordered for risk in theme.risks)),
                confirmations=_confirmations_for_event(theme_names, direction),
                failure_signals=_failure_signals_for_event(theme_names, direction),
            )
        )

    return tuple(sorted(events, key=lambda item: item.score, reverse=True))


def _action_for_tier(tier: str, direction: str) -> str:
    if direction == "down":
        return "偏风险事件，优先观察相关A股是否补跌，避免逆势接力"
    if tier == "strong":
        return "重点观察，竞价不过热时等待开盘回踩确认"
    if tier == "watch":
        return "加入候选，等待板块扩散和龙头确认"
    if tier == "weak":
        return "只做跟踪，不作为优先交易方向"
    return "风险折扣较高，不追高，优先防兑现"


def _confirmations_for_event(themes: tuple[str, ...], direction: str) -> tuple[str, ...]:
    theme_text = "、".join(themes[:3]) or "相关主题"
    if direction == "down":
        return (
            f"{theme_text}相关ETF低开后无法快速修复",
            "核心个股开盘15分钟弱于大盘",
            "板块内下跌扩散而非单一个股波动",
        )
    return (
        f"{theme_text}相关ETF高开不极端且站上分时均线",
        "核心龙头不快速跳水，后排有跟涨扩散",
        "板块至少5只个股涨幅超过5%或成交额明显放大",
    )


def _failure_signals_for_event(themes: tuple[str, ...], direction: str) -> tuple[str, ...]:
    theme_text = "、".join(themes[:3]) or "相关主题"
    if direction == "down":
        return (
            f"{theme_text}低开后快速修复并强于指数",
            "外盘利空没有引发A股板块扩散下跌",
        )
    return (
        f"{theme_text}竞价无反应或开盘15分钟缩量回落",
        "龙头高开低走，ETF放量下杀",
        "只有一两只个股上涨，板块没有扩散",
    )
