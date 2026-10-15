"""Gera os selos circulares dos pilares do Instituto Educacional Hermínio Silva.

Três opções de estilo (A, B, C) x cinco pilares, em SVG com a fonte Nunito embutida.
Saída: pilares/svg/*.svg e pilares/index.html (galeria usada para gerar os PNGs).
"""
import base64
import math
from pathlib import Path

ROOT = Path(__file__).parent
FONT_B64 = base64.b64encode((ROOT / "fonts" / "nunito-latin.woff2").read_bytes()).decode()
FONT_CSS = (
    "@font-face{font-family:'Nunito';font-weight:200 1000;"
    f"src:url(data:font/woff2;base64,{FONT_B64}) format('woff2');}}"
)

NAVY = "#0B1F5C"
PAPER = "#F7F7F7"

# Paleta extraída do escudo HS
CORES = {
    "azul": dict(base="#0A5DBE", claro="#4A90D9", escuro="#073F86"),
    "vermelho": dict(base="#E52421", claro="#EF5B50", escuro="#A8150F"),
    "verde": dict(base="#38A33B", claro="#6CC26B", escuro="#1E7D2A"),
    "amarelo": dict(base="#FBB40A", claro="#FDCB55", escuro="#D98600"),
    "marinho": dict(base="#0B1F5C", claro="#2E4A9A", escuro="#050F33"),
}
QUADRANTES = ["#E52421", "#FBB40A", "#38A33B", "#0A5DBE"]  # escudo, horário a partir do topo-direito


# ---------- Ícones (caixa 200x200, centro 100,100) ----------
def ic_livro(fg, det):
    return f"""
    <path d="M97 62 C78 50 46 47 22 53 L22 152 C46 146 78 148 97 160 Z" fill="{fg}"/>
    <path d="M103 62 C122 50 154 47 178 53 L178 152 C154 146 122 148 103 160 Z" fill="{fg}"/>
    <text x="60" y="122" text-anchor="middle" font-size="58" font-weight="900" fill="{det}">A</text>
    <text x="140" y="122" text-anchor="middle" font-size="58" font-weight="900" fill="{det}">b</text>
    <path d="M14 66 L14 166 C50 156 82 160 100 172 C118 160 150 156 186 166 L186 66"
          fill="none" stroke="{fg}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>"""


def ic_lampada(fg, det):
    raios = ""
    for ang in (-160, -125, -90, -55, -20):
        a = math.radians(ang)
        x1, y1 = 100 + 64 * math.cos(a), 78 + 64 * math.sin(a)
        x2, y2 = 100 + 84 * math.cos(a), 78 + 84 * math.sin(a)
        raios += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{fg}" stroke-width="11" stroke-linecap="round"/>'
    return f"""{raios}
    <path d="M100 30 C127 30 148 51 148 78 C148 97 137 108 128 118 C122 125 121 130 121 136 L79 136
             C79 130 78 125 72 118 C63 108 52 97 52 78 C52 51 73 30 100 30 Z" fill="{fg}"/>
    <rect x="78" y="143" width="44" height="14" rx="7" fill="{fg}"/>
    <rect x="86" y="163" width="28" height="13" rx="6.5" fill="{fg}"/>
    <path d="M100 52 L107 71 L126 78 L107 85 L100 104 L93 85 L74 78 L93 71 Z" fill="{det}"/>"""


def ic_coracao(fg, det):
    return f"""
    <path d="M100 172 C42 134 16 104 16 70 C16 44 37 26 61 26 C79 26 92 36 100 50
             C108 36 121 26 139 26 C163 26 184 44 184 70 C184 104 158 134 100 172 Z" fill="{fg}"/>
    <circle cx="74" cy="78" r="9" fill="{det}"/>
    <circle cx="126" cy="78" r="9" fill="{det}"/>
    <path d="M70 102 Q100 132 130 102" fill="none" stroke="{det}" stroke-width="10" stroke-linecap="round"/>"""


def ic_maos_planta(fg, det):
    return f"""
    <path d="M100 138 L100 88" stroke="{fg}" stroke-width="11" stroke-linecap="round"/>
    <path d="M100 104 C68 104 48 84 46 56 C76 56 98 76 100 104 Z" fill="{fg}"/>
    <path d="M100 90 C102 58 124 38 156 36 C156 66 134 88 100 90 Z" fill="{fg}"/>
    <path d="M101 99 C88 88 74 76 62 66" stroke="{det}" stroke-width="5" stroke-linecap="round" fill="none"/>
    <path d="M101 85 C114 72 128 60 142 50" stroke="{det}" stroke-width="5" stroke-linecap="round" fill="none"/>
    <path d="M12 128 C24 120 40 122 50 132 L62 146 C70 150 88 150 100 150 C112 150 130 150 138 146
             L150 132 C160 122 176 120 188 128 L170 160 C160 176 140 184 118 184 L82 184
             C60 184 40 176 30 160 Z" fill="{fg}"/>
    <path d="M42 150 C56 166 74 172 100 172 C126 172 144 166 158 150" fill="none"
          stroke="{det}" stroke-width="5" stroke-linecap="round" opacity=".55"/>"""


