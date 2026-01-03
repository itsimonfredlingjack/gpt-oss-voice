/* Serverkontroll (touch-first) */

// Optional auth: pass ?token=... once, we store it in sessionStorage.
const urlParams = new URLSearchParams(window.location.search);
const tokenFromQuery = urlParams.get("token");
if (tokenFromQuery) sessionStorage.setItem("dashboardApiToken", tokenFromQuery);
const apiToken = sessionStorage.getItem("dashboardApiToken");

const debugEnabled = ["1", "true", "yes", "y", "on"].includes(
  (urlParams.get("debug") || "").trim().toLowerCase(),
);

const api = {
  async getStatus() {
    const res = await fetch("/api/status", { cache: "no-store" });
    if (!res.ok) throw new Error(`status ${res.status}`);
    return await res.json();
  },
  async trigger(action, opts = {}) {
    const res = await fetch("/api/trigger", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiToken ? { "X-API-Token": apiToken } : {}),
      },
      body: JSON.stringify({ action, ...opts }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.message || `trigger ${res.status}`);
    return data;
  },
};

const els = {
  hostValue: document.getElementById("hostValue"),
  cpuValue: document.getElementById("cpuValue"),
  ramValue: document.getElementById("ramValue"),
  modelValue: document.getElementById("modelValue"),
  tempValue: document.getElementById("tempValue"),
  syncValue: document.getElementById("syncValue"),
  apiState: document.getElementById("apiState"),
  logLines: document.getElementById("logLines"),
  inputDebug: document.getElementById("inputDebug"),
  buttons: Array.from(document.querySelectorAll(".diagBtn")),
};

const state = {
  log: [],
  armedAction: null,
  armedUntilTs: 0,
  armedTimer: null,
};

