# GitHub ETL Pipeline

## Project Overview

This project is a production-oriented ETL pipeline that extracts repository data from the GitHub REST API, validates and transforms the data using Python and Pydantic, and loads it into PostgreSQL using SQLAlchemy. The project is intentionally being developed incrementally to demonstrate the engineering practices expected from a Senior Python ETL / Backend Developer: clean separation of responsibilities, data validation, efficient database operations, transaction management, automated testing, API integration, observability, containerization, CI/CD, and cloud-native deployment. Rather than building a simple script that "moves data from A to B", the goal is to demonstrate how a senior engineer approaches an ETL system by considering correctness, performance, maintainability, failure modes, testability, scalability, and operational concerns from the beginning.

---

# Project Goals

The pipeline uses public GitHub repository data as a realistic external data source.

The long-term architecture is:

```text
                         ┌──────────────────┐
                         │    GitHub API    │
                         │   REST / JSON     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Extract      │
                         │   HTTP Client    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Transform     │
                         │ Pydantic Models  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       Load       │
                         │    SQLAlchemy    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   PostgreSQL     │
                         └──────────────────┘
```

The project will progressively evolve from a local ETL application into a containerized, tested, observable and cloud-ready pipeline.

---

# What This Project Demonstrates

The project is designed to showcase the following engineering concepts:

- Python 3.x application architecture
- ETL pipeline design
- REST API integration
- External API failure handling
- Pydantic data validation
- SQLAlchemy ORM and Core APIs
- PostgreSQL
- Efficient batch database operations
- Upsert / idempotent loading
- Transaction management
- Unit testing with pytest
- Integration testing
- Test fixtures and factory fixtures
- Mocking external dependencies
- Dependency injection
- Configuration management
- Structured logging and observability
- Error handling and retry strategies
- Docker containerization
- CI/CD
- GitHub Actions
- Kubernetes
- Cloud-native architecture
- AWS/cloud deployment concepts
- Performance measurement and optimization
- Production-oriented application design
- AI-assisted development while maintaining engineering ownership

---

# Project Roadmap

The project is being developed through the following stages:

```text
1. Project foundation
        ↓
2. Database architecture
        ↓
3. ETL extraction
        ↓
4. Data transformation & validation
        ↓
5. Efficient database loading
        ↓
6. Testing strategy
        ↓
7. API mocking & extraction testing
        ↓
8. Error handling & resilience
        ↓
9. Configuration management
        ↓
10. Logging & observability
        ↓
11. Performance optimization
        ↓
12. Dockerization
        ↓
13. CI/CD with GitHub Actions
        ↓
14. Kubernetes
        ↓
15. Cloud deployment
        ↓
16. Production-oriented improvements
```

Each stage introduces a new engineering concern while building on the previous stages.

---

# 1. Project Foundation

## Objective

Establish a clean Python project structure before implementing the complete pipeline.

The application separates the major ETL responsibilities:

```text
extract.py
transform.py
load.py
main.py
```

Additional modules handle:

```text
database.py
database_models.py
models.py
```

Tests are kept separately:

```text
tests/
```

## Design Decision

The pipeline is intentionally divided into separate stages rather than implementing everything in a single script.

Instead of:

```python
response = requests.get(...)
data = response.json()

# transform data

# connect to database

# insert data
```

the application uses:

```text
Extract → Transform → Load
```

## Why?

Separation of responsibilities makes each stage:

- easier to test
- easier to modify
- easier to reason about
- independently reusable
- less coupled to the other stages

This is particularly important for ETL systems because extraction, transformation and loading frequently evolve independently.

### Senior Engineering Perspective

A senior engineer does not optimize only for getting the first version working.

They consider:

> "What happens when this component changes six months from now?"

Separating the ETL stages reduces the blast radius of future changes.

---

# 2. PostgreSQL Database

## Objective

Use PostgreSQL as the persistent destination for repository data.

The application connects using SQLAlchemy:

```text
Python
   ↓
SQLAlchemy
   ↓
psycopg
   ↓
PostgreSQL
```

PostgreSQL runs inside Docker during local development.

## Design Decision

PostgreSQL was chosen instead of an embedded database because it provides a realistic production-oriented relational database environment.

The project therefore exercises concepts such as:

- relational schema design
- primary keys
- unique constraints
- transactions
- indexes
- upserts
- batch operations
- database connections

### Senior Engineering Perspective

Choosing a realistic database makes the project more representative of production systems.

The goal is not simply to demonstrate that Python can write records somewhere.

The goal is to demonstrate understanding of how an ETL application interacts with a production-grade relational database.

---

# 3. Database Models

