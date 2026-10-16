"""
Build a single animated SVG that cycles through N colored-ASCII artworks, each
rendered from a high-res emoji glyph. Reveal (top->bottom wipe) + show/hold/hide
is driven by CSS @keyframes (GitHub renders CSS keyframes inside <img> SVGs),
so the gallery loops forever on the profile with no JavaScript.

Usage: python build_cycle.py <out.svg>
"""
import html, os, sys, colorsys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ascii-cycle.svg")
USERNAME = os.environ.get("GH_PROFILE_USER", "alefkaue")
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

# (emoji, caption shown under the terminal title)
ARTS = [
    ("\U0001F43A", "wolf"),
    ("\U0001F434", "horse"),
    ("\U0001F981", "lion"),
    ("\U0001F42F", "tiger"),
    ("\U0001F409", "dragon"),
    ("\U0001F985", "eagle"),
    ("\U0001F480", "skull"),
    ("\U0001F916", "robot"),
    ("\U0001F47E", "invader"),
    ("\U0001F988", "shark"),
]

COLS, ROWS = 92, 48
CELL_W, CELL_H = 8.0, 15.0
FONT_SIZE = 13.2
RAMP = " .`:-=+*oe%#@&$"      # faint -> dense
ALPHA_THR = 60
QUANT = 26                    # color quantization bucket (smaller file)

PAD = 20
TITLEBAR_H = 34
STATUS_H = 30
ART_W = int(COLS * CELL_W)
ART_H = int(ROWS * CELL_H)
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK = "#7d8590", "#c9d1d9"

# ---- timing (one full loop) ----------------------------------------------
N = len(ARTS)
REVEAL = 1.3
HOLD = 3.1
FADE = 0.45
WINDOW = REVEAL + HOLD + FADE        # per-art
T = WINDOW * N                        # total loop seconds


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# cyber neon palette: deep blue -> blue -> cyan -> near white (dark->bright)
_NEON = [(0.0, (11, 42, 90)), (0.35, (31, 111, 235)),
         (0.70, (34, 211, 238)), (1.0, (214, 247, 255))]


def neon_ramp(lum):
    t = max(0.0, min(1.0, lum))
    for i in range(len(_NEON) - 1):
        t0, c0 = _NEON[i]
        t1, c1 = _NEON[i + 1]
        if t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            r, g, b = _lerp(c0, c1, f)
            return r / 255, g / 255, b / 255
    return _NEON[-1][1][0] / 255, _NEON[-1][1][1] / 255, _NEON[-1][1][2] / 255


def render_emoji_rgba(ch):
    """Render one emoji large + transparent, autocrop to its alpha bbox."""
    S = 480
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(EMOJI_FONT, 380)
    # center it
    bbox = d.textbbox((0, 0), ch, font=fnt, embedded_color=True)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((S - w) / 2 - bbox[0], (S - h) / 2 - bbox[1]), ch, font=fnt, embedded_color=True)
    a = img.split()[3]
    box = a.getbbox()
    if box:
        img = img.crop(box)
    return img


def fit_grid(img):
    """Fit cropped RGBA into COLS x ROWS honoring monospace cell aspect."""
    cw, chh = img.size
    # effective pixel aspect so a square subject looks square in 8x15 cells
    target_ratio = COLS / ROWS            # ~1.9
    subj_ratio = (cw / chh) * (CELL_H / CELL_W)
    if subj_ratio > target_ratio:
        new_cols = COLS
        new_rows = max(1, int(round(COLS / subj_ratio)))
    else:
        new_rows = ROWS
        new_cols = max(1, int(round(ROWS * subj_ratio)))
    small = img.resize((new_cols, new_rows), Image.LANCZOS)
    canvas = Image.new("RGBA", (COLS, ROWS), (0, 0, 0, 0))
    ox, oy = (COLS - new_cols) // 2, (ROWS - new_rows) // 2
    canvas.paste(small, (ox, oy))
    return canvas


