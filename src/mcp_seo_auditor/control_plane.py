"""HTTP client for family control-plane consume. Never send HTML or URLs."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

PRODUCT = 'seo-auditor'
_ID = re.compile(r'^[a-zA-Z0-9_-]{1,100}$')


def assert_control_plane_url(base_url: str) -> str:
    if not isinstance(base_url, str) or not re.match(r'^https?://', base_url, re.I):
        raise ValueError('CONTROL_PLANE_URL must be an http(s) URL')
    return base_url.rstrip('/')


def consume(*, base_url: str, api_key: str, request_id: str, units: int = 1,
            product: str = PRODUCT, timeout: float = 10.0, opener=None) -> dict:
    root = assert_control_plane_url(base_url)
    payload = {'product': product, 'requestId': request_id, 'units': units}
    if not isinstance(api_key, str) or not api_key:
        return {'ok': False, 'status': 401, 'error': 'unauthorized', 'payload': payload}
    if not isinstance(request_id, str) or not _ID.match(request_id):
        return {'ok': False, 'status': 400, 'error': 'invalid_request_id', 'payload': payload}
    if not isinstance(units, int) or isinstance(units, bool) or units < 1:
        return {'ok': False, 'status': 400, 'error': 'invalid_units', 'payload': payload}

    req = urllib.request.Request(
        f'{root}/v1/usage/consume',
        data=json.dumps(payload).encode(),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    open_url = opener.open if opener else urllib.request.urlopen
    try:
        with open_url(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode() or 'null')
            status = getattr(resp, 'status', 200)
            if status == 200 and isinstance(body, dict) and body.get('allowed'):
                return {
                    'ok': True, 'status': 200, 'duplicate': bool(body.get('duplicate')),
                    'used': body.get('used'), 'limit': body.get('limit'), 'payload': payload,
                }
            return {'ok': False, 'status': status, 'error': (body or {}).get('error', 'control_plane_error'), 'payload': payload}
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode() or 'null')
        except Exception:
            body = None
        if exc.code == 429:
            return {'ok': False, 'status': 429, 'error': 'quota_exceeded',
                    'used': (body or {}).get('used'), 'limit': (body or {}).get('limit'), 'payload': payload}
        if exc.code == 409:
            return {'ok': False, 'status': 409, 'error': 'request_id_conflict', 'payload': payload}
        if exc.code == 401:
            return {'ok': False, 'status': 401, 'error': 'unauthorized', 'payload': payload}
        return {'ok': False, 'status': exc.code, 'error': (body or {}).get('error', 'control_plane_error'), 'payload': payload}
    except Exception:
        return {'ok': False, 'status': 502, 'error': 'control_plane_unreachable', 'payload': payload}
