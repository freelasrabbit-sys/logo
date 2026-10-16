"""Legendas dinâmicas (tipografia cinética) + motion design para o vídeo
do leão — 1080x1920, 30 fps, 44,7 s.

Paleta: verdes e branco na maior parte; amarelo e vermelho-alaranjado só
nas palavras de destaque e em alguns elementos. Tempos das palavras em
assets/legendas_palavras_leao.json (transcritos com Whisper). Uso:

    python3 legendas_leao.py ENTRADA.mp4 SAIDA.mp4
"""
import math

import kinetic as K
from kinetic import *  # noqa: F401,F403

DARK = (6, 62, 36)       # contorno
GREEN = (28, 160, 78)
MINT = (150, 232, 150)   # verde claro (texto sobre o fundo verde)
LEAF = (88, 200, 92)
WHITE = (255, 255, 255)
YELLOW = (255, 206, 36)
REDOR = (255, 84, 28)    # vermelho-alaranjado

K.STROKE = DARK
K.CUTS = [14.6333, 35.1333, 40.3]
K.TRANS_COLORS = [DARK, GREEN, WHITE, LEAF, YELLOW, GREEN, REDOR]

# planos: aberto (0–35,1 s), médio (35,1–40,3 s), close no rosto (40,3 s–fim)
TOP1, TOP2 = 175, 305
BOT0, BOT1, BOT2 = 1420, 1550, 1680


def wave(i, amp=14):
    def path(t):
        return 0, amp * math.sin(t * 9 - i * 0.6), 4 * math.sin(t * 9 - i * 0.6), 1, 1
    return path


# --- formas geométricas nas margens de cada plano
scene_decor(0.3, 14.4, 21, [WHITE, MINT, YELLOW, LEAF])
scene_decor(14.9, 34.9, 22, [MINT, WHITE, LEAF, YELLOW, WHITE])
scene_decor(35.4, 40.1, 23, [WHITE, MINT, REDOR, LEAF])
scene_decor(40.6, 44.8, 24, [WHITE, YELLOW, MINT, LEAF])

# 0 — abertura sem fala: anéis pulsando em volta do leão
for i, (rx, ry) in enumerate([(540, 1000), (540, 1000), (540, 1000)]):
    ripple(rx, ry, 0.25 + i * 0.35, [WHITE, MINT, YELLOW][i], 900, dur=1.1)
shape("ring", 540, 1000, 1.3, 4.95, 1000, WHITE, 0.012, inn="pop", out="pop", pulse=0.03, z=1,
      alpha=0.5)

# 1 — "Ei você,"  (o leão acena)
shape("burst", 330, TOP1 + 60, 5.0, 6.6, 520, YELLOW, 16, inn="pop", spin=40, z=3, alpha=0.9)
word("EI", 330, TOP1 + 60, 5.06, 6.6, 250, WHITE, inn="stamp", rot=-8, idle=5)
ripple(250, 800, 5.1, WHITE, 300)
ripple(250, 800, 5.35, MINT, 300)
pill("VOCÊ,", 740, TOP2 + 10, 5.74, 6.6, 120, REDOR, inn="spin", rot=6)
sparkles(540, TOP1 + 90, 5.2, 6.6, 420, [WHITE, YELLOW], n=6, seed=31)

# 2 — "já pensou em fazer parte de uma história"
line([("JÁ", 6.7, 105, WHITE, dict(inn="drop")), ("PENSOU", 6.92, 105, WHITE, dict(inn="drop")),
      ("EM", 7.18, 85, WHITE)], TOP1, 8.25, out="up")
line([("FAZER", 7.3, 110, WHITE, dict(inn="slide_l")),
      ("PARTE", 7.52, 120, MINT, dict(inn="squash", rot=-4))], TOP2 + 5, 8.25, out="up")
ripple(780, TOP2, 7.55, MINT, 280)
line([("DE", 7.78, 85, WHITE), ("UMA", 7.92, 85, WHITE)], BOT0, 9.4, out="down", inn="rise")
pill("HISTÓRIA", 540, BOT1 + 10, 8.02, 9.4, 120, WHITE, GREEN, inn="squash", rot=-3, out="down")

# 3 — "de mais de 31 anos dedicada à educação?"
line([("DE", 8.32, 90, WHITE), ("MAIS", 8.54, 105, MINT, dict(inn="drop")), ("DE", 8.7, 90, WHITE)],
     TOP1 - 10, 10.95, out="up", inn="drop")
