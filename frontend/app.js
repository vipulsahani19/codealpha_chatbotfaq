/* ===================================================================
   CircuitBot frontend — talks to the FastAPI backend for everything.
   No matching logic lives here anymore; this file only renders the UI
   and calls the API defined in config.js (API_BASE).
   =================================================================== */

const els = {
  messages: document.getElementById("messages"),
  form: document.getElementById("composerForm"),
  input: document.getElementById("userInput"),
  topicList: document.getElementById("topicList"),
  statAsked: document.getElementById("statAsked"),
  statFaqs: document.getElementById("statFaqs"),
  statAvg: document.getElementById("statAvg"),
  statMemory: document.getElementById("statMemory"),
  statusBadge: document.getElementById("statusBadge"),
  statusText: document.getElementById("statusText"),
};

async function init() {
  els.form.addEventListener("submit", onSubmit);
  renderWelcome();
  await checkHealth();
  await loadCategories();
  await refreshStats();
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error("bad status");
    setStatus(true);
  } catch (err) {
    setStatus(false);
    showConnectionError();
  }
}

function setStatus(online) {
  els.statusBadge.classList.toggle("online", online);
  els.statusBadge.classList.toggle("offline", !online);
  els.statusText.textContent = online ? "backend online" : "backend offline";
}

function showConnectionError() {
  const div = document.createElement("div");
  div.className = "welcome";
  div.innerHTML = `Can't reach the backend at <code>${escapeHtml(API_BASE)}</code>. Start it with
    <code>uvicorn main:app --reload --port 8000</code> from the <code>backend/</code> folder,
    or update <code>API_BASE</code> in <code>config.js</code> to your deployed Render URL.`;
  els.messages.appendChild(div);
}

async function loadCategories() {
  try {
    const res = await fetch(`${API_BASE}/api/categories`);
    const categories = await res.json();
    categories.forEach(cat => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "topic-chip";
      chip.textContent = cat.category;
      chip.addEventListener("click", () => askQuestion(cat.question));
      els.topicList.appendChild(chip);
    });
  } catch (err) {
    // Sidebar topics are a nice-to-have; fail silently if backend is down,
    // the connection error banner already covers it.
  }
}

async function refreshStats() {
  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    const stats = await res.json();
    applyStats(stats);
  } catch (err) {
    /* backend offline — leave placeholders */
  }
}

function applyStats(stats) {
  els.statAsked.textContent = stats.asked;
  els.statFaqs.textContent = stats.faqs_count;
  els.statAvg.textContent = stats.asked > 0 ? Math.round(stats.avg_score * 100) + "%" : "—";
  els.statMemory.textContent = `${stats.memory.length}/${stats.memory_limit}`;
}

function renderWelcome() {
  const div = document.createElement("div");
  div.className = "welcome";
  div.innerHTML = `Hi! I'm CircuitBot — ask me anything about B.Tech, AI, machine learning, programming languages, DSA, databases, or placements. Try a topic chip on the left, or just type your question below.`;
  els.messages.appendChild(div);
}

function onSubmit(e) {
  e.preventDefault();
  const q = els.input.value.trim();
  if (!q) return;
  els.input.value = "";
  askQuestion(q);
}

async function askQuestion(question) {
  addUserMessage(question);
  const typingNode = addTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error(`status ${res.status}`);
    const data = await res.json();

    typingNode.remove();
    setStatus(true);

    if (data.matched) {
      addBotMessage(data.answer, data.score, data.category);
    } else {
      addFallbackMessage(data.message, data.suggestions || []);
    }
    if (data.stats) applyStats(data.stats);
  } catch (err) {
    typingNode.remove();
    setStatus(false);
    addErrorMessage();
  }
}

function addUserMessage(text) {
  const div = document.createElement("div");
  div.className = "msg user";
  div.textContent = text;
  els.messages.appendChild(div);
  scrollToBottom();
}

function addTypingIndicator() {
  const div = document.createElement("div");
  div.className = "msg bot";
  div.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span>`;
  els.messages.appendChild(div);
  scrollToBottom();
  return div;
}

function addBotMessage(answer, score, category) {
  const div = document.createElement("div");
  div.className = "msg bot";
  const pct = Math.round(score * 100);
  div.innerHTML = `
    ${escapeHtml(answer)}
    <div class="msg-meta">
      <span class="match-pill">${pct}% match</span>
      <span>${escapeHtml(category)}</span>
    </div>
  `;
  els.messages.appendChild(div);
  scrollToBottom();
}

function addFallbackMessage(message, suggestions) {
  const div = document.createElement("div");
  div.className = "msg bot fallback";
  div.innerHTML = `
    ${escapeHtml(message)}
    <div class="suggest-row"></div>
  `;
  const row = div.querySelector(".suggest-row");
  suggestions.forEach(s => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "suggest-chip";
    btn.textContent = s.question;
    btn.addEventListener("click", () => askQuestion(s.question));
    row.appendChild(btn);
  });
  els.messages.appendChild(div);
  scrollToBottom();
}

function addErrorMessage() {
  const div = document.createElement("div");
  div.className = "msg bot fallback";
  div.textContent = "Couldn't reach the backend just now. Check that the FastAPI server is running and API_BASE in config.js points to it, then try again.";
  els.messages.appendChild(div);
  scrollToBottom();
}

function scrollToBottom() {
  els.messages.scrollTop = els.messages.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

init();
