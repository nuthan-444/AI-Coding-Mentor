# 🧠 AI Coding Practice Mentor

An AI system that **remembers your past coding mistakes** and improves its feedback and test questions over time using Hindsight (Vectorize) memory.

---

## Architecture

```
Browser (HTML/CSS/JS)
        ↓
Node.js + Express  (Auth, Sessions, MongoDB)
        ↓
Python FastAPI     (AI Engine)
        ↓
  ┌─────────────────┐
  │  Groq LLM API   │  ← Code analysis, question generation, evaluation
  └─────────────────┘
  ┌─────────────────┐
  │ Hindsight Memory│  ← Stores & retrieves user mistake patterns
  └─────────────────┘
```

---

## Folder Structure

```
/project
├── frontend/
│   ├── index.html       ← Dashboard (code editor + feedback + weaknesses)
│   ├── login.html       ← Login page
│   ├── signup.html      ← Signup page
│   ├── practice.html    ← Practice test page
│   ├── style.css        ← Global styles
│   └── app.js           ← Shared JS utilities
│
├── backend-node/
│   ├── server.js        ← Express app entry point
│   ├── routes/
│   │   ├── auth.js      ← /signup, /login, /logout, /api/me
│   │   └── api.js       ← /analyze, /practice, /submit-test, /weaknesses
│   ├── models/
│   │   └── User.js      ← Mongoose User model
│   ├── package.json
│   └── .env.example
│
└── backend-python/
    ├── main.py          ← FastAPI AI engine
    ├── requirements.txt
    └── .env.example
```

---

## Setup Instructions

### Prerequisites

- Node.js v18+
- Python 3.10+
- MongoDB (local or Atlas)
- Groq API key → https://console.groq.com
- Hindsight/Vectorize API key → https://hindsight.ai (or your provider)

---

### Step 1 — Configure Environment Variables

**Node.js backend:**
```bash
cd backend-node
cp .env.example .env
# Edit .env:
# PORT=3000
# MONGO_URI=mongodb://localhost:27017/coding-mentor
# SESSION_SECRET=some-long-random-string
# PYTHON_URL=http://localhost:8000
```

**Python backend:**
```bash
cd backend-python
cp .env.example .env
# Edit .env:
# GROQ_API_KEY=gsk_xxxxxxxxxxxx
# HINDSIGHT_API_KEY=your-hindsight-key
# HINDSIGHT_URL=https://api.hindsight.com
```

---

### Step 2 — Install Dependencies

**Node.js:**
```bash
cd backend-node
npm install
```

**Python:**
```bash
cd backend-python
pip install -r requirements.txt
```

---

### Step 3 — Run All Three Servers

Open **3 terminals**:

**Terminal 1 — MongoDB** (if running locally):
```bash
mongod
```

**Terminal 2 — Python AI Engine:**
```bash
cd backend-python
python main.py
# Runs on http://localhost:8000
```

**Terminal 3 — Node.js Server:**
```bash
cd backend-node
npm start
# Runs on http://localhost:3000
```

---

### Step 4 — Open the App

Visit: **http://localhost:3000**

1. Create an account via the Signup page
2. Paste code in the editor on the Dashboard
3. Click **Analyze Code** → AI provides feedback and stores your mistake patterns
4. Go to **Practice** → AI generates questions targeting your weak spots
5. Submit answers → AI evaluates and updates your weakness score

---

## How the Memory System Works

| Action | Effect on Hindsight |
|--------|-------------------|
| Code analyzed with errors | Mistake stored with `score: 1` |
| Same mistake repeated | Score incremented |
| Practice question answered correctly | Score decremented |
| Score reaches 0 | Memory removed (weakness resolved!) |

The **weakness score** drives everything:
- Higher score = appears more in practice tests
- Correct answers progressively reduce the score
- The AI tailors its feedback based on your history

---

## API Reference

### Node.js Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /signup | — | Create account |
| POST | /login | — | Login |
| POST | /logout | — | Logout |
| GET | /api/me | — | Current session |
| POST | /analyze | ✅ | Analyze code |
| POST | /practice | ✅ | Get practice questions |
| POST | /submit-test | ✅ | Evaluate answer |
| GET | /weaknesses | ✅ | Get weakness list |

### Python Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /analyze | LLM code analysis + memory store |
| POST | /generate-test | Generate questions from weaknesses |
| POST | /evaluate-test | Evaluate answer + update scores |
| POST | /weaknesses | Retrieve user weaknesses |
| GET | /health | Check API + key config status |

---

## Groq Models Available

Change `GROQ_MODEL` in `main.py`:
- `qwen-qwq-32b` (default, excellent for code)
- `mixtral-8x7b-32768` (fast, good quality)
- `llama-3.3-70b-versatile` (powerful)
- `gemma2-9b-it` (lightweight)

---

## Notes for Hackathon Demo

- Without Hindsight keys, the system **still works** — memory calls are gracefully skipped
- Without Groq key, analysis endpoints will return a 500 with a clear message
- The frontend is fully served by Node.js — no separate static server needed