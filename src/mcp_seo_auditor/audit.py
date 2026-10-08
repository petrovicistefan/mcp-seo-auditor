"""Deterministic static HTML checks. Findings are heuristics, not ranking predictions."""
import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag

MAX_HTML = 2_000_000

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles, self.headings, self.images, self.links = [], [], [], []
        self.meta, self.canonicals, self.schemas = {}, [], []
        self.lang, self.base = '', None
        self.capture, self.parts, self.depth = None, [], 0
        self.hidden = 0
        self.words = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang', '') or ''
        if tag == 'base' and self.base is None: self.base = a.get('href')
        if tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            self.meta.setdefault(key, []).append(a.get('content', '') or '')
        if tag == 'link' and 'canonical' in (a.get('rel') or '').lower().split():
            self.canonicals.append(a.get('href', '') or '')
        if tag == 'img': self.images.append(a)
        if tag == 'a': self.links.append(a.get('href', '') or '')
        if tag in ('script', 'style'): self.hidden += 1
        if tag == 'title' or tag in ('h1','h2','h3','h4','h5','h6') or (tag == 'script' and (a.get('type') or '').lower() == 'application/ld+json'):
            self.capture, self.parts = tag, []

    def handle_endtag(self, tag):
        if self.capture == tag:
            value = ''.join(self.parts).strip()
            if tag == 'title': self.titles.append(value)
            elif tag == 'script': self.schemas.append(value)
            else: self.headings.append({'level': int(tag[1]), 'text': value})
            self.capture = None
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if self.capture: self.parts.append(data)
        if not self.hidden: self.words.extend(data.split())

def audit_html(html, url='https://example.com/', headers=None):
    if not isinstance(html, str) or len(html.encode('utf-8')) > MAX_HTML:
        raise ValueError('HTML must be a string of at most 2 MB')
    p = Page(); p.feed(html); p.close()
    findings = []
    def add(code, severity, evidence, recommendation):
        findings.append(dict(code=code, severity=severity, evidence=evidence, recommendation=recommendation))
    title = p.titles[0] if p.titles else ''
    description = p.meta.get('description', [''])[0]
    if not title: add('missing_title', 'error', 'No nonempty title', 'Add a descriptive, unique title in head.')
    if len(p.titles) > 1: add('multiple_titles', 'warning', len(p.titles), 'Keep one title element.')
    if title and (len(title) < 15 or len(title) > 65): add('title_length', 'info', len(title), 'Review readability and likely truncation; no fixed Google character limit applies.')
    if not description: add('missing_description', 'warning', 'No description', 'Write a useful, page-specific meta description.')
    if len(p.meta.get('description', [])) > 1: add('multiple_descriptions','warning',len(p.meta['description']),'Keep one meta description.')
    h1 = [h for h in p.headings if h['level'] == 1]
    if not h1: add('missing_h1','warning','No H1','Add a clear main heading when appropriate.')
    if len(h1) > 1: add('multiple_h1','info',len(h1),'Review heading structure; multiple H1s are not automatically a ranking penalty.')
    if not p.lang: add('missing_lang','info','No html lang','Declare the document language for accessibility.')
    if not p.canonicals: add('missing_canonical','info','No HTML canonical','Consider a canonical where duplicate URLs exist; an HTTP canonical may also be valid.')
    if len(p.canonicals) > 1: add('multiple_canonicals','warning',p.canonicals,'Use one consistent canonical target.')
    for c in p.canonicals:
        if not c or urlsplit(urljoin(url, c)).scheme not in ('https','http'):
            add('invalid_canonical','error',c,'Use a valid HTTP(S) canonical URL.')
    robots = ','.join(p.meta.get('robots', []) + p.meta.get('googlebot', []) + [str((headers or {}).get('x-robots-tag',''))]).lower()
    if 'noindex' in robots or 'none' in robots.replace(',', ' ').split():
        add('noindex','warning',robots,'Confirm exclusion from indexing is intentional; do not remove for private pages.')
    missing_alt = sum('alt' not in i for i in p.images)
    if missing_alt: add('missing_alt','warning',missing_alt,'Add descriptive alt to informative images; use empty alt for decorative images.')
    valid_schemas = 0
    for s in p.schemas:
        try:
            data = json.loads(s)
            if not isinstance(data, (dict,list)): raise ValueError('Expected object or array')
            valid_schemas += 1
        except (ValueError, TypeError): add('invalid_json_ld','warning',s[:120],'Fix JSON-LD syntax; semantic/schema eligibility needs separate validation.')
    base = urljoin(url, p.base) if p.base else url
    links = sorted({urldefrag(urljoin(base,h))[0] for h in p.links if h and urlsplit(urljoin(base,h)).scheme in ('http','https')})
    internal = [l for l in links if urlsplit(l).netloc == urlsplit(url).netloc]
    if not p.meta.get('viewport'): add('missing_viewport','info','No viewport metadata','Check responsive behavior and add viewport metadata if appropriate.')
    penalties = {'error': 20, 'warning': 8, 'info': 2}
    score = max(0, 100 - sum(penalties[f['severity']] for f in findings))
    return {'url':url, 'score':score, 'scoreMeaning':'Heuristic technical checklist score, not ranking or traffic prediction',
            'metadata':{'title':title, 'description':description, 'canonical':p.canonicals, 'lang':p.lang, 'robots':robots},
            'headings':p.headings, 'images':{'total':len(p.images),'missingAlt':missing_alt},
            'structuredData':{'blocks':len(p.schemas),'validJsonBlocks':valid_schemas,'semanticValidation':False},
            'wordCount':len(p.words), 'internalLinks':internal[:200], 'externalLinkCount':len(links)-len(internal),
            'findings':sorted(findings,key=lambda f: {'error':0,'warning':1,'info':2}[f['severity']]),
            'limitations':['Static HTML only; JavaScript is not executed.','No ranking, backlinks, Core Web Vitals, or Google index verification.','Link targets are not checked for HTTP status.']}
