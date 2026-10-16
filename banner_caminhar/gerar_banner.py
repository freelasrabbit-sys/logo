#!/usr/bin/env python3
"""Banner Colégio Caminhar 5 x 1 m — vetor puro, textos em curvas, camadas.

Gera:
  banner_caminhar_5x1m.pdf  (CMYK, camadas PDF/OCG — abre no CorelDRAW e Illustrator)
  banner_caminhar_5x1m.svg  (camadas Inkscape/Corel, RGB)
  preview.png
Uso: python3 gerar_banner.py [pasta_fontes]
"""
import math, os, random, sys, zlib, subprocess, urllib.request
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "build", "fonts")
W, H = 5000.0, 1000.0  # mm

# ---------------------------------------------------------------- fontes
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    from fontTools.varLib.instancer import instantiateVariableFont
    jobs = [("Fredoka-Bold.ttf", "fredoka/Fredoka%5Bwdth,wght%5D.ttf", {"wdth": 100, "wght": 700}),
            ("Fredoka-CondBold.ttf", "fredoka/Fredoka%5Bwdth,wght%5D.ttf", {"wdth": 85, "wght": 700}),
            ("Nunito-Black.ttf", "nunito/Nunito%5Bwght%5D.ttf", {"wght": 900}),
            ("Baloo2-ExtraBold.ttf", "baloo2/Baloo2%5Bwght%5D.ttf", {"wght": 800}),
            ("Itim-Regular.ttf", "itim/Itim-Regular.ttf", None)]
    for out, src, w in jobs:
        p = os.path.join(FONT_DIR, out)
        if os.path.exists(p):
            continue
        tmp = p + ".src"
        urllib.request.urlretrieve(GF + src, tmp)
        f = TTFont(tmp)
        if w:
            instantiateVariableFont(f, w, inplace=True)
        f.save(p); os.remove(tmp)

# ---------------------------------------------------------------- cores (CMYK p/ PDF, RGB p/ SVG)
COL = {
    "creme":    ((0, .02, .08, 0), "#FBF7EC"),
    "azul":     ((1, .78, 0, .02), "#1D4E9E"),
    "azul2":    ((.85, .55, 0, 0), "#2F6DB8"),
    "amarelo":  ((0, .12, .95, 0), "#FBD21A"),
    "branco":   ((0, 0, 0, 0), "#FFFFFF"),
    "verde":    ((.75, 0, 1, 0), "#2BB741"),
}

# ---------------------------------------------------------------- geometria
def mat_mul(a, b):
    return (a[0]*b[0]+a[2]*b[1], a[1]*b[0]+a[3]*b[1], a[0]*b[2]+a[2]*b[3],
            a[1]*b[2]+a[3]*b[3], a[0]*b[4]+a[2]*b[5]+a[4], a[1]*b[4]+a[3]*b[5]+a[5])
def rot(deg, cx=0, cy=0):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return mat_mul((1, 0, 0, 1, cx, cy), mat_mul((c, s, -s, c, 0, 0), (1, 0, 0, 1, -cx, -cy)))
def tx(m, p):
    return (m[0]*p[0]+m[2]*p[1]+m[4], m[1]*p[0]+m[3]*p[1]+m[5])
def xform(ops, m):
    return [(o[0],) + tuple(tx(m, p) for p in o[1:]) for o in ops]

K = 0.5522847498
def arc(cx, cy, r, a0, a1, move=True):
    ops = []
    n = max(1, int(math.ceil(abs(a1 - a0) / 90)))
    step = (a1 - a0) / n
    for i in range(n):
        t0, t1 = math.radians(a0 + i*step), math.radians(a0 + (i+1)*step)
        k = 4/3*math.tan((t1-t0)/4)
        p0 = (cx+r*math.cos(t0), cy+r*math.sin(t0)); p3 = (cx+r*math.cos(t1), cy+r*math.sin(t1))
        p1 = (p0[0]-k*r*math.sin(t0), p0[1]+k*r*math.cos(t0))
        p2 = (p3[0]+k*r*math.sin(t1), p3[1]-k*r*math.cos(t1))
        if i == 0:
            ops.append(("M" if move else "L", p0))
        ops.append(("C", p1, p2, p3))
    return ops
