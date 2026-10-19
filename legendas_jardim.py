"""Legendas dinâmicas (tipografia cinética) + motion design para o vídeo da
Jardim dos Sonhos (mascote estrela, matrículas/natação) — 1080x1920, 30 fps,
44,3 s (as duas partes enviadas, unidas em sequência).

Paleta da escola: azul, lilás-azulado, pêssego, verde, lilás e laranja.
Destaque principal: "Matrículas 2027 abertas". Tempos das palavras em
assets/legendas_palavras_jardim.json (Whisper, revisados). Uso:

    python3 legendas_jardim.py ENTRADA.mp4 SAIDA.mp4
"""
import math
import os
import random

import kinetic as K
from kinetic import *  # noqa: F401,F403

BLUE = (55, 100, 183)
PERI = (121, 119, 255)
PEACH = (247, 209, 188)
GREEN = (29, 176, 105)
LILAC = (213, 173, 223)
ORANGE = (245, 134, 52)
WHITE = (255, 255, 255)
INK = (28, 48, 112)  # contorno / texto escuro
PALETTE = [BLUE, PERI, PEACH, GREEN, LILAC, ORANGE]

K.STROKE = INK
K.CUTS = [15.0667, 24.2333, 34.3]
K.TRANS_COLORS = [BLUE, PERI, PEACH, GREEN, LILAC, ORANGE, BLUE]
K.LOGO = os.path.join(K.HERE, "assets/logo_jardim_dos_sonhos.png")

# a estrela fica no centro/baixo; o alto do quadro (teto, parede, céu) é a área livre
TOP1, TOP2, TOP3 = 200, 330, 465


def wave(i, amp=12):
    def path(t):
        return 0, amp * math.sin(t * 9 - i * 0.6), 4 * math.sin(t * 9 - i * 0.6), 1, 1
    return path


def bubbles(t0, t1, n, seed, y0=1850, x=(80, 1000)):
    """Bolhas subindo da piscina."""
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + (t1 - t0 - 1.0) * i / n + rnd.uniform(0, 0.3)
        bx = rnd.uniform(*x)
        sp = rnd.uniform(260, 420)
        life = rnd.uniform(1.6, 2.6)
        ph = rnd.uniform(0, 6)

        def path(t, st=st, sp=sp, life=life, ph=ph):
            dt = max(0.0, t - st)
            return 22 * math.sin(dt * 4 + ph), -sp * dt, 0, 1, 1 - clamp01((dt - life * 0.6) / (life * 0.4))
        shape("ring" if i % 3 else "circle", bx, y0, st, st + life, rnd.randint(26, 58),
              WHITE, 0.16, inn="pop", out="none", path=path, z=2, alpha=0.85 if i % 3 else 0.55, idle=0)


# --- formas nas margens de cada cena
scene_decor(0.3, 14.85, 41, [WHITE, PEACH, PERI, ORANGE])
scene_decor(15.3, 24.0, 42, [WHITE, LILAC, PERI, GREEN])
scene_decor(24.5, 34.1, 43, [BLUE, PERI, GREEN, ORANGE, LILAC])
scene_decor(34.55, 44.4, 44, [BLUE, ORANGE, PERI, GREEN])
bubbles(4.2, 15.0, 26, 51)
bubbles(15.2, 24.1, 16, 52)

# 1 — "Agora presta atenção, porque esse é o nosso grande diferencial."
line([("AGORA", 0.0, 110, WHITE, dict(inn="drop")), ("PRESTA", 0.82, 110, WHITE, dict(inn="drop"))],
     TOP1, 1.8, out="up")
word("ATENÇÃO!", 540, TOP2 + 20, 1.16, 1.8, 160, WHITE, inn="stamp", rot=-4, idle=5, out="up")
ripple(540, TOP2 + 20, 1.2, PEACH, 560)
line([("PORQUE", 1.86, 95, WHITE), ("ESSE", 2.08, 95, WHITE), ("É", 2.3, 95, WHITE), ("O", 2.38, 95, WHITE),
      ("NOSSO", 2.46, 95, WHITE)], TOP1, 4.0, out="up", inn="drop")
