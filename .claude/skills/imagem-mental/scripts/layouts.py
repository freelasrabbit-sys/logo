"""Layouts de imagem mental, cada um inspirado num modelo de referência.

Todos desenham num espaço de ~1000 x 1000 unidades com o centro em (500, 500).
Cada função recebe um `Ctx` e devolve um `Desenho` com as camadas preenchidas
e a caixa ocupada (usada depois para enquadrar no formato final).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cores as C
import icones
import texto


# ----------------------------------------------------------------------------- base

@dataclass
class Desenho:
    camadas: dict = field(default_factory=lambda: {
        "Decoração": [], "Formas": [], "Ícones": [], "Textos": [], "Logo": []})
    defs: list = field(default_factory=list)
    caixa: tuple = (0, 0, 1000, 1000)
    usou_slogan: bool = False

    def add(self, camada, svg):
        self.camadas[camada].append(svg)


@dataclass
class Ctx:
    itens: list  # [{"texto": str, "icone": str}]
    cores_itens: list  # uma cor por item
    paleta: list  # cores da marca (logo)
    logo_uri: str
    logo_w: float
    logo_h: float
    fundo: str = "#ffffff"
    familia: str = "Poppins"
    curvas: bool = True
    slogan: str = ""
    sombra: bool = True
    estilo_icone: str = "linha"  # linha | solido | negrito
    limites: list = field(default_factory=list)
    logo_inline: tuple | None = None  # (conteúdo, x, y, largura, altura do viewBox) de logo SVG
    teto_rotulo: float | None = None  # tamanho único para todos os tópicos (2ª passada)
    tamanhos_rotulo: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.itens)

    @property
    def principal(self):
        return self.paleta[0]

    def cor(self, i):
        return self.paleta[i % len(self.paleta)]

    @property
    def texto_fora(self):
        """Cor para textos escritos direto sobre o fundo."""
        return C.texto_sobre(self.fundo, "#3a3a3a")

    def texto(self, txt, x, y, **kw):
        kw.setdefault("familia", self.familia)
        kw.setdefault("curvas", self.curvas)
        svg, altura, caixa = texto.bloco(txt, x, y, **kw)
        self.limites.append(caixa)
        return svg, altura

    def rotulo(self, i, x, y, *, tamanho, max_larg, max_linhas=3, peso=600, cor="#333333",
               alinhamento="middle", vertical="middle", caixa_alta=False, cor_desc=None, id_=None):
        """Título do item e, se houver, a descrição em letra menor logo abaixo."""
        item = self.itens[i]
        desc = (item.get("descricao") or "").strip()
        comum = dict(alinhamento=alinhamento, max_larg=max_larg)
        ref = tamanho  # tamanho pedido pelo layout, base para decidir quando hifenizar
        if self.teto_rotulo:
            tamanho = min(tamanho, self.teto_rotulo)
        titulo_cmp = item["texto"].upper() if caixa_alta else item["texto"]
        self.tamanhos_rotulo.append(texto.ajustar(titulo_cmp, self.familia, peso, tamanho, max_larg,
                                                  min(max_linhas, 2) if desc else max_linhas,
                                                  referencia=ref)[1])
        if not desc:
            return self.texto(item["texto"], x, y, tamanho=tamanho, peso=peso, cor=cor, max_linhas=max_linhas,
                              referencia=ref,
                              vertical=vertical, caixa_alta=caixa_alta, id_=f"texto-{i + 1}", **comum)
        titulo = item["texto"].upper() if caixa_alta else item["texto"]
        lt, tt = texto.ajustar(titulo, self.familia, peso, tamanho * 0.95, max_larg, min(max_linhas, 2))
        ld, td = texto.ajustar(desc, self.familia, 400, max(tt * 0.74, 15), max_larg * 1.08,
                               max(max_linhas, 3), minimo=13)
        h_t = tt * 1.15 * (len(lt) - 1) + tt * 0.72
        h_d = td * 1.25 * (len(ld) - 1) + td * 0.72
        vao = tt * 0.5
        total = h_t + vao + h_d
        topo = {"middle": y - total / 2, "top": y, "bottom": y - total}[vertical]
        s1, _ = self.texto(titulo, x, topo, tamanho=tt, peso=peso, cor=cor, max_linhas=2,
                           vertical="top", id_=f"titulo-{i + 1}", **comum)
        s2, _ = self.texto(desc, x, topo + h_t + vao, tamanho=td, peso=400, cor=cor_desc or cor,
                           max_linhas=len(ld), vertical="top", entrelinha=1.25, alinhamento=alinhamento,
                           max_larg=max_larg * 1.08, id_=f"descricao-{i + 1}")
        return f'<g id="texto-{i + 1}">{s1}{s2}</g>', total

    def icone(self, i, cx, cy, tam, cor, espessura=1.6):
        return icones.svg(self.itens[i]["icone"], cx, cy, tam, cor, espessura, id_=f"icone-{i + 1}",
                          estilo=self.estilo_icone)

    def logo(self, cx, cy, max_w, max_h):
        esc = min(max_w / self.logo_w, max_h / self.logo_h)
        w, h = self.logo_w * esc, self.logo_h * esc
        if self.logo_inline:  # logo vetorial: entra como curvas, editável no CorelDRAW
            interno, vx, vy, vw, vh = self.logo_inline
            e = w / vw
            return (f'<g id="logo-escola" transform="translate({cx - w / 2 - vx * e:.2f} '
                    f'{cy - h / 2 - vy * e:.2f}) scale({e:.5f})">{interno}</g>'), w, h
        return (f'<image id="logo-escola" x="{cx - w / 2:.2f}" y="{cy - h / 2:.2f}" '
                f'width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="xMidYMid meet" '
                f'href="{self.logo_uri}" xlink:href="{self.logo_uri}"/>'), w, h

    def logo_no_circulo(self, cx, cy, raio):
        """Maior logo que cabe dentro de um círculo."""
        a = self.logo_w / self.logo_h
        w = 2 * raio * a / math.sqrt(1 + a * a)
        return self.logo(cx, cy, w, w / a)


def polar(cx, cy, r, ang):
    a = math.radians(ang)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def setor(cx, cy, r_in, r_out, a0, a1):
    """Setor de anel de a0 a a1 (graus, sentido horário da tela)."""
    grande = 1 if (a1 - a0) % 360 > 180 else 0
    x0, y0 = polar(cx, cy, r_out, a0)
    x1, y1 = polar(cx, cy, r_out, a1)
    x2, y2 = polar(cx, cy, r_in, a1)
    x3, y3 = polar(cx, cy, r_in, a0)
    return (f"M{x0:.2f} {y0:.2f} A{r_out} {r_out} 0 {grande} 1 {x1:.2f} {y1:.2f} "
            f"L{x2:.2f} {y2:.2f} A{r_in} {r_in} 0 {grande} 0 {x3:.2f} {y3:.2f}Z")


def ancora(ang):
    """Alinhamento do rótulo conforme o lado em que ele fica."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    h = "start" if c > 0.35 else "end" if c < -0.35 else "middle"
    v = "bottom" if s < -0.6 else "top" if s > 0.6 else "middle"
    return h, v


