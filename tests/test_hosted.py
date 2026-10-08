import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

from mcp_seo_auditor.control_plane import consume
from mcp_seo_auditor.hosted import create_server


class FakeControlPlane(BaseHTTPRequestHandler):
    used = 0
    limit = 2
    events = []

    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        body = json.loads(self.rfile.read(length).decode())
        FakeControlPlane.events.append(body)
        auth = self.headers.get('Authorization', '')
        if auth != 'Bearer mcp_test':
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"unauthorized"}')
            return
        if FakeControlPlane.used + body.get('units', 1) > FakeControlPlane.limit:
            self.send_response(429)
            self.end_headers()
            self.wfile.write(json.dumps({
                'allowed': False, 'used': FakeControlPlane.used, 'limit': FakeControlPlane.limit,
            }).encode())
            return
        FakeControlPlane.used += body.get('units', 1)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'allowed': True, 'duplicate': False,
            'used': FakeControlPlane.used, 'limit': FakeControlPlane.limit,
        }).encode())


class HostedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FakeControlPlane.used = 0
        FakeControlPlane.events = []
        cls.cp = HTTPServer(('127.0.0.1', 0), FakeControlPlane)
        cls.cp_thread = threading.Thread(target=cls.cp.serve_forever, daemon=True)
        cls.cp_thread.start()
        cls.cp_url = f'http://127.0.0.1:{cls.cp.server_address[1]}'
        cls.hosted = create_server(cls.cp_url, host='127.0.0.1', port=0)
        cls.hosted_thread = threading.Thread(target=cls.hosted.serve_forever, daemon=True)
        cls.hosted_thread.start()
        cls.hosted_url = f'http://127.0.0.1:{cls.hosted.server_address[1]}'

    @classmethod
    def tearDownClass(cls):
        cls.hosted.shutdown()
        cls.cp.shutdown()

    def _post(self, path, body, token='mcp_test'):
        req = urllib.request.Request(
            self.hosted_url + path,
            data=json.dumps(body).encode(),
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode())

    def test_audit_html_quota_and_payload_hygiene(self):
        FakeControlPlane.used = 0
        FakeControlPlane.events = []
        status, body = self._post('/v1/audit-html', {
            'requestId': 'h1',
            'html': '<html lang="en"><head><title>Example business and services</title>'
                    '<meta name="description" content="Useful business description">'
                    '<meta name="viewport" content="width=device-width">'
                    '<link rel="canonical" href="https://example.com/"></head>'
                    '<body><h1>Services</h1></body></html>',
        })
        self.assertEqual(status, 200)
        self.assertEqual(body['usage']['product'], 'seo-auditor')
        self.assertIn('report', body)

        status2, _ = self._post('/v1/audit-html', {
            'requestId': 'h2',
            'html': '<html><head><title>x</title></head><body><h1>y</h1></body></html>',
        })
        self.assertEqual(status2, 200)

        status3, err = self._post('/v1/audit-html', {
            'requestId': 'h3',
            'html': '<html></html>',
        })
        self.assertEqual(status3, 429)
        self.assertEqual(err['error'], 'quota_exceeded')

        for event in FakeControlPlane.events:
            self.assertEqual(sorted(event.keys()), ['product', 'requestId', 'units'])
            self.assertEqual(event['product'], 'seo-auditor')
            self.assertNotIn('html', event)
            self.assertNotIn('url', event)

    def test_consume_helper_rejects_bad_url(self):
        with self.assertRaises(ValueError):
            consume(base_url='ftp://x', api_key='k', request_id='r1')


if __name__ == '__main__':
    unittest.main()
