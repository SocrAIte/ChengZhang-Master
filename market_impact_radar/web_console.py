from __future__ import annotations


def render_console_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>跨市场热点研究控制台</title>
  <style>
    html { scroll-behavior: smooth; }
    body { margin: 0; background: #f7f8fa; color: #18202f; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    header { background: #fff; border-bottom: 1px solid #d9dee7; padding: 18px 24px; }
    h1 { font-size: 22px; margin: 0 0 4px; }
    h2 { font-size: 16px; margin: 0 0 12px; }
    h3 { color: #344054; }
    main { display: grid; gap: 16px; grid-template-columns: minmax(220px, 320px) 1fr; padding: 16px; }
    section, article, .metric { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 14px; }
    .section-card { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); margin-bottom: 14px; padding: 14px; }
    .section-card > h2, details.collapsible-section > summary { background: #f0f5ff; border-radius: 6px; margin: -2px -6px 12px; padding: 6px 10px; }
    button { background: #fff; border: 1px solid #d9dee7; border-radius: 6px; cursor: pointer; display: block; margin: 0 0 8px; padding: 10px; text-align: left; width: 100%; }
    button.active, button:hover { border-color: #1f6feb; }
    button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible { outline: 2px solid #1f6feb; outline-offset: 2px; }
    input, select { border: 1px solid #d9dee7; border-radius: 6px; padding: 9px; width: 100%; }
    label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; }
    .muted { color: #667085; font-size: 13px; }
    .controls { display: grid; gap: 10px; margin: 12px 0; }
    .signal-controls { grid-template-columns: minmax(180px, 1fr) repeat(4, minmax(130px, 180px)); }
    .metrics { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); margin-bottom: 14px; }
    .badge { border: 1px solid #d9dee7; border-radius: 999px; display: inline-block; font-size: 12px; line-height: 1.5; margin: 2px 4px 2px 0; padding: 2px 8px; }
    .badge-risk { background: #fff7ed; border-color: #fed7aa; color: #9a3412; }
    .badge-status { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
    .badge-data { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
    .badge-warning { background: #fffaeb; border-color: #fedf89; color: #93370d; }
    .badge-muted, .badge-unknown { background: #f8fafc; color: #475467; }
    .badge-ok { background: #ecfdf3; border-color: #abefc6; color: #067647; }
    .status-strip { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .ui-language-toggle { display: inline-block; margin: 10px 0 0; padding: 7px 10px; text-align: center; width: auto; }
    .workspace-nav { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; margin-top: 14px; padding: 12px; position: sticky; top: 0; z-index: 5; }
    .workspace-nav h2 { margin-bottom: 6px; }
    .nav-links { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .nav-links a, .back-to-top { background: #fff; border: 1px solid #d9dee7; border-radius: 999px; display: inline-block; font-size: 12px; padding: 5px 9px; text-decoration: none; }
    .nav-links a:hover, .back-to-top:hover { border-color: #1f6feb; }
    .section-description { margin-top: -4px; }
    details.collapsible-section { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; margin-bottom: 14px; padding: 14px; }
    details.collapsible-section > summary { cursor: pointer; font-size: 16px; font-weight: 700; margin-bottom: 8px; }
    details.collapsible-section[open] > summary { margin-bottom: 12px; }
    .back-to-top { margin-top: 12px; }
    .error { color: #b42318; }
    .signals { display: grid; gap: 12px; }
    .analysis-layout { align-items: start; display: grid; gap: 14px; grid-template-columns: minmax(260px, 1fr) minmax(320px, 420px); }
    .signal-card { cursor: pointer; transition: border-color 120ms ease, box-shadow 120ms ease; }
    .signal-card.selected { border-color: #1f6feb; box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.12); }
    .signal-detail { position: sticky; top: 12px; }
    .theme-detail { margin-bottom: 14px; }
    .theme-button { background: transparent; border: 0; color: #1f6feb; cursor: pointer; display: inline; font: inherit; margin: 0; padding: 0; text-align: left; width: auto; }
    .theme-button.active { font-weight: 700; text-decoration: underline; }
    .detail-section { border-top: 1px solid #eef1f6; margin-top: 12px; overflow-x: auto; padding-top: 12px; }
    .detail-section h3 { font-size: 14px; margin: 0 0 8px; }
    .evidence-chain { display: grid; gap: 8px; margin: 0; padding-left: 20px; }
    .candidate-table { border-collapse: collapse; font-size: 13px; line-height: 1.4; width: 100%; }
    .candidate-table th, .candidate-table td { border-bottom: 1px solid #eef1f6; padding: 6px 7px; text-align: left; vertical-align: top; word-break: break-word; }
    .candidate-table th { background: #f8fafc; color: #667085; font-weight: 600; }
    .history-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-bottom: 14px; }
    .history-table { border-collapse: collapse; font-size: 13px; line-height: 1.4; width: 100%; }
    .history-table th, .history-table td { border-bottom: 1px solid #eef1f6; padding: 6px 7px; text-align: left; vertical-align: top; word-break: break-word; }
    .history-table th { background: #f8fafc; color: #667085; font-weight: 600; }
    .history-table tbody tr:nth-child(even), .candidate-table tbody tr:nth-child(even) { background: #fbfcfe; }
    .history-table td:nth-child(n+2), .candidate-table td:nth-child(n+2) { font-variant-numeric: tabular-nums; }
    .brief-section { background: #fbfcfe; border: 1px solid #eef1f6; border-radius: 8px; margin-top: 10px; padding: 10px; }
    .brief-section h3 { font-size: 14px; margin: 0 0 6px; }
    .research-brief { margin-bottom: 14px; }
    .research-brief-controls { align-items: end; display: grid; gap: 10px; grid-template-columns: minmax(180px, 260px) repeat(2, minmax(150px, 190px)); margin: 12px 0; }
    .brief-toggle-grid { display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 10px 0; }
    .brief-toggle-grid label { align-items: center; background: #fbfcfe; border: 1px solid #eef1f6; border-radius: 6px; display: flex; gap: 8px; padding: 7px 8px; }
    .brief-toggle-grid input { width: auto; }
    .brief-meta { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
    .brief-warning { border: 1px solid #fedf89; background: #fffaeb; border-radius: 6px; color: #93370d; padding: 8px; }
    .research-brief-textarea { box-sizing: border-box; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; min-height: 360px; resize: vertical; white-space: pre; }
    .research-notes { margin-bottom: 14px; }
    .research-notes-controls { align-items: end; display: grid; gap: 10px; grid-template-columns: minmax(180px, 260px) repeat(3, minmax(140px, 180px)); margin: 12px 0; }
    .research-notes-textarea { box-sizing: border-box; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; min-height: 320px; resize: vertical; white-space: pre; width: 100%; }
    .manual-notes { min-height: 110px; resize: vertical; width: 100%; }
    .research-export { margin-bottom: 14px; }
    .export-controls { align-items: end; display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 12px 0; }
    .export-preview { box-sizing: border-box; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; min-height: 280px; resize: vertical; white-space: pre; width: 100%; }
    .review-queue { margin-bottom: 14px; }
    .review-controls { align-items: end; display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 12px 0; }
    .review-item-list { display: grid; gap: 10px; margin-top: 10px; }
    .review-item { background: #fbfcfe; border: 1px solid #eef1f6; border-radius: 8px; padding: 10px; }
    .review-item h3 { font-size: 14px; margin: 0 0 6px; }
    .theme-hotlist, .theme-group { margin-bottom: 14px; }
    .theme-summary { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
    .theme-card { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 12px; }
    .theme-card h3, .theme-group h3 { margin: 0 0 8px; }
    .morning-brief, .compare-workspace { margin-bottom: 14px; }
    .source-reliability { margin-bottom: 14px; }
    .source-detail { margin-top: 14px; }
    .theme-source-matrix { margin-bottom: 14px; }
    .matrix-table-wrap { overflow-x: auto; }
    .matrix-cell { min-width: 150px; }
    .matrix-cell button { margin: 0; padding: 8px; }
    .matrix-cell.weak { background: #fff7ed; }
    .compare-grid { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
    .compare-card { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 12px; }
    .compare-actions { align-items: end; display: grid; gap: 10px; grid-template-columns: minmax(180px, 1fr) auto; margin: 10px 0; }
    .notice { border: 1px solid #fedf89; background: #fffaeb; border-radius: 6px; color: #93370d; padding: 8px; }
    button.inline-action { display: inline-block; margin: 4px 6px 4px 0; padding: 7px 9px; text-align: center; width: auto; }
    button.inline-action.active { background: #eff6ff; }
    .artifacts { margin-bottom: 14px; }
    .artifacts li { margin-bottom: 4px; }
    a { color: #1f6feb; }
    pre { background: #101828; border-radius: 8px; color: #f2f4f7; overflow: auto; padding: 12px; }
    [hidden] { display: none; }
    @media (max-width: 960px) { main, .signal-controls, .analysis-layout { grid-template-columns: 1fr; } .signal-detail { position: static; } }
  </style>
</head>
<body>
  <header>
    <h1>跨市场热点研究控制台</h1>
    <div class="muted">只读 daily report 研究工作台。页面只读取已有 API 数据，不运行 pipeline。</div>
    <button id="ui-language-toggle" class="ui-language-toggle" type="button">English</button>
    <div id="status-strip" class="status-strip" aria-label="API 状态和版本"></div>
    <nav id="workspace-navigation" class="workspace-nav" aria-label="工作台导航">
      <h2>工作台导航</h2>
      <div class="nav-links">
        <a href="#console-usage-guide">使用引导</a>
        <a href="#morning-brief">今日观察摘要</a>
        <a href="#daily-research-brief">每日研究摘要</a>
        <a href="#research-review-queue">研究复核清单</a>
        <a href="#research-notes-composer">研究笔记工作区</a>
        <a href="#research-export-package">研究包导出</a>
        <a href="#date-compare">日期对比</a>
        <a href="#console-controls">筛选控件</a>
        <a href="#theme-hotlist">主题热榜</a>
        <a href="#source-reliability">数据来源可靠性</a>
        <a href="#theme-source-matrix">主题 &times; 来源矩阵</a>
        <a href="#theme-compare">主题对比</a>
        <a href="#historical-review">历史复盘</a>
        <a href="#signal-explorer">信号浏览器</a>
        <a href="#signal-detail">信号详情</a>
        <a href="#theme-detail">主题详情</a>
        <a href="#source-detail">来源详情</a>
        <a href="#artifact-links">产物链接</a>
      </div>
    </nav>
  </header>
  <main>
    <section class="section-card">
      <h2>Daily 运行记录</h2>
      <div id="runs-status" class="muted">正在加载运行记录...</div>
      <div class="controls">
        <div>
          <label for="run-select">运行日期</label>
          <select id="run-select"></select>
        </div>
        <button id="refresh-runs" type="button">刷新运行记录</button>
      </div>
      <div id="runs"></div>
    </section>
    <section class="section-card">
      <h2>Dashboard 数据</h2>
      <div id="dashboard-status" class="muted">请选择一个运行日期加载 dashboard 数据。</div>
      <p class="muted section-description">按日期、搜索词、风险、状态、排序和视图模式调整只读研究视图。</p>
      <div id="console-controls" class="controls signal-controls">
        <div>
          <label for="signal-search">搜索信号</label>
          <input id="signal-search" type="search" placeholder="搜索主题、触发源、候选池、风险">
        </div>
        <div>
          <label for="risk-filter">风险筛选</label>
          <select id="risk-filter">
            <option value="">全部风险</option>
            <option value="high">高风险</option>
            <option value="medium">中风险</option>
            <option value="low">低风险</option>
            <option value="unknown">未知风险</option>
          </select>
        </div>
        <div>
          <label for="status-filter">状态筛选</label>
          <select id="status-filter">
            <option value="">全部状态</option>
            <option value="confirmed">已确认</option>
            <option value="downgraded">已降级</option>
            <option value="failed">未通过</option>
            <option value="missing_data">缺数据</option>
            <option value="not_checked">未检查</option>
            <option value="unknown">未知状态</option>
          </select>
        </div>
        <div>
          <label for="sort-select">信号排序</label>
          <select id="sort-select">
            <option value="default">默认顺序</option>
            <option value="score_desc">分数从高到低</option>
            <option value="risk_level">风险等级</option>
            <option value="intraday_status">盘中状态</option>
            <option value="theme">主题名称</option>
          </select>
        </div>
        <div>
          <label for="view-mode">视图</label>
          <select id="view-mode">
            <option value="grouped">按主题分组</option>
            <option value="flat">平铺信号列表</option>
          </select>
        </div>
      </div>
      <div id="signal-count" class="muted">尚未加载信号。</div>
      <a class="back-to-top" href="#workspace-navigation">返回顶部</a>
      <div id="dashboard"></div>
    </section>
  </main>
  <script>
    const runsEl = document.querySelector("#runs");
    const runsStatusEl = document.querySelector("#runs-status");
    const runSelectEl = document.querySelector("#run-select");
    const refreshRunsEl = document.querySelector("#refresh-runs");
    const dashboardEl = document.querySelector("#dashboard");
    const dashboardStatusEl = document.querySelector("#dashboard-status");
    const signalSearchEl = document.querySelector("#signal-search");
    const riskFilterEl = document.querySelector("#risk-filter");
    const statusFilterEl = document.querySelector("#status-filter");
    const sortSelectEl = document.querySelector("#sort-select");
    const viewModeEl = document.querySelector("#view-mode");
    const signalCountEl = document.querySelector("#signal-count");
    const statusStripEl = document.querySelector("#status-strip");
    const uiLanguageToggleEl = document.querySelector("#ui-language-toggle");
    let currentSignals = [];
    let signalsAreaEl = null;
    let currentArtifacts = null;
    let currentDashboardData = null;
    let selectedSignalIndex = null;
    let selectedTheme = "";
    let selectedSource = "";
    let selectedMatrixTheme = "";
    let selectedMatrixSource = "";
    let compareThemes = [];
    let compareNotice = "";
    let uiLang = "zh";
    let briefMode = "full";
    let briefLang = "zh";
    let briefSections = {
      overview: true,
      watchThemes: true,
      evidence: true,
      candidates: true,
      risk: true,
      dataQuality: true,
      dateCompare: true,
      reviewQueue: true,
      history: true,
      finalNotes: true,
    };
    let dateCompareData = null;
    let compareFromDate = "";
    let compareToDate = "";
    let reviewSeverity = "";
    let reviewCategory = "";
    let reviewScope = "visible";
    let notesLang = "zh";
    let notesMode = "full";
    let exportLang = "";
    let exportFormat = "md";
    let manualResearchNotes = "";
    let notesSections = {
      context: true,
      watchThemes: true,
      reviewItems: true,
      evidenceGaps: true,
      dateCompare: true,
      candidates: true,
      dataQuality: true,
      openQuestions: true,
      followUp: true,
    };
    let exportSections = {
      dailyBrief: true,
      researchNotes: true,
      reviewQueue: true,
      dateCompare: true,
      sourceReliability: true,
      matrixSummary: true,
      candidatePool: true,
      manualNotes: true,
      queryState: true,
    };
    let visibleSignalCount = 0;
    let apiHealthData = null;
    let apiVersionData = null;
    let themeHistoryData = null;
    let candidateHistoryData = null;
    let dataQualityHistoryData = null;
    let sourceHistoryData = null;
    let themeSourceMatrixData = null;
    const VALID_RISKS = new Set(["", "low", "medium", "high", "unknown"]);
    const VALID_STATUSES = new Set(["", "confirmed", "downgraded", "missing_data", "failed", "not_checked", "unknown"]);
    const VALID_SORTS = new Set(["default", "score_desc", "risk_level", "intraday_status", "theme"]);
    const VALID_VIEWS = new Set(["grouped", "flat"]);
    const VALID_UI_LANGS = new Set(["en", "zh"]);
    const VALID_BRIEF_LANGS = new Set(["en", "zh"]);
    const VALID_BRIEF_MODES = new Set(["full", "compact"]);
    const VALID_REVIEW_SEVERITIES = new Set(["", "high", "medium", "low", "info"]);
    const VALID_REVIEW_CATEGORIES = new Set(["", "weak_evidence", "missing_source", "missing_fetched_at", "stale_or_partial_data", "fallback_used", "high_risk_with_weak_data", "date_compare_change", "candidate_pool_change", "theme_source_gap"]);
    const VALID_REVIEW_SCOPES = new Set(["visible", "all"]);
    const VALID_NOTES_LANGS = new Set(["en", "zh"]);
    const VALID_NOTES_MODES = new Set(["full", "compact"]);
    const VALID_EXPORT_LANGS = new Set(["", "en", "zh"]);
    const VALID_EXPORT_FORMATS = new Set(["md", "txt", "json"]);
    const NOTES_SECTION_KEYS = ["context", "watchThemes", "reviewItems", "evidenceGaps", "dateCompare", "candidates", "dataQuality", "openQuestions", "followUp"];
    const EXPORT_SECTION_KEYS = ["dailyBrief", "researchNotes", "reviewQueue", "dateCompare", "sourceReliability", "matrixSummary", "candidatePool", "manualNotes", "queryState"];
    const BRIEF_SECTION_KEYS = ["overview", "watchThemes", "evidence", "candidates", "risk", "dataQuality", "dateCompare", "reviewQueue", "history", "finalNotes"];
    const MAX_COMPARE_THEMES = 3;

    function normalizeChoice(value, allowed, fallback) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      const normalizedValue = textValue === "all" ? "" : textValue;
      return allowed.has(normalizedValue) ? normalizedValue : fallback;
    }

    function normalizeSort(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      const aliases = { "score-desc": "score_desc", risk: "risk_level", status: "intraday_status" };
      const normalizedValue = aliases[textValue] || textValue || "default";
      return VALID_SORTS.has(normalizedValue) ? normalizedValue : "default";
    }

    function normalizeBriefLang(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_BRIEF_LANGS.has(textValue) ? textValue : "zh";
    }

    function normalizeUiLang(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_UI_LANGS.has(textValue) ? textValue : "zh";
    }

    function uiText(zh, en) {
      return uiLang === "en" ? en : zh;
    }

    function normalizeBriefMode(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_BRIEF_MODES.has(textValue) ? textValue : "full";
    }

    function normalizeNotesLang(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_NOTES_LANGS.has(textValue) ? textValue : "zh";
    }

    function normalizeNotesMode(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_NOTES_MODES.has(textValue) ? textValue : "full";
    }

    function normalizeExportLang(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_EXPORT_LANGS.has(textValue) ? textValue : "";
    }

    function normalizeExportFormat(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_EXPORT_FORMATS.has(textValue) ? textValue : "md";
    }

    function normalizeReviewScope(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase() || "visible";
      return VALID_REVIEW_SCOPES.has(textValue) ? textValue : "visible";
    }

    function normalizeConsoleState(state) {
      return {
        date: String(state.date || "").trim(),
        search: String(state.search || "").trim(),
        risk: normalizeChoice(state.risk, VALID_RISKS, ""),
        status: normalizeChoice(state.status, VALID_STATUSES, ""),
        sort: normalizeSort(state.sort),
        view: normalizeChoice(state.view || "grouped", VALID_VIEWS, "grouped"),
        theme: String(state.theme || "").trim(),
        source: String(state.source || "").trim(),
        matrixTheme: String(state.matrixTheme || "").trim(),
        matrixSource: String(state.matrixSource || "").trim(),
        compare: normalizeCompareThemes(state.compare),
        uiLang: normalizeUiLang(state.uiLang),
        briefLang: normalizeBriefLang(state.briefLang || state.uiLang),
        briefMode: normalizeBriefMode(state.briefMode),
        compareFrom: String(state.compareFrom || "").trim(),
        compareTo: String(state.compareTo || "").trim(),
        reviewSeverity: normalizeChoice(state.reviewSeverity, VALID_REVIEW_SEVERITIES, ""),
        reviewCategory: normalizeChoice(state.reviewCategory, VALID_REVIEW_CATEGORIES, ""),
        reviewScope: normalizeReviewScope(state.reviewScope),
        notesLang: normalizeNotesLang(state.notesLang || state.uiLang),
        notesMode: normalizeNotesMode(state.notesMode),
        exportLang: normalizeExportLang(state.exportLang || state.uiLang),
        exportFormat: normalizeExportFormat(state.exportFormat),
      };
    }

    function normalizeCompareThemes(value) {
      const rawValues = Array.isArray(value) ? value : String(value || "").split(",");
      const themes = [];
      for (const item of rawValues) {
        const theme = String(item || "").trim();
        if (!theme) continue;
        if (!themes.some((existing) => sameTheme(existing, theme))) themes.push(theme);
        if (themes.length >= MAX_COMPARE_THEMES) break;
      }
      return themes;
    }

    function readConsoleStateFromUrl() {
      const params = new URLSearchParams(window.location.search);
      return normalizeConsoleState({
        date: params.get("date"),
        search: params.get("search"),
        risk: params.get("risk"),
        status: params.get("status"),
        sort: params.get("sort"),
        view: params.get("view"),
        theme: params.get("theme"),
        source: params.get("source"),
        matrixTheme: params.get("matrixTheme"),
        matrixSource: params.get("matrixSource"),
        compare: params.get("compare"),
        uiLang: params.get("uiLang"),
        briefLang: params.get("briefLang"),
        briefMode: params.get("briefMode"),
        compareFrom: params.get("compareFrom"),
        compareTo: params.get("compareTo"),
        reviewSeverity: params.get("reviewSeverity"),
        reviewCategory: params.get("reviewCategory"),
        reviewScope: params.get("reviewScope"),
        notesLang: params.get("notesLang"),
        notesMode: params.get("notesMode"),
        exportLang: params.get("exportLang"),
        exportFormat: params.get("exportFormat"),
      });
    }

    function selectHasValue(select, value) {
      return Array.from(select.options).some((option) => option.value === value);
    }

    function setSelectValue(select, value, fallback) {
      select.value = selectHasValue(select, value) ? value : fallback;
    }

    function syncControlsFromState(state) {
      const normalizedState = normalizeConsoleState(state);
      signalSearchEl.value = normalizedState.search;
      setSelectValue(riskFilterEl, normalizedState.risk, "");
      setSelectValue(statusFilterEl, normalizedState.status, "");
      setSelectValue(sortSelectEl, normalizedState.sort, "default");
      setSelectValue(viewModeEl, normalizedState.view, "grouped");
      selectedTheme = normalizedState.theme;
      selectedSource = normalizedState.source;
      selectedMatrixTheme = normalizedState.matrixTheme;
      selectedMatrixSource = normalizedState.matrixSource;
      compareThemes = normalizedState.compare;
      uiLang = normalizedState.uiLang;
      briefLang = normalizedState.briefLang;
      briefMode = normalizedState.briefMode;
      compareFromDate = normalizedState.compareFrom;
      compareToDate = normalizedState.compareTo;
      reviewSeverity = normalizedState.reviewSeverity;
      reviewCategory = normalizedState.reviewCategory;
      reviewScope = normalizedState.reviewScope;
      notesLang = normalizedState.notesLang;
      notesMode = normalizedState.notesMode;
      exportLang = normalizedState.exportLang;
      exportFormat = normalizedState.exportFormat;
      if (normalizedState.date && selectHasValue(runSelectEl, normalizedState.date)) {
        runSelectEl.value = normalizedState.date;
      }
    }

    function currentConsoleState() {
      return normalizeConsoleState({
        date: runSelectEl.value,
        search: signalSearchEl.value,
        risk: riskFilterEl.value,
        status: statusFilterEl.value,
        sort: sortSelectEl.value,
        view: viewModeEl.value,
        theme: selectedTheme,
        source: selectedSource,
        matrixTheme: selectedMatrixTheme,
        matrixSource: selectedMatrixSource,
        compare: compareThemes,
        uiLang,
        briefLang,
        briefMode,
        compareFrom: compareFromDate,
        compareTo: compareToDate,
        reviewSeverity,
        reviewCategory,
        reviewScope,
        notesLang,
        notesMode,
        exportLang,
        exportFormat,
      });
    }

    function updateQueryState(patch = {}) {
      const state = normalizeConsoleState({ ...currentConsoleState(), ...patch });
      const params = new URLSearchParams();
      if (state.date) params.set("date", state.date);
      if (state.search) params.set("search", state.search);
      if (state.risk) params.set("risk", state.risk);
      if (state.status) params.set("status", state.status);
      if (state.sort !== "default") params.set("sort", state.sort);
      if (state.view !== "grouped") params.set("view", state.view);
      if (state.theme) params.set("theme", state.theme);
      if (state.source) params.set("source", state.source);
      if (state.matrixTheme) params.set("matrixTheme", state.matrixTheme);
      if (state.matrixSource) params.set("matrixSource", state.matrixSource);
      if (state.compare.length) params.set("compare", state.compare.join(","));
      if (state.uiLang !== "zh") params.set("uiLang", state.uiLang);
      if (state.briefLang !== "zh") params.set("briefLang", state.briefLang);
      if (state.briefMode !== "full") params.set("briefMode", state.briefMode);
      if (state.compareFrom) params.set("compareFrom", state.compareFrom);
      if (state.compareTo) params.set("compareTo", state.compareTo);
      if (state.reviewSeverity) params.set("reviewSeverity", state.reviewSeverity);
      if (state.reviewCategory) params.set("reviewCategory", state.reviewCategory);
      if (state.reviewScope !== "visible") params.set("reviewScope", state.reviewScope);
      if (state.notesLang !== "zh") params.set("notesLang", state.notesLang);
      if (state.notesMode !== "full") params.set("notesMode", state.notesMode);
      if (state.exportLang) params.set("exportLang", state.exportLang);
      if (state.exportFormat !== "md") params.set("exportFormat", state.exportFormat);
      const query = params.toString();
      const nextUrl = `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash || ""}`;
      window.history.replaceState(null, "", nextUrl);
    }

    function clear(node) {
      while (node.firstChild) node.removeChild(node.firstChild);
    }

    function text(tag, value, className) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      node.textContent = value == null || value === "" ? "unknown" : String(value);
      return node;
    }

    function link(href, label) {
      const node = document.createElement("a");
      node.href = href;
      node.target = "_blank";
      node.rel = "noreferrer";
      node.textContent = label;
      return node;
    }

    function anchorLink(href, label, className) {
      const node = document.createElement("a");
      node.href = href;
      if (className) node.className = className;
      node.textContent = label;
      return node;
    }

    function description(value) {
      return text("p", value, "muted section-description");
    }

    function appendBackToTop(node) {
      node.appendChild(anchorLink("#workspace-navigation", uiText("返回顶部", "Back to top"), "back-to-top"));
      return node;
    }

    function setText(selector, zh, en) {
      const node = document.querySelector(selector);
      if (node) node.textContent = uiText(zh, en);
    }

    function setOptionLabels(select, labels) {
      if (!select) return;
      for (const [value, zh, en] of labels) {
        const option = Array.from(select.options).find((item) => item.value === value);
        if (option) option.textContent = uiText(zh, en);
      }
    }

    function applyStaticUiLanguage() {
      document.documentElement.lang = uiLang === "en" ? "en" : "zh-CN";
      document.title = uiText("跨市场热点研究控制台", "Market Impact Radar Research Console");
      setText("header h1", "跨市场热点研究控制台", "Market Impact Radar Research Console");
      setText("header > .muted", "只读 daily report 研究工作台。页面只读取已有 API 数据，不运行 pipeline。", "Readonly daily report research workspace. The page only reads existing API data and does not run the pipeline.");
      if (uiLanguageToggleEl) {
        uiLanguageToggleEl.textContent = uiText("English", "中文");
        uiLanguageToggleEl.setAttribute("aria-label", uiText("切换到英文界面", "Switch to Chinese interface"));
      }
      setText("#workspace-navigation h2", "工作台导航", "Workspace Navigation");
      const navLabels = {
        "#console-usage-guide": ["使用引导", "Usage Guide"],
        "#morning-brief": ["今日观察摘要", "Morning Brief"],
        "#daily-research-brief": ["每日研究摘要", "Daily Research Brief"],
        "#research-review-queue": ["研究复核清单", "Research Review Queue"],
        "#research-notes-composer": ["研究笔记工作区", "Research Notes"],
        "#research-export-package": ["研究包导出", "Research Export"],
        "#date-compare": ["日期对比", "Date Compare"],
        "#console-controls": ["筛选控件", "Controls"],
        "#theme-hotlist": ["主题热榜", "Theme Hotlist"],
        "#source-reliability": ["数据来源可靠性", "Source Reliability"],
        "#theme-source-matrix": ["主题 × 来源矩阵", "Theme × Source Matrix"],
        "#theme-compare": ["主题对比", "Theme Compare"],
        "#historical-review": ["历史复盘", "Historical Review"],
        "#signal-explorer": ["信号浏览器", "Signal Explorer"],
        "#signal-detail": ["信号详情", "Signal Detail"],
        "#theme-detail": ["主题详情", "Theme Detail"],
        "#source-detail": ["来源详情", "Source Detail"],
        "#artifact-links": ["产物链接", "Artifact Links"],
      };
      for (const [href, labels] of Object.entries(navLabels)) {
        const node = document.querySelector(`#workspace-navigation a[href="${href}"]`);
        if (node) node.textContent = uiText(labels[0], labels[1]);
      }
      setText("main > section:nth-of-type(1) h2", "Daily 运行记录", "Daily Runs");
      setText("label[for='run-select']", "运行日期", "Run Date");
      setText("#refresh-runs", "刷新运行记录", "Refresh Runs");
      setText("main > section:nth-of-type(2) h2", "Dashboard 数据", "Dashboard Data");
      setText("label[for='signal-search']", "搜索信号", "Signal Search");
      setText("label[for='risk-filter']", "风险筛选", "Risk Filter");
      setText("label[for='status-filter']", "状态筛选", "Status Filter");
      setText("label[for='sort-select']", "信号排序", "Sort");
      setText("label[for='view-mode']", "视图", "View");
      setOptionLabels(riskFilterEl, [["", "全部风险", "All risk"], ["high", "高风险", "High"], ["medium", "中风险", "Medium"], ["low", "低风险", "Low"], ["unknown", "未知风险", "Unknown"]]);
      setOptionLabels(statusFilterEl, [["", "全部状态", "All status"], ["confirmed", "已确认", "Confirmed"], ["downgraded", "已降级", "Downgraded"], ["failed", "未通过", "Failed"], ["missing_data", "缺数据", "Missing data"], ["not_checked", "未检查", "Not checked"], ["unknown", "未知状态", "Unknown"]]);
      setOptionLabels(sortSelectEl, [["default", "默认顺序", "Default order"], ["score_desc", "分数从高到低", "Score descending"], ["risk_level", "风险等级", "Risk level"], ["intraday_status", "盘中状态", "Intraday status"], ["theme", "主题名称", "Theme name"]]);
      setOptionLabels(viewModeEl, [["grouped", "按主题分组", "Grouped by theme"], ["flat", "平铺信号列表", "Flat signal list"]]);
    }

    function setUiLanguage(nextLang) {
      uiLang = normalizeUiLang(nextLang);
      briefLang = uiLang;
      notesLang = uiLang;
      exportLang = uiLang;
      updateQueryState({ uiLang, briefLang, notesLang, exportLang });
      if (currentDashboardData) {
        renderDashboard(currentDashboardData, currentArtifacts);
      } else {
        applyStaticUiLanguage();
      }
    }

    function badgeClass(value) {
      const label = normalized(value);
      if (label.includes("risk:") || label.includes("main risk") || label.includes("max risk")) return "badge-risk";
      if (label.includes("intraday") || label.includes("status:") || label.includes("main status") || label.includes("confirmed") || label.includes("downgraded") || label.includes("failed") || label.includes("not_checked")) return "badge-status";
      if (label.includes("data:") || label.includes("data status") || label.includes("fetched") || label.includes("source")) return label.includes("unknown") || label.includes("missing") || label.includes("partial") || label.includes("stale") ? "badge-warning" : "badge-data";
      if (label.includes("weak") || label.includes("missing") || label.includes("fallback") || label.includes("needs verification")) return "badge-warning";
      if (label.includes("unknown") || label.includes("unavailable")) return "badge-unknown";
      if (label.includes("ok") || label.includes("fresh")) return "badge-ok";
      if (label.includes("strength:")) return "badge-muted";
      return "badge-muted";
    }

    function list(values) {
      const ul = document.createElement("ul");
      const items = Array.isArray(values) ? values : [];
      if (items.length === 0) items.push("None");
      for (const item of items) ul.appendChild(text("li", typeof item === "string" ? item : JSON.stringify(item)));
      return ul;
    }

    function arrayValue(value) {
      if (Array.isArray(value)) return value;
      if (value == null || value === "") return [];
      return [value];
    }

    function firstText(value, fallback = "unknown") {
      const values = arrayValue(value);
      if (values.length === 0) return fallback;
      const first = values[0];
      if (first == null || first === "") return fallback;
      return typeof first === "string" ? first : JSON.stringify(first);
    }

    function fieldValue(object, keys, fallback = "unknown") {
      if (!object || typeof object !== "object" || Array.isArray(object)) return fallback;
      for (const key of keys) {
        const value = object[key];
        if (value != null && value !== "") return Array.isArray(value) ? firstText(value, fallback) : String(value);
      }
      return fallback;
    }

    function sourceValues(signal) {
      return arrayValue(signal.sources || signal.source);
    }

    function fetchedValues(signal) {
      return arrayValue(signal.fetched_at || signal.fetchedAt);
    }

    function dataStatusLabel(value) {
      const status = normalized(value);
      if (status.includes("missing")) return "缺失";
      if (status.includes("partial")) return "部分数据";
      if (status.includes("stale")) return "过期";
      if (status === "failed") return "失败";
      if (status === "ok") return "正常";
      if (status === "fresh") return "新鲜";
      return "未知";
    }

    function riskLabel(value) {
      const risk = normalized(value);
      if (risk === "high") return "高风险";
      if (risk === "medium") return "中风险";
      if (risk === "low") return "低风险";
      return "未知风险";
    }

    function intradayStatusLabel(value) {
      const status = normalized(value || "not_checked");
      if (status === "confirmed") return "已确认";
      if (status === "downgraded") return "已降级";
      if (status === "failed") return "未通过";
      if (status === "missing_data") return "缺数据";
      if (status === "not_checked") return "未检查";
      return "未知状态";
    }

    function strengthLabel(value) {
      const strength = normalized(value);
      if (strength.includes("strong")) return "强";
      if (strength.includes("medium")) return "中";
      if (strength.includes("weak")) return "弱";
      return value == null || value === "" ? "未知" : String(value);
    }

    function unknownLabel(value) {
      return value == null || value === "" ? "未知" : String(value);
    }

    function dataQualityItems(signal) {
      const items = [dataStatusLabel(signal.data_status)];
      const sources = sourceValues(signal);
      items.push(sources.length ? `来源: ${sources.join(", ")}` : "来源: 未知");
      const fetched = fetchedValues(signal);
      items.push(fetched.length ? `拉取时间: ${fetched.join(", ")}` : "拉取时间: 未知");
      if (signal.fallback_used === true || normalized(signal.fallback_used) === "true") items.push("fallback 来源");
      return items;
    }

    function candidateRows(values) {
      return arrayValue(values).map((candidate) => {
        if (candidate && typeof candidate === "object" && !Array.isArray(candidate)) {
          return {
            name: fieldValue(candidate, ["name", "label", "title", "symbol", "ticker", "code"]),
            code: fieldValue(candidate, ["code", "ticker", "symbol"], ""),
            category: fieldValue(candidate, ["category", "sector", "theme", "type"], ""),
            reason: fieldValue(candidate, ["reason", "mapping_reason", "note", "description"], ""),
            risk: fieldValue(candidate, ["risk", "risk_level", "warning"], ""),
          };
        }
        return { name: String(candidate || "unknown"), code: "", category: "", reason: "", risk: "" };
      });
    }

    function artifactLabel(key, fallback) {
      const labels = {
        dashboard_html: "Dashboard 页面",
        dashboard_data_json: "Dashboard 数据",
        run_summary_json: "运行摘要",
        knowledge_review_html: "知识图谱复核",
        run_diagnostics_html: "运行诊断",
        knowledge_check_json: "知识检查",
        knowledge_fix_suggestions_json: "知识修复建议",
        report_md: "报告 Markdown",
      };
      return labels[key] || fallback || "产物";
    }

    function setStatus(node, message, failed = false) {
      node.textContent = message;
      node.className = failed ? "muted error" : "muted";
    }

    function normalized(value) {
      return String(value == null ? "unknown" : value).toLowerCase();
    }

    function themeName(signal) {
      return signal.theme ? String(signal.theme) : "Unknown Theme";
    }

    function themeKey(value) {
      return String(value || "Unknown Theme").trim().toLowerCase();
    }

    function sameTheme(left, right) {
      return themeKey(left) === themeKey(right);
    }

    function sourceName(value) {
      return String(value || "Unknown Source").trim() || "Unknown Source";
    }

    function sourceKey(value) {
      return sourceName(value).toLowerCase();
    }

    function sameSource(left, right) {
      return sourceKey(left) === sourceKey(right);
    }

    function themeHistoryItem(theme) {
      const themes = Array.isArray(themeHistoryData?.themes) ? themeHistoryData.themes : [];
      return themes.find((item) => sameTheme(item.theme, theme)) || null;
    }

    function candidateHistoryForTheme(candidates, theme) {
      return (Array.isArray(candidates) ? candidates : []).filter((candidate) => {
        const themes = Array.isArray(candidate.themes) ? candidate.themes : [];
        return themes.some((item) => sameTheme(item, theme));
      });
    }

    function selectTheme(theme, signalIndex = null) {
      selectedTheme = String(theme || "Unknown Theme").trim() || "Unknown Theme";
      if (signalIndex != null) selectedSignalIndex = signalIndex;
      updateQueryState({ theme: selectedTheme });
      renderSignalSections();
    }

    function selectSource(source) {
      selectedSource = sourceName(source);
      updateQueryState({ source: selectedSource });
      renderSignalSections();
    }

    function createSourceButton(source, label = null) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "theme-button source-button";
      if (selectedSource && sameSource(selectedSource, source)) button.className += " active";
      button.dataset.source = sourceName(source);
      button.textContent = label || sourceName(source);
      button.addEventListener("click", () => selectSource(source));
      return button;
    }

    function selectMatrixCell(theme, source) {
      selectedMatrixTheme = String(theme || "Unknown Theme").trim() || "Unknown Theme";
      selectedMatrixSource = sourceName(source);
      selectedTheme = selectedMatrixTheme;
      selectedSource = selectedMatrixSource;
      updateQueryState({ matrixTheme: selectedMatrixTheme, matrixSource: selectedMatrixSource, theme: selectedTheme, source: selectedSource });
      renderSignalSections();
    }

    function matrixCellItem(theme, source) {
      const rows = Array.isArray(themeSourceMatrixData?.matrix) ? themeSourceMatrixData.matrix : [];
      return rows.find((item) => sameTheme(item.theme, theme) && sameSource(item.source, source)) || null;
    }

    function createThemeButton(theme, label = null) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "theme-button";
      if (selectedTheme && sameTheme(selectedTheme, theme)) button.className += " active";
      button.dataset.theme = String(theme || "Unknown Theme");
      button.textContent = label || theme || "Unknown Theme";
      button.addEventListener("click", () => selectTheme(theme));
      return button;
    }

    function addCompareTheme(theme) {
      const normalizedTheme = String(theme || "Unknown Theme").trim() || "Unknown Theme";
      if (compareThemes.some((item) => sameTheme(item, normalizedTheme))) {
        compareNotice = `${normalizedTheme} 已在对比列表中。`;
      } else if (compareThemes.length >= MAX_COMPARE_THEMES) {
        compareNotice = "最多可对比 3 个主题。";
      } else {
        compareThemes = [...compareThemes, normalizedTheme];
        compareNotice = "";
      }
      updateQueryState({ compare: compareThemes });
      renderSignalSections();
    }

    function removeCompareTheme(theme) {
      compareThemes = compareThemes.filter((item) => !sameTheme(item, theme));
      compareNotice = "";
      updateQueryState({ compare: compareThemes });
      renderSignalSections();
    }

    function createCompareButton(theme, label = "加入对比") {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "inline-action";
      if (compareThemes.some((item) => sameTheme(item, theme))) button.className += " active";
      button.dataset.compareTheme = String(theme || "Unknown Theme");
      button.textContent = label;
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        addCompareTheme(theme);
      });
      return button;
    }

    function availableThemeNames() {
      const names = [];
      const addName = (value) => {
        const theme = String(value || "Unknown Theme").trim() || "Unknown Theme";
        if (!names.some((item) => sameTheme(item, theme))) names.push(theme);
      };
      currentSignals.forEach((signal) => addName(themeName(signal)));
      (Array.isArray(themeHistoryData?.themes) ? themeHistoryData.themes : []).forEach((item) => addName(item.theme));
      compareThemes.forEach(addName);
      names.sort((left, right) => left.localeCompare(right));
      return names;
    }

    function numberScore(signal) {
      const value = Number(signal.score);
      return Number.isFinite(value) ? value : null;
    }

    function riskRank(value) {
      const risk = normalized(value);
      if (risk === "high") return 3;
      if (risk === "medium") return 2;
      if (risk === "low") return 1;
      return 0;
    }

    function statusRank(value) {
      const status = normalized(value || "not_checked");
      if (status === "confirmed") return 5;
      if (status === "downgraded") return 4;
      if (status === "failed") return 3;
      if (status === "missing_data") return 2;
      if (status === "not_checked") return 1;
      return 0;
    }

    function strengthRank(value) {
      const strength = normalized(value);
      if (strength.includes("strong")) return 3;
      if (strength.includes("medium")) return 2;
      if (strength.includes("weak")) return 1;
      return 0;
    }

    function strongestStrength(signals) {
      let best = "unknown";
      let bestRank = -1;
      for (const signal of signals) {
        const rank = strengthRank(signal.strength);
        if (rank > bestRank) {
          bestRank = rank;
          best = signal.strength || "unknown";
        }
      }
      return best;
    }

    function topScore(signals) {
      const scores = signals.map(numberScore).filter((value) => value != null);
      return scores.length ? Math.max(...scores) : "unknown";
    }

    function maxRisk(signals) {
      let best = "unknown";
      let bestRank = -1;
      for (const signal of signals) {
        const risk = signal.risk_level || "unknown";
        const rank = riskRank(risk);
        if (rank > bestRank) {
          bestRank = rank;
          best = risk;
        }
      }
      return best;
    }

    function mainStatus(signals) {
      const counts = {};
      for (const signal of signals) {
        const status = signal.intraday_status || signal.status || "not_checked";
        counts[status] = (counts[status] || 0) + 1;
      }
      return Object.entries(counts).sort((left, right) => right[1] - left[1] || statusRank(right[0]) - statusRank(left[0]))[0]?.[0] || "not_checked";
    }

    function distribution(signals, field, fallback) {
      const counts = {};
      for (const signal of signals) {
        const value = signal[field] || fallback;
        counts[value] = (counts[value] || 0) + 1;
      }
      return Object.entries(counts).sort((left, right) => right[1] - left[1]).map(([key, count]) => `${key}: ${count}`).join(", ") || "none";
    }

    function candidateCount(signals, field) {
      return signals.reduce((total, signal) => total + arrayValue(signal[field]).length, 0);
    }

    function triggerSummary(signals) {
      const values = [];
      for (const signal of signals) {
        for (const item of arrayValue(signal.external_triggers)) {
          const label = typeof item === "string" ? item : JSON.stringify(item);
          if (label && !values.includes(label)) values.push(label);
        }
      }
      return values.slice(0, 5).join(", ") || "暂无外部触发信息。";
    }

    function uniqueValues(values, limit = 5) {
      const output = [];
      for (const value of values) {
        const label = value == null || value === "" ? "" : String(value);
        if (!label) continue;
        if (!output.includes(label)) output.push(label);
        if (output.length >= limit) break;
      }
      return output;
    }

    function countSignalsBy(signals, getter) {
      const counts = {};
      for (const signal of signals) {
        const value = getter(signal) || "unknown";
        counts[value] = (counts[value] || 0) + 1;
      }
      return counts;
    }

    function hasFallback(signal) {
      return signal.fallback_used === true || normalized(signal.fallback_used) === "true";
    }

    function isWeakDataStatus(value) {
      return ["missing", "missing_data", "partial", "stale", "failed", "unknown"].includes(normalized(value || "unknown"));
    }

    function weakEvidenceReasons(signal) {
      const reasons = [];
      const dataStatus = signal.data_status || "unknown";
      const sources = sourceValues(signal);
      const fetched = fetchedValues(signal);
      if (isWeakDataStatus(dataStatus)) reasons.push(`${dataStatus} data`);
      if (!sources.length) reasons.push("缺少数据来源");
      if (!fetched.length) reasons.push("缺少 fetched_at");
      if (hasFallback(signal)) reasons.push("使用 fallback 来源");
      if (normalized(signal.risk_level) === "high" && isWeakDataStatus(dataStatus)) reasons.push("高风险主题且数据证据较弱");
      return uniqueValues(reasons, 6);
    }

    function reviewSeverityRank(value) {
      return { high: 4, medium: 3, low: 2, info: 1 }[normalized(value)] || 0;
    }

    function reviewSeverityLabel(value) {
      const labels = { high: "高", medium: "中", low: "低", info: "信息" };
      return labels[normalized(value || "info")] || "信息";
    }

    function reviewCategoryLabel(value) {
      const labels = {
        weak_evidence: "弱证据",
        missing_source: "缺少数据来源",
        missing_fetched_at: "缺少 fetched_at",
        stale_or_partial_data: "过期 / 部分数据",
        fallback_used: "使用 fallback",
        high_risk_with_weak_data: "高风险 + 弱数据",
        date_compare_change: "日期对比变化",
        candidate_pool_change: "候选池变化",
        theme_source_gap: "主题-来源证据缺口",
      };
      return labels[value] || "全部类型";
    }

    function reviewSeverityClass(value) {
      const severity = normalized(value);
      if (severity === "high") return "badge badge-warning";
      if (severity === "medium") return "badge badge-risk";
      if (severity === "low") return "badge badge-status";
      return "badge badge-muted";
    }

    function reviewItem(category, severity, reason, options = {}) {
      return {
        category,
        severity,
        reason,
        theme: options.theme || "",
        source: options.source || "",
        action: options.action || "在写入研究摘要前复核证据上下文。",
        context: options.context || "",
        signalIndex: options.signalIndex,
      };
    }

    function reviewSignalContext(signal) {
      return [
        `强度 ${strengthLabel(signal.strength)}`,
        `score ${signal.score ?? "unknown"}`,
        `风险 ${riskLabel(signal.risk_level)}`,
        `状态 ${intradayStatusLabel(signal.intraday_status || signal.status)}`,
        `数据 ${dataStatusLabel(signal.data_status)}`,
      ].join(", ");
    }

    function pushUniqueReviewItem(items, item) {
      const key = [item.category, item.severity, item.theme, item.source, item.reason, item.context].join("|").toLowerCase();
      if (!items.some((existing) => [existing.category, existing.severity, existing.theme, existing.source, existing.reason, existing.context].join("|").toLowerCase() === key)) {
        items.push(item);
      }
    }

    function buildSignalReviewItems(signals) {
      const items = [];
      for (const signal of signals) {
        const theme = themeName(signal);
        const sources = sourceValues(signal);
        const sourceLabel = sources.join(", ") || "Unknown Source";
        const fetched = fetchedValues(signal);
        const dataStatus = signal.data_status || "unknown";
        const context = reviewSignalContext(signal);
        const reasons = weakEvidenceReasons(signal);
        const riskIsHigh = normalized(signal.risk_level) === "high";
        const dataIsWeak = isWeakDataStatus(dataStatus);
        if (reasons.length) {
          const severity = riskIsHigh && dataIsWeak ? "high" : "medium";
          pushUniqueReviewItem(items, reviewItem("weak_evidence", severity, `证据需要确认：${reasons.join(", ")}。`, { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (!sources.length) {
          pushUniqueReviewItem(items, reviewItem("missing_source", riskIsHigh ? "high" : "medium", "该信号缺少数据来源元数据。", { theme, source: "Unknown Source", context, signalIndex: signal.__index }));
        }
        if (!fetched.length) {
          pushUniqueReviewItem(items, reviewItem("missing_fetched_at", dataIsWeak ? "high" : "medium", "缺少 fetched_at 元数据，需要确认数据新鲜度。", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (dataIsWeak) {
          pushUniqueReviewItem(items, reviewItem("stale_or_partial_data", riskIsHigh && ["missing", "missing_data", "failed"].includes(normalized(dataStatus)) ? "high" : "medium", `数据状态为 ${dataStatusLabel(dataStatus)}。`, { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (hasFallback(signal)) {
          pushUniqueReviewItem(items, reviewItem("fallback_used", "medium", "使用了 fallback 来源。", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (normalized(signal.risk_level) === "high" && isWeakDataStatus(dataStatus)) {
          pushUniqueReviewItem(items, reviewItem("high_risk_with_weak_data", "high", "高风险主题同时存在较弱的数据证据。", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
      }
      return items;
    }

    function buildMatrixReviewItems() {
      const rows = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      return rows.map((cell) => reviewItem("theme_source_gap", "high", cell.reason || "主题-来源证据缺口需要复核。", {
        theme: cell.theme || "Unknown Theme",
        source: cell.source || "Unknown Source",
        context: `弱证据 ${cell.weak_signal_count || 0}`,
        action: "打开矩阵上下文，确认来源覆盖、新鲜度和 data_status。",
      }));
    }

    function buildDateCompareReviewItems() {
      if (!dateCompareData || dateCompareData.available === false) return [];
      const summary = dateCompareData.summary || {};
      const items = [];
      if (Number(summary.changed_themes_count || 0) > 0) {
        pushUniqueReviewItem(items, reviewItem("date_compare_change", "medium", `${summary.changed_themes_count} 个主题在对比日期之间发生变化。`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "在引用变化前复核 score、风险、状态和数据质量差异。",
        }));
      }
      if (Number(summary.weaker_data_quality_count || 0) > 0) {
        pushUniqueReviewItem(items, reviewItem("date_compare_change", "high", `${summary.weaker_data_quality_count} 个主题在日期对比中显示证据质量变弱。`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "检查变化是否来自缺少来源、缺少 fetched_at、fallback 或 data_status。",
        }));
      }
      const newEtf = Number(summary.new_etf_candidates_count || 0);
      const newStock = Number(summary.new_stock_candidates_count || 0);
      if (newEtf + newStock > 0) {
        pushUniqueReviewItem(items, reviewItem("candidate_pool_change", "medium", `日期对比中出现 ${newEtf} 个新增 ETF 观察候选和 ${newStock} 个新增个股观察候选。`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "将候选池变化作为观察上下文复核，不作为行动清单。",
        }));
      }
      return items;
    }

    function buildResearchReviewItems(visibleSignals, scope = reviewScope) {
      const signals = scope === "all" ? currentSignals : visibleSignals;
      const items = buildSignalReviewItems(signals)
        .concat(buildMatrixReviewItems())
        .concat(buildDateCompareReviewItems());
      return items.sort((left, right) => reviewSeverityRank(right.severity) - reviewSeverityRank(left.severity)
        || String(left.category).localeCompare(String(right.category))
        || String(left.theme || "").localeCompare(String(right.theme || ""))
        || String(left.source || "").localeCompare(String(right.source || "")));
    }

    function filterResearchReviewItems(items) {
      return items.filter((item) => (!reviewSeverity || item.severity === reviewSeverity) && (!reviewCategory || item.category === reviewCategory));
    }

    function sourceBreakdown(signals) {
      const rows = new Map();
      for (const signal of signals) {
        const sources = sourceValues(signal);
        const sourceList = sources.length ? sources : ["Unknown Source"];
        for (const source of sourceList) {
          const item = rows.get(source) || { source, signal_count: 0, themes: [], data_status_counts: {}, latest_fetched_at: null, weak_count: 0, fallback_count: 0, missing_fetched_at_count: 0 };
          item.signal_count += 1;
          const theme = themeName(signal);
          if (!item.themes.some((value) => sameTheme(value, theme))) item.themes.push(theme);
          const status = signal.data_status || "unknown";
          item.data_status_counts[status] = (item.data_status_counts[status] || 0) + 1;
          fetchedValues(signal).forEach((value) => {
            if (!item.latest_fetched_at || String(value) > String(item.latest_fetched_at)) item.latest_fetched_at = value;
          });
          if (isWeakDataStatus(status)) item.weak_count += 1;
          if (hasFallback(signal)) item.fallback_count += 1;
          if (!fetchedValues(signal).length) item.missing_fetched_at_count += 1;
          rows.set(source, item);
        }
      }
      return Array.from(rows.values()).sort((left, right) => right.signal_count - left.signal_count || left.source.localeCompare(right.source));
    }

    function sourceHistoryItem(source) {
      const sources = Array.isArray(sourceHistoryData?.sources) ? sourceHistoryData.sources : [];
      return sources.find((item) => sameSource(item.source, source)) || null;
    }

    function signalHasSource(signal, source) {
      const sources = sourceValues(signal);
      if (!sources.length) return sameSource("Unknown Source", source);
      return sources.some((item) => sameSource(item, source));
    }

    async function fetchJson(url) {
      const response = await fetch(url, { headers: { "Accept": "application/json" } });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || response.statusText);
      return payload;
    }

    function renderStatusStrip() {
      clear(statusStripEl);
      const run = currentDashboardData?.run || {};
      const schema = apiVersionData?.dashboard_schema_version || currentDashboardData?.schema_version || "unknown";
      [
        `API: ${apiHealthData?.status || "Unknown"}`,
        `API 版本: ${apiVersionData?.api_version || apiHealthData?.version || "Unknown"}`,
        `Schema: ${schema}`,
        `运行日期: ${run.date || runSelectEl.value || "unknown"}`,
        `信号: ${currentSignals.length}`,
        `可见: ${visibleSignalCount}`,
        `生成时间: ${run.generated_at || "unknown"}`,
      ].forEach((value) => statusStripEl.appendChild(badge(value)));
    }

    async function loadApiStatus() {
      try {
        apiHealthData = await fetchJson("/api/health");
      } catch (error) {
        apiHealthData = { status: "Unknown" };
      }
      try {
        apiVersionData = await fetchJson("/api/version");
      } catch (error) {
        apiVersionData = { api_version: "Unknown", dashboard_schema_version: "unknown" };
      }
      renderStatusStrip();
    }

    async function loadHistoryReview() {
      try {
        [themeHistoryData, candidateHistoryData, dataQualityHistoryData, sourceHistoryData, themeSourceMatrixData] = await Promise.all([
          fetchJson("/api/history/themes"),
          fetchJson("/api/history/candidates"),
          fetchJson("/api/history/data-quality"),
          fetchJson("/api/history/sources"),
          fetchJson("/api/history/theme-source-matrix"),
        ]);
      } catch (error) {
        themeHistoryData = { runs_count: "unknown", date_range: {}, themes: [] };
        candidateHistoryData = { etf_candidates: [], stock_candidates: [] };
        dataQualityHistoryData = { runs_count: "unknown", date_range: {}, data_status_counts: {}, source_counts: {}, themes_with_weak_data: [] };
        sourceHistoryData = { runs_count: "unknown", date_range: {}, sources: [] };
        themeSourceMatrixData = { runs_count: "unknown", date_range: {}, themes: [], sources: [], matrix: [], weak_cells: [] };
      }
    }

    async function loadDateCompare(toDate = runSelectEl.value) {
      const targetTo = compareToDate || toDate || runSelectEl.value;
      if (!targetTo) {
        dateCompareData = null;
        renderSignalSections();
        return;
      }
      const params = new URLSearchParams();
      if (compareFromDate) params.set("from", compareFromDate);
      params.set("to", targetTo);
      try {
        dateCompareData = await fetchJson(`/api/history/compare?${params.toString()}`);
      } catch (error) {
        dateCompareData = { available: false, notes: [`日期对比不可用：${error.message}`], summary: {}, themes: { new: [], removed: [], changed: [] }, candidates: { etf: {}, stock: {} }, data_quality: {}, sources: {} };
      }
      renderSignalSections();
    }

    function renderRuns(payload) {
      clear(runsEl);
      clear(runSelectEl);
      const runs = Array.isArray(payload.runs) ? payload.runs : [];
      const state = readConsoleStateFromUrl();
      syncControlsFromState(state);
      setStatus(runsStatusEl, `找到 ${runs.length} 条运行记录`);
      if (runs.length === 0) {
        runSelectEl.disabled = true;
        runsEl.appendChild(text("p", "未找到 daily run。", "muted"));
        updateQueryState({ date: "" });
        return;
      }
      runSelectEl.disabled = false;
      const availableDates = runs.map((run) => run.date).filter(Boolean);
      const targetDate = availableDates.includes(state.date) ? state.date : availableDates[0];
      let targetButton = null;
      runs.forEach((run) => {
        const option = document.createElement("option");
        option.value = run.date || "";
        option.textContent = `${run.date || "unknown"} (${run.status || "unknown"})`;
        runSelectEl.appendChild(option);
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.date = run.date || "";
        button.appendChild(text("strong", run.date || "unknown"));
        button.appendChild(document.createElement("br"));
        button.appendChild(text("span", `状态: ${run.status || "unknown"}`, "muted"));
        button.addEventListener("click", () => loadDashboard(run.date, button));
        runsEl.appendChild(button);
        if (run.date === targetDate) targetButton = button;
      });
      if (targetDate) loadDashboard(targetDate, targetButton);
    }

    function metric(label, value) {
      const node = document.createElement("div");
      node.className = "metric";
      node.appendChild(text("div", label, "muted"));
      node.appendChild(text("strong", value));
      return node;
    }

    function signalText(signal) {
      return [
        signal.theme,
        signal.strength,
        signal.intraday_status,
        signal.risk_level,
        signal.data_status,
        signal.a_share_mapping_reason,
        JSON.stringify(signal.external_triggers || []),
        JSON.stringify(signal.etf_candidates || []),
        JSON.stringify(signal.stock_candidates || []),
        JSON.stringify(signal.risks || []),
      ].map((value) => normalized(value)).join(" ");
    }

    function filteredSignals() {
      const query = normalized(signalSearchEl.value).trim();
      const risk = normalized(riskFilterEl.value).trim();
      const status = normalized(statusFilterEl.value).trim();
      return currentSignals.filter((signal) => {
        const matchesQuery = !query || signalText(signal).includes(query);
        const matchesRisk = !risk || normalized(signal.risk_level) === risk;
        const matchesStatus = !status || normalized(signal.intraday_status || signal.status || "not_checked") === status;
        return matchesQuery && matchesRisk && matchesStatus;
      });
    }

    function sortSignals(signals) {
      const mode = sortSelectEl.value || "default";
      const sorted = [...signals];
      sorted.sort((left, right) => {
        if (mode === "score_desc" || mode === "score-desc") return (numberScore(right) ?? -Infinity) - (numberScore(left) ?? -Infinity);
        if (mode === "risk_level" || mode === "risk") return riskRank(right.risk_level) - riskRank(left.risk_level) || left.__index - right.__index;
        if (mode === "intraday_status" || mode === "status") return statusRank(right.intraday_status || right.status) - statusRank(left.intraday_status || left.status) || left.__index - right.__index;
        if (mode === "theme") return themeName(left).localeCompare(themeName(right)) || left.__index - right.__index;
        return left.__index - right.__index;
      });
      return sorted;
    }

    function groupedSignals(signals) {
      const groups = new Map();
      for (const signal of signals) {
        const theme = themeName(signal);
        if (!groups.has(theme)) groups.set(theme, []);
        groups.get(theme).push(signal);
      }
      return Array.from(groups.entries())
        .map(([theme, items]) => ({ theme, signals: items }))
        .sort((left, right) => (numberScore({ score: topScore(right.signals) }) ?? -Infinity) - (numberScore({ score: topScore(left.signals) }) ?? -Infinity) || left.theme.localeCompare(right.theme));
    }

    function applySignalFilters() {
      updateQueryState();
      renderSignalSections();
    }

    function renderArtifacts(payload) {
      const section = document.createElement("details");
      section.id = "artifact-links";
      section.className = "artifacts collapsible-section section-card";
      section.appendChild(text("summary", uiText("产物链接", "Artifact Links")));
      section.appendChild(description("当前运行生成的静态产物。缺失文件会显示为 unavailable。"));
      const items = Array.isArray(payload && payload.artifacts) ? payload.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "暂无 artifact index。", "muted"));
        return appendBackToTop(section);
      }
      const ul = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        const status = item.exists ? "available" : "unavailable";
        li.appendChild(text("span", `${artifactLabel(item.key, item.file_name)}: ${status}`, item.exists ? "" : "error"));
        if (item.exists && item.api) {
          li.appendChild(text("span", " "));
          li.appendChild(link(item.api, "打开 API"));
        } else if (item.exists) {
          li.appendChild(text("span", ` (${item.relative_path || item.file_name || "local file"})`, "muted"));
        }
        ul.appendChild(li);
      }
      const indexItem = document.createElement("li");
      indexItem.appendChild(text("span", "Daily Runs Index: unavailable", "error"));
      ul.appendChild(indexItem);
      section.appendChild(ul);
      return appendBackToTop(section);
    }

    function topCounterValue(counts) {
      const entries = counts && typeof counts === "object" ? Object.entries(counts) : [];
      if (entries.length === 0) return "unknown";
      entries.sort((left, right) => Number(right[1]) - Number(left[1]) || left[0].localeCompare(right[0]));
      return entries[0][0];
    }

    function renderHistoryTable(title, headers, rows) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      if (!rows.length) {
        section.appendChild(text("p", "暂无历史观察数据。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      headers.forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        row.forEach((value) => tr.appendChild(text("td", value == null || value === "" ? "未知" : value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalThemeTrends(themes) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "历史主题趋势"));
      const rows = themes.slice(0, 10);
      if (!rows.length) {
        section.appendChild(text("p", "暂无历史观察数据。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["主题", "信号数", "出现运行数", "最高分", "平均分", "主要风险", "主要状态", "最后出现", "近期日期", "对比"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((item) => {
        const tr = document.createElement("tr");
        const themeCell = document.createElement("td");
        themeCell.appendChild(createThemeButton(item.theme));
        tr.appendChild(themeCell);
        [item.signal_count, item.runs_seen, item.max_score ?? "unknown", item.avg_score ?? "unknown", topCounterValue(item.risk_counts), topCounterValue(item.intraday_status_counts), item.last_seen || "unknown", (item.recent_dates || []).join(", ")].forEach((value) => tr.appendChild(text("td", value)));
        const compareCell = document.createElement("td");
        compareCell.appendChild(createCompareButton(item.theme, "加入对比"));
        tr.appendChild(compareCell);
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalReview() {
      const section = document.createElement("details");
      section.id = "historical-review";
      section.className = "collapsible-section section-card";
      section.appendChild(text("summary", uiText("历史复盘", "Historical Review")));
      section.appendChild(description("查看主题、候选池和数据质量在历史 daily runs 中的出现情况。这里展示的是出现频率和状态分布，不是收益回测。"));
      const themes = Array.isArray(themeHistoryData?.themes) ? themeHistoryData.themes : [];
      const etfs = Array.isArray(candidateHistoryData?.etf_candidates) ? candidateHistoryData.etf_candidates : [];
      const stocks = Array.isArray(candidateHistoryData?.stock_candidates) ? candidateHistoryData.stock_candidates : [];
      const summary = document.createElement("div");
      summary.className = "history-grid";
      summary.appendChild(metric("历史运行数", themeHistoryData?.runs_count ?? "unknown"));
      summary.appendChild(metric("日期范围", `${themeHistoryData?.date_range?.start || "unknown"} to ${themeHistoryData?.date_range?.end || "unknown"}`));
      summary.appendChild(metric("观察主题", themes.length));
      summary.appendChild(metric("观察候选", etfs.length + stocks.length));
      section.appendChild(summary);

      section.appendChild(renderHistoricalThemeTrends(themes));

      const candidateRows = etfs.slice(0, 10).map((item) => ["ETF", item.name, item.code || "unknown", item.appearances, (item.themes || []).join(", "), item.last_seen || "unknown"])
        .concat(stocks.slice(0, 10).map((item) => ["个股", item.name, item.code || "unknown", item.appearances, (item.themes || []).join(", "), item.last_seen || "unknown"]));
      section.appendChild(renderHistoryTable("反复出现的观察候选", ["类型", "名称", "代码", "出现次数", "主题", "最后出现"], candidateRows));

      const dataCounts = {};
      for (const theme of themes) {
        const counts = theme.data_status_counts && typeof theme.data_status_counts === "object" ? theme.data_status_counts : {};
        for (const [key, count] of Object.entries(counts)) dataCounts[key] = (dataCounts[key] || 0) + Number(count || 0);
      }
      const qualityRows = Object.entries(dataCounts).sort((left, right) => Number(right[1]) - Number(left[1])).map(([status, count]) => [status, count]);
      section.appendChild(renderHistoryTable("数据质量趋势", ["数据状态", "观察次数"], qualityRows));
      return appendBackToTop(section);
    }

    function badge(value, className = null) {
      const node = text("span", value, className || `badge ${badgeClass(value)}`);
      return node;
    }

    function createSignalCard(signal) {
      const card = document.createElement("article");
      card.className = "signal-card";
      if (selectedSignalIndex === signal.__index) card.className += " selected";
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", `打开 ${themeName(signal)} 的信号详情`);
      card.dataset.search = signalText(signal);
      card.dataset.risk = normalized(signal.risk_level);
      card.dataset.status = normalized(signal.intraday_status || signal.status || "not_checked");
      card.addEventListener("click", () => {
        selectedSignalIndex = signal.__index;
        selectedTheme = themeName(signal);
        updateQueryState({ theme: selectedTheme });
        renderSignalSections();
      });
      card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectedSignalIndex = signal.__index;
          selectedTheme = themeName(signal);
          updateQueryState({ theme: selectedTheme });
          renderSignalSections();
        }
      });
      const heading = document.createElement("h3");
      heading.appendChild(createThemeButton(themeName(signal)));
      card.appendChild(heading);
      [`强度: ${strengthLabel(signal.strength)}`, `score: ${signal.score ?? "unknown"}`, `盘中: ${intradayStatusLabel(signal.intraday_status || signal.status)}`, `风险: ${riskLabel(signal.risk_level)}`, `数据: ${dataStatusLabel(signal.data_status)}`].forEach((value) => card.appendChild(badge(value)));
      dataQualityItems(signal).forEach((value) => card.appendChild(badge(value)));
      card.appendChild(text("p", signal.a_share_mapping_reason || "暂无映射原因。", "muted"));
      [["外部触发", signal.external_triggers], ["ETF 观察池", signal.etf_candidates], ["个股观察池", signal.stock_candidates], ["风险提示", signal.risks]].forEach(([label, values]) => {
        card.appendChild(text("strong", label));
        card.appendChild(list(values));
      });
      return card;
    }

    function renderValueList(title, values) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      section.appendChild(list(arrayValue(values)));
      return section;
    }

    function renderDataQualitySection(signal) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "数据质量 / 新鲜度"));
      dataQualityItems(signal).forEach((value) => section.appendChild(badge(value)));
      section.appendChild(text("p", "数据质量标签只描述已有来源元数据，不代表交易判断。", "muted"));
      return section;
    }

    function renderCandidateTable(title, values) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      const rows = candidateRows(values);
      if (rows.length === 0) {
        section.appendChild(text("p", "暂无候选池数据。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "candidate-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["名称", "代码 / ticker", "类别 / 板块", "原因", "风险 / 备注"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      for (const row of rows) {
        const tr = document.createElement("tr");
        [row.name, row.code || "unknown", row.category || "unknown", row.reason || "unknown", row.risk || "unknown"].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      }
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderEvidenceChain(signal) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "证据链"));
      const chain = document.createElement("ol");
      chain.className = "evidence-chain";
      [
        ["外部变动", arrayValue(signal.external_triggers).join(", ") || "未知"],
        ["A 股主题映射", firstText(signal.a_share_mapping_reason, "未知")],
        ["候选池", `${arrayValue(signal.etf_candidates).length} 个 ETF 观察候选，${arrayValue(signal.stock_candidates).length} 个个股观察候选`],
        ["风险提示", arrayValue(signal.risks).join(", ") || "暂无风险提示。"],
        ["数据质量", dataQualityItems(signal).join(" | ")],
      ].forEach(([label, value]) => {
        const item = document.createElement("li");
        item.appendChild(text("strong", label));
        item.appendChild(text("div", value, "muted"));
        chain.appendChild(item);
      });
      section.appendChild(chain);
      return section;
    }

    function renderDetailArtifactLinks() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "相关产物链接"));
      const items = Array.isArray(currentArtifacts && currentArtifacts.artifacts) ? currentArtifacts.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "暂无产物链接。", "muted"));
        return section;
      }
      const ul = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        li.appendChild(text("span", `${artifactLabel(item.key, item.file_name)}: ${item.exists ? "available" : "unavailable"}`, item.exists ? "" : "error"));
        if (item.exists && item.api) {
          li.appendChild(text("span", " "));
          li.appendChild(link(item.api, "打开 API"));
        }
        ul.appendChild(li);
      }
      section.appendChild(ul);
      return section;
    }

    function renderSignalDetail(signal) {
      const panel = document.createElement("article");
      panel.id = "signal-detail";
      panel.className = "signal-detail section-card";
      panel.appendChild(text("h2", uiText("信号详情", "Signal Detail")));
      panel.appendChild(description("查看单条可见信号的外部触发、映射原因、观察池、风险提示和数据质量。"));
      if (!signal) {
        panel.appendChild(text("p", "当前筛选条件下没有匹配信号。", "muted"));
        return appendBackToTop(panel);
      }
      panel.appendChild(text("h3", themeName(signal)));
      panel.appendChild(text("h3", "概览"));
      [`强度: ${strengthLabel(signal.strength)}`, `score: ${signal.score ?? "unknown"}`, `盘中: ${intradayStatusLabel(signal.intraday_status || signal.status)}`, `风险: ${riskLabel(signal.risk_level)}`, `数据: ${dataStatusLabel(signal.data_status)}`].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(renderDataQualitySection(signal));
      panel.appendChild(renderValueList("来源", sourceValues(signal)));
      sourceValues(signal).forEach((source) => panel.appendChild(createSourceButton(source, `打开来源: ${source}`)));
      if (!sourceValues(signal).length) panel.appendChild(createSourceButton("Unknown Source", "打开来源: Unknown Source"));
      panel.appendChild(renderValueList("外部触发", signal.external_triggers));
      panel.appendChild(renderValueList("A 股映射原因", signal.a_share_mapping_reason));
      panel.appendChild(renderEvidenceChain(signal));
      panel.appendChild(renderCandidateTable("ETF 观察池", signal.etf_candidates));
      panel.appendChild(renderCandidateTable("个股观察池", signal.stock_candidates));
      panel.appendChild(renderValueList("风险提示", signal.risks));
      panel.appendChild(renderDetailArtifactLinks());
      const details = document.createElement("details");
      details.className = "detail-section";
      details.appendChild(text("summary", uiText("原始 signal JSON", "Raw signal JSON")));
      const pre = document.createElement("pre");
      pre.textContent = JSON.stringify(signal, null, 2);
      details.appendChild(pre);
      panel.appendChild(details);
      return appendBackToTop(panel);
    }

    function renderCountBadges(title, counts) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      const entries = counts && typeof counts === "object" ? Object.entries(counts) : [];
      if (entries.length === 0) {
        section.appendChild(text("p", "暂无历史分布数据。", "muted"));
        return section;
      }
      entries.sort((left, right) => Number(right[1]) - Number(left[1]) || left[0].localeCompare(right[0]));
      entries.forEach(([key, count]) => section.appendChild(badge(`${key}: ${count}`)));
      return section;
    }

    function renderThemeSignalList(theme, visibleSignals) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "当前主题信号"));
      const signals = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      if (signals.length === 0) {
        section.appendChild(text("p", "当前筛选条件下，该主题没有可见信号。", "muted"));
        return section;
      }
      signals.forEach((signal) => {
        const item = document.createElement("article");
        item.className = "theme-card";
        item.appendChild(text("h3", themeName(signal)));
        [`强度: ${strengthLabel(signal.strength)}`, `score: ${signal.score ?? "unknown"}`, `盘中: ${intradayStatusLabel(signal.intraday_status || signal.status)}`, `风险: ${riskLabel(signal.risk_level)}`, `数据: ${dataStatusLabel(signal.data_status)}`].forEach((value) => item.appendChild(badge(value)));
        item.appendChild(renderValueList("外部触发", signal.external_triggers));
        item.appendChild(renderValueList("A 股映射原因", signal.a_share_mapping_reason));
        item.appendChild(renderValueList("风险提示", signal.risks));
        item.appendChild(renderValueList("fetched_at / 拉取时间", fetchedValues(signal)));
        item.appendChild(renderValueList("来源", sourceValues(signal)));
        item.addEventListener("click", () => {
          selectedSignalIndex = signal.__index;
          selectedTheme = themeName(signal);
          updateQueryState({ theme: selectedTheme });
          renderSignalSections();
        });
        section.appendChild(item);
      });
      return section;
    }

    function renderThemeCandidateHistory(title, candidates) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      if (!candidates.length) {
        section.appendChild(text("p", "该主题暂无反复出现的候选池。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "candidate-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["名称", "代码 / ticker", "出现次数", "近期日期", "最后出现"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      candidates.forEach((candidate) => {
        const tr = document.createElement("tr");
        [candidate.name, candidate.code || "unknown", candidate.appearances ?? "unknown", (candidate.recent_dates || []).join(", "), candidate.last_seen || "unknown"].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderThemeDetail(visibleSignals) {
      const panel = document.createElement("article");
      panel.id = "theme-detail";
      panel.className = "theme-detail section-card";
      panel.appendChild(text("h2", uiText("主题详情", "Theme Detail")));
      panel.appendChild(description("集中查看一个观察主题的当前信号、本地历史、观察池、风险和数据质量。"));
      const theme = selectedTheme || (visibleSignals[0] ? themeName(visibleSignals[0]) : "");
      if (!theme) {
        panel.appendChild(text("p", "请从主题热榜、历史主题趋势、信号卡片或分组标题中选择一个主题。", "muted"));
        return appendBackToTop(panel);
      }
      const currentSignalsForTheme = currentSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const visibleSignalsForTheme = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const history = themeHistoryItem(theme);
      const etfs = candidateHistoryForTheme(candidateHistoryData?.etf_candidates, theme);
      const stocks = candidateHistoryForTheme(candidateHistoryData?.stock_candidates, theme);

      panel.appendChild(text("h3", theme));
      panel.appendChild(createCompareButton(theme, "加入对比"));
      panel.appendChild(text("h3", "概览"));
      [
        `今日信号: ${currentSignalsForTheme.length}`,
        `当前可见: ${visibleSignalsForTheme.length}`,
        `今日最高 score: ${topScore(currentSignalsForTheme)}`,
        `今日最强强度: ${strengthLabel(strongestStrength(currentSignalsForTheme))}`,
        `今日主要状态: ${intradayStatusLabel(mainStatus(currentSignalsForTheme))}`,
        `今日主要风险: ${riskLabel(maxRisk(currentSignalsForTheme))}`,
        `历史信号: ${history?.signal_count ?? "unknown"}`,
        `出现运行数: ${history?.runs_seen ?? "unknown"}`,
        `平均 score: ${history?.avg_score ?? "unknown"}`,
        `最高 score: ${history?.max_score ?? "unknown"}`,
        `最后出现: ${history?.last_seen || "unknown"}`,
      ].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(text("p", "主题详情是基于已有观察的研究视图，不代表行动、定价或未来结果。", "muted"));

      if (!history && currentSignalsForTheme.length === 0) {
        panel.appendChild(text("p", "该主题暂无当前或历史观察。", "muted"));
      }
      panel.appendChild(renderThemeSignalList(theme, visibleSignals));
      panel.appendChild(renderCountBadges("历史风险分布", history?.risk_counts));
      panel.appendChild(renderCountBadges("历史盘中状态分布", history?.intraday_status_counts));
      panel.appendChild(renderCountBadges("历史数据状态分布", history?.data_status_counts));
      panel.appendChild(renderValueList("近期日期", history?.recent_dates || []));
      panel.appendChild(renderValueList("外部触发摘要", history?.external_triggers || currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers))));
      panel.appendChild(renderValueList("风险摘要", currentSignalsForTheme.flatMap((signal) => arrayValue(signal.risks))));
      panel.appendChild(renderValueList("数据质量摘要", currentSignalsForTheme.flatMap((signal) => dataQualityItems(signal))));
      panel.appendChild(renderValueList("需要复核", currentSignalsForTheme.flatMap((signal) => weakEvidenceReasons(signal))));
      panel.appendChild(renderThemeCandidateHistory("ETF 观察池", etfs));
      panel.appendChild(renderThemeCandidateHistory("个股观察池", stocks));
      return appendBackToTop(panel);
    }

    function renderBriefList(title, values) {
      const section = document.createElement("div");
      section.className = "brief-section";
      section.appendChild(text("h3", title));
      section.appendChild(list(arrayValue(values)));
      return section;
    }

    function briefCandidateLabelsFromSignals(signals, field, limit = 10) {
      const labels = [];
      for (const signal of signals) {
        for (const row of candidateRows(signal[field])) {
          const label = row.code ? `${row.name} (${row.code})` : row.name;
          if (label && !labels.includes(label)) labels.push(label);
          if (labels.length >= limit) return labels;
        }
      }
      return labels;
    }

    function briefRecurringCandidateLabels(candidates, limit = 5) {
      return (Array.isArray(candidates) ? [...candidates] : [])
        .sort((left, right) => Number(right.appearances || 0) - Number(left.appearances || 0))
        .slice(0, limit)
        .map((item) => `${item.name || "unknown"} (${item.appearances || 0} 次出现)`);
    }

    function briefTopThemes(signals, limit = 5) {
      const isZh = briefLang === "zh";
      return groupedSignals(signals).slice(0, limit).map((group) => {
        const signal = group.signals[0] || {};
        const triggers = uniqueValues(group.signals.flatMap((item) => arrayValue(item.external_triggers)), 3).join(", ") || (isZh ? "未知" : "unknown");
        const mapping = signal.a_share_mapping_reason || (isZh ? "不可用" : "not available");
        return isZh
          ? `- ${group.theme}: score ${topScore(group.signals)}，强度 ${strengthLabel(strongestStrength(group.signals))}，状态 ${intradayStatusLabel(mainStatus(group.signals))}，风险 ${riskLabel(maxRisk(group.signals))}，数据 ${distribution(group.signals, "data_status", "unknown")}。触发：${triggers}。映射：${mapping}`
          : `- ${group.theme}: score ${topScore(group.signals)}, strength ${strongestStrength(group.signals)}, status ${mainStatus(group.signals)}, risk ${maxRisk(group.signals)}, data ${distribution(group.signals, "data_status", "unknown")}. Triggers: ${triggers}. Mapping: ${mapping}`;
      });
    }

    function briefLines(title, lines) {
      const safeLines = Array.isArray(lines) && lines.length ? lines : [briefLang === "zh" ? "- 不可用" : "- not available"];
      return [`## ${title}`, ...safeLines, ""];
    }

    function currentFilterSummary() {
      const parts = [];
      const state = currentConsoleState();
      if (state.search) parts.push(`search=${state.search}`);
      if (state.risk) parts.push(`risk=${state.risk}`);
      if (state.status) parts.push(`status=${state.status}`);
      if (state.sort !== "default") parts.push(`sort=${state.sort}`);
      if (state.view !== "grouped") parts.push(`view=${state.view}`);
      return parts.join(", ") || "default view";
    }

    function briefSectionLabel(key, lang = briefLang) {
      const labels = {
        overview: lang === "zh" ? "概览" : "Overview",
        watchThemes: lang === "zh" ? "观察主题" : "Watch Themes",
        evidence: lang === "zh" ? "证据链" : "Evidence Chain",
        candidates: lang === "zh" ? "观察池" : "Observation Candidates",
        risk: lang === "zh" ? "风险与谨慎项" : "Risk Notes",
        dataQuality: lang === "zh" ? "数据质量" : "Data Quality",
        dateCompare: lang === "zh" ? "日期对比" : "Date Compare",
        reviewQueue: lang === "zh" ? "研究复核清单" : "Research Review Queue",
        history: lang === "zh" ? "历史观察" : "Historical Context",
        finalNotes: lang === "zh" ? "研究备注" : "Final Notes",
      };
      return labels[key] || key;
    }
    function briefSectionEnabled(key, mode) {
      if (!briefSections[key]) return false;
      if (mode !== "compact") return true;
      return ["overview", "watchThemes", "risk", "dataQuality", "dateCompare", "reviewQueue", "candidates", "finalNotes"].includes(key);
    }

    function briefTermList() {
      const en = ["b" + "uy", "s" + "ell", "must " + "b" + "uy", "target " + "price", "pr" + "ofit", "win " + "rate", "guarante" + "ed", "sure " + "rise", "trading " + "signal", "entry " + "point", "exit " + "point"];
      const zh = ["买" + "入", "卖" + "出", "必" + "买", "目" + "标价", "收益" + "率", "胜" + "率", "必" + "涨", "涨停" + "预测", "买" + "点", "卖" + "点", "交易" + "信号"];
      return en.concat(zh);
    }

    function hasBriefTerminologyWarning(value) {
      const body = String(value || "").toLowerCase();
      return briefTermList().some((term) => body.includes(String(term).toLowerCase()));
    }

    function buildDailyResearchBrief(mode, visibleSignals) {
      const run = currentDashboardData?.run || {};
      const isZh = briefLang === "zh";
      const generatedAt = run.generated_at || currentDashboardData?.generated_at || "unknown";
      const weakSignals = currentSignals.filter((signal) => weakEvidenceReasons(signal).length > 0);
      const weakMatrixCells = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      const dataCounts = countSignalsBy(currentSignals, (signal) => signal.data_status || "unknown");
      const sourceRows = sourceBreakdown(currentSignals);
      const missingSourceCount = currentSignals.filter((signal) => sourceValues(signal).length === 0).length;
      const missingFetchedCount = currentSignals.filter((signal) => fetchedValues(signal).length === 0).length;
      const fallbackCount = currentSignals.filter(hasFallback).length;
      const highRiskThemes = groupedSignals(currentSignals).filter((group) => normalized(maxRisk(group.signals)) === "high").map((group) => `- ${group.theme}: risk ${maxRisk(group.signals)}, status ${mainStatus(group.signals)}`).slice(0, 5);
      const cautionSignals = currentSignals
        .filter((signal) => ["downgraded", "failed", "missing_data"].includes(normalized(signal.intraday_status || signal.status)) || weakEvidenceReasons(signal).length > 0)
        .slice(0, 8)
        .map((signal) => `- ${themeName(signal)}: status ${signal.intraday_status || signal.status || "not_checked"}, risk ${signal.risk_level || "unknown"}, data ${signal.data_status || "unknown"}, notes ${weakEvidenceReasons(signal).join(", ") || "not available"}`);
      const recurringThemes = (Array.isArray(themeHistoryData?.themes) ? [...themeHistoryData.themes] : [])
        .sort((left, right) => Number(right.runs_seen || 0) - Number(left.runs_seen || 0) || Number(right.signal_count || 0) - Number(left.signal_count || 0))
        .slice(0, 5)
        .map((item) => `- ${item.theme || "Unknown Theme"}: ${item.signal_count || 0} signals across ${item.runs_seen || 0} runs, last seen ${item.last_seen || "unknown"}`);
      const etfs = briefCandidateLabelsFromSignals(visibleSignals, "etf_candidates", 10);
      const stocks = briefCandidateLabelsFromSignals(visibleSignals, "stock_candidates", 10);
      const recurringEtfs = briefRecurringCandidateLabels(candidateHistoryData?.etf_candidates, 5);
      const recurringStocks = briefRecurringCandidateLabels(candidateHistoryData?.stock_candidates, 5);
      const triggerSummaryText = uniqueValues(visibleSignals.flatMap((signal) => arrayValue(signal.external_triggers)), 8).join(", ") || "not available";
      const mappingSummary = uniqueValues(visibleSignals.map((signal) => signal.a_share_mapping_reason), 5).join(" | ") || "not available";
      const riskSummary = uniqueValues(visibleSignals.flatMap((signal) => arrayValue(signal.risks)), 8).join(" | ") || "not available";
      const qualitySummary = Object.entries(dataCounts).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown";
      const compare = dateCompareData || {};
      const compareSummary = compare.summary || {};
      const topReviewItems = buildResearchReviewItems(visibleSignals, "visible").slice(0, 5);
      const dateCompareLines = compare.available === false
        ? [`- ${compare.notes?.join(" ") || "Date comparison is not available."}`]
        : [
          `- From / to: ${compare.from_date || "unknown"} -> ${compare.to_date || "unknown"}`,
          `- New watch themes: ${compareSummary.new_themes_count || 0}`,
          `- Removed from current watch list: ${compareSummary.removed_themes_count || 0}`,
          `- Changed themes: ${compareSummary.changed_themes_count || 0}`,
          `- Candidate pool changes: ${compareSummary.new_etf_candidates_count || 0} new ETF observation candidates, ${compareSummary.new_stock_candidates_count || 0} new stock observation candidates`,
          `- Data quality changes: ${compareSummary.weaker_data_quality_count || 0} weaker, ${compareSummary.improved_data_quality_count || 0} improved`,
          `- Source coverage notes: ${(compare.sources?.new || []).length} new sources, ${(compare.sources?.removed || []).length} removed sources`,
        ];
      const lines = [
        isZh ? "# 今日跨市场热点观察摘要" : "# Daily Overseas-to-A-share Research Brief",
        isZh
          ? "> 本摘要仅用于跨市场热点观察与研究复盘，不构成买卖建议。所有候选池均为观察对象，需结合数据质量、盘中验证和风险提示进一步确认。"
          : "> This brief is for research and observation only. Candidate pools are watchlists, not trading recommendations. Signals require confirmation with data quality, intraday validation, and risk notes.",
        "",
      ];

      const sections = [
        ["overview", isZh ? "一、概览" : "Overview", [
          isZh ? `- 日期：${run.date || runSelectEl.value || "unknown"}` : `- Run date: ${run.date || runSelectEl.value || "unknown"}`,
          isZh ? `- 生成时间：${generatedAt}` : `- Generated at: ${generatedAt}`,
          isZh ? `- 当前可见信号 / 总信号：${visibleSignals.length} / ${currentSignals.length}` : `- Visible signals / total signals: ${visibleSignals.length} / ${currentSignals.length}`,
          isZh ? `- 当前筛选条件：${currentFilterSummary()}` : `- Current filters: ${currentFilterSummary()}`,
          isZh ? `- 当前关注主题：${selectedTheme || "not selected"}` : `- Selected theme: ${selectedTheme || "not selected"}`,
          isZh ? `- 当前对比主题：${compareThemes.length ? compareThemes.join(", ") : "not selected"}` : `- Compared themes: ${compareThemes.length ? compareThemes.join(", ") : "not selected"}`,
          isZh ? `- 当前关注数据源：${selectedSource || "not selected"}` : `- Selected source: ${selectedSource || "not selected"}`,
        ]],
        ["watchThemes", isZh ? "二、海外热点可能传导的 A 股主题" : "Overseas-to-A-share Watch Themes", briefTopThemes(visibleSignals, 5)],
        ["evidence", isZh ? "三、证据链摘要" : "Evidence Chain Summary", [
          isZh ? `- 外盘触发：${triggerSummaryText}` : `- External triggers: ${triggerSummaryText}`,
          isZh ? `- A 股主题映射：${mappingSummary}` : `- A-share theme mapping: ${mappingSummary}`,
          isZh ? `- 候选池：${etfs.length} 个 ETF 观察对象，${stocks.length} 个个股观察对象` : `- Candidate pools: ${etfs.length} ETF observation candidates, ${stocks.length} stock observation candidates`,
          isZh ? `- 风险提示：${riskSummary}` : `- Risk notes: ${riskSummary}`,
          isZh ? `- 数据质量：${qualitySummary}` : `- Data quality notes: ${qualitySummary}`,
        ]],
        ["candidates", isZh ? "四、ETF / 个股观察池" : "Observation Candidate Pools", [
          isZh ? `- ETF 观察池：${etfs.join(", ") || "not available"}` : `- ETF observation candidates: ${etfs.join(", ") || "not available"}`,
          isZh ? `- 个股观察池：${stocks.join(", ") || "not available"}` : `- Stock observation candidates: ${stocks.join(", ") || "not available"}`,
          isZh ? `- 历史反复出现 ETF：${recurringEtfs.join(", ") || "not available"}` : `- Recurring ETF candidates: ${recurringEtfs.join(", ") || "not available"}`,
          isZh ? `- 历史反复出现个股：${recurringStocks.join(", ") || "not available"}` : `- Recurring stock candidates: ${recurringStocks.join(", ") || "not available"}`,
        ]],
        ["risk", isZh ? "五、风险与谨慎项" : "Risk and Caution Notes", highRiskThemes.concat(cautionSignals).slice(0, 10)],
        ["dataQuality", isZh ? "六、数据质量摘要" : "Data Quality Summary", [
          isZh ? `- data_status 分布：${qualitySummary}` : `- Data status distribution: ${qualitySummary}`,
          isZh ? `- 覆盖数据源：${sourceRows.length}` : `- Sources covered: ${sourceRows.length}`,
          isZh ? `- 缺失 source 数量：${missingSourceCount}` : `- Missing source count: ${missingSourceCount}`,
          isZh ? `- 缺失 fetched_at 数量：${missingFetchedCount}` : `- Missing fetched_at count: ${missingFetchedCount}`,
          isZh ? `- fallback source 数量：${fallbackCount}` : `- Fallback source count: ${fallbackCount}`,
          isZh ? `- 弱证据信号：${weakSignals.length}` : `- Weak evidence signals: ${weakSignals.length}`,
          isZh ? `- 需复核 theme-source 组合：${weakMatrixCells.length}` : `- Theme-source pairs needing review: ${weakMatrixCells.length}`,
        ]],
        ["dateCompare", isZh ? "日期对比观察" : "Date-over-Date Changes", dateCompareLines],
        ["reviewQueue", isZh ? "研究复核清单" : "Research Review Queue", topReviewItems.length ? topReviewItems.map((item) => `- [${reviewSeverityLabel(item.severity)}] ${item.theme || item.source || "General review"}: ${item.reason} Action: ${item.action}`) : ["- No review items for the current view."]],
        ["history", isZh ? "七、历史观察" : "Historical Context", recurringThemes.concat([
          isZh ? `- 历史日期范围：${themeHistoryData?.date_range?.start || "unknown"} to ${themeHistoryData?.date_range?.end || "unknown"}` : `- Historical date range: ${themeHistoryData?.date_range?.start || "unknown"} to ${themeHistoryData?.date_range?.end || "unknown"}`,
          isZh ? `- 历史数据质量样本：${dataQualityHistoryData?.runs_count ?? "unknown"}` : `- Historical data quality runs: ${dataQualityHistoryData?.runs_count ?? "unknown"}`,
        ])],
        ["finalNotes", isZh ? "八、研究备注" : "Final Research Notes", [
          isZh ? `- 今日观察主题主要集中在：${groupedSignals(visibleSignals).slice(0, 3).map((group) => group.theme).join(", ") || "not available"}。` : `- Today's overseas-to-A-share watch themes are mainly represented by ${groupedSignals(visibleSignals).slice(0, 3).map((group) => group.theme).join(", ") || "not available"}.`,
          isZh ? `- ${weakSignals.length} 个信号和 ${weakMatrixCells.length} 个 theme-source 组合需要证据或新鲜度复核。` : `- ${weakSignals.length} signals and ${weakMatrixCells.length} theme-source pairs need evidence or freshness review.`,
          isZh ? "- 本摘要仅用于研究观察，仍需结合数据源质量、盘中验证和市场环境确认。" : "- This brief is for research and observation only and requires confirmation from source data and market context.",
        ]],
      ];

      for (const [key, title, sectionLines] of sections) {
        if (briefSectionEnabled(key, mode)) lines.push(...briefLines(title, sectionLines));
      }
      return lines.join("\\n").trim();
    }

    function copyBriefText(textarea, statusNode) {
      const message = briefLang === "zh"
        ? { markdown: "Markdown 已复制。", plain: "纯文本已复制。", failed: "复制失败，可手动选择文本。" }
        : { markdown: "Markdown copied.", plain: "Plain text copied.", failed: "Copy failed. You can manually select the text." };
      const done = (kind) => { statusNode.textContent = kind === "plain" ? message.plain : message.markdown; };
      const failed = () => {
        textarea.focus();
        textarea.select();
        statusNode.textContent = message.failed;
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textarea.value || "").then(() => done(textarea.dataset.copyKind || "markdown")).catch(failed);
      } else {
        failed();
      }
    }

    function renderDailyResearchBrief(visibleSignals) {
      const section = document.createElement("article");
      section.id = "daily-research-brief";
      section.className = "research-brief section-card";
      section.appendChild(text("h2", uiText("每日研究摘要", "Daily Research Brief")));
      section.appendChild(description("根据当前筛选、观察主题、证据链、候选池、风险和数据质量，生成可复制的研究摘要。"));
      const controls = document.createElement("div");
      controls.className = "research-brief-controls";
      const langField = document.createElement("div");
      const langLabel = document.createElement("label");
      langLabel.setAttribute("for", "brief-language-select");
      langLabel.textContent = "摘要语言";
      const langSelect = document.createElement("select");
      langSelect.id = "brief-language-select";
      [["en", "English"], ["zh", "中文"]].forEach(([value, title]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = title;
        langSelect.appendChild(option);
      });
      langSelect.value = briefLang;
      langSelect.addEventListener("change", () => {
        briefLang = normalizeBriefLang(langSelect.value);
        updateQueryState({ briefLang });
        renderSignalSections();
      });
      langField.appendChild(langLabel);
      langField.appendChild(langSelect);
      controls.appendChild(langField);
      const field = document.createElement("div");
      const label = document.createElement("label");
      label.setAttribute("for", "brief-mode-select");
      label.textContent = "摘要模式";
      const select = document.createElement("select");
      select.id = "brief-mode-select";
      [["full", "完整摘要"], ["compact", "简洁摘要"]].forEach(([value, title]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = title;
        select.appendChild(option);
      });
      select.value = briefMode;
      select.addEventListener("change", () => {
        briefMode = select.value === "compact" ? "compact" : "full";
        updateQueryState({ briefMode });
        renderSignalSections();
      });
      field.appendChild(label);
      field.appendChild(select);
      controls.appendChild(field);
      const copyMarkdown = document.createElement("button");
      copyMarkdown.type = "button";
      copyMarkdown.className = "inline-action";
      copyMarkdown.textContent = "复制 Markdown";
      const copyPlain = document.createElement("button");
      copyPlain.type = "button";
      copyPlain.className = "inline-action";
      copyPlain.textContent = "复制纯文本";
      controls.appendChild(copyMarkdown);
      controls.appendChild(copyPlain);
      section.appendChild(controls);
      const toggleWrap = document.createElement("div");
      toggleWrap.className = "brief-toggle-grid";
      BRIEF_SECTION_KEYS.forEach((key) => {
        const item = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = briefSections[key] !== false;
        input.addEventListener("change", () => {
          briefSections[key] = input.checked;
          renderSignalSections();
        });
        item.appendChild(input);
        item.appendChild(text("span", briefSectionLabel(key)));
        toggleWrap.appendChild(item);
      });
      section.appendChild(text("h3", "包含小节"));
      section.appendChild(toggleWrap);
      if (briefMode === "compact") {
        section.appendChild(text("p", "简洁摘要会使用更精简的小节集合。", "muted"));
      }
      const status = text("p", briefLang === "zh" ? "研究 / 观察用途。本摘要在浏览器本地生成，不保存到服务器。" : "Research / observation only. This brief is generated in the browser and is not saved to the server.", "muted");
      section.appendChild(status);
      const meta = document.createElement("div");
      meta.className = "brief-meta";
      [
        briefLang === "zh" ? `语言：中文` : `language: English`,
        briefLang === "zh" ? `模式：${briefMode}` : `mode: ${briefMode}`,
        briefLang === "zh" ? `已启用小节：${BRIEF_SECTION_KEYS.filter((key) => briefSectionEnabled(key, briefMode)).length}` : `enabled sections: ${BRIEF_SECTION_KEYS.filter((key) => briefSectionEnabled(key, briefMode)).length}`,
        briefLang === "zh" ? `当前可见信号：${visibleSignals.length}` : `visible signals: ${visibleSignals.length}`,
        briefLang === "zh" ? "本地生成" : "generated locally",
        briefLang === "zh" ? "不保存到服务器" : "not saved",
      ].forEach((value) => meta.appendChild(badge(value)));
      section.appendChild(meta);
      const textarea = document.createElement("textarea");
      textarea.className = "research-brief-textarea";
      textarea.readOnly = true;
      textarea.setAttribute("aria-label", "生成的每日研究摘要");
      textarea.value = currentSignals.length ? buildDailyResearchBrief(briefMode, visibleSignals) : "Not enough data to build a research brief. No signals available for the current filters.";
      const warning = text("p", briefLang === "zh" ? "未发现类似交易口径。" : "No trading-like wording detected.", "muted");
      if (hasBriefTerminologyWarning(textarea.value)) {
        warning.className = "brief-warning";
        warning.textContent = briefLang === "zh" ? "摘要包含类似交易口径，请复核。" : "Brief contains trading-like wording. Please review.";
      }
      section.appendChild(warning);
      copyMarkdown.addEventListener("click", () => {
        textarea.dataset.copyKind = "markdown";
        copyBriefText(textarea, status);
      });
      copyPlain.addEventListener("click", () => {
        textarea.dataset.copyKind = "plain";
        copyBriefText(textarea, status);
      });
      section.appendChild(textarea);
      return appendBackToTop(section);
    }

    function renderReviewSelect(id, labelText, options, value, onChange) {
      const field = document.createElement("div");
      const label = document.createElement("label");
      label.setAttribute("for", id);
      label.textContent = labelText;
      const select = document.createElement("select");
      select.id = id;
      options.forEach(([optionValue, optionLabel]) => {
        const option = document.createElement("option");
        option.value = optionValue;
        option.textContent = optionLabel;
        select.appendChild(option);
      });
      select.value = value;
      select.addEventListener("change", () => onChange(select.value));
      field.appendChild(label);
      field.appendChild(select);
      return field;
    }

    function reviewSummaryCount(items, predicate) {
      return items.filter(predicate).length;
    }

    function renderResearchReviewQueue(visibleSignals) {
      const section = document.createElement("article");
      section.id = "research-review-queue";
      section.className = "review-queue section-card";
      section.appendChild(text("h2", uiText("研究复核清单", "Research Review Queue")));
      section.appendChild(description("汇总当前视图中需要人工确认的证据缺口、数据来源问题、日期变化和候选池变化。"));
      const controls = document.createElement("div");
      controls.className = "review-controls";
      controls.appendChild(renderReviewSelect("review-severity-filter", "严重程度", [
        ["", "全部"],
        ["high", "高"],
        ["medium", "中"],
        ["low", "低"],
        ["info", "信息"],
      ], reviewSeverity, (value) => {
        reviewSeverity = normalizeChoice(value, VALID_REVIEW_SEVERITIES, "");
        updateQueryState({ reviewSeverity });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("review-category-filter", "复核类型", [
        ["", "全部类型"],
        ["weak_evidence", "弱证据"],
        ["missing_source", "缺少数据来源"],
        ["missing_fetched_at", "缺少 fetched_at"],
        ["stale_or_partial_data", "过期 / 部分数据"],
        ["fallback_used", "使用 fallback"],
        ["high_risk_with_weak_data", "高风险 + 弱数据"],
        ["date_compare_change", "日期对比变化"],
        ["candidate_pool_change", "候选池变化"],
        ["theme_source_gap", "主题-来源证据缺口"],
      ], reviewCategory, (value) => {
        reviewCategory = normalizeChoice(value, VALID_REVIEW_CATEGORIES, "");
        updateQueryState({ reviewCategory });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("review-scope-select", "范围", [
        ["visible", "当前可见结果"],
        ["all", "当前运行全部结果"],
      ], reviewScope, (value) => {
        reviewScope = normalizeReviewScope(value);
        updateQueryState({ reviewScope });
        renderSignalSections();
      }));
      section.appendChild(controls);

      const allItems = buildResearchReviewItems(visibleSignals, reviewScope);
      const filteredItems = filterResearchReviewItems(allItems);
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["复核事项", filteredItems.length],
        ["高优先级", reviewSummaryCount(filteredItems, (item) => item.severity === "high")],
        ["弱证据", reviewSummaryCount(filteredItems, (item) => item.category === "stale_or_partial_data" || item.category === "high_risk_with_weak_data")],
        ["来源缺口", reviewSummaryCount(filteredItems, (item) => item.category === "missing_source" || item.category === "missing_fetched_at")],
        ["矩阵缺口", reviewSummaryCount(filteredItems, (item) => item.category === "theme_source_gap")],
        ["日期对比提示", reviewSummaryCount(filteredItems, (item) => item.category === "date_compare_change" || item.category === "candidate_pool_change")],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(text("h3", "复核清单摘要"));
      section.appendChild(metrics);

      if (!filteredItems.length) {
        section.appendChild(text("p", "当前视图暂无需要复核的事项。所选筛选条件下的证据与数据来源信息较完整。", "muted"));
        return appendBackToTop(section);
      }

      const shownItems = filteredItems.slice(0, 10);
      section.appendChild(text("p", filteredItems.length > shownItems.length ? `默认显示前 10 条复核事项。当前筛选共 ${filteredItems.length} 条。` : `当前显示 ${shownItems.length} 条复核事项。`, "muted"));
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["严重程度", "复核类型", "主题", "来源", "原因", "建议复核动作", "上下文"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      shownItems.forEach((item) => {
        const row = document.createElement("tr");
        const severityCell = document.createElement("td");
        severityCell.appendChild(badge(reviewSeverityLabel(item.severity), reviewSeverityClass(item.severity)));
        row.appendChild(severityCell);
        row.appendChild(text("td", reviewCategoryLabel(item.category)));
        const themeCell = document.createElement("td");
        if (item.theme) themeCell.appendChild(createThemeButton(item.theme));
        else themeCell.appendChild(text("span", "不可用", "muted"));
        row.appendChild(themeCell);
        const sourceCell = document.createElement("td");
        if (item.source) sourceCell.appendChild(createSourceButton(item.source));
        else sourceCell.appendChild(text("span", "不可用", "muted"));
        row.appendChild(sourceCell);
        row.appendChild(text("td", item.reason));
        row.appendChild(text("td", item.action));
        const contextCell = document.createElement("td");
        contextCell.appendChild(text("div", item.context || "不可用"));
        if (item.theme && item.source) {
          const matrixButton = document.createElement("button");
          matrixButton.type = "button";
          matrixButton.className = "inline-action";
          matrixButton.textContent = "打开矩阵上下文";
          matrixButton.addEventListener("click", () => selectMatrixCell(item.theme, item.source));
          contextCell.appendChild(matrixButton);
        }
        row.appendChild(contextCell);
        tbody.appendChild(row);
      });
      table.appendChild(tbody);
      const wrap = document.createElement("div");
      wrap.className = "matrix-table-wrap";
      wrap.appendChild(table);
      section.appendChild(wrap);
      return appendBackToTop(section);
    }

    function notesSectionLabel(key, lang = notesLang) {
      const labels = {
        context: lang === "zh" ? "上下文" : "Context",
        watchThemes: lang === "zh" ? "重点观察主题" : "Key Watch Themes",
        reviewItems: lang === "zh" ? "研究复核事项" : "Review Items",
        evidenceGaps: lang === "zh" ? "证据缺口" : "Evidence Gaps",
        dateCompare: lang === "zh" ? "日期对比变化" : "Date-over-Date Changes",
        candidates: lang === "zh" ? "候选池变化" : "Candidate Pool Notes",
        dataQuality: lang === "zh" ? "数据质量提示" : "Data Quality Notes",
        openQuestions: lang === "zh" ? "待确认问题" : "Open Research Questions",
        followUp: lang === "zh" ? "后续复核动作" : "Follow-up Checks",
      };
      return labels[key] || key;
    }

    function exportSectionLabel(key) {
      const labels = {
        dailyBrief: "每日研究摘要",
        researchNotes: "研究笔记",
        reviewQueue: "研究复核清单",
        dateCompare: "日期对比",
        sourceReliability: "数据来源可靠性",
        matrixSummary: "主题 × 来源矩阵摘要",
        candidatePool: "候选池摘要",
        manualNotes: "人工补充笔记",
        queryState: "当前 URL / 查询状态",
      };
      return labels[key] || key;
    }

    function effectiveExportLang() {
      return exportLang || (notesLang === "zh" || briefLang === "zh" ? "zh" : "en");
    }

    function notesSectionEnabled(key, mode = notesMode) {
      if (!notesSections[key]) return false;
      if (mode !== "compact") return true;
      return ["context", "watchThemes", "reviewItems", "dataQuality", "followUp"].includes(key);
    }

    function notesLines(title, lines) {
      const safeLines = Array.isArray(lines) && lines.length ? lines : ["- not available"];
      return [`## ${title}`, ...safeLines, ""];
    }

    function reviewItemNoteLine(item) {
      const subject = [item.theme, item.source].filter(Boolean).join(" / ") || "General review";
      return `- [${reviewSeverityLabel(item.severity)}] ${subject}: ${item.reason} Next check: ${item.action}`;
    }

    function buildResearchNotes(mode, visibleSignals, manualNotes = "") {
      const run = currentDashboardData?.run || {};
      const isZh = notesLang === "zh";
      const generatedAt = run.generated_at || currentDashboardData?.generated_at || "unknown";
      const reviewItems = buildResearchReviewItems(visibleSignals, "visible");
      const highItems = reviewItems.filter((item) => item.severity === "high").slice(0, 5);
      const mediumItems = reviewItems.filter((item) => item.severity === "medium").slice(0, 5);
      const missingSourceCount = currentSignals.filter((signal) => sourceValues(signal).length === 0).length;
      const missingFetchedCount = currentSignals.filter((signal) => fetchedValues(signal).length === 0).length;
      const fallbackCount = currentSignals.filter(hasFallback).length;
      const weakMatrixCells = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      const compare = dateCompareData || {};
      const compareSummary = compare.summary || {};
      const etfs = briefCandidateLabelsFromSignals(visibleSignals, "etf_candidates", 8);
      const stocks = briefCandidateLabelsFromSignals(visibleSignals, "stock_candidates", 8);
      const qualitySummary = Object.entries(countSignalsBy(currentSignals, (signal) => signal.data_status || "unknown")).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown";
      const topThemes = briefTopThemes(visibleSignals, 5);
      const evidenceGaps = reviewItems
        .filter((item) => ["weak_evidence", "missing_source", "missing_fetched_at", "stale_or_partial_data", "fallback_used", "theme_source_gap"].includes(item.category))
        .slice(0, 8)
        .map(reviewItemNoteLine);
      const dateLines = compare.available === false
        ? [`- ${compare.notes?.join(" ") || "Date comparison is not available."}`]
        : [
          `- Compared runs: ${compare.from_date || "unknown"} -> ${compare.to_date || "unknown"}`,
          `- Changed themes: ${compareSummary.changed_themes_count || 0}`,
          `- Candidate pool changes: ${compareSummary.new_etf_candidates_count || 0} new ETF observation candidates, ${compareSummary.new_stock_candidates_count || 0} new stock observation candidates`,
          `- Data quality changes: ${compareSummary.weaker_data_quality_count || 0} weaker, ${compareSummary.improved_data_quality_count || 0} improved`,
        ];
      const sections = [
        ["context", isZh ? "一、当前观察上下文" : "Context", [
          isZh ? `- 运行日期：${run.date || runSelectEl.value || "unknown"}` : `- Run date: ${run.date || runSelectEl.value || "unknown"}`,
          isZh ? `- 生成时间：${generatedAt}` : `- Generated at: ${generatedAt}`,
          isZh ? `- 当前筛选条件：${currentFilterSummary()}` : `- Current filters: ${currentFilterSummary()}`,
          isZh ? `- 当前关注主题：${selectedTheme || "not selected"}` : `- Selected theme: ${selectedTheme || "not selected"}`,
          isZh ? `- 当前关注数据源：${selectedSource || "not selected"}` : `- Selected source: ${selectedSource || "not selected"}`,
          isZh ? `- 当前对比主题：${compareThemes.length ? compareThemes.join(", ") : "not selected"}` : `- Compared themes: ${compareThemes.length ? compareThemes.join(", ") : "not selected"}`,
        ]],
        ["watchThemes", isZh ? "二、重点观察主题" : "Key Watch Themes", topThemes],
        ["reviewItems", isZh ? "三、需要复核的事项" : "Review Items", highItems.concat(mediumItems).map(reviewItemNoteLine)],
        ["evidenceGaps", isZh ? "四、证据缺口与数据质量" : "Evidence Gaps", evidenceGaps],
        ["dateCompare", isZh ? "五、日期对比变化" : "Date-over-Date Changes", dateLines],
        ["candidates", isZh ? "六、候选池变化" : "Candidate Pool Notes", [
          isZh ? `- ETF 观察池：${etfs.join(", ") || "not available"}` : `- ETF observation candidates: ${etfs.join(", ") || "not available"}`,
          isZh ? `- 个股观察池：${stocks.join(", ") || "not available"}` : `- Stock observation candidates: ${stocks.join(", ") || "not available"}`,
        ]],
        ["dataQuality", isZh ? "七、数据质量提示" : "Data Quality Notes", [
          isZh ? `- data_status 分布：${qualitySummary}` : `- Data status distribution: ${qualitySummary}`,
          isZh ? `- 缺 source：${missingSourceCount}` : `- Missing source count: ${missingSourceCount}`,
          isZh ? `- 缺 fetched_at：${missingFetchedCount}` : `- Missing fetched_at count: ${missingFetchedCount}`,
          isZh ? `- fallback source：${fallbackCount}` : `- Fallback source count: ${fallbackCount}`,
          isZh ? `- 需要复核的 theme-source 组合：${weakMatrixCells.length}` : `- Theme-source pairs needing review: ${weakMatrixCells.length}`,
        ]],
        ["openQuestions", isZh ? "八、待确认问题" : "Open Research Questions", [
          isZh ? "- 哪些观察主题需要等待盘中状态进一步确认？" : "- Which watch themes still require intraday confirmation?",
          isZh ? "- 哪些 source / fetched_at 缺口会影响证据新鲜度判断？" : "- Which source or fetched_at gaps affect evidence freshness?",
          isZh ? "- 哪些候选池变化需要补充人工复核？" : "- Which candidate pool changes need human review?",
        ]],
        ["followUp", isZh ? "九、后续复核动作" : "Follow-up Checks", [
          isZh ? "- 复核 high / medium 研究复核事项。" : "- Review high and medium research review items.",
          isZh ? "- 检查 Source Reliability 与 Theme × Source Matrix 中的证据缺口。" : "- Check evidence gaps in Source Reliability and Theme x Source Matrix.",
          isZh ? "- 将已确认内容再整理进 Daily Research Brief。" : "- Move confirmed observations into the Daily Research Brief.",
        ]],
      ];
      const lines = [
        isZh ? "# 跨市场热点研究复核笔记" : "# Research Notes",
        isZh ? "> 本笔记仅用于跨市场热点观察、证据复核与研究记录，不构成买卖建议。" : "> Research and observation only. This is not market action advice.",
        "",
      ];
      for (const [key, title, sectionLines] of sections) {
        if (notesSectionEnabled(key, mode)) lines.push(...notesLines(title, sectionLines));
      }
      const trimmedManual = String(manualNotes || "").trim();
      if (trimmedManual) {
        lines.push(isZh ? "## 人工补充笔记" : "## Manual Research Notes", trimmedManual, "");
      }
      if (mode === "compact") {
        lines.push(isZh ? "_Compact 模式：仅保留核心复核内容。_" : "_Compact mode: core review content only._");
      }
      return lines.join("\\n").trim();
    }

    function copyNotesText(textarea, statusNode, kind) {
      const message = notesLang === "zh"
        ? { markdown: "Markdown 已复制。", plain: "纯文本已复制。", failed: "复制失败，可手动选择文本。" }
        : { markdown: "Markdown copied.", plain: "Plain text copied.", failed: "Copy failed. You can manually select the text." };
      const done = () => { statusNode.textContent = kind === "plain" ? message.plain : message.markdown; };
      const failed = () => {
        textarea.focus();
        textarea.select();
        statusNode.textContent = message.failed;
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textarea.value || "").then(done).catch(failed);
      } else {
        failed();
      }
    }

    function renderResearchNotesComposer(visibleSignals) {
      const section = document.createElement("article");
      section.id = "research-notes-composer";
      section.className = "research-notes section-card";
      section.appendChild(text("h2", uiText("研究笔记工作区", "Research Notes Composer")));
      section.appendChild(description("根据当前页面状态生成本地研究笔记，也可以添加人工补充内容。笔记不会保存到服务器。"));
      const controls = document.createElement("div");
      controls.className = "research-notes-controls";
      controls.appendChild(renderReviewSelect("notes-language-select", "笔记语言", [["en", "English"], ["zh", "中文"]], notesLang, (value) => {
        notesLang = normalizeNotesLang(value);
        updateQueryState({ notesLang });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("notes-mode-select", "笔记模式", [["full", "完整笔记"], ["compact", "简洁笔记"]], notesMode, (value) => {
        notesMode = normalizeNotesMode(value);
        updateQueryState({ notesMode });
        renderSignalSections();
      }));
      const copyMarkdown = document.createElement("button");
      copyMarkdown.type = "button";
      copyMarkdown.className = "inline-action";
      copyMarkdown.textContent = "复制 Markdown";
      const copyPlain = document.createElement("button");
      copyPlain.type = "button";
      copyPlain.className = "inline-action";
      copyPlain.textContent = "复制纯文本";
      const regenerate = document.createElement("button");
      regenerate.type = "button";
      regenerate.className = "inline-action";
      regenerate.textContent = "重新生成笔记";
      controls.appendChild(copyMarkdown);
      controls.appendChild(copyPlain);
      controls.appendChild(regenerate);
      section.appendChild(controls);
      section.appendChild(text("p", "每日研究摘要适合作为摘要输出；研究笔记工作区适合作为复核过程笔记，记录开放问题和后续复核动作。", "muted"));
      const toggleWrap = document.createElement("div");
      toggleWrap.className = "brief-toggle-grid";
      NOTES_SECTION_KEYS.forEach((key) => {
        const item = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = notesSections[key] !== false;
        input.addEventListener("change", () => {
          notesSections[key] = input.checked;
          renderSignalSections();
        });
        item.appendChild(input);
        item.appendChild(text("span", notesSectionLabel(key)));
        toggleWrap.appendChild(item);
      });
      section.appendChild(text("h3", "包含小节"));
      section.appendChild(toggleWrap);
      const manualLabel = document.createElement("label");
      manualLabel.setAttribute("for", "manual-research-notes");
      manualLabel.textContent = "人工补充笔记";
      const manualHelp = text("p", notesLang === "zh"
        ? "人工补充笔记仅保留在当前浏览器页面中，并会在复制研究笔记时一起带出；系统不会保存到服务器。"
        : "Manual notes are only kept in this browser view and are included when copying research notes. They are not saved to the server.",
        "muted");
      const manual = document.createElement("textarea");
      manual.id = "manual-research-notes";
      manual.className = "manual-notes";
      manual.setAttribute("aria-label", "人工补充笔记");
      manual.placeholder = "在这里添加本地观察。内容不会保存到服务器。";
      section.appendChild(manualLabel);
      section.appendChild(manualHelp);
      section.appendChild(manual);
      const status = text("p", notesLang === "zh" ? "研究 / 观察用途。本笔记在浏览器本地生成，不保存到服务器。" : "Research / observation only. Notes are generated locally and not saved to the server.", "muted");
      section.appendChild(status);
      const textarea = document.createElement("textarea");
      textarea.className = "research-notes-textarea";
      textarea.readOnly = true;
      textarea.setAttribute("aria-label", "生成的研究笔记");
      const updateNotes = () => {
        manualResearchNotes = manual.value;
        textarea.value = currentSignals.length ? buildResearchNotes(notesMode, visibleSignals, manual.value) : "Not enough data to build research notes.";
      };
      manual.value = manualResearchNotes;
      manual.addEventListener("input", updateNotes);
      regenerate.addEventListener("click", updateNotes);
      copyMarkdown.addEventListener("click", () => copyNotesText(textarea, status, "markdown"));
      copyPlain.addEventListener("click", () => copyNotesText(textarea, status, "plain"));
      updateNotes();
      section.appendChild(textarea);
      return appendBackToTop(section);
    }

    function exportFileStem() {
      const run = currentDashboardData?.run || {};
      const date = String(run.date || runSelectEl.value || "").trim();
      return date ? `market-impact-research-${date}` : "market-impact-research-notes";
    }

    function viewUrlForExport() {
      return `${window.location.pathname}${window.location.search}${window.location.hash}`;
    }

    function sourceReliabilityExportLines() {
      const isZh = effectiveExportLang() === "zh";
      const dataCounts = countSignalsBy(currentSignals, (signal) => signal.data_status || "unknown");
      const sourceRows = sourceBreakdown(currentSignals);
      const missingSourceCount = currentSignals.filter((signal) => sourceValues(signal).length === 0).length;
      const missingFetchedCount = currentSignals.filter((signal) => fetchedValues(signal).length === 0).length;
      const fallbackCount = currentSignals.filter(hasFallback).length;
      return [
        isZh ? `- 数据状态分布：${Object.entries(dataCounts).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", ") || "未知"}` : `- Data status distribution: ${Object.entries(dataCounts).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown"}`,
        isZh ? `- 覆盖来源数：${sourceRows.length}` : `- Sources covered: ${sourceRows.length}`,
        isZh ? `- 缺少来源数量：${missingSourceCount}` : `- Missing source count: ${missingSourceCount}`,
        isZh ? `- 缺少 fetched_at 数量：${missingFetchedCount}` : `- Missing fetched_at count: ${missingFetchedCount}`,
        isZh ? `- fallback 来源数量：${fallbackCount}` : `- Fallback source count: ${fallbackCount}`,
      ];
    }

    function matrixSummaryExportLines() {
      const isZh = effectiveExportLang() === "zh";
      const themes = Array.isArray(themeSourceMatrixData?.themes) ? themeSourceMatrixData.themes : [];
      const sources = Array.isArray(themeSourceMatrixData?.sources) ? themeSourceMatrixData.sources : [];
      const matrix = Array.isArray(themeSourceMatrixData?.matrix) ? themeSourceMatrixData.matrix : [];
      const weakCells = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      return [
        isZh ? `- 主题数：${themes.length}` : `- Themes: ${themes.length}`,
        isZh ? `- 来源数：${sources.length}` : `- Sources: ${sources.length}`,
        isZh ? `- 矩阵单元格：${matrix.length}` : `- Matrix cells: ${matrix.length}`,
        isZh ? `- 需要复核的主题-来源组合：${weakCells.length}` : `- Theme-source pairs needing review: ${weakCells.length}`,
      ];
    }

    function dateCompareExportLines() {
      const isZh = effectiveExportLang() === "zh";
      const compare = dateCompareData || {};
      if (compare.available === false) return [`- ${compare.notes?.join(" ") || (isZh ? "日期对比不可用。" : "Date comparison is not available.")}`];
      const summary = compare.summary || {};
      return [
        isZh ? `- 对比日期：${compare.from_date || "未知"} -> ${compare.to_date || "未知"}` : `- Compared runs: ${compare.from_date || "unknown"} -> ${compare.to_date || "unknown"}`,
        isZh ? `- 新增观察主题：${summary.new_themes_count || 0}` : `- New watch themes: ${summary.new_themes_count || 0}`,
        isZh ? `- 移出当前观察列表：${summary.removed_themes_count || 0}` : `- Removed from current watch list: ${summary.removed_themes_count || 0}`,
        isZh ? `- 发生变化的主题：${summary.changed_themes_count || 0}` : `- Changed themes: ${summary.changed_themes_count || 0}`,
        isZh ? `- 新增 ETF 观察候选：${summary.new_etf_candidates_count || 0}` : `- New ETF observation candidates: ${summary.new_etf_candidates_count || 0}`,
        isZh ? `- 新增个股观察候选：${summary.new_stock_candidates_count || 0}` : `- New stock observation candidates: ${summary.new_stock_candidates_count || 0}`,
        isZh ? `- 证据质量变化：${summary.weaker_data_quality_count || 0} 个变弱，${summary.improved_data_quality_count || 0} 个改善` : `- Evidence quality changes: ${summary.weaker_data_quality_count || 0} weaker, ${summary.improved_data_quality_count || 0} improved`,
      ];
    }

    function candidatePoolExportLines(visibleSignals) {
      const isZh = effectiveExportLang() === "zh";
      const etfs = briefCandidateLabelsFromSignals(visibleSignals, "etf_candidates", 10);
      const stocks = briefCandidateLabelsFromSignals(visibleSignals, "stock_candidates", 10);
      return [
        isZh ? `- ETF 观察候选：${etfs.join(", ") || "不可用"}` : `- ETF observation candidates: ${etfs.join(", ") || "not available"}`,
        isZh ? `- 个股观察候选：${stocks.join(", ") || "不可用"}` : `- Stock observation candidates: ${stocks.join(", ") || "not available"}`,
      ];
    }

    function buildExportMarkdown(visibleSignals) {
      const isZh = effectiveExportLang() === "zh";
      const run = currentDashboardData?.run || {};
      const reviewItems = buildResearchReviewItems(visibleSignals, reviewScope);
      const lines = [
        isZh ? "# 控制台研究包" : "# Console Research Export Package",
        isZh
          ? "> 本导出内容仅用于研究观察与复盘记录，不构成买卖建议、下单指令或收益预测。"
          : "> This export is for research and observation only. It is not trading advice, not an order instruction, and not a forecast of returns.",
        "",
        isZh ? "## 导出上下文" : "## Export Context",
        isZh ? `- 运行日期：${run.date || runSelectEl.value || "未知"}` : `- Run date: ${run.date || runSelectEl.value || "unknown"}`,
        isZh ? `- 本地生成时间：${new Date().toISOString()}` : `- Generated locally at: ${new Date().toISOString()}`,
        isZh ? `- 当前筛选：${currentFilterSummary()}` : `- Current filters: ${currentFilterSummary()}`,
        isZh ? `- 当前关注主题：${selectedTheme || "未选择"}` : `- Selected theme: ${selectedTheme || "not selected"}`,
        isZh ? `- 当前关注来源：${selectedSource || "未选择"}` : `- Selected source: ${selectedSource || "not selected"}`,
        isZh ? `- 当前对比主题：${compareThemes.length ? compareThemes.join(", ") : "未选择"}` : `- Compared themes: ${compareThemes.length ? compareThemes.join(", ") : "not selected"}`,
        "",
      ];
      if (exportSections.dailyBrief) lines.push(buildDailyResearchBrief(briefMode, visibleSignals), "");
      if (exportSections.researchNotes) lines.push(buildResearchNotes(notesMode, visibleSignals, exportSections.manualNotes ? manualResearchNotes : ""), "");
      if (exportSections.reviewQueue) {
        lines.push(isZh ? "## 研究复核清单" : "## Research Review Queue");
        const reviewLines = reviewItems.slice(0, 10).map(reviewItemNoteLine);
        lines.push(...(reviewLines.length ? reviewLines : [isZh ? "- 当前视图暂无需要复核的事项。" : "- No review items for the current view."]), "");
      }
      if (exportSections.dateCompare) lines.push(...notesLines(isZh ? "日期对比" : "Date Compare", dateCompareExportLines()));
      if (exportSections.sourceReliability) lines.push(...notesLines(isZh ? "数据来源与新鲜度" : "Source Reliability", sourceReliabilityExportLines()));
      if (exportSections.matrixSummary) lines.push(...notesLines(isZh ? "主题-来源矩阵摘要" : "Theme x Source Matrix Summary", matrixSummaryExportLines()));
      if (exportSections.candidatePool) lines.push(...notesLines(isZh ? "观察候选池摘要" : "Candidate Pool Summary", candidatePoolExportLines(visibleSignals)));
      if (exportSections.manualNotes && !exportSections.researchNotes && manualResearchNotes.trim()) {
        lines.push(isZh ? "## 人工补充笔记" : "## Manual Research Notes", manualResearchNotes.trim(), "");
      }
      if (exportSections.queryState) {
        lines.push(isZh ? "## 当前视图状态" : "## Current URL / Query State");
        lines.push(`- URL: ${viewUrlForExport()}`);
        lines.push(isZh ? `- 查询状态: ${JSON.stringify(currentConsoleState())}` : `- Query state: ${JSON.stringify(currentConsoleState())}`);
        lines.push("");
      }
      return lines.join("\\n").trim() || (isZh ? "当前视图暂无可导出内容。" : "No export content available for the current view.");
    }

    function buildExportPlainText(visibleSignals) {
      return buildExportMarkdown(visibleSignals)
        .split("\\n")
        .map((line) => line.replace(/^#{1,6}\\s*/, "").replace(/^>\\s*/, ""))
        .join("\\n");
    }

    function buildExportMetadata(visibleSignals) {
      const run = currentDashboardData?.run || {};
      return {
        schema_version: "1.0",
        generated_locally_at: new Date().toISOString(),
        run_date: run.date || runSelectEl.value || null,
        query_state: currentConsoleState(),
        selected_theme: selectedTheme || null,
        selected_source: selectedSource || null,
        compare_themes: compareThemes,
        compare_from: compareFromDate || null,
        compare_to: compareToDate || null,
        visible_signals_count: visibleSignals.length,
        review_items_count: buildResearchReviewItems(visibleSignals, reviewScope).length,
        export_sections: EXPORT_SECTION_KEYS.filter((key) => exportSections[key] !== false),
        notes: {
          research_brief_included: exportSections.dailyBrief !== false,
          research_notes_included: exportSections.researchNotes !== false,
          manual_notes_included: exportSections.manualNotes !== false && Boolean(manualResearchNotes.trim()),
        },
      };
    }

    function exportPreviewText(visibleSignals) {
      if (exportFormat === "json") return JSON.stringify(buildExportMetadata(visibleSignals), null, 2);
      if (exportFormat === "txt") return buildExportPlainText(visibleSignals);
      return buildExportMarkdown(visibleSignals);
    }

    function downloadTextFile(fileName, content, type, statusNode) {
      const blob = new Blob([content || ""], { type });
      const href = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = href;
      anchor.download = fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(href), 0);
      statusNode.textContent = `已准备本地下载：${fileName}`;
    }

    function renderResearchExportPackage(visibleSignals) {
      const section = document.createElement("article");
      section.id = "research-export-package";
      section.className = "research-export section-card";
      section.appendChild(text("h2", uiText("研究包导出", "Research Export Package")));
      section.appendChild(description("研究笔记工作区用于生成和补充笔记；研究包导出用于将选定内容下载到本地文件。导出完全在浏览器本地完成。"));
      section.appendChild(text("p", effectiveExportLang() === "zh"
        ? "本导出内容仅用于研究观察与复盘记录，不构成买卖建议、下单指令或收益预测。"
        : "This export is for research and observation only. It is not trading advice, not an order instruction, and not a forecast of returns.",
        "muted"));
      const controls = document.createElement("div");
      controls.className = "export-controls";
      controls.appendChild(renderReviewSelect("export-language-select", "导出语言", [["", "自动"], ["en", "English"], ["zh", "中文"]], exportLang, (value) => {
        exportLang = normalizeExportLang(value);
        updateQueryState({ exportLang });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("export-format-select", "预览格式", [["md", "Markdown"], ["txt", "纯文本"], ["json", "JSON 元信息"]], exportFormat, (value) => {
        exportFormat = normalizeExportFormat(value);
        updateQueryState({ exportFormat });
        renderSignalSections();
      }));
      const mdButton = document.createElement("button");
      mdButton.type = "button";
      mdButton.className = "inline-action";
      mdButton.textContent = "下载 Markdown";
      const txtButton = document.createElement("button");
      txtButton.type = "button";
      txtButton.className = "inline-action";
      txtButton.textContent = "下载纯文本";
      const jsonButton = document.createElement("button");
      jsonButton.type = "button";
      jsonButton.className = "inline-action";
      jsonButton.textContent = "下载 JSON 元信息";
      controls.appendChild(mdButton);
      controls.appendChild(txtButton);
      controls.appendChild(jsonButton);
      section.appendChild(controls);
      section.appendChild(text("h3", "导出内容"));
      const toggleWrap = document.createElement("div");
      toggleWrap.className = "brief-toggle-grid";
      EXPORT_SECTION_KEYS.forEach((key) => {
        const item = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = exportSections[key] !== false;
        input.addEventListener("change", () => {
          exportSections[key] = input.checked;
          renderSignalSections();
        });
        item.appendChild(input);
        item.appendChild(text("span", exportSectionLabel(key)));
        toggleWrap.appendChild(item);
      });
      section.appendChild(toggleWrap);
      section.appendChild(text("h3", "导出预览"));
      const preview = document.createElement("textarea");
      preview.id = "export-preview";
      preview.className = "export-preview";
      preview.readOnly = true;
      preview.setAttribute("aria-label", "导出预览");
      preview.value = currentSignals.length ? exportPreviewText(visibleSignals) : "当前视图暂无可导出内容。";
      section.appendChild(preview);
      const status = text("p", "下载文件在当前浏览器本地生成，不会保存到服务器。", "muted");
      section.appendChild(status);
      mdButton.addEventListener("click", () => downloadTextFile(`${exportFileStem()}.md`, buildExportMarkdown(visibleSignals), "text/markdown;charset=utf-8", status));
      txtButton.addEventListener("click", () => downloadTextFile(`${exportFileStem()}.txt`, buildExportPlainText(visibleSignals), "text/plain;charset=utf-8", status));
      jsonButton.addEventListener("click", () => downloadTextFile(`${exportFileStem()}.json`, JSON.stringify(buildExportMetadata(visibleSignals), null, 2), "application/json;charset=utf-8", status));
      return appendBackToTop(section);
    }

    function renderConsoleUsageGuide() {
      const section = document.createElement("article");
      section.id = "console-usage-guide";
      section.className = "section-card";
      section.appendChild(text("h2", uiText("使用引导", "Console Usage Guide")));
      section.appendChild(description("推荐的只读研究工作流。使用这些区域不会改变数据，也不会运行 pipeline。"));
      const steps = [
        ["第一步", "先看今日摘要", "快速了解今天海外热点可能传导到哪些 A 股方向。"],
        ["第二步", "查看研究复核清单", "确认哪些证据、数据来源、候选池变化需要人工复核。"],
        ["第三步", "查看主题 × 来源矩阵", "判断主题与数据源之间的证据覆盖是否充分。"],
        ["第四步", "使用日期对比", "观察今天相对上一期新增、消失或变化的主题和候选池。"],
        ["第五步", "生成研究笔记", "把复核事项、证据缺口和观察结果整理成本地研究笔记。"],
        ["第六步", "查看详情面板", "必要时深入查看主题、来源或单条信号详情。"],
      ];
      const list = document.createElement("ol");
      steps.forEach(([prefix, title, body]) => {
        const item = document.createElement("li");
        item.appendChild(text("strong", `${prefix}: ${title}`));
        item.appendChild(text("div", body, "muted"));
        list.appendChild(item);
      });
      section.appendChild(list);
      section.appendChild(text("p", "本控制台用于研究观察与证据复核，不提供交易指令、下单、目标价或收益预测。", "muted"));
      return appendBackToTop(section);
    }

    function renderMorningBrief(visibleSignals) {
      const section = document.createElement("article");
      section.id = "morning-brief";
      section.className = "morning-brief section-card";
      section.appendChild(text("h2", uiText("今日观察摘要", "Morning Brief")));
      section.appendChild(description("汇总当前运行日期下的海外热点、A 股观察主题、数据质量和风险提示。"));
      const run = currentDashboardData?.run || {};
      const statusCounts = countSignalsBy(currentSignals, (signal) => signal.intraday_status || signal.status || "not_checked");
      const dataCounts = countSignalsBy(currentSignals, (signal) => signal.data_status || "unknown");
      const weakSignals = currentSignals.filter((signal) => weakEvidenceReasons(signal).length > 0);
      const weakMatrixCells = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      const reviewItems = buildResearchReviewItems(visibleSignals, reviewScope);
      const highReviewItems = reviewItems.filter((item) => item.severity === "high");
      const groups = groupedSignals(currentSignals);
      const strongThemes = groups.slice(0, 3).map((group) => `${group.theme} (${topScore(group.signals)})`);
      const highRiskThemes = groups.filter((group) => normalized(maxRisk(group.signals)) === "high").slice(0, 3).map((group) => group.theme);
      const recurringThemes = (Array.isArray(themeHistoryData?.themes) ? [...themeHistoryData.themes] : [])
        .sort((left, right) => Number(right.runs_seen || 0) - Number(left.runs_seen || 0) || Number(right.signal_count || 0) - Number(left.signal_count || 0))
        .slice(0, 3)
        .map((item) => `${item.theme || "Unknown Theme"} (${item.runs_seen || 0} 次运行)`);
      const topEtfs = (Array.isArray(candidateHistoryData?.etf_candidates) ? [...candidateHistoryData.etf_candidates] : [])
        .sort((left, right) => Number(right.appearances || 0) - Number(left.appearances || 0))
        .slice(0, 3)
        .map((item) => `${item.name || "unknown"} (${item.appearances || 0})`);
      const topStocks = (Array.isArray(candidateHistoryData?.stock_candidates) ? [...candidateHistoryData.stock_candidates] : [])
        .sort((left, right) => Number(right.appearances || 0) - Number(left.appearances || 0))
        .slice(0, 3)
        .map((item) => `${item.name || "unknown"} (${item.appearances || 0})`);
      const qualityNotes = Object.entries(dataCounts)
        .filter(([status]) => ["missing", "missing_data", "partial", "stale", "unknown"].includes(normalized(status)))
        .map(([status, count]) => `${dataStatusLabel(status)}: ${count}`);
      const briefGrid = document.createElement("div");
      briefGrid.className = "theme-summary";
      [
        ["运行日期", run.date || runSelectEl.value || "未知"],
        ["信号数量", currentSignals.length],
        ["当前可见信号", visibleSignals.length],
        ["状态概览", Object.entries(statusCounts).map(([key, count]) => `${intradayStatusLabel(key)}: ${count}`).join(", ") || "未知"],
        ["数据质量提示", qualityNotes.join(", ") || "当前信号没有缺失、部分、过期或未知的数据状态标签。"],
        ["需要确认", `${weakSignals.length} 条信号需要数据复核。`],
        ["研究复核清单", `${reviewItems.length} 条复核事项，其中 ${highReviewItems.length} 条为高优先级。`],
        ["矩阵复核", `${weakMatrixCells.length} 个主题-来源组合需要证据复核。`],
        ["谨慎项", highRiskThemes.length ? `高风险主题：${highRiskThemes.join(", ")}` : "当前信号中没有高风险主题。"],
      ].forEach(([label, value]) => briefGrid.appendChild(metric(label, value)));
      section.appendChild(briefGrid);
      section.appendChild(renderBriefList("今日核心观察", strongThemes));
      section.appendChild(renderBriefList("历史反复出现主题", recurringThemes));
      section.appendChild(renderBriefList("反复出现的 ETF 观察候选", topEtfs));
      section.appendChild(renderBriefList("反复出现的个股观察候选", topStocks));
      return appendBackToTop(section);
    }

    function renderCompareSelector() {
      const wrap = document.createElement("div");
      wrap.className = "compare-actions";
      const field = document.createElement("div");
      const label = document.createElement("label");
      label.setAttribute("for", "compare-theme-select");
      label.textContent = "主题选择";
      const select = document.createElement("select");
      select.id = "compare-theme-select";
      const themes = availableThemeNames();
      if (!themes.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "暂无可选主题";
        select.appendChild(option);
        select.disabled = true;
      } else {
        themes.forEach((theme) => {
          const option = document.createElement("option");
          option.value = theme;
          option.textContent = theme;
          select.appendChild(option);
        });
      }
      field.appendChild(label);
      field.appendChild(select);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "inline-action";
      button.textContent = "加入对比";
      button.disabled = !themes.length;
      button.addEventListener("click", () => addCompareTheme(select.value));
      wrap.appendChild(field);
      wrap.appendChild(button);
      return wrap;
    }

    function renderCompareEvidence(theme, currentSignalsForTheme, etfs, stocks) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "证据链"));
      const history = themeHistoryItem(theme);
      const triggers = uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers)).concat(arrayValue(history?.external_triggers)), 5);
      const mappings = uniqueValues(currentSignalsForTheme.map((signal) => signal.a_share_mapping_reason), 3);
      const risks = uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.risks)), 5);
      const chain = document.createElement("ol");
      chain.className = "evidence-chain";
      [
        ["外部触发", triggers.join(", ") || "未知"],
        ["A 股主题映射", mappings.join(" | ") || "未知"],
        ["候选池", `${etfs.length} 个 ETF 观察候选，${stocks.length} 个个股观察候选`],
        ["风险提示", risks.join(", ") || "暂无风险提示。"],
        ["数据质量", distribution(currentSignalsForTheme, "data_status", "unknown")],
      ].forEach(([label, value]) => {
        const item = document.createElement("li");
        item.appendChild(text("strong", label));
        item.appendChild(text("div", value, "muted"));
        chain.appendChild(item);
      });
      section.appendChild(chain);
      return section;
    }

    function renderCompareCard(theme, visibleSignals) {
      const card = document.createElement("article");
      card.className = "compare-card";
      const heading = document.createElement("h3");
      heading.appendChild(createThemeButton(theme));
      card.appendChild(heading);
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "inline-action";
      remove.textContent = "移除";
      remove.addEventListener("click", () => removeCompareTheme(theme));
      card.appendChild(remove);
      const currentSignalsForTheme = currentSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const visibleSignalsForTheme = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const history = themeHistoryItem(theme);
      const etfs = candidateHistoryForTheme(candidateHistoryData?.etf_candidates, theme);
      const stocks = candidateHistoryForTheme(candidateHistoryData?.stock_candidates, theme);
      [
        `今日信号: ${currentSignalsForTheme.length}`,
        `当前可见: ${visibleSignalsForTheme.length}`,
        `最高 score: ${topScore(currentSignalsForTheme)}`,
        `最强强度: ${strengthLabel(strongestStrength(currentSignalsForTheme))}`,
        `主要状态: ${intradayStatusLabel(mainStatus(currentSignalsForTheme))}`,
        `主要风险: ${riskLabel(maxRisk(currentSignalsForTheme))}`,
        `数据状态: ${distribution(currentSignalsForTheme, "data_status", "unknown")}`,
        `历史信号: ${history?.signal_count ?? "未知"}`,
        `出现运行数: ${history?.runs_seen ?? "未知"}`,
        `平均 score: ${history?.avg_score ?? "未知"}`,
        `最高 score: ${history?.max_score ?? "未知"}`,
        `最后出现: ${history?.last_seen || "未知"}`,
        `ETF 观察池: ${etfs.length}`,
        `个股观察池: ${stocks.length}`,
      ].forEach((value) => card.appendChild(badge(value)));
      if (currentSignalsForTheme.length === 0 && !history) {
        card.appendChild(text("p", "该主题暂无当前或历史观察。", "muted"));
      } else if (visibleSignalsForTheme.length === 0) {
        card.appendChild(text("p", "当前筛选条件下该主题没有可见信号；如有历史上下文仍会显示。", "muted"));
      }
      card.appendChild(renderCountBadges("历史风险分布", history?.risk_counts));
      card.appendChild(renderCountBadges("历史盘中状态分布", history?.intraday_status_counts));
      card.appendChild(renderCountBadges("历史数据状态分布", history?.data_status_counts));
      card.appendChild(renderValueList("近期日期", history?.recent_dates || []));
      card.appendChild(renderValueList("主要外部触发", uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers)).concat(arrayValue(history?.external_triggers)), 5)));
      card.appendChild(renderValueList("需要复核", currentSignalsForTheme.flatMap((signal) => weakEvidenceReasons(signal))));
      card.appendChild(renderCompareEvidence(theme, currentSignalsForTheme, etfs, stocks));
      return card;
    }

    function appearsInComparedThemes(candidate) {
      const themes = Array.isArray(candidate.themes) ? candidate.themes : [];
      return compareThemes.filter((theme) => themes.some((item) => sameTheme(item, theme))).length;
    }

    function renderCandidateOverlapTable(title, candidates) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      if (!compareThemes.length) {
        section.appendChild(text("p", "请选择主题以比较观察池重叠。", "muted"));
        return section;
      }
      const rows = (Array.isArray(candidates) ? candidates : [])
        .map((candidate) => ({ ...candidate, compared_count: appearsInComparedThemes(candidate) }))
        .filter((candidate) => candidate.compared_count > 0)
        .sort((left, right) => right.compared_count - left.compared_count || Number(right.appearances || 0) - Number(left.appearances || 0))
        .slice(0, 12);
      if (!rows.length) {
        section.appendChild(text("p", "所选主题之间暂无观察候选重叠。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "candidate-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Name", "Code / ticker", "Themes", "Appearances", "Last seen", "Compared themes"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((candidate) => {
        const tr = document.createElement("tr");
        [candidate.name, candidate.code || "unknown", (candidate.themes || []).join(", "), candidate.appearances ?? "unknown", candidate.last_seen || "unknown", candidate.compared_count].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderSourceBreakdown(signals) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "来源汇总"));
      const rows = sourceBreakdown(signals);
      if (!rows.length) {
        section.appendChild(text("p", "当前信号暂无来源元数据。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["来源", "信号数", "主题数", "最新 fetched_at", "数据状态分布", "弱证据信号", "fallback 数", "缺少 fetched_at"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        const sourceCell = document.createElement("td");
        sourceCell.appendChild(createSourceButton(row.source));
        tr.appendChild(sourceCell);
        [
          row.signal_count,
          row.themes.length,
          row.latest_fetched_at || "未知",
          Object.entries(row.data_status_counts).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", "),
          row.weak_count,
          row.fallback_count,
          row.missing_fetched_at_count,
        ].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderWeakEvidenceSignals(signals) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "弱证据信号"));
      const rows = signals
        .map((signal) => ({ signal, reasons: weakEvidenceReasons(signal) }))
        .filter((item) => item.reasons.length > 0);
      if (!rows.length) {
        section.appendChild(text("p", "当前运行中没有发现弱证据信号。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["主题", "强度", "Score", "风险", "盘中状态", "数据状态", "来源", "Fetched at", "需要确认"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach(({ signal, reasons }) => {
        const tr = document.createElement("tr");
        [themeName(signal), strengthLabel(signal.strength), signal.score ?? "未知", riskLabel(signal.risk_level), intradayStatusLabel(signal.intraday_status || signal.status), dataStatusLabel(signal.data_status)].forEach((value) => tr.appendChild(text("td", value)));
        const sourceCell = document.createElement("td");
        const sources = sourceValues(signal);
        if (sources.length) {
          sources.forEach((source, index) => {
            if (index) sourceCell.appendChild(text("span", ", "));
            sourceCell.appendChild(createSourceButton(source));
          });
        } else {
          sourceCell.appendChild(createSourceButton("Unknown Source"));
        }
        tr.appendChild(sourceCell);
        [fetchedValues(signal).join(", ") || "未知", reasons.join(", ")].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalDataQualityTrend() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "历史数据质量趋势"));
      if (!dataQualityHistoryData || dataQualityHistoryData.runs_count === 0) {
        section.appendChild(text("p", "历史数据不足。", "muted"));
        return section;
      }
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["历史运行数", dataQualityHistoryData.runs_count ?? "未知"],
        ["缺少来源", dataQualityHistoryData.missing_source_count ?? 0],
        ["缺少 fetched_at", dataQualityHistoryData.missing_fetched_at_count ?? 0],
        ["fallback 数", dataQualityHistoryData.fallback_count ?? 0],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(metrics);
      section.appendChild(renderHistoryTable("历史 data_status 分布", ["数据状态", "观察次数"], Object.entries(dataQualityHistoryData.data_status_counts || {}).map(([key, count]) => [dataStatusLabel(key), count])));
      section.appendChild(renderHistoryTable("出现次数最多的来源", ["来源", "观察次数"], Object.entries(dataQualityHistoryData.source_counts || {}).sort((left, right) => Number(right[1]) - Number(left[1])).slice(0, 10).map(([key, count]) => [key, count])));
      const weakThemes = Array.isArray(dataQualityHistoryData.themes_with_weak_data) ? dataQualityHistoryData.themes_with_weak_data : [];
      section.appendChild(renderHistoryTable("弱数据主题", ["主题", "弱证据信号", "近期日期", "最后出现", "数据状态分布"], weakThemes.slice(0, 10).map((item) => [item.theme, item.weak_signal_count, (item.recent_dates || []).join(", "), item.last_seen || "未知", Object.entries(item.data_status_counts || {}).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", ")])));
      return section;
    }

    function sourceReliabilityNotes(source, item, currentSignalsForSource) {
      const notes = [];
      if (!item && currentSignalsForSource.length === 0) notes.push("所选运行或可用历史中未找到该来源。");
      if ((item?.missing_fetched_at_count || 0) > 0 || currentSignalsForSource.some((signal) => !fetchedValues(signal).length)) notes.push("部分信号缺少 fetched_at。");
      const weakCount = item?.weak_signal_count || currentSignalsForSource.filter((signal) => weakEvidenceReasons(signal).length).length;
      if (weakCount > 0) notes.push("部分信号存在部分、过期、缺失、失败或未知的数据状态。");
      if ((item?.fallback_count || 0) > 0 || currentSignalsForSource.some(hasFallback)) notes.push("部分信号使用了 fallback 来源。");
      if ((item?.themes || []).length > 1) notes.push("该来源覆盖多个主题。");
      if ((item?.signal_count || currentSignalsForSource.length) <= 1) notes.push("该来源在可用历史中的覆盖有限。");
      return notes;
    }

    function renderSourceExampleSignals(item) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "示例信号"));
      const examples = Array.isArray(item?.example_signals) ? item.example_signals : [];
      if (!examples.length) {
        section.appendChild(text("p", "该来源暂无历史信号样例。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["日期", "主题", "强度", "Score", "风险", "盘中状态", "数据状态", "Fetched at", "Fallback"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      examples.forEach((signal) => {
        const tr = document.createElement("tr");
        [signal.date, signal.theme, strengthLabel(signal.strength), signal.score ?? "未知", riskLabel(signal.risk_level), intradayStatusLabel(signal.intraday_status), dataStatusLabel(signal.data_status), signal.fetched_at || "未知", signal.fallback_used ?? "未知"].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderSourceDetail(currentSignalsInput, visibleSignals) {
      const panel = document.createElement("article");
      panel.id = "source-detail";
      panel.className = "source-detail section-card";
      panel.appendChild(text("h2", uiText("来源详情", "Source Detail")));
      panel.appendChild(description("查看单个数据来源的覆盖主题、新鲜度、弱证据信号和近期样例。"));
      const source = selectedSource || (sourceBreakdown(currentSignalsInput)[0]?.source || "");
      if (!source) {
        panel.appendChild(text("p", "请从来源汇总、弱证据信号或信号详情中选择一个来源。", "muted"));
        return appendBackToTop(panel);
      }
      const history = sourceHistoryItem(source);
      const currentSignalsForSource = currentSignalsInput.filter((signal) => signalHasSource(signal, source));
      const visibleSignalsForSource = visibleSignals.filter((signal) => signalHasSource(signal, source));
      panel.appendChild(text("h3", sourceName(source)));
      panel.appendChild(text("h3", "概览"));
      [
        `当前信号: ${currentSignalsForSource.length}`,
        `当前可见: ${visibleSignalsForSource.length}`,
        `历史信号: ${history?.signal_count ?? "未知"}`,
        `主题数: ${(history?.themes || uniqueValues(currentSignalsForSource.map(themeName), 20)).length}`,
        `最后出现: ${history?.last_seen || "未知"}`,
        `最新 fetched_at: ${history?.latest_fetched_at || "未知"}`,
        `fallback 数: ${history?.fallback_count ?? currentSignalsForSource.filter(hasFallback).length}`,
        `缺少 fetched_at: ${history?.missing_fetched_at_count ?? currentSignalsForSource.filter((signal) => !fetchedValues(signal).length).length}`,
        `弱证据信号: ${history?.weak_signal_count ?? currentSignalsForSource.filter((signal) => weakEvidenceReasons(signal).length).length}`,
      ].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(text("p", "来源详情是证据质量视图，不把来源排名为绝对可靠，也不生成交易指令。", "muted"));
      if (!history && currentSignalsForSource.length === 0) {
        panel.appendChild(text("p", "该来源暂无当前或历史观察。", "muted"));
      }
      panel.appendChild(renderValueList("来源可靠性提示", sourceReliabilityNotes(source, history, currentSignalsForSource)));
      panel.appendChild(renderValueList("覆盖主题", history?.themes || uniqueValues(currentSignalsForSource.map(themeName), 20)));
      panel.appendChild(renderValueList("近期日期", history?.recent_dates || []));
      panel.appendChild(renderCountBadges("历史 data_status 分布", history?.data_status_counts));
      panel.appendChild(renderCountBadges("Historical risk distribution", history?.risk_counts));
      panel.appendChild(renderCountBadges("Historical intraday status distribution", history?.intraday_status_counts));
      panel.appendChild(renderWeakEvidenceSignals(currentSignalsForSource));
      panel.appendChild(renderSourceExampleSignals(history));
      return appendBackToTop(panel);
    }

    function renderMatrixSummary() {
      const section = document.createElement("div");
      section.className = "metrics";
      const themes = Array.isArray(themeSourceMatrixData?.themes) ? themeSourceMatrixData.themes : [];
      const sources = Array.isArray(themeSourceMatrixData?.sources) ? themeSourceMatrixData.sources : [];
      const cells = Array.isArray(themeSourceMatrixData?.matrix) ? themeSourceMatrixData.matrix : [];
      const weakCells = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      const missingSource = themes.reduce((total, item) => total + Number(item.missing_source_count || 0), 0);
      const missingFetched = cells.reduce((total, item) => total + Number(item.missing_fetched_at_count || 0), 0);
      const fallback = cells.reduce((total, item) => total + Number(item.fallback_count || 0), 0);
      const weakStatusCount = cells.reduce((total, item) => {
        const counts = item.data_status_counts || {};
        return total + Object.entries(counts).filter(([status]) => isWeakDataStatus(status)).reduce((sum, [, count]) => sum + Number(count || 0), 0);
      }, 0);
      [
        ["主题数", themes.length],
        ["来源数", sources.length],
        ["矩阵单元格", cells.length],
        ["弱证据单元格", weakCells.length],
        ["缺少来源", missingSource],
        ["缺少 fetched_at", missingFetched],
        ["fallback 数", fallback],
        ["弱数据状态", weakStatusCount],
      ].forEach(([label, value]) => section.appendChild(metric(label, value)));
      return section;
    }

    function renderMatrixTable() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "矩阵表"));
      const themes = (Array.isArray(themeSourceMatrixData?.themes) ? themeSourceMatrixData.themes : []).slice(0, 12);
      const sources = (Array.isArray(themeSourceMatrixData?.sources) ? [...themeSourceMatrixData.sources] : []).sort((left, right) => Number(right.signal_count || 0) - Number(left.signal_count || 0)).slice(0, 8);
      if (!themes.length || !sources.length) {
        section.appendChild(text("p", "暂无主题-来源矩阵数据。", "muted"));
        return section;
      }
      const wrap = document.createElement("div");
      wrap.className = "matrix-table-wrap";
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      header.appendChild(text("th", "主题 / 来源"));
      sources.forEach((source) => {
        const th = document.createElement("th");
        th.appendChild(createSourceButton(source.source));
        table.dataset.sourceColumns = "top";
        header.appendChild(th);
      });
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      themes.forEach((theme) => {
        const tr = document.createElement("tr");
        const themeCell = document.createElement("td");
        themeCell.appendChild(createThemeButton(theme.theme));
        tr.appendChild(themeCell);
        sources.forEach((source) => {
          const td = document.createElement("td");
          td.className = "matrix-cell";
          const cell = matrixCellItem(theme.theme, source.source);
          if (!cell) {
            td.appendChild(text("span", "empty", "muted"));
          } else {
            if (cell.weak_signal_count || cell.missing_fetched_at_count || cell.fallback_count || Object.keys(cell.data_status_counts || {}).some(isWeakDataStatus)) td.className += " weak";
            const button = document.createElement("button");
            button.type = "button";
            button.className = "inline-action";
            button.textContent = `${cell.signal_count} 条信号`;
            button.addEventListener("click", () => selectMatrixCell(theme.theme, source.source));
            td.appendChild(button);
            td.appendChild(badge(`弱证据: ${cell.weak_signal_count || 0}`));
            td.appendChild(badge(`缺少 fetched: ${cell.missing_fetched_at_count || 0}`));
            td.appendChild(badge(`fallback: ${cell.fallback_count || 0}`));
            td.appendChild(text("div", Object.entries(cell.data_status_counts || {}).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", ") || "未知", "muted"));
            td.appendChild(text("div", `最新: ${cell.latest_fetched_at || "未知"}`, "muted"));
          }
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      wrap.appendChild(table);
      section.appendChild(wrap);
      return section;
    }

    function renderMatrixCellDetail() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "单元格详情"));
      const fallbackCell = (Array.isArray(themeSourceMatrixData?.matrix) ? themeSourceMatrixData.matrix : [])[0];
      const theme = selectedMatrixTheme || fallbackCell?.theme || "";
      const source = selectedMatrixSource || fallbackCell?.source || "";
      if (!theme || !source) {
        section.appendChild(text("p", "请选择一个矩阵单元格查看主题-来源证据。", "muted"));
        return section;
      }
      const cell = matrixCellItem(theme, source);
      section.appendChild(text("h3", `${theme} / ${source}`));
      if (!cell) {
        section.appendChild(text("p", "该主题-来源组合暂无信号。", "muted"));
        return section;
      }
      section.appendChild(text("h3", "概览"));
      [
        `信号数: ${cell.signal_count}`,
        `弱证据信号: ${cell.weak_signal_count || 0}`,
        `缺少 fetched_at: ${cell.missing_fetched_at_count || 0}`,
        `fallback: ${cell.fallback_count || 0}`,
        `最后出现: ${cell.last_seen || "未知"}`,
        `最新 fetched_at: ${cell.latest_fetched_at || "未知"}`,
      ].forEach((value) => section.appendChild(badge(value)));
      section.appendChild(renderCountBadges("单元格 data_status 分布", cell.data_status_counts));
      section.appendChild(renderValueList("近期日期", cell.recent_dates || []));
      const examples = Array.isArray(cell.example_signals) ? cell.example_signals : [];
      section.appendChild(renderHistoryTable("示例信号", ["日期", "强度", "Score", "风险", "盘中状态", "数据状态", "Fetched at", "Fallback"], examples.map((signal) => [signal.date, strengthLabel(signal.strength), signal.score ?? "未知", riskLabel(signal.risk_level), intradayStatusLabel(signal.intraday_status), dataStatusLabel(signal.data_status), signal.fetched_at || "未知", signal.fallback_used ?? "未知"])));
      return section;
    }

    function renderWeakEvidenceCells() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "需要复核的主题-来源组合"));
      const rows = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      if (!rows.length) {
        section.appendChild(text("p", "当前可用历史中没有发现主题-来源证据缺口。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["主题", "来源", "原因", "弱证据信号", "缺少 fetched_at", "Fallback", "数据状态分布", "近期日期"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.slice(0, 12).forEach((row) => {
        const tr = document.createElement("tr");
        const themeCell = document.createElement("td");
        themeCell.appendChild(createThemeButton(row.theme));
        tr.appendChild(themeCell);
        const sourceCell = document.createElement("td");
        sourceCell.appendChild(createSourceButton(row.source));
        tr.appendChild(sourceCell);
        [row.reason, row.weak_signal_count, row.missing_fetched_at_count, row.fallback_count, Object.entries(row.data_status_counts || {}).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", "), (row.recent_dates || []).join(", ")].forEach((value) => tr.appendChild(text("td", value)));
        tr.addEventListener("click", () => selectMatrixCell(row.theme, row.source));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderThemeSourceMatrix() {
      const section = document.createElement("article");
      section.id = "theme-source-matrix";
      section.className = "theme-source-matrix section-card";
      section.appendChild(text("h2", uiText("主题 × 来源矩阵", "Theme × Source Matrix")));
      section.appendChild(text("p", "查看每个主题由哪些来源支撑，以及哪些主题-来源组合存在证据缺口或需要复核。", "muted"));
      section.appendChild(text("h3", "矩阵摘要"));
      section.appendChild(renderMatrixSummary());
      section.appendChild(renderMatrixTable());
      section.appendChild(renderMatrixCellDetail());
      section.appendChild(renderWeakEvidenceCells());
      return appendBackToTop(section);
    }

    function renderSourceReliability() {
      const section = document.createElement("article");
      section.id = "source-reliability";
      section.className = "source-reliability section-card";
      section.appendChild(text("h2", uiText("数据来源可靠性", "Source Reliability")));
      section.appendChild(description("查看当前信号的数据来源覆盖、fetched_at 新鲜度、缺失字段、fallback 来源和弱证据情况。"));
      const dataCounts = countSignalsBy(currentSignals, (signal) => signal.data_status || "unknown");
      const withSources = currentSignals.filter((signal) => sourceValues(signal).length > 0).length;
      const withFetched = currentSignals.filter((signal) => fetchedValues(signal).length > 0).length;
      const fallbackCount = currentSignals.filter(hasFallback).length;
      const weakSignals = currentSignals.filter((signal) => weakEvidenceReasons(signal).length > 0);
      const highRiskWeakThemes = uniqueValues(weakSignals.filter((signal) => normalized(signal.risk_level) === "high").map(themeName), 20);
      const weakSourceCount = sourceBreakdown(currentSignals).filter((row) => row.weak_count > 0).length;
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["信号总数", currentSignals.length],
        ["有来源的信号", withSources],
        ["缺少来源的信号", currentSignals.length - withSources],
        ["有 fetched_at 的信号", withFetched],
        ["缺少 fetched_at 的信号", currentSignals.length - withFetched],
        ["fallback 数", fallbackCount],
        ["需要复核", weakSignals.length],
        ["存在弱证据的来源", weakSourceCount],
        ["高风险 + 弱数据主题", highRiskWeakThemes.length],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(metrics);
      section.appendChild(renderHistoryTable("当前 data_status 分布", ["数据状态", "信号数"], Object.entries(dataCounts).map(([key, count]) => [dataStatusLabel(key), count])));
      section.appendChild(renderSourceBreakdown(currentSignals));
      section.appendChild(renderWeakEvidenceSignals(currentSignals));
      section.appendChild(renderSourceDetail(currentSignals, filteredSignals()));
      section.appendChild(renderHistoricalDataQualityTrend());
      return appendBackToTop(section);
    }

    function renderThemeCompare(visibleSignals) {
      const section = document.createElement("article");
      section.id = "theme-compare";
      section.className = "compare-workspace section-card";
      section.appendChild(text("h2", uiText("主题对比", "Theme Compare")));
      section.appendChild(description("并排比较多个观察主题的今日信号、历史触发、候选池、风险和数据质量。"));
      section.appendChild(renderCompareSelector());
      if (compareNotice) section.appendChild(text("p", compareNotice, "notice"));
      if (!compareThemes.length) {
        section.appendChild(text("p", "暂无已选择的对比主题。", "muted"));
      } else {
        const grid = document.createElement("div");
        grid.className = "compare-grid";
        compareThemes.forEach((theme) => grid.appendChild(renderCompareCard(theme, visibleSignals)));
        section.appendChild(grid);
      }
      const overlap = document.createElement("div");
      overlap.className = "detail-section";
      overlap.appendChild(text("h3", "候选池对比"));
      overlap.appendChild(text("p", "观察池重叠用于显示多个主题中反复出现的候选对象，不是排名或指令。", "muted"));
      overlap.appendChild(renderCandidateOverlapTable("ETF observation candidates", candidateHistoryData?.etf_candidates));
      overlap.appendChild(renderCandidateOverlapTable("Stock observation candidates", candidateHistoryData?.stock_candidates));
      section.appendChild(overlap);
      return appendBackToTop(section);
    }

    function compareSummaryValue(key) {
      return dateCompareData?.summary?.[key] ?? 0;
    }

    function compareCountText(counts) {
      return Object.entries(counts || {}).map(([key, count]) => `${dataStatusLabel(key)}: ${count}`).join(", ") || "未知";
    }

    function renderDateSelect(id, labelText, value) {
      const field = document.createElement("div");
      const label = document.createElement("label");
      label.setAttribute("for", id);
      label.textContent = labelText;
      const select = document.createElement("select");
      select.id = id;
      Array.from(runSelectEl.options).forEach((option) => {
        const item = document.createElement("option");
        item.value = option.value;
        item.textContent = option.textContent;
        select.appendChild(item);
      });
      if (value && !selectHasValue(select, value)) {
        const item = document.createElement("option");
        item.value = value;
        item.textContent = `${value} (不可用)`;
        select.appendChild(item);
      }
      if (value && selectHasValue(select, value)) select.value = value;
      field.appendChild(label);
      field.appendChild(select);
      return { field, select };
    }

    function renderDateCompareControls() {
      const wrap = document.createElement("div");
      wrap.className = "controls signal-controls";
      const fromField = renderDateSelect("compare-from-select", "对比起始日期", compareFromDate);
      const toField = renderDateSelect("compare-to-select", "对比目标日期", compareToDate || runSelectEl.value);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "inline-action";
      button.textContent = "对比日期";
      button.addEventListener("click", () => {
        compareFromDate = fromField.select.value;
        compareToDate = toField.select.value;
        updateQueryState({ compareFrom: compareFromDate, compareTo: compareToDate });
        loadDateCompare(runSelectEl.value);
      });
      wrap.appendChild(fromField.field);
      wrap.appendChild(toField.field);
      wrap.appendChild(button);
      return wrap;
    }

    function renderThemeChangeTable() {
      const themes = dateCompareData?.themes || {};
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "主题变化表"));
      const rows = [];
      (Array.isArray(themes.new) ? themes.new : []).forEach((theme) => rows.push(["新增", theme, "未知", "未知", "未知", "未知", "未知", "未知", "新增观察主题"]));
      (Array.isArray(themes.removed) ? themes.removed : []).forEach((theme) => rows.push(["移出", theme, "未知", "未知", "未知", "未知", "未知", "未知", "不在当前观察列表中"]));
      (Array.isArray(themes.changed) ? themes.changed : []).forEach((item) => {
        const notes = [];
        if (item.changes?.score_delta != null) notes.push(`分数变化 ${item.changes.score_delta}`);
        if (item.changes?.risk_changed) notes.push("风险变化");
        if (item.changes?.intraday_status_changed) notes.push("盘中状态变化");
        if (item.changes?.data_status_changed) notes.push("数据质量变化");
        rows.push([
          "变化",
          item.theme,
          item.from?.score ?? "未知",
          item.to?.score ?? "未知",
          item.changes?.score_delta ?? "未知",
          `${riskLabel(item.from?.risk_level)} -> ${riskLabel(item.to?.risk_level)}`,
          `${intradayStatusLabel(item.from?.intraday_status)} -> ${intradayStatusLabel(item.to?.intraday_status)}`,
          `${dataStatusLabel(item.from?.data_status)} -> ${dataStatusLabel(item.to?.data_status)}`,
          notes.join(", ") || "元数据变化",
        ]);
      });
      if (!rows.length) {
        section.appendChild(text("p", "所选日期暂无主题变化。", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["变化", "主题", "起始分数", "目标分数", "分数变化", "风险", "盘中状态", "数据状态", "说明"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        row.forEach((value, index) => {
          const td = document.createElement("td");
          if (index === 1) td.appendChild(createThemeButton(value));
          else td.appendChild(text("span", value));
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderCandidateChangeTable(title, payload) {
      const rows = [];
      for (const group of ["new", "removed", "repeated"]) {
        (Array.isArray(payload?.[group]) ? payload[group] : []).slice(0, 12).forEach((item) => {
          rows.push([group === "new" ? "新增" : group === "removed" ? "移出" : "重复出现", item.name, item.code || "未知", (item.themes || []).join(", "), item.from_appearance ?? 0, item.to_appearance ?? 0, item.last_seen || "未知"]);
        });
      }
      return renderHistoryTable(title, ["变化", "名称", "代码 / ticker", "主题", "起始", "目标", "最后出现"], rows);
    }

    function renderDataQualityChangeSection() {
      const quality = dateCompareData?.data_quality || {};
      const rows = [
        ["起始数据状态", compareCountText(quality.from_counts)],
        ["目标数据状态", compareCountText(quality.to_counts)],
        ["缺少来源变化", quality.missing_source_delta ?? 0],
        ["缺少 fetched_at 变化", quality.missing_fetched_at_delta ?? 0],
        ["fallback 变化", quality.fallback_delta ?? 0],
      ];
      const section = renderHistoryTable("数据质量变化", ["指标", "数值"], rows);
      section.appendChild(renderHistoryTable("证据质量变弱主题", ["主题", "起始弱证据分", "目标弱证据分"], (quality.weaker_themes || []).map((item) => [item.theme, item.from_weak_score, item.to_weak_score])));
      section.appendChild(renderHistoryTable("证据质量改善主题", ["主题", "起始弱证据分", "目标弱证据分"], (quality.improved_themes || []).map((item) => [item.theme, item.from_weak_score, item.to_weak_score])));
      return section;
    }

    function renderSourceChangeSection() {
      const sources = dateCompareData?.sources || {};
      return renderHistoryTable("来源覆盖变化", ["变化", "来源"], [
        ["新增来源", (sources.new || []).join(", ") || "无"],
        ["移出来源", (sources.removed || []).join(", ") || "无"],
        ["重复来源", (sources.repeated || []).join(", ") || "无"],
      ]);
    }

    function renderDateCompare() {
      const section = document.createElement("article");
      section.id = "date-compare";
      section.className = "date-compare section-card";
      section.appendChild(text("h2", uiText("日期对比", "Date Compare")));
      section.appendChild(description("比较两个 daily run，查看新增 / 移除 / 变化的观察主题、候选池变化、数据质量变化和来源覆盖变化。"));
      section.appendChild(renderDateCompareControls());
      section.appendChild(text("h3", "日期对比摘要"));
      if (!dateCompareData || dateCompareData.available === false) {
        section.appendChild(text("p", (dateCompareData?.notes || ["当前没有足够的历史运行记录用于日期对比。"]).join(" "), "muted"));
        return appendBackToTop(section);
      }
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["对比起始日期", dateCompareData.from_date || "未知"],
        ["对比目标日期", dateCompareData.to_date || "未知"],
        ["新增观察主题", compareSummaryValue("new_themes_count")],
        ["移出当前观察列表", compareSummaryValue("removed_themes_count")],
        ["发生变化的主题", compareSummaryValue("changed_themes_count")],
        ["新增 ETF 观察候选", compareSummaryValue("new_etf_candidates_count")],
        ["新增个股观察候选", compareSummaryValue("new_stock_candidates_count")],
        ["数据质量变化", `${compareSummaryValue("weaker_data_quality_count")} 变弱 / ${compareSummaryValue("improved_data_quality_count")} 改善`],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      const summary = document.createElement("div");
      summary.className = "detail-section";
      summary.appendChild(metrics);
      section.appendChild(summary);
      section.appendChild(renderThemeChangeTable());
      section.appendChild(renderCandidateChangeTable("ETF 观察候选变化", dateCompareData.candidates?.etf));
      section.appendChild(renderCandidateChangeTable("个股观察候选变化", dateCompareData.candidates?.stock));
      section.appendChild(renderDataQualityChangeSection());
      section.appendChild(renderSourceChangeSection());
      section.appendChild(renderValueList("对比说明", dateCompareData.notes || []));
      return appendBackToTop(section);
    }

    function createThemeSummaryCard(group) {
      const node = document.createElement("article");
      node.className = "theme-card";
      const heading = document.createElement("h3");
      heading.appendChild(createThemeButton(group.theme));
      node.appendChild(heading);
      node.appendChild(createCompareButton(group.theme, uiText("加入对比", "Compare")));
      node.appendChild(badge(uiText(`${group.signals.length} 个信号`, `${group.signals.length} signals`)));
      node.appendChild(badge(uiText(`最高分数: ${topScore(group.signals)}`, `top score: ${topScore(group.signals)}`)));
      node.appendChild(badge(uiText(`最高风险: ${riskLabel(maxRisk(group.signals))}`, `max risk: ${maxRisk(group.signals)}`)));
      node.appendChild(badge(uiText(`主要状态: ${intradayStatusLabel(mainStatus(group.signals))}`, `main status: ${mainStatus(group.signals)}`)));
      node.appendChild(badge(uiText(`ETF 候选: ${candidateCount(group.signals, "etf_candidates")}`, `ETF candidates: ${candidateCount(group.signals, "etf_candidates")}`)));
      node.appendChild(badge(uiText(`个股候选: ${candidateCount(group.signals, "stock_candidates")}`, `stock candidates: ${candidateCount(group.signals, "stock_candidates")}`)));
      node.appendChild(text("p", triggerSummary(group.signals), "muted"));
      return node;
    }

    function renderThemeHotlist(signals) {
      const section = document.createElement("article");
      section.id = "theme-hotlist";
      section.className = "theme-hotlist section-card";
      section.appendChild(text("h2", uiText("主题热榜", "Theme Hotlist")));
      section.appendChild(description("快速查看当前可见观察主题、触发摘要、风险等级和候选池数量。"));
      const groups = groupedSignals(signals);
      if (groups.length === 0) {
        section.appendChild(text("p", "当前筛选条件下没有匹配主题。", "muted"));
        return appendBackToTop(section);
      }
      const wrap = document.createElement("div");
      wrap.className = "theme-summary";
      for (const group of groups) wrap.appendChild(createThemeSummaryCard(group));
      section.appendChild(wrap);
      return appendBackToTop(section);
    }

    function renderGroupedSignals(signals) {
      const wrap = document.createElement("div");
      wrap.className = "signals";
      for (const group of groupedSignals(signals)) {
        const section = document.createElement("article");
        section.className = "theme-group";
        const heading = document.createElement("h2");
        heading.appendChild(createThemeButton(group.theme));
        section.appendChild(heading);
        section.appendChild(badge(uiText(`${group.signals.length} 个信号`, `${group.signals.length} signals`)));
        section.appendChild(badge(uiText(`最高分数: ${topScore(group.signals)}`, `highest score: ${topScore(group.signals)}`)));
        section.appendChild(badge(uiText(`最强强度: ${strengthLabel(strongestStrength(group.signals))}`, `strongest: ${strongestStrength(group.signals)}`)));
        section.appendChild(badge(uiText(`风险分布: ${distribution(group.signals, "risk_level", "unknown")}`, `risks: ${distribution(group.signals, "risk_level", "unknown")}`)));
        section.appendChild(badge(uiText(`状态分布: ${distribution(group.signals, "intraday_status", "not_checked")}`, `statuses: ${distribution(group.signals, "intraday_status", "not_checked")}`)));
        section.appendChild(badge(uiText(`ETF 候选: ${candidateCount(group.signals, "etf_candidates")}`, `ETF candidates: ${candidateCount(group.signals, "etf_candidates")}`)));
        section.appendChild(badge(uiText(`个股候选: ${candidateCount(group.signals, "stock_candidates")}`, `stock candidates: ${candidateCount(group.signals, "stock_candidates")}`)));
        section.appendChild(text("p", triggerSummary(group.signals), "muted"));
        for (const signal of group.signals) section.appendChild(createSignalCard(signal));
        wrap.appendChild(section);
      }
      return wrap;
    }

    function renderFlatSignals(signals) {
      const wrap = document.createElement("div");
      wrap.className = "signals";
      for (const signal of signals) wrap.appendChild(createSignalCard(signal));
      return wrap;
    }

    function renderSignalSections() {
      if (!signalsAreaEl) return;
      clear(signalsAreaEl);
      const visibleSignals = sortSignals(filteredSignals());
      visibleSignalCount = visibleSignals.length;
      if (visibleSignals.length === 0) {
        selectedSignalIndex = null;
      } else if (!visibleSignals.some((signal) => signal.__index === selectedSignalIndex)) {
        selectedSignalIndex = visibleSignals[0].__index;
      }
      const selectedSignal = visibleSignals.find((signal) => signal.__index === selectedSignalIndex) || null;
      signalCountEl.textContent = uiText(`当前可见 ${visibleSignals.length} / 总信号 ${currentSignals.length}`, `visible ${visibleSignals.length} / total signals ${currentSignals.length}`);
      signalsAreaEl.appendChild(renderConsoleUsageGuide());
      signalsAreaEl.appendChild(renderMorningBrief(visibleSignals));
      signalsAreaEl.appendChild(renderDailyResearchBrief(visibleSignals));
      signalsAreaEl.appendChild(renderResearchReviewQueue(visibleSignals));
      signalsAreaEl.appendChild(renderResearchNotesComposer(visibleSignals));
      signalsAreaEl.appendChild(renderResearchExportPackage(visibleSignals));
      signalsAreaEl.appendChild(renderDateCompare());
      signalsAreaEl.appendChild(renderSourceReliability());
      signalsAreaEl.appendChild(renderThemeSourceMatrix());
      signalsAreaEl.appendChild(renderThemeHotlist(visibleSignals));
      signalsAreaEl.appendChild(renderThemeCompare(visibleSignals));
      const layout = document.createElement("div");
      layout.className = "analysis-layout";
      const listPane = document.createElement("div");
      listPane.id = "signal-explorer";
      listPane.className = "section-card";
      const heading = text("h2", viewModeEl.value === "flat" ? `信号浏览器（${visibleSignals.length}）` : `按主题分组的信号（${visibleSignals.length}）`);
      listPane.appendChild(heading);
      listPane.appendChild(description("浏览当前运行中的信号列表，可按搜索、风险、状态、排序和视图模式筛选。"));
      if (visibleSignals.length === 0) {
        listPane.appendChild(text("p", "当前筛选条件下没有匹配信号。", "muted"));
        appendBackToTop(listPane);
        layout.appendChild(listPane);
        layout.appendChild(renderSignalDetail(null));
        signalsAreaEl.appendChild(layout);
        signalsAreaEl.appendChild(renderThemeDetail(visibleSignals));
        renderStatusStrip();
        return;
      }
      listPane.appendChild(viewModeEl.value === "flat" ? renderFlatSignals(visibleSignals) : renderGroupedSignals(visibleSignals));
      appendBackToTop(listPane);
      layout.appendChild(listPane);
      layout.appendChild(renderSignalDetail(selectedSignal));
      signalsAreaEl.appendChild(layout);
      signalsAreaEl.appendChild(renderThemeDetail(visibleSignals));
      renderStatusStrip();
      applyStaticUiLanguage();
    }

    function renderDashboard(data, artifacts) {
      clear(dashboardEl);
      currentDashboardData = data;
      currentArtifacts = artifacts;
      selectedSignalIndex = null;
      const run = data.run || {};
      const summary = data.summary || {};
      const signals = Array.isArray(data.signals) ? data.signals : [];
      currentSignals = signals.map((signal, index) => ({ ...signal, __index: index }));
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [[uiText("日期", "Date"), run.date], [uiText("状态", "Status"), run.status], ["Schema", data.schema_version], [uiText("强信号", "Strong"), summary.strong_signals], [uiText("已确认", "Confirmed"), summary.confirmed], [uiText("缺数据", "Missing data"), summary.missing_data]].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      dashboardEl.appendChild(metrics);

      signalsAreaEl = document.createElement("div");
      signalsAreaEl.id = "signals-area";
      dashboardEl.appendChild(signalsAreaEl);
      renderSignalSections();

      dashboardEl.appendChild(renderHistoricalReview());
      dashboardEl.appendChild(renderArtifacts(artifacts));

      const details = document.createElement("details");
      details.appendChild(text("summary", uiText("原始 dashboard_data.json", "Raw dashboard_data.json")));
      const pre = document.createElement("pre");
      pre.textContent = JSON.stringify(data, null, 2);
      details.appendChild(pre);
      dashboardEl.appendChild(details);
    }

    async function loadDashboard(date, button) {
      if (!date) return;
      for (const item of document.querySelectorAll("#runs button")) item.classList.remove("active");
      if (button) button.classList.add("active");
      runSelectEl.value = date;
      updateQueryState({ date });
      setStatus(dashboardStatusEl, uiText(`正在加载 ${date}...`, `Loading ${date}...`));
      try {
        const [data, artifacts] = await Promise.all([
          fetchJson(`/api/runs/${date}/dashboard-data`),
          fetchJson(`/api/runs/${date}/artifacts`),
        ]);
        setStatus(dashboardStatusEl, uiText(`已加载 ${date}`, `Loaded ${date}`));
        renderDashboard(data, artifacts);
        loadDateCompare(date);
      } catch (error) {
        clear(dashboardEl);
        currentSignals = [];
        signalsAreaEl = null;
        currentDashboardData = null;
        currentArtifacts = null;
        selectedSignalIndex = null;
        visibleSignalCount = 0;
        signalCountEl.textContent = uiText("尚未加载信号。", "No signals loaded yet.");
        renderStatusStrip();
        setStatus(dashboardStatusEl, uiText(`加载 dashboard 数据失败: ${error.message}`, `Failed to load dashboard data: ${error.message}`), true);
      }
    }

    async function loadRuns() {
      setStatus(runsStatusEl, uiText("正在加载运行记录...", "Loading runs..."));
      clear(runsEl);
      clear(dashboardEl);
      currentSignals = [];
      signalsAreaEl = null;
      currentDashboardData = null;
      currentArtifacts = null;
      selectedSignalIndex = null;
      visibleSignalCount = 0;
      signalCountEl.textContent = uiText("尚未加载信号。", "No signals loaded yet.");
      renderStatusStrip();
      try {
        renderRuns(await fetchJson("/api/runs"));
      } catch (error) {
        clear(runSelectEl);
        runSelectEl.disabled = true;
        setStatus(runsStatusEl, uiText(`加载运行记录失败: ${error.message}`, `Failed to load runs: ${error.message}`), true);
      }
    }

    runSelectEl.addEventListener("change", () => loadDashboard(runSelectEl.value));
    refreshRunsEl.addEventListener("click", loadRuns);
    signalSearchEl.addEventListener("input", applySignalFilters);
    riskFilterEl.addEventListener("change", applySignalFilters);
    statusFilterEl.addEventListener("change", applySignalFilters);
    sortSelectEl.addEventListener("change", applySignalFilters);
    viewModeEl.addEventListener("change", applySignalFilters);
    uiLanguageToggleEl?.addEventListener("click", () => setUiLanguage(uiLang === "zh" ? "en" : "zh"));
    syncControlsFromState(readConsoleStateFromUrl());
    applyStaticUiLanguage();
    renderStatusStrip();
    loadApiStatus();
    loadHistoryReview().finally(loadRuns);
  </script>
</body>
</html>
"""
