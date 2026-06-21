# InsightOS Architecture

## MVP boundary

This repository is a runnable product skeleton for InsightOS. It includes application shells, local infrastructure, health checks, and test configuration.

It intentionally excludes real market data integrations, paid financial APIs, personalized investment advice, and trading functionality.

## Runtime services

- `frontend`: Next.js application served on port `3000`
- `backend`: FastAPI application served on port `8000`
- `postgres`: PostgreSQL database served on port `5432`
- `redis`: Redis cache/queue service served on port `6379`

## Data access

The backend owns database access through `app/db/session.py`. The initial health check verifies that the database connection can execute a simple query.

## API contract

Initial endpoint:

- `GET /health`: returns service status, app metadata, database connectivity, and Redis connectivity
