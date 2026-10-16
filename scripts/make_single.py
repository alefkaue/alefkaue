"""
Render ONE emoji as a single large animated colored-ASCII SVG:
- one-shot top->bottom reveal (SMIL clip height),
- a looping cyber scanline sweeping down,
- a blinking status cursor.
SMIL is used throughout (GitHub renders SMIL inside <img> SVGs reliably).

Usage: python make_single.py <emoji> <name> <out.svg>
"""
import html, os, sys, colorsys
from PIL import Image, ImageDraw, ImageFont

CH = sys.argv[1] if len(sys.argv) > 1 else "\U0001F47E"
NAME = sys.argv[2] if len(sys.argv) > 2 else "invader"
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "ascii-invader.svg")
USERNAME = os.environ.get("GH_PROFILE_USER", "alefkaue")
EMOJI_FONT = r"C:\Windows\Fonts\seguiemj.ttf"

COLS, ROWS = 100, 52
CELL_W, CELL_H = 8.0, 15.0
FONT_SIZE = 13.2
RAMP = " .`:-=+*oe%#@&$"
ALPHA_THR = 60
QUANT = 24

PAD = 20
TITLEBAR_H = 34
STATUS_H = 30
ART_W = int(COLS * CELL_W)
ART_H = int(ROWS * CELL_H)
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK, SCAN = "#7d8590", "#c9d1d9", "#22d3ee"

_NEON = [(0.0, (11, 42, 90)), (0.35, (31, 111, 235)), (0.70, (34, 211, 238)), (1.0, (214, 247, 255))]


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def neon_ramp(lum):
    t = max(0.0, min(1.0, lum))
    for i in range(len(_NEON) - 1):
        t0, c0 = _NEON[i]
        t1, c1 = _NEON[i + 1]
        if t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            r, g, b = _lerp(c0, c1, f)
            return r / 255, g / 255, b / 255
    c = _NEON[-1][1]
    return c[0] / 255, c[1] / 255, c[2] / 255


def render_emoji_rgba(ch):
    S = 480
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(EMOJI_FONT, 380)
    bbox = d.textbbox((0, 0), ch, font=fnt, embedded_color=True)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((S - w) / 2 - bbox[0], (S - h) / 2 - bbox[1]), ch, font=fnt, embedded_color=True)
    box = img.split()[3].getbbox()
    return img.crop(box) if box else img


def fit_grid(img):
    cw, chh = img.size
    target = COLS / ROWS
    subj = (cw / chh) * (CELL_H / CELL_W)
    if subj > target:
        nc, nr = COLS, max(1, int(round(COLS / subj)))
    else:
        nr, nc = ROWS, max(1, int(round(ROWS * subj)))
    small = img.resize((nc, nr), Image.LANCZOS)
    canvas = Image.new("RGBA", (COLS, ROWS), (0, 0, 0, 0))
    canvas.paste(small, ((COLS - nc) // 2, (ROWS - nr) // 2))
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
            idx = max(1, min(len(RAMP) - 1, int((1.0 - lum) * (len(RAMP) - 1) + 0.5)))
            ch = RAMP[idx]
            hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if ss < 0.18:
                r2, g2, b2 = neon_ramp(lum)
            else:
                ss = min(1.0, ss * 1.7 + 0.08)
                vv = max(0.64, min(1.0, vv * 1.08))
                r2, g2, b2 = colorsys.hsv_to_rgb(hh, ss, vv)
            col = tuple(min(255, (int(c * 255) // QUANT * QUANT) + QUANT // 2) for c in (r2, g2, b2))
            cells.append((ch, "#%02x%02x%02x" % col))
        rows.append(cells)
    return rows


def row_svg(cells, y):
    runs = []
    cur_col, cur_txt = None, []
    for cell in cells:
        ch, col = (" ", cur_col) if cell is None else cell
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
        inner.append(f'<tspan fill="{col if col else "none"}">{safe}</tspan>')
    return (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" font-size="{FONT_SIZE}" '
            f'letter-spacing="0">' + "".join(inner) + '</text>')


art_top = TITLEBAR_H + PAD * 0.4
rows = grid_rows(fit_grid(render_emoji_rgba(CH)))

p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
     f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
     '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
     f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
     f'<clipPath id="rv"><rect x="{PAD}" y="{art_top:.1f}" width="{ART_W}" height="0">'
     f'<animate attributeName="height" from="0" to="{ART_H}" begin="0.3s" dur="1.6s" fill="freeze"/>'
     f'</rect></clipPath></defs>',
     f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
     f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
     f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>']
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    p.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
p.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2+4}" fill="{MUTED}" font-size="12" '
         f'text-anchor="middle">{USERNAME.lower()}@github: ~$ ./{NAME}.sh</text>')

# art (clipped reveal) + cursor riding the reveal edge
p.append('<g clip-path="url(#rv)">')
for ry, cells in enumerate(rows):
    p.append(row_svg(cells, art_top + ry * CELL_H + CELL_H * 0.76))
p.append('</g>')

# scanline sweeping down (loops), begins after reveal
p.append(f'<rect x="{PAD}" y="{art_top:.1f}" width="{ART_W}" height="10" fill="{SCAN}" opacity="0.14">'
         f'<animate attributeName="y" from="{art_top:.1f}" to="{art_top+ART_H-10:.1f}" '
         f'begin="1.9s" dur="2.8s" repeatCount="indefinite"/></rect>')

# status bar
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
p.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
prompt = f"{USERNAME.lower()}@github:~$ cat {NAME}.art "
p.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">'
         f'{USERNAME.lower()}@github:~$ cat <tspan fill="{INK}">{NAME}.art</tspan></text>')
cur_x = PAD + int(len(prompt) * 7.8)
p.append(f'<rect x="{cur_x}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
         f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
         f'dur="1s" repeatCount="indefinite"/></rect>')

p.append("</svg>")
svg = "".join(p)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {len(svg)} bytes; {CANVAS_W}x{CANVAS_H}")