def grid_rows(img):
    px = img.load()
    rows = []
    for y in range(ROWS):
        cells = []
        for x in range(COLS):
            r, g, b, a = px[x, y]
            if a < ALPHA_THR:
                cells.append(None)
                continue
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(1, min(len(RAMP) - 1, idx))   # never space inside subject
            ch = RAMP[idx]
            hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if ss < 0.18:
                # grayish emoji -> cyber neon gradient by luminance
                r2, g2, b2 = neon_ramp(lum)
            else:
                # colorful emoji -> keep hue, push saturation + brightness
                ss = min(1.0, ss * 1.7 + 0.08)
                vv = max(0.64, min(1.0, vv * 1.08))
                r2, g2, b2 = colorsys.hsv_to_rgb(hh, ss, vv)
            col = (int(r2 * 255) // QUANT * QUANT,
                   int(g2 * 255) // QUANT * QUANT,
                   int(b2 * 255) // QUANT * QUANT)
            col = tuple(min(255, c + QUANT // 2) for c in col)
            cells.append((ch, "#%02x%02x%02x" % col))
        rows.append(cells)
    return rows


def row_svg(cells, y):
    """One <text> per row; consecutive same-color cells share a <tspan>."""
    runs = []
    cur_col, cur_txt = None, []
    for cell in cells:
        if cell is None:
            ch, col = " ", cur_col
        else:
            ch, col = cell
        if col != cur_col and cur_txt:
            runs.append((cur_col, "".join(cur_txt)))
            cur_txt = []
        cur_col = col
        cur_txt.append(ch)
    if cur_txt:
        runs.append((cur_col, "".join(cur_txt)))
    inner = []
    for col, txt in runs:
        safe = html.escape(txt).replace(" ", "\u00a0")
        if col is None:
            inner.append(f'<tspan fill="none">{safe}</tspan>')
        else:
            inner.append(f'<tspan fill="{col}">{safe}</tspan>')
    return (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
            f'font-size="{FONT_SIZE}" letter-spacing="0">' + "".join(inner) + '</text>')


def pct(v):
    s = f"{v*100:.3f}".rstrip("0").rstrip(".")
    return s


def keyframes(i):
    a = i * WINDOW / T
    c = (i * WINDOW + REVEAL) / T
    bminus = ((i + 1) * WINDOW - FADE) / T
    b = (i + 1) * WINDOW / T
    name = f"k{i}"
    k = (f"@keyframes {name}{{"
         f"0%{{opacity:0;clip-path:inset(0 0 100% 0);}}"
         f"{pct(a)}%{{opacity:0;clip-path:inset(0 0 100% 0);}}"
         f"{pct(a)}%{{opacity:1;}}"
         f"{pct(c)}%{{opacity:1;clip-path:inset(0 0 0 0);}}"
         f"{pct(bminus)}%{{opacity:1;clip-path:inset(0 0 0 0);}}"
         f"{pct(b)}%{{opacity:0;clip-path:inset(0 0 0 0);}}"
         f"100%{{opacity:0;}}}}")
    return k


art_top = TITLEBAR_H + PAD * 0.4
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
]

# styles — clip-path drives hide/reveal (GitHub renders CSS @keyframes in <img>
# SVGs; clip-path animation hides inactive layers reliably, opacity alone does not).
css = [f".s{i}{{opacity:0;animation:k{i} {T:.1f}s linear infinite;}}" for i in range(N)]
parts.append("<style>" + "".join(keyframes(i) for i in range(N)) + "".join(css) + "</style>")

parts.append('<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             '</linearGradient></defs>')
parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2+4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{USERNAME.lower()}@github: ~$ ./ascii-gallery.sh</text>')

# slides
for i, (ch, name) in enumerate(ARTS):
    print(f"  rendering {name}...")
    img = fit_grid(render_emoji_rgba(ch))
    rows = grid_rows(img)
    g = [f'<g class="s{i}">']
    for ry, cells in enumerate(rows):
        y = art_top + ry * CELL_H + CELL_H * 0.76
        g.append(row_svg(cells, y))
    g.append('</g>')
    parts.append("".join(g))

# status bar + captions
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
prompt = f"{USERNAME.lower()}@github:~$ cat "
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">{prompt}</text>')
cap_x = PAD + int(len(prompt) * 8.0) + 8
for i, (ch, name) in enumerate(ARTS):
    parts.append(f'<text class="s{i}" x="{cap_x}" y="{status_y:.1f}" fill="{INK}" font-size="13">{name}.art</text>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {len(svg)} bytes; {CANVAS_W}x{CANVAS_H}; loop {T:.1f}s; {N} arts")


def static_svg(ch, name):
    img = fit_grid(render_emoji_rgba(ch))
    rows = grid_rows(img)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
         f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, Consolas, monospace">',
         f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="{BG}"/>',
         f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
         f'<text x="{PAD}" y="22" fill="{MUTED}" font-size="12">{name}.art</text>']
    for ry, cells in enumerate(rows):
        y = art_top + ry * CELL_H + CELL_H * 0.76
        p.append(row_svg(cells, y))
    p.append("</svg>")
    return "".join(p)


if os.environ.get("SHEET"):
    cards = []
    for ch, name in ARTS:
        cards.append(f'<div style="margin:6px">{static_svg(ch, name)}</div>')
    htmlout = ("<!doctype html><meta charset='utf-8'>"
               "<style>svg{width:372px;height:auto;display:block}</style>"
               "<body style='margin:0;background:#010409;display:flex;flex-wrap:wrap;'>"
               + "".join(cards) + "</body>")
    with open(os.path.join(HERE, "sheet.html"), "w", encoding="utf-8") as f:
        f.write(htmlout)
    print("wrote sheet.html")
