"""Paleta a partir do logo, utilitários de cor e preparo do logo para embutir."""
from __future__ import annotations

import base64
import colorsys
import io
import os

from PIL import Image, ImageChops


def hex_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def misturar(a: str, b: str, t: float) -> str:
    """Interpola a -> b (t=0 devolve a, t=1 devolve b)."""
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex(x + (y - x) * t for x, y in zip(ra, rb))


def clarear(c: str, t: float) -> str:
    return misturar(c, "#ffffff", t)


def escurecer(c: str, t: float) -> str:
    return misturar(c, "#000000", t)


def luminancia(c: str) -> float:
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (canal(v) for v in hex_rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def texto_sobre(fundo: str, escuro="#2b2b2b") -> str:
    """Branco quando o contraste basta para texto em negrito (>= 3:1); senão, o de mais contraste."""
    if contraste(fundo, "#ffffff") >= 3.0:
        return "#ffffff"
    return "#ffffff" if contraste(fundo, "#ffffff") >= contraste(fundo, escuro) else escuro


def legivel_em(cor: str, fundo: str, minimo=3.0) -> str:
    """Escurece (ou clareia) `cor` até ter contraste mínimo com `fundo`."""
    c = cor
    for _ in range(12):
        if contraste(c, fundo) >= minimo:
            return c
        c = escurecer(c, 0.12) if luminancia(fundo) > 0.4 else clarear(c, 0.12)
    return c


def _sat_luz(c):
    r, g, b = (v / 255 for v in hex_rgb(c))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


# --------------------------------------------------------------------------- logo

def abrir_logo(caminho: str) -> Image.Image:
    if caminho.lower().endswith(".svg"):
        import cairosvg

        png = cairosvg.svg2png(url=caminho, output_width=1200)
        return Image.open(io.BytesIO(png)).convert("RGBA")
    return Image.open(caminho).convert("RGBA")


def recortar(img: Image.Image, tolerancia=18) -> Image.Image:
    """Remove a margem vazia (transparente ou da cor do canto) em volta do logo."""
    alfa = img.split()[-1]
    if alfa.getextrema()[0] < 250:
        caixa = alfa.point(lambda a: 255 if a > 10 else 0).getbbox()
    else:
        canto = Image.new("RGBA", img.size, img.getpixel((0, 0)))
        dif = ImageChops.difference(img, canto).convert("L")
        caixa = dif.point(lambda v: 255 if v > tolerancia else 0).getbbox()
    return img.crop(caixa) if caixa else img


def fundo_branco_para_transparente(img: Image.Image, limite=245) -> Image.Image:
    """Para logos JPG com fundo branco: deixa o branco do entorno transparente.

    Só remove o branco conectado às bordas (flood fill), preservando brancos
    internos do desenho.
    """
    from PIL import ImageDraw

    rgb = img.convert("RGB")
    marcado = rgb.copy()
    w, h = rgb.size
    sentinela = (255, 0, 254)
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if min(rgb.getpixel(xy)) >= limite:
            ImageDraw.floodfill(marcado, xy, sentinela, thresh=255 - limite + 8)
    mascara = Image.eval(
        ImageChops.difference(marcado, Image.new("RGB", (w, h), sentinela)).convert("L"),
        lambda v: 0 if v < 4 else 255,
    )
    saida = img.copy()
    saida.putalpha(ImageChops.multiply(img.split()[-1], mascara))
    return saida


def logo_data_uri(caminho: str, max_lado=1400):
    """Devolve (data_uri, largura, altura) do logo pronto para <image>."""
    if caminho.lower().endswith(".svg"):
        with open(caminho, "rb") as f:
            dados = f.read()
        img = abrir_logo(caminho)
        w, h = recortar(img).size
        return "data:image/svg+xml;base64," + base64.b64encode(dados).decode(), w, h
    img = abrir_logo(caminho)
    if img.split()[-1].getextrema()[0] >= 250:
        img = fundo_branco_para_transparente(img)
    img = recortar(img)
    img.thumbnail((max_lado, max_lado), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), *img.size


# ------------------------------------------------------------------------ paleta

def _mesmo_tom(a, b) -> bool:
    """Tons da mesma cor (ex.: verde e verde-claro do antisserrilhado)."""
    ha, sa, la = _sat_luz(a)
    hb, sb, lb = _sat_luz(b)
    dh = min(abs(ha - hb), 1 - abs(ha - hb))
    return dh < 0.045 or sum((x - y) ** 2 for x, y in zip(hex_rgb(a), hex_rgb(b))) ** 0.5 < 50


def paleta_do_logo(caminho: str, n=5) -> list[str]:
    """Cores marcantes do logo, da mais presente para a menos presente.

    Ignora branco, cinzas e quase-preto, e junta tons muito parecidos.
    """
    img = abrir_logo(caminho)
    img.thumbnail((240, 240))
    fundo = Image.new("RGBA", img.size, (255, 255, 255, 255))
    rgb = Image.alpha_composite(fundo, img).convert("RGB")
    q = rgb.quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    contagem = sorted(q.getcolors(), reverse=True)
    cores = []
    for qtd, idx in contagem:
        c = rgb_hex(pal[idx * 3 : idx * 3 + 3])
        _, s, l = _sat_luz(c)
        if l > 0.9 or l < 0.12 or s < 0.25:
            continue
        if any(_mesmo_tom(c, o) for o in cores):
            continue
        cores.append(c)
    if not cores:  # logo monocromático/escuro
        cores = ["#1f4e9c"]
    return cores[:n]


# Paletas de apoio, inspiradas nos modelos de referência
ARCO_IRIS = ["#f6b40e", "#3f63b0", "#0f7a3d", "#9b1f48", "#f26b0f", "#00a7c8", "#e63329", "#7a3fa0"]
VIBRANTE = ["#1b8fd6", "#f39200", "#0b4fa3", "#e30613", "#00b4e6", "#2a9fd8", "#7ab51d", "#8e44ad"]


def expandir(base: list[str], n: int, modo="marca") -> list[str]:
    """Gera n cores para os itens.

    modo='marca'      -> todas na cor principal (ex.: modelo Athena)
    modo='alternada'  -> alterna as cores do logo (ex.: Sagaz, Pistori)
    modo='arco-iris'  -> cores das paletas de apoio, começando pelas do logo
    """
    if modo == "marca":
        return [base[0]] * n
    if modo == "alternada":
        cores = list(base)
        i = 0
        while len(cores) < n:  # completa com variações das cores da marca
            c = base[i % len(base)]
            cores.append(escurecer(c, 0.18) if (i // len(base)) % 2 == 0 else clarear(c, 0.2))
            i += 1
        return [cores[i % len(cores)] for i in range(n)]
    extra = [c for c in ARCO_IRIS if all(
        sum((x - y) ** 2 for x, y in zip(hex_rgb(c), hex_rgb(b))) ** 0.5 > 70 for b in base)]
    cores = (list(base) + extra + VIBRANTE)[: max(n, 1)]
    return cores[:n]


if __name__ == "__main__":
    import sys

    for c in sys.argv[1:]:
        print(os.path.basename(c), paleta_do_logo(c))
