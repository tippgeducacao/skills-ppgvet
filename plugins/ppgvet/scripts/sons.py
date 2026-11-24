#!/usr/bin/env python3
"""Efeitos sonoros do acervo.
uso: sons.py gerar              gera os sons sintéticos (nossos, sem licença) em acervo/sons/<tipo>/
     sons.py pico <arquivo>     ms do pico do som (para o pico cair no quadro do gesto: regras/oficio/som.md)
     sons.py tratar <entrada> <saida.wav> [--estereo]   arquivo baixado (Kenney, Freesound) no padrão do acervo
     sons.py --teste
Padrão: WAV 48 kHz 16 bits, mono (estéreo nos que passam de um lado ao outro), sem silêncio no começo, pico até -1 dBFS
e volume médio (50 ms) até -12 dBFS, para todos soarem parecidos."""
import os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, acervo  # noqa: E402

SR = 48000
PICO = 10 ** (-1 / 20)  # -1 dBFS
VOLUME = 10 ** (-12 / 20)  # teto do volume médio (janela de 50 ms): som longo não fica mais alto que os curtos
rng = np.random.default_rng(7)  # semente fixa: o mesmo som toda vez


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def fase(freq):
    """fase de uma frequência que muda no tempo (soma acumulada)"""
    return 2 * np.pi * np.cumsum(freq) / SR


def ruido(n, cor=0.0):
    """ruído branco (cor 0) até rosado (cor ~0.98), por um filtro de um polo"""
    r = rng.standard_normal(n)
    if cor:
        out, y = np.empty(n), 0.0
        for i, x in enumerate(r):
            y = cor * y + (1 - cor) * x
            out[i] = y
        r = out
    return r


def passa_banda(x, centro, q=1.2):
    """filtro passa-banda com centro que muda no tempo (state variable filter)"""
    y, lp, bp = np.empty_like(x), 0.0, 0.0
    for i, s in enumerate(x):
        f = 2 * np.sin(np.pi * min(centro[i], SR / 6) / SR)
        hp = s - lp - bp / q
        bp += f * hp
        lp += f * bp
        y[i] = bp
    return y


def sino(dur, pico_em):
    """envelope em sino: sobe até pico_em (0..1 da duração) e desce"""
    u = np.linspace(0, 1, int(SR * dur))
    return np.where(u < pico_em, (u / pico_em) ** 2, ((1 - u) / (1 - pico_em)) ** 1.5)


def pan(x, de=-0.8, ate=0.8):
    p = (np.linspace(de, ate, len(x)) + 1) / 2
    return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], axis=1)


def sons():
    """nome: (tipo, sinal). Cada receita é uma linha de síntese simples; o resultado é medido em --teste."""
    s = {}
    t = t_(0.15); s["pop"] = ("interface", np.sin(fase(200 + 700 * np.exp(-50 * t))) * np.exp(-30 * t))
    nota = lambda f, d: (np.sin(fase(np.full_like(t_(d), f))) + 0.3 * np.sin(fase(np.full_like(t_(d), 2 * f)))) * np.exp(-14 * t_(d))
    s["notificacao"] = ("interface", np.concatenate([nota(880, 0.13), nota(1320, 0.45)]))
    t = t_(1.6)
    mod = np.sin(fase(np.full_like(t, 1320 * 1.4))) * 2.2 * np.exp(-4 * t)  # sino FM
    s["ding"] = ("interface", np.sin(fase(np.full_like(t, 1320)) + mod) * np.exp(-3 * t))
    brilho = np.zeros(int(SR * 0.9))
    for k, f in enumerate([2093, 2637, 3136, 4186, 5274, 6272]):  # arpejo agudo, de dó a sol
        a = int(SR * 0.06 * k); tt = t_(0.35)
        brilho[a:a + len(tt)] += np.sin(fase(np.full_like(tt, f))) * np.exp(-14 * tt) * (0.9 - 0.08 * k)
    s["brilho"] = ("interface", brilho)
    tique = np.zeros(int(SR * 1.0))
    for a, f in ((0, 3200), (0.5, 2400)):
        tt = t_(0.03); tique[int(SR * a):int(SR * a) + len(tt)] += passa_banda(ruido(len(tt)), np.full(len(tt), f), 4) * np.exp(-200 * tt)
    s["tique-taque"] = ("interface", tique)
    g = np.concatenate([np.sign(np.sin(fase(np.full_like(t_(d), f)))) * 0.6 if k % 2 else ruido(int(SR * d)) * 0.5
                        for k, (f, d) in enumerate([(0, .03), (180, .04), (0, .02), (520, .05), (0, .03), (90, .06)])])
    s["glitch"] = ("interface", np.round(g * 6) / 6)  # bit crush
    d = 0.35; n = int(SR * d)
    s["whoosh-curto"] = ("transicao", pan(passa_banda(ruido(n, .6), np.interp(np.linspace(0, 1, n), [0, .6, 1], [400, 3000, 800])) * sino(d, .6)))
    d = 0.28; n = int(SR * d)  # filtro estreito varrendo de 700 a 7000 Hz: o movimento é o que soa como swipe
    s["swipe"] = ("transicao", pan(passa_banda(ruido(n, .3), 700 * 10 ** np.linspace(0, 1, n), 4) * sino(d, .75), -.8, .8))
    d = 2; n = int(SR * d); u = np.linspace(0, 1, n)
    r = passa_banda(ruido(n, .5), 300 * (20 ** u), 1.5) + 0.25 * np.sin(fase(200 * (4 ** u)))
    s["riser"] = ("transicao", pan(r * u ** 2, -.3, .3))
    d = 1.2; n = int(SR * d); tt = t_(d)
    # cauda que fecha de 5000 a 400 Hz, tocada ao contrário: o som cresce e o filtro abre até o fim (sucção)
    s["reverse"] = ("transicao", pan((passa_banda(ruido(n, .7), 400 + 4600 * np.exp(-3 * tt), 1.4) * np.exp(-4 * tt))[::-1], .5, -.2))
    # camadas: sub (35-80 Hz) + corpo (110-70 Hz com harmônicos, o que o celular toca) + baque (ruído em 250 Hz) + estalo
    tt = t_(1.4)
    sub = np.sin(fase(35 + 45 * np.exp(-6 * tt))) * np.exp(-3.2 * tt) * .6
    corpo = np.tanh(3.5 * np.sin(fase(70 + 40 * np.exp(-12 * tt)))) * np.exp(-5 * tt) * 1.0
    boom = sub + corpo
    k = int(SR * .12); boom[:k] += passa_banda(ruido(k, .3), np.full(k, 250), .9) * np.exp(-30 * t_(.12)) * 2.0
    k = int(SR * .006); boom[:k] += passa_banda(ruido(k), np.full(k, 3000), .8) * .8
    s["impacto-grave"] = ("impacto", np.tanh(1.6 * boom))
    return s


