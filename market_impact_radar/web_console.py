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
    .signal-controls { grid-template-columns: minmax(180px, 1fr) repeat(2, minmax(130px, 180px)); }
    .metrics { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); margin-bottom: 14px; }
    .badge { border: 1px solid #d9dee7; border-radius: 999px; display: inline-block; font-size: 12px; margin: 2px 4px 2px 0; padding: 2px 8px; }
    .error { color: #b42318; }
    .signals { display: grid; gap: 12px; }
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
    const signalCountEl = document.querySelector("#signal-count");

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

    function applySignalFilters() {
      const cards = Array.from(document.querySelectorAll(".signal-card"));
      const query = normalized(signalSearchEl.value).trim();
      const risk = normalized(riskFilterEl.value).trim();
      const status = normalized(statusFilterEl.value).trim();
      let visible = 0;
      for (const card of cards) {
        const matchesQuery = !query || card.dataset.search.includes(query);
        const matchesRisk = !risk || card.dataset.risk === risk;
        const matchesStatus = !status || card.dataset.status === status;
        const show = matchesQuery && matchesRisk && matchesStatus;
        card.hidden = !show;
        if (show) visible += 1;
      }
      signalCountEl.textContent = `${visible} of ${cards.length} signals visible`;
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

    function renderDashboard(data, artifacts) {
      clear(dashboardEl);
      const run = data.run || {};
      const summary = data.summary || {};
      const signals = Array.isArray(data.signals) ? data.signals : [];
      const metrics = document.createElement("div");
      metrics.className = "metrics";
      [["Date", run.date], ["Status", run.status], ["Schema", data.schema_version], ["Strong", summary.strong_signals], ["Confirmed", summary.confirmed], ["Missing data", summary.missing_data]].forEach(([label, value]) => metrics.appendChild(metric(label, value)));
      dashboardEl.appendChild(metrics);
      dashboardEl.appendChild(renderArtifacts(artifacts));

      const wrap = document.createElement("div");
      wrap.className = "signals";
      wrap.appendChild(text("h2", `Signals (${signals.length})`));
      if (signals.length === 0) wrap.appendChild(text("p", "No signals in this run.", "muted"));
      for (const signal of signals) {
        const card = document.createElement("article");
        card.className = "signal-card";
        card.dataset.search = signalText(signal);
        card.dataset.risk = normalized(signal.risk_level);
        card.dataset.status = normalized(signal.intraday_status || signal.status || "not_checked");
        card.appendChild(text("h3", signal.theme || "unknown theme"));
        [`strength: ${signal.strength || "unknown"}`, `score: ${signal.score ?? "unknown"}`, `intraday: ${signal.intraday_status || "not_checked"}`, `risk: ${signal.risk_level || "unknown"}`, `data: ${signal.data_status || "unknown"}`].forEach((value) => card.appendChild(text("span", value, "badge")));
        card.appendChild(text("p", signal.a_share_mapping_reason || "No mapping reason provided.", "muted"));
        [["External triggers", signal.external_triggers], ["ETF candidates", signal.etf_candidates], ["Stock candidates", signal.stock_candidates], ["Risks", signal.risks]].forEach(([label, values]) => {
          card.appendChild(text("strong", label));
          card.appendChild(list(values));
        });
        wrap.appendChild(card);
      }
      dashboardEl.appendChild(wrap);
      applySignalFilters();

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
        signalCountEl.textContent = "No signals loaded.";
        setStatus(dashboardStatusEl, `Failed to load dashboard data: ${error.message}`, true);
      }
    }

    async function loadRuns() {
      setStatus(runsStatusEl, "Loading runs...");
      clear(runsEl);
      clear(dashboardEl);
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
    loadRuns();
  </script>
</body>
</html>
"""
