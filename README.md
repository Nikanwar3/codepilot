# CodePilot

Production-grade AI Software Engineering Agent Platform. A developer connects
a GitHub repository and asks an agent to understand the codebase, explain
architecture, find bugs/security issues, generate patches, run tests in an
isolated sandbox, and return a verified result.

Being built incrementally. See progress below.

## Build steps

- [x] **Step 1 — Backend foundation**: FastAPI skeleton, typed config,
      structured logging, async Postgres + Redis plumbing, Docker Compose
      (Postgres/pgvector + Redis), Alembic wiring, first test.
- [ ] Step 2 — Database schema (users, repositories, files, code_chunks,
      tasks, agent_runs, tool_calls, findings, patches, test_runs) + Alembic
      migration.
- [ ] Step 3 — Repository ingestion (clone, Tree-sitter parsing, chunking).
- [ ] Step 4 — RAG (embeddings, pgvector retrieval, reranking).
- [ ] Step 5 — LangGraph agent (Supervisor + Code Analysis + Security +
      Test/Debug + Review agents) and tool calling.
- [ ] Step 6 — Autonomous debugging loop + Docker sandbox execution.
- [ ] Step 7 — Celery + Redis async job pipeline.
- [ ] Step 8 — Auth (JWT + RBAC) + rate limiting.
- [ ] Step 9 — Frontend (Next.js) + SSE live agent progress.
- [ ] Step 10 — Observability (Prometheus/Grafana).
- [ ] Step 11 — Testing (unit/integration/e2e/agent eval).
- [ ] Step 12 — CI/CD + AWS deployment.

## Local development

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

# Start Postgres + Redis only, run the API on the host:
docker compose up -d postgres redis
uvicorn app.main:app --reload

# Or run everything in containers:
docker compose up --build
```

API docs: http://localhost:8000/docs
Liveness: http://localhost:8000/api/v1/health/live
Readiness (checks DB + Redis): http://localhost:8000/api/v1/health/ready

## Testing

```bash
cd backend
pytest -v
```