def sombra(d, ctx, dy=7, opac=0.10):
    if not ctx.sombra:
        return ""
    return f'<path d="{d}" fill="#000000" fill-opacity="{opac}" transform="translate(0 {dy})"/>'


def circulo_d(cx, cy, r):
    return (f"M{cx - r:.2f} {cy:.2f} a{r:.2f} {r:.2f} 0 1 0 {2 * r:.2f} 0 "
            f"a{r:.2f} {r:.2f} 0 1 0 {-2 * r:.2f} 0Z")


# ------------------------------------------------------------------- 1. ARCO (Athena)

def arco(ctx: Ctx) -> Desenho:
    """Anel em forma de 'C' aberto à direita; ícones no anel, rótulos por fora."""
    D = Desenho()
    cx, cy, r_in, r_out = 500, 500, 190, 305
    abertura = 80
    inicio, fim = -abertura / 2, -(360 - abertura / 2)  # anda no sentido anti-horário
    passo = (inicio - fim) / ctx.n
    D.add("Decoração", f'<path id="contorno" d="{setor(cx, cy, r_in - 9, r_out + 9, fim - 2.2, inicio + 2.2)}" '
                       f'fill="{C.clarear(ctx.principal, 0.82)}"/>')
    for i in range(ctx.n):
        a1 = inicio - i * passo
        a0 = a1 - passo
        meio = (a0 + a1) / 2
        cor = ctx.cores_itens[i]
        D.add("Formas", f'<path id="segmento-{i + 1}" d="{setor(cx, cy, r_in, r_out, a0, a1)}" fill="{cor}" '
                        f'stroke="{ctx.fundo}" stroke-width="7" stroke-linejoin="round"/>')
        ix, iy = polar(cx, cy, (r_in + r_out) / 2, meio)
        D.add("Ícones", ctx.icone(i, ix, iy, 62, C.texto_sobre(cor)))
        tx, ty = polar(cx, cy, r_out + 30, meio)
        h, v = ancora(meio)
        svg, _ = ctx.rotulo(i, tx, ty, peso=500, tamanho=25, cor=ctx.texto_fora,
                           max_larg=250, max_linhas=3, alinhamento=h, vertical=v)
        D.add("Textos", svg)
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{r_in - 9}" fill="#ffffff"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, r_in - 22)[0])
    D.caixa = (90, 120, 910, 880)
    return D


# ------------------------------------------------------------- 2. ANEL (Koala)

def anel(ctx: Ctx) -> Desenho:
    """Anel completo dividido em fatias, com selo do ícone e texto dentro de cada fatia."""
    D = Desenho()
    cx, cy, r_in, r_out = 500, 500, 165, 360
    passo = 360 / ctx.n
    tinta = C.clarear(ctx.principal, 0.55)
    escuro = C.legivel_em(C.escurecer(ctx.principal, 0.15), tinta, 3.2)
    for i in range(ctx.n):
        a0 = -90 - passo / 2 + i * passo
        a1 = a0 + passo
        meio = a0 + passo / 2
        cor = ctx.cores_itens[i] if len(set(ctx.cores_itens)) > 1 else tinta
        d = setor(cx, cy, r_in, r_out, a0, a1)
        D.add("Formas", f'<path id="fatia-{i + 1}" d="{d}" fill="{cor}" stroke="{ctx.fundo}" '
                        f'stroke-width="14" stroke-linejoin="round"/>')
        bx, by = polar(cx, cy, r_out - 62, meio)
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{bx:.2f}" cy="{by:.2f}" r="36" fill="#ffffff" '
                        f'stroke="{escuro if cor == tinta else cor}" stroke-width="3"/>')
        D.add("Ícones", ctx.icone(i, bx, by, 40, escuro if cor == tinta else C.escurecer(cor, 0.1)))
        rt = (r_in + r_out - 124) / 2 + 6
        tx, ty = polar(cx, cy, rt, meio)
        corda = 2 * rt * math.sin(math.radians(passo / 2))
        cor_txt = escuro if cor == tinta else C.texto_sobre(cor)
        svg, _ = ctx.rotulo(i, tx, ty, peso=600, tamanho=21, cor=cor_txt,
                           max_larg=min(corda * 0.78, 190), max_linhas=3)
        D.add("Textos", svg)
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{r_in - 10}" fill="#ffffff"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, r_in - 22)[0])
    D.caixa = (130, 130, 870, 870)
    return D


# ------------------------------------------------------- 3. LEQUE (Criança Feliz)

def leque(ctx: Ctx) -> Desenho:
    """Meia-lua em leque, cada fatia de uma cor, com o logo na base."""
    D = Desenho()
    cx, cy, r_in, r_out = 500, 640, 235, 460
    a_ini, a_fim = 172, 368
    passo = (a_fim - a_ini) / ctx.n
    for i in range(ctx.n):
        a0 = a_ini + i * passo
        a1 = a0 + passo
        meio = (a0 + a1) / 2
        cor = ctx.cores_itens[i]
        d = setor(cx, cy, r_in, r_out, a0, a1)
        D.add("Formas", f'<path id="fatia-{i + 1}" d="{d}" fill="{cor}"/>')
        cor_txt = C.texto_sobre(cor)
        ix, iy = polar(cx, cy, r_out - 78, meio)
        D.add("Ícones", ctx.icone(i, ix, iy, 58, cor_txt, 2))
        rt = r_out - 175
        tx, ty = polar(cx, cy, rt, meio)
        corda = 2 * rt * math.sin(math.radians(passo / 2))
        svg, _ = ctx.rotulo(i, tx, ty, peso=500, tamanho=20, cor=cor_txt,
                           max_larg=min(corda * 0.8, 200), max_linhas=4, caixa_alta=True)
        D.add("Textos", svg)
    # maior logo que cabe no semicírculo interno, apoiado na base
    a, folga, lim = ctx.logo_w / ctx.logo_h, 12, (r_in - 14)
    w = 2 * lim
    while (w / 2) ** 2 + (folga + w / a) ** 2 > lim ** 2:
        w *= 0.98
    D.add("Logo", ctx.logo(cx, cy - folga - w / a / 2, w, w / a)[0])
    D.caixa = (40, 180, 960, 710)
    return D


# ------------------------------------------------------ 4. PÉTALAS (Estela Maris)

