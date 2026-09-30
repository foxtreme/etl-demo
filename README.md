# GitHub ETL Pipeline

A production-oriented Python ETL pipeline that extracts repository data from the GitHub REST API, validates and
transforms it with Pydantic, and loads it into PostgreSQL.

The project demonstrates how a relatively small ETL workload can be designed with production concerns in mind:
reliability, testability, idempotency, transactions, observability, containerization, CI/CD, and deployment.

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
* **SQLAlchemy + PostgreSQL** — provides realistic relational persistence and transaction management.
* **Batch upserts** — reduces database round trips and makes repeated execution idempotent.
* **Explicit transactions** — failures roll back the current load instead of leaving partial data committed.
* **Retry policy** — transient network failures, HTTP 429, and 5xx responses are retried; permanent client errors are
  not.
* **Dependency isolation** — external API calls are mocked in tests while PostgreSQL integration tests use a real
  database.
* **Environment-based configuration** — credentials and deployment-specific settings stay outside the application code.
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
├── config.py               # Environment-based configuration
├── database.py             # SQLAlchemy engine/session setup
├── database_models.py      # PostgreSQL models
├── models.py               # Pydantic models
├── logging_config.py       # Application logging
├── main.py                 # ETL orchestration
│
├── tests/                  # Unit and integration tests
├── alembic/                # Database migrations
├── k8s/                    # Kubernetes manifests
├── .github/workflows/      # GitHub Actions CI
│
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## Technology Stack

| Area             | Technology              |
|------------------|-------------------------|
| Language         | Python 3.14             |
| API              | GitHub REST API         |
| Validation       | Pydantic                |
| Database         | PostgreSQL              |
| Database access  | SQLAlchemy + psycopg    |
| Migrations       | Alembic                 |
| Testing          | pytest                  |
| Containerization | Docker / Docker Compose |
| CI/CD            | GitHub Actions          |
| Orchestration    | Kubernetes              |
| Cloud            | Google Cloud Platform   |

## Running Locally

### Prerequisites

* Python 3.14+
* Docker Desktop
* GitHub personal access token
* PostgreSQL via Docker Compose

Create a `.env` file containing:

```env
GITHUB_TOKEN=your_github_token
DATABASE_URL=postgresql+psycopg://etl_user:etl_password@localhost:5432/github_etl
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the ETL:

```bash
python main.py
```

The default configuration extracts repositories from the `microsoft` organization. The organization can be changed
through `GITHUB_ORG`.

## Running Tests

The project uses both unit and PostgreSQL integration tests.

```bash
python -m pytest
```

The test suite covers transformation, extraction, retry behavior, batching, upserts, transaction rollback, and
integration with PostgreSQL.

Integration tests require a PostgreSQL instance configured through `DATABASE_URL`.

## Docker

Build and run the complete environment:

```bash
docker compose build
docker compose up
```

The ETL container is intentionally a short-lived batch workload: it starts, processes the data, loads PostgreSQL, and
exits.

## CI/CD

GitHub Actions runs automatically on pushes and pull requests.

The CI workflow:

1. Starts PostgreSQL.
2. Installs Python dependencies.
3. Runs Alembic migrations.
4. Executes the test suite.
5. Builds the Docker image.
6. Runs the containerized ETL against PostgreSQL.

This provides both application-level and container-level validation.

## Kubernetes

The ETL is also modeled as a Kubernetes **Job** rather than a long-running Deployment.

This matches the workload: the pipeline performs a bounded batch operation and terminates when the work is complete.

The Kubernetes configuration demonstrates:

* Job lifecycle
* ConfigMaps
* Secrets
* Persistent PostgreSQL storage
* Service networking
* Resource configuration

## Cloud Deployment

The project was also used to explore a managed GCP deployment model:

```text
GitHub
   │
   ▼
Artifact Registry
   │
   ▼
Cloud Run Job
   │
   ├── GitHub API
   │
   ▼
Cloud SQL PostgreSQL
   ▲
   │
Secret Manager + IAM
```

The application container remains unchanged; cloud-specific configuration is supplied by the deployment environment.

The GCP environment was created as a hands-on learning exercise using a trial account and is not intended to remain
permanently provisioned.

## Performance

Performance decisions were based on measurement rather than premature optimization.

For the database-only workload, batch upserts significantly reduced database overhead compared with individual inserts.
End-to-end execution is dominated primarily by external API/network latency for the current workload.

The project intentionally does not introduce additional infrastructure or processing frameworks until the workload
justifies them.

## Production Considerations

The current implementation is intentionally sized for a small portfolio workload.

For a substantially larger production dataset, potential next steps would include:

* incremental extraction
* checkpointing
* stronger rate-limit handling
* exponential backoff and jitter
* metrics and alerting
* workload partitioning
* larger-scale data processing
* immutable container image versions
* centralized secret and infrastructure management

These are deliberately treated as architectural trade-offs rather than technologies to add for their own sake.

## Project Goal

The goal is not simply to demonstrate:

```python
requests.get(...)
```

followed by:

```sql
INSERT INTO...
```

The project demonstrates the engineering decisions around that pipeline:

* How should transient API failures be handled?
* How do we validate external data?
* How do we prevent duplicate records?
* What happens when a database operation fails?
* How do we test external dependencies?
* How do we reproduce the environment?
* How does the same workload move from local development to containers, Kubernetes, and cloud infrastructure?

The result is a compact but realistic example of designing and operating a Python ETL workload.
