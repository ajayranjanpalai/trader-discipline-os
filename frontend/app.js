const API = "/api";
const defaultLocalTaskTitles = [
  "Wake up at 5:30",
  "Fresh by 7am",
  "Market analisis",
  "Gym/excrise",
  "Act on the To Do List",
  "Project Work",
  "Study",
  "Drink 4 L Water",
  "No junk food",
  "Track expences daily",
  "No phone before 1hr of sleep",
  "No p***",
  "Tomorrow's To Do List",
];

function makeLocalTask(title, index = Date.now()) {
  return {
    id: `local-${String(title).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}-${index}`,
    title,
    category: "routine",
    task_scope: "daily",
    due_date: "",
    sample: true,
  };
}

function initialLocalTasks() {
  const raw = localStorage.getItem("tdos_local_tasks");
  const customized = localStorage.getItem("tdos_local_tasks_customized") === "1";
  if (raw) {
    const saved = JSON.parse(raw);
    if (saved.length || customized) return saved;
  }
  const seeded = defaultLocalTaskTitles.map(makeLocalTask);
  localStorage.setItem("tdos_local_tasks", JSON.stringify(seeded));
  return seeded;
}

const state = {
  token: localStorage.getItem("tdos_token"),
  user: JSON.parse(localStorage.getItem("tdos_user") || "null"),
  trades: JSON.parse(localStorage.getItem("tdos_cache_trades") || "[]"),
  expenses: JSON.parse(localStorage.getItem("tdos_cache_expenses") || "[]"),
  capital: JSON.parse(localStorage.getItem("tdos_cache_capital") || "null"),
  tasks: JSON.parse(localStorage.getItem("tdos_cache_tasks") || "[]"),
  analytics: JSON.parse(localStorage.getItem("tdos_cache_analytics") || "null"),
  discipline: null,
  charts: {},
  editingTradeId: null,
  draggingTaskId: null,
  filters: { search: "", outcome: "all", emotion: "all" },
  dailyPlan: JSON.parse(localStorage.getItem("tdos_daily_plan") || "null"),
  calculator: { size: 0, riskAmount: 0 },
  riskSettings: JSON.parse(localStorage.getItem("tdos_risk_settings") || "null") || {
    capital: 100000,
    riskPct: 1,
    dailyLoss: 2000,
    drawdownPct: 10,
  },
  sampleTaskChecks: JSON.parse(localStorage.getItem("tdos_sample_task_checks") || "{}"),
  localTasks: initialLocalTasks(),
  playbook: JSON.parse(localStorage.getItem("tdos_playbook") || "null") || [
    { id: "pullback", name: "A+ Pullback", criteria: "Trend intact, clean retest, defined invalidation, no late entry." },
    { id: "breakout", name: "Opening Range Breakout", criteria: "Range formed, volume expansion, stop below structure, reward at least 2R." },
  ],
};

const quotes = [
  "Plan the trade. Trade the plan.",
  "Your edge is worthless without restraint.",
  "One clean trade beats five emotional trades.",
  "Capital is protected by behavior first.",
];

const DELTA_USD_INR_RATE = 85;
const deltaUsdToInr = (value) => Number(value || 0) * DELTA_USD_INR_RATE;
const tradeBrokerage = (trade) => Number(trade?.brokerage || 0);
const netTradePnlInr = (trade) => deltaUsdToInr(trade?.pnl) - tradeBrokerage(trade);

const fmtMoney = (value) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);

const qs = (selector, root = document) => root.querySelector(selector);
const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
const storageJSON = (key, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
  } catch (_error) {
    return fallback;
  }
};
const escapeHTML = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
const fallbackIcons = {
  zap: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h7l-1 8 10-14h-7l1-6Z"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  "shopping-bag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7L6 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/></svg>',
  "layout-dashboard": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="6" height="6"/><rect x="14" y="4" width="6" height="6"/><rect x="4" y="14" width="6" height="6"/><rect x="14" y="14" width="6" height="6"/></svg>',
  "candlestick-chart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3v18M4 8h4v8H4zM12 3v18M10 5h4v6h-4zM18 3v18M16 12h4v5h-4z"/></svg>',
  "shield-check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6l-7-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></svg>',
  "bar-chart-3": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20V4M4 20h18M8 16v-5M13 16V7M18 16v-9"/></svg>',
  "wallet-cards": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16v13H4z"/><path d="M4 10h16M7 5h11v2"/></svg>',
  "list-checks": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 7 2 2 4-4M12 8h8M4 15l2 2 4-4M12 16h8"/></svg>',
  sparkles: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3ZM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15ZM5 15l.8 2.2L8 18l-2.2.8L5 21l-.8-2.2L2 18l2.2-.8L5 15Z"/></svg>',
};
const setupPrefix = /^\[Setup:\s*([^\]]+)\]\s*/i;
const localDateKey = (value = new Date()) => {
  const date = new Date(value);
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 10);
};
const todayDateKey = () => localDateKey();

function toast(message, tone = "info") {
  const host = qs("#toastHost");
  const node = document.createElement("div");
  node.className = `toast ${tone}`;
  node.textContent = message;
  host.appendChild(node);
  setTimeout(() => node.remove(), 3200);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || data.message || "Request failed");
  return data;
}

function isOfflineError(error) {
  const message = String(error?.message || "").toLowerCase();
  return !navigator.onLine || message.includes("failed to fetch") || message.includes("networkerror") || message.includes("load failed");
}

function createIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
    return;
  }
  qsa("[data-lucide]").forEach((node) => {
    const name = node.dataset.lucide;
    if (!fallbackIcons[name]) return;
    node.innerHTML = fallbackIcons[name];
    node.classList.add("lucide-fallback");
  });
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator) || location.protocol === "file:") return;
  navigator.serviceWorker.register("sw.js").catch(() => {});
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function showApp() {
  qs("#authScreen").classList.add("hidden");
  qs("#appShell").classList.remove("hidden");
  qs("#sidebarName").textContent = state.user?.name || "Trader";
  qs("#avatar").textContent = (state.user?.name || "T").trim()[0].toUpperCase();
  loadAll();
}

function showAuth() {
  qs("#authScreen").classList.remove("hidden");
  qs("#appShell").classList.add("hidden");
}