def circle(cx, cy, r, ccw=False):
    o = arc(cx, cy, r, 0, -360 if ccw else 360); o.append(("Z",)); return o
def rrect(x, y, w, h, r):
    r = min(r, w/2, h/2)
    o = arc(x+w-r, y+r, r, -90, 0)
    o += arc(x+w-r, y+h-r, r, 0, 90, False)
    o += arc(x+r, y+h-r, r, 90, 180, False)
    o += arc(x+r, y+r, r, 180, 270, False)
    o.append(("Z",)); return o
def poly(pts, close=True):
    o = [("M", pts[0])] + [("L", p) for p in pts[1:]]
    if close: o.append(("Z",))
    return o
def smooth(pts, closed=True, t=1.0):
    """Catmull-Rom -> Bézier."""
    n = len(pts); o = [("M", pts[0])]
    rng = range(n) if closed else range(n-1)
    for i in rng:
        p0 = pts[(i-1) % n] if closed or i > 0 else pts[0]
        p1, p2 = pts[i], pts[(i+1) % n]
        p3 = pts[(i+2) % n] if closed or i+2 < n else pts[-1]
        c1 = (p1[0]+(p2[0]-p0[0])*t/6, p1[1]+(p2[1]-p0[1])*t/6)
        c2 = (p2[0]-(p3[0]-p1[0])*t/6, p2[1]-(p3[1]-p1[1])*t/6)
        o.append(("C", c1, c2, p2))
    if closed: o.append(("Z",))
    return o
def bbox(ops):
    xs = [p[0] for o in ops for p in o[1:]]; ys = [p[1] for o in ops for p in o[1:]]
    return min(xs), min(ys), max(xs), max(ys)

# ---------------------------------------------------------------- texto -> curvas
class OpsPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.ops = []
    def _moveTo(self, p): self.ops.append(("M", p))
    def _lineTo(self, p): self.ops.append(("L", p))
    def _curveToOne(self, a, b, c): self.ops.append(("C", a, b, c))
    def _qCurveToOne(self, a, b):
        p0 = self._getCurrentPoint()
        self.ops.append(("C", (p0[0]+2/3*(a[0]-p0[0]), p0[1]+2/3*(a[1]-p0[1])),
                         (b[0]+2/3*(a[0]-b[0]), b[1]+2/3*(a[1]-b[1])), b))
    def _closePath(self): self.ops.append(("Z",))
    _endPath = _closePath

FONTS = {}
def font(name):
    if name not in FONTS:
        p = os.path.join(FONT_DIR, name)
        blob = hb.Blob.from_file_path(p)
        f = hb.Font(hb.Face(blob))
        tt = TTFont(p)
        FONTS[name] = (f, tt, tt.getGlyphSet(), tt["head"].unitsPerEm, tt.getGlyphOrder())
    return FONTS[name]

def text(fname, s, size, x, y, anchor="middle", track=0.0, width=None, cap=None, feats=None):
    """Retorna contornos do texto (mm). size = corpo em mm; width força largura;
    cap = altura de maiúscula desejada (mm). track em fração do corpo."""
    f, tt, gs, upem, order = font(fname)
    if cap:
        size = cap / (tt["OS/2"].sCapHeight / upem)
    buf = hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(f, buf, dict({"kern": True, "liga": True}, **(feats or {})))
    glyphs = []; pen_x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append((order[info.codepoint], pen_x + pos.x_offset, pos.y_offset))
        pen_x += pos.x_advance + track*upem
    adv = pen_x - track*upem
    sx = size / upem
    if width:
        sx = width / adv; size = sx * upem
    total = adv * sx
    x0 = {"start": x, "middle": x - total/2, "end": x - total}[anchor]
    ops = []
    for g, gx, gy in glyphs:
        pen = OpsPen(gs); gs[g].draw(pen)
        m = (sx, 0, 0, -sx, x0 + gx*sx, y - gy*sx)
        ops += xform(pen.ops, m)
    return ops, total, size