def petalas(ctx: Ctx) -> Desenho:
    """Gotas coloridas em giro, apontando para o logo; rótulos coloridos por fora."""
    D = Desenho()
    cx, cy = 500, 500
    dist = 300
    r = min(88, math.pi * dist / ctx.n * 0.48)
    k = 1.75 * r
    alfa = math.acos(r / k)
    giro = 20
    for i in range(ctx.n):
        beta = -90 + i * 360 / ctx.n
        hx, hy = polar(cx, cy, dist, beta)
        cor = ctx.cores_itens[i]
        px, py = r * math.sin(alfa), -r * math.cos(alfa)
        d = (f"M0 {-k:.2f} L{px:.2f} {py:.2f} A{r:.2f} {r:.2f} 0 1 1 {-px:.2f} {py:.2f}Z")
        rot = beta + 270 + giro
        tr = f'translate({hx:.2f} {hy:.2f}) rotate({rot:.2f})'
        if ctx.sombra:
            D.add("Decoração", f'<path d="{d}" fill="#000000" fill-opacity="0.09" stroke="#000000" '
                               f'stroke-opacity="0.09" stroke-width="16" stroke-linejoin="round" '
                               f'transform="translate(0 7) {tr}"/>')
        D.add("Formas", f'<path id="petala-{i + 1}" d="{d}" fill="{cor}" stroke="{cor}" stroke-width="16" '
                        f'stroke-linejoin="round" transform="{tr}"/>')
        D.add("Ícones", ctx.icone(i, hx, hy, r * 0.75, C.texto_sobre(cor), 1.7))
        tx, ty = polar(cx, cy, dist + r + 34, beta)
        h, v = ancora(beta)
        svg, _ = ctx.rotulo(i, tx, ty, peso=700, tamanho=26,
                           cor=C.legivel_em(cor, ctx.fundo, 3.0), max_larg=230, max_linhas=3,
                           alinhamento=h, vertical=v)
        D.add("Textos", svg)
    if C.luminancia(ctx.fundo) < 0.8:  # fundo colorido: logo sobre disco branco
        D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{dist - k - 4:.2f}" fill="#ffffff"/>')
        D.add("Logo", ctx.logo_no_circulo(cx, cy, dist - k - 18)[0])
    else:
        D.add("Logo", ctx.logo_no_circulo(cx, cy, dist - k + 10)[0])
    D.caixa = (40, 70, 960, 930)
    return D


# ------------------------------------------------------- 5. ÁRVORE (Infan Gardeno)

