from __future__ import annotations

import html
from datetime import date
from typing import Any

from .dashboard_contract import normalize_dashboard_data
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


def render_dashboard_from_data(dashboard_data: dict[str, Any] | None) -> str:
    data = normalize_dashboard_data(dashboard_data)
    run = _safe_dict(data.get("run"))
    schema_version = _text(data.get("schema_version") or "unknown")
    run_date = _text(run.get("date") or "unknown")
    generated_at = _text(run.get("generated_at") or "unknown")
    status = _text(run.get("status") or "unknown")
    warnings = _as_list(run.get("warnings"))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Daily Market Radar {html.escape(run_date)}</title>
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
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); }}
    .card h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .meta {{ color: var(--muted); font-size: 12px; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .strong, .confirmed, .ok {{ color: var(--strong); background: #e8f6f0; }}
    .watch, .not_checked, .unknown {{ color: var(--watch); background: #eaf1ff; }}
    .weak, .downgraded, .partial, .medium {{ color: var(--weak); background: #fff4d6; }}
    .risk, .failed, .missing, .error, .high, .flagged {{ color: var(--risk); background: #fee4e2; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; font-size: 12px; color: #344054; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; white-space: nowrap; }}
    .note-list {{ margin: 8px 0 0 18px; padding: 0; }}
    .muted {{ color: var(--muted); }}
    .signal-card {{ margin-bottom: 14px; }}
    .signal-head {{ display: flex; gap: 10px; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; }}
    .signal-head h3 {{ margin: 0; font-size: 16px; }}
    .signal-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); margin-top: 12px; }}
    .field-label {{ margin: 0 0 4px; color: var(--muted); font-size: 12px; }}
    .field-value {{ margin: 0; }}
    .candidate-list {{ margin: 6px 0 0 18px; padding: 0; }}
    .candidate-list li {{ margin-bottom: 4px; }}
    details {{ margin-top: 12px; }}
    summary {{ cursor: pointer; font-weight: 600; }}
    .output-list {{ margin: 0; padding: 0; list-style: none; }}
    .output-list li {{ margin-bottom: 6px; }}
    .controls {{ display: grid; gap: 12px; }}
    .control-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .control-label {{ display: grid; gap: 4px; color: var(--muted); font-size: 12px; }}
    .control-label input, .control-label select {{ border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; color: var(--text); background: var(--panel); font: inherit; }}
    .filter-chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .filter-chip {{ border: 1px solid var(--line); border-radius: 999px; background: var(--panel); color: var(--text); padding: 6px 10px; cursor: pointer; font: inherit; }}
    .filter-chip.active {{ border-color: var(--watch); color: var(--watch); background: #eaf1ff; }}
    .signal-count {{ color: var(--muted); font-size: 12px; }}
    .signal-card[hidden] {{ display: none; }}
  </style>
</head>
<body>
  <header>
    <h1>Daily Market Radar</h1>
    <p>{html.escape(run_date)} · generated_at {html.escape(generated_at)} · Schema: {html.escape(schema_version)}</p>
  </header>
  <main>
    {_run_summary_from_data(run_date, generated_at, status, warnings, schema_version)}
    {_market_context_from_data(data)}
    {_signal_overview_from_data(data)}
    {_signal_list_from_data(data)}
    {_knowledge_from_data(data)}
    {_outputs_from_data(data)}
  </main>
  {_dashboard_filter_script()}
</body>
</html>
"""


def _run_summary_from_data(
    run_date: str,
    generated_at: str,
    status: str,
    warnings: list[Any],
    schema_version: str,
) -> str:
    warning_items = "".join(f"<li>{html.escape(_text(item))}</li>" for item in warnings)
    warnings_html = f"<ul class='note-list'>{warning_items}</ul>" if warning_items else "<p class='muted'>No warnings.</p>"
    return f"""<section>
  <h2>Run Summary</h2>
  <div class="grid">
    <div class="card"><h3>Date</h3><p>{html.escape(run_date)}</p></div>
    <div class="card"><h3>Generated At</h3><p>{html.escape(generated_at)}</p></div>
    <div class="card"><h3>Status</h3><p><span class="pill {html.escape(status)}">{html.escape(status)}</span></p></div>
    <div class="card"><h3>Schema</h3><p>{html.escape(schema_version)}</p></div>
    <div class="card"><h3>Warnings</h3>{warnings_html}</div>
  </div>
</section>"""


def _market_context_from_data(data: dict[str, Any]) -> str:
    context = _safe_dict(data.get("market_context"))
    a_trade_day = _text(context.get("a_share_trading_day") or "unknown")
    is_trading = _text(context.get("is_a_share_trading_day") if "is_a_share_trading_day" in context else "unknown")
    context_source = _join_html(_as_list(context.get("sources") or context.get("source"))) or "unknown"
    context_time = _join_html(_as_list(context.get("fetched_at") or context.get("updated_at"))) or "unknown"
    sessions = _as_list(context.get("foreign_market_context"))
    session_rows = "".join(
        f"<tr><td>{html.escape(_text(_safe_dict(payload).get('market') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(payload).get('session_date') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(payload).get('is_market_trading_day') if 'is_market_trading_day' in _safe_dict(payload) else 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(payload).get('mapped_a_share_trade_day') or 'unknown'))}</td></tr>"
        for payload in sessions
    )
    if not session_rows:
        session_rows = "<tr><td colspan='4'>External context not provided.</td></tr>"
    return f"""<section>
  <h2>Market Context</h2>
  <div class="grid">
    <div class="card"><h3>A-share Trade Day</h3><p>{html.escape(a_trade_day)}</p></div>
    <div class="card"><h3>A-share Trading Status</h3><p>{html.escape(is_trading)}</p></div>
    <div class="card"><h3>Context Source</h3><p>{context_source}</p></div>
    <div class="card"><h3>Updated At</h3><p>{context_time}</p></div>
  </div>
  <table><thead><tr><th>Market</th><th>Session Date</th><th>Trading Day</th><th>Mapped A-share Day</th></tr></thead><tbody>{session_rows}</tbody></table>
</section>"""


def _signal_overview_from_data(data: dict[str, Any]) -> str:
    summary = _safe_dict(data.get("summary"))
    cards = (
        ("strong_signals", _as_int(summary.get("strong_signals")), "strong"),
        ("confirmed", _as_int(summary.get("confirmed")), "confirmed"),
        ("downgraded", _as_int(summary.get("downgraded")), "downgraded"),
        ("failed", _as_int(summary.get("failed")), "failed"),
        ("missing_data", _as_int(summary.get("missing_data")), "missing"),
        ("knowledge_issues", _as_int(summary.get("knowledge_issues")), "partial" if _as_int(summary.get("knowledge_issues")) else "ok"),
    )
    cards_html = "".join(
        f"<div class='card'><h3>{html.escape(label)}</h3><p><span class='pill {html.escape(style)}'>{value}</span></p></div>"
        for label, value, style in cards
    )
    return f"""<section>
  <h2>Signal Overview</h2>
  <div class="grid">{cards_html}</div>
</section>"""


def _signal_list_from_data(data: dict[str, Any]) -> str:
    signals = [_safe_dict(item) for item in _as_list(data.get("signals"))]
    cards = []
    for signal in signals:
        theme_name = _text(signal.get("theme") or "unknown")
        strength = _text(signal.get("strength") or "unknown")
        intraday_status = _text(signal.get("intraday_status") or "not_checked")
        risk_level = _text(signal.get("risk_level") or "unknown")
        data_status = _text(signal.get("data_status") or "unknown")
        score = _score_attr(signal.get("score"))
        search_text = _signal_search_text(signal)
        quick_tags = " ".join(_quick_filter_tags(signal, strength, intraday_status, risk_level, data_status))
        cards.append(
            f"""<article class="card signal-card" data-signal-card data-strength="{_attr(strength)}" data-intraday-status="{_attr(intraday_status)}" data-risk-level="{_attr(risk_level)}" data-data-status="{_attr(data_status)}" data-score="{_attr(score)}" data-search="{_attr(search_text)}" data-quick-tags="{_attr(quick_tags)}">
  <div class="signal-head">
    <h3>{html.escape(theme_name)}</h3>
    <div>
      <span class="pill {html.escape(intraday_status)}">{html.escape(intraday_status)}</span>
      <span class="pill {html.escape(risk_level)}">{html.escape(risk_level)}</span>
    </div>
  </div>
  <div class="signal-grid">
    <div><p class="field-label">Strength</p><p class="field-value">{html.escape(strength)}</p></div>
    <div><p class="field-label">Score</p><p class="field-value">{_number(signal.get('score'))}</p></div>
    <div><p class="field-label">Intraday Status</p><p class="field-value">{html.escape(intraday_status)}</p></div>
    <div><p class="field-label">Risk Level</p><p class="field-value">{html.escape(risk_level)}</p></div>
    <div><p class="field-label">Data Status</p><p class="field-value">{html.escape(data_status)}</p></div>
    <div><p class="field-label">Sources</p><p class="field-value">{_join_html(_as_list(signal.get('sources'))) or 'unknown'}</p></div>
    <div><p class="field-label">Fetched At</p><p class="field-value">{_join_html(_as_list(signal.get('fetched_at'))) or 'unknown'}</p></div>
  </div>
  <details open>
    <summary>Signal Evidence</summary>
    <div class="signal-grid">
      <div><p class="field-label">External Triggers</p>{_items_html(_as_list(signal.get('external_triggers')), 'No external triggers provided.')}</div>
      <div><p class="field-label">A-share Mapping Reason</p>{_items_html(_as_list(signal.get('a_share_mapping_reason')), 'No mapping reason provided.')}</div>
      <div><p class="field-label">Risks</p>{_items_html(_as_list(signal.get('risks')), 'No risk notes provided.')}</div>
    </div>
  </details>
  <details open>
    <summary>ETF Candidates</summary>
    {_items_html(_as_list(signal.get('etf_candidates')), 'No ETF candidates available.')}
  </details>
  <details open>
    <summary>Stock Candidates</summary>
    {_items_html(_as_list(signal.get('stock_candidates')), 'No stock candidates available.')}
  </details>
</article>"""
        )
    body = "".join(cards) or "<div class='card'>No signals available.</div>"
    return f"""<section>
  <h2>Signal List</h2>
  {_signal_controls_from_data(signals)}
  <div id="signal-card-list">{body}</div>
</section>"""


def _signal_controls_from_data(signals: list[dict[str, Any]]) -> str:
    total = len(signals)
    return f"""<div class="card controls" id="signal-browser-controls">
  <div class="control-grid">
    <label class="control-label" for="signal-search">Search
      <input id="signal-search" type="search" placeholder="Search theme, triggers, mapping, candidates, risks">
    </label>
    {_filter_select("filter-strength", "strength", "strength", signals)}
    {_filter_select("filter-intraday-status", "intraday_status", "intradayStatus", signals)}
    {_filter_select("filter-risk-level", "risk_level", "riskLevel", signals)}
    {_filter_select("filter-data-status", "data_status", "dataStatus", signals)}
    <label class="control-label" for="signal-sort">sort
      <select id="signal-sort">
        <option value="">Original order</option>
        <option value="score_desc">Score descending</option>
        <option value="risk_level">Risk level</option>
        <option value="intraday_status">Intraday status</option>
      </select>
    </label>
  </div>
  <div class="filter-chips" aria-label="Quick signal views">
    <button type="button" class="filter-chip active" data-quick-filter="all">All</button>
    <button type="button" class="filter-chip" data-quick-filter="confirmed">Confirmed</button>
    <button type="button" class="filter-chip" data-quick-filter="downgraded">Downgraded</button>
    <button type="button" class="filter-chip" data-quick-filter="missing">Missing Data</button>
    <button type="button" class="filter-chip" data-quick-filter="high-risk">High Risk</button>
    <button type="button" class="filter-chip" data-quick-filter="strong">Strong Signals</button>
  </div>
  <div class="signal-count"><span id="visible-signal-count">{total}</span> / <span id="total-signal-count">{total}</span> signals visible</div>
</div>"""


def _filter_select(element_id: str, label: str, dataset_field: str, signals: list[dict[str, Any]]) -> str:
    values = []
    for signal in signals:
        value = _text(signal.get(label) or "unknown")
        if value not in values:
            values.append(value)
    options = [f"<option value=''>All {html.escape(label)}</option>"]
    options.extend(
        f"<option value='{_attr(value)}'>{html.escape(value)}</option>"
        for value in sorted(values, key=str.lower)
        if value not in {"", "unknown"}
    )
    if "unknown" in values:
        options.append("<option value='unknown'>unknown</option>")
    return f"""<label class="control-label" for="{html.escape(element_id)}">{html.escape(label)}
      <select id="{html.escape(element_id)}" data-signal-filter data-field="{html.escape(dataset_field)}">
        {''.join(options)}
      </select>
    </label>"""


def _knowledge_from_data(data: dict[str, Any]) -> str:
    knowledge = _safe_dict(data.get("knowledge"))
    outputs = _safe_dict(data.get("outputs"))
    review_link = _path_link(outputs.get("knowledge_review_html"))
    if knowledge.get("status") == "unknown" and not _as_list(knowledge.get("issues")):
        return f"""<section>
  <h2>Knowledge Graph</h2>
  <div class="card"><h3>Status <span class="pill not_checked">not_checked</span></h3><p class="muted">Knowledge verification was not provided.</p><p><strong>Review:</strong> {review_link}</p></div>
</section>"""
    issues = _as_list(knowledge.get("issues"))
    suggestions = _as_list(knowledge.get("suggestions"))
    total = len(issues)
    status = _text(knowledge.get("status") or ("issues" if total else "ok"))
    issue_rows = "".join(
        f"<tr><td>{html.escape(_text(_safe_dict(item).get('severity') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('kind') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('target') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('message') or ''))}</td></tr>"
        for item in issues[:12]
    ) or "<tr><td colspan='4'>No knowledge issues.</td></tr>"
    suggestion_rows = "".join(
        f"<tr><td>{html.escape(_text(_safe_dict(item).get('kind') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('target') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('confidence') or 'unknown'))}</td>"
        f"<td>{html.escape(_text(_safe_dict(item).get('reason') or ''))}</td></tr>"
        for item in suggestions[:12]
    ) or "<tr><td colspan='4'>No suggestions available.</td></tr>"
    return f"""<section>
  <h2>Knowledge Graph</h2>
  <div class="card"><h3>Status <span class="pill {'partial' if total else 'ok'}">{html.escape(status)}</span></h3>
    <p>issues={total}; suggestions={len(suggestions)}</p>
    <p><strong>Review:</strong> {review_link}</p>
  </div>
  <h2>Knowledge Issues</h2>
  <table><thead><tr><th>Severity</th><th>Kind</th><th>Target</th><th>Message</th></tr></thead><tbody>{issue_rows}</tbody></table>
  <h2>Mapping Suggestions</h2>
  <table><thead><tr><th>Kind</th><th>Target</th><th>Confidence</th><th>Reason</th></tr></thead><tbody>{suggestion_rows}</tbody></table>
</section>"""


def _outputs_from_data(data: dict[str, Any]) -> str:
    outputs = _safe_dict(data.get("outputs"))
    report_md = outputs.get("report_md")
    dashboard_html = outputs.get("dashboard_html")
    knowledge_review_html = outputs.get("knowledge_review_html")
    return f"""<section>
  <h2>Output Links</h2>
  <div class="card">
    <ul class="output-list">
      <li><strong>report_md:</strong> {_path_link(report_md)}</li>
      <li><strong>dashboard_html:</strong> {_path_link(dashboard_html)}</li>
      <li><strong>knowledge_review_html:</strong> {_path_link(knowledge_review_html)}</li>
    </ul>
  </div>
</section>"""


def _dashboard_filter_script() -> str:
    return """<script>
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-signal-card]"));
  var list = document.getElementById("signal-card-list");
  var search = document.getElementById("signal-search");
  var filters = Array.prototype.slice.call(document.querySelectorAll("[data-signal-filter]"));
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-quick-filter]"));
  var sort = document.getElementById("signal-sort");
  var visibleCount = document.getElementById("visible-signal-count");
  var totalCount = document.getElementById("total-signal-count");
  var activeQuick = "all";

  if (!list || !search || !visibleCount || !totalCount) {
    return;
  }

  function normalize(value) {
    return String(value || "").toLowerCase();
  }

  function cardValue(card, field) {
    return normalize(card.dataset[field] || "");
  }

  function matchesQuick(card) {
    if (activeQuick === "all") {
      return true;
    }
    return (" " + normalize(card.dataset.quickTags) + " ").indexOf(" " + activeQuick + " ") !== -1;
  }

  function matchesFilters(card) {
    return filters.every(function (filter) {
      var value = normalize(filter.value);
      if (!value) {
        return true;
      }
      return cardValue(card, filter.dataset.field).indexOf(value) !== -1;
    });
  }

  function matchesSearch(card) {
    var query = normalize(search.value).trim();
    if (!query) {
      return true;
    }
    return normalize(card.dataset.search).indexOf(query) !== -1;
  }

  function applySort() {
    var mode = sort ? sort.value : "";
    var ordered = cards.slice();
    if (mode === "score_desc") {
      ordered.sort(function (a, b) {
        return (Number(b.dataset.score) || 0) - (Number(a.dataset.score) || 0);
      });
    } else if (mode === "risk_level") {
      ordered.sort(function (a, b) {
        return cardValue(a, "riskLevel").localeCompare(cardValue(b, "riskLevel"));
      });
    } else if (mode === "intraday_status") {
      ordered.sort(function (a, b) {
        return cardValue(a, "intradayStatus").localeCompare(cardValue(b, "intradayStatus"));
      });
    }
    ordered.forEach(function (card) {
      list.appendChild(card);
    });
  }

  function applyFilters() {
    var visible = 0;
    cards.forEach(function (card) {
      var show = matchesQuick(card) && matchesFilters(card) && matchesSearch(card);
      card.hidden = !show;
      if (show) {
        visible += 1;
      }
    });
    visibleCount.textContent = String(visible);
    totalCount.textContent = String(cards.length);
  }

  search.addEventListener("input", applyFilters);
  filters.forEach(function (filter) {
    filter.addEventListener("change", applyFilters);
  });
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeQuick = chip.dataset.quickFilter || "all";
      chips.forEach(function (item) {
        item.classList.toggle("active", item === chip);
      });
      applyFilters();
    });
  });
  if (sort) {
    sort.addEventListener("change", function () {
      applySort();
      applyFilters();
    });
  }

  applySort();
  applyFilters();
})();
</script>"""


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _number(value: Any) -> str:
    try:
        return f"{float(value):.0f}"
    except (TypeError, ValueError):
        return "unknown"


def _score_attr(value: Any) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return ""


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _join_html(values: list[Any]) -> str:
    clean = [_format_item(value) for value in values if _format_item(value) not in {"", "unknown"}]
    return "<br>".join(html.escape(item) for item in clean[:8])


def _items_html(values: list[Any], empty_text: str) -> str:
    items = [_format_item(value) for value in values if _format_item(value) not in {"", "unknown"}]
    if not items:
        return f"<p class='muted'>{html.escape(empty_text)}</p>"
    return "<ul class='candidate-list'>" + "".join(f"<li>{html.escape(item)}</li>" for item in items[:12]) + "</ul>"


def _format_item(value: Any) -> str:
    if isinstance(value, dict):
        preferred = [
            value.get("name"),
            value.get("ticker"),
            value.get("code"),
            value.get("category"),
            value.get("sector"),
        ]
        title = " ".join(str(item) for item in preferred if item)
        details = []
        for key in ("score", "risk", "risk_level", "source", "fetched_at", "reason", "mapping_reason"):
            if value.get(key) is not None:
                details.append(f"{key}: {value.get(key)}")
        fallback = "; ".join(f"{key}: {payload}" for key, payload in value.items() if payload is not None)
        if title and details:
            return f"{title} ({'; '.join(details)})"
        return title or fallback or "unknown"
    if isinstance(value, (list, tuple)):
        return ", ".join(_format_item(item) for item in value if _format_item(item))
    return _text(value)


def _signal_search_text(signal: dict[str, Any]) -> str:
    values: list[Any] = [
        signal.get("theme"),
        *_as_list(signal.get("external_triggers")),
        *_as_list(signal.get("a_share_mapping_reason")),
        *_as_list(signal.get("etf_candidates")),
        *_as_list(signal.get("stock_candidates")),
        *_as_list(signal.get("risks")),
    ]
    return " ".join(_format_item(value) for value in values if _format_item(value) not in {"", "unknown"})


def _quick_filter_tags(
    signal: dict[str, Any],
    strength: str,
    intraday_status: str,
    risk_level: str,
    data_status: str,
) -> list[str]:
    tags = []
    if intraday_status == "confirmed":
        tags.append("confirmed")
    if intraday_status == "downgraded":
        tags.append("downgraded")
    if "missing" in data_status.lower() or "missing" in intraday_status.lower():
        tags.append("missing")
    if risk_level.lower() in {"high", "risk", "failed", "flagged"} or intraday_status == "failed":
        tags.append("high-risk")
    if "strong" in strength.lower() or _is_at_least(signal.get("score"), 80.0):
        tags.append("strong")
    return tags


def _is_at_least(value: Any, threshold: float) -> bool:
    try:
        return float(value) >= threshold
    except (TypeError, ValueError):
        return False


def _attr(value: Any) -> str:
    return html.escape(_text(value), quote=True)


def _path_link(value: Any) -> str:
    if value in (None, ""):
        return "<span class='muted'>not provided</span>"
    text = _text(value)
    escaped = html.escape(text)
    normalized = text.replace("\\", "/")
    href_target = normalized
    if "://" not in normalized and "/" in normalized:
        href_target = normalized.rstrip("/").split("/")[-1]
    href = html.escape(href_target, quote=True)
    return f"<a href='{href}'>{escaped}</a>"
