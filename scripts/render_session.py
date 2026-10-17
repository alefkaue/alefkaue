#!/usr/bin/env python3
"""An animated monochrome shell session for alefkaue, from public calendar data.

Adapted from valthvn's SESSION profile (monochrome terminal + contribution
candles). Standard library only; no external services or JavaScript.
"""
import datetime as dt
import html
import json
import math
import os
from html import escape
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/session'
USER = os.environ.get('GH_PROFILE_USER', 'alefkaue')

# (display label, repository name, number)
PROJECTS = [('mini-soc-analyzer', 'mini-soc-analyzer', '01'),
            ('pentest-ponto-cego', 'pentest-ponto-cego', '02'),
            ('estagios', 'estagios', '03')]

WORDMARK = 'ALEFKAUE'
TAGLINE = 'LEARNING SECURITY, ONE COMMIT AT A TIME.'
WHOAMI = [('user', 'Alef Santos / alefkaue'),
          ('role', 'Estudante de TI'),
          ('focus', 'Segurança da Informação & Dev'),
          ('mindset', 'Learn. Break. Defend.'),
          ('source', 'Open source. Always curious.')]
STACK = {
    "languages": ["Python", "Bash", "SQL"],
    "security": ["Linux", "Redes", "SIEM", "Pentest"],
    "dev": ["Git", "Docker", "APIs REST"],
    "learning": ["Blue Team", "Red Team", "Cloud"],
}


def rect(x, y, w, h, fill, stroke='#f0f0f0', sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def text(x, y, value, size=14, fill='#f0f0f0', weight=400, family='monospace'):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{html.escape(str(value))}</text>')


def svg(w, h, title, description, body):
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
              f'role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title>'
              f'<desc id="desc">{html.escape(description)}</desc>{body}</svg>\n')
    ET.fromstring(result)
    return result


def normalize_days(data):
    """A 365-day window ending at the last actual date, not the machine clock."""
    raw = data['days']
    if not raw:
        raise ValueError('Contribution data must contain days')
    lookup = {}
    for row in raw:
        date = dt.date.fromisoformat(row['date'])
        count = row['count']
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError('Contribution counts must be nonnegative integers')
        if date in lookup:
            raise ValueError('Duplicate contribution dates')
        lookup[date] = count
    end = max(lookup)
    start = end - dt.timedelta(days=364)
    return [{'date': start + dt.timedelta(days=i), 'count': lookup[start + dt.timedelta(days=i)]}
            for i in range(365)]


T = partial(text, fill='#f0f0f0')
R = partial(rect, stroke='none', sw=0)
STYLE = '''<style>
@keyframes type{0%{clip-path:inset(0 100% 0 0)}6%{clip-path:inset(0 0 0 0)}90%{clip-path:inset(0 0 0 0)}94%{clip-path:inset(0 100% 0 0)}100%{clip-path:inset(0 100% 0 0)}}
@keyframes enter{0%{opacity:0}6%{opacity:1}90%{opacity:1}94%{opacity:0}100%{opacity:0}}
@keyframes pop{from{opacity:0}to{opacity:1}}
@keyframes cursor{50%{opacity:0}}
.type{animation:type 18s linear infinite}
.output{animation:enter 18s linear infinite}
.pop{animation:pop .5s both}
.cursor{animation:cursor 1s step-end infinite}
@media(prefers-reduced-motion:reduce){.type,.output,.pop,.cursor{animation:none}.type{clip-path:inset(0 0 0 0)}.output,.pop{opacity:1}}
</style>'''


def reveal(body, delay, kind='output'):
    return f'<g class="{kind}" style="animation-delay:{delay}s">{body}</g>'


def shell(body, height, title, desc, animated=True):
    return svg(960, height, title, desc, (STYLE if animated else '') + body)


