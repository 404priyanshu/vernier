# Vernier

AI-powered code review and vulnerability scanner for GitHub pull requests.

Vernier pulls a PR diff, runs heuristic static checks, batches the remaining hunks into LLM calls, and caches both the prompt identity and the model result in Redis. Each finding ships with a contextual fix and a test stub. Reviews live in PostgreSQL.

Stack: **Next.js**, **FastAPI**, **PostgreSQL**, **Redis**, OpenAI-compatible LLM API (SpaceXAI / xAI by default).

## Architecture

```
GitHub PR URL or unified diff
        │
        ▼
   FastAPI pipeline
        │
        ├─ parse hunks
        ├─ heuristic detectors (SQL injection, pickle, XSS, N+1, …)
        ├─ pack uncached hunks into batches
        ├─ Redis GET/SET keyed by sha256(prompt version + model + hunk)
        ├─ LLM JSON findings (skipped on cache hit)
        └─ merge + persist (Postgres)
        │
        ▼
   Next.js bench: findings, fixes, test stubs
```

## Quick start

```bash
cd vernier
cp .env.example .env
docker compose up -d postgres redis
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
cd frontend && npm install && cd ..

# terminal 1
cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend && npm run dev
```

If Docker is not available, run the API on SQLite. Redis is optional; without it the API keeps the cache in memory:

```bash
cd backend
DATABASE_URL=sqlite:///./vernier.db ../.venv/bin/uvicorn app.main:app --reload --port 8000
```

Open [http://localhost:3000](http://localhost:3000). The API seeds a sample review of `harbor-labs/checkout-api#1842` so the bench is not empty on first boot.

Set `FEATHERLESS_API_KEY` (or `XAI_API_KEY` / `OPENAI_API_KEY` + `LLM_BASE_URL`) to enable LLM-assisted analysis. Without a key, Vernier still completes reviews using heuristics and template fixes.

Optional: `GITHUB_TOKEN` raises the GitHub API rate limit and unlocks private repositories.

## Tests and CI

```bash
cd backend && pytest -q
```

GitHub Actions runs Ruff + Pytest for the API and `tsc` + lint + production build for the web app.

## HTTP API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Postgres, Redis, LLM status |
| GET | `/api/reviews` | List reviews |
| GET | `/api/reviews/stats` | Cache and corpus counters |
| GET | `/api/reviews/{id}` | Review plus findings |
| POST | `/api/reviews` | `{ "pr_url" }` or `{ "diff" }` |
| POST | `/api/webhooks/github` | `pull_request` opened / synchronize |

POST `/api/reviews` runs the pipeline in the request and returns the finished review.

## Deploy on Vercel

The repo is a Vercel Services project: Next.js at `/` and FastAPI at `/api`. Postgres is Neon. Redis is Upstash.

```bash
vercel link --yes --project vernier
vercel --prod
```

## Caching

Cache key: `vernier:llm:` + SHA-256 of `{ prompt_version, model, normalized hunk }`.

TTL defaults to seven days (`CACHE_TTL_SECONDS`). Repeating the same diff against the same prompt version does not call the model again.

## Webhooks

Point a GitHub webhook at `POST /api/webhooks/github` for `pull_request` events. Set `GITHUB_WEBHOOK_SECRET` to require `X-Hub-Signature-256`.