The database representation is separated from the Pydantic representation.

The project currently has two models:

```text
models.py
    ↓
Pydantic Repository

database_models.py
    ↓
SQLAlchemy RepositoryDB
```

## Why two models?

The external/API-facing representation and the database representation serve different purposes.

Pydantic models are responsible for:

- data validation
- Python application representation
- defining expected input/output structure

SQLAlchemy models are responsible for:

- database mapping
- database column types
- constraints
- persistence

### Senior Engineering Perspective

Keeping these concerns separate prevents the database schema from becoming the application's data contract.

A change to the database representation should not necessarily require changing the API/data-validation model.

---

# 4. Database Migrations with Alembic

## Objective

Manage database schema changes through migrations rather than manually modifying the database.

Alembic is used to create and evolve the PostgreSQL schema.

## Design Decision

The database schema should be reproducible.

Instead of relying on:

> "My local database happens to look like this."

we want:

> "The schema can be recreated and evolved from version-controlled migration files."

### Senior Engineering Perspective

Schema changes are part of application deployment.

Treating database structure as version-controlled code makes environments reproducible and reduces deployment risk.

---

# 5. Data Extraction

## Objective

Extract repository information from the GitHub REST API.

The extractor will eventually be responsible for concerns such as:

- HTTP requests
- pagination
- authentication
- rate limiting
- API errors
- timeouts
- retries
- response validation

The extractor should return raw API data rather than immediately coupling the API layer to PostgreSQL.

## Design Decision

Extraction is kept separate from transformation and loading.

```text
GitHub API
    ↓
extract.py
    ↓
raw repository data
```

This makes the extraction layer independently testable.

### Senior Engineering Perspective

External systems should be treated as unreliable dependencies.

The database loader should not need to know whether its data came from GitHub, another API, a CSV file, or a message queue.

That separation makes the pipeline easier to evolve.

---

# 6. Data Transformation and Validation

The transformation layer converts GitHub's API representation into the application's internal model.

For example, GitHub provides:

```text
stargazers_count
forks_count
open_issues_count
```

while the application model uses:

```text
stars
forks
open_issues
```

The transformation layer performs this mapping.

Pydantic is used to validate the resulting structure.

```text
GitHub JSON
    ↓
transform_repository()
    ↓
Pydantic Repository
```

## Design Decision

Pydantic provides a clear contract between extraction and loading.

The loader therefore doesn't have to defensively handle arbitrary dictionaries.

It receives a validated domain object.

### Senior Engineering Perspective

Strong boundaries between pipeline stages reduce the number of assumptions each component needs to make.

The loader can effectively say:

> "If I received a `Repository`, I know its structure."

This reduces runtime surprises and makes failures occur closer to their source.

---

# 7. Efficient Database Loading

## Objective

Load repositories efficiently into PostgreSQL.

The loader uses PostgreSQL's `INSERT ... ON CONFLICT DO UPDATE` behavior.

This provides an **upsert** operation:

```text
Repository doesn't exist
        ↓
      INSERT

Repository already exists
        ↓
      UPDATE
```

## Idempotency

The loader is designed so that processing the same repository more than once does not create duplicate rows.

This is an important ETL property:

> Running the pipeline repeatedly should converge on the same database state.

## Batch Processing

The loader accepts a configurable batch size:

```python
load_repositories(
    session,
    repositories,
    batch_size=500,
)
```

Rather than executing one database operation per repository, repositories are grouped into batches.

### Why?

Each database execution has overhead.

Conceptually:

```text
100 repositories

Individual:
DB → DB → DB → DB → ... → DB

Batch:
DB → DB
```

The isolated benchmark demonstrated the effect:

```text
Individual inserts: ~0.289 s
Batch inserts:      ~0.046 s
```

The batch approach was approximately 6× faster for the database-only workload.

The end-to-end pipeline was slower because GitHub API/network latency dominated the total execution time.

### Senior Engineering Perspective

Optimization should be based on measurement rather than intuition.

The project therefore distinguishes between:

```text
database performance
```

and:

```text
end-to-end pipeline performance
```

This prevents optimizing the wrong bottleneck.

---

# 8. Transaction Management

The pipeline explicitly manages database transactions.

The orchestration layer follows the pattern:

```text
BEGIN
   ↓
Load data
   ↓
Everything succeeds?
   │
   ├── YES → COMMIT
   │
   └── NO  → ROLLBACK
```

The project includes an integration test verifying that a simulated failure before commit does not leave partial data persisted.

## Why?

ETL pipelines frequently process many records.

A failure halfway through processing can otherwise leave the database in an inconsistent state.

### Senior Engineering Perspective

