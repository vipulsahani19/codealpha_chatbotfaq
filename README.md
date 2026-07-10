<div align="center">

# 🤖 CircuitBot

### B.Tech AI & Programming FAQ Assistant

*A full-stack AI chatbot that answers 87 curated questions on AI, Machine Learning, Deep Learning, NLP, programming languages, DSA, databases, web development, and careers — using real machine learning (TF-IDF + cosine similarity), not hardcoded rules.*

[![Live Frontend](https://img.shields.io/badge/Frontend-Live-brightgreen?style=for-the-badge&logo=vercel)](https://codealpha-chatbotfaq.vercel.app/)
[![Live Backend](https://img.shields.io/badge/Backend-Live-success?style=for-the-badge&logo=fastapi)](https://codealpha-chatbotfaq.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**[🌐 Live Demo](https://codealpha-chatbotfaq.vercel.app/)** · **[📘 API Docs](https://codealpha-chatbotfaq.onrender.com/docs)** · **[🐛 Report a Bug](../../issues)**

</div>

---

## 📸 Overview

CircuitBot is a 3-tier full-stack AI project built for a B.Tech curriculum: a static frontend, a FastAPI REST backend, and a SQLite persistence layer — tied together by a real, explainable machine learning matching engine.

| | |
|---|---|
| 🔗 **Frontend (Vercel)** | [codealpha-chatbotfaq.vercel.app](https://codealpha-chatbotfaq.vercel.app/) |
| 🔗 **Backend (Render)** | [codealpha-chatbotfaq.onrender.com](https://codealpha-chatbotfaq.onrender.com/) |
| 📘 **Interactive API Docs** | [codealpha-chatbotfaq.onrender.com/docs](https://codealpha-chatbotfaq.onrender.com/docs) |

> ⚠️ The backend runs on Render's free tier, which spins down after 15 minutes of inactivity. The **first** request after a period of inactivity may take 30–60 seconds while it wakes up — this is expected, not a bug.

---

## ✨ Features

- 💬 **Real-time chat UI** with a typing indicator, match-confidence badges, and smart fallback suggestions when nothing matches confidently
- 🧠 **Genuine ML matching** — TF-IDF vectorization (unigrams + bigrams) and cosine similarity, not keyword/regex rules
- 📊 **Live stats panel** — total questions asked, FAQ count, running average match confidence, and short-term "memory" of recent questions
- 🗂️ **87 curated FAQs** across 10 categories: B.Tech basics, AI, ML, Deep Learning, NLP, Programming Languages, DSA, Databases, Web Development, Careers & Exams
- 🟢 **Live backend status indicator** so you always know if the API is reachable
- 🗄️ **Persistent SQLite storage** for the FAQ knowledge base and every chat interaction
- 🚀 **Zero-cost, zero-dependency deploy** — no GPU, no model downloads, no API keys required

---

## 🏗️ Architecture

```
┌─────────────────────┐        HTTPS / JSON         ┌──────────────────────┐
│       Frontend        │ ───────────────────────────▶ │       Backend          │
│   HTML · CSS · JS     │ ◀─────────────────────────── │  FastAPI · SQLite      │
│   hosted on Vercel    │                              │  scikit-learn TF-IDF   │
└─────────────────────┘                              └──────────────────────┘
```

**Why TF-IDF instead of a transformer/embedding model?** An earlier version used a pretrained transformer (`all-MiniLM-L6-v2`) for richer semantic matching. It worked, but reliably exceeded the 512MB RAM ceiling on free-tier hosting — first from PyTorch/CUDA bloat, then from the ONNX Runtime thread pool over-allocating memory in a small container. TF-IDF needs no model download and only a few MB of RAM, so it deploys reliably anywhere while still being a real, fully explainable ML technique: the same vector-space model classical search engines are built on.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Backend | FastAPI (Python) |
| AI / ML | scikit-learn `TfidfVectorizer` + cosine similarity |
| Database | SQLite |
| Hosting | Vercel (frontend) · Render (backend) |

---

## 📁 Project Structure

```
circuitbot-fullstack/
├── backend/
│   ├── main.py            # FastAPI app + all API routes
│   ├── ai_engine.py        # TF-IDF vectorization + cosine similarity
│   ├── database.py         # SQLite schema, queries, stats
│   ├── seed_data.py        # the 87 FAQ entries
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── config.js           # API_BASE — points to the Render backend
│   └── app.js
├── render.yaml              # one-click backend deploy config for Render
└── README.md
```

---

## 🔌 API Reference

Base URL: `https://codealpha-chatbotfaq.onrender.com`

| Method | Route             | Description                                                  |
|--------|-------------------|----------------------------------------------------------------|
| GET    | `/api/health`     | Liveness check                                                  |
| GET    | `/api/faqs`       | All FAQs (id, category, question, answer)                       |
| GET    | `/api/categories` | One sample question per category, used for the topic chips      |
| POST   | `/api/ask`        | `{ "question": "..." }` → matched answer or fallback + live stats |
| GET    | `/api/stats`      | Total asked, FAQ count, average match score, recent memory      |

**Example: `POST /api/ask`**
```json
// Request
{ "question": "what is overfitting" }

// Response
{
  "matched": true,
  "answer": "Overfitting happens when a model learns the training data too closely...",
  "category": "Machine Learning",
  "score": 0.58,
  "stats": { "asked": 4, "faqs_count": 87, "avg_score": 0.43, "memory": [...], "memory_limit": 3 }
}
```

Try it live in the interactive docs: **[/docs](https://codealpha-chatbotfaq.onrender.com/docs)**

---

## 🖥️ Running Locally

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
No model download needed — the TF-IDF vectorizer fits directly on the FAQ corpus at startup. A SQLite database is created automatically at `backend/data/app.db`.

### Frontend
```bash
cd frontend
python3 -m http.server 5500
# open http://localhost:5500
```
`frontend/config.js` points to `http://localhost:8000` by default for local development.

---

## ☁️ Deployment

### Backend → Render
1. Push this repo to GitHub.
2. On [render.com](https://render.com): **New → Web Service** → connect this repo.
3. Render auto-detects `render.yaml` (root directory `backend`, free instance).
4. Deploy. No PyTorch/CUDA/model download, so the build is small and fast.

### Frontend → Vercel
1. On [vercel.com/new](https://vercel.com/new): import the same repo.
2. **Root Directory:** `frontend`. **Framework Preset:** Other.
3. Set `frontend/config.js` → `API_BASE` to your live Render URL before deploying.
4. Deploy.

### Connect them
On Render → your service → **Environment**, set `ALLOWED_ORIGIN` to your exact Vercel URL so CORS only allows your deployed site.

---

## ➕ Adding More FAQs

Add an entry to `FAQS` in `backend/seed_data.py`:
```python
{"id": 88, "category": "Your Category", "question": "Your question?", "answer": "Your answer."}
```
Delete `backend/data/app.db` and restart the server to re-seed. The TF-IDF vectorizer refits automatically — no other code changes needed.

---

## 🎓 Project Notes (Viva / Report)

- **Architecture**: 3-tier — static frontend, FastAPI REST backend, SQLite persistence.
- **AI component**: TF-IDF (Term Frequency–Inverse Document Frequency) vectorization with unigrams and bigrams, plus cosine similarity — IDF automatically downweights common words ("what", "is"), and cosine similarity is insensitive to sentence length.
- **Data layer**: SQLite stores both the FAQ knowledge base and every chat interaction (question, matched FAQ, confidence score, timestamp), powering the live stats panel.
- **Engineering trade-off**: chose a lightweight classical ML technique over a transformer/embedding model specifically for deployment reliability on free-tier infrastructure — a deliberate, explainable decision, not a limitation overlooked.

---

## 🚧 Future Improvements

- [ ] Add a root `/` route on the backend with a friendly welcome message
- [ ] Admin panel for adding/editing FAQs without touching code
- [ ] Persist stats across Render free-tier spin-downs using an external database
- [ ] Optional LLM fallback for genuinely out-of-scope questions

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Built as a B.Tech mini-project — a from-scratch, fully explainable ML-powered FAQ assistant.

</div>
