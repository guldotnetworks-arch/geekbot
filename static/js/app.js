/* ── Productivity Tracker – frontend ── */

const CIRCUMFERENCE = 2 * Math.PI * 52; // r=52 from SVG

// ── State ────────────────────────────────────────────────────────────────────
let timerInterval = null;
let timerRunning = false;
let timerSeconds = 25 * 60;
let timerTotal = 25 * 60;
let currentMode = "work";
let activeTaskId = null;
let taskTimerSeconds = 0; // accumulated seconds for active task this session

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const d = new Date();
  document.getElementById("today-label").textContent = d.toLocaleDateString("en-US", {
    weekday: "long", month: "long", day: "numeric", year: "numeric",
  });

  setupTimerModes();
  setupTaskForm();
  loadTasks();
  loadStats();
  renderRing(1);
});

// ── Timer ─────────────────────────────────────────────────────────────────────
function setupTimerModes() {
  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (timerRunning) return;
      document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.dataset.mode;
      timerTotal = parseInt(btn.dataset.minutes, 10) * 60;
      timerSeconds = timerTotal;
      renderTimer();
      renderRing(1);
    });
  });

  document.getElementById("btn-start").addEventListener("click", toggleTimer);
  document.getElementById("btn-reset").addEventListener("click", resetTimer);
}

function toggleTimer() {
  if (timerRunning) {
    pauseTimer();
  } else {
    startTimer();
  }
}

function startTimer() {
  timerRunning = true;
  document.getElementById("btn-start").textContent = "Pause";
  document.getElementById("ring-progress").classList.add("running");
  activeTaskId = document.getElementById("timer-task-select").value || null;

  timerInterval = setInterval(() => {
    timerSeconds--;
    if (currentMode === "work") taskTimerSeconds++;
    renderTimer();
    renderRing(timerSeconds / timerTotal);

    if (timerSeconds <= 0) {
      clearInterval(timerInterval);
      timerRunning = false;
      onTimerComplete();
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timerInterval);
  timerRunning = false;
  document.getElementById("btn-start").textContent = "Resume";
  document.getElementById("ring-progress").classList.remove("running");
  if (currentMode === "work" && activeTaskId) {
    patchTaskTime(activeTaskId, taskTimerSeconds);
  }
}

function resetTimer() {
  clearInterval(timerInterval);
  timerRunning = false;
  if (currentMode === "work" && activeTaskId && taskTimerSeconds > 0) {
    patchTaskTime(activeTaskId, taskTimerSeconds);
  }
  taskTimerSeconds = 0;
  timerSeconds = timerTotal;
  document.getElementById("btn-start").textContent = "Start";
  document.getElementById("ring-progress").classList.remove("running");
  renderTimer();
  renderRing(1);
}

function onTimerComplete() {
  document.getElementById("ring-progress").classList.remove("running");
  document.getElementById("btn-start").textContent = "Start";

  const duration = timerTotal - timerSeconds; // should be ~timerTotal
  logSession(activeTaskId, timerTotal, currentMode);

  if (currentMode === "work" && activeTaskId) {
    patchTaskTime(activeTaskId, taskTimerSeconds);
  }
  taskTimerSeconds = 0;

  playBell();
  timerSeconds = timerTotal;
  renderTimer();
  renderRing(1);
  loadStats();
}

function renderTimer() {
  const m = Math.floor(timerSeconds / 60).toString().padStart(2, "0");
  const s = (timerSeconds % 60).toString().padStart(2, "0");
  document.getElementById("timer-time").textContent = `${m}:${s}`;
}

function renderRing(fraction) {
  const offset = CIRCUMFERENCE * (1 - fraction);
  const ring = document.getElementById("ring-progress");
  ring.style.strokeDasharray = CIRCUMFERENCE;
  ring.style.strokeDashoffset = offset;
}

function playBell() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 1.5);
  } catch (_) {}
}

// ── Task API calls ─────────────────────────────────────────────────────────────
async function loadTasks() {
  const res = await fetch("/api/tasks");
  const tasks = await res.json();
  renderTaskList(tasks);
  populateTaskSelect(tasks);
}

