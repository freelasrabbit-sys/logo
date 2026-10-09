"""Separa o logotipo oficial (assets/logo_oficial.png) nas camadas que a animação move.

Nada é redesenhado: cada camada é recortada dos pixels do arquivo oficial. Os textos
brancos/azuis são separados do fundo pela própria cor (alpha = mistura texto/fundo),
de modo que caixa + textos recompostos reproduzem o arquivo original. A única área
completada é a borda da caixa escondida sob a aba, copiada da borda visível equivalente. Saída: logo_oficial/*.png (2x) e logo_oficial/layout.js.
Uso: python3 extract_logo.py
"""
import base64
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "logo_oficial")
SRC = os.path.join(HERE, "assets", "logo_oficial.png")

ORANGE = np.array([255, 80, 0], float)
NAVY = np.array([3, 39, 88], float)
WHITE = np.array([255, 255, 255], float)

# posição no quadro 1080x1920: mesma largura de caixa (741 px) e mesmo centro do logo do vídeo
BOX = (37, 121, 463, 386)          # caixa laranja no arquivo oficial (x0, y0, x1, y1 exclusivo)
TAB = (51, 75, 276, 152)           # aba azul "ESCOLA"
K = 741 / (BOX[2] - BOX[0])
CX, CY = (BOX[0] + BOX[2]) / 2, (77 + 419) / 2
FX, FY = 539.5, 927.0
UP = 2                              # camadas exportadas em 2x para nitidez nos zooms

src = Image.open(SRC).convert("RGB")
a = np.asarray(src).astype(float)
H, W = a.shape[:2]

# fundo branco = região branca conectada às bordas
near_white = a.min(2) > 245
bg = np.zeros_like(near_white)
bg[0, :] = bg[-1, :] = bg[:, 0] = bg[:, -1] = True
bg &= near_white
while True:
    grown = bg.copy()
    grown[1:] |= bg[:-1]
    grown[:-1] |= bg[1:]
    grown[:, 1:] |= bg[:, :-1]
    grown[:, :-1] |= bg[:, 1:]
    grown &= near_white
    if (grown == bg).all():
        break
    bg = grown
# borda (1-2 px) entre fundo e figura
edge = np.zeros_like(bg)
for dy in (-2, -1, 0, 1, 2):
    for dx in (-2, -1, 0, 1, 2):
        edge |= np.roll(np.roll(bg, dy, 0), dx, 1)
edge &= ~bg
interior = ~bg & ~edge


def frame_rect(x0, y0, x1, y1):
    return dict(left=FX + (x0 - CX) * K, top=FY + (y0 - CY) * K, w=(x1 - x0) * K, h=(y1 - y0) * K)


def save(name, rgb, alpha, rect):
    x0, y0, x1, y1 = rect
    rgba = np.zeros((y1 - y0, x1 - x0, 4))
    rgba[..., :3] = rgb
    rgba[..., 3] = np.clip(alpha[y0:y1, x0:x1], 0, 1) * 255
    im = Image.fromarray(rgba.round().astype(np.uint8), "RGBA")
    im = im.resize((round((x1 - x0) * K * UP), round((y1 - y0) * K * UP)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))
    return dict(src=f"logo_oficial/{name}.png", **frame_rect(*rect))


def only(alpha, rect):
    out = np.zeros_like(alpha)
    x0, y0, x1, y1 = rect
    out[y0:y1, x0:x1] = alpha[y0:y1, x0:x1]
    return out


def segments(alpha, rect, gap=1):
    """colunas com tinta dentro de rect -> lista de (x0, x1) por letra."""
    x0, y0, x1, y1 = rect
    cols = alpha[y0:y1, x0:x1].max(0) > 0.04
    segs, s = [], None
    for i, c in enumerate(list(cols) + [False]):
        if c and s is None:
            s = i
        elif not c and s is not None:
            segs.append((x0 + s, x0 + i))
            s = None
    # junta pedaços separados por menos de `gap` colunas
    out = []
    for sg in segs:
        if out and sg[0] - out[-1][1] < gap:
            out[-1] = (out[-1][0], sg[1])
        else:
            out.append(sg)
    return [(max(x0, s - 1), min(x1, e + 1)) for s, e in out]


os.makedirs(OUT, exist_ok=True)
L = {}

# ---- caixa laranja (sem os textos)
box_a = np.where(bg, 0.0, 1.0)
box_a[edge] = (255 - a[..., 2][edge]) / 255          # laranja x branco: canal B
# trecho escondido sob a aba: copia a borda superior/canto visíveis equivalentes
ty0, ty1 = 100, 160
straight = box_a[ty0:ty1, 300].copy()
for x in range(TAB[0] - 2, TAB[2] + 2):
    xs = (BOX[0] + BOX[2] - 1) - x                    # espelho horizontal (canto direito)
    col = box_a[ty0:ty1, xs] if x < 80 else straight
    box_a[ty0:ty1, x] = col
