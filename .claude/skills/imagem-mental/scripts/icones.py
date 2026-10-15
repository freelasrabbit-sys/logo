"""Ícones de linha (Tabler Icons, licença MIT) e busca por palavra-chave em PT/EN."""
from __future__ import annotations

import json
import os
import unicodedata
from functools import lru_cache

ICONES_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icones")

# Conceitos frequentes em imagens mentais de escolas -> ícone Tabler.
# A busca usa estas chaves primeiro e depois as tags em inglês do Tabler.
PT = {
    "acolh": "heart-handshake",
    "afeto": "heart",
    "amor": "heart",
    "carinho": "heart",
    "seguro": "shield-check",
    "seguranca": "shield-check",
    "protec": "shield-heart",
    "bilingue": "world",
    "ingles": "language",
    "idioma": "language",
    "lingua": "language",
    "integral": "clock-hour-4",
    "periodo": "clock-hour-4",
    "familia": "users-group",
    "parceria": "users-group",
    "pais": "users-group",
    "social": "heart-handshake",
    "solidar": "heart-handshake",
    "comunidade": "friends",
    "competenc": "certificate",
    "habilidade": "puzzle",
    "excelencia": "award",
    "qualidade": "rosette-discount-check",
    "tradic": "school",
    "anos": "calendar-star",
    "experiencia": "calendar-star",
    "especializ": "school",
    "infantil": "mood-kid",
    "infancia": "mood-kid",
    "crianca": "mood-kid",
    "brincar": "horse-toy",
    "brincando": "horse-toy",
    "ludico": "horse-toy",
    "protagonis": "book",
    "aprendiz": "book",
    "leitura": "book",
    "livro": "book",
    "ensino": "books",
    "educac": "school",
    "pedagog": "school",
    "projeto": "bulb",
    "inova": "bulb",
    "criativ": "palette",
    "arte": "palette",
    "musica": "music",
    "esporte": "ball-football",
    "fisica": "run",
    "alimenta": "apple",
    "saudavel": "apple",
    "nutric": "apple",
    "natureza": "plant",
    "sustentab": "plant-2",
    "verde": "plant",
    "area externa": "trees",
    "espaco": "building-community",
    "estrutura": "building-community",
    "sala": "chalkboard",
    "laborator": "flask",
    "ciencia": "flask",
    "tecnolog": "device-laptop",
    "robotica": "robot",
    "digital": "device-laptop",
    "professor": "chalkboard",
    "docente": "chalkboard",
    "educador": "chalkboard",
    "equipe": "users",
    "corpo": "users",
    "custo": "coin",
    "beneficio": "coin",
    "preco": "coin",
    "valor": "diamond",
    "valores": "diamond",
    "etica": "scale",
    "cidadania": "flag",
    "emocion": "mood-smile",
    "socioemocion": "mood-smile",
    "inclus": "accessible",
    "diversid": "friends",
    "vestibular": "target-arrow",
    "enem": "target-arrow",
    "aprovac": "trophy",
    "resultado": "trophy",
    "olimpiad": "medal",
    "futuro": "rocket",
    "lideranc": "flag",
    "empreend": "briefcase",
    "material": "backpack",
    "transporte": "bus",
    "matematic": "math-symbols",
    "alfabetiz": "abc",
    "matricula": "clipboard-check",
    "individual": "user-heart",
    "personaliz": "user-heart",
    "atencao": "eye-heart",
    "cuidado": "heart-plus",
    "saude": "heart-plus",
    "desenvolv": "trending-up",
    "evolu": "trending-up",
    "crescimento": "seedling",
    "autonom": "rocket",
    "comunica": "messages",
    "dialogo": "messages",
}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _nos():
    with open(os.path.join(ICONES_DIR, "tabler-outline.json"), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _tags():
    with open(os.path.join(ICONES_DIR, "tabler-tags.json"), encoding="utf-8") as f:
        return json.load(f)


def existe(nome: str) -> bool:
    return nome in _nos()


def sugerir(texto: str, n: int = 8) -> list[str]:
    """Sugere ícones para um texto em português (ou inglês)."""
    t = _norm(texto)
    achados: list[str] = []
    for chave, icone in PT.items():
        if chave in t and icone not in achados and existe(icone):
            achados.append(icone)
    palavras = [p for p in t.replace("-", " ").split() if len(p) > 2]
    pontos: dict[str, int] = {}
    for nome, tags in _tags().items():
        if nome.startswith("brand-"):
            continue
        alvo = " ".join([nome.replace("-", " ")] + [_norm(str(x)) for x in tags if x])
        s = sum(3 if p == nome else 1 for p in palavras if p in alvo)
        if s:
            pontos[nome] = s - (1 if nome.endswith("-off") else 0)
    for nome, _ in sorted(pontos.items(), key=lambda kv: (-kv[1], len(kv[0]))):
        if nome not in achados:
            achados.append(nome)
    return achados[:n] or ["star"]


def svg(nome: str, cx: float, cy: float, tamanho: float, cor: str, espessura: float = 1.6,
        id_=None) -> str:
    """Desenha o ícone centrado em (cx, cy) com largura `tamanho`."""
    if not existe(nome):
        nome = sugerir(nome, 1)[0]
    esc = tamanho / 24
    partes = []
    for tag, attrs in _nos()[nome]:
        if attrs.get("stroke") == "none":
            continue
        a = " ".join(f'{k}="{v}"' for k, v in attrs.items() if k != "key")
        partes.append(f"<{tag} {a}/>")
    id_attr = f' id="{id_}"' if id_ else ""
    return (
        f'<g{id_attr} data-icone="{nome}" transform="translate({cx - tamanho / 2:.2f} {cy - tamanho / 2:.2f}) '
        f'scale({esc:.4f})" fill="none" stroke="{cor}" stroke-width="{espessura}" '
        f'stroke-linecap="round" stroke-linejoin="round">{"".join(partes)}</g>'
    )


if __name__ == "__main__":
    import sys

    for termo in sys.argv[1:] or ["Ensino Bilíngue"]:
        print(f"{termo}: {', '.join(sugerir(termo))}")