A senior engineer considers failure paths as part of the normal application design.

Success is only one possible outcome.

The system must also define what happens when:

- an API fails
- validation fails
- the database fails
- a batch fails
- the process crashes

---

# 9. Automated Testing

The project uses pytest.

The test suite currently contains:

```text
10 tests
```

covering:

### Transformation unit tests

```text
valid transformation
missing optional language
missing required field
```

### Loading unit tests

```text
SQL execution
multiple batches
invalid batch size
```

### PostgreSQL integration tests

```text
insert
upsert/update
multiple batches
rollback
```

## Testing Philosophy

The project deliberately uses multiple testing levels.

```text
                 ┌─────────────────┐
                 │ Integration     │
                 │ tests           │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │ Unit tests      │
                 └─────────────────┘
```

Unit tests verify individual behaviors quickly.

Integration tests verify that components work correctly against a real PostgreSQL database.

### Senior Engineering Perspective

Mocking everything can produce tests that verify the mocks rather than the system.

Using a real PostgreSQL database for integration tests gives confidence that:

```text
SQLAlchemy
    ↓
psycopg
    ↓
PostgreSQL
```

actually works.

At the same time, external APIs will be mocked where appropriate so tests remain deterministic.

---

# 10. Pytest Fixtures and Test Data Factories

The test suite uses pytest fixtures for shared infrastructure.

Current fixtures include concepts such as:

```text
db_session
repository_factory
register_repository_cleanup
```

The repository factory provides controlled test data:

```python
repository_factory(
    123,
    stars=5000,
)
```

## Why?

Tests should focus on the behavior being tested rather than repetitive object construction.

Factory fixtures also make it easy to create edge cases:

```python
repository_factory(
    123,
    language=None,
)
```

or:

```python
repository_factory(
    123,
    stars=5000,
)
```

### Senior Engineering Perspective

Good test infrastructure reduces duplication without hiding important behavior.

The goal is not abstraction for its own sake.

The goal is to make tests:

- readable
- deterministic
- isolated
- maintainable

---

# 11. External API Mocking

## Objective

Test GitHub extraction without requiring a real network connection.

The tests will mock the HTTP boundary.

Instead of:

```text
pytest
   ↓
Internet
   ↓
GitHub
```

we want:

```text
pytest
   ↓
HTTP mock
   ↓
simulated GitHub response
```

## Why?

Tests should not depend on:

- Internet availability
- GitHub availability
- API rate limits
- changing external data
- network latency

The extraction tests should be deterministic.

### Senior Engineering Perspective

The important principle is:

> Mock external dependencies, not the behavior under test.

We want to test our HTTP client's behavior while controlling the external system's response.

This will allow us to test scenarios such as:

```text
200 OK
400 Bad Request
401 Unauthorized
404 Not Found
429 Rate Limited
500 Server Error
timeout
malformed response
empty response
```

without depending on GitHub to actually produce those conditions.

---

# 12. Error Handling and Resilience

Once extraction is implemented, the pipeline will explicitly handle failure modes.

Potential concerns include:

- connection failures
- HTTP errors
- timeouts
- rate limiting
- transient server failures
- malformed responses
- database failures

Where appropriate, retries will be introduced with controlled backoff rather than blindly retrying everything.

## Design Principle

Not every error is retryable.

For example:

```text
401 Unauthorized
    → retrying probably won't help

429 Too Many Requests
    → retry after appropriate delay

500 Server Error
    → potentially retry

Connection timeout
    → potentially retry
```

### Senior Engineering Perspective

Resilience is not equivalent to:

> "Try again."

A robust system understands which failures are transient and which are permanent.

---

# 13. Configuration Management

Hard-coded configuration will eventually be replaced with environment-based configuration.

For example:

```text
DATABASE_URL
GITHUB_TOKEN
GITHUB_API_URL
BATCH_SIZE
LOG_LEVEL
```

## Why?

Configuration should not be embedded in application code.

Different environments should be able to use different configuration:

```text
Development
      ↓
Testing
      ↓
Staging
      ↓
Production
```

without changing the Python source code.

### Senior Engineering Perspective

Separating configuration from code is essential for deployment portability and security.

Secrets such as GitHub tokens should never be committed to Git.

---

# 14. Logging and Observability

The project will introduce structured logging.

Instead of relying primarily on:

```python
print(...)
```

the application will provide meaningful operational information such as:

```text
Pipeline started
Extracting page 1
Extracted 100 repositories
Transformation completed
Loading batch 1
Loading batch 2
Pipeline completed
```

Failures will include enough context to diagnose the problem.

## Why?

When a pipeline runs locally, a developer can watch the terminal.

