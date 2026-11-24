"""Generate the KpG brand logo set as pure-path SVGs (no font dependencies)."""
import os, re
from textpath import text_path, glyph_paths, _font, shape
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen

OUT = os.environ.get("OUT", "out")
os.makedirs(OUT, exist_ok=True)

INK = "#0E2A47"      # Azul tinta
BRASS = "#A8864F"    # Latón
BRASS_L = "#C9AC78"  # Latón claro (sobre fondo oscuro)
PAPER = "#F6F7F9"    # Blanco papel (frío)
WHITE = "#FFFFFF"

SERIF = ("Newsreader[opsz,wght].ttf", {"opsz": 72, "wght": 500})
SANS = ("InstrumentSans[wdth,wght].ttf", {"wght": 500, "wdth": 100})
DESC = "CONTADORES Y ASESORES"


class SegPen(BasePen):
    """Flatten outlines into line segments (for stem/rule intersection)."""
    def __init__(self):
        super().__init__(None); self.segs = []; self.cur = None; self.start = None
    def _moveTo(self, p): self.cur = self.start = p
    def _lineTo(self, p): self.segs.append((self.cur, p)); self.cur = p
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur; N = 24
        for i in range(1, N + 1):
            t = i / N; mt = 1 - t
            x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
            y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
            self._lineTo((x, y))
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur; N = 24
        for i in range(1, N + 1):
            t = i / N; mt = 1 - t
            self._lineTo((mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0], mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]))
    def _closePath(self):
        if self.cur != self.start: self._lineTo(self.start)


def stem_span(size, x, base, y, kern):
    """x-extent of the 'p' outline at height y (SVG coords)."""
    font, upem, glyphs, _ = shape(SERIF[0], "KpG", size, SERIF[1], 0, None, kern)
    s = size / upem
    gid, gx, gy = glyphs[1]
    pen = SegPen()
    font.draw_glyph_with_pen(gid, TransformPen(pen, (s, 0, 0, -s, x + gx*s, base - gy*s)))
    xs = []
    for (x0, y0), (x1, y1) in pen.segs:
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return min(xs), max(xs)


def wordmark(size=200, x=0, base=0, text="KpG", tw=0.020, gw=0.030, cutw=0.028):
    """KpG + double rule crossed by the p descender (cuenta T).
    Returns dict with path data for letters and rules plus geometry."""
    kern = {0: -0.010, 1: -0.004}
    gl, _ = glyph_paths(SERIF[0], text, size, x, base, SERIF[1], kern_adjust=kern)
    left = gl[0][1][0]; right = gl[-1][1][2]
    top = min(b[1] for _, b in gl)
    desc = gl[1][1][3] if len(gl) > 1 else gl[0][1][3]
    t = size * tw           # rule thickness
    gap = size * gw         # space between the two rules
    y1 = base + size * 0.075
    y2 = y1 + t + gap
    cut = size * cutw       # breathing room around the stem
    rules = []
    if text == "KpG":
        a0, a1 = stem_span(size, x, base, y1, kern)
        b0, b1 = stem_span(size, x, base, y2 + t, kern)
        sx0 = min(a0, b0) - cut; sx1 = max(a1, b1) + cut
        for yy in (y1, y2):
            rules.append((left, yy, sx0 - left, t))
            rules.append((sx1, yy, right - sx1, t))
    else:
        right = gl[-1][1][2]
        for yy in (y1, y2):
            rules.append((left, yy, right - left, t))
        desc = y2 + t
    letters = " ".join(d for d, _ in gl)
    if text != "KpG":
        desc = y2 + t
    return dict(letters=letters, rules=rules, left=left, right=right, top=top,
                desc=desc, base=base, y2=y2 + t, size=size)


def rects(rs, fill):
    return "".join(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"/>' for x, y, w, h in rs)


def svg(w, h, body, title, vb_x=0, vb_y=0, bg=None):
    bgr = f'<rect x="{vb_x}" y="{vb_y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:.2f} {vb_y:.2f} {w:.2f} {h:.2f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{title}"><title>{title}</title>{bgr}{body}</svg>\n')


def stacked(ink, accent, bg=None, desc_fill=None, name="", pad=None):
    wm = wordmark(200, 0, 0)
    cx = (wm["left"] + wm["right"]) / 2
    dsize = wm["size"] * 0.092
    ty = wm["desc"] + dsize * 2.9
    dd, dw, db = text_path(SANS[0], DESC, dsize, cx, ty, SANS[1], tracking=0.30, anchor="middle")
    # optically center: tracking adds trailing space only between glyphs, so anchor=middle is exact
    body = (f'<path d="{wm["letters"]}" fill="{ink}"/>' + rects(wm["rules"], accent) +
            f'<path d="{dd}" fill="{desc_fill or ink}"/>')
    x0 = min(wm["left"], db[0]); x1 = max(wm["right"], db[2])
    y0 = wm["top"]; y1 = db[3]
    p = pad if pad is not None else (x1 - x0) * 0.10
    return svg(x1 - x0 + 2*p, y1 - y0 + 2*p, body, name, x0 - p, y0 - p, bg), wm