function saveAuth(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem("tdos_token", token);
  localStorage.setItem("tdos_user", JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem("tdos_token");
  localStorage.removeItem("tdos_user");
  state.token = null;
  state.user = null;
}

async function loadAll() {
  const requests = await Promise.allSettled([
    api("/trades"),
    api("/expenses"),
    api("/capital"),
    api("/tasks"),
    api("/analytics"),
    api("/insights"),
  ]);
  const [trades, expenses, capital, tasks, analytics, insights] = requests;
  const failed = requests.filter((result) => result.status === "rejected");

  if (trades.status === "fulfilled") {
    state.trades = trades.value.trades || [];
    state.discipline = trades.value.discipline;
  }
  if (expenses.status === "fulfilled") state.expenses = expenses.value.expenses || [];
  if (capital.status === "fulfilled") {
    state.capital = capital.value;
    if (capital.value.summary?.starting_capital) {
      state.riskSettings.capital = capital.value.summary.starting_capital;
      localStorage.setItem("tdos_risk_settings", JSON.stringify(state.riskSettings));
    }
  }
  if (tasks.status === "fulfilled") {
    state.tasks = tasks.value.tasks || [];
    state.taskStats = tasks.value.stats;
  }
  if (analytics.status === "fulfilled") state.analytics = analytics.value;
  if (insights.status === "fulfilled") state.insights = insights.value.insights || [];

  hydrateOfflineState({
    tradesFailed: trades.status === "rejected",
    expensesFailed: expenses.status === "rejected",
    capitalFailed: capital.status === "rejected",
    tasksFailed: tasks.status === "rejected",
    analyticsFailed: analytics.status === "rejected",
  });
  renderAll();

  if (!failed.length) {
    cacheState();
    return;
  }

  const firstError = failed[0].reason;
  toast(isOfflineError(firstError) ? "Offline mode: showing saved dashboard data." : firstError.message, isOfflineError(firstError) ? "info" : "danger");
  if (String(firstError.message || "").toLowerCase().includes("token")) logout();
}

function cacheState() {
  localStorage.setItem("tdos_cache_trades", JSON.stringify(state.trades));
  localStorage.setItem("tdos_cache_expenses", JSON.stringify(state.expenses));
  localStorage.setItem("tdos_cache_capital", JSON.stringify(state.capital));
  localStorage.setItem("tdos_cache_tasks", JSON.stringify(state.tasks));
  localStorage.setItem("tdos_cache_analytics", JSON.stringify(state.analytics));
}

function hydrateOfflineState(sources = {}) {
  if (sources.tradesFailed && !state.trades.length) state.trades = storageJSON("tdos_cache_trades", []);
  if (sources.expensesFailed && !state.expenses.length) state.expenses = storageJSON("tdos_cache_expenses", []);
  if (sources.capitalFailed && !state.capital) state.capital = storageJSON("tdos_cache_capital", null);
  if (sources.tasksFailed && !state.tasks.length) state.tasks = storageJSON("tdos_cache_tasks", []);
  if (!state.discipline) state.discipline = buildLocalDiscipline();
  if (sources.analyticsFailed && !state.analytics) state.analytics = buildLocalAnalytics();
}

function buildLocalDiscipline() {
  const today = new Date().toDateString();
  const todayTrades = state.trades.filter((trade) => new Date(trade.timestamp).toDateString() === today);
  const losses = todayTrades.filter((trade) => netTradePnlInr(trade) < 0).length;
  const firstTradeProfit = netTradePnlInr(todayTrades[0]) > 0;
  const allowed = todayTrades.length < 2 && losses < 2 && !firstTradeProfit;
  return {
    score: state.trades.length ? Math.max(0, 100 - losses * 10) : "--",
    message: allowed ? "Offline discipline check: wait for a valid setup." : "Offline discipline check: stop trading for the day.",
    allowed,
    today_count: todayTrades.length,
  };
}

function expenseCategoryData() {
  const categories = new Map();
  state.expenses.forEach((expense) => {
    const label = expense.category || "other";
    categories.set(label, (categories.get(label) || 0) + Number(expense.amount || 0));
  });
  return [...categories.entries()].map(([label, value]) => ({ label, value }));
}

function capitalSummary() {
  const transactions = state.capital?.transactions || [];
  const hasTransactions = transactions.length > 0;
  const deposits = hasTransactions
    ? transactions
      .filter((transaction) => transaction.transaction_type === "deposit")
      .reduce((sum, transaction) => sum + Number(transaction.amount || 0), 0)
    : Number(state.capital?.summary?.deposits || 0);
  const withdrawals = hasTransactions
    ? transactions
      .filter((transaction) => transaction.transaction_type === "withdrawal")
      .reduce((sum, transaction) => sum + Number(transaction.amount || 0), 0)
    : Number(state.capital?.summary?.withdrawals || 0);
  const grossPnl = state.trades.reduce((sum, trade) => sum + deltaUsdToInr(trade.pnl), 0);
  const brokerage = state.trades.reduce((sum, trade) => sum + tradeBrokerage(trade), 0);
  const netPnl = grossPnl - brokerage;
  const startingCapital = Number(state.capital?.summary?.starting_capital ?? state.user?.starting_capital ?? state.riskSettings.capital ?? 100000);
  return {
    starting_capital: startingCapital,
    deposits,
    withdrawals,
    gross_pnl: grossPnl,
    brokerage,
    net_pnl: netPnl,
    current_capital: startingCapital + deposits - withdrawals + netPnl,
  };
}

function buildLocalAnalytics() {
  const trades = [...state.trades].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const pnlValues = trades.map(netTradePnlInr);
  const wins = pnlValues.filter((pnl) => pnl > 0);
  const losses = pnlValues.filter((pnl) => pnl < 0);
  const totalPnl = pnlValues.reduce((sum, pnl) => sum + pnl, 0);
  const daily = new Map();
  const emotion = new Map();
  let running = 0;
  const equity = trades.map((trade) => {
    running += netTradePnlInr(trade);
    return { label: new Date(trade.timestamp).toLocaleDateString(), value: running };
  });

  trades.forEach((trade) => {
    const day = new Date(trade.timestamp).toLocaleDateString();
    const pnl = netTradePnlInr(trade);
    daily.set(day, (daily.get(day) || 0) + pnl);
    if (trade.emotion) emotion.set(trade.emotion, (emotion.get(trade.emotion) || 0) + pnl);
  });

  return {
    summary: {
      total_pnl: totalPnl,
      gross_pnl: capitalSummary().gross_pnl,
      total_brokerage: capitalSummary().brokerage,
      current_capital: capitalSummary().current_capital,
      starting_capital: capitalSummary().starting_capital,
      deposits: capitalSummary().deposits,
      withdrawals: capitalSummary().withdrawals,
      total_trades: trades.length,
      win_rate: trades.length ? Math.round((wins.length / trades.length) * 100) : 0,
      avg_profit: wins.length ? wins.reduce((sum, pnl) => sum + pnl, 0) / wins.length : 0,
      avg_loss: losses.length ? losses.reduce((sum, pnl) => sum + pnl, 0) / losses.length : 0,
      risk_reward_ratio: Math.abs(losses.reduce((sum, pnl) => sum + pnl, 0)) ? (wins.reduce((sum, pnl) => sum + pnl, 0) / Math.abs(losses.reduce((sum, pnl) => sum + pnl, 0))).toFixed(2) : 0,
      best_trade: pnlValues.length ? Math.max(...pnlValues) : 0,
    },
    charts: {
      equity_curve: equity,
      daily_pl: [...daily.entries()].map(([label, value]) => ({ label, value })),
      win_loss: { wins: wins.length, losses: losses.length },
      emotion_performance: [...emotion.entries()].map(([label, value]) => ({ label, value })),
      expense_categories: expenseCategoryData(),
    },
  };
}

function refreshLocalAnalytics() {
  state.discipline = buildLocalDiscipline();
  state.analytics = buildLocalAnalytics();
  cacheState();
}

function renderAll() {
  renderDiscipline();
  renderMetrics();
  renderCommandBriefing();
  renderTrades();
  renderExpenses();
  renderCapital();
  renderTasks();
  renderInsights();
  renderSessionReview();
  renderDailyPlan();
  renderPlaybook();
  renderPositionCalculator();
  renderRiskDesk();
  renderTicker();
  renderCharts();
  renderRiskPreview();
  renderTaskClock();
}

function renderDiscipline() {
  const d = state.discipline || { score: "--", message: "Discipline engine ready.", allowed: true, today_count: 0 };
  qs("#disciplineScore").textContent = typeof d.score === "number" ? `${d.score}%` : d.score;
  qs("#mToday").textContent = `${d.today_count || 0} / 2 today`;
  qs("#ruleStatus").textContent = d.message || "Discipline engine ready.";
  qs("#riskState").textContent = d.allowed ? "Clear" : "Locked";
  qs("#riskState").className = d.allowed ? "profit" : "loss";
  const alert = qs("#disciplineAlert");
  alert.className = `alert show ${d.allowed ? "success" : "danger"}`;
  alert.textContent = d.message || "Discipline engine ready.";
}

function renderMetrics() {
  const summary = state.analytics?.summary || {};
  qs("#mPnl").textContent = fmtMoney(summary.total_pnl);
  qs("#mPnl").className = summary.total_pnl >= 0 ? "profit" : "loss";
  qs("#mWinRate").textContent = `${summary.win_rate || 0}%`;
  qs("#mTrades").textContent = summary.total_trades || state.trades.length || 0;
  const fit = playbookStats();
  qs("#mPlaybookFit").textContent = `${fit.fitRate}%`;
  qs("#mPlaybookCount").textContent = `${fit.tagged} tagged trade${fit.tagged === 1 ? "" : "s"}`;
  qs("#aAvgProfit").textContent = fmtMoney(summary.avg_profit);
  qs("#aAvgLoss").textContent = fmtMoney(summary.avg_loss);
  qs("#aRR").textContent = summary.risk_reward_ratio || 0;
  qs("#aBest").textContent = fmtMoney(summary.best_trade);
  qs("#quote").textContent = quotes[new Date().getDate() % quotes.length];

  const todayKey = new Date().toDateString();
  const todayNet = state.trades
    .filter((trade) => new Date(trade.timestamp).toDateString() === todayKey)
    .reduce((sum, trade) => sum + netTradePnlInr(trade), 0);
  qs("#todayNet").textContent = fmtMoney(todayNet);
  qs("#todayNet").className = todayNet >= 0 ? "profit" : "loss";

  qs("#bestSetup").textContent = fit.best ? `${fit.best.name} ${fmtMoney(fit.best.avg)}` : "--";
  const todayPlan = getTodayPlan();
  qs("#planState").textContent = todayPlan ? todayPlan.bias : "Not Set";
  qs("#planState").className = todayPlan ? "profit" : "loss";
}

function renderTrades() {
  const recent = qs("#recentTrades");
  recent.innerHTML = (state.trades.slice(0, 5).map(tradeRowCard).join("")) || empty("No trades logged yet.");
  renderEmotionFilterOptions();
  const visibleTrades = filteredTrades();
  qs("#tradeCountLabel").textContent = `${visibleTrades.length} shown / ${state.trades.length} logged`;
  qs("#tradeRows").innerHTML = visibleTrades.map((trade) => `
    <tr>
      <td>${new Date(trade.timestamp).toLocaleString()}</td>
      <td>${escapeHTML(trade.pair)}</td>
      <td>${escapeHTML(setupMeta(trade).name || "--")}</td>
      <td>${escapeHTML(trade.direction)}</td>
      <td>${trade.entry}</td>
      <td>${trade.exit}</td>
      <td>${fmtMoney(tradeBrokerage(trade))}</td>
      <td class="${netTradePnlInr(trade) >= 0 ? "profit" : "loss"}">${fmtMoney(netTradePnlInr(trade))}</td>
      <td>${escapeHTML(trade.emotion)}</td>
      <td class="table-row-actions">
        <button class="mini-btn" data-edit-trade="${trade.id}">Edit</button>
        <button class="mini-btn" data-delete-trade="${trade.id}">Delete</button>
      </td>
    </tr>
  `).join("") || `<tr><td colspan="10">${empty("No trades match the current filters.")}</td></tr>`;
}

function tradeRowCard(trade) {
  const setup = setupMeta(trade).name;
  return `
    <div class="item-row">
      <div><b>${escapeHTML(trade.pair)}</b><br><small>${escapeHTML(setup ? `${setup} / ${trade.emotion}` : `${trade.direction} / ${trade.emotion}`)}</small></div>
      <strong class="${netTradePnlInr(trade) >= 0 ? "profit" : "loss"}">${fmtMoney(netTradePnlInr(trade))}</strong>
    </div>
  `;
}

function filteredTrades() {
  const query = state.filters.search.trim().toLowerCase();
  return state.trades.filter((trade) => {
    const outcomeMatch =
      state.filters.outcome === "all" ||
      (state.filters.outcome === "win" && netTradePnlInr(trade) > 0) ||
      (state.filters.outcome === "loss" && netTradePnlInr(trade) < 0);
    const emotionMatch = state.filters.emotion === "all" || trade.emotion === state.filters.emotion;
    const searchText = [trade.pair, trade.direction, trade.emotion, setupMeta(trade).name, trade.trade_reason, trade.notes].join(" ").toLowerCase();
    return outcomeMatch && emotionMatch && (!query || searchText.includes(query));
  });
}

function setupMeta(trade) {
  const reason = trade?.trade_reason || "";
  const match = reason.match(setupPrefix);
  const idOrName = match?.[1]?.trim() || "";
  const setup = state.playbook.find((item) => item.id === idOrName || item.name.toLowerCase() === idOrName.toLowerCase());
  return {
    id: setup?.id || idOrName,
    name: setup?.name || idOrName,
    reason: reason.replace(setupPrefix, "").trim(),
  };
}

function encodeTradePayload(form) {
  const data = formData(form);
  const setupId = data.setup_tag;
  const setup = state.playbook.find((item) => item.id === setupId);
  delete data.setup_tag;
  const reason = String(data.trade_reason || "").replace(setupPrefix, "").trim();
  data.trade_reason = setup ? `[Setup: ${setup.id}] ${reason}`.trim() : reason;
  return data;
}

function playbookStats() {
  const grouped = new Map();
  state.trades.forEach((trade) => {
    const meta = setupMeta(trade);
    if (!meta.name) return;
    const current = grouped.get(meta.id) || { name: meta.name, count: 0, wins: 0, pnl: 0 };
    current.count += 1;
    current.wins += netTradePnlInr(trade) > 0 ? 1 : 0;
    current.pnl += netTradePnlInr(trade);
    grouped.set(meta.id, current);
  });
  const setups = [...grouped.values()].map((item) => ({
    ...item,
    avg: item.count ? item.pnl / item.count : 0,
    winRate: item.count ? Math.round((item.wins / item.count) * 100) : 0,
  }));
  const tagged = setups.reduce((sum, item) => sum + item.count, 0);
  const fitRate = state.trades.length ? Math.round((tagged / state.trades.length) * 100) : 0;
  const best = setups.sort((a, b) => b.avg - a.avg)[0];
  return { tagged, fitRate, best };
}

function persistPlaybook() {
  localStorage.setItem("tdos_playbook", JSON.stringify(state.playbook));
}

function renderPlaybook() {
  const select = qs("#setupTag");
  if (!select) return;
  const current = select.value;
  select.innerHTML = `<option value="">No setup tag</option>${state.playbook.map((setup) => `<option value="${escapeHTML(setup.id)}">${escapeHTML(setup.name)}</option>`).join("")}`;
  select.value = state.playbook.some((setup) => setup.id === current) ? current : "";
  qs("#playbookCount").textContent = `${state.playbook.length} active`;
  qs("#playbookList").innerHTML = state.playbook.map((setup) => `
    <div class="playbook-item">
      <div>
        <strong>${escapeHTML(setup.name)}</strong>
        <span>${escapeHTML(setup.criteria)}</span>
      </div>
      <button class="mini-btn" type="button" data-delete-setup="${escapeHTML(setup.id)}">Remove</button>
    </div>
  `).join("") || empty("No setups saved yet.");
}

function addPlaybookSetup() {
  const name = qs("#playbookName").value.trim();
  const criteria = qs("#playbookCriteria").value.trim();
  if (!name || !criteria) {
    toast("Add a setup name and entry criteria.", "danger");
    return;
  }
  state.playbook.push({
    id: `${name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}-${Date.now().toString(36)}`,
    name,
    criteria,
  });
  qs("#playbookName").value = "";
  qs("#playbookCriteria").value = "";
  persistPlaybook();
  renderPlaybook();
  renderMetrics();
  toast("Setup added to playbook.");
}

function deletePlaybookSetup(id) {
  state.playbook = state.playbook.filter((setup) => setup.id !== id);
  persistPlaybook();
  renderPlaybook();
  renderMetrics();
  renderTrades();
  toast("Setup removed.");
}

function renderEmotionFilterOptions() {
  const select = qs("#emotionFilter");
  const current = select.value || state.filters.emotion;
  const emotions = [...new Set(state.trades.map((trade) => trade.emotion).filter(Boolean))].sort();
  select.innerHTML = `<option value="all">All emotions</option>${emotions.map((emotion) => `<option value="${escapeHTML(emotion)}">${escapeHTML(emotion)}</option>`).join("")}`;
  select.value = emotions.includes(current) ? current : "all";
  state.filters.emotion = select.value;
}

function renderExpenses() {
  const total = state.expenses.reduce((sum, expense) => sum + Number(expense.amount || 0), 0);
  qs("#expenseTotal").textContent = fmtMoney(total);
  qs("#expenseList").innerHTML = state.expenses.map((expense) => `
    <div class="item-row">
      <div><b>${escapeHTML(expense.title)}</b><br><small>${escapeHTML(expense.category)} / ${escapeHTML(expense.payment_method)}</small></div>
      <span class="loss">${fmtMoney(expense.amount)}</span>
      <button class="mini-btn" data-delete-expense="${expense.id}">Delete</button>
    </div>
  `).join("") || empty("No expenses tracked yet.");
}

function renderCapital() {
  const summary = capitalSummary();
  const transactions = state.capital?.transactions || [];
  const netFlow = Number(summary.deposits || 0) - Number(summary.withdrawals || 0);
  const total = qs("#capitalFlowTotal");
  const list = qs("#capitalList");
  if (!total || !list) return;
  total.textContent = fmtMoney(netFlow);
  total.className = netFlow >= 0 ? "profit" : "loss";
  list.innerHTML = transactions.map((transaction) => {
    const isDeposit = transaction.transaction_type === "deposit";
    return `
      <div class="item-row">
        <div>
          <b>${isDeposit ? "Add Money" : "Withdraw Money"}</b><br>
          <small>${escapeHTML(transaction.note || new Date(transaction.created_at).toLocaleString())}</small>
        </div>
        <strong class="${isDeposit ? "profit" : "loss"}">${isDeposit ? "+" : "-"}${fmtMoney(transaction.amount)}</strong>
        <button class="mini-btn" data-delete-capital="${transaction.id}" type="button">Delete</button>
      </div>
    `;
  }).join("") || empty("No capital deposits or withdrawals yet.");
}

function renderTasks() {
  renderTaskClock();
  const stats = currentTaskStats();
  qs("#taskProgress").textContent = `${stats.completion_rate || 0}%`;
  qs("#taskCompleted").textContent = `${stats.completed || 0} / ${stats.total || 0} complete`;
  qs("#taskProgressBar").style.width = `${stats.completion_rate || 0}%`;
  qs("#taskStreak").textContent = `${stats.streak || 0} day streak`;
  const scoreRing = qs("#taskScoreRing");
  if (scoreRing) {
    const score = stats.completion_rate || 0;
    scoreRing.style.setProperty("--score", `${score}%`);
    scoreRing.querySelector("strong").textContent = `${score}%`;
  }
  const taskCountText = `${stats.due_today} task${stats.due_today === 1 ? "" : "s"}`;
  qs("#taskDueSummary").textContent = stats.due_today
    ? stats.email_configured
      ? `${taskCountText} must be completed by today. Email warning can go to ${state.user?.email || "your account email"}.`
      : `${taskCountText} must be completed by today. Email warnings are not configured.`
    : "Complete at least one task daily to extend your streak.";
  const emailButton = qs("#emailTaskWarnings");
  if (emailButton) {
    const hasWarnings = Boolean(tasksWithWarnings().length);
    emailButton.disabled = !hasWarnings || !stats.email_configured;
    emailButton.textContent = !hasWarnings ? "No Email Warning" : stats.email_configured ? "Email Warning" : "Email Not Set Up";
  }
  renderTaskSheet();
  renderTaskLab();
}

function renderTaskSheet() {
  const sheet = qs("#taskSheet");
  if (!sheet) return;
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const today = now.getDate();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
  const dayLabels = days.map((day) => new Date(year, month, day).toLocaleDateString([], { weekday: "short" }).slice(0, 2));
  const rows = taskRowsForDisplay();

  sheet.style.setProperty("--day-count", daysInMonth);
  sheet.innerHTML = `
    <div class="sheet-row sheet-row-head">
      <div class="sheet-label">Dates</div>
      ${days.map((day) => `<div class="sheet-date ${day === today ? "today" : ""}">${day}</div>`).join("")}
      <div class="sheet-action">Total</div>
    </div>
    <div class="sheet-row sheet-row-head sheet-row-days">
      <div class="sheet-label">Days</div>
      ${dayLabels.map((label, index) => `<div class="sheet-date ${index + 1 === today ? "today" : ""}">${label}</div>`).join("")}
      <div class="sheet-action">%</div>
    </div>
    ${rows.map((task) => taskSheetRow(task, year, month, today)).join("")}
  `;
}

function sampleTaskRows() {
  return state.localTasks;
}

function taskSheetRow(task, year, month, today) {
  const completed = taskEffectiveCompleted(task);
  const tone = taskDueState(task).tone;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const completedAt = task.completed_at ? new Date(task.completed_at) : null;
  const completedInMonth = completedAt && completedAt.getFullYear() === year && completedAt.getMonth() === month;
  const completedDay = completedInMonth ? completedAt.getDate() : completed ? today : 0;
  const completionPct = completed ? 100 : 0;
  const action = task.sample
    ? `<button class="sheet-delete" type="button" title="Remove task" aria-label="Remove ${escapeHTML(task.title)}" data-remove-sample-task="${escapeHTML(task.id)}">Delete</button>`
    : `<button class="sheet-delete" type="button" title="Delete task" aria-label="Delete ${escapeHTML(task.title)}" data-delete-task="${task.id}">Delete</button>`;
  const dragAttrs = task.sample && !state.tasks.length ? `draggable="true" data-drag-task="${escapeHTML(task.id)}"` : "";
  const dragHandle = task.sample && !state.tasks.length ? `<button class="sheet-drag-handle" type="button" title="Drag to reorder" aria-label="Drag ${escapeHTML(task.title)}">::</button>` : "";
  const cells = Array.from({ length: daysInMonth }, (_, index) => {
    const day = index + 1;
    const isDone = completed && day === completedDay;
    const canToggle = day === today;
    const toggleAttr = task.sample ? `data-toggle-sample-task="${task.id}"` : `data-complete-task="${task.id}"`;
    return `
      <button class="sheet-check ${isDone ? "checked" : ""} ${day === today ? "today" : ""}" type="button" ${canToggle ? toggleAttr : "disabled"} aria-label="${escapeHTML(task.title)} day ${day}">
        ${isDone ? "&#10003;" : ""}
      </button>
    `;
  }).join("");
  return `
    <div class="sheet-row sheet-task-row ${tone}" ${dragAttrs}>
      <div class="sheet-label">
        ${dragHandle}
        <div>
          <strong>${escapeHTML(task.title)}</strong>
          <span>${escapeHTML(task.category || "routine")} / ${escapeHTML(taskScheduleLabel(task))}</span>
        </div>
        ${action}
      </div>
      ${cells}
      <div class="sheet-action">
        <strong class="${completed ? "profit" : tone === "danger" ? "loss" : ""}">${completionPct}%</strong>
      </div>
    </div>
  `;
}

function taskRowsForDisplay() {
  const hasLocalCustomization = localStorage.getItem("tdos_local_tasks_customized") === "1";
  return state.tasks.length
    ? [...state.tasks, ...(hasLocalCustomization ? state.localTasks : [])]
    : state.localTasks;
}

function taskMonthSeries() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const today = now.getDate();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const rows = taskRowsForDisplay();
  return Array.from({ length: daysInMonth }, (_, index) => {
    const day = index + 1;
    const dateKey = localDateKey(new Date(year, month, day));
    const total = rows.length;
    let completed = 0;
    if (!state.tasks.length) {
      completed = Object.values(state.sampleTaskChecks[dateKey] || {}).filter(Boolean).length;
    } else if (day === today) {
      completed = rows.filter(taskEffectiveCompleted).length;
    }
    const pct = total ? Math.round((completed / total) * 100) : 0;
    return { day, dateKey, total, completed, pct, isToday: day === today, isPast: day <= today };
  });
}

