from app import App, Response, Request

app = App()


@app.route('^/index/(?P<name>[a-zA-Z]+)$')
def index(request: Request, name: str) -> Response:
    return Response(body=f'Hello index: {name}!')


@app.route('^/number/(?P<num>[0-9]+)$')
def number(request: Request, num: int) -> Response:
    return Response(body=f'Hello index: {num}!')


@app.route('/tmp')
def tmp(request: Request) -> Response:
    return Response(body='Hello tmp!')

