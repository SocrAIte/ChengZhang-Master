from __future__ import annotations


def render_console_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Impact Radar Console</title>
  <style>
    body { margin: 0; background: #f7f8fa; color: #18202f; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    header { background: #fff; border-bottom: 1px solid #d9dee7; padding: 18px 24px; }
    h1 { font-size: 22px; margin: 0 0 4px; }
    h2 { font-size: 16px; margin: 0 0 12px; }
    main { display: grid; gap: 16px; grid-template-columns: minmax(220px, 320px) 1fr; padding: 16px; }
    section, article, .metric { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 14px; }
    button { background: #fff; border: 1px solid #d9dee7; border-radius: 6px; cursor: pointer; display: block; margin: 0 0 8px; padding: 10px; text-align: left; width: 100%; }
    button.active, button:hover { border-color: #1f6feb; }
    input, select { border: 1px solid #d9dee7; border-radius: 6px; padding: 9px; width: 100%; }
    label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; }
    .muted { color: #667085; font-size: 13px; }
    .controls { display: grid; gap: 10px; margin: 12px 0; }
    .signal-controls { grid-template-columns: minmax(180px, 1fr) repeat(4, minmax(130px, 180px)); }
    .metrics { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); margin-bottom: 14px; }
    .badge { border: 1px solid #d9dee7; border-radius: 999px; display: inline-block; font-size: 12px; margin: 2px 4px 2px 0; padding: 2px 8px; }
    .status-strip { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .error { color: #b42318; }
    .signals { display: grid; gap: 12px; }
    .analysis-layout { align-items: start; display: grid; gap: 14px; grid-template-columns: minmax(260px, 1fr) minmax(320px, 420px); }
    .signal-card { cursor: pointer; }
    .signal-card.selected { border-color: #1f6feb; box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.12); }
    .signal-detail { position: sticky; top: 12px; }
    .theme-detail { margin-bottom: 14px; }
    .theme-button { background: transparent; border: 0; color: #1f6feb; cursor: pointer; display: inline; font: inherit; margin: 0; padding: 0; text-align: left; width: auto; }
    .theme-button.active { font-weight: 700; text-decoration: underline; }
    .detail-section { border-top: 1px solid #eef1f6; margin-top: 12px; padding-top: 12px; }
    .detail-section h3 { font-size: 14px; margin: 0 0 8px; }
    .evidence-chain { display: grid; gap: 8px; margin: 0; padding-left: 20px; }
    .candidate-table { border-collapse: collapse; font-size: 13px; width: 100%; }
    .candidate-table th, .candidate-table td { border-bottom: 1px solid #eef1f6; padding: 7px; text-align: left; vertical-align: top; }
    .candidate-table th { color: #667085; font-weight: 600; }
    .history-grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-bottom: 14px; }
    .history-table { border-collapse: collapse; font-size: 13px; width: 100%; }
    .history-table th, .history-table td { border-bottom: 1px solid #eef1f6; padding: 7px; text-align: left; vertical-align: top; }
    .history-table th { color: #667085; font-weight: 600; }
    .theme-hotlist, .theme-group { margin-bottom: 14px; }
    .theme-summary { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
    .theme-card { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 12px; }
    .theme-card h3, .theme-group h3 { margin: 0 0 8px; }
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
  </header>
  <main>
    <section>
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
    <section>
      <h2>Dashboard Data</h2>
      <div id="dashboard-status" class="muted">Select a run to load dashboard data.</div>
      <div class="controls signal-controls">
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
    let visibleSignalCount = 0;
    let apiHealthData = null;
    let apiVersionData = null;
    let themeHistoryData = null;
    let candidateHistoryData = null;
    const VALID_RISKS = new Set(["", "low", "medium", "high", "unknown"]);
    const VALID_STATUSES = new Set(["", "confirmed", "downgraded", "missing_data", "failed", "not_checked", "unknown"]);
    const VALID_SORTS = new Set(["default", "score_desc", "risk_level", "intraday_status", "theme"]);
    const VALID_VIEWS = new Set(["grouped", "flat"]);

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

    function normalizeConsoleState(state) {
      return {
        date: String(state.date || "").trim(),
        search: String(state.search || "").trim(),
        risk: normalizeChoice(state.risk, VALID_RISKS, ""),
        status: normalizeChoice(state.status, VALID_STATUSES, ""),
        sort: normalizeSort(state.sort),
        view: normalizeChoice(state.view || "grouped", VALID_VIEWS, "grouped"),
        theme: String(state.theme || "").trim(),
      };
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
        [themeHistoryData, candidateHistoryData] = await Promise.all([
          fetchJson("/api/history/themes"),
          fetchJson("/api/history/candidates"),
        ]);
      } catch (error) {
        themeHistoryData = { runs_count: "unknown", date_range: {}, themes: [] };
        candidateHistoryData = { etf_candidates: [], stock_candidates: [] };
      }
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
      const section = document.createElement("article");
      section.className = "artifacts";
      section.appendChild(text("h2", "Artifact Links"));
      section.appendChild(text("p", "Artifacts for the current run. Missing files are shown as unavailable.", "muted"));
      const items = Array.isArray(payload && payload.artifacts) ? payload.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "No artifact index available.", "muted"));
        return section;
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
      return section;
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
      ["Theme", "Signals", "Runs seen", "Max score", "Avg score", "Main risk", "Main status", "Last seen", "Recent dates"].forEach((label) => header.appendChild(text("th", label)));
      thead.appendChild(header);
      table.appendChild(thead);
      const tbody = document.createElement("tbody");
      rows.forEach((item) => {
        const tr = document.createElement("tr");
        const themeCell = document.createElement("td");
        themeCell.appendChild(createThemeButton(item.theme));
        tr.appendChild(themeCell);
        [item.signal_count, item.runs_seen, item.max_score ?? "unknown", item.avg_score ?? "unknown", topCounterValue(item.risk_counts), topCounterValue(item.intraday_status_counts), item.last_seen || "unknown", (item.recent_dates || []).join(", ")].forEach((value) => tr.appendChild(text("td", value)));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }

    function renderHistoricalReview() {
      const section = document.createElement("article");
      section.appendChild(text("h2", "Historical Review"));
      section.appendChild(text("p", "Historical signals are observation clues from existing daily reports, not a trading backtest or recommendation.", "muted"));
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
      return section;
    }

    function badge(value) {
      return text("span", value, "badge");
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
      panel.className = "signal-detail";
      panel.appendChild(text("h2", "Signal Detail Panel"));
      if (!signal) {
        panel.appendChild(text("p", "No signals match the current filters.", "muted"));
        return panel;
      }
      panel.appendChild(text("h3", themeName(signal)));
      [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => panel.appendChild(badge(value)));
      panel.appendChild(renderDataQualitySection(signal));
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
      return panel;
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
      panel.className = "theme-detail";
      panel.appendChild(text("h2", "Theme Detail"));
      const theme = selectedTheme || (visibleSignals[0] ? themeName(visibleSignals[0]) : "");
      if (!theme) {
        panel.appendChild(text("p", "Select a theme from Theme Hotlist, Historical Theme Trends, a signal card, or grouped theme header.", "muted"));
        return panel;
      }
      const currentSignalsForTheme = currentSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const visibleSignalsForTheme = visibleSignals.filter((signal) => sameTheme(themeName(signal), theme));
      const history = themeHistoryItem(theme);
      const etfs = candidateHistoryForTheme(candidateHistoryData?.etf_candidates, theme);
      const stocks = candidateHistoryForTheme(candidateHistoryData?.stock_candidates, theme);

      panel.appendChild(text("h3", theme));
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
      panel.appendChild(text("p", "Theme drilldown is a research view over existing observations. It does not imply a trade, price target, or future outcome.", "muted"));

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
      panel.appendChild(renderThemeCandidateHistory("ETF observation pool", etfs));
      panel.appendChild(renderThemeCandidateHistory("Stock observation pool", stocks));
      return panel;
    }

    function createThemeSummaryCard(group) {
      const node = document.createElement("article");
      node.className = "theme-card";
      const heading = document.createElement("h3");
      heading.appendChild(createThemeButton(group.theme));
      node.appendChild(heading);
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
      section.className = "theme-hotlist";
      section.appendChild(text("h2", "Theme Hotlist"));
      section.appendChild(text("p", "Hot themes based on the current visible signals. For observation only, not trading advice.", "muted"));
      const groups = groupedSignals(signals);
      if (groups.length === 0) {
        section.appendChild(text("p", "No themes match the current filters.", "muted"));
        return section;
      }
      const wrap = document.createElement("div");
      wrap.className = "theme-summary";
      for (const group of groups) wrap.appendChild(createThemeSummaryCard(group));
      section.appendChild(wrap);
      return section;
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
      signalsAreaEl.appendChild(renderThemeHotlist(visibleSignals));
      signalsAreaEl.appendChild(renderThemeDetail(visibleSignals));
      const layout = document.createElement("div");
      layout.className = "analysis-layout";
      const listPane = document.createElement("div");
      const heading = text("h2", viewModeEl.value === "flat" ? `Signals (${visibleSignals.length})` : `Signals grouped by theme (${visibleSignals.length})`);
      listPane.appendChild(heading);
      if (visibleSignals.length === 0) {
        listPane.appendChild(text("p", "No signals match the current filters.", "muted"));
        layout.appendChild(listPane);
        layout.appendChild(renderSignalDetail(null));
        signalsAreaEl.appendChild(layout);
        renderStatusStrip();
        return;
      }
      listPane.appendChild(viewModeEl.value === "flat" ? renderFlatSignals(visibleSignals) : renderGroupedSignals(visibleSignals));
      layout.appendChild(listPane);
      layout.appendChild(renderSignalDetail(selectedSignal));
      signalsAreaEl.appendChild(layout);
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
      dashboardEl.appendChild(renderArtifacts(artifacts));
      dashboardEl.appendChild(renderHistoricalReview());

      signalsAreaEl = document.createElement("div");
      signalsAreaEl.id = "signals-area";
      dashboardEl.appendChild(signalsAreaEl);
      renderSignalSections();

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
