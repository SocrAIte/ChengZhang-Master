from __future__ import annotations

import html
from datetime import date

from .intraday import summarize_intraday_evaluation
from .models import RadarResult, ScoredTheme
from .scoring import signal_tier


def render_dashboard_html(
    result: RadarResult,
    report_date: str | None = None,
    intraday_evaluation: dict | None = None,
    knowledge_verification: dict | None = None,
) -> str:
    report_date = report_date or date.today().isoformat()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>跨市场传导雷达 {html.escape(report_date)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #667085;
      --line: #d8dde6;
      --strong: #0f7b5f;
      --watch: #1d5fd1;
      --weak: #8a5a00;
      --risk: #b42318;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 14px/1.55 "Segoe UI", Arial, sans-serif; }}
    header {{ padding: 22px 28px; background: #101828; color: white; }}
    header h1 {{ margin: 0; font-size: 22px; letter-spacing: 0; }}
    header p {{ margin: 6px 0 0; color: #cbd5e1; }}
    main {{ padding: 22px 28px 36px; max-width: 1440px; margin: 0 auto; }}
    section {{ margin-bottom: 22px; }}
    h2 {{ font-size: 17px; margin: 0 0 12px; }}
    .grid {{ display: grid; gap: 12px; }}
    .events {{ grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
    .tiers {{ grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); }}
    .card h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .meta {{ color: var(--muted); font-size: 12px; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .strong {{ color: var(--strong); background: #e8f6f0; }}
    .watch {{ color: var(--watch); background: #eaf1ff; }}
    .weak {{ color: var(--weak); background: #fff4d6; }}
    .risk {{ color: var(--risk); background: #fee4e2; }}
    .bad {{ color: var(--risk); font-weight: 700; }}
    .alert {{ border-left: 5px solid var(--line); }}
    .alert-high {{ border-left-color: var(--risk); background: #fff7f6; }}
    .alert-medium {{ border-left-color: var(--weak); background: #fffbeb; }}
    .alert-low {{ border-left-color: var(--strong); background: #f0fdf4; }}
    .status-failed, .status-missing {{ color: var(--risk); font-weight: 700; }}
    .status-downgraded {{ color: var(--weak); font-weight: 700; }}
    .status-confirmed {{ color: var(--strong); font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; font-size: 12px; color: #344054; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; white-space: nowrap; }}
    ul {{ margin: 8px 0 0 18px; padding: 0; }}
  </style>
</head>
<body>
  <header>
    <h1>跨市场传导雷达</h1>
    <p>{html.escape(report_date)} · 数据时间 {html.escape(result.as_of or "未提供")}</p>
  </header>
  <main>
    {_intraday_alert_section(intraday_evaluation)}
    {_source_quality_section(result)}
    {_events_section(result)}
    {_tiers_section(result.scored_themes)}
    {_risk_section(result.scored_themes)}
    {_knowledge_verification_section(knowledge_verification)}
    {_candidates_section("候选 ETF", result.etf_candidates)}
    {_candidates_section("候选个股", result.stock_candidates)}
    {_intraday_section(intraday_evaluation)}
  </main>
</body>
</html>
"""


def _source_quality_section(result: RadarResult) -> str:
    quality = result.context.get("external_data_quality", {})
    if not quality:
        return ""
    rows = []
    for asset in result.external_assets[:24]:
        status = html.escape(asset.data_status)
        if asset.data_status != "ok":
            status = f"<span class='bad'>{status}</span>"
        rows.append(
            f"<tr><td>{html.escape(asset.symbol)}</td><td>{html.escape(asset.name)}</td>"
            f"<td>{html.escape(asset.source or '-')}</td><td>{html.escape(asset.fetched_at or '-')}</td>"
            f"<td class='num'>{_fmt(asset.price)}</td><td class='num'>{_fmt(asset.prev_close)}</td>"
            f"<td class='num'>{asset.change_pct:+.2f}%</td><td>{status}</td></tr>"
        )
    warning = ""
    if quality.get("issues"):
        warning = "<p class='bad'>存在过期、缺失或多源分歧记录；异常资产不会参与强信号生成。</p>"
    return f"""<section>
  <h2>数据来源与拉取时间</h2>
  <div class="card">
    <div class="meta">来源：{html.escape('、'.join(quality.get('sources', [])) or '未提供')} · 拉取时间：{html.escape(quality.get('fetched_at_min') or '未提供')} ~ {html.escape(quality.get('fetched_at_max') or '未提供')}</div>
    {warning}
  </div>
  <table><thead><tr><th>代码</th><th>名称</th><th>来源</th><th>拉取时间</th><th class="num">价格</th><th class="num">前收</th><th class="num">涨跌幅</th><th>状态</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</section>"""


def _events_section(result: RadarResult) -> str:
    cards = []
    for event in result.events[:8]:
        cards.append(
            f"""<article class="card">
  <h3>{html.escape(event.title)} <span class="pill {event.tier}">{_tier_name(event.tier)}</span></h3>
  <div class="meta">分数 {event.score:.0f} · {'、'.join(html.escape(item) for item in event.trigger_assets)}</div>
  <p>{html.escape(event.action)}</p>
  <div class="meta">映射：{'、'.join(html.escape(item) for item in event.themes)}</div>
</article>"""
        )
    return f"""<section>
  <h2>冲击事件</h2>
  <div class="grid events">{''.join(cards) or '<div class="card">暂无事件</div>'}</div>
</section>"""


def _tiers_section(themes: tuple[ScoredTheme, ...]) -> str:
    groups = {"strong": [], "watch": [], "weak": [], "risk": []}
    for theme in themes:
        groups[signal_tier(theme)].append(theme)
    cards = []
    for tier, title in (("strong", "强信号"), ("watch", "可观察"), ("weak", "弱观察"), ("risk", "风险/不追")):
        rows = "".join(
            f"<tr><td>{html.escape(item.theme)}</td><td class='num'>{item.score:.0f}</td><td class='num'>{item.risk_discount:.0f}</td></tr>"
            for item in groups[tier][:8]
        )
        cards.append(
            f"""<article class="card">
  <h3><span class="pill {tier}">{title}</span></h3>
  <table><thead><tr><th>主题</th><th class="num">分数</th><th class="num">风险</th></tr></thead><tbody>{rows or '<tr><td colspan="3">无</td></tr>'}</tbody></table>
</article>"""
        )
    return f"""<section>
  <h2>信号分层</h2>
  <div class="grid tiers">{''.join(cards)}</div>
</section>"""


def _risk_section(themes: tuple[ScoredTheme, ...]) -> str:
    rows = []
    for theme in themes:
        for detail in theme.risk_details[:6]:
            rows.append(
                f"<tr><td>{html.escape(theme.theme)}</td><td>{html.escape(str(detail.get('field', '')))}</td>"
                f"<td class='num'>{html.escape(str(detail.get('value', '')))}</td>"
                f"<td class='num'>{float(detail.get('penalty', 0)):+.0f}</td>"
                f"<td>{html.escape(str(detail.get('message', '')))}</td></tr>"
            )
    return f"""<section>
  <h2>规则命中明细</h2>
  <table><thead><tr><th>主题</th><th>字段</th><th class="num">数值</th><th class="num">扣分</th><th>说明</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="5">暂无风险规则命中</td></tr>'}</tbody></table>
</section>"""


def _candidates_section(title: str, candidates: tuple) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(item.name)}</td><td>{html.escape(item.theme)}</td><td class='num'>{item.score:.0f}</td><td>{html.escape(item.risk)}</td><td>{html.escape(item.rationale)}</td></tr>"
        for item in candidates[:12]
    )
    return f"""<section>
  <h2>{html.escape(title)}</h2>
  <table><thead><tr><th>名称</th><th>主题</th><th class="num">分数</th><th>风险</th><th>逻辑</th></tr></thead><tbody>{rows or '<tr><td colspan="5">暂无候选</td></tr>'}</tbody></table>
</section>"""


def _intraday_section(evaluation: dict | None) -> str:
    if not evaluation:
        return ""
    rows = "".join(
        f"<tr><td>{html.escape(row['theme'])}</td><td class='status-{html.escape(row['status'])}'>{html.escape(row['status'])}</td><td>{html.escape(row['action'])}</td><td>{html.escape('；'.join(row['reasons']))}</td></tr>"
        for row in evaluation.get("evaluations", [])
    )
    return f"""<section>
  <h2>盘中验证</h2>
  <table><thead><tr><th>主题</th><th>状态</th><th>操作</th><th>理由</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""


def _intraday_alert_section(evaluation: dict | None) -> str:
    if not evaluation:
        return ""
    summary = summarize_intraday_evaluation(evaluation)
    severity = html.escape(summary["severity"])
    risk_themes = "、".join(html.escape(item) for item in summary["risk_themes"]) or "暂无"
    confirmed = "、".join(html.escape(item) for item in summary["confirmed_themes"]) or "暂无"
    return f"""<section>
  <h2>盘中风险总览</h2>
  <div class="card alert alert-{severity}">
    <h3>{html.escape(summary['headline'])}</h3>
    <p>市场宽度：{html.escape(str(summary['market_pressure']))}</p>
    <p><strong>重点风险：</strong>{risk_themes}</p>
    <p><strong>已确认：</strong>{confirmed}</p>
  </div>
</section>"""


def _knowledge_verification_section(report: dict | None) -> str:
    if not report:
        return ""
    counts = report.get("quality_counts", {})
    source = report.get("source_summary", {})
    issues = report.get("issues", [])
    rows = "".join(
        f"<tr><td>{html.escape(str(item.get('severity', '')))}</td>"
        f"<td>{html.escape(str(item.get('kind', '')))}</td>"
        f"<td>{html.escape(str(item.get('target', '')))}</td>"
        f"<td>{html.escape(str(item.get('message', '')))}</td></tr>"
        for item in issues[:12]
    )
    severity = "high" if int(counts.get("high", 0) or 0) else "medium" if int(counts.get("medium", 0) or 0) else "low"
    return f"""<section>
  <h2>知识图谱复核</h2>
  <div class="card alert alert-{severity}">
    <h3>问题 {int(counts.get('total', 0) or 0)} 个：高 {int(counts.get('high', 0) or 0)} / 中 {int(counts.get('medium', 0) or 0)} / 低 {int(counts.get('low', 0) or 0)}</h3>
    <p>模式：{html.escape(str(source.get('mode', '')))}；缓存：{html.escape(str(source.get('generated_dir', '')))}</p>
  </div>
  <table><thead><tr><th>级别</th><th>类型</th><th>对象</th><th>说明</th></tr></thead><tbody>{rows or '<tr><td colspan="4">暂无复核问题</td></tr>'}</tbody></table>
</section>"""


def _tier_name(tier: str) -> str:
    return {"strong": "强", "watch": "观察", "weak": "弱", "risk": "风险"}.get(tier, tier)


def _fmt(value: float | None) -> str:
    if value is None:
        return "-"
    return html.escape(f"{value:.2f}")
