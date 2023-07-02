import json
from typing import Dict, Protocol

from openapi_core.datatypes import RequestParameters
from werkzeug.datastructures import Headers, ImmutableMultiDict

from powertools_oas_validator.exceptions import InvalidEventError
from powertools_oas_validator.types import Request


class EventParserProtocol(Protocol):
    def event_to_request(self) -> Request:
        raise NotImplementedError  # pragma: nocover


class EventParser(EventParserProtocol):
    def __init__(self, event: Dict) -> None:
        self.event = event

    def event_to_request(self) -> Request:
        return Request(
            host_url=self.get_host_url(),
            path=self.get_path(),
            full_url_pattern=self.get_full_url_pattern(),
            method=self.get_method(),
            parameters=self.get_parameters(),
            body=self.get_body(),
            mimetype=self.get_mimetype(),
        )

    def _get_headers(self) -> Dict:
        try:
            return self.event["headers"]
        except KeyError:
            raise InvalidEventError("'headers' missing from event.")

    def get_path(self) -> str:
        try:
            return self.event["path"]
        except KeyError:
            raise InvalidEventError("'path' missing from event.")

    def get_host_url(self) -> str:
        try:
            proto = self._get_headers()["X-Forwarded-Proto"]
        except KeyError:
            raise InvalidEventError("'headers.X-Forwarded-Proto' missing from event.")

        try:
            host = self._get_headers()["Host"]
        except KeyError:
            raise InvalidEventError("'headers.Host' missing from event.")

        return f"{proto}://{host}"

    def get_method(self) -> str:
        try:
            return self.event["httpMethod"].lower()
        except KeyError:
            raise InvalidEventError("'httpMethod' missing from event.")

    def get_mimetype(self) -> str:
        try:
            return self._get_headers()["Content-Type"]
        except KeyError:
            raise InvalidEventError("'headers.Content-Type' missing from event.")

    def get_full_url_pattern(self) -> str:
        host_url = self.get_host_url()

        try:
            return host_url + self.event["path"]
        except KeyError:
            raise InvalidEventError("'path' missing from event.")

    def get_parameters(self) -> RequestParameters:
        try:
            query_params = self.event["queryStringParameters"]
        except KeyError:
            query_params = {}

        query_params = ImmutableMultiDict(query_params)

        headers = Headers(self._get_headers())

        cookies: Dict = {}  # TODO: support cookies

        cookies = ImmutableMultiDict(cookies)

        try:
            path_params = self.event["pathParameters"]
        except KeyError:
            path_params = {}

        return RequestParameters(
            query=query_params, header=headers, cookie=cookies, path=path_params
        )

    def get_body(self) -> str:
        try:
            body = self.event["body"]
        except KeyError:
            return ""

        if type(body) == str:
            return body
        else:
            return json.dumps(body)