shape("burst", 540, TOP2 + 60, 8.95, 10.95, 600, YELLOW, 18, inn="pop", spin=30, z=3, alpha=0.9)
f31 = font("L", 250)
for i, ch in enumerate("31"):
    cx = 430 - f31.getlength("31") / 2 + f31.getlength("31"[:i]) + f31.getlength(ch) / 2
    e = word(ch, cx, TOP2 + 55, 9.0 + 0.08 * i, 10.95, 250, YELLOW, inn="drop", out="up", idle=4)
    e["roll"] = (9.0 + 0.08 * i, 0.35 + 0.1 * i)  # dígitos girando até parar
    e["roll_size"] = 250
    e["roll_fill"] = YELLOW
word("ANOS", 720, TOP2 + 85, 9.36, 10.95, 135, WHITE, inn="slide_r", rot=-4, out="up")
ripple(540, TOP2 + 60, 9.05, WHITE, 640)
confetti(540, TOP2 + 60, 9.1, n=36, ang=90, spread=80, speed=(300, 900), seed=32,
         colors=[WHITE, MINT, YELLOW, LEAF])
line([("DEDICADA", 9.66, 100, WHITE, dict(inn="slide_l")), ("À", 10.06, 100, WHITE)], BOT0 + 10, 10.95,
     out="down")
pill("EDUCAÇÃO?", 540, BOT1 + 30, 10.16, 10.95, 130, GREEN, inn="stamp", rot=3, out="down", pulse=0.03)
ripple(540, BOT1 + 30, 10.2, MINT, 640)

# 4 — "Aqui unimos conhecimento, valores e formação do caráter."
line([("AQUI", 11.12, 110, WHITE, dict(inn="drop")), ("UNIMOS", 11.34, 120, MINT, dict(inn="squash"))],
     TOP1, 12.85, out="up")
line([("E", 12.76, 90, WHITE), ("FORMAÇÃO", 12.94, 110, WHITE, dict(inn="drop")), ("DO", 13.36, 90, WHITE)],
     TOP1, 14.4, out="up")
pill("CONHECIMENTO", 540, BOT0 - 30, 11.68, 14.4, 100, GREEN, inn="slide_l", rot=-3, out="left")
shape("plus", 540, BOT0 + 52, 12.35, 14.4, 46, WHITE, inn="spin", spin=90, z=6)
pill("VALORES", 540, BOT1 + 15, 12.4, 14.4, 100, WHITE, GREEN, inn="slide_r", rot=3, out="right")
shape("plus", 540, BOT1 + 97, 13.55, 14.4, 46, WHITE, inn="spin", spin=-90, z=6)
word("CARÁTER", 540, BOT2 + 40, 13.6, 14.4, 150, YELLOW, inn="stamp", rot=-3, out="down")
ripple(540, BOT2 + 40, 13.65, YELLOW, 560)
sparkles(540, BOT2 + 40, 13.7, 14.4, 400, [YELLOW, WHITE], n=5, seed=33)

# 5 — "Por isso, nossa educação não termina quando a aula acaba."
line([("POR", 14.6, 110, WHITE, dict(inn="drop")), ("ISSO,", 14.86, 110, WHITE, dict(inn="drop"))],
     TOP1, 18.45, out="up")
line([("NOSSA", 15.72, 95, WHITE), ("EDUCAÇÃO", 15.86, 130, MINT, dict(inn="squash", rot=-3))],
     TOP2 + 10, 18.45, out="up")
pill("NÃO", 265, BOT0 - 10, 16.5, 18.45, 105, REDOR, inn="stamp", rot=-6, out="down")
word("TERMINA", 715, BOT0 - 5, 16.8, 18.45, 110, WHITE, inn="slide_r", out="down")
line([("QUANDO", 17.28, 90, WHITE), ("A", 17.54, 90, WHITE), ("AULA", 17.7, 110, YELLOW, dict(inn="drop")),
      ("ACABA.", 17.88, 110, WHITE, dict(inn="drop"))], BOT1 + 30, 18.45, out="down")
shape("triangle", 140, BOT0 - 140, 16.55, 18.45, 70, MINT, inn="spin", spin=80, z=4)
shape("circle", 950, BOT0 - 150, 16.6, 18.45, 46, YELLOW, inn="pop", z=4)

# 6 — "Ela está nas descobertas, nas decisões, na convivência"
line([("ELA", 18.84, 100, WHITE), ("ESTÁ", 19.08, 100, WHITE), ("NAS", 19.3, 100, WHITE)], TOP1, 20.95,
     out="up", inn="drop")
letters("DESCOBERTAS", 540, BOT1, 19.6, 21.0, 145, [WHITE, MINT], stagger=0.05, inn="drop", out="down")
sparkles(540, BOT1, 19.8, 21.0, 470, [YELLOW, WHITE, MINT], n=7, size=70, seed=34)
word("NAS", 540, TOP1 - 10, 21.12, 22.6, 90, WHITE, inn="drop", out="up")
pill("DECISÕES", 540, TOP2 + 10, 21.46, 22.6, 125, WHITE, GREEN, inn="squash", rot=-3, out="up")
for i, (ax, rot) in enumerate([(130, 90), (950, -90)]):
    def side(t, i=i):
        dt = t - 21.5
        return (-1 if i == 0 else 1) * ((dt * 160) % 60), 0, 0, 1, 1
    shape("arrow", ax, TOP2 + 10, 21.5, 22.6, 70, YELLOW, inn="pop", rot=rot, path=side, z=4)