def hero():
    b = T(32, 35, '●  PUBLIC SESSION', 11) + T(733, 35, 'TTY / 001   UTF-8', 11)
    b += R(32, 53, 896, 1, '#393939')
    b += T(27, 142, WORDMARK, 100, weight=700, family='Arial,Helvetica,sans-serif')
    b += T(33, 177, TAGLINE, 12)
    b += reveal(T(34, 232, f'~ $ ssh {USER}@github', 16), 0, 'type')
    b += reveal(T(34, 262, 'Connection established. Welcome to my corner.', 12, fill='#b8b8b8'), 1.2)
    b += reveal(T(34, 310, '~ $ whoami --verbose', 16), 1.8, 'type')
    for i, (key, value) in enumerate(WHOAMI):
        b += reveal(T(34, 351 + i * 28, key, 12, fill='#969696') + T(135, 351 + i * 28, value, 12), 3 + i * .2)
    b += reveal(T(34, 525, '~ $ ./explore', 16), 4.6, 'type')
    b += reveal(T(34, 556, 'projects/      stack.json      activity.log', 13, fill='#b8b8b8'), 5.4)
    b += reveal(T(34, 596, '~ $', 16) + '<rect class="cursor" x="77" y="582" width="10" height="18" fill="#f0f0f0"/>', 5.8)
    b += R(32, 622, 896, 1, '#393939') + T(34, 650, 'END OF BOOT / YOUR NEXT COMMAND IS BELOW ↓', 11, fill='#969696')
    return shell(b, 676, f'{WORDMARK} — a living terminal session',
                 f'Animated connection and whoami sequence. {WHOAMI[0][1]} — {WHOAMI[1][1]}; '
                 f'{WHOAMI[2][1]}. Project links and an expandable stack follow.')


def project(label, repo, number):
    b = T(26, 32, number, 12, fill='#969696') + T(74, 33, 'cd ~/projects/' + repo, 17)
    b += T(74, 62, 'OPEN REPOSITORY', 10, fill='#969696') + T(895, 48, '↗', 26)
    b += R(26, 81, 908, 1, '#393939')
    return shell(b, 90, 'Open ' + label, 'Shell-style link to the ' + label + ' repository.', False)


def candles(days):
    result = []
    for i in range(len(days) - 90, len(days)):
        opening = sum(d['count'] for d in days[i - 7:i])
        closing = sum(d['count'] for d in days[i - 6:i + 1])
        result.append(dict(date=days[i]['date'], count=days[i]['count'], open=opening, close=closing,
                           high=max(opening, closing), low=min(opening, closing)))
    return result


def activity(data):
    days = normalize_days(data)
    series = candles(days)
    last = series[-1]
    total = sum(d['count'] for d in days)
    recent_total = sum(c['count'] for c in series)
    step = max(1, math.ceil(max(c['high'] for c in series) / 4))
    ceiling = step * 4
    peak_volume = max(1, max(c['count'] for c in series))

    def y(value):
        return 334 - 184 * value / ceiling
    b = T(32, 39, '~ $ git activity --candles', 17)
    b += T(32, 70, '1D / ROLLING 7D TOTAL / LAST 90 DAYS', 11, fill='#969696')
    b += T(32, 116, last['close'], 34, weight=700) + T(125, 113, 'CONTRIBUTIONS / LAST 7D', 11)
    b += T(550, 87, f'O {last["open"]}   H {last["high"]}   L {last["low"]}   C {last["close"]}', 12)
    b += T(550, 113, 'FILLED: UP / HOLLOW: DOWN / LINE: FLAT', 10, fill='#969696')
    for value in range(0, ceiling + 1, step):
        b += R(32, y(value), 830, 1, '#252525') + T(884, y(value) + 4, value, 10, fill='#969696')
    b += R(872, 141, 1, 290, '#393939')
    b += f'<path d="M32 {y(last["close"])} H872" fill="none" stroke="#b8b8b8" stroke-dasharray="3 5"/>'
    b += R(879, y(last['close']) - 10, 49, 20, '#f0f0f0') + T(886, y(last['close']) + 4, last['close'], 11, fill='#0b0b0b')
    b += T(32, 366, 'VOL / DAILY CONTRIBUTIONS', 10, fill='#969696')
    for i, c in enumerate(series):
        x = 36 + i * 9.2
        color = '#eeeeee' if c['close'] >= c['open'] else '#969696'
        top, bottom = y(c['high']), y(c['low'])
        body = f'<path d="M{x} {top} V{bottom}" stroke="{color}"/>'
        if c['open'] == c['close']:
            body += f'<path d="M{x-2.7} {top} H{x+2.7}" stroke="{color}"/>'
        else:
            body += rect(x - 2.7, top, 5.4, bottom - top, '#eeeeee' if c['close'] > c['open'] else 'none', color, 1)
        if c['count']:
            h = 46 * c['count'] / peak_volume
            body += R(x - 2.7, 425 - h, 5.4, h, color)
        attributes = ' '.join(f'data-{key}="{c[key]}"' for key in ('date', 'count', 'open', 'high', 'low', 'close'))
        body = (f'<g {attributes}><title>{c["date"]}: {c["count"]} contributions; rolling 7D O {c["open"]}, '
                f'H {c["high"]}, L {c["low"]}, C {c["close"]}</title>' + body + '</g>')
        b += reveal(body, i * .025, 'pop')
    for i in (0, 30, 60, 89):
        b += T(32 + i * 9.2 - (45 if i == 89 else 0), 450, str(series[i]['date']), 10, fill='#969696')
    b += R(32, 472, 896, 1, '#393939')
    b += T(32, 510, total, 30, weight=700) + T(145, 508, 'CONTRIBUTIONS / 365 DAYS', 11)
    b += T(505, 510, recent_total, 30, weight=700) + T(620, 508, 'CONTRIBUTIONS / 90 DAYS', 11)
    b += T(32, 546, 'PUBLIC CALENDAR SNAPSHOT / ' + data['generated_at'], 10, fill='#969696')
    return shell(b, 570, 'Real GitHub activity — monochrome contribution candles',
                 f'{total} contributions in 365 observed days; {recent_total} in the last 90. '
                 'Daily candles: open is the previous trailing seven-day total; close is the current total. '
                 'High and low are the larger and smaller endpoints, without invented intraday movement. '
                 'Filled bodies rise, hollow bodies fall, lines are flat. Volume is each day’s actual count.')