def arvore(ctx: Ctx) -> Desenho:
    """Árvore: logo no círculo central, itens como copa, tronco e nuvem com o slogan."""
    D = Desenho()
    cx, cy, rc = 500, 430, 175
    folha = ctx.cores_itens
    anel_cor = ctx.cor(1) if len(ctx.paleta) > 1 else C.clarear(ctx.principal, 0.35)
    tronco = ctx.cor(2) if len(ctx.paleta) > 2 else "#e8801a"
    a_ini, a_fim = 155, 385
    dist = rc + 112
    arco_len = math.radians(a_fim - a_ini) * dist
    rf = min(118, arco_len / ctx.n * 0.58)
    passo = (a_fim - a_ini) / max(ctx.n - 1, 1)
    # tronco
    base = 830
    d_tronco = (f"M{cx - 38} {cy + rc - 10} C{cx - 34} {base - 120} {cx - 40} {base - 40} {cx - 95} {base} "
                f"L{cx + 95} {base} C{cx + 40} {base - 40} {cx + 34} {base - 120} {cx + 38} {cy + rc - 10}Z")
    D.add("Formas", f'<path id="tronco" d="{d_tronco}" fill="{tronco}"/>')
    for i in range(ctx.n):
        ang = a_ini + i * passo if ctx.n > 1 else 270
        fx, fy = polar(cx, cy, dist, ang)
        D.add("Formas", sombra(circulo_d(fx, fy, rf), ctx))
        D.add("Formas", f'<circle id="folha-{i + 1}" cx="{fx:.2f}" cy="{fy:.2f}" r="{rf:.2f}" fill="{folha[i]}"/>')
        cor_txt = C.texto_sobre(folha[i])
        D.add("Ícones", ctx.icone(i, fx, fy - rf * 0.38, rf * 0.42, cor_txt, 1.8))
        svg, _ = ctx.rotulo(i, fx, fy + rf * 0.2, peso=600, tamanho=17, cor=cor_txt,
                           max_larg=rf * 1.45, max_linhas=4, caixa_alta=True)
        D.add("Textos", svg)
    D.add("Formas", sombra(circulo_d(cx, cy, rc + 16), ctx, 8, 0.12))
    D.add("Formas", f'<circle id="anel-central" cx="{cx}" cy="{cy}" r="{rc}" fill="#ffffff" '
                    f'stroke="{anel_cor}" stroke-width="30"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, rc - 30)[0])
    if ctx.slogan:
        D.usou_slogan = True
        nx, ny, nw, nh = cx, base + 40, 470, 105
        bolhas = [(-0.36, 0.05, 0.3), (-0.12, -0.18, 0.36), (0.16, -0.12, 0.33), (0.36, 0.06, 0.28)]
        nuvem = [f'<rect x="{nx - nw / 2:.2f}" y="{ny - nh * 0.1:.2f}" width="{nw}" height="{nh * 0.6:.2f}" '
                 f'rx="{nh * 0.3:.2f}"/>']
        for bx, by, br in bolhas:
            nuvem.append(f'<circle cx="{nx + bx * nw:.2f}" cy="{ny + by * nh:.2f}" r="{br * nh * 1.4:.2f}"/>')
        D.add("Formas", f'<g id="nuvem" fill="{anel_cor}">{"".join(nuvem)}</g>')
        svg, _ = ctx.texto(ctx.slogan, nx, ny + nh * 0.12, peso=700, tamanho=22,
                           cor=C.texto_sobre(anel_cor), max_larg=nw * 0.86, max_linhas=2,
                           caixa_alta=True, id_="slogan")
        D.add("Textos", svg)
        D.caixa = (90, 0, 910, 960)
    else:
        D.add("Formas", f'<ellipse id="chao" cx="{cx}" cy="{base + 4}" rx="190" ry="16" '
                        f'fill="{C.clarear(tronco, 0.6)}"/>')
        D.caixa = (90, 0, 910, 860)
    return D


# ------------------------------------------------------------- 6. BALÕES (Pistori)

def baloes(ctx: Ctx) -> Desenho:
    """Círculo central com logo e slogan, balões de fala coloridos em volta."""
    D = Desenho()
    cx, cy, R = 500, 500, 190
    dist = 400
    rb = min(130, math.pi * dist / ctx.n * 0.52)
    D.add("Decoração", sombra(circulo_d(cx, cy, R + 22), ctx, 10, 0.08))
    D.add("Decoração", f'<circle id="aro-central" cx="{cx}" cy="{cy}" r="{R + 22}" fill="#ffffff" '
                       f'stroke="#9d9d9d" stroke-width="2.5"/>')
    D.add("Decoração", f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff" stroke="#efefef" stroke-width="2"/>')
    for i in range(ctx.n):
        beta = -90 + i * 360 / ctx.n
        bx, by = polar(cx, cy, dist, beta)
        cor = ctx.cores_itens[i]
        gid = f"grad-{i + 1}"
        D.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
                      f'<stop offset="0" stop-color="{C.clarear(cor, 0.12)}"/>'
                      f'<stop offset="1" stop-color="{C.escurecer(cor, 0.08)}"/></linearGradient>')
        # ponta do balão apontando para o aro central
        volta = beta + 180
        p1 = polar(bx, by, rb * 0.9, volta - 28)
        p2 = polar(bx, by, rb * 0.9, volta + 4)
        ponta = polar(cx, cy, R + 52, beta - 9)
        d_ponta = f"M{p1[0]:.2f} {p1[1]:.2f} L{ponta[0]:.2f} {ponta[1]:.2f} L{p2[0]:.2f} {p2[1]:.2f}Z"
        D.add("Formas", sombra(circulo_d(bx, by, rb), ctx))
        D.add("Formas", f'<g id="balao-{i + 1}" fill="url(#{gid})"><path d="{d_ponta}" fill="{cor}"/>'
                        f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{rb:.2f}"/></g>')
        D.add("Formas", f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{rb - 13:.2f}" fill="none" '
                        f'stroke="#ffffff" stroke-opacity="0.45" stroke-width="1.6"/>')
        # ponto no aro
        ax, ay = polar(cx, cy, R + 22, beta - 9)
        D.add("Decoração", f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="10" fill="#ffffff" stroke="{cor}" '
                           f'stroke-width="3"/><circle cx="{ax:.2f}" cy="{ay:.2f}" r="4.5" fill="{cor}"/>')
        # selo com o ícone
        ang_selo = -128
        if abs((ang_selo - volta + 180) % 360 - 180) < 60:  # não cobrir a ponta do balão
            ang_selo = -52
        sx, sy = polar(bx, by, rb * 0.98, ang_selo)
        rs = rb * 0.34
        D.add("Formas", sombra(circulo_d(sx, sy, rs), ctx, 4, 0.12))
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{sx:.2f}" cy="{sy:.2f}" r="{rs:.2f}" fill="#ffffff" '
                        f'stroke="#f1f1f1" stroke-width="3"/>')
        D.add("Ícones", ctx.icone(i, sx, sy, rs * 1.15, C.legivel_em(cor, "#ffffff", 2.6), 1.7))
        svg, _ = ctx.rotulo(i, bx, by + 6, peso=700, tamanho=25,
                           cor=C.texto_sobre(cor), max_larg=rb * 1.62, max_linhas=4)
        D.add("Textos", svg)
    if ctx.slogan:
        D.usou_slogan = True
        D.add("Logo", ctx.logo(cx, cy - 55, R * 1.6, R * 0.8)[0])
        svg, _ = ctx.texto(ctx.slogan, cx, cy + 75, peso=500, tamanho=30, cor="#555555",
                           max_larg=R * 1.55, max_linhas=3, id_="slogan")
        D.add("Textos", svg)
    else:
        D.add("Logo", ctx.logo_no_circulo(cx, cy, R - 18)[0])
    D.caixa = (0, 0, 1000, 1000)
    return D


# ----------------------------------------------------------- 7. ÓRBITA (Koala)

def orbita(ctx: Ctx) -> Desenho:
    """Logo entre dois parênteses em arco; itens em círculos nos dois lados."""
    D = Desenho()
    cx, cy, R = 500, 500, 175
    escuro = C.legivel_em(C.escurecer(ctx.principal, 0.1), "#ffffff", 4)
    for lado in (0, 180):
        x0, y0 = polar(cx, cy, R + 30, lado - 58)
        x1, y1 = polar(cx, cy, R + 30, lado + 58)
        D.add("Decoração", f'<path d="M{x0:.2f} {y0:.2f} A{R + 30} {R + 30} 0 0 1 {x1:.2f} {y1:.2f}" '
                           f'fill="none" stroke="{ctx.principal}" stroke-width="14" stroke-linecap="round"/>')
    esq = math.ceil(ctx.n / 2)
    lados = [(180, list(range(esq))), (0, list(range(esq, ctx.n)))]
    dist = 395
    ab_max = min(110, 36 * (esq - 1)) if esq > 1 else 0
    vao = 2 * dist * math.sin(math.radians(ab_max / 2)) / (esq - 1) if esq > 1 else 220
    rc = min(112, vao * 0.47)
    for centro, idx in lados:
        k = len(idx)
        abertura = min(110, 36 * (k - 1)) if k > 1 else 0
        for j, i in enumerate(idx):
            if centro == 180:
                ang = centro + abertura / 2 - (abertura / max(k - 1, 1)) * j
            else:
                ang = centro - abertura / 2 + (abertura / max(k - 1, 1)) * j
            px, py = polar(cx, cy, dist, ang)
            cor = ctx.cores_itens[i] if len(set(ctx.cores_itens)) > 1 else C.clarear(ctx.principal, 0.55)
            D.add("Formas", f'<circle id="item-{i + 1}" cx="{px:.2f}" cy="{py:.2f}" r="{rc:.2f}" fill="{cor}"/>')
            cor_el = escuro if C.luminancia(cor) > 0.35 else "#ffffff"
            D.add("Ícones", ctx.icone(i, px, py - rc * 0.4, rc * 0.48, cor_el, 2.1))
            svg, _ = ctx.rotulo(i, px, py + rc * 0.26, peso=600, tamanho=18, cor=cor_el,
                               max_larg=rc * 1.55, max_linhas=3)
            D.add("Textos", svg)
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, R - 8)[0])
    alt = dist * math.sin(math.radians(ab_max / 2)) + rc
    D.caixa = (5, cy - max(alt, R + 40), 995, cy + max(alt, R + 40))
    return D


# ------------------------------------------------------------- 8. ONDA (Sagaz)

