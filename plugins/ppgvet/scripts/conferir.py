#!/usr/bin/env python3
"""Pré-confere uma aula editada. uso: conferir.py <video.mp4> <pasta-saida>
      conferir.py --lote <destino.jpg> <SIGLA> <videos...>   (intro e moldura de todas, com a referência da pós em cima)
      conferir.py --salvar-ref <SIGLA> <aula aprovada.mp4>   |   conferir.py --teste
Gera na pasta: aula.srt, leitura.txt, achados.txt (tela preta, congelada, silêncio, volume, repetição,
fala de regravação, trocas de cena com o que estava sendo dito) e folhas de quadros (inicio.jpg, fim.jpg, cenas-N.jpg)."""
import difflib, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, MAC, WHISPER, MODELO, acervo, baixo, dur, pasta  # noqa: E402
REGRAVA = re.compile(r"\b(corta|cortar|de novo|errei|desculp\w*|gravando|grava[cç][aã]o|recome[cç]\w*|esquece|"
                     r"deixa eu (come[cç]ar|refazer|falar de novo)|pera[ií]|perd[ií] (a linha|o fio)|pode tirar)\b", re.I)

INVENTA = re.compile(r"^\s*(legenda[s]? (por|de)\b.*|ahn, né, é\.?)\s*$", re.I)
OBRIGADO = re.compile(r"^\s*obrigad[oa]\.?\s*$", re.I)  # o whisper inventa no silêncio, mas também é despedida real


def inventado(seg, silencios):
    """texto que o whisper inventa: "Legenda por…" sempre; "Obrigado." só se cair dentro de um silêncio"""
    a, b, t = seg
    meio = (a + b) / 2
    return bool(INVENTA.match(t)) or (bool(OBRIGADO.match(t)) and any(s <= meio <= e for s, e in silencios))


def hms(s):
    s = int(s)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stderr


def ler_srt(txt):
    segs = []
    for b in re.split(r"\n\s*\n", txt.strip()):
        ln = b.splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ln[1]) if len(ln) > 2 else None
        if m:
            g = list(map(int, m.groups()))
            segs.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000,
                         " ".join(ln[2:]).strip()))
    return segs


def palavras(t):
    return re.findall(r"\w+", t.lower())


def repeticoes(segs):
    """Frase dita duas vezes seguidas (regravação que ficou) ou trecho de 2+ palavras repetido colado."""
    out = []
    for i, (a, _, t) in enumerate(segs):
        w = palavras(t)
        for j in (i + 1, i + 2):
            if j < len(segs) and len(w) >= 4:
                w2 = palavras(segs[j][2])
                if difflib.SequenceMatcher(None, w, w2).ratio() >= 0.7:
                    out.append((a, f"frase repetida: «{t}» / «{segs[j][2]}»"))
        m = re.search(r"\b((?:\w+\s+)+\w+)\s+\1\b", " ".join(w))
        if m:
            out.append((a, f"trecho repetido: «{m.group(1)}» em «{t}»"))
    return out


def cortes(t, s):
    """Corte de edição = pico isolado de diferença entre quadros. Pico com outro a menos de 1 s é animação (intro, fim)."""
    pk = [i for i in range(5, len(s) - 5) if s[i] > 0.006 and s[i] > 5 * max(s[i - 5:i] + s[i + 1:i + 6])]
    return [t[i] for i in pk if not any(j != i and abs(t[j] - t[i]) < 1 for j in pk)]


def voz(a, t):
    """dB nos 50 ms antes e depois do corte."""
    def db(x):
        return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9) if len(x) else -99
    i = int(t * 16000)
    return db(a[max(0, i - 800):i]), db(a[i:i + 800])


def tipo_corte(antes, depois, lim=-35):
    if antes > lim and depois > lim:
        return "voz dos dois lados: corte no meio da fala?"
    if depois > lim:
        return "voz começa colada no corte: começo da palavra comido?"
    if antes > lim:
        return "voz termina colada no corte: fim da palavra comido?"
    return None


def ouvir(wav, t, pasta):
    """Transcreve 3 s antes e 3 s depois do corte, separados, para ver se a palavra saiu inteira."""
    lados = []
    for ini in (max(0, t - 3), t):
        tmp = os.path.join(pasta, "_ouvir.wav")
        run([FF(), "-v", "error", "-y", "-ss", f"{ini:.2f}", "-t", f"{min(3, t) if ini < t else 3:.2f}", "-i", wav,
             "-af", "apad=pad_dur=0.5", tmp])
        out = subprocess.run([WHISPER(), "-m", MODELO(), "-l", "pt", "-nt", "-np", "-f", tmp],
                             capture_output=True, text=True).stdout
        os.remove(tmp)
        lados.append(" ".join(out.split()) or "(nada)")
    return " | ".join(lados)


