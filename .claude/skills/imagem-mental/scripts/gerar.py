#!/usr/bin/env python3
"""Gera uma imagem mental a partir de um arquivo de configuração JSON.

Uso:
    python3 gerar.py config.json                     # PNG (aprovação)
    python3 gerar.py config.json --formatos png,svg,pdf
    python3 gerar.py config.json --previa            # todos os layouts lado a lado
    python3 gerar.py config.json --layout petalas --fundo "#0b2a4a"

Saídas (pasta --saida, padrão: ao lado do JSON, em ./saida):
    <nome>.png             imagem para aprovação / redes sociais
    <nome>.pdf             vetorial, textos em curvas (impressão, CorelDRAW)
    <nome>_editavel.svg    camadas nomeadas + textos editáveis (requer as fontes)
    <nome>_curvas.svg      camadas nomeadas + textos convertidos em curvas
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

import cairosvg  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import cores as C  # noqa: E402
import icones  # noqa: E402
from layouts import LAYOUTS, Ctx  # noqa: E402

# largura, altura, unidade. Formatos em mm usam 10 unidades por mm no viewBox.
FORMATOS = {
    "quadrado": (1080, 1080, "px"),
    "retrato": (1080, 1350, "px"),
    "stories": (1080, 1920, "px"),
    "paisagem": (1920, 1080, "px"),
    "a4": (210, 297, "mm"),
    "a4-paisagem": (297, 210, "mm"),
    "a3": (297, 420, "mm"),
}

CAMADAS = ["Fundo", "Decoração", "Formas", "Ícones", "Textos", "Logo"]


def carregar_config(caminho):
    with open(caminho, encoding="utf-8") as f:
        cfg = json.load(f)
    base = os.path.dirname(os.path.abspath(caminho))
    if not os.path.isabs(cfg["logo"]):
        cfg["logo"] = os.path.join(base, cfg["logo"])
    estilo = cfg.get("estilo", "classico")  # infantil | classico
    cfg.setdefault("fonte", "Fredoka" if estilo == "infantil" else "Poppins")
    cfg.setdefault("estilo_icone", "solido" if estilo == "infantil" else "linha")
    solido = cfg["estilo_icone"] == "solido"
    itens = []
    for it in cfg["itens"]:
        it = {"texto": it} if isinstance(it, str) else dict(it)
        if not it.get("icone") or not icones.existe(it["icone"]):
            pedido = it.get("icone")
            it["icone"] = icones.sugerir(it.get("icone") or it["texto"], 1, solido)[0]
            if pedido:
                print(f"aviso: ícone '{pedido}' não existe; usando '{it['icone']}'", file=sys.stderr)
        itens.append(it)
    cfg["itens"] = itens
    # conjunto coerente: se algum ícone não tiver versão preenchida, todos saem em traço grosso
    if solido and not all(icones.tem_solido(i["icone"]) for i in itens):
        faltam = [i["icone"] for i in itens if not icones.tem_solido(i["icone"])]
        print(f"aviso: sem versão preenchida para {faltam}; usando traço grosso em todos", file=sys.stderr)
        cfg["estilo_icone"] = "negrito"
    return cfg, base


def logo_svg_inline(caminho):
    """Conteúdo de um logo SVG para embutir como curvas (sem <image>)."""
    with open(caminho, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"<svg\b[^>]*>", txt)
    vb = re.search(r'viewBox="([^"]+)"', m.group(0)) if m else None
    if not m or not vb:
        return None
    x, y, w, h = (float(v) for v in vb.group(1).replace(",", " ").split())
    interno = txt[m.end():txt.rfind("</svg>")]
    return interno, x, y, w, h


def montar_svg(cfg, layout, curvas, formato, fundo):
    func, modo_padrao, _ = LAYOUTS[layout]
    paleta = cfg.get("cores") or C.paleta_do_logo(cfg["logo"])
    modo = cfg.get("modo_cor") or modo_padrao
    cores_itens = cfg.get("cores_itens") or C.expandir(paleta, len(cfg["itens"]), modo)
    uri, lw, lh = C.logo_data_uri(cfg["logo"])
    inline = logo_svg_inline(cfg["logo"]) if cfg["logo"].lower().endswith(".svg") else None
    if inline:
        lw, lh = inline[3], inline[4]
    ctx = Ctx(itens=cfg["itens"], cores_itens=cores_itens, paleta=paleta, logo_uri=uri,
              logo_w=lw, logo_h=lh, fundo=fundo, familia=cfg.get("fonte", "Poppins"),
              curvas=curvas, slogan=cfg.get("slogan", ""), sombra=cfg.get("sombra", True),
              estilo_icone=cfg.get("estilo_icone", "linha"), logo_inline=inline)
    D = func(ctx)
    # todos os tópicos com o mesmo tamanho de letra: refaz usando o menor tamanho que coube
    if ctx.tamanhos_rotulo and min(ctx.tamanhos_rotulo) < max(ctx.tamanhos_rotulo) * 0.97:
        ctx.teto_rotulo = min(ctx.tamanhos_rotulo)
        ctx.limites, ctx.tamanhos_rotulo = [], []
        D = func(ctx)

    x0, y0, x1, y1 = D.caixa
    for a, b, c, d in ctx.limites:  # garante que nenhum texto fique cortado
        x0, y0, x1, y1 = min(x0, a), min(y0, b), max(x1, c), max(y1, d)
    if ctx.slogan and not D.usou_slogan:
        svg, alt = ctx.texto(ctx.slogan, 500, y1 + 40, peso=600, tamanho=30,
                             cor=C.legivel_em(C.escurecer(ctx.principal, 0.1), fundo, 4),
                             max_larg=min(x1 - x0, 820), max_linhas=2, vertical="top", id_="slogan")
        D.add("Textos", svg)
        y1 += 40 + alt + 20

    W, H, unidade = FORMATOS[formato]
    vw, vh = (W * 10, H * 10) if unidade == "mm" else (W, H)
    margem = 0.06 * min(vw, vh)
    esc = min((vw - 2 * margem) / (x1 - x0), (vh - 2 * margem) / (y1 - y0))
    tx = (vw - (x1 - x0) * esc) / 2 - x0 * esc
    ty = (vh - (y1 - y0) * esc) / 2 - y0 * esc
    transf = f"translate({tx:.2f} {ty:.2f}) scale({esc:.4f})"

    grupos = [f'<g id="camada-fundo" inkscape:groupmode="layer" inkscape:label="Fundo">'
              f'<rect id="fundo" width="{vw}" height="{vh}" fill="{fundo}"/></g>']
    for nome in CAMADAS[1:]:
        conteudo = "".join(s for s in D.camadas[nome] if s)
        if conteudo:
            slug = re.sub(r"[^a-z]", "", nome.lower().replace("í", "i").replace("ç", "c").replace("ã", "a"))
            grupos.append(f'<g id="camada-{slug}" inkscape:groupmode="layer" inkscape:label="{nome}" '
                          f'transform="{transf}">{conteudo}</g>')
    tamanho = f'width="{W}mm" height="{H}mm"' if unidade == "mm" else f'width="{W}" height="{H}"'
    titulo = cfg.get("escola", "Imagem mental")
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" {tamanho} '
            f'viewBox="0 0 {vw} {vh}"><title>{titulo} - imagem mental</title>'
            f'<defs>{"".join(D.defs)}</defs>{"".join(grupos)}</svg>'), (W, H, unidade)


def png_de_svg(svg: str, dims, largura_px=None) -> bytes:
    W, H, unidade = dims
    if largura_px is None:
        largura_px = round(W / 25.4 * 300) if unidade == "mm" else W * 2
    return cairosvg.svg2png(bytestring=svg.encode(), output_width=largura_px,
                            output_height=round(largura_px * H / W))


def nome_arquivo(cfg, layout):
    base = cfg.get("nome_arquivo") or f"imagem-mental-{cfg.get('escola', 'escola')}-{layout}"
    base = base.lower()
    for a, b in zip("áàâãéêíóôõúçü ", "aaaaeeioooucu-"):
        base = base.replace(a, b)
    return re.sub(r"[^a-z0-9_-]", "", base)


def previa(cfg, saida, formato, fundo, layouts=None, rotulo="previa-layouts", lado=520):
    """Uma folha com vários layouts lado a lado, para escolher qual seguir."""
    miniaturas = []
    for nome in layouts or LAYOUTS:
        svg, dims = montar_svg(cfg, nome, True, formato, fundo)
        img = Image.open(io.BytesIO(png_de_svg(svg, dims, lado))).convert("RGB")
        miniaturas.append((nome, img))
    col = min(4, len(miniaturas))
    lin = (len(miniaturas) + col - 1) // col
    w, h = miniaturas[0][1].size
    folha = Image.new("RGB", (col * (w + 20) + 20, lin * (h + 60) + 20), "#e6e6e6")
    d = ImageDraw.Draw(folha)
    for k, (nome, img) in enumerate(miniaturas):
        x, y = 20 + (k % col) * (w + 20), 20 + (k // col) * (h + 60)
        folha.paste(img, (x, y))
        d.text((x + 6, y + h + 12), nome, fill="#222222", font_size=26)
    caminho = os.path.join(saida, nome_arquivo(cfg, rotulo) + ".png")
    folha.save(caminho)
    return caminho


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--layout", choices=list(LAYOUTS))
    ap.add_argument("--formato", choices=list(FORMATOS))
    ap.add_argument("--fundo", help="cor do fundo, ex.: #ffffff (padrão) ou #0b2a4a")
    ap.add_argument("--formatos", default="png", help="png,pdf,svg (svg gera editável e em curvas)")
    ap.add_argument("--saida")
    ap.add_argument("--largura-png", type=int, help="largura do PNG em pixels")
    ap.add_argument("--previa", action="store_true", help="gera folha com todos os layouts")
    ap.add_argument("--opcoes", help="3 layouts separados por vírgula: gera um PNG de cada + folha comparativa")
    a = ap.parse_args()

    cfg, base = carregar_config(a.config)
    layout = a.layout or cfg.get("layout", "arco")
    formato = a.formato or cfg.get("formato", "quadrado")
    fundo = a.fundo or cfg.get("fundo", "#ffffff")
    saida = a.saida or os.path.join(base, "saida")
    os.makedirs(saida, exist_ok=True)

    print("paleta:", cfg.get("cores") or C.paleta_do_logo(cfg["logo"]))
    print("ícones:", ", ".join(f"{i['texto']!r}->{i['icone']}" for i in cfg["itens"]))
    if a.previa:
        print(previa(cfg, saida, formato, fundo))
        return
    if a.opcoes:
        escolhidos = [x.strip() for x in a.opcoes.split(",") if x.strip()]
        for k, lay in enumerate(escolhidos, 1):
            svg, dims = montar_svg(cfg, lay, True, formato, fundo)
            p = os.path.join(saida, f"{nome_arquivo(cfg, lay)}-opcao{k}.png")
            with open(p, "wb") as f:
                f.write(png_de_svg(svg, dims, a.largura_png))
            print(p)
        print(previa(cfg, saida, formato, fundo, escolhidos, "opcoes", 900))
        return

    nome = nome_arquivo(cfg, layout)
    pedidos = {f.strip() for f in a.formatos.split(",")}
    svg_curvas, dims = montar_svg(cfg, layout, True, formato, fundo)
    gerados = []
    if "png" in pedidos:
        p = os.path.join(saida, nome + ".png")
        with open(p, "wb") as f:
            f.write(png_de_svg(svg_curvas, dims, a.largura_png))
        gerados.append(p)
    if "pdf" in pedidos:
        p = os.path.join(saida, nome + ".pdf")
        cairosvg.svg2pdf(bytestring=svg_curvas.encode(), write_to=p)
        gerados.append(p)
    if "svg" in pedidos:
        p = os.path.join(saida, nome + "_curvas.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg_curvas)
        gerados.append(p)
        svg_edit, _ = montar_svg(cfg, layout, False, formato, fundo)
        p = os.path.join(saida, nome + "_editavel.svg")
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg_edit)
        gerados.append(p)
    for p in gerados:
        print(p)


if __name__ == "__main__":
    main()
