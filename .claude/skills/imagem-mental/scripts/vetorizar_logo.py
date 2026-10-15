#!/usr/bin/env python3
"""Vetoriza um logo raster (PNG/JPG) em SVG, uma camada de curvas por cor.

Funciona bem para logos de cores chapadas (tipografia, formas geométricas).
Logos com degradê, foto ou muitos detalhes finos devem ser pedidos em vetor à escola.

Uso:
    python3 vetorizar_logo.py logo.jpg --cores "#012650,#830006" -o logo.svg
    python3 vetorizar_logo.py logo.png            # cores detectadas automaticamente
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import potrace
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import cores as C  # noqa: E402


def _caminho(curva, esc):
    p = curva.start_point
    d = [f"M{p.x * esc:.2f} {p.y * esc:.2f}"]
    for seg in curva.segments:
        if seg.is_corner:
            d.append(f"L{seg.c.x * esc:.2f} {seg.c.y * esc:.2f} L{seg.end_point.x * esc:.2f} {seg.end_point.y * esc:.2f}")
        else:
            d.append(f"C{seg.c1.x * esc:.2f} {seg.c1.y * esc:.2f} {seg.c2.x * esc:.2f} {seg.c2.y * esc:.2f} "
                     f"{seg.end_point.x * esc:.2f} {seg.end_point.y * esc:.2f}")
    return " ".join(d) + "Z"


def vetorizar(caminho, cores_hex=None, ampliar=3, detalhe_min=6):
    img = C.abrir_logo(caminho)
    if img.split()[-1].getextrema()[0] >= 250:
        img = C.fundo_branco_para_transparente(img)
    img = C.recortar(img)
    w0, h0 = img.size
    img = img.resize((w0 * ampliar, h0 * ampliar), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(ampliar * 0.6))  # suaviza serrilhado de JPG
    cores_hex = cores_hex or C.paleta_do_logo(caminho)
    fundo = Image.new("RGBA", img.size, (255, 255, 255, 255))
    rgb = np.asarray(Image.alpha_composite(fundo, img).convert("RGB"), dtype=np.int32)

    # cada pixel vai para a cor mais próxima (cores da marca + branco do fundo)
    refs = np.array([C.hex_rgb(c) for c in cores_hex] + [(255, 255, 255)], dtype=np.int32)
    dist = ((rgb[:, :, None, :] - refs[None, None, :, :]) ** 2).sum(-1)
    rotulo = dist.argmin(-1)

    esc = 1 / ampliar
    camadas = []
    for k, cor in enumerate(cores_hex):
        mascara = rotulo == k
        if mascara.sum() < 50:
            continue
        trilhas = potrace.Bitmap(~mascara).trace(  # potracer: False = tinta
            turdsize=detalhe_min * ampliar, alphamax=1.0,
                                                opticurve=True, opttolerance=0.2)
        d = " ".join(_caminho(c, esc) for c in trilhas)
        camadas.append(f'<path id="logo-cor-{k + 1}" fill="{cor}" fill-rule="evenodd" d="{d}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w0}" height="{h0}" viewBox="0 0 {w0} {h0}">'
            f'{"".join(camadas)}</svg>')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logo")
    ap.add_argument("--cores", help="cores do logo em hex, separadas por vírgula")
    ap.add_argument("-o", "--saida")
    a = ap.parse_args()
    cores_hex = [c.strip() for c in a.cores.split(",")] if a.cores else None
    svg = vetorizar(a.logo, cores_hex)
    saida = a.saida or os.path.splitext(a.logo)[0] + "_vetor.svg"
    with open(saida, "w", encoding="utf-8") as f:
        f.write(svg)
    print(saida)


if __name__ == "__main__":
    main()
