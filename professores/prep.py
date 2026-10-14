"""Separa a capa "Feliz Dia dos Professores" em camadas para a animação.

Gera em layers/: quadro-negro limpo (bg.png), avião, maçã, nuvem, cada letra de
FELIZ / DIA / PROFESSORES, o texto do selo DOS e da data, e layers.json com as
posições. Uso: python3 prep.py
"""
import json
import os

import numpy as np
from PIL import Image, ImageFilter

SRC = "assets/referencia_capa.jpg"
OUT = "layers"
os.makedirs(OUT, exist_ok=True)

img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W, _ = img.shape


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def blur(a, r):
    if a.ndim == 2:
        return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L")
                          .filter(ImageFilter.GaussianBlur(r)), np.float32) / 255
    return np.asarray(to_img(a).filter(ImageFilter.GaussianBlur(r)), np.float32)


def morph(m, size, op):
    f = ImageFilter.MaxFilter(size) if op == "dilate" else ImageFilter.MinFilter(size)
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8), "L").filter(f), np.float32) / 255


# ---------------------------------------------------------------- quadro limpo
# cada área com elemento recebe um pedaço de quadro limpo da mesma coluna
FILL = [  # (x0, y0, x1, y1, y_fonte)
    (0, 525, 445, 805, 240),
    (395, 495, 655, 805, 175),
    (80, 775, 1015, 1180, 1420),
    (840, 1040, 1080, 1335, 1560),
]
def box1(a, r, axis):
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def fblur(a, r):
    """aproxima um blur gaussiano em float com três passadas de caixa."""
    k = max(1, int(r / 1.7))
    for _ in range(3):
        a = box1(box1(a, k, 0), k, 1)
    return a


# iluminação de baixa frequência do quadro, interpolada por cima dos elementos
hole = np.zeros((H, W), np.float32)
for x0, y0, x1, y1, _ in FILL:
    hole[y0:y1, x0:x1] = 1
known = 1 - hole
low = None
for r in (180, 90, 40):  # do mais largo (sempre válido) para o mais fino
    wsum = fblur(known, r)
    est = fblur(img * known[..., None], r) / np.maximum(wsum, 1e-4)[..., None]
    c = np.clip(wsum / 0.35, 0, 1)[..., None] if low is not None else 1
    low = est if low is None else low * (1 - c) + est * c
LOW_R = 40

bg = img.copy()
for x0, y0, x1, y1, sy in FILL:
    h, w = y1 - y0, x1 - x0
    src = img[sy:sy + h, x0:x1]
    patch = src - fblur(src, LOW_R) + low[y0:y1, x0:x1]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = 26.0
    edge = np.minimum.reduce([yy, h - 1 - yy, xx if x0 > 0 else np.full_like(xx, f),
                              (w - 1 - xx) if x1 < W else np.full_like(xx, f)])
    m = np.clip(edge / f, 0, 1)[..., None]
    bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - m) + patch * m
to_img(bg).save(f"{OUT}/bg.png")
B = blur(bg, 12)  # cor local do quadro, para a separação por cor

manifest = {}


def save(name, rgb, alpha, x0, y0, x1, y1):
    a = alpha[y0:y1, x0:x1]
    ys, xs = np.where(a > 0.02)
    if len(xs) == 0:
        return
    cx0, cx1, cy0, cy1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([rgb[y0:y1, x0:x1][cy0:cy1, cx0:cx1], a[cy0:cy1, cx0:cx1] * 255])
    Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA").save(f"{OUT}/{name}.png")
    manifest[name] = {"x": int(x0 + cx0), "y": int(y0 + cy0), "w": int(cx1 - cx0), "h": int(cy1 - cy0)}


def region(x0, y0, x1, y1):
    m = np.zeros((H, W), np.float32)
    m[y0:y1, x0:x1] = 1
    return m


lum = img.mean(-1)
mn = img.min(-1)
sat = img.max(-1) - img.min(-1)
Bl = B.mean(-1)
WHITE = np.full_like(img, 255)

# ---------------------------------------------------------------- avião (giz branco)
a = np.clip((lum - Bl - 28) / 150, 0, 1) * region(0, 560, 415, 775)
core = morph((a > 0.45).astype(np.float32), 9, "dilate")
a = a * blur(core, 1.5)
save("aviao", np.full_like(img, 245), a, 0, 560, 415, 775)

# ---------------------------------------------------------------- maçã
m = ((sat > 45) | (lum > Bl + 70)).astype(np.float32) * region(425, 525, 625, 780)
m = morph(morph(m, 9, "dilate"), 9, "erode")  # fecha os buracos
m = morph(morph(m, 5, "erode"), 5, "dilate")  # remove grãos soltos
a = blur(m, 1.2)
save("maca", img, a, 425, 525, 625, 780)

# ---------------------------------------------------------------- nuvem (giz azul)
blue = np.array([118, 182, 246], np.float32)
d = blue - B
proj = ((img - B) * d).sum(-1) / (d * d).sum(-1)
a = np.clip((proj - 0.12) / 0.6, 0, 1) * region(870, 1075, 1080, 1300)
a = a * blur(morph((a > 0.4).astype(np.float32), 15, "dilate"), 3)
save("nuvem", np.broadcast_to(blue, img.shape), a, 870, 1075, 1080, 1300)

