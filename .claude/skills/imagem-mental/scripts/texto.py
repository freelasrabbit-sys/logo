"""Medição, quebra de linha e desenho de textos (editável ou em curvas).

Usa as fontes de assets/fontes. O mesmo bloco de texto pode sair como
<text> (editável no CorelDRAW/Illustrator/Inkscape, exige a fonte instalada)
ou como <path> (curvas: idêntico em qualquer programa, sem depender de fonte).
"""
from __future__ import annotations

import os
from functools import lru_cache
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTES_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fontes")

PESOS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}
FAMILIAS = {"Poppins": [400, 500, 600, 700, 800], "Fredoka": [400, 500, 600, 700]}


def _peso_disponivel(familia: str, peso: int) -> int:
    pesos = FAMILIAS[familia]
    return min(pesos, key=lambda p: abs(p - peso))


@lru_cache(maxsize=None)
def carregar(familia: str, peso: int):
    peso = _peso_disponivel(familia, peso)
    caminho = os.path.join(FONTES_DIR, f"{familia}-{PESOS[peso]}.ttf")
    fonte = TTFont(caminho)
    return fonte, fonte.getGlyphSet(), fonte.getBestCmap(), fonte["head"].unitsPerEm, peso


def largura(txt: str, familia: str, peso: int, tamanho: float) -> float:
    fonte, gs, cmap, upm, _ = carregar(familia, peso)
    hmtx = fonte["hmtx"]
    total = 0
    for ch in txt:
        g = cmap.get(ord(ch)) or cmap.get(ord("?"))
        total += hmtx[g][0]
    return total * tamanho / upm


VOGAIS = set("aeiouáéíóúâêôãõàüAEIOUÁÉÍÓÚÂÊÔÃÕÀÜ")
GRUPOS = {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tr", "vr",
          "ch", "lh", "nh", "qu", "gu"}


def silabas_corte(palavra: str) -> list[int]:
    """Posições onde a palavra pode ser hifenizada (regras simples do português)."""
    p = palavra.lower()
    cortes = []
    i = 1
    while i < len(p) - 2:
        a, b, c = p[i - 1], p[i], p[i + 1]
        if a in VOGAIS and b not in VOGAIS and c in VOGAIS:  # v-cv
            cortes.append(i)
        elif a in VOGAIS and b not in VOGAIS and c not in VOGAIS and i + 2 < len(p):
            par = b + c
            if par in GRUPOS:  # v-ccv (pr, bl, ch, lh, nh...)
                cortes.append(i)
            else:  # vc-cv (rr, ss, sc, rn...)
                cortes.append(i + 1)
        i += 1
    # evita cortar logo após duas vogais (hiato/ditongo: "socioe-mocional")
    return [k for k in cortes if 2 <= k <= len(p) - 3 and not (p[k - 1] in VOGAIS and p[k - 2] in VOGAIS)]


def _hifenizar(palavra, familia, peso, tamanho, max_larg, ocupado):
    """Maior pedaço da palavra (com hífen) que cabe no espaço restante da linha."""
    melhor = None
    for k in silabas_corte(palavra):
        pedaco = palavra[:k] + "-"
        if largura((ocupado + " " if ocupado else "") + pedaco, familia, peso, tamanho) <= max_larg:
            melhor = k
    return melhor


def quebrar(txt: str, familia: str, peso: int, tamanho: float, max_larg: float,
            hifenizar: bool = False) -> list[str]:
    """Quebra por palavras. Respeita quebras manuais com '\\n'.

    Com hifenizar=True, palavras que não cabem sozinhas na linha são divididas com hífen.
    """
    linhas: list[str] = []
    for paragrafo in txt.split("\n"):
        atual = ""
        palavras = paragrafo.split()
        while palavras:
            palavra = palavras.pop(0)
            teste = f"{atual} {palavra}".strip()
            if largura(teste, familia, peso, tamanho) <= max_larg:
                atual = teste
                continue
            if hifenizar and largura(palavra, familia, peso, tamanho) > max_larg:
                k = _hifenizar(palavra, familia, peso, tamanho, max_larg, atual)
                if k is None and atual:
                    linhas.append(atual)
                    atual = ""
                    k = _hifenizar(palavra, familia, peso, tamanho, max_larg, "")
                if k is not None:
                    linhas.append(f"{atual} {palavra[:k]}-".strip())
                    atual = ""
                    palavras.insert(0, palavra[k:])
                    continue
            if atual:
                linhas.append(atual)
            atual = palavra
        linhas.append(atual)
    return linhas