def padrao(x):
    """sem silêncio no começo, fade de 5 ms no fim, pico até -1 dBFS e volume médio até -12 dBFS"""
    m = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    x = x[np.argmax(m > m.max() * 10 ** (-60 / 20)):]
    f = np.linspace(1, 0, int(SR * .005))
    x[-len(f):] = (x[-len(f):].T * f).T
    def vol(y):
        m = np.abs(y).max(axis=1) if y.ndim == 2 else np.abs(y)
        j = min(int(SR * .05), len(m))
        return m.max(), np.sqrt(np.convolve(m ** 2, np.ones(j) / j, "valid").max())
    pico, rms = vol(x)
    base = x = x * min(PICO / pico, VOLUME / max(rms, 1e-9))
    g = 1.0
    while vol(x)[1] < VOLUME / 2.5 and g < 4:  # curto demais (click): saturação suave até -20 dBFS ou +12 dB, sem estourar
        g *= 1.25
        y = np.tanh(g * base / PICO)  # sempre do som de antes, para não acumular distorção
        x = y * PICO / np.abs(y).max()
    return x


def salvar(x, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with wave.open(caminho, "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def ler(caminho, canais=1):
    """qualquer formato (wav, mp3, flac, ogg) pelo ffmpeg, em float 48 kHz"""
    raw = subprocess.run([FF(), "-v", "error", "-i", caminho, "-ac", str(canais), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, "<f4").astype(float)
    return x.reshape(-1, 2) if canais == 2 else x


def pico_ms(x):
    """ms do pico de energia (janela de 5 ms): onde o som "bate" """
    m = np.abs(x).max(axis=1) if x.ndim == 2 else np.abs(x)
    j = int(SR * .005)
    e = np.convolve(m ** 2, np.ones(j), "same")
    return round(1000 * int(np.argmax(e)) / SR)


def teste():
    for nome, (tipo, x) in sons().items():
        y = padrao(x.copy())
        assert np.abs(y).max() <= PICO + 1e-9, nome
        assert np.abs(y[:10]).max() > 1e-4, f"{nome}: silêncio no começo"
        assert np.isfinite(y).all() and len(y) > SR * .05, nome
    x = np.zeros(SR); x[SR // 2] = 1
    assert abs(pico_ms(x) - 500) <= 3
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a == ["gerar"]:
        for nome, (tipo, x) in sons().items():
            salvar(padrao(x), acervo("sons", tipo, f"{nome}.wav"))
            print(tipo, nome)
    elif a[:1] == ["pico"]:
        print(pico_ms(ler(a[1])))
    elif a[:1] == ["tratar"]:
        salvar(padrao(ler(a[1], 2 if "--estereo" in a else 1)), a[2])
        print(a[2])
    else:
        sys.exit(__doc__)