word("NA", 540, BOT0, 22.7, 24.3, 90, WHITE, inn="rise", out="down")
pill("CONVIVÊNCIA", 540, BOT1 + 20, 23.0, 24.3, 120, GREEN, inn="stamp", rot=2, out="down", pulse=0.03)
hearts(540, BOT0 - 60, 23.05, 24.3, n=6, seed=35, colors=(REDOR, YELLOW, WHITE))
for k in range(6):
    def orbit(t, k=k):
        a = t * 2.6 + k * math.pi / 3
        return 470 * math.cos(a), 160 * math.sin(a), 0, 1, 1
    shape("circle", 540, 900, 23.1 + 0.04 * k, 24.3, 34, [WHITE, MINT, YELLOW][k % 3], inn="pop",
          path=orbit, z=2)

# 7 — "e na maneira como cada aluno aprende a enxergar o mundo!"
line([("E", 23.88, 95, WHITE), ("NA", 24.36, 95, WHITE), ("MANEIRA", 24.62, 110, MINT, dict(inn="drop"))],
     TOP1, 26.35, out="up", inn="drop")
line([("COMO", 24.98, 95, WHITE), ("CADA", 25.42, 95, WHITE), ("ALUNO", 25.8, 125, YELLOW,
                                                              dict(inn="stamp", rot=-4))],
     TOP2 + 10, 26.35, out="up")
line([("APRENDE", 26.44, 115, WHITE, dict(inn="slide_l")), ("A", 27.16, 95, WHITE)], TOP1, 29.35,
     out="up")
for i, e in enumerate(letters("ENXERGAR", 540, TOP2 + 10, 27.32, 29.35, 130, [MINT, WHITE],
                              stagger=0.04, inn="spin", out="up")):
    e["path"] = wave(i, 10)
word("O", 200, BOT1 - 20, 27.82, 29.35, 110, WHITE, inn="drop", out="down")
shape("ring", 620, BOT1, 28.06, 29.35, 520, MINT, 0.05, inn="pop", z=3, pulse=0.05)
word("MUNDO!", 620, BOT1, 28.06, 29.35, 165, YELLOW, inn="stamp", rot=-3, idle=4, out="down")
ripple(620, BOT1, 28.1, YELLOW, 640)
for k in range(5):
    def orbit2(t, k=k):
        a = -t * 3 + k * 2 * math.pi / 5
        return 290 * math.cos(a), 290 * math.sin(a) * 0.9, 0, 1, 1
    shape(["star", "circle", "sparkle", "circle", "star"][k], 620, BOT1, 28.1 + 0.03 * k, 29.35, 38,
          [WHITE, MINT, YELLOW, WHITE, MINT][k], inn="pop", path=orbit2, z=6)

# 8 — "Venha conhecer nossa proposta pedagógica."
for i, e in enumerate(letters("VENHA", 540, TOP1 + 10, 29.56, 32.6, 175, [WHITE, MINT], stagger=0.05,
                              inn="drop", out="up")):
    e["path"] = wave(i)
word("CONHECER", 540, TOP2 + 30, 30.04, 32.6, 115, MINT, inn="slide_r", rot=-2, out="up")
line([("NOSSA", 30.52, 95, WHITE, dict(inn="drop")), ("PROPOSTA", 30.82, 115, WHITE, dict(inn="drop"))],
     BOT0, 32.6, out="down")
pill("PEDAGÓGICA", 540, BOT1 + 25, 31.38, 32.6, 130, WHITE, GREEN, inn="stamp", rot=-3, out="down",
     pulse=0.03)
ripple(540, BOT1 + 25, 31.42, WHITE, 680)
shape("star", 140, BOT0 - 150, 31.45, 32.6, 76, YELLOW, inn="spin", spin=90, z=4)
shape("plus", 950, BOT0 - 150, 31.5, 32.6, 60, WHITE, inn="spin", spin=-60, z=4)

# 9 — "Porque formar um bom aluno é importante,"
line([("PORQUE", 32.88, 100, WHITE), ("FORMAR", 33.04, 110, MINT, dict(inn="drop")), ("UM", 33.42, 90, WHITE)],
     TOP1, 35.0, out="up", inn="drop")
line([("BOM", 33.58, 115, WHITE, dict(inn="squash")), ("ALUNO", 33.74, 125, WHITE, dict(inn="slide_r"))],
     TOP2 + 10, 35.0, out="up")