In production, the system may run:

- inside Docker
- inside Kubernetes
- as a scheduled job
- in a cloud environment

Operational visibility therefore becomes essential.

### Senior Engineering Perspective

A production application should be diagnosable without attaching a debugger to it.

---

# 15. Performance Optimization

Performance improvements will be driven by measurements.

Areas to investigate include:

- API request count
- API pagination
- database round trips
- batch size
- transaction frequency
- memory usage
- processing time
- network latency

The project will avoid premature optimization.

## Principle

First:

```text
Measure
```

Then:

```text
Identify bottleneck
```

Then:

```text
Optimize
```

Then:

```text
Measure again
```

### Senior Engineering Perspective

Performance engineering is fundamentally an empirical discipline.

A senior developer should be able to explain not only:

> "This implementation is faster."

but also:

> "This was the bottleneck, this change addressed it, and these measurements demonstrate the improvement."

---

# 16. Docker Containerization

## Objective

Package the ETL application into a reproducible container.

The eventual architecture will resemble:

```text
┌───────────────────────────────┐
│ Docker                        │
│                               │
│  ┌─────────────────────────┐  │
│  │ ETL Application         │  │
│  │ Python                  │  │
│  └────────────┬────────────┘  │
│               │               │
└───────────────┼───────────────┘
                │
                ▼
          PostgreSQL
```

## Why?

Docker eliminates many environment-specific problems.

Instead of requiring developers to manually reproduce:

```text
Python version
dependencies
system packages
configuration
```

the application environment becomes reproducible.

### Senior Engineering Perspective

Containerization is not just about packaging.

It establishes a consistent deployment artifact that can move through:

```text
Development
     ↓
CI
     ↓
Staging
     ↓
Production
```

---

# 17. CI/CD with GitHub Actions

## Objective

Automatically validate changes whenever code is pushed or a pull request is created.

The CI pipeline will eventually perform tasks such as:

```text
Git push / Pull Request
        ↓
Install dependencies
        ↓
Run linting
        ↓
Run unit tests
        ↓
Run integration tests
        ↓
Build Docker image
        ↓
Publish artifact
```

## Why GitHub Actions?

The project already uses GitHub as its source-control platform, making GitHub Actions a natural CI/CD solution.

It also aligns directly with modern Python/cloud development practices.

### Senior Engineering Perspective

CI turns quality checks from a developer responsibility into an automated system.

The objective is to make the default path:

> "Bad code does not get merged."

rather than:

> "Someone should remember to run the tests."

---

# 18. Kubernetes

## Objective

Deploy the containerized pipeline using Kubernetes concepts.

The project will explore:

- Pods
- Deployments / Jobs
- ConfigMaps
- Secrets
- resource limits
- health checks
- scheduling
- container lifecycle

Because an ETL pipeline is fundamentally a workload rather than a continuously running web service, Kubernetes Jobs/CronJobs will be considered where appropriate.

## Design Decision

The deployment model should match the workload.

A batch ETL process does not necessarily need to behave like a permanently running API server.

### Senior Engineering Perspective

Cloud-native architecture is not about putting everything into Kubernetes.

It's about understanding the workload and selecting the appropriate operational model.

---

# 19. Cloud Deployment

The project will eventually explore deployment to a major cloud provider, with AWS as the primary target.

Potential components include:

```text
Container Registry
       ↓
Container Runtime / Kubernetes
       ↓
PostgreSQL
       ↓
Monitoring / Logging
```

The exact services will be selected based on the architecture developed in the earlier stages.

## Why?

The Luxoft target role emphasizes cloud-native applications and experience with major cloud platforms.

The objective is therefore to demonstrate not merely familiarity with cloud terminology, but an understanding of how a Python ETL workload can be designed for cloud deployment.

---

# 20. Production-Oriented Improvements

Once the core pipeline is complete, additional production concerns will be evaluated.

Potential areas include:

- idempotency
- retry policies
- dead-letter strategies
- rate-limit handling
- graceful shutdown
- memory constraints
- large dataset processing
- incremental extraction
- checkpointing
- monitoring
- alerting
- security
- secret management
- data quality checks

Not every feature will necessarily be implemented.

The goal is to evaluate each concern based on whether it provides meaningful value for this workload.

### Senior Engineering Perspective

Senior engineering is not about adding the largest number of technologies.

It is about understanding the trade-offs and choosing the appropriate level of complexity.

---

# Architecture Evolution

The project intentionally evolves through multiple levels of maturity.

### Initial version

```text
GitHub
  ↓
Python
  ↓
PostgreSQL
```

### Tested application