def ic_balao(fg, det):
    return f"""
    <rect x="16" y="28" width="168" height="114" rx="44" fill="{fg}"/>
    <path d="M58 132 L42 178 L98 138 Z" fill="{fg}" stroke="{fg}" stroke-width="6" stroke-linejoin="round"/>
    <text x="100" y="110" text-anchor="middle" font-size="70" font-weight="900" fill="{det}">Hi!</text>"""


PILARES = [
    dict(slug="alfabetizacao", cor="azul", icone=ic_livro,
         topo="ALFABETIZAÇÃO", base="E LETRAMENTO", kicker="ALFABETIZAÇÃO E", nome="Letramento"),
    dict(slug="criatividade", cor="amarelo", icone=ic_lampada,
         topo="CRIATIVIDADE", base="E INOVAÇÃO", kicker="CRIATIVIDADE E", nome="Inovação"),
    dict(slug="socioemocional", cor="vermelho", icone=ic_coracao,
         topo="DESENVOLVIMENTO", base="SOCIOEMOCIONAL", kicker="DESENVOLVIMENTO", nome="Socioemocional"),
    dict(slug="responsabilidade-social", cor="verde", icone=ic_maos_planta,
         topo="RESPONSABILIDADE", base="SOCIAL", kicker="RESPONSABILIDADE", nome="Social"),
    dict(slug="ingles", cor="marinho", icone=ic_balao,
         topo="INGLÊS", base="TODOS OS DIAS", kicker="INGLÊS", nome="Todos os dias"),
]


def icone(p, fg, det, sombra, cx, cy, escala):
    """Ícone com a 'sombra 3D' deslocada, como as letras HS do escudo."""
    tx, ty = cx - 100 * escala, cy - 100 * escala
    corpo = p["icone"](fg, det)
    sombra_g = p["icone"](sombra, sombra)
    return (f'<g transform="translate({tx + 5 * escala:.1f} {ty + 8 * escala:.1f}) scale({escala})">{sombra_g}</g>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({escala})">{corpo}</g>')


def arco(cx, cy, r, a0, a1, horario=True):
    """Caminho de arco entre ângulos (graus, 0 = direita, sentido horário na tela)."""
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    grande = 1 if abs(a1 - a0) > 180 else 0
    return f"M{p0[0]:.2f} {p0[1]:.2f} A{r} {r} 0 {grande} {1 if horario else 0} {p1[0]:.2f} {p1[1]:.2f}"


