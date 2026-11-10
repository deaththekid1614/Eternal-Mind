# ETERNAL MIND — Stage 1 Handoff
**Project ID:** EM-001
**Date:** 10 November 2026
**Status:** COMPLETE
**Next Stage:** Stage 2 (Identity & Ingestion)

---

## 1. Local LLM Runtime (Ollama)
- Runtime: Ollama (v0.40.16)
- Model: qwen2.5:3b (1.9 GB)
- Model Settings: Temperature: 0.4, Context Length: 2048, Keep-Alive: 10m
- Storage: Models are saved to E:\IDE\Eternal-Mind\models\ollama via OLLAMA_MODELS env var.

## 2. Backend Architecture (FastAPI)
The backend is fully functional and serves text generation.
- Port: 127.0.0.1:8000
- Virtual Environment: backend\.venv
- Config: backend/app/config.py (Loads .env via pydantic-settings).
- Service: backend/app/intelligence/llm_service.py (Uses httpx async to talk to Ollama, timeout set to 300s for HDD cold starts).
- API Routes:
  - GET /api/health (Returns {"status": "ok"})
  - POST /api/chat (Accepts {"message": "..."}, returns {"response": "..."})
- CORS: Enabled for localhost:5173 and 127.0.0.1:5173.

## 3. Frontend Architecture (React + Vite)
- Port: 127.0.0.1:5173
- API Client: frontend/src/services/api.ts (Handles async fetch requests to the backend).
- UI: frontend/src/components/Chat/Chat.tsx (Displays scrolling chat history, loading state, and input field).
- Styling: Dark mode, inline CSS, clean minimal UI.

## 4. Benchmark Results
Hardware: Intel i7-8750H, GTX 1050 Ti (4GB), 16GB RAM.
- Short Prompt (7 tokens): 8.72 seconds total -> 32.96 tokens/sec.
- Long Prompt (305 tokens): 11.07 seconds total -> 28.54 tokens/sec.
- Observation: Generation speed is highly usable for real-time chat. First-token latency is acceptable but can be improved with context limit tuning.

## 5. How to Run the Project (Stage 1)
You need two terminal windows open at all times.

Terminal 1 (Backend):
Set-Location "E:\IDE\Eternal-Mind\backend"
& .venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000

Terminal 2 (Frontend):
Set-Location "E:\IDE\Eternal-Mind\frontend"
npm run dev

## 6. Next Steps (Stage 2 Gate)
Stage 2 is Identity Profile & Data Ingestion.
1. Create SQLite database schemas (conversations, messages, identity_facts).
2. Build an ingestion pipeline to parse and review personal data.
3. Add an identity editor UI to the frontend.
4. Ensure all imported data is quarantined and requires owner approval before being saved to the database.

Definition of Done for Stage 2: The system can store and retrieve the owner's identity profile fields securely, with explicit provenance and approval status.