# ---------------------------------------------------------------- documento
class Doc:
    def __init__(self): self.layers = []
    def layer(self, name):
        self.layers.append((name, [])); return self.layers[-1][1]
def fill(L, ops, col, evenodd=False):
    L.append({"t": "f", "ops": ops, "c": col, "eo": evenodd})
def stroke(L, ops, col, w, dash=None):
    L.append({"t": "s", "ops": ops, "c": col, "w": w, "dash": dash})

# ---------------------------------------------------------------- elementos
def brush(x0, y0, x1, y1, seed, amp=7):
    """Faixa de pincel com pontas irregulares."""
    rnd = random.Random(seed); pts = []
    h = y1 - y0; n = 14
    for i in range(n+1):
        pts.append((x0 + (x1-x0)*i/n + rnd.uniform(-8, 8), y0 + rnd.uniform(-amp, amp)))
    for k in range(5):  # ponta direita
        pts.append((x1 + rnd.uniform(5, 30) - k*6, y0 + h*(k+1)/6 + rnd.uniform(-4, 4)))
    for i in range(n, -1, -1):
        pts.append((x0 + (x1-x0)*i/n + rnd.uniform(-8, 8) - h*0.15, y1 + rnd.uniform(-amp, amp)))
    for k in range(5):  # ponta esquerda
        pts.append((x0 - rnd.uniform(5, 30) - h*0.15 + k*h*0.03, y1 - h*(k+1)/6 + rnd.uniform(-4, 4)))
    return smooth(pts, t=0.8)

def star(cx, cy, R, ri, rot_deg, round_=0.28):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i*36 + rot_deg); r = R if i % 2 == 0 else ri
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    o = []
    for i in range(10):
        p, q, nx = pts[i-1], pts[i], pts[(i+1) % 10]
        rr = round_ if i % 2 == 0 else round_*0.6
        a = (q[0]+(p[0]-q[0])*rr, q[1]+(p[1]-q[1])*rr)
        b = (q[0]+(nx[0]-q[0])*rr, q[1]+(nx[1]-q[1])*rr)
        o.append(("M" if i == 0 else "L", a))
        o.append(("C", ((a[0]+2*q[0])/3, (a[1]+2*q[1])/3), ((b[0]+2*q[0])/3, (b[1]+2*q[1])/3), b))
    o.append(("Z",)); return o

def sparks(L, cx, cy, angles, r1, r2, col, w):
    for a in angles:
        t = math.radians(a)
        stroke(L, poly([(cx+r1*math.cos(t), cy+r1*math.sin(t)), (cx+r2*math.cos(t), cy+r2*math.sin(t))], False), col, w)

def pin(cx, top, h):
    """Marcador de mapa (gota) com furo — preencher com evenodd."""
    r = h*0.36; cy = top + r
    o = arc(cx, cy, r, 145, 395)
    o += [("C", (cx+r*0.55, cy+r*1.25), (cx+r*0.15, top+h*0.85), (cx, top+h)),
          ("C", (cx-r*0.15, top+h*0.85), (cx-r*0.55, cy+r*1.25), o[0][1]), ("Z",)]
    return o + circle(cx, cy, r*0.42, ccw=True)

