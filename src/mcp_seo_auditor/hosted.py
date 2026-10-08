"""Hosted HTTP surface with control-plane quotas. Local MCP stdio stays free."""
from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .audit import audit_html
from .control_plane import assert_control_plane_url, consume
from .server import audit_url, crawl_site

PRODUCT = 'seo-auditor'
_ID = re.compile(r'^[a-zA-Z0-9_-]{1,100}$')
MAX_BODY = 2 * 1024 * 1024


class HostedError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _run(path: str, body: dict):
    if path == '/v1/audit-html':
        if not isinstance(body.get('html'), str):
            raise HostedError(400, 'invalid_html')
        return audit_html(body['html'], url=body.get('url') or 'https://example.com/')
    if path == '/v1/audit-url':
        if not isinstance(body.get('url'), str):
            raise HostedError(400, 'invalid_url')
        return audit_url(body['url'])
    if path == '/v1/crawl':
        if not isinstance(body.get('url'), str):
            raise HostedError(400, 'invalid_url')
        max_pages = body.get('max_pages', 5)
        if type(max_pages) is not int or not 1 <= max_pages <= 10:
            raise HostedError(400, 'invalid_max_pages')
        return crawl_site(body['url'], max_pages=max_pages)
    raise HostedError(404, 'not_found')


def make_handler(*, control_plane_url: str, consume_fn=consume):
    base_url = assert_control_plane_url(control_plane_url)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # noqa: N802
            return

        def _send(self, status: int, body: dict):
            raw = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # noqa: N802
            if self.path.split('?', 1)[0] == '/health':
                return self._send(200, {'status': 'ok'})
            return self._send(404, {'error': 'not_found'})

        def do_POST(self):  # noqa: N802
            try:
                path = self.path.split('?', 1)[0]
                if path not in ('/v1/audit-html', '/v1/audit-url', '/v1/crawl'):
                    raise HostedError(404, 'not_found')
                auth = self.headers.get('Authorization', '')
                if not auth.startswith('Bearer ') or not auth[7:]:
                    raise HostedError(401, 'unauthorized')
                api_key = auth[7:]
                length = int(self.headers.get('Content-Length') or 0)
                if length > MAX_BODY:
                    raise HostedError(413, 'body_too_large')
                raw = self.rfile.read(length) if length else b''
                try:
                    body = json.loads(raw.decode() or 'null')
                except Exception as exc:
                    raise HostedError(400, 'invalid_json') from exc
                if not isinstance(body, dict):
                    raise HostedError(400, 'invalid_json')
                request_id = body.get('requestId')
                if not isinstance(request_id, str) or not _ID.match(request_id):
                    raise HostedError(400, 'invalid_request_id')
                units = body.get('units', 1)
                if type(units) is not int or units < 1:
                    raise HostedError(400, 'invalid_units')

                reservation = consume_fn(
                    base_url=base_url, api_key=api_key, request_id=request_id, units=units,
                )
                if not reservation.get('ok'):
                    status = reservation.get('status', 502)
                    if status not in (401, 409, 429) and not (400 <= status < 600):
                        status = 502
                    raise HostedError(status, reservation.get('error') or 'control_plane_error')

                try:
                    report = _run(path, body)
                except HostedError:
                    raise
                except Exception as exc:
                    raise HostedError(400, str(exc) or 'analysis_failed') from exc

                return self._send(200, {
                    'report': report,
                    'usage': {
                        'product': PRODUCT,
                        'requestId': request_id,
                        'units': units,
                        'duplicate': reservation.get('duplicate'),
                        'used': reservation.get('used'),
                        'limit': reservation.get('limit'),
                    },
                })
            except HostedError as exc:
                return self._send(exc.status, {'error': str(exc)})
            except Exception:
                return self._send(500, {'error': 'internal_error'})

    return Handler


def create_server(control_plane_url: str, host='127.0.0.1', port=3104, consume_fn=consume):
    handler = make_handler(control_plane_url=control_plane_url, consume_fn=consume_fn)
    return ThreadingHTTPServer((host, port), handler)


def main():
    url = os.environ.get('CONTROL_PLANE_URL', '')
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '3104'))
    server = create_server(url, host=host, port=port)
    print('SEO Auditor hosted listening', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