function nowTime() {
  const d = new Date();
  return d.toLocaleTimeString("sv-SE", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function addLog(line, level = "info") {
  const prefix = level === "error" ? "FEL" : level === "warn" ? "VAR" : "OK ";
  state.log.unshift(`[${nowTime()}] ${prefix}  ${line}`);
  state.log = state.log.slice(0, 14);
  els.logLines.textContent = state.log.join("\n");
}

function fmtPercent(value) {
  if (value === null || value === undefined) return "—";
  return `${Math.round(value)}%`;
}

function setApiState(ok, message) {
  els.apiState.textContent = `API: ${ok ? "ONLINE" : "OFFLINE"}${
    message ? ` (${message})` : ""
  }`;
}

function renderStatus(status) {
  const host = status?.hostname || status?.ip || "—";
  els.hostValue.textContent = host;
  els.cpuValue.textContent = fmtPercent(status?.cpu?.percent);
  els.ramValue.textContent = fmtPercent(status?.memory?.percent);

  els.modelValue.textContent = status?.settings?.ollama_model || "—";
  const temp = status?.settings?.ollama_temperature;
  els.tempValue.textContent =
    temp === null || temp === undefined ? "—" : String(temp);

  const ts = status?.ts ? new Date(status.ts) : null;
  els.syncValue.textContent = ts
    ? ts.toLocaleTimeString("sv-SE", { hour: "2-digit", minute: "2-digit" })
    : "—";
}

function attachActivateHandler(el, handler) {
  // Some embedded/cast WebViews deliver pointer/touch but not "click".
  // We listen for pointerup (preferred) and keep click as a fallback.
  let lastPointerUpAt = 0;

  el.addEventListener("pointerup", (ev) => {
    lastPointerUpAt = Date.now();
    handler(ev);
  });

  el.addEventListener("click", (ev) => {
    if (Date.now() - lastPointerUpAt < 700) return;
    handler(ev);
  });
}

function setBtnState(btn, stateName) {
  btn.classList.remove(
    "diagBtn--working",
    "diagBtn--ok",
    "diagBtn--err",
    "diagBtn--confirm",
  );
  if (stateName === "working") btn.classList.add("diagBtn--working");
  if (stateName === "ok") btn.classList.add("diagBtn--ok");
  if (stateName === "err") btn.classList.add("diagBtn--err");
  if (stateName === "confirm") btn.classList.add("diagBtn--confirm");
}

function disarmConfirm() {
  state.armedAction = null;
  state.armedUntilTs = 0;
  if (state.armedTimer) window.clearTimeout(state.armedTimer);
  state.armedTimer = null;
  for (const b of els.buttons) setBtnState(b, "");
}

function armConfirm(actionId, btn) {
  disarmConfirm();
  state.armedAction = actionId;
  state.armedUntilTs = Date.now() + 6000;
  setBtnState(btn, "confirm");
  state.armedTimer = window.setTimeout(() => {
    disarmConfirm();
  }, 6000);
}

async function runAction(btn) {
  const actionId = btn.dataset.action || "";
  const titleEl = btn.querySelector(".diagBtn__title");
  const label = titleEl ? titleEl.textContent : actionId;
  const dangerous = btn.dataset.dangerous === "1";

  // Two-tap confirm for dangerous actions.
  let confirm = false;
  if (dangerous) {
    const armedOk =
      state.armedAction === actionId && Date.now() <= state.armedUntilTs;
    if (!armedOk) {
      armConfirm(actionId, btn);
      addLog(`${label}: bekräfta (tryck igen)`, "warn");
      return;
    }
    confirm = true;
    disarmConfirm();
  }

  // Prevent overlapping actions.
  for (const b of els.buttons) b.disabled = true;

  setBtnState(btn, "working");
  addLog(`${label}: kör…`, "warn");

  try {
    const result = await api.trigger(actionId, confirm ? { confirm: true } : {});
    addLog(result?.message || `${label}: klar`);
    setBtnState(btn, "ok");

    // Fast refresh for model/temp actions.
    if (actionId === "switch_model" || actionId === "lower_temperature") {
      try {
        const status = await api.getStatus();
        renderStatus(status);
      } catch {
        // ignore
      }
    }
  } catch (err) {
    addLog(`${label}: ${err?.message || err}`, "error");
    setBtnState(btn, "err");
  } finally {
    for (const b of els.buttons) b.disabled = false;
    window.setTimeout(() => setBtnState(btn, ""), 1800);
  }
}

function initButtons() {
  for (const btn of els.buttons) {
    attachActivateHandler(btn, () => runAction(btn));
  }
}

function initInputDebug() {
  if (!debugEnabled) return;
  if (!els.inputDebug) return;

  els.inputDebug.classList.remove("inputDebug--hidden");
  els.inputDebug.setAttribute("aria-hidden", "false");

  const fmt = (n) => (typeof n === "number" ? Math.round(n) : "—");
  const write = (line) => {
    els.inputDebug.textContent = line;
  };

  const handler = (type, ev) => {
    const target = ev?.target?.tagName ? ev.target.tagName.toLowerCase() : "—";
    const x = fmt(ev?.clientX);
    const y = fmt(ev?.clientY);
    const p = ev?.pointerType ? String(ev.pointerType) : "—";
    write(`[input] ${type}  target=${target}  x=${x} y=${y}  pointer=${p}`);
  };

  ["pointerdown", "pointerup", "touchstart", "touchend", "click"].forEach((t) => {
    document.addEventListener(t, (ev) => handler(t, ev), {
      capture: true,
      passive: true,
    });
  });

  write("[input] debug=1");
}

async function refreshStatusOnce() {
  const status = await api.getStatus();
  renderStatus(status);
  setApiState(true, "");
}

async function boot() {
  initInputDebug();
  initButtons();
  addLog("Startar…");

  try {
    await refreshStatusOnce();
    addLog("Redo.");
  } catch (err) {
    setApiState(false, "offline");
    addLog(`API offline: ${err?.message || err}`, "error");
  }

  window.setInterval(async () => {
    try {
      await refreshStatusOnce();
    } catch {
      setApiState(false, "offline");
    }
  }, 2000);
}

boot();
