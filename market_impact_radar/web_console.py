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
    .error { color: #b42318; }
    .signals { display: grid; gap: 12px; }
    .theme-hotlist, .theme-group { margin-bottom: 14px; }
    .theme-summary { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
    .theme-card { background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 12px; }
    .theme-card h3, .theme-group h3 { margin: 0 0 8px; }
    .artifacts { margin-bottom: 14px; }
    .artifacts li { margin-bottom: 4px; }
    a { color: #1f6feb; }
    pre { background: #101828; border-radius: 8px; color: #f2f4f7; overflow: auto; padding: 12px; }
    [hidden] { display: none; }
    @media (max-width: 760px) { main, .signal-controls { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>Market Impact Radar Console</h1>
    <div class="muted">Read-only daily report viewer. This page only reads existing API data and does not run the pipeline.</div>
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
            <option value="score-desc">Score descending</option>
            <option value="risk">Risk level</option>
            <option value="status">Intraday status</option>
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
    let currentSignals = [];
    let signalsAreaEl = null;

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

    function renderRuns(payload) {
      clear(runsEl);
      clear(runSelectEl);
      const runs = Array.isArray(payload.runs) ? payload.runs : [];
      setStatus(runsStatusEl, `${runs.length} runs found`);
      if (runs.length === 0) {
        runSelectEl.disabled = true;
        runsEl.appendChild(text("p", "No daily runs found.", "muted"));
        return;
      }
      runSelectEl.disabled = false;
      runs.forEach((run, index) => {
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
        if (index === 0 && run.date) loadDashboard(run.date, button);
      });
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
        if (mode === "score-desc") return (numberScore(right) ?? -Infinity) - (numberScore(left) ?? -Infinity);
        if (mode === "risk") return riskRank(right.risk_level) - riskRank(left.risk_level) || left.__index - right.__index;
        if (mode === "status") return statusRank(right.intraday_status || right.status) - statusRank(left.intraday_status || left.status) || left.__index - right.__index;
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
      renderSignalSections();
    }

    function renderArtifacts(payload) {
      const section = document.createElement("article");
      section.className = "artifacts";
      section.appendChild(text("h2", "Artifacts"));
      const items = Array.isArray(payload && payload.artifacts) ? payload.artifacts : [];
      if (items.length === 0) {
        section.appendChild(text("p", "No artifact index available.", "muted"));
        return section;
      }
      const ul = document.createElement("ul");
      for (const item of items) {
        const li = document.createElement("li");
        const status = item.exists ? "available" : "missing";
        li.appendChild(text("span", `${artifactLabel(item.key, item.file_name)}: ${status}`, item.exists ? "" : "error"));
        if (item.exists && item.api) {
          li.appendChild(text("span", " "));
          li.appendChild(link(item.api, "open API"));
        } else if (item.exists) {
          li.appendChild(text("span", ` (${item.relative_path || item.file_name || "local file"})`, "muted"));
        }
        ul.appendChild(li);
      }
      section.appendChild(ul);
      return section;
    }

    function badge(value) {
      return text("span", value, "badge");
    }

    function createSignalCard(signal) {
      const card = document.createElement("article");
      card.className = "signal-card";
      card.dataset.search = signalText(signal);
      card.dataset.risk = normalized(signal.risk_level);
      card.dataset.status = normalized(signal.intraday_status || signal.status || "not_checked");
      card.appendChild(text("h3", themeName(signal)));
      [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => card.appendChild(badge(value)));
      card.appendChild(text("p", signal.a_share_mapping_reason || "No mapping reason provided.", "muted"));
      [["External triggers", signal.external_triggers], ["ETF candidates", signal.etf_candidates], ["Stock candidates", signal.stock_candidates], ["Risks", signal.risks]].forEach(([label, values]) => {
        card.appendChild(text("strong", label));
        card.appendChild(list(values));
      });
      return card;
    }

    function createThemeSummaryCard(group) {
      const node = document.createElement("article");
      node.className = "theme-card";
      node.appendChild(text("h3", group.theme));
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
        section.appendChild(text("h2", group.theme));
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
      signalCountEl.textContent = `${visibleSignals.length} of ${currentSignals.length} signals visible`;
      signalsAreaEl.appendChild(renderThemeHotlist(visibleSignals));
      const heading = text("h2", viewModeEl.value === "flat" ? `Signals (${visibleSignals.length})` : `Signals grouped by theme (${visibleSignals.length})`);
      signalsAreaEl.appendChild(heading);
      if (visibleSignals.length === 0) {
        signalsAreaEl.appendChild(text("p", "No signals match the current filters.", "muted"));
        return;
      }
      signalsAreaEl.appendChild(viewModeEl.value === "flat" ? renderFlatSignals(visibleSignals) : renderGroupedSignals(visibleSignals));
    }

    function renderDashboard(data, artifacts) {
      clear(dashboardEl);
      const run = data.run || {};
      const summary = data.summary || {};
      const signals = Array.isArray(data.signals) ? data.signals : [];
      currentSignals = signals.map((signal, index) => ({ ...signal, __index: index }));
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [["Date", run.date], ["Status", run.status], ["Schema", data.schema_version], ["Strong", summary.strong_signals], ["Confirmed", summary.confirmed], ["Missing data", summary.missing_data]].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      dashboardEl.appendChild(metrics);
      dashboardEl.appendChild(renderArtifacts(artifacts));

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
        signalCountEl.textContent = "No signals loaded.";
        setStatus(dashboardStatusEl, `Failed to load dashboard data: ${error.message}`, true);
      }
    }

    async function loadRuns() {
      setStatus(runsStatusEl, "Loading runs...");
      clear(runsEl);
      clear(dashboardEl);
      currentSignals = [];
      signalsAreaEl = null;
      signalCountEl.textContent = "No signals loaded.";
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
    loadRuns();
  </script>
</body>
</html>
"""
