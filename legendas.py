"""Legendas dinâmicas (tipografia cinética) + motion design para o vídeo
"Espaço Criança Feliz" — 1080x1920, 30 fps.

Lê o vídeo original, desenha por cima de cada quadro as palavras faladas
(tempos de assets/legendas_palavras.json, transcritos com Whisper), formas
animadas, confetes, transições e "camera punch", e grava com o áudio
original. Uso:

    python3 legendas.py ENTRADA.mp4 SAIDA.mp4
"""
import math
import multiprocessing
import os
import random
import subprocess
import sys
import tempfile
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
LILITA = os.path.join(HERE, "assets/fonts/LilitaOne-Regular.ttf")
FREDOKA = os.path.join(HERE, "assets/fonts/Fredoka-Variable.ttf")

# paleta da marca (boné azul, sol amarelo, arco-íris)
NAVY = (18, 28, 96)
BLUE = (30, 76, 214)
YELLOW = (255, 212, 32)
RED = (238, 46, 58)
GREEN = (36, 178, 82)
ORANGE = (255, 138, 22)
PINK = (255, 84, 158)
CYAN = (32, 188, 240)
PURPLE = (140, 72, 224)
WHITE = (255, 255, 255)
RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
CUTS = [8.7667, 18.2, 26.3333]  # trocas de cenário (detectadas com ffmpeg)


# ---------------------------------------------------------------- easing
def clamp01(x):
    return min(1.0, max(0.0, x))


def ease_out_back(x, k=1.9):
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def ease_out_expo(x):
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    return x ** 3