def svg(w, h, corpo, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs><style>{FONT_CSS} text{{font-family:Nunito,sans-serif}}</style>{defs}</defs>{corpo}</svg>')


def tamanho_fonte(texto, largura, maximo, fator=0.66):
    return min(maximo, largura / (len(texto) * fator))


# ---------- Opção A: selo sólido com texto circular ----------
def opcao_a(p):
    c = CORES[p["cor"]]
    cx = cy = 300
    uid = p["slug"]
    fs_t = tamanho_fonte(p["topo"], 560, 40)
    fs_b = tamanho_fonte(p["base"], 560, 40)
    defs = (f'<path id="t-{uid}" d="{arco(cx, cy, 222, 180, 360)}"/>'
            f'<path id="b-{uid}" d="{arco(cx, cy, 254, 180, 0, horario=False)}"/>')
    corpo = f"""
    <circle cx="{cx}" cy="{cy}" r="290" fill="{c['escuro']}"/>
    <circle cx="{cx}" cy="{cy - 4}" r="284" fill="{c['base']}"/>
    <path d="{arco(cx, cy - 4, 274, 205, 335)}" fill="none" stroke="{c['claro']}" stroke-width="12" stroke-linecap="round"/>
    <circle cx="{cx}" cy="{cy}" r="200" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="2 12" stroke-linecap="round" opacity=".85"/>
    <circle cx="{cx}" cy="{cy}" r="186" fill="{c['escuro']}" opacity=".18"/>
    {icone(p, '#fff', c['base'], c['escuro'], cx, cy - 2, 1.45)}
    <text font-size="{fs_t:.1f}" font-weight="900" fill="#fff" letter-spacing="3">
      <textPath href="#t-{uid}" startOffset="50%" text-anchor="middle">{p['topo']}</textPath></text>
    <text font-size="{fs_b:.1f}" font-weight="900" fill="#fff" letter-spacing="3">
      <textPath href="#b-{uid}" startOffset="50%" text-anchor="middle">{p['base']}</textPath></text>
    <circle cx="{cx - 240}" cy="{cy}" r="8" fill="#fff"/>
    <circle cx="{cx + 240}" cy="{cy}" r="8" fill="#fff"/>"""
    return svg(600, 600, corpo, defs)


# ---------- Opção B: anel em 4 cores (quadrantes do escudo) + nome abaixo ----------
def opcao_b(p):
    c = CORES[p["cor"]]
    cx, cy = 300, 270
    anel = ""
    for i, cor in enumerate(QUADRANTES):
        a0 = -90 + i * 90 + 4
        anel += f'<path d="{arco(cx, cy, 236, a0, a0 + 82)}" fill="none" stroke="{cor}" stroke-width="30" stroke-linecap="round"/>'
    fs_k = tamanho_fonte(p["kicker"], 520, 34, 0.78)
    fs_n = tamanho_fonte(p["nome"], 560, 76, 0.6)
    corpo = f"""
    <circle cx="{cx}" cy="{cy}" r="262" fill="#fff"/>
    {anel}
    <circle cx="{cx}" cy="{cy + 6}" r="196" fill="{c['escuro']}"/>
    <circle cx="{cx}" cy="{cy}" r="196" fill="{c['base']}"/>
    <path d="{arco(cx, cy, 182, 215, 325)}" fill="none" stroke="{c['claro']}" stroke-width="10" stroke-linecap="round"/>
    {icone(p, '#fff', c['base'], c['escuro'], cx, cy, 1.38)}
    <text x="{cx}" y="606" text-anchor="middle" font-size="{fs_k:.1f}" font-weight="800" fill="{NAVY}" letter-spacing="7">{p['kicker']}</text>
    <text x="{cx}" y="{606 + 18 + fs_n * 0.86:.0f}" text-anchor="middle" font-size="{fs_n:.1f}" font-weight="900" fill="{NAVY}">{p['nome']}</text>"""
    return svg(600, 720, corpo)


# ---------- Opção C: botão claro com anel colorido e nome dentro ----------
def opcao_c(p):
    c = CORES[p["cor"]]
    cx = cy = 300
    fs_k = tamanho_fonte(p["kicker"], 330, 26, 0.8)
    fs_n = tamanho_fonte(p["nome"], 370, 54, 0.6)
    corpo = f"""
    <circle cx="{cx}" cy="{cy + 6}" r="290" fill="{c['escuro']}"/>
    <circle cx="{cx}" cy="{cy}" r="290" fill="{c['base']}"/>
    <path d="{arco(cx, cy, 276, 205, 335)}" fill="none" stroke="{c['claro']}" stroke-width="12" stroke-linecap="round"/>
    <circle cx="{cx}" cy="{cy}" r="256" fill="#fff"/>
    {icone(p, c['base'], '#fff', c['escuro'], cx, 226, 1.22)}
    <text x="{cx}" y="408" text-anchor="middle" font-size="{fs_k:.1f}" font-weight="800" fill="{c['escuro'] if p['cor'] != 'amarelo' else '#B86E00'}" letter-spacing="4">{p['kicker']}</text>
    <text x="{cx}" y="{408 + 12 + fs_n * 0.9:.0f}" text-anchor="middle" font-size="{fs_n:.1f}" font-weight="900" fill="{NAVY}">{p['nome']}</text>"""
    return svg(600, 600, corpo)


OPCOES = {
    "a": ("Opção A — Selo sólido com texto circular", opcao_a),
    "b": ("Opção B — Anel nas 4 cores do escudo", opcao_b),
    "c": ("Opção C — Botão claro com nome interno", opcao_c),
}


def main():
    out = ROOT / "svg"
    out.mkdir(exist_ok=True)
    secoes = ""
    for chave, (titulo, fn) in OPCOES.items():
        cards = ""
        for p in PILARES:
            s = fn(p)
            nome = f"opcao-{chave}_{p['slug']}"
            (out / f"{nome}.svg").write_text(s, encoding="utf-8")
            cards += f'<div class="selo" data-nome="{nome}">{s}</div>'
        secoes += f'<section data-opcao="{chave}"><h2>{titulo}</h2><div class="linha">{cards}</div></section>'
    html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Pilares Hermínio Silva</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{FONT_CSS}
body{{margin:0;background:{PAPER};font-family:Nunito,sans-serif;color:{NAVY};padding:48px 40px}}
h1{{font-weight:900;font-size:40px;margin:0 0 4px}} p.sub{{margin:0 0 40px;font-weight:700;letter-spacing:.2em;font-size:14px}}
h2{{font-weight:900;font-size:24px;margin:40px 0 20px}}
section{{padding:24px 32px 40px;background:{PAPER}}}
.linha{{display:flex;gap:36px;align-items:flex-start;flex-wrap:wrap}}
.selo svg{{width:300px;height:auto;display:block}}
</style></head><body>
<h1>Pilares Pedagógicos</h1><p class="sub">INSTITUTO EDUCACIONAL HERMÍNIO SILVA</p>
{secoes}</body></html>"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print("ok:", len(PILARES) * len(OPCOES), "selos")


if __name__ == "__main__":
    main()
