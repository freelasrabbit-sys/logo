"""Gera src/data/edl.json (lista de cortes + legendas) a partir das transcrições do Whisper.

Uso: python3 scripts/build_edl.py transcripts.json

Cada corte é dado em segundos do vídeo original; as bordas são ajustadas para
coincidir com o início/fim das palavras, para não cortar no meio de uma fala.
"""

import json
import re
import sys
from pathlib import Path

FPS = 30
TRANSITION = 12  # frames de transição entre depoimentos
PAD_IN, PAD_OUT = 0.12, 0.25  # respiro antes/depois de cada trecho (s)

# chave da transcrição -> arquivo em public/clips, tamanho (px) e identificação
SOURCES = {
    "3aa6d4bc": ("clips/ex-alunos.mp4", 1024, 576, "Henrique e Isabela · ex-alunos"),
    "23e02f9a": ("clips/ex-aluna.mp4", 476, 768, "Ex-aluna"),
    "464fb1ac": ("clips/professora-rosangela.mp4", 480, 848, "Rosângela · ex-professora"),
    "397c8cbe": ("clips/professora-juscelia.mp4", 576, 1024, "Juscelia · ex-professora"),
    "6f98fa35": ("clips/familia.mp4", 1024, 576, "Eric e Raquel · pais de ex-alunos"),
}

# (fonte, início, fim) em segundos — a ordem aqui é a ordem do vídeo
CUTS = [
    # Ex-alunos: apresentação, cresceram junto com a escola, orgulho
    ("3aa6d4bc", 0.6, 12.3),
    ("3aa6d4bc", 17.8, 34.5),
    ("3aa6d4bc", 63.9, 70.1),
    # Ex-aluna: 10 anos na escola, segunda casa, orgulho
    ("23e02f9a", 1.9, 16.8),
    ("23e02f9a", 39.1, 43.4),
    ("23e02f9a", 84.4, 88.5),
    # Prof. Rosângela: depoimento completo, sem a pausa
    ("464fb1ac", 0.7, 13.9),
    ("464fb1ac", 15.1, 25.9),
    # Prof. Juscelia: apresentação, gerações de crianças, aprendizados, fecho
    ("397c8cbe", 0.0, 11.0),
    ("397c8cbe", 11.7, 20.9),
    ("397c8cbe", 68.2, 81.3),
    ("397c8cbe", 98.2, 104.7),
    # Família: 14 anos, gratidão, fazem parte da história, despedida
    ("6f98fa35", 0.0, 17.8),
    ("6f98fa35", 22.7, 30.2),
    ("6f98fa35", 81.3, 89.3),
    ("6f98fa35", 106.6, 111.0),
]

# Correções de grafia nas legendas
FIXES = [
    (r"\bCapitul[úu]\b", "Capítulo I"),
    (r"\b[Cc]ap[íi]tulo 1\b", "Capítulo I"),
    (r"\bcapítulo\b", "Capítulo"),
    (r"\bhistorias\b", "histórias"),
]


def fix_text(text: str) -> str:
    for pat, rep in FIXES:
        text = re.sub(pat, rep, text)
    return text


def main() -> None:
    raw = json.loads(Path(sys.argv[1]).read_text())
    words = {
        Path(k).stem[:8]: [w for seg in v for w in seg["w"]] for k, v in raw.items()
    }

    edl = json.loads(Path("src/data/edl.json").read_text())
    segments = []
    prev_src = None
    nth = 0  # posição do trecho dentro do mesmo depoimento
    for i, (key, a, b) in enumerate(CUTS):
        ws = [w for w in words[key] if w[0] >= a - 0.05 and w[0] < b]
        start, end = ws[0][0], ws[-1][1]
        new_speaker = key != prev_src
        nth = 0 if new_speaker else nth + 1
        next_new = i + 1 == len(CUTS) or CUTS[i + 1][0] != key
        pad_in = PAD_IN + (TRANSITION / FPS if new_speaker else 0)
        pad_out = PAD_OUT + (TRANSITION / FPS if next_new else 0)
        t0 = max(0.0, start - pad_in)
        t1 = end + pad_out
        trim = round(t0 * FPS)
        dur = round(t1 * FPS) - trim

        # "1" de "Capítulo 1" vira um token separado no Whisper: junta antes de corrigir
        text_words = []
        for w in ws:
            m = re.fullmatch(r"1([.,!?]?)", w[2].strip())
            if m and text_words and "apítulo" in text_words[-1][2]:
                prev = text_words[-1]
                text_words[-1] = (prev[0], w[1], prev[2] + " I" + m.group(1))
                continue
            text_words.append(tuple(w))
        captions = [
            {
                "text": fix_text(w[2] if w[2].startswith(" ") else " " + w[2]),
                "startMs": round((w[0] - trim / FPS) * 1000),
                "endMs": round((w[1] - trim / FPS) * 1000),
                "timestampMs": None,
                "confidence": None,
            }
            for w in text_words
        ]
        src, width, height, label = SOURCES[key]
        segments.append(
            {
                "src": src,
                "srcWidth": width,
                "srcHeight": height,
                "trimBefore": trim,
                "durationInFrames": dur,
                # alterna o enquadramento a cada corte seco para disfarçar o "pulo"
                "zoom": 1.0 if nth % 2 == 0 else 1.08,
                "label": label,
                "newSpeaker": new_speaker,
                "captions": captions,
            }
        )
        prev_src = key

    edl["transitionFrames"] = TRANSITION
    edl["segments"] = segments
    Path("src/data/edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1))

    total = (
        edl["cover"]["durationInFrames"]
        + edl["end"]["durationInFrames"]
        + sum(s["durationInFrames"] for s in segments)
        - TRANSITION * (sum(s["newSpeaker"] for s in segments) + 1)
    )
    print(f"{len(segments)} trechos, duração total {total / FPS:.1f}s")


if __name__ == "__main__":
    main()