def whatsapp(L, cx, cy, R):
    bub = arc(cx, cy, R, 128, 470) + [("L", (cx-R*1.12, cy+R*1.12)), ("Z",)]
    fill(L, bub, "verde")
    ring = arc(cx, cy, R*0.74, 130, 465) + [("L", (cx-R*0.82, cy+R*0.82)), ("Z",)]
    stroke(L, ring, "branco", R*0.1)
    # fone
    c = (cx + R*0.12, cy - R*0.12); rr = R*0.36
    stroke(L, arc(c[0], c[1], rr, 75, 195), "branco", R*0.17)
    for a in (75, 195):
        t = math.radians(a); p = (c[0]+rr*math.cos(t), c[1]+rr*math.sin(t))
        e = (p[0]-math.sin(t)*R*0.11*(1 if a == 75 else -1), p[1]+math.cos(t)*R*0.11*(1 if a == 75 else -1))
        fill(L, rrect(p[0]-R*0.11, p[1]-R*0.11, R*0.22, R*0.22, R*0.07) if False else circle(p[0], p[1], R*0.13), "branco")

def plane(cx, cy, s, ang):
    m = rot(ang, cx, cy)
    outer = [(cx-s, cy+0.1*s), (cx+s, cy-0.45*s), (cx-0.2*s, cy+0.55*s), (cx-0.35*s, cy+0.15*s)]
    fold = [(cx-0.35*s, cy+0.15*s), (cx+s, cy-0.45*s), (cx-0.3*s, cy+0.8*s), (cx-0.35*s, cy+0.15*s)]
    return xform(poly(outer), m), xform(poly(fold, False), m)

def heart(cx, cy, s):
    return [("M", (cx, cy+s*0.95)),
            ("C", (cx-s*0.2, cy+s*0.6), (cx-s*1.05, cy+s*0.2), (cx-s*0.95, cy-s*0.35)),
            ("C", (cx-s*0.85, cy-s*0.95), (cx-s*0.1, cy-s*0.95), (cx, cy-s*0.35)),
            ("C", (cx+s*0.1, cy-s*0.95), (cx+s*0.85, cy-s*1.0), (cx+s*0.97, cy-s*0.4)),
            ("C", (cx+s*1.08, cy+s*0.15), (cx+s*0.3, cy+s*0.55), (cx+s*0.05, cy+s*0.98))]

