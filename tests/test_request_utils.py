import pytest
import requests
from request_utils import request_with_retry


class FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_request_with_retry_returns_returns_response_on_success(monkeypatch):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse(200)

    monkeypatch.setattr(requests, 'get', fake_get)

    response = request_with_retry("https://example.com")

    assert response.status_code == 200
    assert calls == 1


def test_request_with_retry_retries_on_server_error(monkeypatch):
    responses = [
        FakeResponse(500),
        FakeResponse(200)
    ]

    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        response = responses[calls]
        calls += 1
        return response

    monkeypatch.setattr(requests, 'get', fake_get)

    response = request_with_retry("https://example.com", delay=0)
    assert response.status_code == 200
    assert calls == 2


def test_request_with_retry_raises_after_retries_exhausted(monkeypatch):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse(500)

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(requests.HTTPError):
        request_with_retry("https://example.com", max_retries=3, delay=0)

    assert calls == 4


def test_request_with_retry_does_not_retry_non_retryable_error(monkeypatch):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        return FakeResponse(404)

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(requests.HTTPError):
        request_with_retry("https://example.com", max_retries=3, delay=0)
    assert calls == 1


def test_request_with_retry_retries_on_rate_lmit(monkeypatch):
    responses = [
        FakeResponse(429),
        FakeResponse(200)
    ]

    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        response = responses[calls]
        calls += 1
        return response

    monkeypatch.setattr(requests, 'get', fake_get)

    response = request_with_retry("https://example.com", delay=0)

    assert response.status_code == 200
    assert calls == 2


def test_request_with_retry_retries_on_timeout(monkeypatch):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise requests.Timeout()
        return FakeResponse(200)

    monkeypatch.setattr(requests, 'get', fake_get)

    response = request_with_retry("https://example.com", delay=0)
    assert response.status_code == 200
    assert calls == 2


def test_request_with_retry_retries_on_connection_error(monkeypatch):
    calls = 0

    def fake_get(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise requests.ConnectionError()
        return FakeResponse(200)

    monkeypatch.setattr(requests, 'get', fake_get)

    response = request_with_retry("https://example.com", delay=0)
    assert response.status_code == 200
    assert calls == 2


def test_request_with_retry_waits_between_retries(monkeypatch):
    sleep_calls = []

    def fake_sleep(delay):
        sleep_calls.append(delay)

    monkeypatch.setattr('request_utils.time.sleep', fake_sleep)
