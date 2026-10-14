# 🌐 Smart IoT Device Troubleshooting Chatbot

**IBM College Mini Project** — An intelligent conversational chatbot that helps users identify and resolve common smart home device problems using natural language.

---

## 📋 Table of Contents

- [Project Objective](#-project-objective)
- [Architecture](#-architecture)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Demo Mode](#-demo-mode)
- [Running Tests](#-running-tests)
- [Common Errors](#-common-errors)

---

## 🎯 Project Objective

Develop an intelligent conversational chatbot that:
- Understands natural language descriptions of IoT device problems
- Classifies issues into categories (connectivity, setup, firmware, configuration)
- Guides users through step-by-step troubleshooting
- Retrieves answers from a curated knowledge base
- Maintains session state across a conversation
- Works fully offline in Demo Mode (no paid APIs required)

**Supported devices:** Smart Bulbs, Smart Plugs, Smart Speakers, Smart Cameras, and other Wi-Fi smart home devices.

---

## 🏗 Architecture

```
frontend/          React + Vite + Tailwind CSS
    └── src/
        ├── App.jsx              Main application
        ├── api.js               Axios API client
        └── components/
            ├── Header.jsx       Status bar + branding
            ├── WelcomePanel.jsx Device selector + suggested questions
            ├── ChatWindow.jsx   Message bubbles, summary, sources
            └── MessageInput.jsx Text input + send + restart

backend/           Python + FastAPI
    ├── main.py                  FastAPI app + CORS
    ├── routes.py                API route handlers
    ├── schemas.py               Pydantic request/response models
    ├── troubleshooting_engine.py Rule-based conversation logic
    ├── retrieval.py             Keyword TF-IDF retrieval + optional ChromaDB
    ├── session_manager.py       In-memory session store
    ├── llm_config.py            IBM watsonx.ai integration (optional)
    └── knowledge_base/          Troubleshooting guide documents (.txt)
```

---

## ✨ Features

- **Stateful troubleshooting conversation** — tracks symptoms, steps, and resolution
- **Device categorisation** — Smart Bulb, Plug, Speaker, Camera, Other
- **Issue classification** — Connectivity, Setup, Configuration, Firmware
- **Step-by-step guidance** — one clear step at a time with progress indicator
- **"It worked" / "Still not working"** action buttons
- **Diagnosis summary** — device, category, symptoms, steps, outcome
- **Knowledge base sources** — real document references (not fabricated)
- **RAG-ready** — ChromaDB + LangChain integration when available
- **IBM watsonx.ai** integration (optional, with graceful fallback)
- **Demo Mode** — fully functional without any paid API
- **Responsive UI** — works on mobile and desktop
- **Keyboard accessible** — Enter to send, full focus management

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, Tailwind CSS 3 |
| Backend | Python 3.10+, FastAPI 0.111, Uvicorn |
| Validation | Pydantic v2 |
| Retrieval | Keyword TF-IDF (built-in), optional ChromaDB |
| LLM | IBM watsonx.ai Granite (optional) |
| HTTP Client | Axios |
| Testing | pytest, FastAPI TestClient |

---

## 📦 Prerequisites

- **Python 3.10 or later** — [python.org](https://www.python.org/downloads/)
- **Node.js 18 or later** — [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node.js)

Verify installations in PowerShell:
```powershell
python --version
node --version
npm --version
```

---

## 📁 Project Structure

```
ibm portfolio/
├── backend/
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── troubleshooting_engine.py
│   ├── retrieval.py
│   ├── session_manager.py
│   ├── llm_config.py
│   ├── tests.py
│   ├── requirements.txt
│   ├── .env.example
│   └── knowledge_base/
│       ├── smart_bulb_guide.txt
│       ├── smart_plug_guide.txt
│       ├── smart_speaker_guide.txt
│       ├── smart_camera_guide.txt
│       ├── wifi_connectivity_guide.txt
│       ├── device_pairing_guide.txt
│       └── firmware_update_guide.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       └── components/
│           ├── Header.jsx
│           ├── WelcomePanel.jsx
│           ├── ChatWindow.jsx
│           └── MessageInput.jsx
├── README.md
└── gitignore.txt
```

---

## ⚙ Installation

### 1. Backend Setup (PowerShell)

```powershell
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

> **Note:** If you get an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Frontend Setup (PowerShell)

Open a **new PowerShell window** and run:

```powershell
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

---

## 🔑 Environment Variables

The backend works in **Demo Mode** without any environment variables. To enable IBM watsonx.ai:

```powershell
# In the backend/ directory, copy the example file
Copy-Item .env.example .env

# Edit .env and add your credentials
notepad .env
```

**.env variables:**
```
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

Leave these empty or omit the file entirely to run in Demo Mode.

---

## 🚀 Running the Application

### Start the Backend

```powershell
# In the backend/ directory with .venv activated
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
Interactive API docs: http://localhost:8000/docs

### Start the Frontend

In a **separate PowerShell window**:

```powershell
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

Open http://localhost:5173 in your browser to use the application.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Backend status and operating mode |
| GET | `/devices` | List of supported device categories |
| POST | `/chat` | Send a message and receive troubleshooting response |
| POST | `/feedback` | Record whether a troubleshooting step worked |
| GET | `/docs` | Swagger interactive API documentation |

### POST /chat — Request Body
```json
{
  "message": "My smart bulb is offline",
  "session_id": "unique-session-uuid",
  "device_type": "smart_bulb"
}
```

### POST /chat — Response Body
```json
{
  "reply": "...",
  "session_id": "...",
  "issue_category": "connectivity",
  "current_step": 1,
  "total_steps": 6,
  "resolution_status": "in_progress",
  "sources": [{"title": "Smart Bulb Troubleshooting Guide", "document": "smart_bulb_guide", "relevance": 1.0}],
  "is_general_guidance": false,
  "summary": null
}
```

---

## 🎭 Demo Mode

The application runs in **Demo Mode** by default — no IBM Cloud account or API key required.

In Demo Mode:
- The **rule-based troubleshooting engine** handles all conversations
- **Keyword TF-IDF retrieval** fetches relevant knowledge base documents
- All features including session management, summaries, and source references work normally
- The status bar shows **"Demo Mode"**

To verify Demo Mode is active:
```powershell
curl http://localhost:8000/health
# Returns: {"status":"ok","mode":"rule_based","rag_available":false,"llm_available":false,...}
```

---

## 🧪 Running Tests

```powershell
# In the backend/ directory with .venv activated
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests.py -v
```

Tests cover:
- Issue classification (connectivity, setup, firmware, configuration)
- Device detection from natural language
- Conversation flow and step progression
- Resolution detection
- Session restart
- Knowledge base retrieval
- All API endpoints
- End-to-end acceptance scenario

---

## ❗ Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual env not active | Run `.\.venv\Scripts\Activate.ps1` |
| `CORS error in browser` | Backend not running | Start `uvicorn main:app --reload --port 8000` |
| `Cannot reach the backend` | Wrong port | Ensure backend runs on port 8000 |
| `npm: command not found` | Node not installed | Install Node.js from nodejs.org |
| `ExecutionPolicy` error | PowerShell restriction | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `chromadb not found` | Optional dependency | Only needed for RAG; app works without it |

---

## 📚 Knowledge Base Documents

| File | Content |
|------|---------|
| `smart_bulb_guide.txt` | Offline, pairing, firmware for smart bulbs |
| `smart_plug_guide.txt` | Offline, setup, configuration for smart plugs |
| `smart_speaker_guide.txt` | Offline, setup, audio for smart speakers |
| `smart_camera_guide.txt` | Offline, pairing, firmware for cameras |
| `wifi_connectivity_guide.txt` | Wi-Fi bands, router settings, interference |
| `device_pairing_guide.txt` | Universal pairing guide for all IoT devices |
| `firmware_update_guide.txt` | Safe firmware update procedures |

---

## 🔒 Safety Notes

- This chatbot never requests or stores Wi-Fi passwords or personal credentials
- It never recommends opening electrical devices or touching live wiring
- It always recommends switching off and unplugging before physical inspection
- Electrical hazards are always referred to qualified professionals

---

*IBM Mini Project — Smart IoT Device Troubleshooting Chatbot*
