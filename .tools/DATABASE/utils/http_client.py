# .tools/database/utils/http_client.py
# by LECHAT Jérôme; creation date: 11/2026, latest edit: 11/2026
# with the help of OpenCode V2 (code model: Kimi K2.7 Code)

# INTERNAL(S)
from dataclasses import dataclass

# EXTERNAL(S)
from scrapling.fetchers import FetcherSession


class HttpError(Exception):
    """ HTTP error (status >= 400). """

    def __init__(self, status: int, url: str) -> None:
        super().__init__(f"HTTP {status} for {url}")
        self.status = status
        self.url = url


@dataclass(frozen=True, slots=True)
class Response:
    """ Standard response: bytes + HTTP metadata. """

    status: int
    body: bytes
    headers: dict[str, str]
    url: str
    encoding: str | None = None

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise HttpError(self.status, self.url)


class HttpClient:
    """ Reused HTTP session: a single open connection, reused for all links. """

    def __init__(self, *, timeout: float = 15.0, headers: dict[str, str] | None = None, retries: int = 3, retry_delay: int = 1) -> None:
        self._timeout = timeout
        self._headers = headers
        self._retries = retries
        self._retry_delay = retry_delay
        self._session: FetcherSession | None = None
        self._active: object | None = None

    def _ensure(self) -> object:
        if self._active is None:
            self._session = FetcherSession(impersonate="chrome", stealthy_headers=True, follow_redirects="safe", timeout=self._timeout, headers=self._headers, retries=self._retries, retry_delay=self._retry_delay)
            self._active = self._session.__enter__()
        return self._active

    def get(self, url: str, *, timeout: float | None = None, headers: dict[str, str] | None = None) -> Response:
        page = self._ensure().get(url, timeout=timeout if timeout is not None else self._timeout, headers=headers) # type: ignore[attr-defined]
        return Response(page.status, page.body, dict(page.headers), page.url, page.encoding)

    def close(self) -> None:
        if self._session is not None:
            self._session.__exit__(None, None, None)
            self._session = None
            self._active = None

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
