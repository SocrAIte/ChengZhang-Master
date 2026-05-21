from __future__ import annotations


def render_console_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Impact Radar Console</title>
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
    <h1>Market Impact Radar Console</h1>
    <div class="muted">Read-only daily report viewer. This page only reads existing API data and does not run the pipeline.</div>
    <div id="status-strip" class="status-strip" aria-label="API status and version"></div>
    <nav id="workspace-navigation" class="workspace-nav" aria-label="Workspace Navigation">
      <h2>Workspace Navigation</h2>
      <div class="muted">Jump between read-only analysis sections without changing filters or running the pipeline.</div>
      <div class="nav-links">
        <a href="#morning-brief">Morning Brief</a>
        <a href="#daily-research-brief">Daily Research Brief</a>
        <a href="#research-review-queue">Research Review Queue</a>
        <a href="#date-compare">Date Compare</a>
        <a href="#console-controls">Controls</a>
        <a href="#theme-hotlist">Theme Hotlist</a>
        <a href="#source-reliability">Source Reliability</a>
        <a href="#theme-source-matrix">Theme &times; Source Matrix</a>
        <a href="#theme-compare">Theme Compare</a>
        <a href="#historical-review">Historical Review</a>
        <a href="#signal-explorer">Signal Explorer</a>
        <a href="#signal-detail">Signal Detail</a>
        <a href="#theme-detail">Theme Detail</a>
        <a href="#source-detail">Source Detail</a>
        <a href="#artifact-links">Artifacts</a>
      </div>
    </nav>
  </header>
  <main>
    <section class="section-card">
      <h2>Daily Runs</h2>
      <div id="runs-status" class="muted">Loading runs...</div>
      <div class="controls">
        <div>
          <label for="run-select">Run Date</label>
          <select id="run-select"></select>
        </div>
        <button id="refresh-runs" type="button">Refresh Runs</button>
      </div>
      <div id="runs"></div>
    </section>
    <section class="section-card">
      <h2>Dashboard Data</h2>
      <div id="dashboard-status" class="muted">Select a run to load dashboard data.</div>
      <p class="muted section-description">Adjust the read-only view by date, search text, risk, status, sort order, and layout mode.</p>
      <div id="console-controls" class="controls signal-controls">
        <div>
          <label for="signal-search">Signal Search</label>
          <input id="signal-search" type="search" placeholder="Search theme, trigger, candidate, risk">
        </div>
        <div>
          <label for="risk-filter">Risk Filter</label>
          <select id="risk-filter">
            <option value="">All risks</option>
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
            <option value="unknown">unknown</option>
          </select>
        </div>
        <div>
          <label for="status-filter">Status Filter</label>
          <select id="status-filter">
            <option value="">All statuses</option>
            <option value="confirmed">confirmed</option>
            <option value="downgraded">downgraded</option>
            <option value="failed">failed</option>
            <option value="missing_data">missing_data</option>
            <option value="not_checked">not_checked</option>
            <option value="unknown">unknown</option>
          </select>
        </div>
        <div>
          <label for="sort-select">Sort Signals</label>
          <select id="sort-select">
            <option value="default">Default order</option>
            <option value="score_desc">Score descending</option>
            <option value="risk_level">Risk level</option>
            <option value="intraday_status">Intraday status</option>
            <option value="theme">Theme name</option>
          </select>
        </div>
        <div>
          <label for="view-mode">View</label>
          <select id="view-mode">
            <option value="grouped">Grouped by theme</option>
            <option value="flat">Flat signal list</option>
          </select>
        </div>
      </div>
      <div id="signal-count" class="muted">No signals loaded.</div>
      <a class="back-to-top" href="#workspace-navigation">Back to top</a>
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
    let briefMode = "full";
    let briefLang = "en";
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
    const VALID_BRIEF_LANGS = new Set(["en", "zh"]);
    const VALID_BRIEF_MODES = new Set(["full", "compact"]);
    const VALID_REVIEW_SEVERITIES = new Set(["", "high", "medium", "low", "info"]);
    const VALID_REVIEW_CATEGORIES = new Set(["", "weak_evidence", "missing_source", "missing_fetched_at", "stale_or_partial_data", "fallback_used", "high_risk_with_weak_data", "date_compare_change", "candidate_pool_change", "theme_source_gap"]);
    const VALID_REVIEW_SCOPES = new Set(["visible", "all"]);
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
      return VALID_BRIEF_LANGS.has(textValue) ? textValue : "en";
    }

    function normalizeBriefMode(value) {
      const textValue = String(value == null ? "" : value).trim().toLowerCase();
      return VALID_BRIEF_MODES.has(textValue) ? textValue : "full";
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
        briefLang: normalizeBriefLang(state.briefLang),
        briefMode: normalizeBriefMode(state.briefMode),
        compareFrom: String(state.compareFrom || "").trim(),
        compareTo: String(state.compareTo || "").trim(),
        reviewSeverity: normalizeChoice(state.reviewSeverity, VALID_REVIEW_SEVERITIES, ""),
        reviewCategory: normalizeChoice(state.reviewCategory, VALID_REVIEW_CATEGORIES, ""),
        reviewScope: normalizeReviewScope(state.reviewScope),
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
        briefLang: params.get("briefLang"),
        briefMode: params.get("briefMode"),
        compareFrom: params.get("compareFrom"),
        compareTo: params.get("compareTo"),
        reviewSeverity: params.get("reviewSeverity"),
        reviewCategory: params.get("reviewCategory"),
        reviewScope: params.get("reviewScope"),
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
      briefLang = normalizedState.briefLang;
      briefMode = normalizedState.briefMode;
      compareFromDate = normalizedState.compareFrom;
      compareToDate = normalizedState.compareTo;
      reviewSeverity = normalizedState.reviewSeverity;
      reviewCategory = normalizedState.reviewCategory;
      reviewScope = normalizedState.reviewScope;
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
        briefLang,
        briefMode,
        compareFrom: compareFromDate,
        compareTo: compareToDate,
        reviewSeverity,
        reviewCategory,
        reviewScope,
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
      if (state.briefLang !== "en") params.set("briefLang", state.briefLang);
      if (state.briefMode !== "full") params.set("briefMode", state.briefMode);
      if (state.compareFrom) params.set("compareFrom", state.compareFrom);
      if (state.compareTo) params.set("compareTo", state.compareTo);
      if (state.reviewSeverity) params.set("reviewSeverity", state.reviewSeverity);
      if (state.reviewCategory) params.set("reviewCategory", state.reviewCategory);
      if (state.reviewScope !== "visible") params.set("reviewScope", state.reviewScope);
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
      node.appendChild(anchorLink("#workspace-navigation", "Back to top", "back-to-top"));
      return node;
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
      if (status.includes("missing")) return "Missing Data";
      if (status.includes("partial")) return "Partial";
      if (status.includes("stale")) return "Stale";
      if (status === "ok") return "Data OK";
      if (status === "fresh") return "Fresh";
      return "Unknown";
    }

    function dataQualityItems(signal) {
      const items = [dataStatusLabel(signal.data_status)];
      const sources = sourceValues(signal);
      items.push(sources.length ? `Sources: ${sources.join(", ")}` : "Sources: Unknown");
      const fetched = fetchedValues(signal);
      items.push(fetched.length ? `Fetched: ${fetched.join(", ")}` : "Fetched: Unknown");
      if (signal.fallback_used === true || normalized(signal.fallback_used) === "true") items.push("Fallback Source");
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
        dashboard_html: "Dashboard",
        dashboard_data_json: "Dashboard Data",
        run_summary_json: "Run Summary",
        knowledge_review_html: "Knowledge Review",
        run_diagnostics_html: "Run Diagnostics",
        knowledge_check_json: "Knowledge Check",
        knowledge_fix_suggestions_json: "Knowledge Fix Suggestions",
        report_md: "Report Markdown",
      };
      return labels[key] || fallback || "artifact";
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
        compareNotice = `${normalizedTheme} is already in compare.`;
      } else if (compareThemes.length >= MAX_COMPARE_THEMES) {
        compareNotice = "Compare supports up to 3 themes.";
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

    function createCompareButton(theme, label = "Compare") {
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
      return values.slice(0, 5).join(", ") || "No external triggers provided.";
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
      if (!sources.length) reasons.push("Unknown source");
      if (!fetched.length) reasons.push("Missing fetched_at");
      if (hasFallback(signal)) reasons.push("Fallback used");
      if (normalized(signal.risk_level) === "high" && isWeakDataStatus(dataStatus)) reasons.push("High risk with weak data quality");
      return uniqueValues(reasons, 6);
    }

    function reviewSeverityRank(value) {
      return { high: 4, medium: 3, low: 2, info: 1 }[normalized(value)] || 0;
    }

    function reviewSeverityLabel(value) {
      const textValue = normalized(value || "info");
      return textValue.charAt(0).toUpperCase() + textValue.slice(1);
    }

    function reviewCategoryLabel(value) {
      const labels = {
        weak_evidence: "Weak Evidence",
        missing_source: "Missing Source",
        missing_fetched_at: "Missing Fetched At",
        stale_or_partial_data: "Stale / Partial Data",
        fallback_used: "Fallback Used",
        high_risk_with_weak_data: "High Risk + Weak Data",
        date_compare_change: "Date Compare Change",
        candidate_pool_change: "Candidate Pool Change",
        theme_source_gap: "Theme-Source Evidence Gap",
      };
      return labels[value] || "All Categories";
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
        action: options.action || "Review evidence context before using this observation in the research brief.",
        context: options.context || "",
        signalIndex: options.signalIndex,
      };
    }

    function reviewSignalContext(signal) {
      return [
        `strength ${signal.strength || "unknown"}`,
        `score ${signal.score ?? "unknown"}`,
        `risk ${signal.risk_level || "unknown"}`,
        `status ${signal.intraday_status || signal.status || "not_checked"}`,
        `data ${signal.data_status || "unknown"}`,
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
        if (reasons.length) {
          pushUniqueReviewItem(items, reviewItem("weak_evidence", normalized(signal.risk_level) === "high" ? "high" : "medium", `Needs verification: ${reasons.join(", ")}.`, { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (!sources.length) {
          pushUniqueReviewItem(items, reviewItem("missing_source", "medium", "Source is missing for this signal.", { theme, source: "Unknown Source", context, signalIndex: signal.__index }));
        }
        if (!fetched.length) {
          pushUniqueReviewItem(items, reviewItem("missing_fetched_at", "medium", "fetched_at is missing, so freshness needs confirmation.", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (isWeakDataStatus(dataStatus)) {
          const severity = ["missing", "missing_data", "failed"].includes(normalized(dataStatus)) ? "high" : "medium";
          pushUniqueReviewItem(items, reviewItem("stale_or_partial_data", severity, `Data status is ${dataStatus}.`, { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (hasFallback(signal)) {
          pushUniqueReviewItem(items, reviewItem("fallback_used", "low", "Fallback source was used.", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
        if (normalized(signal.risk_level) === "high" && isWeakDataStatus(dataStatus)) {
          pushUniqueReviewItem(items, reviewItem("high_risk_with_weak_data", "high", "High risk theme also has weak data quality.", { theme, source: sourceLabel, context, signalIndex: signal.__index }));
        }
      }
      return items;
    }

    function buildMatrixReviewItems() {
      const rows = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      return rows.map((cell) => reviewItem("theme_source_gap", Number(cell.weak_signal_count || 0) > 1 ? "high" : "medium", cell.reason || "Theme-source pair needs evidence review.", {
        theme: cell.theme || "Unknown Theme",
        source: cell.source || "Unknown Source",
        context: `weak signals ${cell.weak_signal_count || 0}`,
        action: "Open matrix context and verify source coverage, freshness, and data status.",
      }));
    }

    function buildDateCompareReviewItems() {
      if (!dateCompareData || dateCompareData.available === false) return [];
      const summary = dateCompareData.summary || {};
      const items = [];
      if (Number(summary.changed_themes_count || 0) > 0) {
        pushUniqueReviewItem(items, reviewItem("date_compare_change", "medium", `${summary.changed_themes_count} themes changed between compared runs.`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "Review score, risk, status, and data quality deltas before quoting the change.",
        }));
      }
      if (Number(summary.weaker_data_quality_count || 0) > 0) {
        pushUniqueReviewItem(items, reviewItem("date_compare_change", "high", `${summary.weaker_data_quality_count} themes show weaker evidence quality in the comparison.`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "Check whether the change is due to missing source, missing fetched_at, fallback, or data_status.",
        }));
      }
      const newEtf = Number(summary.new_etf_candidates_count || 0);
      const newStock = Number(summary.new_stock_candidates_count || 0);
      if (newEtf + newStock > 0) {
        pushUniqueReviewItem(items, reviewItem("candidate_pool_change", "low", `${newEtf} new ETF and ${newStock} new stock observation candidates appeared in the comparison.`, {
          context: `${dateCompareData.from_date || "unknown"} -> ${dateCompareData.to_date || "unknown"}`,
          action: "Review candidate pool changes as observation context, not as an action list.",
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
        `API version: ${apiVersionData?.api_version || apiHealthData?.version || "Unknown"}`,
        `Schema: ${schema}`,
        `Run date: ${run.date || runSelectEl.value || "unknown"}`,
        `Signals: ${currentSignals.length}`,
        `Visible: ${visibleSignalCount}`,
        `Generated: ${run.generated_at || "unknown"}`,
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
        dateCompareData = { available: false, notes: [`Date compare unavailable: ${error.message}`], summary: {}, themes: { new: [], removed: [], changed: [] }, candidates: { etf: {}, stock: {} }, data_quality: {}, sources: {} };
      }
      renderSignalSections();
    }

    function renderRuns(payload) {
      clear(runsEl);
      clear(runSelectEl);
      const runs = Array.isArray(payload.runs) ? payload.runs : [];
      const state = readConsoleStateFromUrl();
      syncControlsFromState(state);
      setStatus(runsStatusEl, `${runs.length} runs found`);
      if (runs.length === 0) {
        runSelectEl.disabled = true;
        runsEl.appendChild(text("p", "No daily runs found.", "muted"));
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
        button.appendChild(text("span", `status: ${run.status || "unknown"}`, "muted"));
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
      section.appendChild(text("summary", "Artifact Links"));
      section.appendChild(description("Artifacts for the current run. Missing files are shown as unavailable."));
      const items = Array.isArray(payload && payload.artifacts) ? payload.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "No artifact index available.", "muted"));
        return appendBackToTop(section);
      }
      const ul = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        const status = item.exists ? "available" : "unavailable";
        li.appendChild(text("span", `${artifactLabel(item.key, item.file_name)}: ${status}`, item.exists ? "" : "error"));
        if (item.exists && item.api) {
          li.appendChild(text("span", " "));
          li.appendChild(link(item.api, "open API"));
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
        section.appendChild(text("p", "No historical observations available.", "muted"));
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
        row.forEach((value) => tr.appendChild(text("td", value == null || value === "" ? "unknown" : value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalThemeTrends(themes) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Historical Theme Trends"));
      const rows = themes.slice(0, 10);
      if (!rows.length) {
        section.appendChild(text("p", "No historical observations available.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Theme", "Signals", "Runs seen", "Max score", "Avg score", "Main risk", "Main status", "Last seen", "Recent dates", "Compare"].forEach((label) => header.appendChild(text("th", label)));
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
        compareCell.appendChild(createCompareButton(item.theme, "Compare"));
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
      section.appendChild(text("summary", "Historical Review"));
      section.appendChild(description("Historical signals are observation clues from existing daily reports, not a trading backtest or recommendation."));
      const themes = Array.isArray(themeHistoryData?.themes) ? themeHistoryData.themes : [];
      const etfs = Array.isArray(candidateHistoryData?.etf_candidates) ? candidateHistoryData.etf_candidates : [];
      const stocks = Array.isArray(candidateHistoryData?.stock_candidates) ? candidateHistoryData.stock_candidates : [];
      const summary = document.createElement("div");
      summary.className = "history-grid";
      summary.appendChild(metric("History runs", themeHistoryData?.runs_count ?? "unknown"));
      summary.appendChild(metric("Date range", `${themeHistoryData?.date_range?.start || "unknown"} to ${themeHistoryData?.date_range?.end || "unknown"}`));
      summary.appendChild(metric("Themes observed", themes.length));
      summary.appendChild(metric("Observation candidates", etfs.length + stocks.length));
      section.appendChild(summary);

      section.appendChild(renderHistoricalThemeTrends(themes));

      const candidateRows = etfs.slice(0, 10).map((item) => ["ETF", item.name, item.code || "unknown", item.appearances, (item.themes || []).join(", "), item.last_seen || "unknown"])
        .concat(stocks.slice(0, 10).map((item) => ["Stock", item.name, item.code || "unknown", item.appearances, (item.themes || []).join(", "), item.last_seen || "unknown"]));
      section.appendChild(renderHistoryTable("Recurring Observation Candidates", ["Type", "Name", "Code", "Appearances", "Themes", "Last seen"], candidateRows));

      const dataCounts = {};
      for (const theme of themes) {
        const counts = theme.data_status_counts && typeof theme.data_status_counts === "object" ? theme.data_status_counts : {};
        for (const [key, count] of Object.entries(counts)) dataCounts[key] = (dataCounts[key] || 0) + Number(count || 0);
      }
      const qualityRows = Object.entries(dataCounts).sort((left, right) => Number(right[1]) - Number(left[1])).map(([status, count]) => [status, count]);
      section.appendChild(renderHistoryTable("Data Quality Trend", ["Data status", "Observations"], qualityRows));
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
      card.setAttribute("aria-label", `Open signal detail for ${themeName(signal)}`);
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
      [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => card.appendChild(badge(value)));
      dataQualityItems(signal).forEach((value) => card.appendChild(badge(value)));
      card.appendChild(text("p", signal.a_share_mapping_reason || "No mapping reason provided.", "muted"));
      [["External triggers", signal.external_triggers], ["ETF candidates", signal.etf_candidates], ["Stock candidates", signal.stock_candidates], ["Risks", signal.risks]].forEach(([label, values]) => {
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
      section.appendChild(text("h3", "Data Quality / Freshness"));
      dataQualityItems(signal).forEach((value) => section.appendChild(badge(value)));
      section.appendChild(text("p", "Data quality labels describe available source metadata only. They are not a trading signal.", "muted"));
      return section;
    }

    function renderCandidateTable(title, values) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", title));
      const rows = candidateRows(values);
      if (rows.length === 0) {
        section.appendChild(text("p", "No candidates available.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "candidate-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Name", "Code / ticker", "Category / sector", "Reason", "Risk / note"].forEach((label) => header.appendChild(text("th", label)));
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
      section.appendChild(text("h3", "Evidence Chain"));
      const chain = document.createElement("ol");
      chain.className = "evidence-chain";
      [
        ["External Move", arrayValue(signal.external_triggers).join(", ") || "unknown"],
        ["A-share Theme Mapping", firstText(signal.a_share_mapping_reason)],
        ["Candidate Pools", `${arrayValue(signal.etf_candidates).length} ETF candidates, ${arrayValue(signal.stock_candidates).length} stock candidates`],
        ["Risk Notes", arrayValue(signal.risks).join(", ") || "No risk notes provided."],
        ["Data Quality", dataQualityItems(signal).join(" | ")],
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
      section.appendChild(text("h3", "Related Artifact Links"));
      const items = Array.isArray(currentArtifacts && currentArtifacts.artifacts) ? currentArtifacts.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "No artifact links available.", "muted"));
        return section;
      }
      const ul = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        li.appendChild(text("span", `${artifactLabel(item.key, item.file_name)}: ${item.exists ? "available" : "unavailable"}`, item.exists ? "" : "error"));
        if (item.exists && item.api) {
          li.appendChild(text("span", " "));
          li.appendChild(link(item.api, "open API"));
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
      panel.appendChild(text("h2", "Signal Detail Panel"));
      panel.appendChild(description("Inspect one visible signal's triggers, mapping reason, observation pools, risk notes, and data quality."));
      if (!signal) {
        panel.appendChild(text("p", "No signals match the current filters.", "muted"));
        return appendBackToTop(panel);
      }
      panel.appendChild(text("h3", themeName(signal)));
      panel.appendChild(text("h3", "Overview"));
      [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(renderDataQualitySection(signal));
      panel.appendChild(renderValueList("Sources", sourceValues(signal)));
      sourceValues(signal).forEach((source) => panel.appendChild(createSourceButton(source, `Open source: ${source}`)));
      if (!sourceValues(signal).length) panel.appendChild(createSourceButton("Unknown Source", "Open source: Unknown Source"));
      panel.appendChild(renderValueList("External Triggers", signal.external_triggers));
      panel.appendChild(renderValueList("A-share Mapping Reason", signal.a_share_mapping_reason));
      panel.appendChild(renderEvidenceChain(signal));
      panel.appendChild(renderCandidateTable("ETF observation pool", signal.etf_candidates));
      panel.appendChild(renderCandidateTable("Stock observation pool", signal.stock_candidates));
      panel.appendChild(renderValueList("Risk Notes", signal.risks));
      panel.appendChild(renderDetailArtifactLinks());
      const details = document.createElement("details");
      details.className = "detail-section";
      details.appendChild(text("summary", "Raw signal JSON"));
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
        section.appendChild(text("p", "No historical distribution available.", "muted"));
        return section;
      }
      entries.sort((left, right) => Number(right[1]) - Number(left[1]) || left[0].localeCompare(right[0]));
      entries.forEach(([key, count]) => section.appendChild(badge(`${key}: ${count}`)));
      return section;
    }

    function renderThemeSignalList(theme, visibleSignals) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Current Theme Signals"));
      const signals = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      if (signals.length === 0) {
        section.appendChild(text("p", "No signal for the selected run under current filters.", "muted"));
        return section;
      }
      signals.forEach((signal) => {
        const item = document.createElement("article");
        item.className = "theme-card";
        item.appendChild(text("h3", themeName(signal)));
        [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => item.appendChild(badge(value)));
        item.appendChild(renderValueList("External Triggers", signal.external_triggers));
        item.appendChild(renderValueList("A-share Mapping Reason", signal.a_share_mapping_reason));
        item.appendChild(renderValueList("Risks", signal.risks));
        item.appendChild(renderValueList("Fetched At", fetchedValues(signal)));
        item.appendChild(renderValueList("Sources", sourceValues(signal)));
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
        section.appendChild(text("p", "No recurring candidates found for this theme.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "candidate-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Name", "Code / ticker", "Appearances", "Recent dates", "Last seen"].forEach((label) => header.appendChild(text("th", label)));
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
      panel.appendChild(text("h2", "Theme Detail"));
      panel.appendChild(description("Review one watch theme across current signals, local history, observation pools, risks, and data quality."));
      const theme = selectedTheme || (visibleSignals[0] ? themeName(visibleSignals[0]) : "");
      if (!theme) {
        panel.appendChild(text("p", "Select a theme from Theme Hotlist, Historical Theme Trends, a signal card, or grouped theme header.", "muted"));
        return appendBackToTop(panel);
      }
      const currentSignalsForTheme = currentSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const visibleSignalsForTheme = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const history = themeHistoryItem(theme);
      const etfs = candidateHistoryForTheme(candidateHistoryData?.etf_candidates, theme);
      const stocks = candidateHistoryForTheme(candidateHistoryData?.stock_candidates, theme);

      panel.appendChild(text("h3", theme));
      panel.appendChild(createCompareButton(theme, "Add to Compare"));
      panel.appendChild(text("h3", "Overview"));
      [
        `today signals: ${currentSignalsForTheme.length}`,
        `visible signals: ${visibleSignalsForTheme.length}`,
        `today highest score: ${topScore(currentSignalsForTheme)}`,
        `today strongest: ${strongestStrength(currentSignalsForTheme)}`,
        `today main status: ${mainStatus(currentSignalsForTheme)}`,
        `today main risk: ${maxRisk(currentSignalsForTheme)}`,
        `historical signals: ${history?.signal_count ?? "unknown"}`,
        `runs seen: ${history?.runs_seen ?? "unknown"}`,
        `avg score: ${history?.avg_score ?? "unknown"}`,
        `max score: ${history?.max_score ?? "unknown"}`,
        `last seen: ${history?.last_seen || "unknown"}`,
      ].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(text("p", "Theme drilldown is a research view over existing observations. It does not imply an action, pricing claim, or future outcome.", "muted"));

      if (!history && currentSignalsForTheme.length === 0) {
        panel.appendChild(text("p", "No current or historical observations found for this theme.", "muted"));
      }
      panel.appendChild(renderThemeSignalList(theme, visibleSignals));
      panel.appendChild(renderCountBadges("Historical Risk Distribution", history?.risk_counts));
      panel.appendChild(renderCountBadges("Historical Intraday Status Distribution", history?.intraday_status_counts));
      panel.appendChild(renderCountBadges("Historical Data Status Distribution", history?.data_status_counts));
      panel.appendChild(renderValueList("Recent Dates", history?.recent_dates || []));
      panel.appendChild(renderValueList("External Trigger Summary", history?.external_triggers || currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers))));
      panel.appendChild(renderValueList("Risk Summary", currentSignalsForTheme.flatMap((signal) => arrayValue(signal.risks))));
      panel.appendChild(renderValueList("Data Quality Summary", currentSignalsForTheme.flatMap((signal) => dataQualityItems(signal))));
      panel.appendChild(renderValueList("Needs Verification", currentSignalsForTheme.flatMap((signal) => weakEvidenceReasons(signal))));
      panel.appendChild(renderThemeCandidateHistory("ETF observation pool", etfs));
      panel.appendChild(renderThemeCandidateHistory("Stock observation pool", stocks));
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
        .map((item) => `${item.name || "unknown"} (${item.appearances || 0} appearances)`);
    }

    function briefTopThemes(signals, limit = 5) {
      return groupedSignals(signals).slice(0, limit).map((group) => {
        const signal = group.signals[0] || {};
        const triggers = uniqueValues(group.signals.flatMap((item) => arrayValue(item.external_triggers)), 3).join(", ") || "unknown";
        const mapping = signal.a_share_mapping_reason || "not available";
        return `- ${group.theme}: score ${topScore(group.signals)}, strength ${strongestStrength(group.signals)}, status ${mainStatus(group.signals)}, risk ${maxRisk(group.signals)}, data ${distribution(group.signals, "data_status", "unknown")}. Triggers: ${triggers}. Mapping: ${mapping}`;
      });
    }

    function briefLines(title, lines) {
      const safeLines = Array.isArray(lines) && lines.length ? lines : ["- not available"];
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
      section.appendChild(text("h2", "Daily Research Brief"));
      section.appendChild(description("Build a copyable research summary from the current filters, watch themes, evidence chains, candidate pools, risks, and data quality notes."));
      const controls = document.createElement("div");
      controls.className = "research-brief-controls";
      const langField = document.createElement("div");
      const langLabel = document.createElement("label");
      langLabel.setAttribute("for", "brief-language-select");
      langLabel.textContent = "Brief Language";
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
      label.textContent = "Brief Mode";
      const select = document.createElement("select");
      select.id = "brief-mode-select";
      [["full", "Full Brief"], ["compact", "Compact Brief"]].forEach(([value, title]) => {
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
      copyMarkdown.textContent = "Copy as Markdown";
      const copyPlain = document.createElement("button");
      copyPlain.type = "button";
      copyPlain.className = "inline-action";
      copyPlain.textContent = "Copy as Plain Text";
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
      section.appendChild(text("h3", "Section toggles"));
      section.appendChild(toggleWrap);
      if (briefMode === "compact") {
        section.appendChild(text("p", "Compact brief uses a reduced section set.", "muted"));
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
      textarea.setAttribute("aria-label", "Generated daily research brief");
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
      section.appendChild(text("h2", "Research Review Queue"));
      section.appendChild(description("A read-only checklist of evidence, source, freshness, matrix, and date-compare items that may need human research review."));
      const controls = document.createElement("div");
      controls.className = "review-controls";
      controls.appendChild(renderReviewSelect("review-severity-filter", "Review Severity", [
        ["", "All severities"],
        ["high", "High"],
        ["medium", "Medium"],
        ["low", "Low"],
        ["info", "Info"],
      ], reviewSeverity, (value) => {
        reviewSeverity = normalizeChoice(value, VALID_REVIEW_SEVERITIES, "");
        updateQueryState({ reviewSeverity });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("review-category-filter", "Review Category", [
        ["", "All categories"],
        ["weak_evidence", "Weak Evidence"],
        ["missing_source", "Missing Source"],
        ["missing_fetched_at", "Missing Fetched At"],
        ["stale_or_partial_data", "Stale / Partial Data"],
        ["fallback_used", "Fallback Used"],
        ["high_risk_with_weak_data", "High Risk + Weak Data"],
        ["date_compare_change", "Date Compare Change"],
        ["candidate_pool_change", "Candidate Pool Change"],
        ["theme_source_gap", "Theme-Source Evidence Gap"],
      ], reviewCategory, (value) => {
        reviewCategory = normalizeChoice(value, VALID_REVIEW_CATEGORIES, "");
        updateQueryState({ reviewCategory });
        renderSignalSections();
      }));
      controls.appendChild(renderReviewSelect("review-scope-select", "Review Scope", [
        ["visible", "Current visible signals"],
        ["all", "Current run and history"],
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
        ["Review items", filteredItems.length],
        ["High severity", reviewSummaryCount(filteredItems, (item) => item.severity === "high")],
        ["Weak evidence", reviewSummaryCount(filteredItems, (item) => item.category === "stale_or_partial_data" || item.category === "high_risk_with_weak_data")],
        ["Source gaps", reviewSummaryCount(filteredItems, (item) => item.category === "missing_source" || item.category === "missing_fetched_at")],
        ["Matrix gaps", reviewSummaryCount(filteredItems, (item) => item.category === "theme_source_gap")],
        ["Date compare notes", reviewSummaryCount(filteredItems, (item) => item.category === "date_compare_change" || item.category === "candidate_pool_change")],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(text("h3", "Review Queue Summary"));
      section.appendChild(metrics);

      if (!filteredItems.length) {
        section.appendChild(text("p", "No review items for the current view.", "muted"));
        return appendBackToTop(section);
      }

      const shownItems = filteredItems.slice(0, 20);
      section.appendChild(text("p", filteredItems.length > shownItems.length ? `Showing top ${shownItems.length} review items of ${filteredItems.length}.` : `Showing ${shownItems.length} review items.`, "muted"));
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Severity", "Category", "Theme", "Source", "Reason", "Suggested research action", "Context"].forEach((label) => header.appendChild(text("th", label)));
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
        else themeCell.appendChild(text("span", "not available", "muted"));
        row.appendChild(themeCell);
        const sourceCell = document.createElement("td");
        if (item.source) sourceCell.appendChild(createSourceButton(item.source));
        else sourceCell.appendChild(text("span", "not available", "muted"));
        row.appendChild(sourceCell);
        row.appendChild(text("td", item.reason));
        row.appendChild(text("td", item.action));
        const contextCell = document.createElement("td");
        contextCell.appendChild(text("div", item.context || "not available"));
        if (item.theme && item.source) {
          const matrixButton = document.createElement("button");
          matrixButton.type = "button";
          matrixButton.className = "inline-action";
          matrixButton.textContent = "Open matrix context";
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

    function renderMorningBrief(visibleSignals) {
      const section = document.createElement("article");
      section.id = "morning-brief";
      section.className = "morning-brief section-card";
      section.appendChild(text("h2", "Morning Brief"));
      section.appendChild(description("High-level summary of today's overseas-to-A-share watch themes and data quality notes."));
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
        .map((item) => `${item.theme || "Unknown Theme"} (${item.runs_seen || 0} runs)`);
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
        .map(([status, count]) => `${status}: ${count}`);
      const briefGrid = document.createElement("div");
      briefGrid.className = "theme-summary";
      [
        ["Run date", run.date || runSelectEl.value || "unknown"],
        ["Signals", currentSignals.length],
        ["Visible signals", visibleSignals.length],
        ["Status overview", Object.entries(statusCounts).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown"],
        ["Data quality notes", qualityNotes.join(", ") || "No missing, partial, stale, or unknown data labels in current signals."],
        ["Needs verification", `${weakSignals.length} signals need data verification.`],
        ["Research review queue", `${reviewItems.length} review items, including ${highReviewItems.length} high priority items.`],
        ["Matrix review", `${weakMatrixCells.length} theme-source pairs need evidence review.`],
        ["Requires confirmation", highRiskThemes.length ? `High risk themes: ${highRiskThemes.join(", ")}` : "No high risk themes in current signals."],
      ].forEach(([label, value]) => briefGrid.appendChild(metric(label, value)));
      section.appendChild(briefGrid);
      section.appendChild(renderBriefList("Today's core observations", strongThemes));
      section.appendChild(renderBriefList("Historical recurring themes", recurringThemes));
      section.appendChild(renderBriefList("Recurring ETF observation candidates", topEtfs));
      section.appendChild(renderBriefList("Recurring stock observation candidates", topStocks));
      return appendBackToTop(section);
    }

    function renderCompareSelector() {
      const wrap = document.createElement("div");
      wrap.className = "compare-actions";
      const field = document.createElement("div");
      const label = document.createElement("label");
      label.setAttribute("for", "compare-theme-select");
      label.textContent = "Theme selector";
      const select = document.createElement("select");
      select.id = "compare-theme-select";
      const themes = availableThemeNames();
      if (!themes.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No themes available";
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
      button.textContent = "Add to Compare";
      button.disabled = !themes.length;
      button.addEventListener("click", () => addCompareTheme(select.value));
      wrap.appendChild(field);
      wrap.appendChild(button);
      return wrap;
    }

    function renderCompareEvidence(theme, currentSignalsForTheme, etfs, stocks) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Evidence Chain"));
      const history = themeHistoryItem(theme);
      const triggers = uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers)).concat(arrayValue(history?.external_triggers)), 5);
      const mappings = uniqueValues(currentSignalsForTheme.map((signal) => signal.a_share_mapping_reason), 3);
      const risks = uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.risks)), 5);
      const chain = document.createElement("ol");
      chain.className = "evidence-chain";
      [
        ["External Move", triggers.join(", ") || "unknown"],
        ["A-share Theme Mapping", mappings.join(" | ") || "unknown"],
        ["Candidate Pools", `${etfs.length} ETF observation candidates, ${stocks.length} stock observation candidates`],
        ["Risk Notes", risks.join(", ") || "No risk notes provided."],
        ["Data Quality", distribution(currentSignalsForTheme, "data_status", "unknown")],
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
      remove.textContent = "Remove";
      remove.addEventListener("click", () => removeCompareTheme(theme));
      card.appendChild(remove);
      const currentSignalsForTheme = currentSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const visibleSignalsForTheme = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const history = themeHistoryItem(theme);
      const etfs = candidateHistoryForTheme(candidateHistoryData?.etf_candidates, theme);
      const stocks = candidateHistoryForTheme(candidateHistoryData?.stock_candidates, theme);
      [
        `today signals: ${currentSignalsForTheme.length}`,
        `visible signals: ${visibleSignalsForTheme.length}`,
        `highest score: ${topScore(currentSignalsForTheme)}`,
        `strongest: ${strongestStrength(currentSignalsForTheme)}`,
        `main status: ${mainStatus(currentSignalsForTheme)}`,
        `main risk: ${maxRisk(currentSignalsForTheme)}`,
        `data status: ${distribution(currentSignalsForTheme, "data_status", "unknown")}`,
        `historical signals: ${history?.signal_count ?? "unknown"}`,
        `runs seen: ${history?.runs_seen ?? "unknown"}`,
        `avg score: ${history?.avg_score ?? "unknown"}`,
        `max score: ${history?.max_score ?? "unknown"}`,
        `last seen: ${history?.last_seen || "unknown"}`,
        `ETF pool: ${etfs.length}`,
        `stock pool: ${stocks.length}`,
      ].forEach((value) => card.appendChild(badge(value)));
      if (currentSignalsForTheme.length === 0 && !history) {
        card.appendChild(text("p", "No current or historical observations found for this theme.", "muted"));
      } else if (visibleSignalsForTheme.length === 0) {
        card.appendChild(text("p", "No visible signal for this theme under the current filters. Historical context is still shown when available.", "muted"));
      }
      card.appendChild(renderCountBadges("Historical Risk Distribution", history?.risk_counts));
      card.appendChild(renderCountBadges("Historical Intraday Status Distribution", history?.intraday_status_counts));
      card.appendChild(renderCountBadges("Historical Data Status Distribution", history?.data_status_counts));
      card.appendChild(renderValueList("Recent Dates", history?.recent_dates || []));
      card.appendChild(renderValueList("Top external triggers", uniqueValues(currentSignalsForTheme.flatMap((signal) => arrayValue(signal.external_triggers)).concat(arrayValue(history?.external_triggers)), 5)));
      card.appendChild(renderValueList("Needs Verification", currentSignalsForTheme.flatMap((signal) => weakEvidenceReasons(signal))));
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
        section.appendChild(text("p", "Select themes to compare observation pool overlap.", "muted"));
        return section;
      }
      const rows = (Array.isArray(candidates) ? candidates : [])
        .map((candidate) => ({ ...candidate, compared_count: appearsInComparedThemes(candidate) }))
        .filter((candidate) => candidate.compared_count > 0)
        .sort((left, right) => right.compared_count - left.compared_count || Number(right.appearances || 0) - Number(left.appearances || 0))
        .slice(0, 12);
      if (!rows.length) {
        section.appendChild(text("p", "No observation candidate overlap found for selected themes.", "muted"));
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
      section.appendChild(text("h3", "Source Breakdown"));
      const rows = sourceBreakdown(signals);
      if (!rows.length) {
        section.appendChild(text("p", "No source metadata available for current signals.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Source", "Signals", "Themes count", "Latest fetched_at", "Data status counts", "Weak signals", "Fallback count", "Missing fetched_at"].forEach((label) => header.appendChild(text("th", label)));
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
          row.latest_fetched_at || "unknown",
          Object.entries(row.data_status_counts).map(([key, count]) => `${key}: ${count}`).join(", "),
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
      section.appendChild(text("h3", "Weak Evidence Signals"));
      const rows = signals
        .map((signal) => ({ signal, reasons: weakEvidenceReasons(signal) }))
        .filter((item) => item.reasons.length > 0);
      if (!rows.length) {
        section.appendChild(text("p", "No weak evidence signals found in the current run.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Theme", "Strength", "Score", "Risk", "Intraday", "Data status", "Sources", "Fetched at", "Needs verification"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach(({ signal, reasons }) => {
        const tr = document.createElement("tr");
        [themeName(signal), signal.strength || "unknown", signal.score ?? "unknown", signal.risk_level || "unknown", signal.intraday_status || signal.status || "not_checked", signal.data_status || "unknown"].forEach((value) => tr.appendChild(text("td", value)));
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
        [fetchedValues(signal).join(", ") || "unknown", reasons.join(", ")].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalDataQualityTrend() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Historical Data Quality Trend"));
      if (!dataQualityHistoryData || dataQualityHistoryData.runs_count === 0) {
        section.appendChild(text("p", "Not enough historical data.", "muted"));
        return section;
      }
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["History runs", dataQualityHistoryData.runs_count ?? "unknown"],
        ["Missing source", dataQualityHistoryData.missing_source_count ?? 0],
        ["Missing fetched_at", dataQualityHistoryData.missing_fetched_at_count ?? 0],
        ["Fallback used", dataQualityHistoryData.fallback_count ?? 0],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(metrics);
      section.appendChild(renderHistoryTable("Historical data_status counts", ["Data status", "Observations"], Object.entries(dataQualityHistoryData.data_status_counts || {}).map(([key, count]) => [key, count])));
      section.appendChild(renderHistoryTable("Top sources by appearances", ["Source", "Observations"], Object.entries(dataQualityHistoryData.source_counts || {}).sort((left, right) => Number(right[1]) - Number(left[1])).slice(0, 10).map(([key, count]) => [key, count])));
      const weakThemes = Array.isArray(dataQualityHistoryData.themes_with_weak_data) ? dataQualityHistoryData.themes_with_weak_data : [];
      section.appendChild(renderHistoryTable("Themes with weak data", ["Theme", "Weak signals", "Recent dates", "Last seen", "Data status counts"], weakThemes.slice(0, 10).map((item) => [item.theme, item.weak_signal_count, (item.recent_dates || []).join(", "), item.last_seen || "unknown", Object.entries(item.data_status_counts || {}).map(([key, count]) => `${key}: ${count}`).join(", ")])));
      return section;
    }

    function sourceReliabilityNotes(source, item, currentSignalsForSource) {
      const notes = [];
      if (!item && currentSignalsForSource.length === 0) notes.push("Source not found in the selected run or available history.");
      if ((item?.missing_fetched_at_count || 0) > 0 || currentSignalsForSource.some((signal) => !fetchedValues(signal).length)) notes.push("Some signals are missing fetched_at.");
      const weakCount = item?.weak_signal_count || currentSignalsForSource.filter((signal) => weakEvidenceReasons(signal).length).length;
      if (weakCount > 0) notes.push("Some signals have partial, stale, missing, failed, or unknown data status.");
      if ((item?.fallback_count || 0) > 0 || currentSignalsForSource.some(hasFallback)) notes.push("Fallback source was used in some signals.");
      if ((item?.themes || []).length > 1) notes.push("This source appears in multiple themes.");
      if ((item?.signal_count || currentSignalsForSource.length) <= 1) notes.push("Source coverage is limited in the available history.");
      return notes;
    }

    function renderSourceExampleSignals(item) {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Example Signals"));
      const examples = Array.isArray(item?.example_signals) ? item.example_signals : [];
      if (!examples.length) {
        section.appendChild(text("p", "No historical signal examples available for this source.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Date", "Theme", "Strength", "Score", "Risk", "Intraday", "Data status", "Fetched at", "Fallback"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      examples.forEach((signal) => {
        const tr = document.createElement("tr");
        [signal.date, signal.theme, signal.strength, signal.score ?? "unknown", signal.risk_level, signal.intraday_status, signal.data_status, signal.fetched_at || "unknown", signal.fallback_used ?? "unknown"].forEach((value) => tr.appendChild(text("td", value)));
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
      panel.appendChild(text("h2", "Source Detail Panel"));
      panel.appendChild(description("Inspect one data source's coverage, freshness, weak evidence signals, and recent examples."));
      const source = selectedSource || (sourceBreakdown(currentSignalsInput)[0]?.source || "");
      if (!source) {
        panel.appendChild(text("p", "Select a source from Source Breakdown, Weak Evidence Signals, or Signal Detail Panel.", "muted"));
        return appendBackToTop(panel);
      }
      const history = sourceHistoryItem(source);
      const currentSignalsForSource = currentSignalsInput.filter((signal) => signalHasSource(signal, source));
      const visibleSignalsForSource = visibleSignals.filter((signal) => signalHasSource(signal, source));
      panel.appendChild(text("h3", sourceName(source)));
      panel.appendChild(text("h3", "Overview"));
      [
        `current signals: ${currentSignalsForSource.length}`,
        `visible signals: ${visibleSignalsForSource.length}`,
        `historical signals: ${history?.signal_count ?? "unknown"}`,
        `themes: ${(history?.themes || uniqueValues(currentSignalsForSource.map(themeName), 20)).length}`,
        `last seen: ${history?.last_seen || "unknown"}`,
        `latest fetched_at: ${history?.latest_fetched_at || "unknown"}`,
        `fallback count: ${history?.fallback_count ?? currentSignalsForSource.filter(hasFallback).length}`,
        `missing fetched_at: ${history?.missing_fetched_at_count ?? currentSignalsForSource.filter((signal) => !fetchedValues(signal).length).length}`,
        `weak signals: ${history?.weak_signal_count ?? currentSignalsForSource.filter((signal) => weakEvidenceReasons(signal).length).length}`,
      ].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(text("p", "Source detail is an evidence quality view. It does not rank sources as absolute truth or produce trading instructions.", "muted"));
      if (!history && currentSignalsForSource.length === 0) {
        panel.appendChild(text("p", "No current or historical observations found for this source.", "muted"));
      }
      panel.appendChild(renderValueList("Source reliability notes", sourceReliabilityNotes(source, history, currentSignalsForSource)));
      panel.appendChild(renderValueList("Covered themes", history?.themes || uniqueValues(currentSignalsForSource.map(themeName), 20)));
      panel.appendChild(renderValueList("Recent dates", history?.recent_dates || []));
      panel.appendChild(renderCountBadges("Historical data_status distribution", history?.data_status_counts));
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
        ["Themes", themes.length],
        ["Sources", sources.length],
        ["Matrix cells", cells.length],
        ["Weak cells", weakCells.length],
        ["Missing source", missingSource],
        ["Missing fetched_at", missingFetched],
        ["Fallback used", fallback],
        ["Weak data status", weakStatusCount],
      ].forEach(([label, value]) => section.appendChild(metric(label, value)));
      return section;
    }

    function renderMatrixTable() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Matrix Table"));
      const themes = (Array.isArray(themeSourceMatrixData?.themes) ? themeSourceMatrixData.themes : []).slice(0, 12);
      const sources = (Array.isArray(themeSourceMatrixData?.sources) ? [...themeSourceMatrixData.sources] : []).sort((left, right) => Number(right.signal_count || 0) - Number(left.signal_count || 0)).slice(0, 8);
      if (!themes.length || !sources.length) {
        section.appendChild(text("p", "No theme-source matrix data available.", "muted"));
        return section;
      }
      const wrap = document.createElement("div");
      wrap.className = "matrix-table-wrap";
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      header.appendChild(text("th", "Theme / Source"));
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
            button.textContent = `${cell.signal_count} signals`;
            button.addEventListener("click", () => selectMatrixCell(theme.theme, source.source));
            td.appendChild(button);
            td.appendChild(badge(`weak: ${cell.weak_signal_count || 0}`));
            td.appendChild(badge(`missing fetched: ${cell.missing_fetched_at_count || 0}`));
            td.appendChild(badge(`fallback: ${cell.fallback_count || 0}`));
            td.appendChild(text("div", Object.entries(cell.data_status_counts || {}).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown", "muted"));
            td.appendChild(text("div", `latest: ${cell.latest_fetched_at || "unknown"}`, "muted"));
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
      section.appendChild(text("h3", "Cell Detail"));
      const fallbackCell = (Array.isArray(themeSourceMatrixData?.matrix) ? themeSourceMatrixData.matrix : [])[0];
      const theme = selectedMatrixTheme || fallbackCell?.theme || "";
      const source = selectedMatrixSource || fallbackCell?.source || "";
      if (!theme || !source) {
        section.appendChild(text("p", "Select a matrix cell to inspect theme-source evidence.", "muted"));
        return section;
      }
      const cell = matrixCellItem(theme, source);
      section.appendChild(text("h3", `${theme} / ${source}`));
      if (!cell) {
        section.appendChild(text("p", "No signals for this theme-source pair.", "muted"));
        return section;
      }
      section.appendChild(text("h3", "Overview"));
      [
        `signals: ${cell.signal_count}`,
        `weak signals: ${cell.weak_signal_count || 0}`,
        `missing fetched_at: ${cell.missing_fetched_at_count || 0}`,
        `fallback: ${cell.fallback_count || 0}`,
        `last seen: ${cell.last_seen || "unknown"}`,
        `latest fetched_at: ${cell.latest_fetched_at || "unknown"}`,
      ].forEach((value) => section.appendChild(badge(value)));
      section.appendChild(renderCountBadges("Cell data_status distribution", cell.data_status_counts));
      section.appendChild(renderValueList("Recent Dates", cell.recent_dates || []));
      const examples = Array.isArray(cell.example_signals) ? cell.example_signals : [];
      section.appendChild(renderHistoryTable("Example signals", ["Date", "Strength", "Score", "Risk", "Intraday", "Data status", "Fetched at", "Fallback"], examples.map((signal) => [signal.date, signal.strength, signal.score ?? "unknown", signal.risk_level, signal.intraday_status, signal.data_status, signal.fetched_at || "unknown", signal.fallback_used ?? "unknown"])));
      return section;
    }

    function renderWeakEvidenceCells() {
      const section = document.createElement("div");
      section.className = "detail-section";
      section.appendChild(text("h3", "Weak Evidence Cells"));
      const rows = Array.isArray(themeSourceMatrixData?.weak_cells) ? themeSourceMatrixData.weak_cells : [];
      if (!rows.length) {
        section.appendChild(text("p", "No theme-source evidence gaps found in available history.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Theme", "Source", "Reason", "Weak signals", "Missing fetched_at", "Fallback", "Data status counts", "Recent dates"].forEach((label) => header.appendChild(text("th", label)));
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
        [row.reason, row.weak_signal_count, row.missing_fetched_at_count, row.fallback_count, Object.entries(row.data_status_counts || {}).map(([key, count]) => `${key}: ${count}`).join(", "), (row.recent_dates || []).join(", ")].forEach((value) => tr.appendChild(text("td", value)));
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
      section.appendChild(text("h2", "Theme × Source Matrix"));
      section.appendChild(text("p", "Theme-source evidence review across existing local daily reports. Matrix cells highlight source coverage and evidence gaps, not trading signals.", "muted"));
      section.appendChild(text("h3", "Matrix Summary"));
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
      section.appendChild(text("h2", "Source Reliability"));
      section.appendChild(description("Check source coverage, freshness, missing data, and weak evidence signals."));
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
        ["Total signals", currentSignals.length],
        ["Signals with sources", withSources],
        ["Signals without sources", currentSignals.length - withSources],
        ["Signals with fetched_at", withFetched],
        ["Signals without fetched_at", currentSignals.length - withFetched],
        ["Fallback used", fallbackCount],
        ["Needs verification", weakSignals.length],
        ["Sources with weak evidence", weakSourceCount],
        ["High risk + weak data themes", highRiskWeakThemes.length],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      section.appendChild(metrics);
      section.appendChild(renderHistoryTable("Current data_status distribution", ["Data status", "Signals"], Object.entries(dataCounts).map(([key, count]) => [key, count])));
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
      section.appendChild(text("h2", "Theme Compare"));
      section.appendChild(description("Compare selected watch themes side by side using current signals and historical context."));
      section.appendChild(renderCompareSelector());
      if (compareNotice) section.appendChild(text("p", compareNotice, "notice"));
      if (!compareThemes.length) {
        section.appendChild(text("p", "No themes selected for comparison.", "muted"));
      } else {
        const grid = document.createElement("div");
        grid.className = "compare-grid";
        compareThemes.forEach((theme) => grid.appendChild(renderCompareCard(theme, visibleSignals)));
        section.appendChild(grid);
      }
      const overlap = document.createElement("div");
      overlap.className = "detail-section";
      overlap.appendChild(text("h3", "Candidate Pool Comparison"));
      overlap.appendChild(text("p", "Observation pool overlap highlights repeated candidates across selected themes. It is not a ranking or instruction.", "muted"));
      overlap.appendChild(renderCandidateOverlapTable("ETF observation candidates", candidateHistoryData?.etf_candidates));
      overlap.appendChild(renderCandidateOverlapTable("Stock observation candidates", candidateHistoryData?.stock_candidates));
      section.appendChild(overlap);
      return appendBackToTop(section);
    }

    function compareSummaryValue(key) {
      return dateCompareData?.summary?.[key] ?? 0;
    }

    function compareCountText(counts) {
      return Object.entries(counts || {}).map(([key, count]) => `${key}: ${count}`).join(", ") || "unknown";
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
        item.textContent = `${value} (not available)`;
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
      const fromField = renderDateSelect("compare-from-select", "From date", compareFromDate);
      const toField = renderDateSelect("compare-to-select", "To date", compareToDate || runSelectEl.value);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "inline-action";
      button.textContent = "Compare dates";
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
      section.appendChild(text("h3", "Theme Change Table"));
      const rows = [];
      (Array.isArray(themes.new) ? themes.new : []).forEach((theme) => rows.push(["new", theme, "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "new watch theme"]));
      (Array.isArray(themes.removed) ? themes.removed : []).forEach((theme) => rows.push(["removed", theme, "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "not in current watch list"]));
      (Array.isArray(themes.changed) ? themes.changed : []).forEach((item) => {
        const notes = [];
        if (item.changes?.score_delta != null) notes.push(`score delta ${item.changes.score_delta}`);
        if (item.changes?.risk_changed) notes.push("risk changed");
        if (item.changes?.intraday_status_changed) notes.push("intraday status changed");
        if (item.changes?.data_status_changed) notes.push("data quality changed");
        rows.push([
          "changed",
          item.theme,
          item.from?.score ?? "unknown",
          item.to?.score ?? "unknown",
          item.changes?.score_delta ?? "unknown",
          `${item.from?.risk_level || "unknown"} -> ${item.to?.risk_level || "unknown"}`,
          `${item.from?.intraday_status || "unknown"} -> ${item.to?.intraday_status || "unknown"}`,
          `${item.from?.data_status || "unknown"} -> ${item.to?.data_status || "unknown"}`,
          notes.join(", ") || "metadata changed",
        ]);
      });
      if (!rows.length) {
        section.appendChild(text("p", "No theme changes available for the selected dates.", "muted"));
        return section;
      }
      const table = document.createElement("table");
      table.className = "history-table";
      const thead = document.createElement("thead");
      const header = document.createElement("tr");
      ["Change", "Theme", "From score", "To score", "Score delta", "Risk", "Intraday", "Data status", "Notes"].forEach((label) => header.appendChild(text("th", label)));
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
          rows.push([group, item.name, item.code || "unknown", (item.themes || []).join(", "), item.from_appearance ?? 0, item.to_appearance ?? 0, item.last_seen || "unknown"]);
        });
      }
      return renderHistoryTable(title, ["Change", "Name", "Code / ticker", "Themes", "From", "To", "Last seen"], rows);
    }

    function renderDataQualityChangeSection() {
      const quality = dateCompareData?.data_quality || {};
      const rows = [
        ["from data_status", compareCountText(quality.from_counts)],
        ["to data_status", compareCountText(quality.to_counts)],
        ["missing source delta", quality.missing_source_delta ?? 0],
        ["missing fetched_at delta", quality.missing_fetched_at_delta ?? 0],
        ["fallback delta", quality.fallback_delta ?? 0],
      ];
      const section = renderHistoryTable("Data Quality Change Section", ["Metric", "Value"], rows);
      section.appendChild(renderHistoryTable("Themes with weaker data quality", ["Theme", "From weak score", "To weak score"], (quality.weaker_themes || []).map((item) => [item.theme, item.from_weak_score, item.to_weak_score])));
      section.appendChild(renderHistoryTable("Themes with improved data quality", ["Theme", "From weak score", "To weak score"], (quality.improved_themes || []).map((item) => [item.theme, item.from_weak_score, item.to_weak_score])));
      return section;
    }

    function renderSourceChangeSection() {
      const sources = dateCompareData?.sources || {};
      return renderHistoryTable("Source Change Section", ["Change", "Sources"], [
        ["new sources", (sources.new || []).join(", ") || "none"],
        ["removed sources", (sources.removed || []).join(", ") || "none"],
        ["repeated sources", (sources.repeated || []).join(", ") || "none"],
      ]);
    }

    function renderDateCompare() {
      const section = document.createElement("article");
      section.id = "date-compare";
      section.className = "date-compare section-card";
      section.appendChild(text("h2", "Date Compare"));
      section.appendChild(description("Compare two local daily runs to review watch-theme, candidate-pool, source coverage, and data quality changes."));
      section.appendChild(renderDateCompareControls());
      section.appendChild(text("h3", "Date Compare Summary"));
      if (!dateCompareData || dateCompareData.available === false) {
        section.appendChild(text("p", (dateCompareData?.notes || ["Not enough daily runs to compare."]).join(" "), "muted"));
        return appendBackToTop(section);
      }
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [
        ["From date", dateCompareData.from_date || "unknown"],
        ["To date", dateCompareData.to_date || "unknown"],
        ["New watch themes", compareSummaryValue("new_themes_count")],
        ["Removed from current watch list", compareSummaryValue("removed_themes_count")],
        ["Changed themes", compareSummaryValue("changed_themes_count")],
        ["New ETF observation candidates", compareSummaryValue("new_etf_candidates_count")],
        ["New stock observation candidates", compareSummaryValue("new_stock_candidates_count")],
        ["Data quality changes", `${compareSummaryValue("weaker_data_quality_count")} weaker / ${compareSummaryValue("improved_data_quality_count")} improved`],
      ].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      const summary = document.createElement("div");
      summary.className = "detail-section";
      summary.appendChild(metrics);
      section.appendChild(summary);
      section.appendChild(renderThemeChangeTable());
      section.appendChild(renderCandidateChangeTable("ETF observation candidate changes", dateCompareData.candidates?.etf));
      section.appendChild(renderCandidateChangeTable("Stock observation candidate changes", dateCompareData.candidates?.stock));
      section.appendChild(renderDataQualityChangeSection());
      section.appendChild(renderSourceChangeSection());
      section.appendChild(renderValueList("Compare notes", dateCompareData.notes || []));
      return appendBackToTop(section);
    }

    function createThemeSummaryCard(group) {
      const node = document.createElement("article");
      node.className = "theme-card";
      const heading = document.createElement("h3");
      heading.appendChild(createThemeButton(group.theme));
      node.appendChild(heading);
      node.appendChild(createCompareButton(group.theme, "Compare"));
      node.appendChild(badge(`${group.signals.length} signals`));
      node.appendChild(badge(`top score: ${topScore(group.signals)}`));
      node.appendChild(badge(`max risk: ${maxRisk(group.signals)}`));
      node.appendChild(badge(`main status: ${mainStatus(group.signals)}`));
      node.appendChild(badge(`ETF candidates: ${candidateCount(group.signals, "etf_candidates")}`));
      node.appendChild(badge(`stock candidates: ${candidateCount(group.signals, "stock_candidates")}`));
      node.appendChild(text("p", triggerSummary(group.signals), "muted"));
      return node;
    }

    function renderThemeHotlist(signals) {
      const section = document.createElement("article");
      section.id = "theme-hotlist";
      section.className = "theme-hotlist section-card";
      section.appendChild(text("h2", "Theme Hotlist"));
      section.appendChild(description("Scan currently visible watch themes, trigger summaries, risk levels, and candidate counts."));
      const groups = groupedSignals(signals);
      if (groups.length === 0) {
        section.appendChild(text("p", "No themes match the current filters.", "muted"));
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
        section.appendChild(badge(`${group.signals.length} signals`));
        section.appendChild(badge(`highest score: ${topScore(group.signals)}`));
        section.appendChild(badge(`strongest: ${strongestStrength(group.signals)}`));
        section.appendChild(badge(`risks: ${distribution(group.signals, "risk_level", "unknown")}`));
        section.appendChild(badge(`statuses: ${distribution(group.signals, "intraday_status", "not_checked")}`));
        section.appendChild(badge(`ETF candidates: ${candidateCount(group.signals, "etf_candidates")}`));
        section.appendChild(badge(`stock candidates: ${candidateCount(group.signals, "stock_candidates")}`));
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
      signalCountEl.textContent = `${visibleSignals.length} of ${currentSignals.length} signals visible`;
      signalsAreaEl.appendChild(renderMorningBrief(visibleSignals));
      signalsAreaEl.appendChild(renderDailyResearchBrief(visibleSignals));
      signalsAreaEl.appendChild(renderResearchReviewQueue(visibleSignals));
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
      const heading = text("h2", viewModeEl.value === "flat" ? `Signals (${visibleSignals.length})` : `Signals grouped by theme (${visibleSignals.length})`);
      listPane.appendChild(heading);
      listPane.appendChild(description("Browse filtered signals as grouped themes or a flat signal list, then open details for evidence and candidate pools."));
      if (visibleSignals.length === 0) {
        listPane.appendChild(text("p", "No signals match the current filters.", "muted"));
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
      [["Date", run.date], ["Status", run.status], ["Schema", data.schema_version], ["Strong", summary.strong_signals], ["Confirmed", summary.confirmed], ["Missing data", summary.missing_data]].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      dashboardEl.appendChild(metrics);

      signalsAreaEl = document.createElement("div");
      signalsAreaEl.id = "signals-area";
      dashboardEl.appendChild(signalsAreaEl);
      renderSignalSections();

      dashboardEl.appendChild(renderHistoricalReview());
      dashboardEl.appendChild(renderArtifacts(artifacts));

      const details = document.createElement("details");
      details.appendChild(text("summary", "Raw dashboard_data.json"));
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
      setStatus(dashboardStatusEl, `Loading ${date}...`);
      try {
        const [data, artifacts] = await Promise.all([
          fetchJson(`/api/runs/${date}/dashboard-data`),
          fetchJson(`/api/runs/${date}/artifacts`),
        ]);
        setStatus(dashboardStatusEl, `Loaded ${date}`);
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
        signalCountEl.textContent = "No signals loaded.";
        renderStatusStrip();
        setStatus(dashboardStatusEl, `Failed to load dashboard data: ${error.message}`, true);
      }
    }

    async function loadRuns() {
      setStatus(runsStatusEl, "Loading runs...");
      clear(runsEl);
      clear(dashboardEl);
      currentSignals = [];
      signalsAreaEl = null;
      currentDashboardData = null;
      currentArtifacts = null;
      selectedSignalIndex = null;
      visibleSignalCount = 0;
      signalCountEl.textContent = "No signals loaded.";
      renderStatusStrip();
      try {
        renderRuns(await fetchJson("/api/runs"));
      } catch (error) {
        clear(runSelectEl);
        runSelectEl.disabled = true;
        setStatus(runsStatusEl, `Failed to load runs: ${error.message}`, true);
      }
    }

    runSelectEl.addEventListener("change", () => loadDashboard(runSelectEl.value));
    refreshRunsEl.addEventListener("click", loadRuns);
    signalSearchEl.addEventListener("input", applySignalFilters);
    riskFilterEl.addEventListener("change", applySignalFilters);
    statusFilterEl.addEventListener("change", applySignalFilters);
    sortSelectEl.addEventListener("change", applySignalFilters);
    viewModeEl.addEventListener("change", applySignalFilters);
    syncControlsFromState(readConsoleStateFromUrl());
    renderStatusStrip();
    loadApiStatus();
    loadHistoryReview().finally(loadRuns);
  </script>
</body>
</html>
"""
