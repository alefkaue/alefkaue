#!/usr/bin/env python3
"""Pre-render the animated ASCII 'ghost' portrait (assets/session/ghost*.svg).

A photo is turned into a dense, monochrome ASCII portrait (70-level ramp). The
face rises out of the dark and its eyes ignite and breathe — the brightest cell
inside each eye box is found automatically so the glow lands on the catchlight.

This is run locally, NOT in CI: it needs Pillow and a source image, while the
daily GitHub Action (scripts/render_session.py) is standard-library only and
only refreshes the contribution activity. The resulting ghost.svg /
ghost-light.svg are committed as static assets; render_session.py references
them from the README so the daily regeneration keeps the portrait in place.

Usage:
    GHOST_SRC=/path/to/portrait.jpg python scripts/make_ghost.py
    # PowerShell:  $env:GHOST_SRC="C:\\path\\portrait.jpg"; py scripts\\make_ghost.py

Env:
    GHOST_SRC   source image path (default: source-ghost.png in the repo root)
"""
import html
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageFilter
except ImportError:
    sys.exit('Pillow is required: pip install Pillow')

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/session'
SRC = Path(os.environ.get('GHOST_SRC', ROOT / 'source-ghost.png'))

COLS = 176
# Eye search boxes (c0, c1, r0, r1) in the COLS-wide grid; the glow is placed on
# the brightest cell inside each. Tuned for the committed portrait — re-check
# these if you swap the source image (scripts/_ghost_ruler helper not included).
EYE_BOXES = [(66, 100, 20, 30), (108, 144, 20, 31)]

RAMP = (" .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$")
MONO = "font-family=\"'Consolas','SFMono-Regular','Menlo',monospace\""

STYLE = ('<style>'
    '@keyframes rise{0%{opacity:0;clip-path:inset(0 0 100% 0)}'
    '28%{opacity:.9;clip-path:inset(0 0 0 0)}100%{opacity:.9;clip-path:inset(0 0 0 0)}}'
    '@keyframes gaze{0%{opacity:0}30%{opacity:0}45%{opacity:1}70%{opacity:.55}'
    '85%{opacity:1}100%{opacity:.8}}'
    '@keyframes flick{0%,97%,100%{opacity:.9}98%{opacity:.7}99%{opacity:1}}'
    '@keyframes cur{50%{opacity:0}}'
    '@keyframes once{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}'
    '.face{animation:rise 7s ease-out infinite}'
    '.eyes{animation:gaze 7s ease-in-out infinite}'
    '.cmd{animation:once 1.2s ease-out both}'
    '.cur{animation:cur 1s step-end infinite}'
    '@media(prefers-reduced-motion:reduce){'
    '.face{animation:none;opacity:.9;clip-path:none}'
    '.eyes{animation:none;opacity:1}.cmd{animation:none;clip-path:none}.cur{animation:none}}'
    '</style>')


def levels(v, lo, hi, gamma):
    v = (v - lo) / max(1, (hi - lo))
    return min(1.0, max(0.0, v)) ** gamma


def to_ascii(im, cols=COLS, lo=54, hi=236, gamma=0.95, blur=0.9):
    im = im.convert('L').filter(ImageFilter.GaussianBlur(blur))
    im = ImageOps.autocontrast(im, cutoff=1)
    w, h = im.size
    rows = max(1, round(cols * (h / w) * 0.5))
    small = im.resize((cols, rows), Image.LANCZOS)
    px = small.load()
    lines, lum = [], []
    for y in range(rows):
        lines.append(''.join(
            RAMP[min(len(RAMP) - 1, int(levels(px[x, y], lo, hi, gamma) * len(RAMP)))]
            for x in range(cols)))
        lum.append([px[x, y] for x in range(cols)])
    return lines, lum


def brightest_cell(lum, box):
    c0, c1, r0, r1 = box
    best, bx, by = -1, (c0 + c1) // 2, (r0 + r1) // 2
    for r in range(r0, r1):
        for c in range(c0, c1):
            if lum[r][c] > best:
                best, bx, by = lum[r][c], c, r
    return bx, by