def ajustar(txt, familia, peso, tamanho, max_larg, max_linhas, minimo=None, referencia=None):
    """Diminui o tamanho até o texto caber em max_linhas e max_larg."""
    minimo = minimo or tamanho * 0.55

    def cabe(linhas, t):
        return len(linhas) <= max_linhas and all(largura(l, familia, peso, t) <= max_larg for l in linhas)

    t = tamanho
    while True:
        linhas = quebrar(txt, familia, peso, t, max_larg)
        if cabe(linhas, t):
            return linhas, t
        # antes de reduzir muito a letra, tenta hifenizar palavras longas
        if t <= (referencia or tamanho) * 0.86:
            hif = quebrar(txt, familia, peso, t, max_larg, hifenizar=True)
            if cabe(hif, t):
                return hif, t
        if t <= minimo:
            return linhas, t
        t *= 0.94


def _linha_em_curvas(linha, familia, peso, tamanho, x, y_base):
    fonte, gs, cmap, upm, _ = carregar(familia, peso)
    hmtx = fonte["hmtx"]
    escala = tamanho / upm
    pen = SVGPathPen(gs)
    cursor = 0
    for ch in linha:
        g = cmap.get(ord(ch)) or cmap.get(ord("?"))
        tp = TransformPen(pen, (escala, 0, 0, -escala, x + cursor * escala, y_base))
        gs[g].draw(tp)
        cursor += hmtx[g][0]
    return pen.getCommands()


def bloco(
    txt,
    x,
    y,
    *,
    familia="Poppins",
    peso=600,
    tamanho=22,
    cor="#333333",
    max_larg=200,
    max_linhas=3,
    alinhamento="middle",  # start | middle | end
    vertical="middle",  # top | middle | bottom
    entrelinha=1.15,
    curvas=False,
    caixa_alta=False,
    id_=None,
    referencia=None,
):
    """Devolve (svg, altura_total, caixa) de um bloco de texto já quebrado e ajustado."""
    if caixa_alta:
        txt = txt.upper()
    linhas, t = ajustar(txt, familia, peso, tamanho, max_larg, max_linhas, referencia=referencia)
    _, _, _, _, peso_real = carregar(familia, peso)
    alt_linha = t * entrelinha
    altura = alt_linha * (len(linhas) - 1) + t * 0.72  # 0.72 ~ altura das maiúsculas
    if vertical == "middle":
        y0 = y - altura / 2 + t * 0.72
    elif vertical == "top":
        y0 = y + t * 0.72
    else:
        y0 = y - altura + t * 0.72

    id_attr = f' id="{id_}"' if id_ else ""
    rotulo = escape(txt.replace("\n", " "), {'"': "&quot;"})
    if curvas:
        d = []
        for i, linha in enumerate(linhas):
            w = largura(linha, familia, peso, t)
            dx = {"start": 0, "middle": -w / 2, "end": -w}[alinhamento]
            d.append(_linha_em_curvas(linha, familia, peso, t, x + dx, y0 + i * alt_linha))
        svg = f'<path{id_attr} data-texto="{rotulo}" fill="{cor}" d="{" ".join(d)}"/>'
    else:
        tspans = "".join(
            f'<tspan x="{x:.2f}" y="{y0 + i * alt_linha:.2f}">{escape(l)}</tspan>'
            for i, l in enumerate(linhas)
        )
        svg = (
            f'<text{id_attr} font-family="{familia}" font-weight="{peso_real}" '
            f'font-size="{t:.2f}" fill="{cor}" text-anchor="{alinhamento}">{tspans}</text>'
        )
    larg_max = max(largura(l, familia, peso, t) for l in linhas)
    xa = {"start": x, "middle": x - larg_max / 2, "end": x - larg_max}[alinhamento]
    topo = y0 - t * 0.72
    return svg, altura, (xa, topo - t * 0.25, xa + larg_max, topo + altura + t * 0.3)
