from __future__ import annotations

import time

import httpx


class RetryingClient:
    def __init__(self, wrapped: httpx.Client, retries: int = 2) -> None:
        self._wrapped = wrapped
        self._retries = retries

    def __enter__(self) -> "RetryingClient":
        self._wrapped.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        self._wrapped.__exit__(*args)

    def get(self, *args: object, **kwargs: object) -> httpx.Response:
        return self._request("GET", *args, **kwargs)

    def post(self, *args: object, **kwargs: object) -> httpx.Response:
        return self._request("POST", *args, **kwargs)

    def _request(self, method: str, *args: object, **kwargs: object) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self._retries + 1):
            try:
                return self._wrapped.request(method, *args, **kwargs)
            except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as exc:
                last_exc = exc
                if attempt >= self._retries:
                    break
                time.sleep(1.5 * (attempt + 1))
        assert last_exc is not None
        raise last_exc


def client(headers: dict[str, str] | None = None) -> RetryingClient:
    base_headers = {
        "User-Agent": "github-high-potential-ai-trend-workflow/0.1",
        "Accept": "application/json,text/html,application/xml;q=0.9,*/*;q=0.8",
    }
    if headers:
        base_headers.update(headers)
    wrapped = httpx.Client(headers=base_headers, timeout=25.0, follow_redirects=True)
    return RetryingClient(wrapped)