# ---------------------------------------------------------------- composição
def build():
    d = Doc()
    FRD, FRC = "Fredoka-Bold.ttf", "Fredoka-CondBold.ttf"  # títulos
    NUN = "Nunito-Black.ttf"                               # logo
    BAL = "Baloo2-ExtraBold.ttf"                           # endereço / telefone
    ITM = "Itim-Regular.ttf"                               # manuscrito

    # 1 Fundo
    L = d.layer("01 Fundo")
    fill(L, poly([(0, 0), (W, 0), (W, H), (0, H)]), "creme")

    # 2 Ondas
    L = d.layer("02 Ondas")
    yel = [(0, 770), (500, 805), (1100, 880), (1700, 935), (2400, 945), (3100, 925), (3800, 900), (4400, 875), (5000, 845)]
    blu = [(0, 830), (500, 860), (1100, 925), (1700, 965), (2400, 972), (3100, 952), (3800, 925), (4400, 900), (5000, 870)]
    def wave(pts):
        o = smooth(pts, closed=False, t=1.0)
        return o + [("L", (W, H)), ("L", (0, H)), ("Z",)]
    fill(L, wave(yel), "amarelo")
    fill(L, wave(blu), "azul")

    # 3 Logo
    L = d.layer("03 Logo Colégio Caminhar")
    lx = 500
    fill(L, xform([("M", (0, 0)), ("C", (-40, 30), (-70, 75), (-62, 120)), ("C", (-30, 95), (5, 80), (40, 72)),
                   ("C", (15, 55), (5, 30), (0, 0)), ("Z",)], (1, 0, 0, 1, lx-30, 125)), "azul")
    fill(L, star(lx+30, 140, 128, 66, -14), "amarelo")
    o, w_, _ = text(NUN, "Caminhar", 0, lx, 440, width=700, feats={"ss01": True})
    fill(L, o, "azul")
    o, _, _ = text(NUN, "COLÉGIO", 0, lx - 350 + 8, 300, anchor="start", cap=40, track=0.04)
    fill(L, o, "azul")

    # 4 Slogan
    L = d.layer("04 Slogan")
    m = rot(-7, 420, 600)
    for i, line in enumerate(["Mais que", "uma escola,", "uma jornada", "de descobertas!"]):
        o, _, _ = text(ITM, line, 60, 430 + i*18, 530 + i*62)
        fill(L, xform(o, m), "azul")
    stroke(L, xform(smooth([(270, 735), (420, 728), (590, 720)], False), m), "amarelo", 12)
    sparks(L, 205, 650, [175, 200, 225], 0, 0, "amarelo", 12)
    for (a, b) in [((150, 610), (190, 625)), ((140, 660), (185, 662)), ((155, 712), (192, 698))]:
        stroke(L, poly([a, b], False), "amarelo", 12)

    # 5 Título
    L = d.layer("05 Titulo Educacao Infantil")
    CX = 2050
    o, wt, _ = text(FRC, "EDUCAÇÃO INFANTIL", 0, CX, 470, width=2150)
    print("titulo largura", round(wt))
    xl = CX - wt/2
    nossa, wn, _ = text(FRD, "NOSSA", 0, xl + 450, 200, cap=130, track=0.02)
    br = brush(xl + 120, 65, xl + 450 + wn/2 + 170, 200, seed=3)
    fill(L, xform(br, rot(-3, CX, 135)), "amarelo")
    fill(L, nossa, "azul")
    fill(L, o, "azul")
    sparks(L, xl - 20, 520, [150, 180, 210], 40, 95, "amarelo", 13)
    # faixa "DE CASA NOVA EM 2027!"
    m = rot(-2.2, CX, 605)
    a, wa, _ = text(FRC, "DE CASA NOVA ", 0, 0, 0, cap=112, anchor="start")
    b, wb, _ = text(FRC, "EM 2027!", 0, 0, 0, cap=112, anchor="start")
    tw = wa + wb; ph = 190; pw = tw + 150
    fill(L, xform(rrect(CX - pw/2, 605 - ph/2, pw, ph, ph/2), m), "azul")
    xs = CX - tw/2
    fill(L, xform(xform(a, (1, 0, 0, 1, xs, 605 + 112/2)), m), "branco")
    fill(L, xform(xform(b, (1, 0, 0, 1, xs + wa, 605 + 112/2)), m), "amarelo")
    pr = CX + pw/2
    sparks(L, pr + 10, 605, [-35, 0, 35], 45, 100, "amarelo", 13)

    # 6 Endereço
    L = d.layer("06 Endereco")
    o, wa, _ = text(BAL, "Rua Visconde de Mauá, 244", 0, 0, 0, cap=72, anchor="start")
    ph = 150; pw = wa + 300; px = CX - pw/2 + 10; py = 715
    fill(L, rrect(px, py, pw, ph, ph/2), "azul")
    fill(L, pin(px + 105, py + 22, 108), "amarelo", evenodd=True)
    fill(L, xform(o, (1, 0, 0, 1, px + 200, py + ph/2 + 36)), "branco")

    # 7 Divisória
    L = d.layer("07 Divisoria")
    stroke(L, poly([(3150, 130), (3150, 790)], False), "amarelo", 10)

    # 8 Matrículas
    L = d.layer("08 Matriculas Abertas")
    RX = 4010
    m = rot(-3, RX, 200)
    o, wm, _ = text(FRD, "MATRÍCULAS", 0, RX, 285, cap=140, track=0.01)
    fill(L, xform(brush(RX - wm/2 - 60, 130, RX + wm/2 + 40, 275, seed=7), m), "amarelo")
    fill(L, xform(o, m), "azul")
    m = rot(-4, RX, 400)
    o, wa, _ = text(FRD, "ABERTAS!", 0, RX, 400 + 70, cap=140, track=0.02)
    ph = 205; pw = wa + 150
    fill(L, xform(rrect(RX - pw/2, 400 - ph/2, pw, ph, 70), m), "azul")
    fill(L, xform(o, m), "branco")
    sparks(L, RX - pw/2 - 30, 400, [160, 185, 210], 30, 95, "azul", 13)
    sparks(L, RX + pw/2 + 30, 380, [-40, -10, 20], 30, 95, "azul", 13)
    hc = (4875, 175)
    stroke(L, xform(heart(hc[0], hc[1], 50), rot(12, *hc)), "amarelo", 11)
    sparks(L, hc[0], hc[1], [200, 235, 270], 80, 115, "amarelo", 10)

    # 9 Chamada
    L = d.layer("09 Chamada visita")
    m = rot(-4, RX, 610)
    for i, line in enumerate(["Agende uma visita e venha", "conhecer nosso novo espaço!"]):
        o, _, _ = text(ITM, line, 72, RX + (i*-10), 580 + i*72)
        fill(L, xform(o, m), "azul")
    stroke(L, xform(smooth([(RX - 420, 690), (RX, 680), (RX + 450, 668)], False), m), "amarelo", 10)

    # 10 WhatsApp
    L = d.layer("10 WhatsApp")
    o, wp, _ = text(BAL, "11 94515-9449", 0, 0, 0, cap=88, anchor="start", track=0.01)
    ph = 140; pw = wp + 270; px = RX - pw/2 + 30; py = 735
    fill(L, rrect(px, py, pw, ph, ph/2), "amarelo")
    whatsapp(L, px + 30, py + ph/2, 82)
    fill(L, xform(o, (1, 0, 0, 1, px + 145, py + ph/2 + 44)), "azul")
    sparks(L, px - 60, py + ph/2, [165, 180, 195], 25, 85, "azul", 12)
    sparks(L, px + pw + 30, py + ph/2, [-15, 0, 15], 25, 85, "azul", 12)

    # 11 Decoração (avião de papel)
    L = d.layer("11 Aviao de papel")
    stroke(L, smooth([(2560, 905), (2700, 915), (2850, 890), (2960, 845)], False), "azul", 7, dash=(22, 20))
    a, b = plane(3040, 805, 70, -25)
    fill(L, a, "creme"); stroke(L, a, "azul", 7); stroke(L, b, "azul", 7)
    return d