function renderTaskLab() {
  const series = taskMonthSeries();
  const elapsed = series.filter((day) => day.isPast);
  const best = elapsed.reduce((max, day) => Math.max(max, day.pct), 0);
  const perfect = elapsed.filter((day) => day.total && day.completed === day.total).length;
  const today = elapsed[elapsed.length - 1] || { pct: 0 };
  const yesterday = elapsed[elapsed.length - 2] || { pct: today.pct };
  const average = elapsed.length ? Math.round(elapsed.reduce((sum, day) => sum + day.pct, 0) / elapsed.length) : 0;
  const trend = today.pct > yesterday.pct ? "Up" : today.pct < yesterday.pct ? "Down" : "Flat";

  qs("#taskBestDay").textContent = `Best ${best}%`;
  qs("#taskPerfectDays").textContent = `${perfect} perfect`;
  qs("#taskTrendLabel").textContent = trend;
  qs("#taskDailyBars").innerHTML = series.map((day) => `
    <span class="${day.isToday ? "today" : ""} ${day.pct === 100 ? "perfect" : ""}" style="--bar:${day.pct}%;" title="Day ${day.day}: ${day.completed}/${day.total}"></span>
  `).join("");
  qs("#taskStreakStrip").innerHTML = series.map((day) => `
    <span class="${day.isToday ? "today" : ""} ${day.pct === 100 ? "perfect" : day.pct ? "partial" : ""}" title="Day ${day.day}: ${day.pct}%"></span>
  `).join("");
  renderTaskTrendGraph(series);
  renderTaskMiniRings([
    ["Score", today.pct],
    ["Avg", average],
    ["Best", best],
    ["Perfect", series.length ? Math.round((perfect / series.length) * 100) : 0],
  ]);
  renderTaskBadgesAndWarnings(elapsed, today);
}

