#!/usr/bin/env python3
"""
AdSense Audit Site Crawler
Usage: python3 crawl_site.py <domain>
Crawls key pages of a website and outputs plain-text content with word counts
for use in an AdSense compliance audit.
"""

import sys
import urllib.request
import urllib.error
from html.parser import HTMLParser
import time
import json

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'head', 'noscript'}
        self.skip_depth = 0
        self.current_skip_tag = None

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip_depth = max(0, self.skip_depth - 1)

    def handle_data(self, data):
        if self.skip_depth == 0:
            stripped = data.strip()
            if stripped and len(stripped) > 2:
                self.text_chunks.append(stripped)

    def get_text(self):
        return ' '.join(self.text_chunks)


def fetch_page(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AdSenseAuditBot/1.0)'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            parser = TextExtractor()
            parser.feed(html)
            text = parser.get_text()
            words = len(text.split())
            chars = len(text)
            return {'url': url, 'words': words, 'chars': chars, 'text': text[:3000], 'error': None}
    except Exception as e:
        return {'url': url, 'words': 0, 'chars': 0, 'text': '', 'error': str(e)}


def crawl_site(domain):
    if not domain.startswith('http'):
        domain = 'https://' + domain

    pages_to_check = [
        ('Home', '/'),
        ('About', '/about'),
        ('Blog Index', '/blog'),
        ('Contact', '/contact'),
        ('Privacy Policy', '/privacy-policy'),
        ('Terms', '/terms-and-conditions'),
        ('Shop', '/shop'),
        ('Labs', '/labs'),
    ]

    results = []
    for name, path in pages_to_check:
        url = domain.rstrip('/') + path
        print(f"Crawling {name}: {url}", file=sys.stderr)
        result = fetch_page(url)
        result['page_name'] = name
        results.append(result)
        time.sleep(0.5)

    return results


if __name__ == '__main__':
    domain = sys.argv[1] if len(sys.argv) > 1 else 'example.com'
    results = crawl_site(domain)
    for r in results:
        print(f"\n{'='*60}")
        print(f"PAGE: {r['page_name']} ({r['url']})")
        if r['error']:
            print(f"ERROR: {r['error']}")
        else:
            print(f"Words: {r['words']} | Chars: {r['chars']}")
            print(f"Preview: {r['text'][:500]}")
