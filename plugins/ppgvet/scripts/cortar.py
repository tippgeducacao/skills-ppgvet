#!/usr/bin/env python3
"""Tira os cortes da live a partir do cortes.json (minutagem HH:MM:SS,mmm do whisper; aceita também HH:MM:SS:FF do Premiere).
A minutagem pode errar até ~10 s, então o script ouve a janela em volta (whisper local) e acha
a primeira_frase e a ultima_frase de verdade; o corte sai com 3 s de folga em cada lado.
Uso: cortar.py <pasta-da-live>/cortes.json <tema>   ->  cortes/corte-<tema>-<titulo>.mp4
Usado também por aula.py (tc, slug, palavras, acha): não mudar a assinatura dessas funções."""
import glob, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import baixo, FF, FFPROBE, WHISPER, MODELO, acervo  # noqa: E402

JANELA, FOLGA = 20, 3  # s ouvidos além da minutagem; s deixados antes/depois da fala


def tc(s, fps=29.97):
    """aceita HH:MM:SS:FF (Premiere) ou HH:MM:SS,mmm / HH:MM:SS.mmm (whisper)"""
    if "," in s or "." in s:
        h, m, se = s.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(se)
    h, m, se, f = map(int, s.split(":"))
    return h * 3600 + m * 60 + se + f / fps


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def palavras(aula, ini, dur):
    """[(início, fim, palavra)] da janela, em segundos da aula"""
    d = tempfile.mkdtemp()
    baixo([FF(), "-v", "error", "-ss", f"{ini:.3f}", "-i", aula, "-t", f"{dur:.3f}", "-ar", "16000", "-ac", "1",
                    os.path.join(d, "a.wav")], check=True)
    baixo([WHISPER(), "-m", MODELO(), "-l", "pt", "-mc", "0", "-sns", "-ml", "1", "-sow", "-osrt", "-of", os.path.join(d, "a"), "-f", os.path.join(d, "a.wav")],
                   check=True, capture_output=True)
    out = []
    texto = open(os.path.join(d, "a.srt"), encoding="utf-8").read().strip()
    shutil.rmtree(d, ignore_errors=True)  # sem sobra no disco: roda dezenas de vezes por aula
    for b in re.split(r"\n\s*\n", texto):
        p = b.strip().splitlines()
        t = [int(x) for x in re.findall(r"\d+", p[1])]
        w = slug(" ".join(p[2:]))
        if w:
            out.append((ini + t[0] * 3600 + t[1] * 60 + t[2] + t[3] / 1000, ini + t[4] * 3600 + t[5] * 60 + t[6] + t[7] / 1000, w))
    return out


# formas faladas que o whisper escreve ora de um jeito, ora de outro ("pro" = "para o", "tá" = "está")
CANON = {"pra": "para", "pro": "para", "pros": "para", "ta": "esta", "to": "estou", "tava": "estava", "ce": "voce"}
canon = lambda w: CANON.get(w, w)


def acha(ws, frase, ultima=False):
    """índice da palavra onde a frase começa (ou termina, se ultima); None se não bater quase todas as palavras.
    Aceita até 2 palavras a mais entre as da frase (o whisper às vezes ouve "a", "e", "né" no meio)."""
    alvo = [canon(w) for w in slug(frase).split("-")]
    alvo = alvo[-5:] if ultima else alvo[:5]
    melhor, idx = (0, 0), None
    for i in range(len(ws)):
        for s in (0, 1):  # a frase pode começar pela 1ª ou pela 2ª palavra (o whisper às vezes perde ou troca a 1ª)
            if canon(ws[i][2]) != alvo[s]:
                continue
            n, j, ult = 0, i, i
            for a in alvo[s:]:
                for k in range(j, min(j + 3, len(ws))):
                    if canon(ws[k][2]) == a:
                        n, j, ult = n + 1, k + 1, k
                        break
            nota = (n, -(ult - i))  # mais palavras certas; empate: a mais compacta ("então? sim. então eu…" perde)
            if nota > melhor or (nota == melhor and ultima):  # empate total: 1ª ocorrência; última frase: a mais tardia
                melhor, idx = nota, ult if ultima else i
    return idx if melhor[0] >= max(len(alvo) - 1, 1) else None