function currentPerfectStreak(series) {
  let streak = 0;
  for (let index = series.length - 1; index >= 0; index -= 1) {
    const day = series[index];
    if (!day.total || day.completed !== day.total) break;
    streak += 1;
  }
  return streak;
}

function renderTaskBadgesAndWarnings(elapsed, today) {
  const streak = currentPerfectStreak(elapsed);
  const missedToday = Math.max(0, (today.total || 0) - (today.completed || 0));
  const badges = [
    { label: "Starter", active: today.completed > 0 },
    { label: "Clean Day", active: today.total > 0 && today.completed === today.total },
    { label: "3 Day Streak", active: streak >= 3 },
    { label: "7 Day Streak", active: streak >= 7 },
  ];
  qs("#taskBadges").innerHTML = badges.map((badge) => `
    <span class="${badge.active ? "active" : ""}">${escapeHTML(badge.label)}</span>
  `).join("");
  qs("#taskWarnings").innerHTML = missedToday
    ? `<strong>${missedToday} missed today</strong><span>Finish the open rows before sleep to protect the streak.</span>`
    : `<strong>All clear</strong><span>No missed tasks for today.</span>`;
}

function renderTaskTrendGraph(series) {
  const points = series.map((day, index) => {
    const x = series.length <= 1 ? 0 : (index / (series.length - 1)) * 100;
    const y = 100 - day.pct;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
  qs("#taskTrendGraph").innerHTML = `
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Monthly task momentum">
      <polyline points="${points}" />
    </svg>
  `;
}

function renderTaskMiniRings(items) {
  qs("#taskMiniRings").innerHTML = items.map(([label, value]) => `
    <div class="task-mini-ring" style="--score:${value}%;">
      <strong>${value}%</strong>
      <span>${escapeHTML(label)}</span>
    </div>
  `).join("");
}

function taskEffectiveCompleted(task) {
  if (task.sample) {
    return Boolean(state.sampleTaskChecks[todayDateKey()]?.[task.id]);
  }
  if ((task.task_scope || "today") === "daily") {
    return Boolean(task.completed_at && localDateKey(task.completed_at) === todayDateKey());
  }
  return Boolean(task.completed);
}

function taskScheduleLabel(task) {
  const scope = task.task_scope || "today";
  if (scope === "daily") return "Daily";
  if (scope === "date") return task.due_date ? `Due ${new Date(`${task.due_date}T00:00:00`).toLocaleDateString()}` : "No date";
  return "Today";
}

function taskDueState(task) {
  if (taskEffectiveCompleted(task)) return { label: "Completed", tone: "complete" };
  const today = todayDateKey();
  const scope = task.task_scope || "today";
  if (scope === "daily" || scope === "today" || task.due_date === today) {
    return { label: "Complete by today", tone: "warning" };
  }
  if (task.due_date && task.due_date < today) return { label: "Overdue", tone: "danger" };
  if (task.due_date) return { label: "Upcoming", tone: "" };
  return { label: "No date", tone: "" };
}

function currentTaskStats() {
  const taskRows = taskRowsForDisplay();
  const total = taskRows.length;
  const completed = taskRows.filter(taskEffectiveCompleted).length;
  const dueToday = taskRows.filter((task) => taskDueState(task).label === "Complete by today").length;
  return {
    ...(state.tasks.length ? state.taskStats || {} : {}),
    total,
    completed,
    due_today: dueToday,
    completion_rate: total ? Math.round((completed / total) * 1000) / 10 : 0,
  };
}

function tasksWithWarnings() {
  return taskRowsForDisplay().filter((task) => ["Complete by today", "Overdue"].includes(taskDueState(task).label));
}

function toggleSampleTask(id) {
  const dateKey = todayDateKey();
  state.sampleTaskChecks[dateKey] = state.sampleTaskChecks[dateKey] || {};
  state.sampleTaskChecks[dateKey][id] = !state.sampleTaskChecks[dateKey][id];
  localStorage.setItem("tdos_sample_task_checks", JSON.stringify(state.sampleTaskChecks));
  renderTasks();
}

function setAllSampleTasks(checked) {
  if (state.tasks.length) {
    toast("Quick actions are for the local checklist.", "danger");
    return;
  }
  const dateKey = todayDateKey();
  state.sampleTaskChecks[dateKey] = state.sampleTaskChecks[dateKey] || {};
  state.localTasks.forEach((task) => {
    state.sampleTaskChecks[dateKey][task.id] = checked;
  });
  localStorage.setItem("tdos_sample_task_checks", JSON.stringify(state.sampleTaskChecks));
  renderTasks();
}

function removeSampleTask(id) {
  state.localTasks = state.localTasks.filter((task) => task.id !== id);
  Object.keys(state.sampleTaskChecks).forEach((dateKey) => {
    delete state.sampleTaskChecks[dateKey][id];
  });
  localStorage.setItem("tdos_local_tasks", JSON.stringify(state.localTasks));
  localStorage.setItem("tdos_local_tasks_customized", "1");
  localStorage.setItem("tdos_sample_task_checks", JSON.stringify(state.sampleTaskChecks));
  renderTasks();
}

function reorderLocalTask(sourceId, targetId) {
  if (!sourceId || !targetId || sourceId === targetId || state.tasks.length) return;
  const from = state.localTasks.findIndex((task) => task.id === sourceId);
  const to = state.localTasks.findIndex((task) => task.id === targetId);
  if (from < 0 || to < 0) return;
  const [task] = state.localTasks.splice(from, 1);
  state.localTasks.splice(to, 0, task);
  localStorage.setItem("tdos_local_tasks", JSON.stringify(state.localTasks));
  localStorage.setItem("tdos_local_tasks_customized", "1");
  renderTasks();
}

function bindTaskDragEvents() {
  const sheet = qs("#taskSheet");
  if (!sheet) return;
  sheet.addEventListener("dragstart", (event) => {
    const row = event.target.closest("[data-drag-task]");
    if (!row) return;
    state.draggingTaskId = row.dataset.dragTask;
    row.classList.add("dragging");
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", state.draggingTaskId);
  });
  sheet.addEventListener("dragend", (event) => {
    event.target.closest("[data-drag-task]")?.classList.remove("dragging");
    qsa(".sheet-task-row.drag-over", sheet).forEach((row) => row.classList.remove("drag-over"));
    state.draggingTaskId = null;
  });
  sheet.addEventListener("dragover", (event) => {
    const row = event.target.closest("[data-drag-task]");
    if (!row || !state.draggingTaskId || row.dataset.dragTask === state.draggingTaskId) return;
    event.preventDefault();
    qsa(".sheet-task-row.drag-over", sheet).forEach((item) => {
      if (item !== row) item.classList.remove("drag-over");
    });
    row.classList.add("drag-over");
  });
  sheet.addEventListener("dragleave", (event) => {
    event.target.closest("[data-drag-task]")?.classList.remove("drag-over");
  });
  sheet.addEventListener("drop", (event) => {
    const row = event.target.closest("[data-drag-task]");
    if (!row) return;
    event.preventDefault();
    row.classList.remove("drag-over");
    reorderLocalTask(state.draggingTaskId || event.dataTransfer.getData("text/plain"), row.dataset.dragTask);
  });
}

function renderTaskClock() {
  const clock = qs("#taskClock");
  if (!clock) return;
  clock.textContent = new Date().toLocaleString([], {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function renderInsights() {
  qs("#insightGrid").innerHTML = (state.insights || []).map((insight) => `
    <article class="insight-card">
      <strong>${escapeHTML(insight.title)}</strong>
      <p>${escapeHTML(insight.message)}</p>
      <small>${escapeHTML(insight.insight_type)} / ${insight.confidence}% confidence</small>
      <div class="confidence"><span style="width:${insight.confidence}%"></span></div>
    </article>
  `).join("") || empty("No insights available yet.");
}

function renderTicker() {
  const ticks = [
    ["BTC", 67420 + Math.round(Math.sin(Date.now() / 90000) * 220)],
    ["ETH", 3510 + Math.round(Math.cos(Date.now() / 90000) * 40)],
    ["NIFTY", 22520 + Math.round(Math.sin(Date.now() / 130000) * 60)],
  ];
  qs("#ticker").textContent = ticks.map(([name, value]) => `${name} ${value}`).join("  /  ");
}

function empty(text) {
  return `<div class="item-row"><span>${text}</span></div>`;
}

function renderSessionReview() {
  const review = qs("#sessionReview");
  const date = new Date();
  qs("#reviewDate").textContent = date.toLocaleDateString();
  const todayTrades = state.trades.filter((trade) => new Date(trade.timestamp).toDateString() === date.toDateString());
  const net = todayTrades.reduce((sum, trade) => sum + netTradePnlInr(trade), 0);
  const losses = todayTrades.filter((trade) => netTradePnlInr(trade) < 0).length;
  const wins = todayTrades.filter((trade) => netTradePnlInr(trade) > 0).length;
  const checklist = [
    ["Trades taken", `${todayTrades.length} / 2`],
    ["Today net", fmtMoney(net)],
    ["Win/Loss", `${wins} / ${losses}`],
    ["Next action", state.discipline?.allowed ? "Wait for valid setup" : "Stop for the day"],
  ];
  review.innerHTML = checklist.map(([label, value]) => `
    <div class="review-row">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `).join("");
}

function executionQualityStats() {
  const sample = state.trades.slice(0, 20);
  if (!sample.length) return { score: 0, sample: 0, tagged: 0, calm: 0, rr: 0 };
  const stableEmotions = new Set(["calm", "confident", "neutral"]);
  const tagged = sample.filter((trade) => setupMeta(trade).name).length;
  const calm = sample.filter((trade) => stableEmotions.has(String(trade.emotion || "").toLowerCase())).length;
  const rr = sample.filter((trade) => Number(trade.risk_reward || 0) >= 1.5).length;
  const score = Math.round(((tagged / sample.length) * 35) + ((calm / sample.length) * 35) + ((rr / sample.length) * 30));
  return { score, sample: sample.length, tagged, calm, rr };
}

function renderCommandBriefing() {
  const plan = getTodayPlan();
  const d = state.discipline || {};
  const todayTrades = state.trades.filter((trade) => new Date(trade.timestamp).toDateString() === new Date().toDateString());
  const netToday = todayTrades.reduce((sum, trade) => sum + netTradePnlInr(trade), 0);
  const lossUsed = state.riskSettings.dailyLoss ? Math.max(0, Math.abs(Math.min(0, netToday)) / state.riskSettings.dailyLoss) * 100 : 0;
  const remainingTrades = Math.max(0, 2 - todayTrades.length);
  const quality = executionQualityStats();
  const taskStats = currentTaskStats();
  const rows = [
    {
      icon: plan ? "OK" : "!",
      tone: plan ? "good" : "warn",
      title: plan ? `${plan.bias} bias / ${plan.setup || "setup not named"}` : "Daily plan missing",
      detail: plan?.notes || "Write your bias, focus setup, and no-trade condition before execution.",
      value: plan?.maxLoss ? fmtMoney(plan.maxLoss) : "Plan",
    },
    {
      icon: d.allowed ? "OK" : "X",
      tone: d.allowed ? "good" : "bad",
      title: d.allowed ? `${remainingTrades} trade slot${remainingTrades === 1 ? "" : "s"} available` : "Trading locked",
      detail: d.message || "Discipline engine ready.",
      value: fmtMoney(netToday),
    },
    {
      icon: lossUsed >= 100 ? "X" : lossUsed >= 70 ? "!" : "OK",
      tone: lossUsed >= 100 ? "bad" : lossUsed >= 70 ? "warn" : "good",
      title: "Daily loss guard",
      detail: state.riskSettings.dailyLoss ? `${lossUsed.toFixed(0)}% of daily loss limit used.` : "Set max daily loss in the Risk Desk.",
      value: state.riskSettings.dailyLoss ? fmtMoney(state.riskSettings.dailyLoss) : "Set",
    },
    {
      icon: taskStats.completion_rate >= 70 ? "OK" : "!",
      tone: taskStats.completion_rate >= 70 ? "good" : "warn",
      title: "Routine execution",
      detail: `${taskStats.completed || 0} of ${taskStats.total || 0} tasks complete today.`,
      value: `${taskStats.completion_rate || 0}%`,
    },
  ];

  qs("#commandBriefing").innerHTML = rows.map((row) => `
    <div class="briefing-row ${row.tone}">
      <div class="briefing-dot">${row.icon}</div>
      <div>
        <strong>${escapeHTML(row.title)}</strong>
        <span>${escapeHTML(row.detail)}</span>
      </div>
      <strong>${escapeHTML(row.value)}</strong>
    </div>
  `).join("");

  qs("#qualityScore").textContent = `${quality.score}%`;
  qs("#qualityMeter").style.width = `${quality.score}%`;
  const actions = coachActions(quality, plan, lossUsed);
  qs("#coachActions").innerHTML = actions.map((action) => `
    <div class="coach-action">
      <div class="briefing-dot">${action.icon}</div>
      <div>
        <strong>${escapeHTML(action.title)}</strong>
        <span>${escapeHTML(action.detail)}</span>
      </div>
      <strong>${escapeHTML(action.value)}</strong>
    </div>
  `).join("");
}

function coachActions(quality, plan, lossUsed) {
  const actions = [];
  if (!plan) {
    actions.push({ icon: "1", title: "Set the day plan", detail: "Bias, setup, max loss, and invalidation come before the next order.", value: "Required" });
  }
  if (quality.sample && quality.tagged / quality.sample < .65) {
    actions.push({ icon: "2", title: "Tag every trade with a setup", detail: "Playbook tagging makes your best and worst setups visible.", value: `${quality.tagged}/${quality.sample}` });
  }
  if (quality.sample && quality.calm / quality.sample < .7) {
    actions.push({ icon: "3", title: "Reduce emotional entries", detail: "FOMO, fear, greed, and revenge trades are lowering execution quality.", value: `${quality.calm}/${quality.sample}` });
  }
  if (quality.sample && quality.rr / quality.sample < .6) {
    actions.push({ icon: "4", title: "Demand cleaner reward", detail: "Keep planned reward at least 1.5R unless the setup is exceptional.", value: `${quality.rr}/${quality.sample}` });
  }
  if (lossUsed >= 70) {
    actions.push({ icon: "!", title: "Throttle risk today", detail: "Daily loss usage is high. Reduce size or stop for the session.", value: `${lossUsed.toFixed(0)}%` });
  }
  if (!actions.length) {
    actions.push({ icon: "OK", title: "Process is clean", detail: "Your recent trades are aligned with setup, emotion, and risk rules.", value: "Ready" });
  }
  return actions.slice(0, 3);
}

function todayPlanKey() {
  return new Date().toISOString().slice(0, 10);
}

function getTodayPlan() {
  return state.dailyPlan?.date === todayPlanKey() ? state.dailyPlan : null;
}

function saveDailyPlan() {
  state.dailyPlan = {
    date: todayPlanKey(),
    bias: qs("#planBias").value,
    setup: qs("#planSetup").value.trim(),
    maxLoss: Number(qs("#planMaxLoss").value || 0),
    notes: qs("#planNotes").value.trim(),
  };
  localStorage.setItem("tdos_daily_plan", JSON.stringify(state.dailyPlan));
  renderDailyPlan();
  renderMetrics();
  toast("Daily plan saved.");
}

function renderDailyPlan() {
  const plan = getTodayPlan();
  qs("#planBias").value = plan?.bias || "neutral";
  qs("#planSetup").value = plan?.setup || "";
  qs("#planMaxLoss").value = plan?.maxLoss || "";
  qs("#planNotes").value = plan?.notes || "";
}

function renderPositionCalculator() {
  if (!qs("#calcCapital").value) qs("#calcCapital").value = state.riskSettings.capital || "";
  if (!qs("#calcRiskPct").value) qs("#calcRiskPct").value = state.riskSettings.riskPct || "";
  const capital = Number(qs("#calcCapital").value || 0);
  const riskPct = Number(qs("#calcRiskPct").value || 0);
  const entry = Number(qs("#calcEntry").value || 0);
  const stop = Number(qs("#calcStop").value || 0);
  const stopDistance = Math.abs(entry - stop);
  const riskAmount = capital * (riskPct / 100);
  const size = stopDistance ? (riskAmount / DELTA_USD_INR_RATE) / stopDistance : 0;
  state.calculator = { size, riskAmount };
  qs("#calcSize").textContent = size ? size.toFixed(2) : "0";
  qs("#calcRiskAmount").textContent = `Risk amount ${fmtMoney(riskAmount)}`;
}

function applyCalculatedSize() {
  if (!state.calculator.size) {
    toast("Enter capital, risk, entry, and stop first.", "danger");
    return;
  }
  const form = qs("#tradeForm");
  form.elements.position_size.value = state.calculator.size.toFixed(2);
  if (!form.elements.entry.value) form.elements.entry.value = qs("#calcEntry").value;
  if (!form.elements.stop_loss.value) form.elements.stop_loss.value = qs("#calcStop").value;
  renderRiskPreview();
  toast("Position size applied.");
}

function equityStats() {
  const capital = Number(capitalSummary().starting_capital || state.riskSettings.capital || 0);
  let running = capital;
  let peak = capital;
  let maxDrawdown = 0;
  state.trades
    .slice()
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .forEach((trade) => {
      running += netTradePnlInr(trade);
      peak = Math.max(peak, running);
      const drawdown = peak ? ((peak - running) / peak) * 100 : 0;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    });
  return { equity: capitalSummary().current_capital, maxDrawdown };
}

function todayNetPnl() {
  const todayKey = new Date().toDateString();
  return state.trades
    .filter((trade) => new Date(trade.timestamp).toDateString() === todayKey)
    .reduce((sum, trade) => sum + netTradePnlInr(trade), 0);
}

async function saveRiskSettings(event) {
  event.preventDefault();
  const data = formData(event.target);
  state.riskSettings = {
    capital: Number(data.capital || 0),
    riskPct: Number(data.riskPct || 0),
    dailyLoss: Number(data.dailyLoss || 0),
    drawdownPct: Number(data.drawdownPct || 0),
  };
  localStorage.setItem("tdos_risk_settings", JSON.stringify(state.riskSettings));
  try {
    const response = await api("/capital/settings", { method: "PUT", body: JSON.stringify({ starting_capital: state.riskSettings.capital }) });
    state.capital = { ...(state.capital || {}), summary: response.summary };
    if (response.user) {
      state.user = response.user;
      localStorage.setItem("tdos_user", JSON.stringify(state.user));
    }
    cacheState();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
  }
  renderRiskDesk();
  renderPositionCalculator();
  toast("Risk settings saved.");
}

async function saveCapitalTransaction(event) {
  event.preventDefault();
  const data = formData(event.target);
  try {
    const response = await api("/capital/transactions", { method: "POST", body: JSON.stringify(data) });
    state.capital = {
      summary: response.summary,
      transactions: [response.transaction, ...(state.capital?.transactions || [])],
    };
    event.target.reset();
    cacheState();
    renderAll();
    toast(data.transaction_type === "deposit" ? "Money added to capital." : "Money withdrawn from capital.");
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    const transaction = {
      ...data,
      id: Date.now(),
      amount: Number(data.amount || 0),
      created_at: new Date().toISOString(),
    };
    state.capital = {
      ...(state.capital || {}),
      transactions: [transaction, ...(state.capital?.transactions || [])],
    };
    event.target.reset();
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: capital movement saved on this device.", "info");
  }
}

async function deleteCapitalTransaction(id) {
  try {
    const response = await api(`/capital/transactions/${id}`, { method: "DELETE" });
    state.capital = {
      summary: response.summary,
      transactions: (state.capital?.transactions || []).filter((transaction) => transaction.id !== id),
    };
    cacheState();
    renderAll();
    toast("Capital transaction deleted.");
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.capital = {
      ...(state.capital || {}),
      transactions: (state.capital?.transactions || []).filter((transaction) => transaction.id !== id),
    };
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: capital transaction removed.", "info");
  }
}

function renderRiskDesk() {
  const form = qs("#riskSettingsForm");
  if (!form) return;
  form.elements.capital.value = state.riskSettings.capital || "";
  form.elements.riskPct.value = state.riskSettings.riskPct || "";
  form.elements.dailyLoss.value = state.riskSettings.dailyLoss || "";
  form.elements.drawdownPct.value = state.riskSettings.drawdownPct || "";

  const { equity, maxDrawdown } = equityStats();
  const netToday = todayNetPnl();
  const lossUsed = state.riskSettings.dailyLoss ? Math.max(0, Math.abs(Math.min(0, netToday)) / state.riskSettings.dailyLoss) * 100 : 0;
  qs("#rEquity").textContent = fmtMoney(equity);
  qs("#rEquityText").textContent = `Start ${fmtMoney(capitalSummary().starting_capital)} + flow ${fmtMoney(Number(capitalSummary().deposits || 0) - Number(capitalSummary().withdrawals || 0))} + net P/L ${fmtMoney(capitalSummary().net_pnl)}`;
  qs("#rDailyLoss").textContent = `${Math.min(999, lossUsed).toFixed(0)}%`;
  qs("#rDailyLoss").className = lossUsed >= 100 ? "loss" : lossUsed >= 70 ? "warning" : "profit";
  qs("#rDailyLossText").textContent = state.riskSettings.dailyLoss ? `${fmtMoney(Math.abs(Math.min(0, netToday)))} used of ${fmtMoney(state.riskSettings.dailyLoss)}` : "No loss limit set";
  qs("#rDrawdown").textContent = `${maxDrawdown.toFixed(1)}%`;
  qs("#rDrawdown").className = maxDrawdown >= Number(state.riskSettings.drawdownPct || 0) ? "loss" : "profit";
  qs("#rRiskTrade").textContent = `${Number(state.riskSettings.riskPct || 0)}%`;

  renderRiskChecklist(lossUsed, maxDrawdown);
  renderPermissionSimulator();
}

function renderRiskChecklist(lossUsed, maxDrawdown) {
  const checks = [
    {
      label: "Daily loss limit",
      ok: lossUsed < 100,
      detail: lossUsed >= 100 ? "Limit reached. Stop trading." : "Daily loss is inside limit.",
    },
    {
      label: "Drawdown guard",
      ok: !state.riskSettings.drawdownPct || maxDrawdown < state.riskSettings.drawdownPct,
      detail: state.riskSettings.drawdownPct ? `Current max drawdown ${maxDrawdown.toFixed(1)}%.` : "Drawdown limit is not set.",
    },
    {
      label: "Discipline engine",
      ok: Boolean(state.discipline?.allowed),
      detail: state.discipline?.message || "Waiting for status.",
    },
    {
      label: "Daily plan",
      ok: Boolean(getTodayPlan()),
      detail: getTodayPlan() ? "Plan is saved for today." : "Set a plan before the first trade.",
    },
  ];
  const failed = checks.filter((check) => !check.ok).length;
  qs("#riskHealthLabel").textContent = failed ? `${failed} attention item${failed > 1 ? "s" : ""}` : "All clear";
  qs("#riskChecklist").innerHTML = checks.map((check) => `
    <div class="risk-check ${check.ok ? "ok" : "bad"}">
      <strong>${escapeHTML(check.label)}</strong>
      <span>${escapeHTML(check.detail)}</span>
    </div>
  `).join("");
}

function renderPermissionSimulator() {
  const plannedRisk = Number(qs("#simRisk")?.value || 0);
  const plannedReward = Number(qs("#simReward")?.value || 0);
  const maxTradeRisk = Number(capitalSummary().current_capital || state.riskSettings.capital || 0) * (Number(state.riskSettings.riskPct || 0) / 100);
  const rr = plannedRisk ? plannedReward / plannedRisk : 0;
  const allowed = Boolean(state.discipline?.allowed) && (!plannedRisk || plannedRisk <= maxTradeRisk);
  const result = qs("#simResult");
  result.className = `permission-box ${allowed ? "ok" : "bad"}`;
  result.innerHTML = `
    <strong>${allowed ? "Trade is inside rules" : "Trade needs adjustment"}</strong>
    <span>Max risk per trade: ${fmtMoney(maxTradeRisk)}. Planned R:R ${rr ? rr.toFixed(2) : "0.00"}.</span>
  `;
}

function chart(id, config) {
  const canvas = qs(`#${id}`);
  if (!canvas) return;
  if (!window.Chart) {
    drawFallbackChart(canvas, config);
    return;
  }
  if (state.charts[id]) state.charts[id].destroy();
  state.charts[id] = new Chart(canvas, config);
}

function drawFallbackChart(canvas, config) {
  const box = canvas.parentElement;
  const width = Math.max(280, box.clientWidth || 640);
  const height = Math.max(180, box.clientHeight || 292);
  const ratio = window.devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.classList.add("chart-fallback");

  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.font = "12px Segoe UI, Arial, sans-serif";
  ctx.lineWidth = 2;

  const dataset = config.data?.datasets?.[0] || {};
  const labels = config.data?.labels || [];
  const values = (dataset.data || []).map((value) => Number(value || 0));
  if (!values.length || values.every((value) => value === 0)) {
    ctx.fillStyle = "#686872";
    ctx.textAlign = "center";
    ctx.fillText("No chart data yet", width / 2, height / 2);
    return;
  }

  if (config.type === "doughnut") {
    const total = values.reduce((sum, value) => sum + Math.max(0, value), 0) || 1;
    const colors = dataset.backgroundColor || ["#ff6b4a", "#25b59f", "#f2b84b", "#6f7dfb"];
    let start = -Math.PI / 2;
    values.forEach((value, index) => {
      const slice = (Math.max(0, value) / total) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(width / 2, height / 2);
      ctx.arc(width / 2, height / 2, Math.min(width, height) * 0.34, start, start + slice);
      ctx.closePath();
      ctx.fillStyle = Array.isArray(colors) ? colors[index % colors.length] : colors;
      ctx.fill();
      start += slice;
    });
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, Math.min(width, height) * 0.19, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = "#9a9aa2";
    ctx.textAlign = "center";
    ctx.fillText(labels.join(" / "), width / 2, height - 14);
    return;
  }

  const pad = 32;
  const min = Math.min(0, ...values);
  const max = Math.max(1, ...values);
  const span = max - min || 1;
  const xFor = (index) => pad + (values.length === 1 ? (width - pad * 2) / 2 : (index / (values.length - 1)) * (width - pad * 2));
  const yFor = (value) => height - pad - ((value - min) / span) * (height - pad * 2);

  ctx.strokeStyle = "rgba(28,32,42,.08)";
  ctx.beginPath();
  ctx.moveTo(pad, yFor(0));
  ctx.lineTo(width - pad, yFor(0));
  ctx.stroke();

  if (config.type === "bar") {
    const barWidth = Math.max(8, (width - pad * 2) / values.length * 0.58);
    values.forEach((value, index) => {
      const x = xFor(index) - barWidth / 2;
      const y = yFor(Math.max(0, value));
      const base = yFor(0);
      ctx.fillStyle = value >= 0 ? "rgba(37,181,159,.76)" : "rgba(239,83,80,.76)";
      ctx.fillRect(x, Math.min(y, base), barWidth, Math.max(2, Math.abs(base - y)));
    });
  } else {
    ctx.strokeStyle = "#ff6b4a";
    ctx.beginPath();
    values.forEach((value, index) => {
      const x = xFor(index);
      const y = yFor(value);
      if (index) ctx.lineTo(x, y);
      else ctx.moveTo(x, y);
    });
    ctx.stroke();
    values.forEach((value, index) => {
      ctx.beginPath();
      ctx.arc(xFor(index), yFor(value), 3, 0, Math.PI * 2);
      ctx.fillStyle = "#ff6b4a";
      ctx.fill();
    });
  }

  ctx.fillStyle = "#7a7f8f";
  ctx.textAlign = "left";
  ctx.fillText(labels[0] || "", pad, height - 8);
  ctx.textAlign = "right";
  ctx.fillText(labels[labels.length - 1] || "", width - pad, height - 8);
}

function baseOptions(showLegend = false, moneyTicks = false) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: showLegend, labels: { color: "#6f7484", boxWidth: 10 } } },
    scales: {
      x: { grid: { color: "rgba(28,32,42,.08)" }, ticks: { color: "#7a7f8f" } },
      y: {
        grid: { color: "rgba(28,32,42,.08)" },
        ticks: {
          color: "#7a7f8f",
          callback: (value) => moneyTicks ? fmtMoney(value).replace(/\u20b9/g, "") : value,
        },
      },
    },
  };
}

function renderCharts() {
  const charts = state.analytics?.charts || {};
  const equity = charts.equity_curve || [];
  const daily = charts.daily_pl || [];
  const emotion = charts.emotion_performance || [];
  const expenses = charts.expense_categories || [];
  const winLoss = charts.win_loss || { wins: 0, losses: 0 };

  chart("dashEquityChart", {
    type: "line",
    data: { labels: equity.map((p) => p.label), datasets: [{ data: equity.map((p) => p.value), borderColor: "#ff6b4a", backgroundColor: "rgba(255,107,74,.14)", fill: true, tension: .36, pointRadius: 2 }] },
    options: baseOptions(false, true),
  });
  chart("dailyChart", {
    type: "bar",
    data: { labels: daily.map((p) => p.label), datasets: [{ data: daily.map((p) => p.value), backgroundColor: daily.map((p) => p.value >= 0 ? "rgba(37,181,159,.76)" : "rgba(239,83,80,.76)"), borderRadius: 5 }] },
    options: baseOptions(false),
  });
  chart("winLossChart", {
    type: "doughnut",
    data: { labels: ["Wins", "Losses"], datasets: [{ data: [winLoss.wins, winLoss.losses], backgroundColor: ["rgba(37,181,159,.78)", "rgba(239,83,80,.78)"] }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#6f7484" } } } },
  });
  chart("emotionChart", {
    type: "bar",
    data: { labels: emotion.map((p) => p.label), datasets: [{ data: emotion.map((p) => p.value), backgroundColor: "rgba(111,125,251,.72)", borderRadius: 5 }] },
    options: baseOptions(false),
  });
  const expenseConfig = {
    type: "doughnut",
    data: { labels: expenses.map((p) => p.label), datasets: [{ data: expenses.map((p) => p.value), backgroundColor: ["#ff6b4a", "#25b59f", "#f2b84b", "#6f7dfb", "#ef5350"] }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#6f7484" } } } },
  };
  chart("expenseChart", expenseConfig);
  chart("expensePageChart", expenseConfig);
}

function setPage(page) {
  qsa(".page").forEach((node) => node.classList.toggle("active", node.id === page));
  qsa(".nav-btn").forEach((node) => node.classList.toggle("active", node.dataset.page === page));
  const titles = { dashboard: "Dashboard", journal: "Trade Journal", risk: "Risk Desk", analytics: "Analytics", expenses: "Expenses", tasks: "Tasks", insights: "AI Insights" };
  qs("#pageTitle").textContent = titles[page] || "Command Center";
  setTimeout(renderCharts, 0);
}

async function submitAuth(event, mode) {
  event.preventDefault();
  try {
    const data = await api(`/auth/${mode}`, { method: "POST", body: JSON.stringify(formData(event.target)) });
    if (mode === "signup" && data.pending) {
      const notice = qs("#signupNotice");
      notice.textContent = data.message;
      notice.classList.remove("hidden");
      event.target.reset();
      toast("Verification email sent.");
      return;
    }
    saveAuth(data.token, data.user);
    toast(mode === "login" ? "Login successful." : "Account created.");
    showApp();
  } catch (error) {
    toast(error.message, "danger");
  }
}

async function saveTrade(event) {
  event.preventDefault();
  if (!state.editingTradeId && !preTradeChecklistComplete()) {
    toast("Complete the pre-trade checklist before logging a new trade.", "danger");
    return;
  }
  const data = encodeTradePayload(event.target);
  const path = state.editingTradeId ? `/trades/${state.editingTradeId}` : "/trades";
  const method = state.editingTradeId ? "PUT" : "POST";
  try {
    await api(path, { method, body: JSON.stringify(data) });
    state.editingTradeId = null;
    qs("#tradeFormTitle").textContent = "New Trade Entry";
    qs("#cancelEditTrade").classList.add("hidden");
    event.target.reset();
    resetChecklist();
    renderRiskPreview();
    localStorage.removeItem("tdos_trade_draft");
    toast("Trade saved.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    const id = state.editingTradeId || Date.now();
    const trade = {
      ...data,
      id,
      entry: Number(data.entry || 0),
      exit: Number(data.exit || 0),
      stop_loss: Number(data.stop_loss || 0),
      position_size: Number(data.position_size || 0),
      pnl: Number(data.pnl || 0),
      brokerage: Number(data.brokerage || 0),
      risk_reward: Number(data.risk_reward || 0),
      timestamp: data.timestamp || new Date().toISOString(),
    };
    if (state.editingTradeId) state.trades = state.trades.map((item) => item.id === state.editingTradeId ? trade : item);
    else state.trades.unshift(trade);
    state.editingTradeId = null;
    qs("#tradeFormTitle").textContent = "New Trade Entry";
    qs("#cancelEditTrade").classList.add("hidden");
    event.target.reset();
    resetChecklist();
    renderRiskPreview();
    localStorage.removeItem("tdos_trade_draft");
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: trade saved on this device.", "info");
  }
}

function editTrade(id) {
  const trade = state.trades.find((item) => item.id === id);
  if (!trade) return;
  const form = qs("#tradeForm");
  state.editingTradeId = id;
  Object.entries(trade).forEach(([key, value]) => {
    if (!form.elements[key]) return;
    form.elements[key].value = key === "timestamp" ? value.slice(0, 16) : value;
  });
  const meta = setupMeta(trade);
  form.elements.setup_tag.value = state.playbook.some((setup) => setup.id === meta.id) ? meta.id : "";
  form.elements.trade_reason.value = meta.reason;
  qs("#tradeFormTitle").textContent = "Edit Trade Entry";
  qs("#cancelEditTrade").classList.remove("hidden");
  resetChecklist(true);
  renderRiskPreview();
  setPage("journal");
}

async function deleteTrade(id) {
  try {
    await api(`/trades/${id}`, { method: "DELETE" });
    toast("Trade deleted.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.trades = state.trades.filter((trade) => trade.id !== id);
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: trade removed from this device.", "info");
  }
}

async function addExpense(event) {
  event.preventDefault();
  const data = formData(event.target);
  try {
    await api("/expenses", { method: "POST", body: JSON.stringify(data) });
    event.target.reset();
    toast("Expense added.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.expenses.unshift({
      ...data,
      id: Date.now(),
      amount: Number(data.amount || 0),
    });
    event.target.reset();
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: expense saved on this device.", "info");
  }
}

async function deleteExpense(id) {
  try {
    await api(`/expenses/${id}`, { method: "DELETE" });
    toast("Expense deleted.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.expenses = state.expenses.filter((expense) => expense.id !== id);
    refreshLocalAnalytics();
    renderAll();
    toast("Offline mode: expense removed from this device.", "info");
  }
}

async function addTask(event) {
  event.preventDefault();
  const data = formData(event.target);
  if (data.task_scope === "date" && !data.due_date) {
    toast("Choose a due date for this task.", "danger");
    return;
  }
  if (data.task_scope === "today") data.due_date = todayDateKey();
  if (data.task_scope === "daily") data.due_date = "";
  if (!state.tasks.length) {
    addLocalTask(data);
    event.target.reset();
    updateTaskDueDateControl();
    toast("Task added.");
    return;
  }
  try {
    await api("/tasks", { method: "POST", body: JSON.stringify(data) });
    event.target.reset();
    updateTaskDueDateControl();
    toast("Task added.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    addLocalTask(data);
    event.target.reset();
    updateTaskDueDateControl();
    toast("Offline mode: task saved on this device.", "info");
  }
}

function addLocalTask(data) {
  const title = String(data.title || "").trim();
  if (!title) return;
  state.localTasks.push({
    id: `local-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
    title,
    category: data.category || "routine",
    task_scope: data.task_scope || "daily",
    due_date: data.due_date || "",
    sample: true,
  });
  localStorage.setItem("tdos_local_tasks", JSON.stringify(state.localTasks));
  localStorage.setItem("tdos_local_tasks_customized", "1");
  renderTasks();
}

async function toggleTask(id) {
  try {
    await api(`/tasks/${id}/complete`, { method: "PATCH" });
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.tasks = state.tasks.map((task) => task.id === id ? {
      ...task,
      completed: !taskEffectiveCompleted(task),
      completed_at: taskEffectiveCompleted(task) ? null : new Date().toISOString(),
    } : task);
    cacheState();
    renderTasks();
    toast("Offline mode: task updated on this device.", "info");
  }
}

async function deleteTask(id) {
  try {
    await api(`/tasks/${id}`, { method: "DELETE" });
    toast("Task deleted.");
    await loadAll();
  } catch (error) {
    if (!isOfflineError(error)) {
      toast(error.message, "danger");
      return;
    }
    state.tasks = state.tasks.filter((task) => task.id !== id);
    cacheState();
    renderTasks();
    toast("Offline mode: task removed from this device.", "info");
  }
}

async function emailTaskWarnings() {
  if (!tasksWithWarnings().length) {
    toast("No task warnings to email.", "danger");
    return;
  }
  try {
    const data = await api("/tasks/warnings/email", { method: "POST" });
    toast(data.sent_to ? `Warning email sent to ${data.sent_to}.` : data.message);
  } catch (error) {
    toast(error.message, "danger");
  }
}

async function regenerateInsights() {
  try {
    const data = await api("/insights/generate", { method: "POST" });
    state.insights = data.insights || [];
    renderInsights();
    toast("Insights regenerated.");
  } catch (error) {
    toast(error.message, "danger");
  }
}

function logout() {
  clearAuth();
  showAuth();
}

function preTradeChecklistComplete() {
  const checks = qsa("[data-checklist]");
  return checks.every((check) => check.checked);
}

function resetChecklist(checked = false) {
  qsa("[data-checklist]").forEach((check) => { check.checked = checked; });
}

function calculateTradeAmounts(form) {
  const entry = Number(form.elements.entry?.value || 0);
  const exit = Number(form.elements.exit?.value || 0);
  const stop = Number(form.elements.stop_loss?.value || 0);
  const size = Number(form.elements.position_size?.value || 0);
  const direction = String(form.elements.direction?.value || "long").toLowerCase();
  const signedMove = direction === "short" ? entry - exit : exit - entry;
  const pnlUsd = signedMove * size;
  const riskUsd = Math.abs(entry - stop) * size;
  const riskReward = riskUsd ? Math.abs(pnlUsd) / riskUsd : 0;
  return { entry, exit, stop, size, pnlUsd, riskUsd, riskReward };
}

function updateTradeDerivedFields(form) {
  const { entry, exit, stop, size, pnlUsd, riskReward } = calculateTradeAmounts(form);
  const hasTradeMath = entry && exit && stop && size;
  if (!hasTradeMath) return;
  form.elements.pnl.value = pnlUsd.toFixed(2);
  form.elements.risk_reward.value = riskReward.toFixed(2);
}

function renderRiskPreview() {
  const form = qs("#tradeForm");
  if (!form) return;
  const { entry, stop, size, riskUsd } = calculateTradeAmounts(form);
  qs("#positionRisk").textContent = fmtMoney(deltaUsdToInr(riskUsd));
  qs("#positionRiskText").textContent = riskUsd
    ? `${Math.abs(entry - stop).toFixed(4)} points x ${size || 0} size = $${riskUsd.toFixed(2)} x ${DELTA_USD_INR_RATE}`
    : "Entry, stop, and size calculate this automatically.";
}

function setCurrentTradeTime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  qs("#tradeForm").elements.timestamp.value = now.toISOString().slice(0, 16);
}

function updateTaskDueDateControl() {
  const form = qs("#taskForm");
  const scope = form.elements.task_scope.value;
  const dueDate = form.elements.due_date;
  dueDate.min = todayDateKey();
  dueDate.disabled = scope !== "date";
  dueDate.required = scope === "date";
  if (scope === "today") dueDate.value = todayDateKey();
  if (scope === "daily") dueDate.value = "";
}

function refreshLiveTaskTime() {
  const previousDate = state.currentDateKey;
  const currentDate = todayDateKey();
  state.currentDateKey = currentDate;
  renderTaskClock();
  if (previousDate && previousDate !== currentDate) {
    updateTaskDueDateControl();
    renderTasks();
    if (state.token) loadAll();
  }
}

function exportTradesCsv() {
  const rows = filteredTrades();
  if (!rows.length) {
    toast("No trades to export.", "danger");
    return;
  }
  const headers = ["time", "pair", "setup", "direction", "entry", "exit", "stop_loss", "position_size", "pnl_usd", "brokerage_inr", "net_pnl_inr", "risk_reward", "emotion", "reason", "notes"];
  const csv = [
    headers.join(","),
    ...rows.map((trade) => headers.map((key) => {
      const meta = setupMeta(trade);
      const value = key === "time"
        ? trade.timestamp
        : key === "setup"
          ? meta.name
          : key === "reason"
            ? meta.reason
            : key === "pnl_usd"
            ? trade.pnl
              : key === "brokerage_inr"
                ? tradeBrokerage(trade)
                : key === "net_pnl_inr"
                  ? netTradePnlInr(trade)
                : trade[key];
      return `"${String(value ?? "").replace(/"/g, '""')}"`;
    }).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `tdos-trades-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function bindEvents() {
  qsa(".auth-tab").forEach((button) => {
    button.addEventListener("click", () => {
      qsa(".auth-tab").forEach((tab) => tab.classList.remove("active"));
      qsa(".auth-form").forEach((form) => form.classList.remove("active"));
      button.classList.add("active");
      qs(`#${button.dataset.auth}Form`).classList.add("active");
    });
  });
  qs("#loginForm").addEventListener("submit", (event) => submitAuth(event, "login"));
  qs("#signupForm").addEventListener("submit", (event) => submitAuth(event, "signup"));
  qs("#logoutBtn").addEventListener("click", logout);
  qs("#tradeForm").addEventListener("submit", saveTrade);
  qs("#riskSettingsForm").addEventListener("submit", saveRiskSettings);
  qs("#capitalForm").addEventListener("submit", saveCapitalTransaction);
  qs("#expenseForm").addEventListener("submit", addExpense);
  qs("#taskForm").addEventListener("submit", addTask);
  qs("#taskScope").addEventListener("change", updateTaskDueDateControl);
  qs("#emailTaskWarnings").addEventListener("click", emailTaskWarnings);
  qs("#markAllSampleTasks").addEventListener("click", () => setAllSampleTasks(true));
  qs("#clearSampleTasks").addEventListener("click", () => setAllSampleTasks(false));
  bindTaskDragEvents();
  qs("#generateInsights").addEventListener("click", regenerateInsights);
  qs("#cancelEditTrade").addEventListener("click", () => {
    state.editingTradeId = null;
    qs("#tradeForm").reset();
    qs("#tradeFormTitle").textContent = "New Trade Entry";
    qs("#cancelEditTrade").classList.add("hidden");
    resetChecklist();
    renderRiskPreview();
  });
  qs("#menuToggle").addEventListener("click", () => qs(".sidebar").classList.toggle("open"));
  qsa(".nav-btn").forEach((button) => button.addEventListener("click", () => setPage(button.dataset.page)));
  qsa("[data-jump]").forEach((button) => button.addEventListener("click", () => setPage(button.dataset.jump)));
  qsa("[data-template-pair]").forEach((button) => {
    button.addEventListener("click", () => {
      qs("#tradeForm").elements.pair.value = button.dataset.templatePair;
    });
  });
  qs("[data-now-time]").addEventListener("click", setCurrentTradeTime);
  qs("#tradeSearch").addEventListener("input", (event) => {
    state.filters.search = event.target.value;
    renderTrades();
  });
  qs("#outcomeFilter").addEventListener("change", (event) => {
    state.filters.outcome = event.target.value;
    renderTrades();
  });
  qs("#emotionFilter").addEventListener("change", (event) => {
    state.filters.emotion = event.target.value;
    renderTrades();
  });
  qs("#exportTrades").addEventListener("click", exportTradesCsv);
  qs("#savePlan").addEventListener("click", saveDailyPlan);
  qsa("#calcCapital, #calcRiskPct, #calcEntry, #calcStop").forEach((input) => {
    input.addEventListener("input", renderPositionCalculator);
  });
  qsa("#simRisk, #simReward").forEach((input) => {
    input.addEventListener("input", renderPermissionSimulator);
  });
  qs("#applyCalcSize").addEventListener("click", applyCalculatedSize);
  qs("#addPlaybookSetup").addEventListener("click", addPlaybookSetup);
  document.body.addEventListener("click", async (event) => {
    const target = event.target;
    if (target.dataset.editTrade) editTrade(Number(target.dataset.editTrade));
    if (target.dataset.deleteTrade) await deleteTrade(Number(target.dataset.deleteTrade));
    if (target.dataset.deleteExpense) await deleteExpense(Number(target.dataset.deleteExpense));
    if (target.dataset.deleteCapital) await deleteCapitalTransaction(Number(target.dataset.deleteCapital));
    if (target.dataset.completeTask) await toggleTask(Number(target.dataset.completeTask));
    if (target.dataset.toggleSampleTask) toggleSampleTask(target.dataset.toggleSampleTask);
    if (target.dataset.removeSampleTask) removeSampleTask(target.dataset.removeSampleTask);
    if (target.dataset.deleteTask) await deleteTask(Number(target.dataset.deleteTask));
    if (target.dataset.deleteSetup) deletePlaybookSetup(target.dataset.deleteSetup);
  });
  const tradeForm = qs("#tradeForm");
  const draft = JSON.parse(localStorage.getItem("tdos_trade_draft") || "null");
  if (draft) Object.entries(draft).forEach(([key, value]) => { if (tradeForm.elements[key]) tradeForm.elements[key].value = value; });
  const refreshTradeMath = () => {
    updateTradeDerivedFields(tradeForm);
    localStorage.setItem("tdos_trade_draft", JSON.stringify(formData(tradeForm)));
    renderRiskPreview();
  };
  tradeForm.addEventListener("input", refreshTradeMath);
  tradeForm.addEventListener("change", refreshTradeMath);
  refreshTradeMath();
  updateTaskDueDateControl();
}

async function bootstrap() {
  bindEvents();
  createIcons();
  registerServiceWorker();
  qs("#pageTitle").textContent = "Dashboard";
  state.currentDateKey = todayDateKey();
  setInterval(renderTicker, 3500);
  setInterval(refreshLiveTaskTime, 1000);
  setTimeout(() => qs("#loader").classList.add("hidden"), 800);
  if (!state.token) {
    showAuth();
    return;
  }
  try {
    const data = await api("/auth/me");
    state.user = data.user;
    localStorage.setItem("tdos_user", JSON.stringify(data.user));
    showApp();
  } catch (error) {
    if (isOfflineError(error) && state.user) {
      showApp();
      toast("Offline mode: using your saved session.", "info");
      return;
    }
    clearAuth();
    showAuth();
  }
}

bootstrap();
