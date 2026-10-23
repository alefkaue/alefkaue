#!/usr/bin/env python3
"""Aggregate language bytes across the user's public repos -> data/languages.json.

Mirrors fetch_contributions.py: standard library only, real public data. Uses
GITHUB_TOKEN when present (5000 req/h in CI); works unauthenticated too (60/h).
Forks are skipped so the breakdown reflects the user's own code. The previous
snapshot is kept intact if the fetch fails or returns nothing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.environ.get('GH_PROFILE_USER', 'alefkaue')
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
OUT_PATH = ROOT / 'data/languages.json'
FOCUS = ('Python', 'TypeScript', 'JavaScript', 'Java', 'C#', 'C++')


def api(url):
    headers = {'User-Agent': 'alefkaue-profile-session/1.0',
               'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28'}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    request = Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode('utf-8')), response.headers
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError(f'request failed: {url}')


def list_repos():
    repos, page = [], 1
    while True:
        batch, _ = api(f'https://api.github.com/users/{USERNAME}/repos'
                       f'?per_page=100&type=owner&sort=pushed&page={page}')
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos if not r.get('fork') and not r.get('archived')]


def aggregate(repos):
    totals, counted = {}, 0
    for repo in repos:
        langs, _ = api(repo['languages_url'])
        if langs:
            counted += 1
        for name, byte_count in langs.items():
            totals[name] = totals.get(name, 0) + int(byte_count)
    return totals, counted


def build(totals, counted):
    grand = sum(totals.values())
    if grand <= 0:
        raise ValueError('no language bytes found')
    ordered = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    # Editorial selection affects labels only, never the byte counts or denominator.
    top = [(name, count) for name, count in ordered if name in FOCUS]
    rows = [{'name': n, 'bytes': b, 'pct': round(100 * b / grand, 1)} for n, b in top]
    other = sum(b for name, b in ordered if name not in FOCUS)
    if other > 0:
        rows.append({'name': 'Other', 'bytes': other, 'pct': round(100 * other / grand, 1)})
    return {
        'username': USERNAME,
        'generated_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'repos_counted': counted,
        'total_bytes': grand,
        'selection': 'Selected languages; remaining languages are grouped as Other. Not a proficiency score.',
        'all_languages': dict(ordered),
        'languages': rows,
    }


if __name__ == '__main__':
    data = build(*aggregate(list_repos()))
    OUT_PATH.parent.mkdir(exist_ok=True)
    tmp = OUT_PATH.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    tmp.replace(OUT_PATH)
    top = ', '.join(f'{r["name"]} {r["pct"]}%' for r in data['languages'])
    print(f'Languages across {data["repos_counted"]} repos: {top}')