# ---------------------------------------------------------------- textos
white_a = np.clip((mn - B.min(-1) - 25) / (235 - B.min(-1) - 25), 0, 1)

# "D" de DIA fica parcialmente atrás do selo DOS: reconstrói a parte escondida
BOX = (557, 896, 719, 979)
white_a_text = white_a * (1 - region(*BOX))
row = white_a[892, 640:BOX[2]].copy()
for y in range(BOX[1], 968):
    white_a_text[y, 640:BOX[2]] = row
stem = np.where(row > 0.5)[0]
if len(stem):
    xl = 640 + stem[0]
    white_a_text[938:968, xl:BOX[2]] = 1
    white_a_text[966:970, xl:BOX[2]] *= 0.5


def components(mask):
    """rotula componentes conectados (vizinhança 8) de uma máscara booleana."""
    lab = np.zeros(mask.shape, np.int32)
    n = 0
    h, w = mask.shape
    for sy, sx in zip(*np.nonzero(mask)):
        if lab[sy, sx]:
            continue
        n += 1
        lab[sy, sx] = n
        stack = [(sy, sx)]
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
    return lab, n


def split_letters(prefix, alpha, rgb, y0, y1, x0, x1, cuts):
    a = alpha[y0:y1, x0:x1]
    prof = a.sum(0)
    xs = [0]
    for c in cuts:  # refina cada corte no mínimo local da projeção
        lo, hi = c - x0 - 12, c - x0 + 12
        xs.append(lo + int(np.argmin(prof[lo:hi])))
    xs.append(x1 - x0)
    col_letter = np.searchsorted(np.array(xs[1:-1]), np.arange(x1 - x0), side="right")
    owner = np.broadcast_to(col_letter, a.shape).copy()
    # componentes inteiros vão para a letra onde está a maior parte deles
    lab, n = components(a > 0.04)
    for k in range(1, n + 1):
        sel = lab == k
        votes = np.bincount(owner[sel], weights=a[sel], minlength=len(xs) - 1)
        if votes.max() >= 0.8 * votes.sum():
            owner[sel] = int(np.argmax(votes))
    names = []
    for i in range(len(xs) - 1):
        n_ = f"{prefix}{i}"
        al = np.zeros_like(alpha)
        al[y0:y1, x0:x1] = a * (owner == i)
        save(n_, rgb, al, x0, y0, x1, y1)
        names.append(n_)
    return names


core = morph((white_a_text > 0.5).astype(np.float32), 5, "dilate")
wa = white_a_text * core
feliz = split_letters("feliz", wa, WHITE, 812, 990, 120, 600, [228, 345, 437, 486])
dia = split_letters("dia", wa, WHITE, 812, 990, 630, 990, [772, 806])

orange = np.array([255, 112, 8], np.float32)
d = orange - B
proj = ((img - B) * d).sum(-1) / (d * d).sum(-1)
oa = np.clip((proj - 0.1) / 0.75, 0, 1) * region(150, 950, 975, 1080)
oa *= np.clip((110 - img[..., 2]) / 40, 0, 1) * (1 - white_a)  # sem branco nem rosa
oa = oa * morph((oa > 0.5).astype(np.float32), 5, "dilate")
prof = split_letters("prof", oa, np.broadcast_to(orange, img.shape), 950, 1080, 150, 975,
                     [235, 309, 398, 460, 521, 591, 660, 747, 832, 888])

# texto branco dentro do selo DOS e da pílula da data
dos_a = white_a * region(BOX[0] + 4, BOX[1] + 4, BOX[2] - 4, BOX[3] - 4)
save("dos_txt", WHITE, dos_a, *[BOX[0], BOX[1], BOX[2], BOX[3]])
PILL = (330, 1072, 742, 1140)
date_a = white_a * region(PILL[0] + 20, PILL[1] + 6, PILL[2] - 20, PILL[3] - 6)
save("data_txt", WHITE, date_a, *PILL)


def median_color(x0, y0, x1, y1, cond):
    p = img[y0:y1, x0:x1][cond[y0:y1, x0:x1]]
    return [int(v) for v in np.median(p, 0)]


manifest["_box"] = {"x0": BOX[0], "y0": BOX[1], "x1": BOX[2], "y1": BOX[3],
                    "color": median_color(*BOX, (sat > 80))}
manifest["_pill"] = {"x0": PILL[0], "y0": PILL[1], "x1": PILL[2], "y1": PILL[3],
                     "color": median_color(*PILL, (img[..., 2] > img[..., 0] + 25) & (lum < 120))}
manifest["_order"] = {"feliz": feliz, "dia": dia, "prof": prof}
with open(f"{OUT}/layers.json", "w") as f:
    json.dump(manifest, f, indent=1)
print(json.dumps({k: v for k, v in manifest.items() if k.startswith("_")}))
