# GitHub ETL Pipeline

A production-oriented Python ETL pipeline that extracts repository data from the GitHub REST API, validates and
transforms it with Pydantic, and loads it into PostgreSQL.

The project focuses on reliability, testability, idempotency, transaction management, observability, containerization,
CI/CD, and deployment across different environments.

## Architecture

```text
                         GitHub REST API
                               │
                               ▼
                        ┌─────────────┐
                        │   Extract   │
                        │ pagination  │
                        │ retries     │
                        └──────┬──────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  Transform  │
                        │  Pydantic   │
                        │  validation │
                        └──────┬──────┘
                               │
                               ▼
                        ┌─────────────┐
                        │    Load     │
                        │ batch upsert│
                        │ transactions│
                        └──────┬──────┘
                               │
                               ▼
                         PostgreSQL
```

The same containerized workload can run locally, as a Kubernetes Job, or in a managed cloud batch environment.

## Key Engineering Decisions

* **Separation of ETL stages** — extraction, transformation, and loading have independent responsibilities.
* **Pydantic validation** — converts untrusted API responses into a defined application model.
* **SQLAlchemy + PostgreSQL** — provides relational persistence and transaction management.
* **Batch upserts** — reduce database round trips and make repeated execution idempotent.
* **Explicit transactions** — failures roll back the current load instead of leaving partial data committed.
* **Retry policy** — transient network failures, HTTP 429, and 5xx responses are retried; permanent client errors are
  not.
* **Dependency isolation** — external API calls are mocked in tests while PostgreSQL integration tests use a real
  database.
* **Environment-based configuration** — credentials and deployment-specific settings stay outside application code.
* **Structured logging** — pipeline stages, progress, timings, retries, and failures are visible without relying on
  `print()`.
* **Containerized deployment** — Docker provides a consistent deployment artifact across environments.

## Project Structure

```text
etl-demo/
├── extract.py              # GitHub API extraction and pagination
├── transform.py            # API → validated domain model
├── load.py                 # Batch PostgreSQL upsert
├── github_client.py        # GitHub HTTP client
├── request_utils.py        # HTTP retry behavior
├── config.py               # Environment-based configur
```