def folha(video, tempos, destino, colunas=4):
    if not tempos:
        return
    qs = []
    for t in tempos:
        p = subprocess.run([FF(), "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=480:-2",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
        im = Image.open(__import__("io").BytesIO(p)).convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 86, 22], fill="black")
        d.text((5, 3), hms(t), fill="yellow", font=ImageFont.load_default())
        qs.append(im)
    w, h = qs[0].size
    linhas = -(-len(qs) // colunas)
    g = Image.new("RGB", (w * colunas, h * linhas), "white")
    for k, im in enumerate(qs):
        g.paste(im, (k % colunas * w, k // colunas * h))
    if destino:
        g.save(destino, quality=85)
    return g


REFS_PACOTE = acervo("aulas-referencia")  # as que quem cuida do pacote publicou: valem para todos


def refs_local():
    return os.path.join(pasta("conferir"), "referencias")  # as aprovadas por esta pessoa (o pacote é só leitura)


def ref_de(sigla):
    """a referência da pessoa vale primeiro; senão, a do pacote"""
    return next((r for r in (os.path.join(d, f"{sigla.upper()}.jpg") for d in (refs_local(), REFS_PACOTE)) if os.path.exists(r)), None)


def linha(video):
    """Intro (0-10 s a cada 2 s) + um quadro do meio (moldura), numa linha só."""
    im = folha(video, [0, 2, 4, 6, 8, 10, dur(video) / 2], None, colunas=7)
    ImageDraw.Draw(im).text((5, im.height - 14), os.path.basename(video), fill="red", font=ImageFont.load_default())
    return im


def lote(destino, sigla, videos):
    """Uma linha por vídeo, com a referência aprovada da pós em cima (se houver)."""
    ref = ref_de(sigla)
    ims = ([Image.open(ref)] if ref else []) + [linha(v) for v in videos]
    g = Image.new("RGB", (ims[0].width, sum(i.height for i in ims)), "white")
    y = 0
    for im in ims:
        g.paste(im, (0, y))
        y += im.height
    g.save(destino, quality=85)
    print(destino, f"com referência ({ref})" if ref else f"SEM referência de {sigla.upper()}: comparar as aulas entre si")


def salvar_ref(sigla, video):
    os.makedirs(refs_local(), exist_ok=True)
    destino = os.path.join(refs_local(), f"{sigla.upper()}.jpg")
    linha(video).save(destino, quality=90)
    print(destino)


def main(video, pasta):
    os.makedirs(pasta, exist_ok=True)
    wav, base = os.path.join(pasta, "aula.wav"), os.path.join(pasta, "aula")
    d_video = dur(video)
    run([FF(), "-v", "error", "-y", "-i", video, "-vn", "-ar", "16000", "-ac", "1", wav])
    if not os.path.exists(base + ".srt"):
        baixo([WHISPER(), "-m", MODELO(), "-l", "pt", "-t", str(min(8, os.cpu_count() or 4)), "-mc", "0", "-sns",
                        "--prompt", "Éé, ahn, né, é.", "-osrt", "-of", base, "-f", wav], capture_output=True, check=True)
    alog = run([FF(), "-hide_banner", "-i", wav, "-af", "silencedetect=n=-40dB:d=2.5", "-f", "null", "-"])
    silencios = re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", alog)
    sil = [(float(a), float(b)) for a, b in silencios]
    # o whisper inventa texto no silêncio do fim ("Legenda por…") e repete o prompt
    segs = [s for s in ler_srt(open(base + ".srt", encoding="utf-8").read()) if not inventado(s, sil)]
    open(os.path.join(pasta, "leitura.txt"), "w", encoding="utf-8").write("".join(f"{hms(a)} {t}\n" for a, _, t in segs))

    # vídeo: uma passada em 480p (tela preta, imagem congelada, diferença entre todos os quadros)
    cenas_txt = "quadros.txt"  # relativo (cwd=pasta): caminho com "C:" quebraria o filtro no Windows
    log = baixo([FF(), "-hide_banner", *(["-hwaccel", "videotoolbox"] if MAC else []), "-i", os.path.abspath(video), "-an", "-vf",
               # troca de slide com a câmera ao lado dá 0,05 a 0,3; professor parado na câmera pequena "congela" até ~7s
               "scale=480:-2,blackdetect=d=0.3:pix_th=0.10,freezedetect=n=-60dB:d=8,"
               f"select='gte(scene,0)',metadata=print:file={cenas_txt}", "-f", "null", "-"],
               cwd=pasta, capture_output=True, text=True, check=True).stderr
    cenas_txt = os.path.join(pasta, cenas_txt)
    pretas = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)
    congela = re.findall(r"freeze_start: ([\d.]+)[\s\S]*?freeze_end: ([\d.]+)", log)
    q = open(cenas_txt).read()
    os.remove(cenas_txt)
    qt = list(map(float, re.findall(r"pts_time:([\d.]+)", q)))
    qs = list(map(float, re.findall(r"scene_score=([\d.]+)", q)))
    cenas = []
    for t, s in zip(qt, qs):
        if s > 0.05 and (not cenas or t - cenas[-1] > 1.5):
            cenas.append(t)
    w = wave.open(wav)
    amostras = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    suspeitos = []
    for t in cortes(qt, qs):
        tipo = tipo_corte(*voz(amostras, t))
        if tipo:
            suspeitos.append(f"{hms(t)} ({t:.1f}s) {tipo}{' [troca de cena]' if any(abs(t - c) < 0.5 for c in cenas) else ''}"
                             f"\n    ouvido: {ouvir(wav, t, pasta)}")
    # áudio: volume (o silêncio já saiu lá em cima)
    elog = run([FF(), "-hide_banner", "-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", elog)[-1]
    pico = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", elog)[-1]

    def dito(t):
        return next((s[2] for s in segs if s[0] - 0.5 <= t <= s[1] + 0.5), "(sem fala)")

    r = [f"# {os.path.basename(video)}  duração {hms(d_video)}  volume {lufs} LUFS  pico {pico} dBFS", ""]
    r += ["## tela preta"] + [f"{hms(float(a))}-{hms(float(b))}" for a, b in pretas] + [""]
    r += ["## imagem congelada (8s+)"] + [f"{hms(float(a))}-{hms(float(b))}" for a, b in congela] + [""]
    r += ["## silêncio (2,5s+)"] + [f"{hms(float(a))}-{hms(float(b))} ({float(b) - float(a):.0f}s)" for a, b in silencios] + [""]
    r += ["## cortes com voz encostada"] + suspeitos + [""]
    r += ["## repetição"] + [f"{hms(a)} {x}" for a, x in repeticoes(segs)] + [""]
    r += ["## fala de regravação"] + [f"{hms(a)} {t}" for a, _, t in segs if REGRAVA.search(t)] + [""]
    r += ["## primeira e última fala"] + [f"{hms(s[0])} {s[2]}" for s in segs[:2] + segs[-2:]] + [""]
    r += ["## trocas de cena (o que estava sendo dito)"] + [f"{hms(t)} {dito(t)}" for t in cenas]
    open(os.path.join(pasta, "achados.txt"), "w", encoding="utf-8").write("\n".join(r) + "\n")

    folha(video, [t for t in range(0, min(30, int(d_video)), 2)], os.path.join(pasta, "inicio.jpg"))
    folha(video, [t for t in range(max(0, int(d_video) - 24), int(d_video) - 1, 2)], os.path.join(pasta, "fim.jpg"))
    meio = [t + 0.7 for t in cenas if 30 < t < d_video - 24]
    for k in range(0, len(meio), 16):
        folha(video, meio[k:k + 16], os.path.join(pasta, f"cenas-{k // 16 + 1}.jpg"))
    os.remove(wav)
    print(f"{os.path.join(pasta, 'achados.txt')}  ({len(segs)} falas, {len(cenas)} trocas de cena)")


def teste():
    srt = "1\n00:00:01,000 --> 00:00:03,500\nentão a gente vai falar de bem-estar\n\n" \
          "2\n00:00:04,000 --> 00:00:06,000\nentão a gente vai falar de bem-estar animal\n\n" \
          "3\n00:01:00,000 --> 00:01:02,000\na seleção a seleção a seleção de pessoas\n"
    s = ler_srt(srt)
    assert [round(x[0], 1) for x in s] == [1.0, 4.0, 60.0], s
    achou = repeticoes(s)
    assert any("frase repetida" in x for _, x in achou) and any("trecho repetido" in x for _, x in achou), achou
    assert REGRAVA.search("pera, deixa eu começar de novo") and not REGRAVA.search("a cooperativa cresceu")
    assert hms(3725) == "01:02:05"
    t = [i / 30 for i in range(300)]
    s = [0.0002] * 300
    s[100] = 0.03                                    # corte isolado
    for i in range(200, 230, 6):
        s[i] = 0.1                                   # animação: picos seguidos
    assert cortes(t, s) == [t[100]], cortes(t, s)
    assert tipo_corte(-20, -22).startswith("voz dos dois") and tipo_corte(-70, -20).startswith("voz começa")
    assert tipo_corte(-70, -80) is None
    assert INVENTA.match("Legenda por Sônia Ruberti") and INVENTA.match("Ahn, né, é.") and not INVENTA.match("Obrigado, pessoal, até a próxima")
    sil = [(700.0, 720.0)]
    assert inventado((710, 711, "Obrigado."), sil)            # no silêncio do fim: inventado
    assert not inventado((690, 691, "Obrigado."), sil)        # com voz: despedida real, fica
    assert inventado((690, 691, "Legenda por Sônia"), sil)
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a[0] == "--lote":       # --lote <destino.jpg> <SIGLA> <videos...>
        lote(a[1], a[2], a[3:])
    elif a[0] == "--salvar-ref":  # --salvar-ref <SIGLA> <aula aprovada>
        salvar_ref(a[1], a[2])
    else:
        main(a[0], a[1])
