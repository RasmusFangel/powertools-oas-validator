from dataclasses import dataclass

from openapi_core.datatypes import RequestParameters
from openapi_core.protocols import Request as CoreRequest


@dataclass
class OpenAPIVersion:  # pragma: nocover
    major: int
    minor: int
    pico: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.pico}"


class Request(CoreRequest):  # pragma: nocover
    def __init__(
        self,
        host_url: str,
        path: str,
        full_url_pattern: str,
        method: str,
        parameters: RequestParameters,
        body: str,
        mimetype: str,
    ) -> None:
        self._host_url = host_url
        self._path = path
        self._full_url_pattern = full_url_pattern
        self._method = method
        self.parameters = parameters
        self._body = body
        self._mimetype = mimetype

    @property
    def host_url(self) -> str:
        return self._host_url

    @host_url.setter
    def host_url(self, val: str) -> None:
        self._host_url = val

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, val: str) -> None:
        self._path = val

    @property
    def full_url_pattern(self) -> str:
        return self._full_url_pattern

    @full_url_pattern.setter
    def full_url_pattern(self, val: str) -> None:
        self._full_url_pattern = val

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, val: str) -> None:
        self._method = val

    @property
    def body(self) -> str:
        return self._body

    @body.setter
    def body(self, val: str) -> None:
        self._body = val

    @property
    def mimetype(self) -> str:
        return self._mimetype

    @mimetype.setter
    def mimetype(self, val: str) -> None:
        self._mimetype = val
