"""Motion design do logo Colégio Athena — 10 s, 1080x1920, 60 fps.

Renderiza os quadros com numpy/PIL a partir das duas imagens do logo e os
envia direto para o ffmpeg. Uso: python3 render.py [saida.mp4]
"""
import math
import multiprocessing
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
FPS = 60
DUR = 10.0
NFRAMES = int(FPS * DUR)
C = np.array([W / 2, H / 2])

BG = np.array([4, 126, 25], np.float32)
WHITE = np.array([255, 255, 255], np.float32)
RED = np.array([248, 32, 34], np.float32)
BLUE = np.array([26, 62, 198], np.float32)

rng = np.random.default_rng(7)


# ---------------------------------------------------------------- easing
def clamp01(x):
    return min(1.0, max(0.0, x))


def prog(t, t0, t1):
    return clamp01((t - t0) / (t1 - t0))


def ease_out_expo(x):
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_out_cubic(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_in_out_expo(x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 2 ** (20 * x - 10) / 2 if x < 0.5 else (2 - 2 ** (-20 * x + 10)) / 2


def ease_out_back(x, k=1.9):
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def bump(t, t0, t1):
    """0 -> 1 -> 0 suave entre t0 e t1."""
    x = prog(t, t0, t1)
    return math.sin(math.pi * x) ** 2


# ---------------------------------------------------------------- layers
def load_alpha(path, color):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    d = color - BG
    return np.clip(((a - BG) @ d) / (d @ d), 0, 1)


class Layer:
    def __init__(self, mask, x0, y0, color):
        self.mask = mask.astype(np.float32)
        self.x0, self.y0 = x0, y0
        self.h, self.w = mask.shape
        self.color = color
        self.anchor = np.array([x0 + self.w / 2, y0 + self.h / 2])


def crop_layer(full, x0, y0, x1, y1, color, pad=6):
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    m = full[y0:y1, x0:x1].copy()
    return Layer(m, x0, y0, color)


emb_full = load_alpha("assets/emblema.jpg", WHITE)
logo_white = load_alpha("assets/logo_completo.jpg", WHITE)
logo_red = load_alpha("assets/logo_completo.jpg", RED)
logo_blue = load_alpha("assets/logo_completo.jpg", BLUE)
emb_full[emb_full < 0.03] = 0
logo_white[logo_white < 0.03] = 0

# --- emblema grande (imagem 1), separado por raio
ECX, ECY = 533.0, 961.5
ex0, ey0, ex1, ey1 = 360, 790, 707, 1134
emb = emb_full[ey0:ey1, ex0:ex1]
yy, xx = np.mgrid[ey0:ey1, ex0:ex1].astype(np.float32)
rr = np.hypot(xx - ECX, yy - ECY)
theta = (np.arctan2(xx - ECX, -(yy - ECY)) / (2 * np.pi)) % 1.0  # 0 no topo, horário


def ring_sel(r0, r1):
    return np.clip((rr - r0) / 2, 0, 1) * np.clip((r1 - rr) / 2, 0, 1)


E_MONO = Layer(emb * ring_sel(-10, 93), ex0, ey0, WHITE)
E_INNER = Layer(emb * ring_sel(93, 111), ex0, ey0, WHITE)
E_OUTER = Layer(emb * ring_sel(147, 170), ex0, ey0, WHITE)
dots = emb * ring_sel(111, 147)
E_DOT_L = Layer(np.where(xx < ECX, dots, 0), ex0, ey0, WHITE)
E_DOT_R = Layer(np.where(xx >= ECX, dots, 0), ex0, ey0, WHITE)
E_DOT_L.anchor = np.array([405.5, 961.5])
E_DOT_R.anchor = np.array([662.5, 961.5])
for L in (E_MONO, E_INNER, E_OUTER, E_DOT_L, E_DOT_R):
    L.anchor = L.anchor if L in (E_DOT_L, E_DOT_R) else np.array([ECX, ECY])

# --- logo completo (imagem 2)
E2CX, E2CY = 277.5, 960.5
E_SCALE = 179.0 / 320.0
L_EMB2 = crop_layer(logo_white, 182, 865, 374, 1057, WHITE)
L_EMB2.anchor = np.array([E2CX, E2CY])
L_COLEGIO = crop_layer(logo_white, 397, 868, 602, 927, WHITE, pad=2)
letter_cols = [(390, 470), (470, 545), (548, 634), (642, 702), (704, 800), (800, 892)]
L_LETTERS = [crop_layer(logo_white, a, 927, b, 1016, WHITE, pad=0) for a, b in letter_cols]
L_RED = crop_layer(logo_red * (np.mgrid[:H, :W][0] < 1031), 390, 1018, 891, 1031, RED, pad=0)
L_BLUE = crop_layer(logo_blue * (np.mgrid[:H, :W][0] >= 1031), 393, 1031, 888, 1046, BLUE, pad=0)
L_ENSINO = crop_layer(logo_white, 610, 1055, 890, 1100, WHITE, pad=3)


# ---------------------------------------------------------------- render core
class Frame:
    """Camada de frente em cor pré-multiplicada (out) + alfa (A)."""
    def __init__(self):
        self.out = np.zeros((H, W, 3), np.float32)
        self.A = np.zeros((H, W), np.float32)


def place(fr, L, Z, s=1.0, d=(0.0, 0.0), rot=0.0, opacity=1.0, mask=None,
          clip=None, blur=0.0, color=None):
    """Compoe a camada L no quadro. Transformação local (escala/rotação em
    torno de L.anchor, translação d) seguida da câmera (zoom Z no centro)."""
    if opacity <= 0.002 or s <= 0.001:
        return
    m = L.mask if mask is None else mask
    d = np.asarray(d, float)
    c, si = math.cos(rot), math.sin(rot)
    R = np.array([[c, -si], [si, c]])
    Rinv = R.T
    A = L.anchor
    # bbox de destino
    corners = np.array([[L.x0, L.y0], [L.x0 + L.w, L.y0], [L.x0, L.y0 + L.h], [L.x0 + L.w, L.y0 + L.h]], float)
    pd = A + d + s * (corners - A) @ R.T
    g = C + Z * (pd - C)
    pad = int(3 * blur) + 2
    gx0 = max(0, int(math.floor(g[:, 0].min())) - pad)
    gy0 = max(0, int(math.floor(g[:, 1].min())) - pad)
    gx1 = min(W, int(math.ceil(g[:, 0].max())) + pad)
    gy1 = min(H, int(math.ceil(g[:, 1].max())) + pad)
    if gx1 <= gx0 or gy1 <= gy0:
        return
    M = Rinv / (s * Z)
    off = A + Rinv @ (C - A - d) / s - M @ C
    G0 = np.array([gx0, gy0], float)
    o = M @ G0 + off - np.array([L.x0, L.y0])
    data = (M[0, 0], M[0, 1], o[0], M[1, 0], M[1, 1], o[1])
    img = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")
    res = img.transform((gx1 - gx0, gy1 - gy0), Image.AFFINE, data, Image.BICUBIC)
    if blur > 0.3:
        res = res.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(res, np.float32) / 255.0
    if clip is not None:
        qy = C[1] + (np.arange(gy0, gy1, dtype=np.float32) - C[1]) / Z
        qx = C[0] + (np.arange(gx0, gx1, dtype=np.float32) - C[0]) / Z
        a = a * clip(qx[None, :], qy[:, None])
    a *= opacity
    col = L.color if color is None else color
    sl = fr.out[gy0:gy1, gx0:gx1]
    sl *= (1 - a)[..., None]
    sl += a[..., None] * col
    As = fr.A[gy0:gy1, gx0:gx1]
    As += a * (1 - As)


def blur_full(arr, radius, down=4):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "L")
    small = img.resize((W // down, H // down), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(radius / down))
    return np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255.0


# ---------------------------------------------------------------- background
gy, gx = np.mgrid[:H, :W].astype(np.float32)
R_C = np.hypot(gx - C[0], gy - C[1])
vign = 1.0 - 0.42 * np.clip(R_C / 1150.0, 0, 1) ** 1.7
BASE = (BG[None, None, :] * vign[..., None]).astype(np.float32)
DARK = np.array([1, 22, 6], np.float32)
EMB_R = np.hypot(gx - ECX, gy - ECY)

# partículas (bokeh)
NP = 70
P_x = rng.uniform(0, W, NP)
P_y = rng.uniform(0, H, NP)
P_r = rng.uniform(2.0, 11.0, NP)
P_a = rng.uniform(0.04, 0.22, NP)
P_v = rng.uniform(12, 55, NP)
P_ph = rng.uniform(0, 2 * np.pi, NP)
P_depth = rng.uniform(0.3, 1.0, NP)
sprites = {}


def sprite(r):
    k = round(r * 2) / 2
    if k not in sprites:
        n = int(k * 3) + 2
        yy_, xx_ = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
        sprites[k] = np.exp(-(xx_ ** 2 + yy_ ** 2) / (2 * (k * 0.8) ** 2))
    return sprites[k]


def light_leak(t):
    lx = W * (0.15 + 0.7 * (0.5 + 0.5 * math.sin(t * 0.35 + 1.0)))
    ly = H * (0.25 + 0.5 * (0.5 + 0.5 * math.cos(t * 0.27)))
    return np.exp(-((gx - lx) ** 2 + (gy - ly) ** 2) / (2 * 380.0 ** 2))


NOISE = [rng.normal(0, 0.9, (H, W, 1)).astype(np.float32) for _ in range(4)]


def background(t, Z):
    k = 0.12 + 0.88 * ease_out_cubic(prog(t, 0.0, 1.1))
    bg = DARK + (BASE - DARK) * k
    leak = light_leak(t) * (0.10 * k)
    bg = bg + leak[..., None] * np.array([60, 140, 70], np.float32)
    # flash inicial
    fl = bump(t, 0.22, 1.0) * 0.45
    if fl > 0.01:
        g = np.exp(-(R_C ** 2) / (2 * 360.0 ** 2)) * fl
        bg = bg + g[..., None] * np.array([120, 230, 140], np.float32)
    # partículas
    for i in range(NP):
        z = 1 + (Z - 1) * P_depth[i]
        px = C[0] + (P_x[i] + 8 * math.sin(t * 0.8 + P_ph[i]) - C[0]) * z
        py = C[1] + (((P_y[i] - P_v[i] * t) % (H + 80)) - 40 - C[1]) * z
        tw = 0.6 + 0.4 * math.sin(t * 2.2 + P_ph[i])
        a = P_a[i] * tw * k * 255
        sp = sprite(P_r[i] * P_depth[i] * 1.2)
        n = sp.shape[0] // 2
        x0, y0 = int(px) - n, int(py) - n
        if x0 < 0 or y0 < 0 or x0 + sp.shape[1] > W or y0 + sp.shape[0] > H:
            continue
        bg[y0:y0 + sp.shape[0], x0:x0 + sp.shape[1]] += (sp * a)[..., None] * np.array([0.85, 1.0, 0.88], np.float32)
    return bg


# ---------------------------------------------------------------- scene
T_MOVE0, T_MOVE1 = 3.25, 4.25


def camera(t):
    # leve dolly-in contínuo que assenta no final
    return 1.10 - 0.10 * ease_out_cubic(prog(t, 0.0, 9.6))


def emblem_state(t):
    """posição / escala / rotação do emblema grande."""
    x = ease_in_out_expo(prog(t, T_MOVE0, T_MOVE1))
    pos = np.array([ECX + (E2CX - ECX) * x, ECY + (E2CY - ECY) * x])
    intro = 0.86 + 0.14 * ease_out_expo(prog(t, 0.25, 2.4))
    breathe = 1 + 0.025 * bump(t, 2.2, 3.4)
    s = (1 + (E_SCALE - 1) * x) * intro * breathe
    rot = -2 * math.pi * x
    return pos, s, rot


def draw_emblem(fr, t, Z):
    if t >= T_MOVE1 + 0.12:
        place(fr, L_EMB2, Z)
        return
    pos, s, rot = emblem_state(t)
    d = pos - np.array([ECX, ECY])
    # anel externo: desenho angular horário
    f_out = ease_in_out_cubic(prog(t, 0.35, 1.55))
    f_in = ease_in_out_cubic(prog(t, 0.65, 1.75))
    edge = 0.012
    if f_out > 0:
        w = np.clip((f_out * (1 + edge) - theta) / edge, 0, 1)
        place(fr, E_OUTER, Z, s, d, rot, mask=E_OUTER.mask * w)
    if f_in > 0:
        w = np.clip((f_in * (1 + edge) - ((1 - theta + 0.5) % 1.0)) / edge, 0, 1)
        place(fr, E_INNER, Z, s, d, rot, mask=E_INNER.mask * w)
    # pontos
    for L, t0 in ((E_DOT_L, 1.45), (E_DOT_R, 1.55)):
        p = prog(t, t0, t0 + 0.45)
        if p > 0:
            ds = ease_out_back(p, 2.6)
            # o ponto escala em torno do próprio centro, depois segue o emblema
            off = L.anchor - np.array([ECX, ECY])
            c_, s_ = math.cos(rot), math.sin(rot)
            off_r = np.array([c_ * off[0] - s_ * off[1], s_ * off[0] + c_ * off[1]]) * s
            dd = pos + off_r - L.anchor
            place(fr, L, Z, s * ds, dd, rot, opacity=min(1, p * 4))
    # monograma
    p = prog(t, 1.6, 2.45)
    if p > 0:
        e = ease_out_expo(p)
        place(fr, E_MONO, Z, s * (1.35 - 0.35 * e), d, rot, opacity=min(1, p * 2.2),
              blur=10 * (1 - e))
    # crossfade para o emblema da arte final
    xf = prog(t, T_MOVE1 - 0.05, T_MOVE1 + 0.12)
    if xf > 0:
        place(fr, L_EMB2, Z, opacity=xf)


def draw_text(fr, t, Z):
    # barras vermelha e azul desenhando da esquerda para a direita
    for L, t0 in ((L_RED, 3.95), (L_BLUE, 4.07)):
        p = ease_out_expo(prog(t, t0, t0 + 0.95))
        if p > 0:
            xe = L.x0 + p * L.w
            place(fr, L, Z, clip=lambda qx, qy, xe=xe: np.clip((xe - qx) / 3, 0, 1))
    # letras ATHENA surgindo de trás das barras
    for i, L in enumerate(L_LETTERS):
        t0 = 4.30 + i * 0.075
        p = prog(t, t0, t0 + 0.85)
        if p > 0:
            dy = 96 * (1 - ease_out_expo(p))
            place(fr, L, Z, d=(0, dy), opacity=min(1, p * 3),
                  clip=lambda qx, qy: np.clip((1018 - qy) / 1.5, 0, 1))
    # "Colégio" surgindo de trás de ATHENA
    p = prog(t, 4.95, 5.85)
    if p > 0:
        dy = 60 * (1 - ease_out_expo(p))
        place(fr, L_COLEGIO, Z, d=(0, dy), opacity=min(1, p * 2.5),
              clip=lambda qx, qy: np.clip((927.5 - qy) / 1.5, 0, 1))
    # "Ensino Bilíngue" descendo de baixo das barras
    p = prog(t, 5.25, 6.15)
    if p > 0:
        dy = -54 * (1 - ease_out_expo(p))
        place(fr, L_ENSINO, Z, d=(0, dy), opacity=min(1, p * 2.5),
              clip=lambda qx, qy: np.clip((qy - 1047) / 1.5, 0, 1))


def bar_tip_glow(fr, t, Z):
    """brilho na ponta das barras enquanto desenham + anéis."""
    for L, t0, col in ((L_RED, 3.95, np.array([255, 160, 150.])), (L_BLUE, 4.07, np.array([160, 190, 255.]))):
        p = prog(t, t0, t0 + 0.95)
        if 0 < p < 1:
            e = ease_out_expo(p)
            xe = L.x0 + e * L.w
            ye = L.y0 + L.h / 2
            gxp = C[0] + Z * (xe - C[0])
            gyp = C[1] + Z * (ye - C[1])
            inten = (1 - p) ** 1.5
            x0, x1 = max(0, int(gxp - 220)), min(W, int(gxp + 220))
            y0, y1 = max(0, int(gyp - 80)), min(H, int(gyp + 80))
            sx, sy = gx[y0:y1, x0:x1] - gxp, gy[y0:y1, x0:x1] - gyp
            g = np.exp(-((sx / 70) ** 2 + (sy / 9) ** 2)) * inten
            g += np.exp(-((sx / 18) ** 2 + (sy / 18) ** 2)) * inten * 0.8
            fr.out[y0:y1, x0:x1] += g[..., None] * col * 0.9
    # cabeça luminosa no desenho dos anéis
    for f0, f1, rad, cw in ((0.35, 1.55, 158.0, 1), (0.65, 1.75, 102.0, -1)):
        p = prog(t, f0, f1)
        if 0 < p < 1:
            f = ease_in_out_cubic(p)
            ang = 2 * math.pi * f
            pos, s, _ = emblem_state(t)
            hx = pos[0] + math.sin(ang) * rad * s
            hy = pos[1] - cw * math.cos(ang) * rad * s
            gxp, gyp = C[0] + Z * (hx - C[0]), C[1] + Z * (hy - C[1])
            inten = math.sin(math.pi * p) ** 0.6
            x0, x1 = max(0, int(gxp - 200)), min(W, int(gxp + 200))
            y0, y1 = max(0, int(gyp - 200)), min(H, int(gyp + 200))
            r2 = (gx[y0:y1, x0:x1] - gxp) ** 2 + (gy[y0:y1, x0:x1] - gyp) ** 2
            g = np.exp(-r2 / (2 * 14.0 ** 2)) * inten
            g += np.exp(-r2 / (2 * 50.0 ** 2)) * inten * 0.35
            fr.out[y0:y1, x0:x1] += g[..., None] * np.array([200, 255, 215.]) * 0.9


def shockwave(fr, t, t0, cx, cy, Z, r_max=700, dur=1.0, strength=0.5):
    p = prog(t, t0, t0 + dur)
    if 0 < p < 1:
        e = ease_out_cubic(p)
        gxp, gyp = C[0] + Z * (cx - C[0]), C[1] + Z * (cy - C[1])
        r = np.hypot(gx - gxp, gy - gyp)
        R = 40 + r_max * e
        w = 6 + 40 * e
        g = np.exp(-((r - R) / w) ** 2) * (1 - p) ** 2 * strength
        fr.out += g[..., None] * np.array([180, 255, 200.])


def anamorphic(fr, t, Z):
    i = bump(t, T_MOVE0 + 0.1, T_MOVE1 + 0.15)
    if i > 0.01:
        pos, _, _ = emblem_state(t)
        gyp = C[1] + Z * (pos[1] - C[1])
        gxp = C[0] + Z * (pos[0] - C[0])
        dy = gy - gyp
        h = np.exp(-(gx - gxp) ** 2 / (2 * 420.0 ** 2))
        g = (np.exp(-(dy / 2.2) ** 2) * 0.9 + np.exp(-(dy / 26) ** 2) * 0.25) * h * i
        fr.out += g[..., None] * np.array([170, 255, 200.])


def shine(fr, t, t0, dur, Z, strength=1.0):
    p = prog(t, t0, t0 + dur)
    if 0 < p < 1:
        e = ease_in_out_cubic(p)
        qx = C[0] + (gx - C[0]) / Z
        qy = C[1] + (gy - C[1]) / Z
        u = qx + 0.45 * qy
        u0 = 150 + 450 * 0.45 + e * (1200 - 150)
        band = np.exp(-((u - u0) / 45) ** 2) * strength
        sa = fr.A * band
        fr.out += sa[..., None] * 140
        gl = blur_full(sa, 26)
        fr.out += gl[..., None] * np.array([150, 255, 180.]) * 1.4


def sparkle(fr, t, t0, x, y, Z, size=1.0):
    p = prog(t, t0, t0 + 0.9)
    if 0 < p < 1:
        i = math.sin(math.pi * p) ** 1.5
        gxp, gyp = C[0] + Z * (x - C[0]), C[1] + Z * (y - C[1])
        x0, x1 = int(gxp - 160), int(gxp + 160)
        y0, y1 = int(gyp - 160), int(gyp + 160)
        sx = gx[y0:y1, x0:x1] - gxp
        sy = gy[y0:y1, x0:x1] - gyp
        L = 120 * size * (0.6 + 0.4 * i)
        star = (np.exp(-(sy / 1.6) ** 2 - (sx / L) ** 2) + np.exp(-(sx / 1.6) ** 2 - (sy / L) ** 2))
        star += np.exp(-(sx ** 2 + sy ** 2) / (2 * 5.0 ** 2)) * 1.2
        star += np.exp(-(sx ** 2 + sy ** 2) / (2 * 30.0 ** 2)) * 0.25
        fr.out[y0:y1, x0:x1] += (star * i)[..., None] * np.array([235, 255, 240.])


class Canvas:
    def __init__(self, bg, fg):
        self.out = bg * (1 - fg.A)[..., None] + fg.out
        self.A = fg.A


def render(t):
    Z = camera(t)
    fg = Frame()
    # motion blur: sub-amostras do emblema durante o giro/deslocamento rápido
    if T_MOVE0 + 0.08 < t < T_MOVE1 - 0.02:
        n = 18
        sub_out = np.zeros((H, W, 3), np.float32)
        sub_A = np.zeros((H, W), np.float32)
        for k in range(n):
            f = Frame()
            draw_emblem(f, t + (k / (n - 1) - 0.5) / FPS, Z)
            sub_out += f.out
            sub_A += f.A
        fg.out, fg.A = sub_out / n, sub_A / n
    else:
        draw_emblem(fg, t, Z)
    draw_text(fg, t, Z)
    fr = Canvas(background(t, Z), fg)
    shockwave(fr, t, 0.32, ECX, ECY, Z, r_max=650, dur=1.2, strength=0.45)
    # bloom suave de tudo que é branco
    if fr.A.max() > 0:
        gl = blur_full(fr.A, 30)
        fr.out += (gl * (1 - fr.A))[..., None] * np.array([90, 200, 110.]) * 0.32
    bar_tip_glow(fr, t, Z)
    anamorphic(fr, t, Z)
    shockwave(fr, t, T_MOVE1 - 0.05, E2CX, E2CY, Z, r_max=900, dur=1.3, strength=0.35)
    shine(fr, t, 2.35, 0.85, Z, 0.9)
    shine(fr, t, 6.45, 1.0, Z, 1.0)
    sparkle(fr, t, 7.15, 856, 934, Z, 1.0)
    sparkle(fr, t, 7.35, 300, 878, Z, 0.7)
    out = fr.out + NOISE[int(round(t * FPS)) % 4]  # dither contra banding
    return np.clip(out, 0, 255).astype(np.uint8)


def render_index(i):
    return render(i / FPS).tobytes()


def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else "build/video_sem_audio.mp4"
    only = None
    if len(sys.argv) > 2:
        only = [float(x) for x in sys.argv[2].split(",")]
    if only:
        for t in only:
            Image.fromarray(render(t)).save(f"{outp}_{t:05.2f}.png")
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
           "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with multiprocessing.Pool() as pool:
        for i, buf in enumerate(pool.imap(render_index, range(NFRAMES), chunksize=2)):
            proc.stdin.write(buf)
            if i % 60 == 0:
                print(f"frame {i}/{NFRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