# ---------------------------------------------------------------- saída SVG
def fmt(v): return ("%.3f" % v).rstrip("0").rstrip(".")
def svg_d(ops):
    s = []
    for o in ops:
        s.append(o[0] + " ".join(fmt(p[0]) + "," + fmt(p[1]) for p in o[1:]))
    return "".join(s)
def write_svg(d, path):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{fmt(W)}mm" height="{fmt(H)}mm" viewBox="0 0 {fmt(W)} {fmt(H)}">']
    for name, items in d.layers:
        lid = name.split(" ", 1)[1].replace(" ", "_")
        out.append(f'<g inkscape:groupmode="layer" id="{lid}" inkscape:label="{name}">')
        for it in items:
            c = COL[it["c"]][1]
            if it["t"] == "f":
                out.append(f'<path fill="{c}" fill-rule="{"evenodd" if it["eo"] else "nonzero"}" d="{svg_d(it["ops"])}"/>')
            else:
                da = f' stroke-dasharray="{fmt(it["dash"][0])} {fmt(it["dash"][1])}"' if it["dash"] else ""
                out.append(f'<path fill="none" stroke="{c}" stroke-width="{fmt(it["w"])}" stroke-linecap="round" '
                           f'stroke-linejoin="round"{da} d="{svg_d(it["ops"])}"/>')
        out.append("</g>")
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))