word("É", 540, BOT0, 34.08, 35.0, 95, WHITE, inn="rise", out="down")
word("IMPORTANTE,", 540, BOT1 + 10, 34.3, 35.0, 145, YELLOW, inn="stamp", rot=-3, out="down")
ripple(540, BOT1 + 10, 34.35, YELLOW, 620)

# 10 — plano médio: "mas contribuir para a formação de um ser humano"
line([("MAS", 35.4, 90, WHITE), ("CONTRIBUIR", 35.56, 110, MINT, dict(inn="squash"))], TOP1 - 20, 38.6,
     out="up", inn="drop")
line([("PARA", 36.1, 85, WHITE), ("A", 36.26, 85, WHITE), ("FORMAÇÃO", 36.4, 100, WHITE, dict(inn="drop"))],
     BOT0 - 40, 37.35, out="down", inn="rise")
line([("DE", 36.8, 85, WHITE), ("UM", 36.94, 85, WHITE)], BOT1 - 50, 37.35, out="down", inn="rise")
pill("SER HUMANO", 540, BOT1 + 85, 37.04, 37.35, 130, GREEN, inn="stamp", rot=-2, out="pop")

# 11 — "consciente, ético e preparado para a vida,"
pill("CONSCIENTE,", 540, BOT0 - 30, 37.46, 40.1, 110, GREEN, inn="slide_l", rot=-3, out="left")
pill("ÉTICO", 540, BOT1 + 30, 38.44, 40.1, 120, WHITE, GREEN, inn="squash", rot=3, out="right")
ripple(540, BOT1 + 30, 38.48, WHITE, 560)
line([("E", 38.74, 85, WHITE), ("PREPARADO", 38.94, 110, MINT, dict(inn="drop"))], TOP1 - 20, 40.1,
     out="up", inn="drop")
line([("PARA", 39.4, 90, WHITE), ("A", 39.64, 90, WHITE), ("VIDA,", 39.84, 120, REDOR,
                                                         dict(inn="stamp", rot=-4))],
     BOT2 + 50, 40.1, out="down", inn="rise")

# 12 — close: "é o que dá sentido à nossa história."  + fechamento
line([("É", 40.6, 90, WHITE), ("O", 40.64, 90, WHITE), ("QUE", 40.74, 90, WHITE), ("DÁ", 40.86, 90, WHITE)],
     BOT0 + 40, 41.4, out="up", inn="drop")
pill("SENTIDO", 540, BOT1 + 60, 41.02, 41.4, 125, GREEN, inn="stamp", rot=-3, out="pop")
word("À NOSSA", 540, BOT0 + 50, 41.46, 44.8, 95, WHITE, inn="drop", out="none")
shape("burst", 540, BOT1 + 85, 41.8, 44.8, 820, YELLOW, 18, inn="pop", spin=25, z=3, alpha=0.85,
      out="none")
letters("HISTÓRIA", 540, BOT1 + 85, 41.84, 44.8, 180, [YELLOW, WHITE], stagger=0.04, inn="spin",
        out="none")
ripple(540, BOT1 + 85, 41.9, YELLOW, 760)
confetti(140, 1920 - 200, 41.95, n=40, ang=-65, spread=25, speed=(1500, 2200), seed=36, life=2.2,
         colors=[WHITE, MINT, LEAF, YELLOW, REDOR])
confetti(940, 1920 - 200, 41.95, n=40, ang=-115, spread=25, speed=(1500, 2200), seed=37, life=2.2,
         colors=[WHITE, MINT, LEAF, YELLOW, REDOR])
pill("HÁ MAIS DE 31 ANOS", 540, TOP1 - 40, 42.5, 44.8, 72, WHITE, GREEN, inn="slide_l", rot=-2, out="none")
word("DEDICADOS À EDUCAÇÃO", 540, TOP1 + 75, 42.75, 44.8, 72, WHITE, inn="drop", out="none")

K.PUNCH = [(5.06, 0.07, 14), (5.74, 0.03, 0), (7.52, 0.02, 0), (9.0, 0.05, 10), (10.16, 0.03, 0),
           (11.34, 0.02, 0), (13.6, 0.04, 8), (16.5, 0.04, 8), (19.6, 0.03, 0), (21.46, 0.02, 0),
           (23.0, 0.03, 0), (25.8, 0.02, 0), (28.06, 0.05, 10), (29.56, 0.03, 0), (31.38, 0.03, 0),
           (34.3, 0.03, 6), (37.04, 0.03, 0), (38.44, 0.03, 0), (39.84, 0.03, 6), (41.02, 0.02, 0),
           (41.84, 0.05, 12)]


if __name__ == "__main__":
    K.main()