async function createTask(title) {
  const res = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  const task = await res.json();
  await loadTasks();
  await loadStats();
  return task;
}

async function toggleTask(id, done) {
  await fetch(`/api/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ done }),
  });
  await loadTasks();
  await loadStats();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  await loadTasks();
  await loadStats();
}

async function patchTaskTime(id, seconds) {
  await fetch(`/api/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ total_seconds: seconds }),
  });
  await loadTasks();
}

// ── Session API ───────────────────────────────────────────────────────────────
async function logSession(taskId, durationSeconds, sessionType) {
  await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId || null, duration_seconds: durationSeconds, session_type: sessionType }),
  });
}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function loadStats() {
  const res = await fetch("/api/stats");
  const data = await res.json();
  document.getElementById("stat-pomodoros").textContent = data.pomodoros;
  document.getElementById("stat-focus").textContent = `${data.focus_minutes}m`;
  document.getElementById("stat-tasks").textContent = `${data.tasks_done}/${data.tasks_total}`;
  renderChart(data.history);
}

// ── Render helpers ────────────────────────────────────────────────────────────
function renderTaskList(tasks) {
  const ul = document.getElementById("task-list");
  ul.innerHTML = "";
  if (tasks.length === 0) {
    ul.innerHTML = '<li style="color:var(--muted);font-size:.85rem;text-align:center;padding:.5rem">No tasks yet — add one above!</li>';
    return;
  }
  tasks.forEach(t => {
    const li = document.createElement("li");
    li.className = `task-item${t.done ? " done" : ""}`;
    li.dataset.id = t.id;

    const check = document.createElement("div");
    check.className = `task-check${t.done ? " checked" : ""}`;
    check.addEventListener("click", () => toggleTask(t.id, !t.done));

    const title = document.createElement("span");
    title.className = "task-title";
    title.textContent = t.title;

    const time = document.createElement("span");
    time.className = "task-time";
    time.textContent = formatSeconds(t.total_seconds);

    const del = document.createElement("button");
    del.className = "task-delete";
    del.textContent = "×";
    del.setAttribute("aria-label", "Delete task");
    del.addEventListener("click", () => deleteTask(t.id));

    li.append(check, title, time, del);
    ul.appendChild(li);
  });
}

function populateTaskSelect(tasks) {
  const sel = document.getElementById("timer-task-select");
  const current = sel.value;
  sel.innerHTML = '<option value="">— no task selected —</option>';
  tasks.filter(t => !t.done).forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = t.title;
    sel.appendChild(opt);
  });
  if (current) sel.value = current;
}

function renderChart(history) {
  const chart = document.getElementById("bar-chart");
  chart.innerHTML = "";
  const maxVal = Math.max(...history.map(h => h.focus_minutes), 1);
  history.forEach(h => {
    const col = document.createElement("div");
    col.className = "bar-col";

    const val = document.createElement("span");
    val.className = "bar-val";
    val.textContent = h.focus_minutes > 0 ? `${h.focus_minutes}m` : "";

    const bar = document.createElement("div");
    bar.className = "bar";
    const pct = (h.focus_minutes / maxVal) * 100;
    bar.style.height = `${Math.max(pct, 2)}%`;

    const label = document.createElement("span");
    label.className = "bar-label";
    const d = new Date(h.date + "T00:00:00");
    label.textContent = d.toLocaleDateString("en-US", { weekday: "short" });

    col.append(val, bar, label);
    chart.appendChild(col);
  });
}

function formatSeconds(s) {
  if (!s) return "";
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m > 0 ? `${m}m ${sec}s` : `${sec}s`;
}

// ── Task form ────────────────────────────────────────────────────────────────
function setupTaskForm() {
  document.getElementById("task-form").addEventListener("submit", async e => {
    e.preventDefault();
    const input = document.getElementById("task-input");
    const title = input.value.trim();
    if (!title) return;
    input.value = "";
    await createTask(title);
  });
}