def ease_in_out_cubic(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_elastic(x):
    if x <= 0 or x >= 1:
        return clamp01(x)
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


# ---------------------------------------------------------------- fontes / sprites
@lru_cache(None)
def font(fk, size):
    if fk == "L":
        return ImageFont.truetype(LILITA, size)
    f = ImageFont.truetype(FREDOKA, size)
    f.set_variation_by_axes([700, 100])  # Bold
    return f


def stroke_w(size):
    return max(3, int(size * 0.085))


def text_w(text, fk, size):
    return font(fk, size).getlength(text) + 2 * stroke_w(size)


@lru_cache(None)
def text_sprite(text, fk, size, fill, stroke=NAVY, letter_colors=None):
    f = font(fk, size)
    sw = stroke_w(size)
    so = max(4, int(size * 0.07))  # sombra "3D"
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    pad = int(size * 0.1)
    w, h = r - l + 2 * pad, b - t + 2 * pad + so
    im = Image.new("RGBA", (w, h), stroke + (0,))
    d = ImageDraw.Draw(im)
    ox, oy = pad - l, pad - t
    shadow = tuple(int(c * 0.55) for c in stroke) + (200,)
    d.text((ox, oy + so), text, font=f, fill=shadow, stroke_width=sw, stroke_fill=shadow)
    if letter_colors:
        d.text((ox, oy), text, font=f, fill=stroke, stroke_width=sw, stroke_fill=stroke)
        for i, ch in enumerate(text):
            x = ox + f.getlength(text[:i])
            d.text((x, oy), ch, font=f, fill=letter_colors[i % len(letter_colors)])
    else:
        d.text((ox, oy), text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


@lru_cache(None)
def pill_sprite(text, fk, size, bg, fg=WHITE, radius=None, padx=None):
    """Palavra dentro de um 'adesivo' arredondado com sombra."""
    f = font(fk, size)
    l, t, r, b = f.getbbox(text)
    padx = int(size * 0.42) if padx is None else padx
    pady = int(size * 0.24)
    so = max(6, int(size * 0.1))
    bw, bh = r - l + 2 * padx, b - t + 2 * pady
    rad = bh // 2 if radius is None else radius
    S = 2
    im = Image.new("RGBA", ((bw + 8) * S, (bh + so + 8) * S), bg + (0,))
    d = ImageDraw.Draw(im)
    dark = tuple(int(c * 0.55) for c in bg)
    d.rounded_rectangle([4 * S, (4 + so) * S, (4 + bw) * S, (4 + bh + so) * S], rad * S, fill=dark + (255,))
    d.rounded_rectangle([4 * S, 4 * S, (4 + bw) * S, (4 + bh) * S], rad * S, fill=bg + (255,),
                        outline=WHITE + (255,), width=int(size * 0.06) * S)
    im = im.resize((bw + 8, bh + so + 8), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((4 + padx - l, 4 + pady - t), text, font=f, fill=fg)
    return im


def _poly_star(cx, cy, r_out, r_in, n, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


@lru_cache(None)
def shape_sprite(kind, size, color, extra=0):
    """Formas desenhadas com supersampling 4x para bordas suaves."""
    S = 4
    n = size * S
    im = Image.new("RGBA", (n, n), color + (0,))
    d = ImageDraw.Draw(im)
    c = n / 2
    col = color + (255,)
    if kind == "circle":
        d.ellipse([0, 0, n - 1, n - 1], fill=col)
    elif kind == "ring":
        wdt = int(n * (extra or 0.13))
        d.ellipse([0, 0, n - 1, n - 1], outline=col, width=wdt)
    elif kind == "star":
        d.polygon(_poly_star(c, c * 1.04, c, c * 0.48, 5), fill=col)
    elif kind == "sparkle":
        d.polygon(_poly_star(c, c, c, c * 0.2, 4), fill=col)
    elif kind == "plus":
        t = n * 0.15
        d.rounded_rectangle([c - t, 0, c + t, n], int(t), fill=col)
        d.rounded_rectangle([0, c - t, n, c + t], int(t), fill=col)
    elif kind == "triangle":
        d.polygon([(c, n * 0.06), (n * 0.96, n * 0.88), (n * 0.04, n * 0.88)], fill=col)
    elif kind == "heart":
        pts = []
        for i in range(120):
            a = 2 * math.pi * i / 120
            x = 16 * math.sin(a) ** 3
            y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((c + x * n / 36, c * 0.92 - y * n / 36))
        d.polygon(pts, fill=col)
    elif kind == "burst":  # raios em volta de um centro vazio
        rays = extra or 14
        for i in range(rays):
            a = 2 * math.pi * i / rays
            a1, a2 = a - math.pi / rays * 0.45, a + math.pi / rays * 0.45
            r0, r1 = c * 0.55, c
            d.polygon([(c + r0 * math.cos(a1), c + r0 * math.sin(a1)),
                       (c + r1 * math.cos(a), c + r1 * math.sin(a)),
                       (c + r0 * math.cos(a2), c + r0 * math.sin(a2))], fill=col)
    elif kind == "squiggle":
        t = n * 0.07
        prev = None
        for i in range(81):
            x = t + (n - 2 * t) * i / 80
            y = c + n * 0.18 * math.sin(i / 80 * 4 * math.pi)
            d.ellipse([x - t, y - t, x + t, y + t], fill=col)
            if prev:
                d.line([prev, (x, y)], fill=col, width=int(2 * t))
            prev = (x, y)
    elif kind == "arrow":
        t = n * 0.14
        d.polygon([(c, 0), (n * 0.92, n * 0.45), (c + t * 1.6, n * 0.45), (c + t * 1.6, n),
                   (c - t * 1.6, n), (c - t * 1.6, n * 0.45), (n * 0.08, n * 0.45)], fill=col)
    elif kind == "confetti":
        d.rounded_rectangle([0, n * 0.3, n - 1, n * 0.7], int(n * 0.08), fill=col)
    elif kind == "blob":
        pts = []
        rnd = random.Random(extra)
        k = [rnd.uniform(0, 2 * math.pi) for _ in range(3)]
        for i in range(160):
            a = 2 * math.pi * i / 160
            r = c * (0.86 + 0.06 * math.sin(3 * a + k[0]) + 0.05 * math.sin(5 * a + k[1])
                     + 0.03 * math.sin(2 * a + k[2]))
            pts.append((c + r * math.cos(a), c + r * math.sin(a)))
        d.polygon(pts, fill=col)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(None)
def rainbow_sprite(radius, band, sweep_q):
    """Arco-íris desenhado até 'sweep_q' (0..60 → 0..180°)."""
    S = 2
    w, h = 2 * radius * S, radius * S + 4
    im = Image.new("RGBA", (w, h), WHITE + (0,))
    d = ImageDraw.Draw(im)
    sweep = 180 * sweep_q / 60
    if sweep > 0:
        for i, col in enumerate(RAINBOW):
            r = (radius - i * band) * S
            d.pieslice([w / 2 - r, h - r, w / 2 + r, h + r], 180, 180 + sweep, fill=col + (255,))
        r = (radius - len(RAINBOW) * band) * S
        d.pieslice([w / 2 - r, h - r, w / 2 + r, h + r], 0, 360, fill=WHITE + (0,))
        # apaga o miolo
        mask = Image.new("L", (w, h), 255)
        ImageDraw.Draw(mask).ellipse([w / 2 - r, h - r, w / 2 + r, h + r], fill=0)
        im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", (w, h), 0), mask))
    return im.resize((w // S, h // S), Image.LANCZOS)


def get_sprite(key):
    kind = key[0]
    if kind == "text":
        return text_sprite(*key[1:])
    if kind == "pill":
        return pill_sprite(*key[1:])
    if kind == "rainbow":
        return rainbow_sprite(*key[1:])
    return shape_sprite(*key)


# ---------------------------------------------------------------- linha do tempo
ELEMS = []


def add(key, x, y, t0, t1, inn="pop", out="pop", rot=0.0, idle=3.0, z=5, din=0.3,
        spin=0.0, path=None, alpha=1.0, scale=1.0, pulse=0.0):
    e = dict(key=key, x=x, y=y, t0=t0, t1=t1, inn=inn, out=out, rot=rot, idle=idle,
             z=z, din=din, spin=spin, path=path, alpha=alpha, scale=scale, pulse=pulse,
             phase=random.Random(len(ELEMS)).uniform(0, 6.28))
    ELEMS.append(e)
    return e


def word(text, x, y, t0, t1, size, fill=WHITE, fk="L", **kw):
    return add(("text", text, fk, size, fill), x, y, t0, t1, **kw)


def pill(text, x, y, t0, t1, size, bg, fg=WHITE, fk="L", **kw):
    return add(("pill", text, fk, size, bg, fg), x, y, t0, t1, **kw)


def shape(kind, x, y, t0, t1, size, color, extra=0, **kw):
    kw.setdefault("z", 2)
    return add((kind, size, color, extra), x, y, t0, t1, **kw)


def line(items, y, t1, cx=540, maxw=990, gap=0.26, **common):
    """Uma linha de palavras que entram uma a uma, cada uma no tempo da fala.
    items: (texto, t0, tamanho, cor[, opções])"""
    widths = [text_w(it[0], common.get("fk", "L"), it[2]) for it in items]
    gaps = [it[2] * gap for it in items[1:]]
    total = sum(widths) + sum(gaps)
    k = min(1.0, maxw / total)
    x = cx - total * k / 2
    out = []
    for i, it in enumerate(items):
        opts = dict(common)
        if len(it) > 4:
            opts.update(it[4])
        size = int(it[2] * k)
        wx = x + widths[i] * k / 2
        out.append(word(it[0], wx, y, it[1], t1, size, it[3], **opts))
        x += widths[i] * k + (gaps[i] * k if i < len(gaps) else 0)
    return out


def letters(text, cx, y, t0, t1, size, colors, stagger=0.035, fk="L", inn="drop", **kw):
    """Cada letra é um elemento próprio (entrada escalonada)."""
    f = font(fk, size)
    total = f.getlength(text)
    x0 = cx - total / 2
    els = []
    j = 0
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        lx = x0 + f.getlength(text[:i]) + f.getlength(ch) / 2
        els.append(word(ch, lx, y, t0 + j * stagger, t1, size, colors[j % len(colors)], fk=fk,
                        inn=inn, **kw))
        j += 1
    return els


def ripple(x, y, t0, color, size=300, dur=0.7, z=1):
    def path(t):
        p = clamp01((t - t0) / dur)
        return 0, 0, 0, 0.25 + 2.2 * ease_out_cubic(p), 1 - p
    shape("ring", x, y, t0, t0 + dur, size, color, 0.06, inn="none", out="none", path=path, z=z)


def sparkles(x, y, t0, t1, spread, colors, n=5, size=60, seed=0):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = spread * rnd.uniform(0.75, 1.1)
        shape("sparkle", x + r * math.cos(a), y + 0.55 * r * math.sin(a), t0 + i * 0.05, t1,
              int(size * rnd.uniform(0.6, 1.2)), colors[i % len(colors)], inn="spin",
              spin=rnd.choice([-90, 90]), pulse=0.25, z=6)


def confetti(x, y, t0, n=50, ang=-90, spread=70, speed=(900, 1700), seed=1, life=1.8):
    rnd = random.Random(seed)
    for i in range(n):
        a = math.radians(ang + rnd.uniform(-spread, spread))
        v = rnd.uniform(*speed)
        vx, vy = v * math.cos(a), v * math.sin(a)
        spin = rnd.uniform(-720, 720)
        sway = rnd.uniform(20, 60)
        kind = rnd.choice(["confetti", "confetti", "circle", "star"])
        sz = rnd.randint(18, 34) if kind != "confetti" else rnd.randint(28, 46)
        st = t0 + rnd.uniform(0, 0.08)

        def path(t, vx=vx, vy=vy, spin=spin, sway=sway, st=st):
            dt = max(0.0, t - st)
            drag = math.exp(-1.6 * dt)
            dx = vx * (1 - drag) / 1.6 + sway * math.sin(dt * 7)
            dy = vy * (1 - drag) / 1.6 + 0.5 * 1500 * dt * dt
            fade = 1 - clamp01((dt - life * 0.7) / (life * 0.3))
            flip = abs(math.cos(dt * 9))  # papel "virando"
            return dx, dy, spin * dt, (1.0, 0.35 + 0.65 * flip), fade
        shape(kind, x, y, st, st + life, sz, rnd.choice(RAINBOW + [PINK]), inn="none", out="none",
              path=path, z=8, idle=0)


def hearts(x, y, t0, t1, n=5, seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        dx0 = rnd.uniform(-330, 330)
        st = t0 + i * 0.12
        sp = rnd.uniform(140, 220)

        def path(t, st=st, sp=sp, dx0=dx0):
            dt = max(0.0, t - st)
            return dx0 + 18 * math.sin(dt * 5), -sp * dt, 12 * math.sin(dt * 4), 1, 1
        shape("heart", x, y, st, t1, rnd.randint(50, 84), rnd.choice([PINK, RED]), inn="pop",
              out="pop", path=path, z=3)


def scene_decor(t0, t1, seed, colors):
    """Formas geométricas flutuando nas margens durante a cena."""
    rnd = random.Random(seed)
    spots = [(70, 520), (1010, 600), (90, 900), (990, 1000), (60, 1260), (1015, 1340),
             (190, 110), (890, 120), (540, 60)]
    kinds = ["ring", "plus", "star", "circle", "sparkle", "triangle", "squiggle", "ring", "plus"]
    rnd.shuffle(kinds)
    for i, (x, y) in enumerate(spots):
        k = kinds[i]
        sz = rnd.randint(46, 80) if k != "squiggle" else 120
        shape(k, x + rnd.uniform(-15, 15), y + rnd.uniform(-30, 30), t0 + 0.08 * i, t1 - 0.02 * i,
              sz, colors[i % len(colors)], inn="spin", out="pop", idle=10,
              spin=rnd.choice([-1, 1]) * rnd.uniform(15, 45), z=1, alpha=0.95)


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
line([("AQUI", 8.85, 100, WHITE, dict(inn="drop")), ("NO", 9.0, 100, WHITE, dict(inn="drop"))],
     BOT0 - 40, 10.45, out="down")


rb = add(("rainbow", 360, 20, 60), 540, BOT1 + 70, 9.1, 10.45, inn="none", out="pop", idle=0, z=3)
rb["sweep"] = (9.1, 9.65)
word("ESPAÇO", 540, BOT1 + 10, 9.16, 10.45, 110, YELLOW, inn="squash", out="down")
letters("CRIANÇA FELIZ", 540, BOT2 + 20, 9.56, 10.45, 125, RAINBOW, stagger=0.04, inn="drop",
        out="down", idle=4)
sparkles(540, BOT1 - 120, 9.6, 10.45, 400, [YELLOW, PINK, CYAN], n=5, seed=9)

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

ELEMS.sort(key=lambda e: e["z"])

# "camera punch": (tempo, intensidade, tremor)
PUNCH = [(0.0, 0.07, 14), (0.9, 0.03, 0), (3.6, 0.02, 0), (4.64, 0.03, 0), (7.04, 0.04, 8),
         (9.56, 0.03, 0), (12.64, 0.02, 0), (13.44, 0.02, 0), (14.46, 0.04, 6), (15.74, 0.025, 0),
         (18.86, 0.04, 8), (20.5, 0.025, 0), (22.56, 0.06, 14), (24.0, 0.05, 12), (27.76, 0.025, 0),
         (29.62, 0.03, 0), (31.98, 0.05, 10)]


# ---------------------------------------------------------------- render
def elem_state(e, t):
    out_d = 0.22
    if t < e["t0"] or t > e["t1"] + (out_d if e["out"] != "none" else 0):
        return None
    p = clamp01((t - e["t0"]) / e["din"])
    q = clamp01((t - e["t1"]) / out_d) if e["out"] != "none" else 0.0
    dx = dy = 0.0
    rot = e["rot"]
    s = e["scale"]
    sx = sy = 1.0
    a = e["alpha"]
    inn = e["inn"]
    if inn == "pop":
        s *= max(0.0, ease_out_back(p))
        a *= clamp01(p * 3)
    elif inn in ("slide_l", "slide_r"):
        sign = -1 if inn == "slide_l" else 1
        dx += sign * (1 - ease_out_expo(p)) * 650
        rot += sign * (1 - ease_out_cubic(p)) * 14
        a *= clamp01(p * 2.5)
    elif inn == "drop":
        dy -= (1 - ease_out_back(p, 2.4)) * 220
        a *= clamp01(p * 3)
    elif inn == "rise":
        dy += (1 - ease_out_back(p, 2.0)) * 220
        a *= clamp01(p * 3)
    elif inn == "stamp":
        s *= 1 + 1.6 * (1 - ease_out_expo(p))
        rot += (1 - ease_out_expo(p)) * 18
        a *= clamp01(p * 3)
    elif inn == "spin":
        rot += (1 - ease_out_back(p)) * -200
        s *= max(0.0, ease_out_back(p))
        a *= clamp01(p * 3)
    elif inn == "squash":
        el = ease_out_elastic(p)
        sy *= max(0.0, el)
        sx *= 1 + 0.35 * (1 - ease_out_cubic(p))
        a *= clamp01(p * 3)
    # saída
    if q > 0:
        o = e["out"]
        qe = ease_in_cubic(q)
        if o == "pop":
            s *= 1 - qe
        elif o == "up":
            dy -= qe * 260
            a *= 1 - q
        elif o == "down":
            dy += qe * 260
            a *= 1 - q
        elif o in ("left", "right"):
            dx += (-1 if o == "left" else 1) * qe * 900
        a *= 1 - q * 0.6
    # movimento contínuo
    life = t - e["t0"]
    if e["idle"]:
        dy += e["idle"] * math.sin(life * 3.2 + e["phase"])
        rot += e["idle"] * 0.35 * math.sin(life * 2.1 + e["phase"] * 1.7)
    rot += e["spin"] * life
    if e["pulse"]:
        s *= 1 + e["pulse"] * math.sin(life * 2 * math.pi * 1.6)
    if e["path"]:
        px, py, pr, ps, pa = e["path"](t)
        dx += px
        dy += py
        rot += pr
        if isinstance(ps, tuple):
            sx *= ps[0]
            sy *= ps[1]
        else:
            s *= ps
        a *= pa
    return e["x"] + dx, e["y"] + dy, s * sx, s * sy, rot, clamp01(a)


def place(canvas, spr, cx, cy, sx, sy, rot, a):
    if sx <= 0.02 or sy <= 0.02 or a <= 0.01:
        return
    w, h = max(1, int(spr.width * sx)), max(1, int(spr.height * sy))
    im = spr if (w, h) == spr.size else spr.resize((w, h), Image.BICUBIC)
    if abs(rot) > 0.2:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    if a < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(round(cx - im.width / 2)), int(round(cy - im.height / 2))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0:
        return
    canvas.alpha_composite(im, (x0, y0), (x0 - x, y0 - y, x1 - x, y1 - y))


def sprite_for(e, t):
    if "sweep" in e:
        p = ease_in_out_cubic(clamp01((t - e["sweep"][0]) / (e["sweep"][1] - e["sweep"][0])))
        return get_sprite(("rainbow", 360, 20, int(round(p * 60))))
    if "roll" in e:
        st, dur = e["roll"]
        if t < st + dur:
            n = int((t - st) * 22)
            ch = "0123456789"[(n * 7 + int(e["x"])) % 10]
            return get_sprite(("text", ch, "L", e["roll_size"], e["roll_fill"]))
    return get_sprite(e["key"])


def camera(t):
    z, sx, sy = 1.0, 0.0, 0.0
    for tk, amp, shake in PUNCH:
        dt = t - tk
        if dt < 0 or dt > 1.2:
            continue
        env = dt / 0.05 if dt < 0.05 else math.exp(-(dt - 0.05) / 0.16)
        z += amp * env
        if shake:
            sx += shake * env * math.sin(dt * 70)
            sy += shake * env * math.cos(dt * 55)
    return z, sx, sy


def transition(canvas, t):
    for c in CUTS:
        if not (c - 0.32 < t < c + 0.45):
            continue
        d = ImageDraw.Draw(canvas)
        cols = [YELLOW, RED, BLUE, GREEN, ORANGE, CYAN, PINK]
        K = len(cols)
        bh = H / K
        skew = 260
        for i, col in enumerate(cols):
            p1 = ease_in_out_cubic(clamp01((t - (c - 0.3 + 0.012 * i)) / 0.25))
            p2 = ease_in_out_cubic(clamp01((t - (c + 0.05 + 0.014 * i)) / 0.28))
            lead = -skew - 60 + p1 * (W + 2 * skew + 120)
            trail = -skew - 60 + p2 * (W + 2 * skew + 120)
            if lead <= trail:
                continue
            y0, y1 = i * bh - 1, (i + 1) * bh + 1
            d.polygon([(trail + skew, y0), (lead + skew, y0), (lead, y1), (trail, y1)], fill=col + (255,))
            # faixa branca na borda de ataque
            if p1 < 1:
                d.polygon([(lead + skew, y0), (lead + skew + 22, y0), (lead + 22, y1), (lead, y1)],
                          fill=WHITE + (255,))


def render_frame(raw, t):
    frame = Image.frombytes("RGB", (W, H), raw)
    z, shx, shy = camera(t)
    if z > 1.001 or abs(shx) > 0.5 or abs(shy) > 0.5:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 - shx / z
        y0 = (H - ch) / 2 - shy / z
        frame = frame.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
    canvas = frame.convert("RGBA")
    transition(canvas, t)
    for e in ELEMS:
        st = elem_state(e, t)
        if st:
            place(canvas, sprite_for(e, t), *st)
    return canvas.convert("RGB").tobytes()


def render_chunk(args):
    src, i0, i1, out = args
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{i0 / FPS:.6f}", "-i", src,
                            "-frames:v", str(i1 - i0), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    n = W * H * 3
    i = i0
    while i < i1:
        raw = dec.stdout.read(n)
        if len(raw) < n:
            break
        enc.stdin.write(render_frame(raw, i / FPS))
        i += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                         "-show_entries", "stream=duration", "-of", "csv=p=0", src]))
    total = int(round(dur * FPS))
    tmp = tempfile.mkdtemp()
    nproc = max(1, multiprocessing.cpu_count())
    nch = nproc * 3
    bounds = [round(total * k / nch) for k in range(nch + 1)]
    jobs = [(src, bounds[k], bounds[k + 1], os.path.join(tmp, f"seg{k:03d}.mp4")) for k in range(nch)]
    with multiprocessing.Pool(nproc) as pool:
        for k, _ in enumerate(pool.imap(render_chunk, jobs)):
            print(f"\r{k + 1}/{nch} blocos", end="", flush=True)
    print()
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for j in jobs:
            f.write(f"file '{j[3]}'\n")
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                           "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy",
                           "-movflags", "+faststart", dst])


if __name__ == "__main__":
    main()
