"""Legendas dinâmicas (tipografia cinética) + motion design para o vídeo
"Espaço Criança Feliz" — 1080x1920, 30 fps.

Tempos das palavras em assets/legendas_palavras.json (transcritos com Whisper).
Uso:

    python3 legendas.py ENTRADA.mp4 SAIDA.mp4
"""
import math
import os
import random

import kinetic as K
from kinetic import *  # noqa: F401,F403

K.CUTS = [8.7667, 18.2, 26.3333]  # trocas de cenário (detectadas com ffmpeg)

TOP1, TOP2, TOP3 = 175, 300, 420
BOT0, BOT1, BOT2 = 1390, 1515, 1645

# --- cenas: formas decorativas nas margens
scene_decor(0.15, 8.55, 11, [YELLOW, WHITE, RED, YELLOW])
scene_decor(9.0, 18.0, 12, [BLUE, YELLOW, RED, GREEN, PINK])
scene_decor(18.45, 26.1, 13, [RED, BLUE, YELLOW, PURPLE])
scene_decor(26.55, 34.1, 14, [ORANGE, BLUE, PINK, GREEN])

# 1 — "Ei, você aí!"
shape("burst", 540, BOT1 - 20, 0.0, 1.75, 620, YELLOW, 16, inn="pop", spin=40, z=3, alpha=0.9)
word("EI,", 540, BOT1 - 30, 0.0, 1.75, 280, YELLOW, inn="stamp", rot=-6, idle=5)
ripple(540, BOT1 - 30, 0.05, WHITE, 420)
word("VOCÊ", 400, BOT2 + 30, 0.9, 1.75, 130, WHITE, inn="slide_l", rot=-3)
pill("AÍ!", 760, BOT2 + 30, 1.28, 1.75, 110, RED, inn="spin", rot=7)
sparkles(540, BOT1, 0.15, 1.75, 380, [WHITE, YELLOW], n=6, seed=5)

# 2 — "Já pensou em fazer parte"
line([("JÁ", 1.94, 120, YELLOW, dict(inn="drop")), ("PENSOU", 2.18, 120, WHITE, dict(inn="drop"))],
     TOP1, 3.6, out="up")
line([("EM", 2.6, 90, WHITE), ("FAZER", 2.74, 110, WHITE, dict(inn="slide_l")),
      ("PARTE", 3.0, 110, YELLOW, dict(inn="squash", rot=-4))], TOP2 + 10, 3.6, out="up")
ripple(780, TOP2 + 10, 3.0, YELLOW, 260)

# 3 — "de uma escola cheia de descobertas"
line([("DE", 3.3, 90, WHITE), ("UMA", 3.48, 90, WHITE), ("ESCOLA", 3.6, 120, YELLOW, dict(inn="stamp"))],
     BOT0, 5.6, out="down")
line([("CHEIA", 3.98, 95, WHITE, dict(inn="slide_r")), ("DE", 4.36, 80, WHITE)], BOT1 - 10, 5.6, out="down")
letters("DESCOBERTAS", 540, BOT2, 4.6, 5.6, 150, RAINBOW, stagger=0.045, out="down")
sparkles(540, BOT2, 4.7, 5.6, 470, [YELLOW, WHITE, CYAN], n=6, size=70, seed=8)
shape("triangle", 140, BOT0 - 60, 3.62, 5.6, 70, YELLOW, inn="spin", spin=60, z=4)
shape("circle", 950, BOT0 - 70, 3.7, 5.6, 46, RED, inn="pop", z=4)

# 4 — "amizades e momentos incríveis?"
word("AMIZADES", 540, TOP1 + 10, 5.72, 7.95, 150, PINK, inn="squash", rot=-3, out="up")
hearts(540, TOP2 + 20, 5.75, 7.95, n=6)
line([("E", 6.32, 85, WHITE), ("MOMENTOS", 6.48, 105, WHITE, dict(inn="slide_r"))], TOP2 + 15, 7.95, out="up")
shape("burst", 540, BOT1 + 10, 7.0, 7.95, 760, WHITE, 18, inn="pop", spin=-30, z=3, alpha=0.85)
word("INCRÍVEIS?", 540, BOT1, 7.04, 7.95, 165, YELLOW, inn="stamp", rot=4, idle=5)
ripple(540, BOT1, 7.08, YELLOW, 600)
confetti(540, BOT1, 7.1, n=34, seed=2, speed=(800, 1400))