def rowtext(lines, x0, y0, adv, lh, fs, fill, cols, cls='', style=''):
    c = f' class="{cls}"' if cls else ''
    s = f' style="{style}"' if style else ''
    tl = cols * adv
    out = []
    for i, row in enumerate(lines):
        y = y0 + i * lh
        out.append(f'<text{c}{s} x="{x0:.1f}" y="{y:.2f}" {MONO} font-size="{fs:.2f}" '
                   f'fill="{fill}" textLength="{tl:.1f}" lengthAdjust="spacing" '
                   f'xml:space="preserve">{html.escape(row)}</text>')
    return ''.join(out)


def build(lines, lum, dark):
    cols, rows = len(lines[0]), len(lines)
    pupils = [brightest_cell(lum, b) for b in EYE_BOXES]
    fg, dim, line, bg, glow = (('#f6f6f6', '#8f8f8f', '#393939', '#0b0b0b', '#ffffff')
                               if dark else ('#1f2328', '#59636e', '#d1d9e0', '#ffffff', '#1f2328'))
    W = 960
    adv = 900.0 / cols
    fs = adv / 0.55
    lh = adv * 2.0
    x0 = (W - cols * adv) / 2
    top = 108
    header = (f'<text x="34" y="34" {MONO} font-size="12" fill="{dim}">'
              f'&#9679;  ENCRYPTED PORTRAIT</text>'
              f'<text x="770" y="34" {MONO} font-size="12" fill="{dim}">TTY / GHOST  UTF-8</text>'
              f'<rect x="34" y="50" width="892" height="1" fill="{line}"/>'
              f'<text class="cmd" x="34" y="84" {MONO} font-size="15" fill="{fg}">'
              f'~ $ ./summon --ghost</text>')
    face = rowtext(lines, x0, top, adv, lh, fs, fg, cols, cls='face')
    eyes_svg = ''
    for (c0, c1, r0, r1) in EYE_BOXES:
        sub = [row[c0:c1] for row in lines[r0:r1]]
        eyes_svg += rowtext(sub, x0 + c0 * adv, top + r0 * lh, adv, lh, fs, glow,
                            c1 - c0, cls='eyes', style='filter:url(#g)')
    orbs = ''
    for (pc, pr) in pupils:
        cx = x0 + pc * adv
        cy = top + pr * lh - fs * 0.35
        orbs += (f'<circle class="eyes" cx="{cx:.1f}" cy="{cy:.1f}" r="{adv*1.6:.1f}" '
                 f'fill="{glow}" filter="url(#g2)"/>')
    defs = ('<defs>'
            '<filter id="g" x="-40%" y="-40%" width="180%" height="180%">'
            '<feGaussianBlur stdDeviation="1.1"/></filter>'
            '<filter id="g2" x="-200%" y="-200%" width="500%" height="500%">'
            '<feGaussianBlur stdDeviation="3.2"/></filter></defs>')
    H = int(top + rows * lh + 26)
    inner = (STYLE + defs + f'<rect width="{W}" height="{H}" fill="{bg}"/>' + header
             + '<g class="flick" style="animation:flick 7s linear infinite">' + face + '</g>'
             + eyes_svg + orbs
             + f'<rect class="cur" x="34" y="92" width="{adv:.1f}" height="{fs:.1f}" fill="{fg}"/>')
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-label="Animated ASCII portrait that '
           f'emerges from the dark; its eyes ignite and watch.">{inner}</svg>\n')
    ET.fromstring(out)
    return out


def main():
    if not SRC.exists():
        sys.exit(f'source image not found: {SRC}\n'
                 'set GHOST_SRC to a portrait, or drop source-ghost.png in the repo root.')
    lines, lum = to_ascii(Image.open(SRC))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'ghost.svg').write_text(build(lines, lum, dark=True), encoding='utf-8')
    (OUT / 'ghost-light.svg').write_text(build(lines, lum, dark=False), encoding='utf-8')
    print(f'ghost portrait rendered from {SRC.name} '
          f'({len(lines[0])}x{len(lines)} chars) -> assets/session/ghost*.svg')


if __name__ == '__main__':
    main()