def onda(ctx: Ctx) -> Desenho:
    """Faixa em ondas (arcos alternados) com ícones nas curvas; logo numa pílula abaixo."""
    D = Desenho()
    cy = 430
    r = min(125, 440 / ctx.n)
    larg = 2 * r * ctx.n
    x0 = 500 - larg / 2
    cor1 = ctx.principal
    cor2 = ctx.cor(1) if len(ctx.paleta) > 1 else C.escurecer(cor1, 0.25)
    D.defs.append(f'<linearGradient id="grad-onda" x1="0" y1="0" x2="1" y2="0">'
                  f'<stop offset="0" stop-color="{C.escurecer(cor1, 0.1)}"/>'
                  f'<stop offset="0.5" stop-color="{C.clarear(cor1, 0.15)}"/>'
                  f'<stop offset="1" stop-color="{C.escurecer(cor1, 0.1)}"/></linearGradient>')
    d = [f"M{x0:.2f} {cy}"]
    for i in range(ctx.n):
        d.append(f"A{r:.2f} {r:.2f} 0 0 {1 if i % 2 == 0 else 0} {x0 + 2 * r * (i + 1):.2f} {cy}")
    caminho = " ".join(d)
    esp = r * 0.3
    if ctx.sombra:
        D.add("Decoração", f'<path d="{caminho}" fill="none" stroke="#000" stroke-opacity="0.1" '
                           f'stroke-width="{esp:.2f}" stroke-linecap="round" transform="translate(0 8)"/>')
    D.add("Formas", f'<path id="onda" d="{caminho}" fill="none" stroke="url(#grad-onda)" '
                    f'stroke-width="{esp:.2f}" stroke-linecap="round"/>')
    for i in range(ctx.n):
        xc = x0 + r + 2 * r * i
        cima = i % 2 == 0
        cor_i = ctx.cores_itens[i] if len(set(ctx.cores_itens)) > 1 else cor2
        iy = cy - r * 0.32 if cima else cy + r * 0.32
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{xc:.2f}" cy="{iy:.2f}" r="{r * 0.46:.2f}" '
                        f'fill="#ffffff" stroke="{C.clarear(cor1, 0.75)}" stroke-width="3"/>')
        D.add("Ícones", ctx.icone(i, xc, iy, r * 0.5, cor_i, 2))
        ty = cy - r - esp / 2 - 22 if cima else cy + r + esp / 2 + 22
        svg, _ = ctx.rotulo(i, xc, ty, peso=600, tamanho=22,
                           cor=C.legivel_em(C.escurecer(cor1, 0.1), ctx.fundo, 4), max_larg=2 * r * 1.45,
                           max_linhas=3, vertical="bottom" if cima else "top")
        D.add("Textos", svg)
    lh = 175
    py = cy + r + esp / 2 + 22 + 90 + lh / 2 + 40
    img, lw, _ = ctx.logo(500, py, 600, lh)
    pw = lw + 70
    D.add("Formas", f'<rect id="pilula-logo" x="{500 - pw / 2:.2f}" y="{py - lh / 2 - 18:.2f}" '
                    f'width="{pw:.2f}" height="{lh + 36}" rx="{(lh + 36) / 2:.2f}" fill="#ffffff" '
                    f'stroke="{cor2}" stroke-width="5"/>')
    D.add("Logo", img)
    D.caixa = (x0 - esp - 60, cy - r - 150, 1000 - x0 + esp + 60, py + lh / 2 + 30)
    return D


# ======================================================= layouts criados sob demanda

# ------------------------------------------------- 9. PILARES (criado para o CTO)

def pilares(ctx: Ctx) -> Desenho:
    """Templo clássico: logo no alto, frontão, e cada tópico é uma coluna que sustenta a escola."""
    D = Desenho()
    n = ctx.n
    x0, x1 = 25, 975
    larg = x1 - x0
    escuro = ctx.principal
    acento = ctx.cor(1) if len(ctx.paleta) > 1 else C.escurecer(escuro, 0.3)
    medio = C.clarear(escuro, 0.12)
    # logo no topo
    img, _, lh = ctx.logo(500, 150, 600, 230)
    D.add("Logo", img)
    topo = 150 + lh / 2 + 40
    # frontão
    f_alt = 125
    D.add("Formas", f'<path id="frontao" d="M{x0 - 20} {topo + f_alt} L500 {topo} L{x1 + 20} {topo + f_alt}Z" '
                    f'fill="{escuro}"/>')
    D.add("Formas", f'<path d="M{x0 + 40} {topo + f_alt - 14} L500 {topo + 22} L{x1 - 40} {topo + f_alt - 14}Z" '
                    f'fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3" stroke-linejoin="round"/>')
    viga = topo + f_alt + 8
    D.add("Formas", f'<rect id="viga" x="{x0 - 20}" y="{viga}" width="{larg + 40}" height="30" fill="{acento}"/>')
    # colunas
    vao = larg / n
    fuste_w = vao * 0.9
    cap_y = viga + 30 + 10
    fuste_y = cap_y + 26
    base_y = fuste_y + 340
    for i in range(n):
        cx = x0 + vao * (i + 0.5)
        D.add("Formas", f'<g id="coluna-{i + 1}">'
                        f'<rect x="{cx - fuste_w / 2 - 12:.2f}" y="{cap_y:.2f}" width="{fuste_w + 24:.2f}" height="20" rx="4" fill="{medio}"/>'
                        f'<rect x="{cx - fuste_w / 2:.2f}" y="{fuste_y:.2f}" width="{fuste_w:.2f}" height="{base_y - fuste_y:.2f}" fill="{escuro}"/>'
                        f'<rect x="{cx - fuste_w / 2 - 12:.2f}" y="{base_y + 6:.2f}" width="{fuste_w + 24:.2f}" height="20" rx="4" fill="{medio}"/>'
                        f'</g>')
        # caneluras discretas
        for k in (-0.28, 0.28):
            D.add("Decoração", f'<line x1="{cx + k * fuste_w:.2f}" y1="{fuste_y + 150:.2f}" x2="{cx + k * fuste_w:.2f}" '
                               f'y2="{base_y - 18:.2f}" stroke="#ffffff" stroke-opacity="0.12" stroke-width="3"/>')
        iy = fuste_y + 62
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{cx:.2f}" cy="{iy:.2f}" r="38" fill="#ffffff"/>')
        D.add("Ícones", ctx.icone(i, cx, iy, 44, escuro, 1.8))
        svg, _ = ctx.rotulo(i, cx, fuste_y + 120 + (base_y - fuste_y - 120) / 2 - 10, tamanho=22, peso=600,
                            cor="#ffffff", max_larg=fuste_w - 14, max_linhas=5)
        D.add("Textos", svg)
    # degraus da base
    d1 = base_y + 32
    D.add("Formas", f'<rect id="degrau-1" x="{x0 - 20}" y="{d1}" width="{larg + 40}" height="24" fill="{acento}"/>')
    D.add("Formas", f'<rect id="degrau-2" x="{x0 - 45}" y="{d1 + 30}" width="{larg + 90}" height="24" fill="{escuro}"/>')
    D.caixa = (x0 - 50, 150 - lh / 2 - 10, x1 + 50, d1 + 60)
    return D


# ------------------------------------------------- 10. DEGRAUS (criado para o CTO)

