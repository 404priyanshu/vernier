.PHONY: up down api web test install

up:
	docker compose up -d postgres redis

down:
	docker compose down

install:
	python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements-dev.txt
	cd frontend && npm install

api:
	cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && ../.venv/bin/pytest -q