# 5 — "Aqui no Espaço Criança Feliz"
line([("AQUI", 8.85, 110, WHITE, dict(inn="drop")), ("NO", 9.0, 110, YELLOW, dict(inn="drop"))],
     TOP1, 10.3, out="up")
shape("burst", 540, BOT1 + 20, 9.12, 10.45, 900, WHITE, 18, inn="pop", spin=25, z=3, alpha=0.85)
if os.path.exists(LOGO):
    add(("logo", 880, 480), 540, BOT1 + 20, 9.16, 10.45, inn="squash", out="down", idle=4, pulse=0.02,
        z=5, din=0.45)
else:  # sem o PNG do logo: nome da escola em texto
    word("ESPAÇO", 540, BOT1 - 20, 9.16, 10.45, 110, YELLOW, inn="squash", out="down")
    letters("CRIANÇA FELIZ", 540, BOT2 - 10, 9.56, 10.45, 125, RAINBOW, stagger=0.04, inn="drop",
            out="down", idle=4)
ripple(540, BOT1 + 20, 9.2, YELLOW, 820)
sparkles(540, BOT1 + 20, 9.4, 10.45, 470, [YELLOW, PINK, CYAN, WHITE], n=7, size=70, seed=9)

# 6 — "cada dia é uma nova aventura"
line([("CADA", 10.56, 95, WHITE), ("DIA", 10.8, 95, YELLOW, dict(inn="squash")), ("É", 10.94, 95, WHITE),
      ("UMA", 11.1, 95, WHITE)], TOP1, 12.4, out="up", inn="drop")
word("NOVA", 540, TOP2, 11.32, 12.4, 115, CYAN, inn="slide_l", rot=-4, out="up")
shape("squiggle", 175, TOP2 + 10, 11.36, 12.4, 140, YELLOW, inn="spin", rot=-10, z=3)
shape("squiggle", 905, TOP2 + 10, 11.36, 12.4, 140, PINK, inn="spin", rot=10, z=3)


def wave(i):
    def path(t):
        return 0, 14 * math.sin(t * 9 - i * 0.6), 4 * math.sin(t * 9 - i * 0.6), 1, 1
    return path


for i, e in enumerate(letters("AVENTURA", 540, BOT1, 11.54, 12.4, 160, [ORANGE, YELLOW], stagger=0.04,
                              inn="spin", out="down")):
    e["path"] = wave(i)
ripple(540, BOT1, 11.6, ORANGE, 560)

# 7 — "Aprendemos, brincamos e crescemos juntos"
pill("APRENDEMOS", 540, TOP1 + 15, 12.64, 14.0, 105, GREEN, inn="slide_l", rot=-4, out="right")
shape("triangle", 135, TOP1 + 120, 12.7, 14.0, 70, YELLOW, inn="spin", spin=90, z=4)
pill("BRINCAMOS", 540, BOT1, 13.44, 14.42, 110, RED, inn="slide_r", rot=4, out="left")
shape("star", 930, BOT0 - 30, 13.5, 14.42, 90, YELLOW, inn="spin", spin=120, z=6)
shape("circle", 150, BOT2, 13.55, 14.42, 56, CYAN, inn="pop", z=6)
pill("E CRESCEMOS", 540, TOP1 + 15, 14.02, 15.15, 100, BLUE, inn="rise", rot=-2, out="up")
for i, ax in enumerate([150, 930]):
    def up(t, i=i):
        dt = t - 14.05
        return 0, -((dt * 260 + i * 60) % 130), 0, 1, 1
    shape("arrow", ax, TOP2 + 40, 14.05, 15.15, 64, GREEN, inn="pop", path=up, z=4)
shape("ring", 540, BOT1, 14.46, 15.15, 560, YELLOW, 0.05, inn="pop", spin=0, z=3, pulse=0.06)
word("JUNTOS!", 540, BOT1, 14.46, 15.15, 175, YELLOW, inn="stamp", rot=-3, idle=4)
for k in range(6):
    def orbit(t, k=k):
        a = t * 3 + k * math.pi / 3
        return 300 * math.cos(a), 300 * math.sin(a) * 0.95, 0, 1, 1
    shape("circle", 540, BOT1, 14.5 + 0.03 * k, 15.15, 34, RAINBOW[k], inn="pop", path=orbit, z=6)