def degraus(ctx: Ctx) -> Desenho:
    """Escada ascendente: cada tópico é um degrau, seta de crescimento e logo no espaço livre acima."""
    D = Desenho()
    n = ctx.n
    x0, x1, chao = 30, 970, 900
    gap = 12
    w = (x1 - x0 - gap * (n - 1)) / n
    h_min, passo = 275, min(95, 360 / max(n - 1, 1))
    acento = ctx.cor(1) if len(ctx.paleta) > 1 else C.escurecer(ctx.principal, 0.3)
    topos = []
    for i in range(n):
        x = x0 + i * (w + gap)
        h = h_min + i * passo
        y = chao - h
        topos.append((x + w / 2, y))
        cor = C.misturar(C.clarear(ctx.principal, 0.35), ctx.principal, i / max(n - 1, 1))
        D.add("Formas", f'<path id="degrau-{i + 1}" d="M{x:.2f} {chao} V{y + 14:.2f} Q{x:.2f} {y:.2f} {x + 14:.2f} {y:.2f} '
                        f'H{x + w - 14:.2f} Q{x + w:.2f} {y:.2f} {x + w:.2f} {y + 14:.2f} V{chao}Z" fill="{cor}"/>')
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{x + w / 2:.2f}" cy="{y + 62:.2f}" r="38" fill="#ffffff"/>')
        D.add("Ícones", ctx.icone(i, x + w / 2, y + 62, 44, ctx.principal, 1.8))
        svg, _ = ctx.rotulo(i, x + w / 2, y + 122, tamanho=22, peso=600, cor="#ffffff",
                            max_larg=w - 14, max_linhas=5, vertical="top")
        D.add("Textos", svg)
        D.add("Textos", ctx.texto(f"{i + 1:02d}", x + w / 2, chao - 26, tamanho=30, peso=700,
                                  cor="#ffffff", max_larg=w, max_linhas=1, vertical="bottom",
                                  id_=f"numero-{i + 1}")[0].replace('fill="#ffffff"', 'fill="#ffffff" fill-opacity="0.35"'))
    # seta de crescimento sobre os degraus
    pts = [(x, y - 42) for x, y in topos]
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    D.add("Decoração", f'<path id="seta" d="{d}" fill="none" stroke="{acento}" stroke-width="5" '
                       f'stroke-dasharray="2 12" stroke-linecap="round"/>')
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    ang = math.degrees(math.atan2(by - ay, bx - ax))
    D.add("Decoração", f'<path d="M0 -13 L24 0 L0 13Z" fill="{acento}" '
                       f'transform="translate({bx:.2f} {by:.2f}) rotate({ang:.2f})"/>')
    # logo no triângulo livre acima dos primeiros degraus
    lim_y = topos[min(2, n - 1)][1] - 80
    img, lw, lh = ctx.logo(x0 + 230, 0, 460, 280)
    cy_logo = min(lim_y - lh / 2, topos[0][1] - 150 - lh / 2)
    D.add("Logo", ctx.logo(x0 + lw / 2, cy_logo, 460, 280)[0])
    D.caixa = (x0 - 10, min(cy_logo - lh / 2, topos[-1][1] - 70) - 10, x1 + 30, chao + 10)
    return D


# --------------------------------------------- 11. MAPA RAMIFICADO (criado para o CTO)

def mapa(ctx: Ctx) -> Desenho:
    """Mapa mental clássico: logo no centro e galhos curvos até cartões dos dois lados."""
    D = Desenho()
    cx, cy, R = 500, 500, 190
    n = ctx.n
    esq = math.ceil(n / 2)
    lados = [(-1, list(range(esq))), (1, list(range(esq, n)))]
    cw, ch = 300, 150
    D.add("Decoração", f'<circle cx="{cx}" cy="{cy}" r="{R + 18}" fill="none" stroke="{C.clarear(ctx.principal, 0.8)}" '
                       f'stroke-width="10"/>')
    for sinal, idx in lados:
        k = len(idx)
        esp = min(235, 720 / max(k, 1))
        for j, i in enumerate(idx):
            y = cy + (j - (k - 1) / 2) * esp
            cor = ctx.cores_itens[i]
            borda_int = cx + sinal * 265  # lado do cartão voltado para o centro
            x_card = borda_int if sinal > 0 else borda_int - cw
            # galho
            sx, sy = cx + sinal * (R + 18) * 0.92, cy + (y - cy) * 0.35
            D.add("Decoração", f'<path id="galho-{i + 1}" d="M{sx:.2f} {sy:.2f} C{cx + sinal * 225:.2f} {sy:.2f} '
                               f'{borda_int - sinal * 60:.2f} {y:.2f} {borda_int:.2f} {y:.2f}" fill="none" '
                               f'stroke="{cor}" stroke-width="5" stroke-linecap="round"/>')
            D.add("Decoração", f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="8" fill="{cor}"/>')
            D.add("Formas", sombra(f"M{x_card + 20} {y - ch / 2} h{cw - 40} a20 20 0 0 1 20 20 v{ch - 40} "
                                   f"a20 20 0 0 1 -20 20 h{-(cw - 40)} a20 20 0 0 1 -20 -20 v{-(ch - 40)} "
                                   f"a20 20 0 0 1 20 -20Z", ctx, 6, 0.08))
            D.add("Formas", f'<rect id="cartao-{i + 1}" x="{x_card:.2f}" y="{y - ch / 2:.2f}" width="{cw}" height="{ch}" '
                            f'rx="20" fill="{cor}"/>')
            # selo do ícone na ponta do galho
            D.add("Formas", f'<circle id="selo-{i + 1}" cx="{borda_int:.2f}" cy="{y:.2f}" r="40" fill="#ffffff" '
                            f'stroke="{cor}" stroke-width="5"/>')
            D.add("Ícones", ctx.icone(i, borda_int, y, 42, cor, 1.8))
            tx = x_card + (62 if sinal > 0 else 22)
            svg, _ = ctx.rotulo(i, tx + (cw - 84) / 2, y, tamanho=26, peso=600, cor=C.texto_sobre(cor),
                                max_larg=cw - 92, max_linhas=3)
            D.add("Textos", svg)
    D.add("Formas", sombra(circulo_d(cx, cy, R), ctx, 8, 0.10))
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, R - 14)[0])
    D.caixa = (cx - 265 - cw - 10, 120, cx + 265 + cw + 10, 880)
    return D


# ---------------------------------------- 12. CICLO (criado para o Hermínio Silva)