# ---------------------------------------------------------------- saída PDF (CMYK + camadas OCG)
PT = 72 / 25.4
def write_pdf(d, path):
    def P(p): return f"{p[0]*PT:.2f} {(H-p[1])*PT:.2f}"
    cs = []; props = []
    for i, (name, items) in enumerate(d.layers):
        cs.append(f"/OC /L{i} BDC")
        for it in items:
            c = " ".join("%.3f" % v for v in COL[it["c"]][0])
            for o in it["ops"]:
                cs.append({"M": "{} m", "L": "{} l", "C": "{} {} {} c", "Z": "h"}[o[0]].format(*[P(p) for p in o[1:]]))
            if it["t"] == "f":
                cs.insert(len(cs) - sum(1 for _ in it["ops"]), f"{c} k")
                cs.append("f*" if it["eo"] else "f")
            else:
                cs.insert(len(cs) - len(it["ops"]), f"{c} K {it['w']*PT:.2f} w 1 J 1 j " +
                          (f"[{it['dash'][0]*PT:.2f} {it['dash'][1]*PT:.2f}] 0 d" if it["dash"] else "[] 0 d"))
                cs.append("S")
        cs.append("EMC")
    stream = zlib.compress("\n".join(cs).encode("latin-1"), 9)
    n = len(d.layers)
    objs = {}
    ocg_ids = list(range(6, 6 + n))
    def pdfstr(s):
        b = s.encode("utf-16-be")
        return "<FEFF" + b.hex().upper() + ">"
    objs[1] = (f"<< /Type /Catalog /Pages 2 0 R /OCProperties << /OCGs [{' '.join(f'{k} 0 R' for k in ocg_ids)}] "
               f"/D << /Order [{' '.join(f'{k} 0 R' for k in ocg_ids)}] /ON [{' '.join(f'{k} 0 R' for k in ocg_ids)}] >> >> >>")
    objs[2] = "<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    wpt, hpt = W*PT, H*PT
    objs[3] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {wpt:.2f} {hpt:.2f}] /TrimBox [0 0 {wpt:.2f} {hpt:.2f}] "
               f"/Resources << /Properties << {' '.join(f'/L{i} {k} 0 R' for i, k in enumerate(ocg_ids))} >> >> /Contents 4 0 R >>")
    objs[5] = f"<< /Title {pdfstr('Banner Colégio Caminhar 5x1m')} /Creator (gerar_banner.py) >>"
    for i, k in enumerate(ocg_ids):
        objs[k] = f"<< /Type /OCG /Name {pdfstr(d.layers[i][0])} >>"
    out = bytearray(b"%PDF-1.6\n%\xe2\xe3\xcf\xd3\n"); offs = {}
    for k in sorted(list(objs) + [4]):
        offs[k] = len(out)
        if k == 4:
            out += f"4 0 obj\n<< /Length {len(stream)} /Filter /FlateDecode >>\nstream\n".encode() + stream + b"\nendstream\nendobj\n"
        else:
            out += f"{k} 0 obj\n{objs[k]}\nendobj\n".encode("latin-1")
    xref = len(out); total = max(offs) + 1
    out += f"xref\n0 {total}\n0000000000 65535 f \n".encode()
    for k in range(1, total):
        out += f"{offs[k]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {total} /Root 1 0 R /Info 5 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    open(path, "wb").write(out)

if __name__ == "__main__":
    ensure_fonts()
    doc = build()
    pdf = os.path.join(HERE, "banner_caminhar_5x1m.pdf")
    write_pdf(doc, pdf)
    write_svg(doc, os.path.join(HERE, "banner_caminhar_5x1m.svg"))
    subprocess.run(["pdftocairo", "-png", "-singlefile", "-scale-to-x", "3000", "-scale-to-y", "-1",
                    pdf, os.path.join(HERE, "preview")], check=True)
    print("ok")