# 8 — "construindo um futuro cheio de possibilidades"
line([("CONSTRUINDO", 15.32, 95, WHITE, dict(inn="slide_l")), ("UM", 15.58, 95, WHITE)], BOT0 - 30,
     17.7, out="down")
add(("pill", "FUTURO", "L", 150, BLUE, YELLOW), 540, BOT1 + 5, 15.74, 17.7, inn="squash", rot=-3, out="down")
ripple(540, BOT1 + 5, 15.8, BLUE, 520)
line([("CHEIO", 16.08, 85, WHITE, dict(inn="drop")), ("DE", 16.44, 85, WHITE, dict(inn="drop"))], TOP1,
     17.7, out="up")
letters("POSSIBILIDADES", 540, TOP2, 16.72, 17.7, 130, [YELLOW, CYAN, PINK, GREEN, ORANGE], stagger=0.035,
        inn="rise", out="up")
for i, (bx, by) in enumerate([(120, TOP2 + 150), (960, TOP2 + 160), (270, TOP3 + 80), (820, TOP3 + 90)]):
    ripple(bx, by, 16.8 + i * 0.15, [YELLOW, CYAN, PINK, GREEN][i], 160)
    shape("circle", bx, by, 16.8 + i * 0.15, 17.7, 40, [YELLOW, CYAN, PINK, GREEN][i], z=4)

# 9 — "E tem uma novidade especial"
line([("E", 18.32, 90, WHITE), ("TEM", 18.5, 90, WHITE), ("UMA", 18.62, 90, WHITE)], TOP1, 20.05,
     out="up", inn="drop")
pill("NOVIDADE", 540, TOP2 + 10, 18.86, 20.05, 125, RED, inn="stamp", rot=-4, out="up", idle=4)
confetti(540, TOP2 + 10, 18.9, n=40, ang=90, spread=80, speed=(300, 900), seed=4)
word("ESPECIAL", 540, BOT1, 19.34, 20.05, 160, YELLOW, inn="squash", rot=3, out="down")
sparkles(540, BOT1, 19.38, 20.05, 430, [YELLOW, WHITE, PINK], n=6, size=70, seed=10)

# 10 — "nossas matrículas para novos alunos"
word("NOSSAS", 540, BOT0 - 40, 20.22, 22.45, 100, WHITE, inn="drop", out="down")
pill("MATRÍCULAS", 540, BOT1 - 10, 20.5, 22.45, 130, YELLOW, NAVY, inn="squash", rot=-2, out="down",
     pulse=0.03)
ripple(540, BOT1 - 10, 20.55, YELLOW, 700)
line([("PARA", 21.22, 85, WHITE), ("NOVOS", 21.52, 95, WHITE, dict(inn="drop")),
      ("ALUNOS", 21.98, 115, CYAN, dict(inn="stamp"))], BOT2 + 20, 22.45, out="down")
shape("star", 130, BOT1 - 140, 20.55, 22.45, 80, YELLOW, inn="spin", spin=90, z=4)
shape("plus", 950, BOT1 - 150, 20.6, 22.45, 64, RED, inn="spin", spin=-60, z=4)

# 11 — "em 2027 estão abertas!"
word("EM", 540, TOP1 - 20, 22.56, 25.95, 90, WHITE, inn="drop", out="up")
shape("burst", 540, TOP2 + 30, 22.6, 25.95, 640, YELLOW, 18, inn="pop", spin=30, z=3, alpha=0.9)
f27 = font("L", 230)
tot = f27.getlength("2027")
for i, ch in enumerate("2027"):
    cx = 540 - tot / 2 + f27.getlength("2027"[:i]) + f27.getlength(ch) / 2
    e = word(ch, cx, TOP2 + 30, 22.56 + 0.07 * i, 25.95, 230, [RED, BLUE, RED, BLUE][i], inn="drop",
             out="up", idle=4)
    e["roll"] = (22.56 + 0.07 * i, 0.55 + 0.1 * i)  # dígitos girando até parar
    e["roll_size"] = 230
    e["roll_fill"] = [RED, BLUE, RED, BLUE][i]
