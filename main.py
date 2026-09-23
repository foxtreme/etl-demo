import logging
import time

from config import Settings
from github_client import GitHubClient
from database import Database
from extract import extract_repositories
from load import load_repositories
from transform import transform_repository
from logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

settings = Settings()

github_client = GitHubClient(
    token=settings.github_token,
    timeout=settings.request_timeout,
    max_retries=settings.max_retries,
    retry_delay=settings.retry_delay
)

database = Database(settings.database_url)
logger.info("Starting ETL pipeline")
extract_time = time.perf_counter()

raw_repositories = list(
    extract_repositories(
        github_client,
        org=settings.github_org,
        per_page=100,
        max_pages=1
    )
)

extract_elapsed = time.perf_counter() - extract_time

logger.info(
    "Extraction completed: %d repositories in %.4f seconds",
    len(raw_repositories),
    extract_elapsed
)

transform_start = time.perf_counter()

repositories = [
    transform_repository(repository)
    for repository in raw_repositories
]

transform_elapsed = time.perf_counter() - transform_start
logger.info(
    "Transformation completed: %d repositories in %.4f seconds",
    len(repositories),
    transform_elapsed
)
load_start = time.perf_counter()

with database.session_factory() as session:
    try:
        load_repositories(session, repositories, batch_size=500)
        session.commit()

    except Exception:
        session.rollback()
        logger.exception("Database loading failed; transaction rolled back")
        raise

load_elapsed = time.perf_counter() - load_start

logger.info(
    "Loading completed: %d repositories in %.4f seconds",
    len(repositories),
    load_elapsed
)

total_elapsed = extract_elapsed + transform_elapsed + load_elapsed

logger.info(
    "ETL pipeline completed successfully in %.4f seconds",
    total_elapsed
)
