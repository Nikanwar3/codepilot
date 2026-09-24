<div align="center">

# CodePilot

**An autonomous AI software engineering agent.**
Connect a GitHub repository. Ask it to explain the architecture, hunt for bugs and
security vulnerabilities, generate a patch, run the tests in an isolated sandbox,
retry on failure, and hand back a verified result.

[![Backend CI](https://github.com/Nikanwar3/codepilot/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Nikanwar3/codepilot/actions/workflows/backend-ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-pgvector-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## What this is

CodePilot is not a chatbot bolted onto an LLM, and it's not a basic RAG demo. It's a
multi-agent system that treats a codebase the way a senior engineer would: read it,
understand it, form a hypothesis, make a change, verify the change actually works,
and only then report back.

```
Developer ──▶ Next.js ──▶ FastAPI ──▶ LangGraph Agent ──▶ Tools / RAG ──▶ LLM
                                            │
                                            ▼
                              Review & Verification (tests, lint, security scan)
                                            │
                                            ▼
                                    Verified Result
```

### Agent roster

| Agent | Responsibility |
|---|---|
| **Supervisor** | Routes the task, coordinates the other agents, owns the final answer |
| **Code Analysis** | Understands structure, dependencies, architecture |
| **Security** | Static analysis, dependency scanning, vulnerability findings |
| **Test / Debug** | Generates patches, runs tests in a Docker sandbox, retries on failure |
| **Review** | Final gate before a result is returned to the user |

### The autonomous debugging loop

```
understand task → retrieve relevant code → analyze → generate patch → apply patch
     → run tests in an isolated Docker sandbox
           ├─ pass → review patch → return verified result
           └─ fail → analyze failure → retry (max 3×) → escalate if still failing
```

### RAG pipeline

```
GitHub repo → clone → AST/Tree-sitter parsing → intelligent chunking
     → embeddings → Postgres + pgvector → retrieval → metadata filtering
     → reranking → LLM
```

## Why these choices

- **LangGraph over a single prompt loop** — the debugging flow is a graph with
  branches (tests pass/fail) and bounded retries, not a linear chain. A supervisor
  routing to specialist agents keeps each agent's context small and its job narrow.
- **pgvector over a dedicated vector DB** — code chunks, metadata, and embeddings
  live in the same transactional store as everything else (users, tasks, findings),
  so retrieval can join against relational metadata (file path, language, repo,
  commit) instead of round-tripping between two databases.
- **Docker sandboxing for generated code** — an LLM-authored patch is untrusted
  input. It never runs on the app server: isolated container, CPU/memory limits,
  timeout, no network, non-root.
- **Celery + Redis for anything slow** — repo indexing, embedding generation,
  security scans, and full agent runs are all long-running and belong off the
  request/response cycle.

## Tech stack

**Backend** — Python, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL + pgvector, Redis,
Celery, LangGraph, OpenAI/Azure OpenAI, Tree-sitter
**Frontend** — Next.js, TypeScript, Tailwind, SSE for live agent progress
**Platform** — Docker, AWS (S3 / RDS / ECS), GitHub Actions, Prometheus + Grafana
**Security** — JWT + RBAC, rate limiting, sandboxed execution
**Testing** — pytest (unit / integration / e2e), agent evaluation tests

## Build status

This is being built incrementally and in the open — each step is a real commit with
its own tests, not a single generated dump.

- [x] **Step 1 — Backend foundation.** FastAPI skeleton, typed config
      (pydantic-settings), structured logging (structlog), async Postgres + Redis
      connectivity, Alembic wiring, Docker Compose, liveness/readiness probes, CI.
- [x] **Step 2 — Database schema.** 10 SQLAlchemy 2.0 models (`users`,
      `repositories`, `files`, `code_chunks` with a pgvector `Vector(1536)`
      column + HNSW index, `tasks`, `agent_runs`, `tool_calls`, `findings`,
      `patches`, `test_runs`), native Postgres enums, FK cascades, and the
      first Alembic migration — schema-validated against a real local Postgres.
- [ ] Step 3 — Repository ingestion: clone, Tree-sitter parsing, chunking.
- [ ] Step 4 — RAG: embeddings, pgvector retrieval, reranking.
- [ ] Step 5 — LangGraph agent graph + tool calling (`read_file`, `search_code`,
      `list_files`, `run_tests`, `run_linter`, `git_diff`, `apply_patch`,
      `dependency_scan`).
- [ ] Step 6 — Autonomous debugging loop + Docker sandbox execution.
- [ ] Step 7 — Celery + Redis async job pipeline.
- [ ] Step 8 — Auth: JWT + RBAC + rate limiting.
- [ ] Step 9 — Frontend (Next.js) + SSE live agent progress.
- [ ] Step 10 — Observability: Prometheus + Grafana.
- [ ] Step 11 — Testing: unit / integration / e2e / agent evaluation.
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

- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/api/v1/health/live
- Readiness (checks DB + Redis): http://localhost:8000/api/v1/health/ready

## Testing

```bash
cd backend
ruff check .        # lint
mypy app             # types
pytest -v --cov=app  # tests + coverage
```

## License

MIT — see [LICENSE](LICENSE).
