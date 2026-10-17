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
PROJECTS = [('SSH Watch / SOC detection', 'ssh-watch', '01'),
            ('Integrity Guard / file monitoring', 'integrity-guard', '02'),
            ('IAM Policy Lens / cloud review', 'iam-policy-lens', '03')]

PROJECT_SUMMARIES = {
    'ssh-watch': 'SOC / SSH failure bursts and login correlation / tested CLI',
    'integrity-guard': 'BLUE TEAM / SHA-256 baselines and file change detection',
    'iam-policy-lens': 'CLOUD SECURITY / offline IAM policy review and evidence',
}

WORDMARK = 'ALEFKAUE'
TAGLINE = 'BREAK IT. UNDERSTAND IT. DEFEND IT.'
WHOAMI = [('user', 'Alef Santos / alefkaue'),
          ('role', 'Cybersecurity Student'),
          ('focus', 'Blue Team · SOC · Pentest'),
          ('mindset', 'Learn. Break. Defend.'),
          ('source', 'Open source. Always curious.')]
STACK = {
    "security": ["Linux", "Networking", "SIEM", "Pentest", "OSINT"],
    "tooling": ["Nmap", "Wireshark", "Burp Suite"],
    "languages": ["Python", "Bash", "SQL"],
    "frameworks": ["Flask", "REST APIs"],
    "dev": ["Git", "Docker"],
    "learning": ["Blue Team", "Red Team", "Cloud Security"],
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
@keyframes grow{0%{clip-path:inset(0 100% 0 0)}12%{clip-path:inset(0 100% 0 0)}44%{clip-path:inset(0 0 0 0)}100%{clip-path:inset(0 0 0 0)}}
.type{animation:type 18s linear infinite}
.output{animation:enter 18s linear infinite}
.pop{animation:pop .5s both}
.grow{animation:grow 18s linear infinite}
.cursor{animation:cursor 1s step-end infinite}
@media(prefers-reduced-motion:reduce){.type,.output,.pop,.grow,.cursor{animation:none}.type,.grow{clip-path:inset(0 0 0 0)}.output,.pop{opacity:1}}
</style>'''


def reveal(body, delay, kind='output'):
    return f'<g class="{kind}" style="animation-delay:{delay}s">{body}</g>'


def shell(body, height, title, desc, animated=True):
    return svg(960, height, title, desc, (STYLE if animated else '') + body)


# The ASCII portrait grid is pre-rendered by scripts/make_ghost.py (Pillow) into
# data/ghost.json; here it is only placed and animated — so the daily CI render
# needs no image and no Pillow. It sits on the right of the hero, rises out of
# the dark, and its eyes ignite (glow on the auto-detected catchlights).
GHOST = ROOT / 'data/ghost.json'
GHOST_STYLE = ('<style>'
    '@keyframes gface{0%{opacity:0;clip-path:inset(0 0 100% 0)}'
    '100%{opacity:.92;clip-path:inset(0 0 0 0)}}'
    '@keyframes ggaze{0%{opacity:0}35%{opacity:0}55%{opacity:1}78%{opacity:.5}100%{opacity:1}}'
    '.gface{opacity:.92;animation:gface 2s ease-out 1.8s both}'
    '.geyes{opacity:0;animation:ggaze 6s ease-in-out 2.6s infinite}'
    '@media(prefers-reduced-motion:reduce){.gface{animation:none;opacity:.92;clip-path:none}'
    '.geyes{animation:none;opacity:1}}</style>')
GHOST_DEFS = ('<defs>'
    '<filter id="gg" x="-40%" y="-40%" width="180%" height="180%">'
    '<feGaussianBlur stdDeviation="0.8"/></filter>'
    '<filter id="gg2" x="-300%" y="-300%" width="700%" height="700%">'
    '<feGaussianBlur stdDeviation="1.7"/></filter></defs>')


def ghost_portrait():
    if not GHOST.exists():
        return ''
    g = json.loads(GHOST.read_text(encoding='utf-8'))
    lines, cols = g['lines'], g['cols']
    rows = len(lines)
    width = 345.0
    adv = width / cols
    fs = adv / 0.55
    lh = adv * 2.0
    x0 = 928 - cols * adv
    y0 = 445 - rows * lh / 2
    mono = 'font-family="monospace"'

    def block(sub, sx, sy, fill, ncols):
        tl = ncols * adv
        out = []
        for i, row in enumerate(sub):
            out.append(f'<text x="{sx:.1f}" y="{sy + i * lh:.2f}" {mono} font-size="{fs:.2f}" '
                       f'fill="{fill}" textLength="{tl:.1f}" lengthAdjust="spacing" '
                       f'xml:space="preserve">{html.escape(row)}</text>')
        return ''.join(out)

    face = f'<g class="gface">{block(lines, x0, y0, "#f0f0f0", cols)}</g>'
    halo = ''
    for c0, c1, r0, r1 in g['eyes']:
        sub = [row[c0:c1] for row in lines[r0:r1]]
        halo += block(sub, x0 + c0 * adv, y0 + r0 * lh, '#ffffff', c1 - c0)
    halo = f'<g class="geyes" filter="url(#gg)">{halo}</g>'
    orbs = ''.join(f'<circle cx="{x0 + pc * adv:.1f}" cy="{y0 + pr * lh - fs * 0.35:.1f}" '
                   f'r="{adv * 1.8:.1f}" fill="#ffffff"/>' for pc, pr in g['pupils'])
    orbs = f'<g class="geyes" filter="url(#gg2)">{orbs}</g>'
    return GHOST_DEFS + GHOST_STYLE + face + halo + orbs


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
    b += ghost_portrait()
    b += R(32, 622, 896, 1, '#393939') + T(34, 650, 'END OF BOOT / YOUR NEXT COMMAND IS BELOW ↓', 11, fill='#969696')
    return shell(b, 676, f'{WORDMARK} — a living terminal session',
                 f'Animated connection and whoami sequence. {WHOAMI[0][1]} — {WHOAMI[1][1]}; '
                 f'{WHOAMI[2][1]}. Project links and an expandable stack follow.')


def projects_header():
    b = T(32, 39, '~ $ ls ~/projects', 17)
    b += T(32, 70, '# FEATURED · DETECTION / INTEGRITY / CLOUD SECURITY', 11, fill='#969696')
    b += R(32, 86, 896, 1, '#393939')
    return shell(b, 100, 'Featured projects', 'Featured security projects: detection, integrity and cloud security.', False)


def project(label, repo, number):
    b = T(26, 32, number, 12, fill='#969696') + T(74, 33, 'cd ~/projects/' + repo, 17)
    b += T(74, 62, PROJECT_SUMMARIES.get(repo, 'OPEN REPOSITORY'), 10, fill='#969696') + T(895, 48, '↗', 26)
    b += R(26, 81, 908, 1, '#393939')
    return shell(b, 90, 'Open ' + label, 'Shell-style link to the ' + label + ' repository.', False)


def project_more():
    b = T(30, 33, '→', 16, fill='#969696') + T(74, 33, 'open portfolio.md', 17)
    b += T(74, 62, 'FULL CYBERSECURITY CATALOG & DEMOS', 10, fill='#969696') + T(895, 48, '↗', 26)
    b += R(26, 81, 908, 1, '#393939')
    return shell(b, 90, 'Open portfolio catalog',
                 'Shell-style link to the full cybersecurity portfolio catalog and demos.', False)


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


def languages():
    """A monochrome byte-share bar of the top languages across public repos."""
    data = json.loads((ROOT / 'data/languages.json').read_text(encoding='utf-8'))
    rows = data['languages']
    bar_x, bar_w, y0, rh = 176, 592, 112, 44
    b = T(32, 39, '~ $ git languages --top', 17)
    b += T(32, 70, f'BYTE SHARE / {data["repos_counted"]} PUBLIC REPOS / FORKS EXCLUDED', 11, fill='#969696')
    b += R(32, 86, 896, 1, '#393939')
    for i, r in enumerate(rows):
        y = y0 + i * rh
        b += T(32, y + 5, r['name'], 14)
        b += R(bar_x, y - 9, bar_w, 16, '#252525')
        fill = max(3.0, bar_w * r['pct'] / 100)
        b += (f'<rect class="grow" style="animation-delay:{0.3 + i * 0.18:.2f}s" '
              f'x="{bar_x}" y="{y - 9}" width="{fill:.1f}" height="16" fill="#f0f0f0"/>')
        b += T(bar_x + bar_w + 18, y + 5, f'{r["pct"]}%', 13)
    height = y0 + len(rows) * rh + 16
    summary = ', '.join(f'{r["name"]} {r["pct"]}%' for r in rows)
    return shell(b, height, f'{USER} — language byte share across public repositories',
                 f'Monochrome bars of the top languages by bytes across {data["repos_counted"]} '
                 f'public, non-fork repositories: {summary}.')


def stack_block():
    """A visible, monochrome toolkit — skills the byte-share bar can't show."""
    order = [('SECURITY', 'security'), ('TOOLING', 'tooling'), ('LANGUAGES', 'languages'),
             ('FRAMEWORKS', 'frameworks'), ('DEV', 'dev'), ('LEARNING', 'learning')]
    rows = [(name, STACK[key]) for name, key in order if STACK.get(key)]
    b = T(32, 39, '~ $ ./stack --list', 17)
    b += T(32, 70, '# TOOLKIT / SKILLS BEYOND THE BYTE COUNT', 11, fill='#969696')
    b += R(32, 86, 896, 1, '#393939')
    y0, rh = 126, 34
    for i, (name, items) in enumerate(rows):
        y = y0 + i * rh
        line = T(32, y, f'[ {name} ]', 13) + T(214, y, ' · '.join(items), 13, fill='#b8b8b8')
        b += reveal(line, 0.2 + i * 0.12, 'pop')
    height = y0 + (len(rows) - 1) * rh + 28
    return shell(b, height, 'Security toolkit and skills',
                 'Toolkit and skills — ' + '; '.join(f'{n}: {", ".join(it)}' for n, it in rows) + '.')


def picture(name, alt):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/session/{name}.svg">'
            f'<img src="./assets/session/{name}-light.svg" width="960" alt="{escape(alt, quote=True)}"></picture>')


def readme():
    links = '\n'.join(f'<a href="https://github.com/{USER}/{repo}">'
                      + picture('project-' + number, 'Open ' + label + ' repository') + '</a><br>'
                      for label, repo, number in PROJECTS)
    return ('<!-- ' + WORDMARK + ' / SESSION 001 -->\n\n'
            + picture('boot', f'{WORDMARK}. Animated monochrome terminal session. {WHOAMI[0][1]} — '
                      f'{WHOAMI[1][1]}; {WHOAMI[2][1]}. Learn. Break. Defend. An ASCII portrait '
                      'rises on the right and its eyes ignite.') + '\n\n'
            + picture('projects-head', 'Featured security projects: detection, integrity and cloud security.') + '\n\n'
            + links + '\n\n'
            + '<a href="./PORTFOLIO.md">'
            + picture('projects-more', 'Open the full cybersecurity portfolio catalog and demos.')
            + '</a>\n\n'
            + picture('stack', 'Security toolkit and skills across security, tooling, languages, '
                      'frameworks, dev and learning — the skills a byte-share bar cannot show.') + '\n\n'
            + picture('languages', 'Monochrome bars of the top languages by byte share across public, '
                      'non-fork repositories, refreshed daily.') + '\n\n'
            + picture('activity', 'Monochrome GitHub contribution candles: 90 daily candles based on rolling '
                      'seven-day totals, actual daily volumes, and totals over 365 and 90 observed days. '
                      'Filled candles rise; hollow candles fall.') + '\n\n'
            '<details>\n<summary><code>~ $ help</code></summary>\n\n'
            '`projects/` — click a repository row above.  \n'
            '`./stack` — security toolkit and skills.  \n'
            '`languages` — real byte share across public repos, refreshed daily.  \n'
            '`activity.log` — real public contribution candles, refreshed daily.\n\n'
            '</details>\n')


def main():
    data = json.loads((ROOT / 'data/contributions.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {'boot': hero(), 'activity': activity(data), 'stack': stack_block(),
              'projects-head': projects_header(), 'projects-more': project_more()}
    if (ROOT / 'data/languages.json').exists():
        assets['languages'] = languages()
    assets.update((f'project-{p[2]}', project(*p)) for p in PROJECTS)
    for name, body in assets.items():
        (OUT / f'{name}.svg').write_text(body, encoding='utf-8')
        light = body
        for dark, lite in {'#f0f0f0': '#1f2328', '#eeeeee': '#1f2328', '#ffffff': '#1f2328',
                           '#b8b8b8': '#59636e', '#969696': '#59636e', '#393939': '#d1d9e0',
                           '#252525': '#d8dee4', '#0b0b0b': '#ffffff'}.items():
            light = light.replace(dark, lite)
        (OUT / f'{name}-light.svg').write_text(light, encoding='utf-8')
    (ROOT / 'README.md').write_text(readme(), encoding='utf-8')
    print('Rendered SESSION: animated boot, repository commands and real activity.')


if __name__ == '__main__':
    main()