def picture(name, alt):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/session/{name}.svg">'
            f'<img src="./assets/session/{name}-light.svg" width="960" alt="{escape(alt, quote=True)}"></picture>')


def readme():
    links = '\n'.join(f'<a href="https://github.com/{USER}/{repo}">'
                      + picture('project-' + number, 'Open ' + label + ' repository') + '</a><br>'
                      for label, repo, number in PROJECTS)
    stack_json = json.dumps(STACK, indent=2, ensure_ascii=False)
    return ('<!-- ' + WORDMARK + ' / SESSION 001 -->\n\n'
            + picture('boot', f'{WORDMARK}. Animated monochrome terminal session. {WHOAMI[0][1]} — '
                      f'{WHOAMI[1][1]}; {WHOAMI[2][1]}. Learn. Break. Defend.') + '\n\n'
            # ghost.svg is a static, pre-rendered ASCII portrait (scripts/make_ghost.py);
            # it is not regenerated here, only referenced so this README keeps it.
            + picture('ghost', 'Animated ASCII portrait that emerges from the dark; its eyes '
                      'ignite and watch over the session.') + '\n\n'
            + links + '\n\n'
            '<details>\n<summary><code>~ $ cat stack.json</code></summary>\n\n'
            '```json\n' + stack_json + '\n```\n\n'
            '</details>\n\n<br>\n\n'
            + picture('activity', 'Monochrome GitHub contribution candles: 90 daily candles based on rolling '
                      'seven-day totals, actual daily volumes, and totals over 365 and 90 observed days. '
                      'Filled candles rise; hollow candles fall.') + '\n\n'
            '<details>\n<summary><code>~ $ help</code></summary>\n\n'
            '`projects/` — click a repository row above.  \n'
            '`stack.json` — expand the toolbox.  \n'
            '`activity.log` — real public contribution candles, refreshed daily.\n\n'
            '</details>\n')


def main():
    data = json.loads((ROOT / 'data/contributions.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {'boot': hero(), 'activity': activity(data)}
    assets.update((f'project-{p[2]}', project(*p)) for p in PROJECTS)
    for name, body in assets.items():
        (OUT / f'{name}.svg').write_text(body, encoding='utf-8')
        light = body
        for dark, lite in {'#f0f0f0': '#1f2328', '#eeeeee': '#1f2328', '#b8b8b8': '#59636e',
                           '#969696': '#59636e', '#393939': '#d1d9e0', '#252525': '#d8dee4',
                           '#0b0b0b': '#ffffff'}.items():
            light = light.replace(dark, lite)
        (OUT / f'{name}-light.svg').write_text(light, encoding='utf-8')
    (ROOT / 'README.md').write_text(readme(), encoding='utf-8')
    print('Rendered SESSION: animated boot, repository commands and real activity.')


if __name__ == '__main__':
    main()
