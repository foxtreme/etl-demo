import time
import logging
import requests

logger = logging.getLogger(__name__)


def request_with_retry(
        url: str,
        *,
        params=None,
        headers=None,
        timeout=10,
        max_retries=3,
        delay=1
):
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url,
                                    params=params,
                                    headers=headers,
                                    timeout=timeout
                                    )

        except (requests.Timeout, requests.ConnectionError) as error:
            if attempt < max_retries:
                logger.warning(
                    "Request failed with %s. Retrying attempt %d/%d",
                    type(error).__name__,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(delay)
                continue
            logger.error(
                "Request failed after %d retries",
                max_retries,
            )
            raise
        if is_retryable_response(response):
            if attempt < max_retries:
                logger.warning(
                    "Received HTTP %d. Retrying attempt %d/%d",
                    response.status_code,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(delay)
                continue

        response.raise_for_status()
        return response


def is_retryable_response(response: requests.Response) -> bool:
    return response.status_code == 429 or 500 <= response.status_code < 600
