#!/usr/bin/env python3
"""Fetch public GitHub contribution cells without a token or third-party service.

Fail on missing or unrecognised counts rather than silently treating them as zero.
The old snapshot stays intact when the request or parsing fails.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = os.environ.get('GH_PROFILE_USER', 'valthvn')
OUT_PATH = ROOT / 'data/contributions.json'


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = []
        self.tooltips = {}
        self.tooltip_id = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('td', 'rect') and attrs.get('data-date'):
            self.cells.append(attrs)
        if tag == 'tool-tip':
            self.tooltip_id = attrs.get('for')
            self.parts = []

    def handle_data(self, value):
        if self.tooltip_id is not None:
            self.parts.append(value)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tooltip_id is not None:
            self.tooltips[self.tooltip_id] = ' '.join(self.parts).strip()
            self.tooltip_id = None
            self.parts = []


def parse_days(document, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    parser = CalendarParser()
    parser.feed(document)
    days = {}
    for cell in parser.cells:
        date = dt.date.fromisoformat(cell['data-date'])
        if date > today:
            continue
        if date in days:
            raise ValueError(f'Duplicate calendar cell for {date}')
        tooltip = parser.tooltips.get(cell.get('id')) or cell.get('aria-label', '')
        if cell.get('data-count') is not None:
            count = int(cell['data-count'])
        elif re.match(r'^\s*no contributions\b', tooltip, re.I):
            count = 0
        else:
            match = re.match(r'^\s*([\d,]+)\s+contributions?\b', tooltip, re.I)
            if not match:
                raise ValueError(f'Missing or unrecognised contribution count for {date}')
            count = int(match[1].replace(',', ''))
        if count < 0:
            raise ValueError(f'Negative contribution count for {date}')
        days[date] = count
    if len(days) < 365:
        raise ValueError(f'Incomplete GitHub calendar ({len(days)} observed days; need 365)')
    end = max(days)
    if end < today - dt.timedelta(days=1):
        raise ValueError(f'Stale GitHub calendar: last observed day is {end}')
    start = end - dt.timedelta(days=364)
    observed = []
    for i in range(365):
        date = start + dt.timedelta(days=i)
        if date not in days:
            raise ValueError(f'Missing calendar date: {date}')
        observed.append({'date': date.isoformat(), 'count': days[date]})
    return observed


def fetch_days():
    url = f'https://github.com/users/{USERNAME}/contributions'
    request = Request(url, headers={'User-Agent': 'valthvn-profile-observatory/1.0', 'Accept-Language': 'en-US,en;q=0.9'})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                document = response.read().decode('utf-8')
            return parse_days(document)
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError('Contribution fetch failed')


def compute_current_streak(days):
    if not days:
        return 0, None, None
    idx = len(days) - 1
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if days[idx]['date'] == today and days[idx]['count'] == 0:
        idx -= 1
    end_idx = idx
    while idx >= 0 and days[idx]['count'] > 0:
        idx -= 1
    length = end_idx - idx
    return (length, days[idx+1]['date'], days[end_idx]['date']) if length else (0, None, None)


def compute_longest_streak(days):
    longest = run = 0
    start = longest_start = longest_end = None
    for row in days:
        if row['count']:
            if not run:
                start = row['date']
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, start, row['date']
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    if not days:
        raise ValueError('Empty contribution calendar')
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    best = max(days, key=lambda row: row['count'])
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)
    monthly = {}
    for row in days:
        month = row['date'][:7]
        monthly[month] = monthly.get(month, 0) + row['count']
    return {
        'username': USERNAME,
        'generated_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'range': {'start': days[0]['date'], 'end': days[-1]['date']},
        'total_contributions': total,
        'active_days': active,
        'avg_per_active_day': round(total/active, 1) if active else 0,
        'current_streak': {'length': cur_len, 'start': cur_start, 'end': cur_end},
        'longest_streak': {'length': long_len, 'start': long_start, 'end': long_end},
        'best_day': {'date': best['date'], 'count': best['count']},
        'monthly': [{'month': k, 'total': v} for k, v in sorted(monthly.items())],
        'days': days,
    }


if __name__ == '__main__':
    data = build_data(fetch_days())
    OUT_PATH.parent.mkdir(exist_ok=True)
    temporary = OUT_PATH.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    temporary.replace(OUT_PATH)
    print(f'Fetched {len(data["days"])} days / {data["total_contributions"]} contributions.')