word("GRANDE", 540, TOP2, 2.7, 4.0, 115, PEACH, inn="squash", out="up")
pill("DIFERENCIAL", 540, TOP3 + 20, 3.04, 4.0, 125, PERI, inn="stamp", rot=-3, out="up")
sparkles(540, TOP3 + 20, 3.1, 4.0, 420, [WHITE, PEACH], n=5, seed=61)

# 2 — "Aqui tem natação,"
line([("AQUI", 4.1, 110, WHITE, dict(inn="drop")), ("TEM", 4.26, 110, WHITE, dict(inn="drop"))], TOP1, 5.35,
     out="up")
pill("NATAÇÃO!", 540, TOP2 + 40, 4.44, 5.35, 160, BLUE, inn="squash", rot=-3, out="up", pulse=0.03)
ripple(540, TOP2 + 40, 4.5, WHITE, 640)
ripple(540, TOP2 + 40, 4.75, PEACH, 640)

# 3 — "somos a única escola da região com piscina"
line([("SOMOS", 5.42, 100, WHITE), ("A", 5.68, 100, WHITE)], TOP1, 7.95, out="up", inn="drop")
line([("ÚNICA", 5.92, 140, ORANGE, dict(inn="stamp", rot=-4)), ("ESCOLA", 6.16, 120, WHITE, dict(inn="drop"))],
     TOP2 + 10, 7.95, out="up")
line([("DA", 6.46, 95, WHITE), ("REGIÃO", 6.6, 105, PEACH, dict(inn="drop"))], TOP3 + 20, 7.95, out="up")
word("COM", 540, 1600, 6.94, 7.95, 90, WHITE, inn="rise", out="down")
for i, e in enumerate(letters("PISCINA", 540, 1730, 7.24, 7.95, 140, [WHITE, PEACH], stagger=0.04,
                              inn="rise", out="down")):
    e["path"] = wave(i)

# 4 — "e aulas de natação para os pequenos."
line([("E", 7.7, 100, WHITE), ("AULAS", 8.0, 110, WHITE, dict(inn="drop")), ("DE", 8.24, 100, WHITE)],
     TOP1, 10.7, out="up", inn="drop")
for i, e in enumerate(letters("NATAÇÃO", 540, TOP2 + 15, 8.44, 10.7, 150, [WHITE, PEACH], stagger=0.04,
                              inn="drop", out="up")):
    e["path"] = wave(i)
line([("PARA", 8.84, 90, WHITE), ("OS", 9.06, 90, WHITE)], 1590, 10.7, out="down", inn="rise")
word("PEQUENOS", 540, 1720, 9.26, 10.7, 145, PEACH, inn="squash", rot=-3, out="down")
hearts(540, 1600, 9.35, 10.7, n=5, seed=62, colors=(PEACH, LILAC, WHITE))

# 5 — "E ainda tem inglês, judô, balé, culinária e Lego Education."
line([("E", 15.06, 100, WHITE), ("AINDA", 15.42, 110, WHITE, dict(inn="drop")),
      ("TEM", 15.72, 110, WHITE, dict(inn="drop"))], TOP1, 20.3, out="up", inn="drop")
pill("INGLÊS", 300, TOP2 + 20, 15.9, 20.3, 100, PERI, inn="slide_l", rot=-5, out="left")
pill("JUDÔ", 790, TOP2 + 20, 16.62, 20.3, 100, GREEN, inn="slide_r", rot=4, out="right")
pill("BALÉ", 290, TOP3 + 55, 17.54, 20.3, 100, LILAC, INK, inn="drop", rot=3, out="left")
pill("CULINÁRIA", 740, TOP3 + 55, 18.2, 20.3, 100, ORANGE, inn="drop", rot=-3, out="right")
word("E", 540, 1440, 18.76, 20.3, 90, WHITE, inn="rise", out="down")
pill("LEGO EDUCATION", 540, 1580, 19.04, 20.3, 110, BLUE, inn="squash", rot=-2, out="down")
for k, (sx, sy) in enumerate([(300, TOP2 + 20), (790, TOP2 + 20), (290, TOP3 + 55), (740, TOP3 + 55),
                              (540, 1580)]):
    ripple(sx, sy, [15.95, 16.67, 17.59, 18.25, 19.1][k], WHITE, 300, dur=0.5)

