import re
import json
from typing import Any, Optional, Callable

from pydantic import BaseModel


class Response(BaseModel):
    status: Optional[str] = None
    response_headers: list[tuple[str, str]] = []
    body: str


class Request:
    def __init__(self, environ, charset="utf-8"):
        self.environ = environ
        self._body = None
        self.charset = charset

    @property
    def path(self):
        return self.environ["PATH_INFO"] or "/"

    @property
    def method(self):
        return self.environ["REQUEST_METHOD"].upper()

    @property
    def query(self):
        return self.environ["QUERY_STRING"]

    @property
    def body(self):
        if self._body is None:
            content_length = int(self.environ.get("CONTENT_LENGTH"), 0)
            self._body = self.environ["wsgi.input"].read(content_length)
        return self._body

    @property
    def text(self):
        return self.body.decode(self.charset)

    @property
    def json(self):
        return json.loads(self.body)


def http404(request: Request) -> Response:
    status = "404 Not Found"
    response_headers = [("Content-type", "text/plain")]
    body = b"404 Not Found"
    return Response(status=status, response_headers=response_headers, body=body)


def response_http(response: Response, start_response):
    status = response.status
    if status is None:
        status = "200 OK"

    response_headers = response.response_headers
    if not response_headers:
        response_headers = [("Content-type", "text/plain")]

    start_response(status, response_headers)
    body = response.body
    return [body.encode()]


class RouteParams(BaseModel):
    path: str
    handler: Callable[[Request, dict], Response]


class Router:
    def __init__(self):
        self.routes: list[RouteParams] = []

    def add(self, params: RouteParams):
        self.routes.append(params)

    def match(self, method: str, path: str) -> (Callable[[Request, dict], Response], dict):
        for route in self.routes:
            if re.match(route.path, path):
                params = re.match(route.path, path).groupdict()
                return route.handler, params
        else:
            return http404, {}


class App:
    def __init__(self):
        self.router = Router()

    def __call__(self, environ, start_response):
        method = environ["REQUEST_METHOD"].upper()
        path = environ["PATH_INFO"] or "/"

        handler, params = self.router.match(method, path)
        request = Request(environ)
        res = handler(request, **params)
        return response_http(res, start_response)

    def route(self, path: str):
        def _handler(handler: Any):
            self.router.add(RouteParams(path=path, handler=handler))
        return _handler