word("ESTÃO", 540, BOT0 - 30, 23.56, 25.95, 105, WHITE, inn="slide_r", out="down")
pill("ABERTAS!", 540, BOT1 + 20, 24.0, 25.95, 150, GREEN, inn="stamp", rot=-5, out="down", pulse=0.04)
confetti(120, H - 300, 24.02, n=45, ang=-65, spread=25, speed=(1500, 2300), seed=6, life=2.0)
confetti(960, H - 300, 24.02, n=45, ang=-115, spread=25, speed=(1500, 2300), seed=7, life=2.0)
ripple(540, BOT1 + 20, 24.05, WHITE, 700)

# 12 — "Venha conhecer nossa escola"
for i, e in enumerate(letters("VENHA", 540, TOP1, 26.1, 28.55, 170, [ORANGE, YELLOW], stagger=0.05,
                              inn="drop", out="up")):
    e["path"] = wave(i)
word("CONHECER", 540, TOP2 + 15, 26.94, 28.55, 110, WHITE, inn="slide_l", rot=-2, out="up")
line([("NOSSA", 27.4, 100, WHITE, dict(inn="drop")), ("ESCOLA", 27.76, 140, YELLOW, dict(inn="stamp"))],
     BOT1, 28.55, out="down")
shape("triangle", 140, BOT1 - 140, 27.8, 28.55, 70, PINK, inn="spin", spin=90, z=4)
shape("ring", 950, BOT1 - 150, 27.8, 28.55, 64, ORANGE, inn="pop", z=4)

# 13 — "e fazer parte dessa história!"
line([("E", 28.64, 95, WHITE), ("FAZER", 28.64, 110, WHITE, dict(inn="drop")),
      ("PARTE", 28.94, 120, PINK, dict(inn="squash", rot=-4))], TOP1 + 10, 30.65, out="up")
word("DESSA", 540, BOT0 - 30, 29.34, 30.65, 100, WHITE, inn="rise", out="down")
letters("HISTÓRIA!", 540, BOT1 + 10, 29.6, 30.65, 165, RAINBOW, stagger=0.04, inn="spin", out="down")
sparkles(540, BOT1 + 10, 29.7, 30.65, 450, [YELLOW, WHITE, PINK, CYAN], n=7, size=70, seed=12)

# 14 — "Estamos esperando por você!"  + fechamento
word("ESTAMOS", 540, TOP1, 30.8, 32.55, 105, WHITE, inn="drop", out="up")
word("ESPERANDO", 540, TOP2 + 10, 31.08, 32.55, 130, CYAN, inn="slide_r", rot=-3, out="up")
word("POR", 540, BOT0 - 40, 31.64, 34.2, 95, WHITE, inn="rise", out="none")
shape("heart", 540, BOT1 + 30, 31.98, 34.2, 520, PINK, inn="pop", z=3, pulse=0.07, out="none")
word("VOCÊ!", 540, BOT1 + 20, 31.98, 34.2, 210, YELLOW, inn="stamp", rot=-4, idle=4, out="none")
ripple(540, BOT1 + 20, 32.02, PINK, 700)
confetti(540, BOT1, 32.05, n=40, seed=9, speed=(900, 1500))
pill("MATRÍCULAS ABERTAS", 540, TOP1, 32.6, 34.2, 80, RED, inn="slide_l", rot=-2, out="none")
letters("2027", 540, TOP2 + 25, 32.75, 34.2, 150, [YELLOW], stagger=0.06, inn="drop", out="none")


K.PUNCH = [(0.0, 0.07, 14), (0.9, 0.03, 0), (3.6, 0.02, 0), (4.64, 0.03, 0), (7.04, 0.04, 8),
         (9.56, 0.03, 0), (12.64, 0.02, 0), (13.44, 0.02, 0), (14.46, 0.04, 6), (15.74, 0.025, 0),
         (18.86, 0.04, 8), (20.5, 0.025, 0), (22.56, 0.06, 14), (24.0, 0.05, 12), (27.76, 0.025, 0),
         (29.62, 0.03, 0), (31.98, 0.05, 10)]


if __name__ == "__main__":
    K.main()
