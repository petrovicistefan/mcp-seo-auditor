import json
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
from mcp_seo_auditor.audit import audit_html
from mcp_seo_auditor.network import public_addresses, validate_url
from mcp_seo_auditor.server import dispatch, crawl_site, invoke, Session

INIT = dict(jsonrpc='2.0',id=0,method='initialize',params={'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}})
READY = dict(jsonrpc='2.0',method='notifications/initialized')

GOOD = '''<html lang="en"><head><title>Example business and services</title><meta name="description" content="Useful business description"><meta name="viewport" content="width=device-width"><link rel="canonical" href="https://example.com/"></head><body><h1>Our <em>services</em></h1><img alt=""><a href="/contact">Contact</a><script type="application/ld+json">{"@type":"Organization"}</script></body></html>'''

class AuditTests(unittest.TestCase):
    def test_good_page(self):
        r = audit_html(GOOD)
        self.assertEqual(r['score'],100)
        self.assertEqual(r['headings'][0]['text'],'Our services')
        self.assertEqual(r['internalLinks'],['https://example.com/contact'])
        self.assertEqual(r['structuredData']['validJsonBlocks'],1)
    def test_issues(self):
        r = audit_html('<img src="a"><script type="application/ld+json">oops</script>',headers={'x-robots-tag':'noindex'})
        codes = {f['code'] for f in r['findings']}
        self.assertTrue({'missing_title','missing_h1','missing_alt','noindex','invalid_json_ld'} <= codes)
    def test_base_and_decorative_alt(self):
        r = audit_html('<base href="https://other.com/"><a href="x">x</a><img alt="">')
        self.assertEqual(r['externalLinkCount'],1)
        self.assertEqual(r['images']['missingAlt'],0)
    def test_size_bound(self):
        with self.assertRaises(ValueError): audit_html('a'*2_000_001)
    def test_url_validation(self):
        for url in ('file:///etc/passwd','http://u:p@example.com','https://example.com:8080','http://example.com/\nX'):
            with self.assertRaises(ValueError): validate_url(url)
    def test_ssrf_mixed_dns(self):
        answers = [(socket.AF_INET,socket.SOCK_STREAM,6,'',('8.8.8.8',80)),(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',80))]
        with patch('socket.getaddrinfo',return_value=answers):
            with self.assertRaises(ValueError): public_addresses('example.com',80)
    def test_private_ranges(self):
        for ip in ('10.0.0.1','169.254.169.254','127.0.0.1','192.168.1.1','::1','::ffff:127.0.0.1'):
            with patch('socket.getaddrinfo',return_value=[(socket.AF_INET6 if ':' in ip else socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,80))]):
                with self.assertRaises(ValueError): public_addresses('example.com',80)
    def test_redirect_robots_checked_before_request(self):
        from mcp_seo_auditor.network import fetch
        response = unittest.mock.Mock(status=302)
        response.getheaders.return_value = [('Location','/blocked')]
        connection = unittest.mock.Mock()
        connection.getresponse.return_value = response
        with patch('mcp_seo_auditor.network.PinnedConnection',return_value=connection):
            with self.assertRaisesRegex(ValueError,'robots'):
                fetch('https://example.com/',allowed=lambda url: not url.endswith('/blocked'))
        self.assertEqual(connection.request.call_count,1)

    def test_node_wrapper(self):
        from pathlib import Path
        wrapper = Path(__file__).resolve().parents[1] / 'bin/mcp-seo-auditor.mjs'
        message = '\n'.join(map(json.dumps,[INIT,READY,{'jsonrpc':'2.0','id':7,'method':'tools/list'}]))+'\n'
        p = subprocess.run(['node',str(wrapper)],input=message,text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(p.stdout.splitlines()[-1])['id'],7)

    def test_validation(self):
        for value in (0,11,True,'5'):
            with self.assertRaises(ValueError): invoke('crawl_site',{'url':'https://example.com','max_pages':value})
        with self.assertRaises(ValueError): invoke('audit_html',{'html':'','unexpected':True})
    def test_protocol(self):
        session = Session()
        call = dict(jsonrpc='2.0',id=1,method='tools/list')
        self.assertEqual(session.dispatch(call)['error']['code'],-32002)
        self.assertEqual(session.dispatch(INIT)['result']['protocolVersion'],'2025-06-18')
        self.assertEqual(session.dispatch(call)['error']['code'],-32002)
        self.assertIsNone(session.dispatch(READY))
        self.assertEqual(len(session.dispatch(call)['result']['tools']),3)
        self.assertIn('error',session.dispatch(INIT))

    def test_invalid_requests_recover(self):
        session = Session()
        for value in (None,True,[],{},1.5):
            r = session.dispatch(dict(jsonrpc='2.0',id=value,method='ping'))
            self.assertEqual(r['error']['code'],-32600)
        malformed = dict(INIT,params={'protocolVersion':'2025-06-18'})
        self.assertEqual(session.dispatch(malformed)['error']['code'],-32602)
        self.assertEqual(session.phase,'new')
        session.dispatch(INIT); session.dispatch(READY)
        for params in ({'name':[]},{'name':'unknown'},{'name':'audit_html','arguments':[]}):
            self.assertEqual(session.dispatch(dict(jsonrpc='2.0',id=2,method='tools/call',params=params))['error']['code'],-32602)
        bad = session.dispatch(dict(jsonrpc='2.0',id=3,method='tools/call',params={'name':'audit_html','arguments':{'html':5}}))
        self.assertTrue(bad['result']['isError'])
        self.assertIn('result',session.dispatch(dict(jsonrpc='2.0',id=4,method='tools/list')))

    def test_stdio(self):
        messages = [INIT, READY, dict(jsonrpc='2.0',id=1,method='tools/list'),dict(jsonrpc='2.0',id=2,method='tools/call',params={'name':'audit_html','arguments':{'html':GOOD}})]
        p = subprocess.run([sys.executable,'-m','mcp_seo_auditor.server'],input='\n'.join(map(json.dumps,messages))+'\n',text=True,capture_output=True,check=True)
        responses = list(map(json.loads,p.stdout.splitlines()))[1:]
        self.assertEqual(len(responses[0]['result']['tools']),3)
        self.assertEqual(responses[1]['result']['structuredContent']['score'],100)
    def test_crawl_duplicates_and_limit(self):
        from urllib.robotparser import RobotFileParser
        robots = RobotFileParser(); robots.parse([])
        def report(url,*args):
            return {'url':url,'metadata':{'title':'Same','description':'Same'},'internalLinks':['https://example.com/a','https://other.com/a'],'http':{'status':200}}
        with patch('mcp_seo_auditor.server.robots_for',return_value=robots), patch('mcp_seo_auditor.server.audit_url',side_effect=report),patch('time.sleep'):
            r = crawl_site('https://example.com/',2)
        self.assertEqual(len(r['pages']),2)
        self.assertEqual(len(r['duplicates']),2)

if __name__ == '__main__': unittest.main()
