#!/usr/bin/env python3
"""update_fetcher.py

Fetches BBC Technology RSS feed, extracts title/link/summary/date and image (if available).
Downloads images into public/images/ and writes public/articles.json.

Designed to run in GitHub Actions or any server environment with internet.
"""
import os, re, json, sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = 'http://feeds.bbci.co.uk/news/technology/rss.xml'
MAX_ITEMS = 30
OUT_DIR = 'public'
IMAGES_DIR = os.path.join(OUT_DIR, 'images')

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def fetch_url(url, timeout=20):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print('Fetch failed', url, e, file=sys.stderr)
        return None

def extract_image(item):
    # Try media:content or enclosure first
    for media in item.findall('.//{http://search.yahoo.com/mrss/}content'):
        if 'url' in media.attrib:
            return media.attrib.get('url')
    enc = item.find('enclosure')
    if enc is not None and 'url' in enc.attrib:
        return enc.attrib.get('url')
    # fallback: look in description/html
    desc = item.findtext('description') or ''
    m = re.search(r'<img[^>]+src=[\'\"]([^\'\"]+)', desc)
    if m:
        return m.group(1)
    return None

def parse_feed(url):
    raw = fetch_url(url)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except Exception as e:
        print('XML parse failed', e, file=sys.stderr)
        return []
    items = []
    for item in root.findall('.//item')[:MAX_ITEMS]:
        title = item.findtext('title') or ''
        link = item.findtext('link') or ''
        pub = item.findtext('pubDate') or ''
        summary = item.findtext('description') or ''
        img = extract_image(item)
        # strip html tags from summary
        summary = re.sub('<[^<]+?>', '', summary)[:400].strip()
        items.append({'title': title.strip(), 'link': link.strip(), 'date': pub.strip(), 'summary': summary, 'image': img, 'source': 'BBC Technology'})
    return items

def safe_filename(url):
    if not url: return None
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name:
        name = parsed.netloc.replace('.', '_')
    name = re.sub(r'[^0-9A-Za-z._-]', '_', name)
    return name

def download_image(url):
    if not url: return None
    try:
        data = fetch_url(url)
        if not data: return None
        name = safe_filename(url)
        path = os.path.join(IMAGES_DIR, name)
        with open(path, 'wb') as f:
            f.write(data)
        return 'images/' + name
    except Exception as e:
        print('Image download failed', url, e, file=sys.stderr)
        return None

def main():
    print('Fetching BBC Tech feed...')
    items = parse_feed(FEED_URL)
    # sort by date best-effort (not all dates parse cleanly)
    def parsed_date(s):
        try:
            return datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %Z')
        except Exception:
            try:
                return datetime.fromisoformat(s)
            except Exception:
                return datetime.min
    items.sort(key=lambda x: parsed_date(x.get('date','')), reverse=True)
    items = items[:MAX_ITEMS]
    # download images
    for it in items:
        img = it.get('image')
        if img:
            local = download_image(img)
            if local:
                it['image_local'] = local
    out = os.path.join(OUT_DIR, 'articles.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print('Wrote', out, 'with', len(items), 'items.')

if __name__ == '__main__':
    main()