def ciclo(ctx: Ctx) -> Desenho:
    """Anel de setas encadeadas (formação contínua): ícones nas setas, títulos coloridos por fora."""
    D = Desenho()
    cx, cy, r_in, r_out = 500, 500, 215, 315
    rm = (r_in + r_out) / 2
    passo = 360 / ctx.n
    gap, ponta = 2.2, 9
    for i in range(ctx.n):
        a0 = -90 - passo / 2 + i * passo + gap
        a1 = a0 + passo - 2 * gap
        cor = ctx.cores_itens[i]
        grande = 1 if (a1 - a0) > 180 else 0
        p = lambda r, a: polar(cx, cy, r, a)  # noqa: E731
        o0, o1, i0, i1 = p(r_out, a0), p(r_out, a1), p(r_in, a1), p(r_in, a0)
        tip, notch = p(rm, a1 + ponta), p(rm, a0 + ponta)
        d = (f"M{o0[0]:.2f} {o0[1]:.2f} A{r_out} {r_out} 0 {grande} 1 {o1[0]:.2f} {o1[1]:.2f} "
             f"L{tip[0]:.2f} {tip[1]:.2f} L{i0[0]:.2f} {i0[1]:.2f} "
             f"A{r_in} {r_in} 0 {grande} 0 {i1[0]:.2f} {i1[1]:.2f} L{notch[0]:.2f} {notch[1]:.2f}Z")
        D.add("Formas", sombra(d, ctx, 6, 0.08))
        D.add("Formas", f'<path id="seta-{i + 1}" d="{d}" fill="{cor}" stroke="{cor}" stroke-width="6" '
                        f'stroke-linejoin="round"/>')
        meio = (a0 + a1) / 2 + ponta / 2
        ix, iy = polar(cx, cy, rm, meio)
        D.add("Ícones", ctx.icone(i, ix, iy, 54, C.texto_sobre(cor), 2))
        tx, ty = polar(cx, cy, r_out + 34, meio)
        h, v = ancora(meio)
        svg, _ = ctx.rotulo(i, tx, ty, tamanho=28, peso=600, cor=C.legivel_em(cor, ctx.fundo, 3.0),
                            max_larg=240, max_linhas=3, alinhamento=h, vertical=v)
        D.add("Textos", svg)
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{r_in - 16}" fill="#ffffff"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, r_in - 28)[0])
    D.caixa = (cx - r_out - 10, cy - r_out - 10, cx + r_out + 10, cy + r_out + 10)
    return D


# ------------------------------------------ 13. SOL (criado para o Hermínio Silva)

def sol(ctx: Ctx) -> Desenho:
    """Logo no centro como um sol: raios coloridos até selos com ícone, títulos por fora."""
    D = Desenho()
    cx, cy, R = 500, 500, 190
    d_selo, r_selo = 360, 86
    D.add("Decoração", f'<circle cx="{cx}" cy="{cy}" r="{R + 22}" fill="none" stroke="#e9e9e9" stroke-width="3" '
                       f'stroke-dasharray="3 10" stroke-linecap="round"/>')
    passo = 360 / ctx.n
    for i in range(ctx.n):
        ang = -90 + i * passo
        cor = ctx.cores_itens[i]
        x0, y0 = polar(cx, cy, R + 38, ang)
        x1, y1 = polar(cx, cy, d_selo - r_selo + 4, ang)
        D.add("Formas", f'<line id="raio-{i + 1}" x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                        f'stroke="{cor}" stroke-width="20" stroke-linecap="round"/>')
        # raiozinhos entre os principais
        mx0, my0 = polar(cx, cy, R + 42, ang + passo / 2)
        mx1, my1 = polar(cx, cy, R + 82, ang + passo / 2)
        D.add("Decoração", f'<line x1="{mx0:.2f}" y1="{my0:.2f}" x2="{mx1:.2f}" y2="{my1:.2f}" '
                           f'stroke="{C.clarear(cor, 0.55)}" stroke-width="10" stroke-linecap="round"/>')
        sx, sy = polar(cx, cy, d_selo, ang)
        D.add("Formas", sombra(circulo_d(sx, sy, r_selo), ctx, 6, 0.10))
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{sx:.2f}" cy="{sy:.2f}" r="{r_selo}" fill="{cor}" '
                        f'stroke="#ffffff" stroke-width="6"/>')
        D.add("Ícones", ctx.icone(i, sx, sy, 80, C.texto_sobre(cor), 2))
        # título centralizado sob o selo (acima, quando o selo está no topo)
        acima = math.sin(math.radians(ang)) < -0.8
        ty = sy - r_selo - 18 if acima else sy + r_selo + 18
        svg, _ = ctx.rotulo(i, sx, ty, tamanho=32, peso=600, cor=C.legivel_em(cor, ctx.fundo, 3.0),
                            max_larg=270, max_linhas=3, vertical="bottom" if acima else "top")
        D.add("Textos", svg)
    D.add("Formas", sombra(circulo_d(cx, cy, R), ctx, 8, 0.08))
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff" stroke="#f1f1f1" stroke-width="3"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, R - 16)[0])
    ext = d_selo + r_selo + 10
    D.caixa = (cx - ext, cy - ext, cx + ext, cy + ext)
    return D


# ------------------------------------------ 14. FLOR (criado para o Hermínio Silva)

def flor(ctx: Ctx) -> Desenho:
    """Flor: círculos coloridos (pétalas) encostados uns nos outros em volta do logo, conteúdo dentro."""
    D = Desenho()
    cx, cy, R = 500, 500, 205
    meia = math.radians(180 / ctx.n)
    rc = min(230, R / (1 / math.sin(meia) - 0.72))
    dist = rc / math.sin(meia) * 0.97
    for i in range(ctx.n):
        ang = -90 + i * 360 / ctx.n
        cor = ctx.cores_itens[i]
        px, py = polar(cx, cy, dist, ang)
        D.add("Formas", f'<circle id="petala-{i + 1}" cx="{px:.2f}" cy="{py:.2f}" r="{rc:.2f}" fill="{cor}" '
                        f'stroke="#ffffff" stroke-width="10"/>')
        # conteúdo na parte visível da pétala (mais para fora)
        qx, qy = polar(cx, cy, dist + rc * 0.28, ang)
        cor_el = C.texto_sobre(cor)
        D.add("Ícones", ctx.icone(i, qx, qy - rc * 0.27, rc * 0.38, cor_el, 2))
        svg, _ = ctx.rotulo(i, qx, qy + rc * 0.17, tamanho=31, peso=600, cor=cor_el,
                            max_larg=rc * 1.3, max_linhas=3)
        D.add("Textos", svg)
    D.add("Formas", sombra(circulo_d(cx, cy, R), ctx, 8, 0.12))
    D.add("Formas", f'<circle id="miolo" cx="{cx}" cy="{cy}" r="{R}" fill="#ffffff" stroke="#ffffff" stroke-width="10"/>')
    D.add("Logo", ctx.logo_no_circulo(cx, cy, R - 18)[0])
    ext = dist + rc + 6
    D.caixa = (cx - ext, cy - ext, cx + ext, cy + ext)
    return D


# ------------------------------------- 15. TORRE DE BLOCOS (criado para o Monteiro)

