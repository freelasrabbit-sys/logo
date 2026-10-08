"""Trilha original de 10 s sincronizada com a animação (sintetizada com numpy).

Ré maior, 120 BPM a partir do impacto principal. Uso: python3 music.py [saida.wav]
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 10.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N)
R = np.zeros(N)
Lr = np.zeros(N)  # envio para reverb
Rr = np.zeros(N)


def hz(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


def add(sig, t0, gain=1.0, pan=0.0, rev=0.2):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0]
    gl = gain * np.cos((pan + 1) * np.pi / 4)
    gr = gain * np.sin((pan + 1) * np.pi / 4)
    L[i0:i0 + len(sig)] += sig * gl
    R[i0:i0 + len(sig)] += sig * gr
    Lr[i0:i0 + len(sig)] += sig * gl * rev
    Rr[i0:i0 + len(sig)] += sig * gr * rev


def tt(d):
    return np.arange(int(d * SR)) / SR


def spectral(noise, gain_fn, nfft=2048):
    """filtro variável no tempo via STFT. gain_fn(t, freqs) -> ganho."""
    hop = nfft // 4
    win = np.hanning(nfft)
    out = np.zeros(len(noise) + nfft)
    freqs = np.fft.rfftfreq(nfft, 1 / SR)
    for s in range(0, len(noise) - nfft, hop):
        X = np.fft.rfft(noise[s:s + nfft] * win)
        X *= gain_fn((s + nfft / 2) / SR, freqs)
        out[s:s + nfft] += np.fft.irfft(X) * win
    return out[: len(noise)] / 1.5


def lowpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X /= np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X, len(x))


# ------------------------------------------------------------- instrumentos
def pluck(f, d=1.2, bright=1.0):
    t = tt(d)
    s = np.zeros_like(t)
    for n in range(1, 14):
        if f * n > 16000:
            break
        s += np.sin(2 * np.pi * f * n * t + n) * (1 / n ** 1.4) * np.exp(-t * (2.5 + n * 1.6 / bright))
    att = np.minimum(1, t / 0.003)
    return s * att * 0.5


def bell(f, d=3.0):
    t = tt(d)
    idx = 2.2 * np.exp(-t * 3)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t))
    s += 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 2)
    return s * np.exp(-t * 1.6) * np.minimum(1, t / 0.002) * 0.35


def pad(freqs, d, att=0.8, rel=1.2):
    t = tt(d)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            for n in range(1, 9):
                s += np.sin(2 * np.pi * ff * n * t + ph * n) / n ** 1.8
    env = np.minimum(1, t / att) * np.minimum(1, (d - t) / rel)
    lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.7 * t)
    return s * env * lfo / (len(freqs) * 3) * 0.6


def kick(d=0.5, f0=140, f1=46, k=28):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * k)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 6)
    s += rng.normal(0, 1, len(t)) * np.exp(-t * 300) * 0.3
    return np.tanh(s * 1.6) * 0.8


def boom(d=3.0):
    t = tt(d)
    f = 30 + 70 * np.exp(-t * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    n = lowpass(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 5) * 0.8
    sn = highpass(rng.normal(0, 1, len(t)), 4000) * np.exp(-t * 3.0) * 0.25
    return np.tanh((s * 1.2 + n + sn) * 1.3) * 0.9


def hat(d=0.12, open_=False):
    t = tt(d)
    n = highpass(rng.normal(0, 1, len(t)), 7500)
    return n * np.exp(-t * (18 if open_ else 60)) * 0.22


def clap(d=0.4):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    n = highpass(lowpass(n, 4500), 900)
    env = np.zeros_like(t)
    for o in (0, 0.009, 0.018):
        env += np.where(t >= o, np.exp(-(t - o) * 90), 0)
    env += np.exp(-t * 12) * 0.5
    return n * env * 0.3


def riser(d, f0=300, f1=9000, q=0.5):
    n = rng.normal(0, 1, int(d * SR))

    def g(t, fr):
        x = t / d
        fc = f0 * (f1 / f0) ** (x ** 1.6)
        return np.exp(-(np.log2(np.maximum(fr, 1) / fc) / q) ** 2)

    s = spectral(n, g)
    env = (np.arange(len(n)) / len(n)) ** 2.2
    return s * env * 0.6


def whoosh(d, f0=200, f1=3500):
    n = rng.normal(0, 1, int(d * SR))

    def g(t, fr):
        x = t / d
        fc = f0 * (f1 / f0) ** np.sin(np.pi * x)
        return np.exp(-(np.log2(np.maximum(fr, 1) / fc) / 0.9) ** 2)

    s = spectral(n, g)
    x = np.arange(len(n)) / len(n)
    return s * np.sin(np.pi * x) ** 2 * 0.7


def sub(f, d):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05) * 0.5


# ------------------------------------------------------------- arranjo
B0 = 4.25          # impacto principal / entrada do groove
BEAT = 0.5

# intro: swell reverso -> impacto no flash
add(riser(0.4, 800, 12000, 0.7), 0.0, 0.5, rev=0.3)
add(boom(3.2), 0.30, 0.9, rev=0.5)
add(bell(hz("D6"), 3.0), 0.32, 0.25, 0.0, rev=0.8)

# anéis desenhando: brilho + arpejo cristalino
add(whoosh(1.4, 1500, 9000), 0.35, 0.25, -0.4, rev=0.6)
add(whoosh(1.2, 1200, 8000), 0.65, 0.22, 0.4, rev=0.6)
for k, n in enumerate(["D5", "F#5", "A5", "D6", "E6", "F#6", "A6"]):
    add(pluck(hz(n), 1.4, 1.6), 0.40 + k * 0.17, 0.22, -0.6 + k * 0.2, rev=0.7)

# pontos "pop"
add(pluck(hz("A5"), 0.8, 2.5), 1.45, 0.4, -0.7, rev=0.5)
add(pluck(hz("D6"), 0.8, 2.5), 1.55, 0.4, 0.7, rev=0.5)

# monograma: hit suave + pad abre
add(kick(0.8, 90, 40, 14), 1.60, 0.55, rev=0.4)
add(pad([hz(n) for n in ["D3", "A3", "E4", "F#4", "A4"]], 3.0, 0.5, 1.4), 1.60, 0.9, rev=0.5)
add(bell(hz("A5"), 3.0), 1.62, 0.18, 0.3, rev=0.9)

# brilho no emblema
for k, n in enumerate(["A5", "B5", "D6", "E6", "F#6"]):
    add(bell(hz(n), 1.5), 2.40 + k * 0.11, 0.1, -0.5 + k * 0.25, rev=0.9)

# transição: riser + whoosh do giro + reverso
add(riser(1.25, 250, 10000, 0.6), 3.0, 0.55, rev=0.4)
add(whoosh(1.1, 150, 2800), 3.2, 0.7, 0.0, rev=0.3)
rev_cym = highpass(rng.normal(0, 1, int(0.9 * SR)), 5000) * (np.linspace(0, 1, int(0.9 * SR)) ** 3)
add(rev_cym * 0.35, B0 - 0.9, 1.0, rev=0.3)

# impacto principal
add(boom(3.5), B0, 1.0, rev=0.6)
add(clap(), B0, 0.5, rev=0.6)

# groove 120 BPM
chords = [
    (["D3", "A3", "D4", "F#4", "A4"], "D2", ["D5", "F#5", "A5", "F#5"]),
    (["C#3", "A3", "C#4", "E4", "A4"], "A1", ["C#5", "E5", "A5", "E5"]),
    (["B2", "F#3", "B3", "D4", "F#4"], "B1", ["B4", "D5", "F#5", "D5"]),
    (["G2", "D3", "B3", "D4", "G4"], "G1", ["B4", "D5", "G5", "D5"]),
]
kick_times = []
for ci, (ch, bass, arp) in enumerate(chords):
    t0 = B0 + ci * 2 * BEAT
    add(pad([hz(n) for n in ch], 1.25, 0.05, 0.3), t0, 0.75, rev=0.5)
    for b in range(2):
        tb = t0 + b * BEAT
        kick_times.append(tb)
        add(kick(), tb, 0.85, rev=0.05)
        add(sub(hz(bass), BEAT * 0.95), tb, 0.55, rev=0.0)
        add(hat(open_=True), tb + BEAT / 2, 0.8, 0.3, rev=0.2)
        add(hat(), tb + BEAT / 4, 0.5, -0.3, rev=0.1)
        add(hat(), tb + 3 * BEAT / 4, 0.5, -0.3, rev=0.1)
        if b == 1:
            add(clap(), tb, 0.45, rev=0.5)
    for k in range(8):
        add(pluck(hz(arp[k % 4]), 0.6, 1.0), t0 + k * BEAT / 4, 0.17, (-0.5, 0.5)[k % 2], rev=0.45)

# letras ATHENA: ticks ascendentes
for i, n in enumerate(["D6", "E6", "F#6", "A6", "B6", "D7"]):
    add(pluck(hz(n), 0.5, 3.0), 4.30 + i * 0.075, 0.16, -0.6 + i * 0.24, rev=0.6)
add(whoosh(0.7, 2000, 9000), 4.85, 0.18, -0.3, rev=0.5)   # Colégio
add(whoosh(0.7, 2000, 9000), 5.15, 0.18, 0.3, rev=0.5)    # Ensino Bilíngue

# brilho final + sparkles
for k, n in enumerate(["F#5", "A5", "D6", "F#6", "A6"]):
    add(bell(hz(n), 2.0), 6.45 + k * 0.13, 0.11, -0.6 + k * 0.3, rev=0.9)
add(bell(hz("D6"), 3.0), 7.15, 0.2, 0.4, rev=0.9)
add(bell(hz("A6"), 3.0), 7.35, 0.16, -0.4, rev=0.9)

# resolução: acorde final longo
T_END = B0 + 8 * BEAT  # 8.25
add(kick(1.0, 120, 38, 18), T_END, 0.8, rev=0.3)
add(boom(2.0), T_END, 0.45, rev=0.7)
add(pad([hz(n) for n in ["D2", "D3", "A3", "E4", "F#4", "A4", "D5"]], DUR - T_END, 0.04, 1.4), T_END, 1.0, rev=0.6)
add(bell(hz("D6"), 2.5), T_END, 0.22, 0.0, rev=0.9)
add(bell(hz("F#6"), 2.5), T_END + 0.02, 0.14, 0.4, rev=0.9)

# ------------------------------------------------------------- sidechain + reverb + master
duck = np.ones(N)
for kt in kick_times + [B0, T_END]:
    i0 = int(kt * SR)
    n = min(N - i0, int(0.35 * SR))
    x = np.arange(n) / SR
    duck[i0:i0 + n] = np.minimum(duck[i0:i0 + n], 1 - 0.45 * np.exp(-x * 10))


def ir(seed, d=2.6):
    g = np.random.default_rng(seed)
    t = tt(d)
    x = g.normal(0, 1, len(t)) * np.exp(-t * 2.6)
    x = lowpass(x, 6000)
    x[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return x / np.sqrt(np.sum(x ** 2))


def conv(x, h):
    n = len(x) + len(h)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)
    return y[: len(x)]


wetL = conv(Lr, ir(11)) * 0.9
wetR = conv(Rr, ir(12)) * 0.9
outL = (L + wetL) * duck
outR = (R + wetR) * duck
# leve compressão/saturação
mx = max(np.abs(outL).max(), np.abs(outR).max())
outL, outR = outL / mx, outR / mx
outL, outR = np.tanh(outL * 1.6) / np.tanh(1.6), np.tanh(outR * 1.6) / np.tanh(1.6)
fade = np.ones(N)
fo = int(1.0 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 2
fade[:200] = np.linspace(0, 1, 200)
st = np.stack([outL * fade, outR * fade], 1) * 0.89  # ~ -1 dBFS

outp = sys.argv[1] if len(sys.argv) > 1 else "build/trilha.wav"
with wave.open(outp, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("ok", outp)
