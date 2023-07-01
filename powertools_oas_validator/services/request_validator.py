import json
from abc import abstractmethod
from typing import Callable, Dict, List, Optional

from chocs import HttpMethod  # type: ignore
from chocs import (
    HttpCookie,
    HttpCookieJar,
    HttpHeaders,
    HttpQueryString,
    HttpRequest,
    HttpResponse,
)
from chocs.middleware import MiddlewareHandler  # type: ignore
from chocs_middleware.openapi.middleware import OpenApiMiddleware
from opyapi import JsonSchema

from powertools_oas_validator.exceptions import InvalidEventError
from powertools_oas_validator.types import ValidationConfig


class MiddlewareWrapper(OpenApiMiddleware):
    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        raise NotImplementedError  # pragma: nocover

    def get_validators_for_uri(
        self, route: str, method: HttpMethod, content_type: str
    ) -> List[Callable]:
        return self._get_validators_for_uri(route, method, content_type)


class RequestValidatorABC(MiddlewareWrapper):
    @abstractmethod
    def get_path(self, event: Dict) -> str:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_method(self, event: Dict) -> HttpMethod:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_headers(self, event: Dict) -> Optional[HttpHeaders]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_query_string(self, event: Dict) -> Optional[HttpQueryString]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_body(self, event: Dict) -> Optional[str]:
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_cookies(self, event: Dict) -> HttpCookieJar:
        raise NotImplementedError  # pragma: nocover


class RequestValidator(RequestValidatorABC):
    def __init__(self, file_path: str, validation_config: ValidationConfig) -> None:
        self.openapi = JsonSchema.from_file(file_path)
        self.validators = validation_config.config
        self._validators: Dict[str, List[Callable]] = {}

    def get_path(self, event: Dict) -> str:
        try:
            return event["resource"]
        except KeyError:
            raise InvalidEventError("'resource' not in event")

    def get_method(self, event: Dict) -> HttpMethod:
        try:
            return HttpMethod[event["httpMethod"]]
        except KeyError:
            raise InvalidEventError("'httpMethod' not in event")

    def get_headers(self, event: Dict) -> Optional[HttpHeaders]:
        if "headers" in event:
            return HttpHeaders(event["headers"])
        else:
            return None

    def get_query_string(self, event: Dict) -> Optional[HttpQueryString]:
        if "rawQueryString" in event:
            return HttpQueryString(event["rawQueryString"])

        else:
            return None

    def get_body(self, event: Dict) -> Optional[str]:
        if "body" in event:
            if type(event["body"]) == dict:
                return json.dumps(event["body"])
            else:
                return event["body"]
        else:
            return None

    def get_cookies(self, event: Dict) -> HttpCookieJar:
        cookie_jar = HttpCookieJar()
        if "cookies" in event:
            for event_cookie in event["cookies"]:
                cookies = event_cookie.replace(" ", "").split(";")

                for cookie in cookies:
                    values = cookie.split("=")

                    if len(values) == 1:
                        value = ""
                    else:
                        value = values[1]

                    cookie_jar.append(HttpCookie(values[0], value))
        return cookie_jar