def torre(ctx: Ctx) -> Desenho:
    """Torre de blocos (como a Torre Rosa Montessori): logo no topo, um bloco por tópico."""
    D = Desenho()
    n = ctx.n
    alt, gap = 112, 16
    w_min, w_max = 600, 920
    img, _, lh = ctx.logo(500, 0, 560, 270)
    topo = lh + 50
    D.add("Logo", ctx.logo(500, lh / 2, 560, 270)[0])
    for i in range(n):
        w = w_min + (w_max - w_min) * (i / max(n - 1, 1))
        x, y = 500 - w / 2, topo + i * (alt + gap)
        cor = ctx.cores_itens[i]
        D.add("Formas", sombra(f"M{x + 24} {y} h{w - 48} a24 24 0 0 1 24 24 v{alt - 48} a24 24 0 0 1 -24 24 "
                               f"h{-(w - 48)} a24 24 0 0 1 -24 -24 v{-(alt - 48)} a24 24 0 0 1 24 -24Z", ctx, 7, 0.10))
        D.add("Formas", f'<g id="bloco-{i + 1}"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{alt}" rx="24" '
                        f'fill="{C.escurecer(cor, 0.14)}"/><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" '
                        f'height="{alt - 9}" rx="24" fill="{cor}"/></g>')
        ix = x + 64
        D.add("Formas", f'<circle id="selo-{i + 1}" cx="{ix:.2f}" cy="{y + alt / 2 - 4:.2f}" r="38" fill="#ffffff"/>')
        D.add("Ícones", ctx.icone(i, ix, y + alt / 2 - 4, 46, C.escurecer(cor, 0.05), 2))
        area_x0, area_x1 = ix + 52, x + w - 30
        svg, _ = ctx.rotulo(i, (area_x0 + area_x1) / 2, y + alt / 2 - 4, tamanho=32, peso=600,
                            cor=C.texto_sobre(cor), max_larg=area_x1 - area_x0, max_linhas=2)
        D.add("Textos", svg)
    base = topo + n * (alt + gap) - gap
    D.caixa = (500 - w_max / 2 - 10, -10, 500 + w_max / 2 + 10, base + 20)
    return D


# ----------------------------------------------- 16. GALHO (criado para o Monteiro)

def _bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def galho(ctx: Ctx) -> Desenho:
    """Galho com folhas atravessando a arte; tópicos pendurados como frutos; logo acima do galho."""
    D = Desenho()
    n = ctx.n
    p0, p1, p2, p3 = (20, 520), (300, 440), (700, 620), (980, 500)
    verde = next((c for c in ctx.paleta if C._sat_luz(c)[0] > 0.2 and C._sat_luz(c)[0] < 0.45), "#6aa53a")
    tronco = C.escurecer(verde, 0.35)
    d = f"M{p0[0]} {p0[1]} C{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}"
    D.add("Formas", f'<path id="galho" d="{d}" fill="none" stroke="{tronco}" stroke-width="16" stroke-linecap="round"/>')
    # folhas ao longo do galho
    for k in range(n + 1):
        t = (k + 0.0) / n
        fx, fy = _bezier(p0, p1, p2, p3, min(max(t, 0.04), 0.96))
        for lado, rot in ((-1, -35), (1, 35)):
            cor_f = verde if lado < 0 else C.clarear(verde, 0.25)
            D.add("Decoração", f'<ellipse cx="0" cy="{lado * 26}" rx="15" ry="30" fill="{cor_f}" '
                               f'transform="translate({fx:.2f} {fy:.2f}) rotate({rot + lado * 10})"/>')
    r = min(88, 900 / n / 2 * 0.86)
    for i in range(n):
        t = (i + 0.5) / n
        bx, by = _bezier(p0, p1, p2, p3, t)
        cor = ctx.cores_itens[i]
        cy = by + 70 + r
        D.add("Formas", f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{bx:.2f}" y2="{cy - r:.2f}" stroke="{tronco}" '
                        f'stroke-width="6" stroke-linecap="round"/>')
        D.add("Formas", sombra(circulo_d(bx, cy, r), ctx, 6, 0.10))
        D.add("Formas", f'<circle id="fruto-{i + 1}" cx="{bx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{cor}" '
                        f'stroke="#ffffff" stroke-width="6"/>')
        D.add("Ícones", ctx.icone(i, bx, cy, r * 0.95, C.texto_sobre(cor), 2))
        svg, _ = ctx.rotulo(i, bx, cy + r + 22, tamanho=30, peso=600, cor=C.legivel_em(cor, ctx.fundo, 3.0),
                            max_larg=900 / n * 0.98, max_linhas=4, vertical="top")
        D.add("Textos", svg)
    y_min = min(_bezier(p0, p1, p2, p3, t / 20)[1] for t in range(21))
    D.add("Logo", ctx.logo(500, y_min - 50 - 150, 640, 300)[0])
    D.caixa = (0, y_min - 50 - 300 - 10, 1000, 820)
    return D


LAYOUTS = {
    "arco": (arco, "marca", "Anel em 'C' com ícones no anel e textos por fora (modelo Athena)"),
    "anel": (anel, "marca", "Anel completo em fatias com selo e texto dentro (modelo Koala)"),
    "leque": (leque, "arco-iris", "Meia-lua colorida em leque com logo na base (modelo Criança Feliz)"),
    "petalas": (petalas, "arco-iris", "Gotas coloridas em giro com textos coloridos por fora (modelo Estela Maris)"),
    "arvore": (arvore, "marca", "Árvore: logo no centro, itens na copa, slogan na nuvem (modelo Infan Gardeno)"),
    "baloes": (baloes, "alternada", "Balões de fala em volta de um círculo com logo e slogan (modelo Pistori)"),
    "orbita": (orbita, "marca", "Logo entre arcos, itens em círculos dos dois lados (modelo Koala 2)"),
    "onda": (onda, "marca", "Faixa em ondas com ícones nas curvas e logo em pílula abaixo (modelo Sagaz)"),
    # criados sob demanda
    "pilares": (pilares, "marca", "Templo: logo no alto e cada tópico é uma coluna (criado para o CTO)"),
    "degraus": (degraus, "marca", "Escada ascendente com seta de crescimento e logo acima (criado para o CTO)"),
    "mapa": (mapa, "alternada", "Mapa mental: logo no centro, galhos curvos até cartões (criado para o CTO)"),
    "ciclo": (ciclo, "arco-iris", "Anel de setas encadeadas, títulos coloridos por fora (criado para o Hermínio Silva)"),
    "sol": (sol, "arco-iris", "Logo como sol, raios até selos coloridos (criado para o Hermínio Silva)"),
    "flor": (flor, "arco-iris", "Pétalas circulares coloridas em volta do logo (criado para o Hermínio Silva)"),
    "torre": (torre, "arco-iris", "Torre de blocos empilhados com logo no topo (criado para o Monteiro)"),
    "galho": (galho, "arco-iris", "Galho com folhas e tópicos pendurados, logo acima (criado para o Monteiro)"),
}