# 6 — "Mas a natação é a alegria da turma!"
line([("MAS", 20.46, 100, WHITE), ("A", 20.72, 100, WHITE), ("NATAÇÃO", 21.0, 120, PEACH,
                                                            dict(inn="squash"))],
     TOP1, 24.0, out="up", inn="drop")
line([("É", 21.54, 95, WHITE), ("A", 22.1, 95, WHITE)], TOP2, 24.0, out="up", inn="drop")
for i, e in enumerate(letters("ALEGRIA", 540, TOP3 + 10, 22.3, 24.0, 170, [ORANGE], stagger=0.045,
                              inn="spin", out="up")):
    e["path"] = wave(i, 10)
sparkles(540, TOP3 + 10, 22.45, 24.0, 440, [WHITE, PEACH, ORANGE], n=6, size=70, seed=63)
word("DA TURMA!", 540, 1560, 22.74, 24.0, 125, WHITE, inn="rise", rot=-2, out="down")

# 7 — sala: "E tem cuidado com a alimentação também."
line([("E", 23.56, 95, WHITE), ("TEM", 24.44, 100, WHITE, dict(inn="drop")),
      ("CUIDADO", 24.7, 115, WHITE, dict(inn="drop"))], TOP1, 27.35, out="up", inn="drop")
line([("COM", 25.22, 95, WHITE), ("A", 25.5, 95, WHITE)], TOP2 - 10, 27.35, out="up", inn="drop")
word("ALIMENTAÇÃO", 540, TOP3 - 10, 25.62, 27.35, 130, GREEN, inn="squash", rot=-2, out="up")
word("TAMBÉM.", 540, 1480, 26.28, 27.35, 105, WHITE, inn="rise", out="down")

# 8 — "Hábitos saudáveis,"
word("HÁBITOS", 540, TOP1, 27.5, 29.05, 120, WHITE, inn="drop", out="up")
pill("SAUDÁVEIS", 540, TOP2 + 30, 28.06, 29.05, 140, GREEN, inn="stamp", rot=-3, out="up", pulse=0.03)
sparkles(540, TOP2 + 30, 28.15, 29.05, 400, [WHITE, GREEN, PEACH], n=5, seed=64)

# 9 — "num ambiente acolhedor e seguro,"
line([("NUM", 29.16, 95, WHITE), ("AMBIENTE", 29.26, 105, WHITE, dict(inn="drop"))], 1420, 31.25,
     out="down", inn="rise")
pill("ACOLHEDOR", 540, 1555, 29.74, 31.25, 120, PEACH, INK, inn="squash", rot=-2, out="down")
line([("E", 30.38, 95, WHITE), ("SEGURO,", 30.66, 115, WHITE, dict(inn="drop"))], 1700, 31.25, out="down",
     inn="rise")
shape("ring", 540, 1555, 29.8, 31.25, 560, PEACH, 0.04, inn="pop", z=3, pulse=0.05)

# 10 — "com equipe de pedagogas."
line([("COM", 31.38, 100, WHITE), ("EQUIPE", 31.56, 115, WHITE, dict(inn="drop")), ("DE", 31.98, 100, WHITE)],
     TOP1, 33.9, out="up", inn="drop")
pill("PEDAGOGAS", 540, TOP2 + 30, 32.28, 33.9, 135, LILAC, INK, inn="stamp", rot=-3, out="up")
ripple(540, TOP2 + 30, 32.33, LILAC, 560)

# 11 — fachada: "As matrículas de 2027 estão abertas!"  (destaque principal)
word("AS", 540, 95, 34.34, 37.3, 80, WHITE, inn="drop", out="up")
pill("MATRÍCULAS", 540, 225, 34.56, 37.3, 145, BLUE, inn="squash", rot=-2, out="up", pulse=0.025)
ripple(540, 225, 34.6, WHITE, 760)
shape("burst", 620, 410, 35.0, 37.3, 560, PEACH, 18, inn="pop", spin=30, z=3, alpha=0.95)
word("DE", 215, 410, 35.06, 37.3, 90, WHITE, inn="drop", out="up")
f27 = font("L", 200)
for i, ch in enumerate("2027"):
    cx = 620 - f27.getlength("2027") / 2 + f27.getlength("2027"[:i]) + f27.getlength(ch) / 2
    e = word(ch, cx, 405, 35.06 + 0.07 * i, 37.3, 200, ORANGE, inn="drop", out="up", idle=4)
    e["roll"] = (35.06 + 0.07 * i, 0.45 + 0.1 * i)  # dígitos girando até parar
    e["roll_size"] = 200
    e["roll_fill"] = ORANGE