def main(cortes_json, tema):
    base = os.path.dirname(os.path.abspath(cortes_json))
    aulas = glob.glob(os.path.join(base, "live-*.mp4")) or glob.glob(os.path.join(base, "aula-*.mp4"))
    assert len(aulas) == 1, f"esperava 1 live-*.mp4 em {base}, achei {len(aulas)}"
    os.makedirs(os.path.join(base, "cortes"), exist_ok=True)
    for c in json.load(open(cortes_json, encoding="utf-8")):
        a, b = tc(c["inicio"]), tc(c["fim"])
        assert b > a, f"minutagem invertida: {c['titulo']}"
        # "saida" e "folga" opcionais: a aula completa usa os dois
        saida = os.path.join(base, c["saida"]) if "saida" in c else os.path.join(base, "cortes", f"corte-{tema}-{slug(c['titulo'])}.mp4")
        folga = float(c.get("folga", FOLGA))
        if os.path.exists(saida):
            print("já existe, pulei:", os.path.basename(saida))
            continue
        # ouve só em volta de cada ponta (não transcreve o meio, que pode ter horas)
        w_ini = palavras(aulas[0], max(a - JANELA, 0), 2 * JANELA)
        w_fim = palavras(aulas[0], max(b - JANELA, 0), 2 * JANELA + 15)  # +15 s: a última palavra pode passar da minutagem
        i, f = acha(w_ini, c["primeira_frase"]), acha(w_fim, c["ultima_frase"], ultima=True)
        if i is None or f is None or w_fim[f][1] <= w_ini[i][0]:
            print(f"AVISO: não achei as frases de '{c['titulo']}', cortei pela minutagem com folga de {JANELA // 2} s")
            ini, fim = a - JANELA / 2, b + JANELA / 2
        else:
            ini, fim = w_ini[i][0] - folga, w_fim[f][1] + folga
        ini = max(ini, 0)
        d = fim - ini
        fade = f"afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03"
        if c.get("abertura"):  # aula completa: abertura PPGVET antes, como na aula curricular
            w, h = subprocess.run([FFPROBE(), "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                   "-of", "csv=p=0", aulas[0]], capture_output=True, text=True, check=True).stdout.strip().split(",")[:2]
            ent = ["-i", acervo("intro", f"{c['abertura']}.mov"), "-ss", f"{ini:.3f}", "-t", f"{d:.3f}", "-i", aulas[0]]
            fc = (f"[0:v]scale={w}:{h},fps=30,setsar=1,format=yuv420p[v0];[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];"
                  f"[1:v]fps=30,setsar=1,format=yuv420p[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo,{fade}[a1];"
                  "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
            cmd = [*ent, "-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
        else:
            cmd = ["-ss", f"{ini:.3f}", "-i", aulas[0], "-t", f"{d:.3f}", "-af", fade]
        baixo([FF(), "-v", "error", *cmd, "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida], check=True)
        print(f"ok: {os.path.basename(saida)} ({fim - ini:.0f} s; minutagem errou {ini + folga - a:+.1f} s no início)")


def teste():
    assert slug("95 por cento das amostras têm micotoxina") == "95-por-cento-das-amostras-tem-micotoxina"
    assert abs(tc("01:00:00:15") - 3600.5005) < 0.01 and tc("02:20:08,240") == 8408.24
    _ws = [(i, i + 1, w) for i, w in enumerate("ola entao gente pra gente concluir nos nao vou sair do intervalo fim".split())]
    assert acha(_ws, "Então gente pra gente concluir") == 1 and acha(_ws, "Vou sair do intervalo", ultima=True) == 11
    print("ok")


if __name__ == "__main__":
    teste() if sys.argv[1:] == ["--teste"] else main(sys.argv[1], sys.argv[2])
