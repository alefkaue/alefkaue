#!/usr/bin/env python3
"""Pre-render the ASCII 'ghost' portrait as data for the boot hero.

A photo becomes a compact, monochrome ASCII portrait (density ramp) that
render_session.py draws on the RIGHT side of the boot session — next to the
whoami block, the same inline placement valthvn uses. The face rises out of
the dark and its eyes ignite; the brightest cell inside each eye box is found
automatically so the glow lands on the catchlight.

This is run locally, NOT in CI: it needs Pillow and a source image. It writes
data/ghost.json (grid + eye/pupil coordinates); render_session.py (standard
library only) reads that JSON, so the daily GitHub Action keeps the portrait
without Pillow or the source image.

Usage:
    GHOST_SRC=/path/to/portrait.jpg python scripts/make_ghost.py
    # PowerShell:  $env:GHOST_SRC="C:\\path\\portrait.jpg"; py scripts\\make_ghost.py

Env:
    GHOST_SRC    source image (default: source-ghost.png in the repo root)
    GHOST_COLS   portrait width in characters (default: 110)
"""
import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageFilter
except ImportError:
    sys.exit('Pillow is required: pip install Pillow')

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(os.environ.get('GHOST_SRC', ROOT / 'source-ghost.png'))
COLS = int(os.environ.get('GHOST_COLS', '110'))
OUT = ROOT / 'data/ghost.json'

RAMP = (" .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$")

# Eye search boxes as fractions of the grid (left, right): (c0,c1,r0,r1).
# Resolution-independent, so changing COLS keeps them on the eyes. Re-tune only
# if you swap to a differently framed source image.
EYE_FRAC = [(0.375, 0.568, 0.417, 0.625),
            (0.614, 0.818, 0.417, 0.646)]


def levels(v, lo, hi, gamma):
    v = (v - lo) / max(1, (hi - lo))
    return min(1.0, max(0.0, v)) ** gamma


def to_ascii(im, cols, lo=70, hi=240, gamma=1.18, blur=1.0):
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
    return [bx, by]


def main():
    if not SRC.exists():
        sys.exit(f'source image not found: {SRC}\n'
                 'set GHOST_SRC to a portrait, or drop source-ghost.png in the repo root.')
    lines, lum = to_ascii(Image.open(SRC), COLS)
    rows = len(lines)
    eyes = [[int(round(c0 * COLS)), int(round(c1 * COLS)),
             int(round(r0 * rows)), int(round(r1 * rows))]
            for (c0, c1, r0, r1) in EYE_FRAC]
    pupils = [brightest_cell(lum, box) for box in eyes]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {'cols': COLS, 'rows': rows, 'lines': lines, 'eyes': eyes, 'pupils': pupils},
        ensure_ascii=False, indent=0), encoding='utf-8')
    print(f'ghost grid {COLS}x{rows} from {SRC.name}; pupils {pupils} -> data/ghost.json')


if __name__ == '__main__':
    main()