word("ESTÃO", 540, 560, 35.92, 37.3, 90, WHITE, inn="slide_l", out="up")
pill("ABERTAS!", 540, 690, 36.28, 37.3, 135, GREEN, inn="stamp", rot=-5, out="up", pulse=0.04)
ripple(540, 690, 36.33, GREEN, 640)
confetti(120, 1920 - 260, 36.3, n=50, ang=-65, spread=25, speed=(1500, 2300), seed=65, life=2.2,
         colors=PALETTE + [WHITE])
confetti(960, 1920 - 260, 36.3, n=50, ang=-115, spread=25, speed=(1500, 2300), seed=66, life=2.2,
         colors=PALETTE + [WHITE])
# selo que permanece até o fim
pill("MATRÍCULAS 2027 ABERTAS", 540, 105, 37.35, 44.4, 66, ORANGE, inn="slide_l", rot=-2, out="none",
     idle=2)

# 12 — "Vem conhecer a escola e agende sua visita pelo WhatsApp."
line([("VEM", 37.4, 115, WHITE, dict(inn="drop")), ("CONHECER", 37.56, 120, PEACH, dict(inn="drop"))],
     TOP2 - 20, 38.7, out="up")
line([("A", 37.9, 100, WHITE), ("ESCOLA", 38.14, 120, WHITE, dict(inn="squash"))], TOP3 - 10, 38.7,
     out="up")
line([("E", 38.44, 100, WHITE), ("AGENDE", 38.78, 115, WHITE, dict(inn="drop")),
      ("SUA", 39.06, 100, WHITE), ("VISITA", 39.22, 115, PEACH, dict(inn="drop"))], TOP2 - 20, 40.6,
     out="up")
word("PELO", 190, TOP3 + 5, 39.58, 40.6, 85, WHITE, inn="rise", out="up")
pill("WHATSAPP", 650, TOP3 + 5, 39.8, 40.6, 110, GREEN, inn="stamp", rot=-3, out="up")
ripple(650, TOP3 + 5, 39.85, GREEN, 520)

# 13 — "Eu tô te esperando! Tchau, tchau!"  + logo
line([("EU", 40.72, 100, WHITE), ("TÔ", 40.8, 100, WHITE), ("TE", 40.94, 100, WHITE)], TOP2 - 20, 41.95,
     out="up", inn="drop")
word("ESPERANDO!", 540, TOP3 - 5, 41.22, 41.95, 140, PERI, inn="squash", rot=-3, out="up")
shape("burst", 540, 470, 41.95, 44.4, 760, WHITE, 18, inn="pop", spin=25, z=3, alpha=0.9, out="none")
add(("logo", 720, 470), 540, 470, 42.0, 44.4, inn="squash", out="none", idle=4, pulse=0.02, z=5, din=0.45)
ripple(540, 470, 42.05, ORANGE, 760)
for i, e in enumerate(letters("TCHAU TCHAU!", 540, 1735, 42.02, 44.4, 115, [WHITE, PEACH], stagger=0.035,
                              inn="drop", out="none")):
    e["path"] = wave(i, 9)

K.PUNCH = [(1.16, 0.04, 8), (3.04, 0.02, 0), (4.44, 0.04, 0), (5.92, 0.02, 0), (15.9, 0.015, 0),
           (19.04, 0.02, 0), (22.3, 0.03, 0), (28.06, 0.025, 0), (32.28, 0.02, 0), (34.56, 0.04, 0),
           (35.06, 0.05, 10), (36.28, 0.06, 14), (39.8, 0.025, 0), (42.0, 0.03, 0)]


if __name__ == "__main__":
    K.main()