def horizontal(ink, accent, bg=None, desc_fill=None, name="", pad=None):
    wm = wordmark(200, 0, 0)
    capH = wm["base"] - wm["top"]
    div_x = wm["right"] + wm["size"] * 0.20
    dsize = wm["size"] * 0.105
    lx = div_x + wm["size"] * 0.20
    # two descriptor lines, vertically centered on the cap height
    l1, l2 = "CONTADORES", "Y ASESORES"
    lead = dsize * 1.75
    mid = (wm["top"] + wm["y2"]) / 2
    capD = dsize * 0.70
    y1 = mid - lead / 2 + capD / 2
    y2 = y1 + lead
    d1, w1, b1 = text_path(SANS[0], l1, dsize, lx, y1, SANS[1], tracking=0.30)
    d2, w2, b2 = text_path(SANS[0], l2, dsize, lx, y2, SANS[1], tracking=0.30)
    body = (f'<path d="{wm["letters"]}" fill="{ink}"/>' + rects(wm["rules"], accent) +
            f'<rect x="{div_x:.2f}" y="{wm["top"]:.2f}" width="{wm["size"]*0.012:.2f}" height="{wm["y2"]-wm["top"]:.2f}" fill="{accent}"/>' +
            f'<path d="{d1} {d2}" fill="{desc_fill or ink}"/>')
    x0 = wm["left"]; x1 = max(b1[2], b2[2])
    y0 = wm["top"]; yb = wm["desc"]
    p = pad if pad is not None else (yb - y0) * 0.30
    return svg(x1 - x0 + 2*p, yb - y0 + 2*p, body, name, x0 - p, y0 - p, bg)


def isotipo(tile, ink_on, accent, name, radius=0.0, wm_scale=0.64, text="KpG", tw=0.028, gw=0.036, cutw=0.032):
    """Square monogram: KpG + cuenta-T rule on a solid tile."""
    S = 512
    wm = wordmark(200, 0, 0, text, tw, gw, cutw)
    w = wm["right"] - wm["left"]; h = wm["desc"] - wm["top"]
    k = S * wm_scale / w
    cx = (wm["left"] + wm["right"]) / 2; cy = (wm["top"] + wm["desc"]) / 2
    tx = S/2 - cx*k; ty = S/2 - cy*k
    r = S * radius
    body = (f'<rect width="{S}" height="{S}" rx="{r:.1f}" fill="{tile}"/>'
            f'<g transform="translate({tx:.2f},{ty:.2f}) scale({k:.5f})">'
            f'<path d="{wm["letters"]}" fill="{ink_on}"/>' + rects(wm["rules"], accent) + '</g>')
    return svg(S, S, body, name)


def wordmark_only(ink, accent, name, pad_ratio=0.08):
    """KpG + cuenta-T double rule, no descriptor: for small sizes and app bars."""
    wm = wordmark(200, 0, 0)
    body = f'<path d="{wm["letters"]}" fill="{ink}"/>' + rects(wm["rules"], accent)
    x0, x1, y0, y1 = wm["left"], wm["right"], wm["top"], wm["desc"]
    p = (x1 - x0) * pad_ratio
    return svg(x1 - x0 + 2*p, y1 - y0 + 2*p, body, name, x0 - p, y0 - p)


def write(fn, s):
    open(os.path.join(OUT, fn), "w").write(s)


T = "KpG y Asesores SpA"
s, WM = stacked(INK, BRASS, name=T); write("kpg-logo.svg", s)
s, _ = stacked(PAPER, BRASS_L, name=T); write("kpg-logo-inverso.svg", s)
s, _ = stacked(INK, INK, name=T); write("kpg-logo-mono-azul.svg", s)
s, _ = stacked("#111111", "#111111", name=T); write("kpg-logo-mono-negro.svg", s)
s, _ = stacked(WHITE, WHITE, name=T); write("kpg-logo-mono-blanco.svg", s)
write("kpg-logo-horizontal.svg", horizontal(INK, BRASS, name=T))
write("kpg-logo-horizontal-inverso.svg", horizontal(PAPER, BRASS_L, name=T))
write("kpg-wordmark.svg", wordmark_only(INK, BRASS, T))
write("kpg-wordmark-inverso.svg", wordmark_only(PAPER, BRASS_L, T))
write("kpg-isotipo.svg", isotipo(INK, PAPER, BRASS_L, T))
write("kpg-isotipo-claro.svg", isotipo("#EEF1F5", INK, BRASS, T))
write("kpg-app-icon.svg", isotipo(INK, PAPER, BRASS_L, T, radius=0.18, wm_scale=0.80, tw=0.034, gw=0.042, cutw=0.036))
write("favicon.svg", isotipo(INK, PAPER, BRASS_L, T, radius=0.14, wm_scale=0.60, text="K", tw=0.052, gw=0.048))
print("ok", sorted(os.listdir(OUT)))
