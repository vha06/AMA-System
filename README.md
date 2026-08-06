# 🚀 AMA-System (Automated Market Analysis System)

**Automated Market Analysis System** - A personal research project building a **Zero-Cost Research Stack** architecture. 
The system takes a user Prompt as input, automatically collects data (Scraping), processes it into a Knowledge Graph (GraphRAG), and finally outputs a strategic analysis report via a **Generative UI**.

---

## ✨ Core Features (Completed)

- **🧠 Multi-Agent Architecture (CrewAI):** Integrates an intelligent multi-agent orchestration framework. Instead of running statically, agents communicate autonomously, breaking down tasks for market analysis, web scraping, and reporting.
- **⚡ Generative UI Dashboard:** Modern Next.js interface, displaying real-time analysis results (Server-Sent Events) including 5 strategic information blocks:
  1. Potential market niche suggestions.
  2. Optimal price range for products.
  3. Risk assessment and bottlenecks.
  4. AI Prompts for product image generation (Midjourney/DALL-E).
  5. SEO-standard keyword set.
- **🕸️ Knowledge Graph (LlamaIndex):** Upgrades GraphRAG with Property Graph, combining the flexible representation power of graphs with LlamaIndex's retrieval speed.
- **🕵️ Stealth Scraping (Playwright Stealth):** Powerful data collection, bypassing Anti-bot barriers from major e-commerce sites.
- **🔐 Session Management & Authentication (Supabase):** Tracks analysis history and real-time user authentication (Database + Auth).
- **🛡️ Safe Fallback / Mock Mode:** The system automatically switches to mock data mode if no API Key is provided, allowing a 100% smooth experience.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Python / FastAPI
- **LLM Engine:** Gemini 3.5 Flash (Fast, $0 cost)
- **Orchestration:** CrewAI (Multi-Agent Framework)
- **Knowledge Base:** LlamaIndex Property Graph + ChromaDB
- **Scraping:** Playwright + Stealth Plugin
- **Package Manager:** `uv` (Fast & Modern)

### Database & Auth
- **Primary DB / Auth:** Supabase (PostgreSQL, RLS)
- **Caching:** Redis (Upstash)

### Frontend
- **Framework:** Next.js 15+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Data Flow:** Server-Sent Events (SSE) with Custom JSON Stream Parser

---

## ⚙️ Demo Setup Guide

### 1. Environment Preparation
The project is designed to run smoothly even without an API account (Fallback Mode).
However, to run full AI and Database features, you need to copy the `.env.example` file to `.env` in the `backend/` directory and fill in the Keys:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-3.5-flash

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 2. Start Backend (Port 8000)
Open a Terminal window (PowerShell or CMD) and run:
```bash
cd backend
uv run playwright install chromium
uv run uvicorn main:app --reload --port 8000
```
- API Docs (Swagger): `http://localhost:8000/docs`

### 3. Start Frontend (Port 3000)
Open a second Terminal window and run:
```bash
cd frontend
npm install
npm run dev
```
- User Interface: `http://localhost:3000`

---

## 📚 Architecture Decision Records (ADRs) & API Docs
To deeply understand the reasons for choosing these technologies (Gemini 3.5, Supabase, CrewAI, LlamaIndex), please see:
- [Architecture Decision Records (ADR)](docs/decisions/)
- [System API Documentation](docs/api.md)
- [Zero-Cost Deployment Guide](docs/deployment_guide.md)

*(Detailed overview of task progress is located in the `docs/task.md` file)*
