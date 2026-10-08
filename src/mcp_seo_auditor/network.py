"""Bounded HTTP fetches with DNS pinning and redirect revalidation."""
import http.client
import ipaddress
import socket
import ssl
import time
from urllib.parse import urlsplit, urljoin, urldefrag
from .audit import MAX_HTML

USER_AGENT = 'MCPSEOAuditor/0.1 (+read-only SEO audit)'

def validate_url(url):
    if not isinstance(url, str) or len(url) > 4096 or any(ord(c) < 33 for c in url):
        raise ValueError('Invalid URL')
    p = urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
        raise ValueError('Only public HTTP(S) URLs without credentials are allowed')
    if p.port and p.port not in (80,443): raise ValueError('Only ports 80 and 443 are allowed')
    return p

def public_addresses(host, port):
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses: raise ValueError('DNS returned no addresses')
    for _, _, _, _, address in addresses:
        ip = ipaddress.ip_address(address[0])
        if not ip.is_global or (getattr(ip,'ipv4_mapped',None) and not ip.ipv4_mapped.is_global):
            raise ValueError('Private, loopback, reserved and link-local destinations are blocked')
    return addresses

class PinnedConnection(http.client.HTTPConnection):
    def connect(self):
        addresses = public_addresses(self.host, self.port)
        family, socktype, proto, _, address = addresses[0]
        self.sock = socket.socket(family, socktype, proto)
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect(address)
            if self.port == 443:
                self.sock = ssl.create_default_context().wrap_socket(self.sock, server_hostname=self.host)
        except Exception:
            self.sock.close()
            raise

def fetch(url, *, same_origin=None, timeout=10, allowed=None):
    start = time.monotonic(); chain = []
    for _ in range(6):
        p = validate_url(url)
        if allowed and not allowed(url): raise ValueError("URL disallowed by robots.txt")
        if same_origin and (p.scheme,p.netloc) != same_origin:
            raise ValueError('Cross-origin crawl redirect blocked')
        conn = PinnedConnection(p.hostname, p.port or (443 if p.scheme == 'https' else 80), timeout=timeout)
        # Encryption follows scheme, not port. Reject unconventional scheme/port combinations.
        if (p.scheme == 'http' and p.port == 443) or (p.scheme == 'https' and p.port == 80):
            raise ValueError('Scheme and port must match')
        try:
            conn.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''), headers={'User-Agent':USER_AGENT,'Accept-Encoding':'identity','Accept':'text/html,text/plain;q=0.9,*/*;q=0.1'})
            response = conn.getresponse()
            headers = {k.lower():v for k,v in response.getheaders()}
            if response.status in (301,302,303,307,308):
                if not headers.get('location'): raise ValueError('Redirect without Location')
                chain.append({'url':url,'status':response.status})
                url = urldefrag(urljoin(url,headers['location']))[0]
                continue
            if headers.get('content-encoding','identity').lower() != 'identity': raise ValueError('Compressed responses are not supported')
            body = response.read(MAX_HTML + 1)
            if len(body) > MAX_HTML: raise ValueError('Response exceeds 2 MB')
            charset = response.headers.get_content_charset() or 'utf-8'
            try: text = body.decode(charset, errors='replace')
            except LookupError: text = body.decode('utf-8', errors='replace')
            return {'url':url,'status':response.status,'headers':headers,'body':text,'redirects':chain,'elapsedMs':round((time.monotonic()-start)*1000)}
        finally: conn.close()
    raise ValueError('Too many redirects')