```text
GitHub
  ↓
Extract
  ↓
Transform + Validate
  ↓
Load
  ↓
PostgreSQL
  │
  └── Unit + Integration Tests
```

### Production-oriented application

```text
                  GitHub API
                      │
                      ▼
               ┌─────────────┐
               │   Extract   │
               └──────┬──────┘
                      │
               ┌──────▼──────┐
               │  Transform  │
               │  Validate   │
               └──────┬──────┘
                      │
               ┌──────▼──────┐
               │     Load    │
               │   Upsert    │
               └──────┬──────┘
                      │
                      ▼
                 PostgreSQL

       ┌────────────────────────────┐
       │ Cross-cutting concerns     │
       │                            │
       │ Testing                    │
       │ Logging                    │
       │ Configuration              │
       │ Error handling             │
       │ Performance                │
       └────────────────────────────┘
```

### Cloud-native version

```text
                    GitHub API
                        │
                        ▼
                 ┌─────────────┐
                 │ ETL Job     │
                 │ Container   │
                 └──────┬──────┘
                        │
                  Kubernetes
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       PostgreSQL             Observability
       / Cloud DB             / Logging
```

---

# Engineering Principles

Throughout the project, implementation decisions are guided by several principles.

## 1. Correctness before optimization

The pipeline should produce correct data before performance optimization is attempted.

## 2. Measure before optimizing

Performance changes should be supported by measurements.

## 3. Explicit boundaries

Each pipeline stage should have a clearly defined responsibility and interface.

## 4. Idempotency

Repeated execution should not corrupt or duplicate data.

## 5. Testability

External dependencies should be isolated so important behaviors can be tested deterministically.

## 6. Failure is a normal state

The design should explicitly consider what happens when dependencies fail.

## 7. Minimize unnecessary complexity

Technologies and abstractions should solve real problems rather than exist for demonstration purposes.

## 8. Reproducibility

Development, testing and deployment environments should be reproducible.

## 9. Observability

Production systems should provide enough information to understand what they are doing and why they failed.

## 10. Maintainability

Code should be organized so that another engineer can understand and modify it without reverse-engineering the entire application.

---

# Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.x |
| Data validation | Pydantic |
| Database | PostgreSQL |
| Database access | SQLAlchemy |
| Database driver | psycopg |
| Migrations | Alembic |
| Testing | pytest |
| API | GitHub REST API |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Orchestration | Kubernetes |
| Cloud | AWS / major cloud concepts |
| Source control | Git / GitHub |

---

# Current Status

The project currently has the following capabilities:

- [x] PostgreSQL running in Docker
- [x] Database schema
- [x] Alembic migrations
- [x] Pydantic repository model
- [x] SQLAlchemy database model
- [x] Repository transformation
- [x] PostgreSQL upsert loading
- [x] Batch database loading
- [x] Explicit transaction handling
- [x] Performance benchmarking
- [x] Unit tests
- [x] PostgreSQL integration tests
- [x] Pytest fixtures
- [x] Factory fixtures
- [x] Automatic test-data cleanup
- [ ] GitHub API extraction tests
- [ ] HTTP mocking
- [ ] API error handling
- [ ] Retry / rate-limit strategy
- [ ] Configuration management
- [ ] Structured logging
- [ ] Dockerized ETL application
- [ ] GitHub Actions CI/CD
- [ ] Kubernetes deployment
- [ ] Cloud deployment
- [ ] Production observability

---

# Running the Tests

Activate the project environment and run:

```bash
python -m pytest
```

The test suite currently contains 10 tests covering transformation, database loading, batching, upserts and transaction rollback.

---

# Why GitHub?

GitHub provides a realistic external data source while keeping the project accessible and reproducible.

The API introduces several real-world engineering concerns:

- pagination
- HTTP failures
- rate limiting
- authentication
- changing external data
- network latency
- response validation

This makes GitHub considerably more useful for demonstrating ETL engineering than a static CSV file alone.

---

# What This Project Is Intended to Demonstrate

This project is not intended to demonstrate that an engineer can write:

```python
requests.get(...)
```

followed by:

```python
INSERT INTO ...
```

The more important objective is to demonstrate the engineering thought process surrounding the pipeline:

```text
What happens if the API fails?

What happens if only half the data loads?

Can the pipeline safely run twice?

How do we know the data is valid?

How do we test external dependencies?

How do we measure performance?

How do we reproduce the environment?

How do we deploy it?

How do we know it is working in production?

How do we diagnose failures?

How does the architecture change when the dataset grows?
```

Those questions drive the evolution of the project.

The resulting application is therefore intended to serve as both a **practical ETL implementation and a demonstration of senior-level software engineering decision-making**.