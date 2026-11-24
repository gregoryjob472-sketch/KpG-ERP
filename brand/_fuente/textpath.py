"""Convert text to SVG path data using HarfBuzz shaping (kerning, variable axes)."""
import os
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_cache = {}


def _font(path, variations):
    key = (path, tuple(sorted((variations or {}).items())))
    if key not in _cache:
        if not os.path.isabs(path):
            path = os.path.join(FONTS, path)
        blob = hb.Blob.from_file_path(path)
        face = hb.Face(blob)
        font = hb.Font(face)
        if variations:
            font.set_variations(variations)
        _cache[key] = (font, face.upem)
    return _cache[key]


def shape(path, text, size, variations=None, tracking=0.0, features=None, kern_adjust=None):
    """Return list of (gid, x, y) in font units plus total advance, upem.

    tracking: extra space per glyph in em units (e.g. 0.2 = 20% of em)
    kern_adjust: dict index->extra advance (em units) applied after glyph i
    """
    font, upem = _font(path, variations)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True})
    out = []
    x = 0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        out.append((info.codepoint, x + pos.x_offset, pos.y_offset))
        x += pos.x_advance
        if i < n - 1:
            x += tracking * upem
        if kern_adjust and i in kern_adjust:
            x += kern_adjust[i] * upem
    return font, upem, out, x


def text_path(path, text, size, x=0, y=0, variations=None, tracking=0.0,
              features=None, kern_adjust=None, anchor="start"):
    """Return (d, width, bbox) where y is the baseline in SVG coords."""
    font, upem, glyphs, adv = shape(path, text, size, variations, tracking, features, kern_adjust)
    s = size / upem
    width = adv * s
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(None)
    bpen = BoundsPen(None)
    for gid, gx, gy in glyphs:
        t = (s, 0, 0, -s, x + gx * s, y - gy * s)
        font.draw_glyph_with_pen(gid, TransformPen(pen, t))
        font.draw_glyph_with_pen(gid, TransformPen(bpen, t))
    return pen.getCommands(), width, bpen.bounds


def glyph_paths(path, text, size, x=0, y=0, variations=None, tracking=0.0,
                features=None, kern_adjust=None):
    """Return per-glyph list of (d, bbox) so letters can be styled separately."""
    font, upem, glyphs, adv = shape(path, text, size, variations, tracking, features, kern_adjust)
    s = size / upem
    res = []
    for gid, gx, gy in glyphs:
        pen = SVGPathPen(None)
        bpen = BoundsPen(None)
        t = (s, 0, 0, -s, x + gx * s, y - gy * s)
        font.draw_glyph_with_pen(gid, TransformPen(pen, t))
        font.draw_glyph_with_pen(gid, TransformPen(bpen, t))
        res.append((pen.getCommands(), bpen.bounds))
    return res, adv * s