box_a = only(box_a, BOX)
L["box"] = save("caixa", ORANGE, box_a, BOX)

# ---- textos brancos dentro da caixa (B: laranja=0, branco=255)
txt_a = np.where(interior, a[..., 2] / 255, 0.0)
txt_a[: TAB[3] + 1] = 0
l2 = (BOX[0], 152, BOX[2], 296)                      # "São José"
l3 = (BOX[0], 296, BOX[2], 372)                      # "DE VILA MATILDE"
L["l2"] = [save(f"sao_jose_{i}", WHITE, txt_a, (s, l2[1], e, l2[3])) for i, (s, e) in enumerate(segments(txt_a, l2, gap=1))]
ys = np.where(txt_a[l3[1]:l3[3], l3[0]:l3[2]].max(1) > 0.04)[0]
xs = np.where(txt_a[l3[1]:l3[3], l3[0]:l3[2]].max(0) > 0.04)[0]
r3 = (l3[0] + xs[0] - 1, l3[1] + ys[0] - 1, l3[0] + xs[-1] + 2, l3[1] + ys[-1] + 2)
L["l3"] = save("de_vila_matilde", WHITE, txt_a, r3)

# ---- aba azul (sem "ESCOLA"); R separa azul de branco e de laranja (ambos R=255)
tab_a = (255 - a[..., 0]) / 252
tab_a[TAB[1] + 6:TAB[3] - 6, TAB[0] + 6:TAB[2] - 6] = 1   # miolo da aba (sob as letras)
tab_a = only(tab_a, TAB)
L["tab"] = save("aba", NAVY, tab_a, TAB)

# ---- "ESCOLA" (B: azul=88, branco=255)
esc_a = np.zeros((H, W))
reg = interior.copy()
reg[:, : TAB[0] + 3] = False
reg[:, TAB[2] - 3:] = False
reg[: TAB[1] + 3] = False
reg[TAB[3] - 4:] = False
esc_a[reg] = (a[..., 2][reg] - 88) / (255 - 88)
esc_box = (TAB[0], TAB[1], TAB[2], TAB[3])
L["l1"] = [save(f"escola_{i}", WHITE, esc_a, (s, esc_box[1], e, esc_box[3])) for i, (s, e) in enumerate(segments(esc_a, esc_box))]

# ---- "INSTITUTO DAS FILHAS DE SÃO JOSÉ" (R: azul=3, branco=255)
ser_a = np.zeros((H, W))
ser_a[BOX[3] + 2:] = (255 - a[BOX[3] + 2:, :, 0]) / 252
sr = (0, 388, W, 425)
segs = segments(ser_a, sr)
lx0, lx1 = segs[0][0], segs[-1][1]
L["serif"] = []
for i, (s, e) in enumerate(segs):
    d = save(f"instituto_{i}", NAVY, ser_a, (s, sr[1], e, sr[3]))
    d["frac"] = ((s + e) / 2 - lx0) / (lx1 - lx0)   # posição relativa na linha (para o tracking)
    L["serif"].append(d)

L["shadow"] = frame_rect(*BOX)
# máscaras (forma da caixa e da aba) embutidas: mask-image com URL de arquivo é bloqueada em file://
for k in ("box", "tab"):
    with open(os.path.join(HERE, L[k]["src"]), "rb") as f:
        L[k]["mask"] = "data:image/png;base64," + base64.b64encode(f.read()).decode()
with open(os.path.join(OUT, "layout.js"), "w") as f:
    f.write("window.LAYOUT = " + json.dumps(L, indent=1) + ";\n")

# ---- verificação: recompõe as camadas sobre branco e compara com o original
comp = np.ones((H, W, 3)) * WHITE
for col, al in ((ORANGE, box_a), (WHITE, txt_a), (NAVY, tab_a), (WHITE, esc_a), (NAVY, ser_a)):
    al = np.clip(al, 0, 1)[..., None]
    comp = comp * (1 - al) + col * al
err = np.abs(comp - a)
print("letras: ESCOLA", len(L["l1"]), "| São José", len(L["l2"]), "| Instituto", len(L["serif"]))
print(f"erro de recomposição: médio {err.mean():.3f}, p99.9 {np.percentile(err, 99.9):.1f}, máx {err.max():.0f} (0-255)")
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
Image.fromarray(comp.round().astype(np.uint8)).save(os.path.join(HERE, "build", "logo_recomposto.png"))
