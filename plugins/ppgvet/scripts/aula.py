#!/usr/bin/env python3
"""Monta a aula curricular a partir do aula.json: abertura animada + trechos da gravação do Meet
(sem o começo, o intervalo e o silêncio do fim) com a moldura da pós e o card do professor.
Uso: aula.py aula.json             mostra onde caem os cortes e monta
     aula.py aula.json --pontos    só mostra onde caem os cortes (para conferir antes)"""
import json, os, re, shutil, subprocess, sys, tempfile
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cortar import acha, palavras, tc  # mesma busca de frase dos cortes de live
from card import card as fazer_card  # noqa: E402
from comum import FF, acervo, baixo, dur, nome_arquivo, pasta, versao_livre  # noqa: E402

ABERTURAS = {"PPGVET": ("intro", "PPGVET.mov")}
MOLDURA = {s: m for m, ss in {
    "BOVINOS": "RNGB NGB CMCB GPL", "AVES": "SA PC", "SUÍNOS": "PS", "PETFOOD": "CBEA CMMV",
    "QUALIDADE": "QSAOA SUZ", "PADRÃO": "GCC CRCV GPERA"}.items() for s in ss.split()}
CAM_X, CAM_W, CAM_Y = 1438, 482, 405       # caixa da câmera na moldura (igual ao layout do Meet)
CARD_W, CARD_BASE = 421, 373               # card: largura do desenho e onde ele termina (padrão do usuário)
JANELA = 25


def card_png(arq, tmp):
    """recorta a sobra transparente (os PNGs têm larguras diferentes) e põe na largura padrão"""
    im = Image.open(arq).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    im = im.resize((CARD_W, round(im.height * CARD_W / im.width)), Image.LANCZOS)
    out = os.path.join(tmp, "card.png")
    im.save(out)
    return out, im.height


PW, PH = 96, 54  # quadro reduzido para detectar o layout do Meet


def compartilhando_quadro(px):
    """layout de tela compartilhada: área acima da câmera preta e área do slide com conteúdo.
    Câmera em tela cheia acende a área de cima; avatar em fundo preto deixa a área do slide quase toda preta."""
    cima = [px[y * PW + x] for y in range(1, 19) for x in range(73, 95)]
    cam = [px[y * PW + x] for y in range(21, 33) for x in range(73, 95)]   # caixinha da câmera à direita
    slide = [px[y * PW + x] for y in range(7, 47) for x in range(0, 72)]
    acesa = lambda r, lim=40: sum(v > lim for v in r) / len(r)
    # slide cheio basta (a caixinha pode mostrar o avatar de quem fala); slide escuro precisa da caixinha da câmera:
    # o avatar de aluno nela é cinza-escuro (>15), já a tela preta de avatar em tela cheia deixa essa área em 0 (Felipe, 10/11)
    return sum(cima) / len(cima) < 25 and (acesa(slide) > 0.3 or (acesa(cam, 15) > 0.3 and acesa(slide) > 0.05))


def quadros(args, antes=""):
    """lê quadros cinza reduzidos do ffmpeg; devolve [(tempo, compartilhando)]"""
    p = subprocess.run([FF(), "-v", "info", *args, "-vf", f"{antes}scale={PW}:{PH},format=gray,showinfo", "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    tempos = [float(l.split("pts_time:")[1].split()[0]) for l in p.stderr.decode(errors="ignore").splitlines() if "pts_time:" in l]
    n = PW * PH
    return [(t, compartilhando_quadro(p.stdout[i * n:(i + 1) * n])) for i, t in enumerate(tempos[:len(p.stdout) // n])]


def layout(bruto, dur):
    """intervalos (início, fim) em que o professor compartilha a tela, no tempo do bruto"""
    q = quadros(["-skip_frame", "nokey", "-i", bruto, "-fps_mode", "passthrough"])  # um quadro a cada ~4 s
    trocas = []
    for (t0, s0), (t1, s1) in zip(q, q[1:]):
        if s0 != s1:  # acerta o instante da troca olhando 5 quadros por segundo entre os dois
            fino = quadros(["-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", bruto], antes="fps=5,")
            t = next((t0 + tt for tt, s in fino if s == s1), t1)
            trocas.append((t, s1))
    estado, ini, out = q[0][1], 0.0, []
    for t, s in trocas:
        if estado:
            out.append((ini, t))
        estado, ini = s, t
    if estado:
        out.append((ini, dur))
    # junta buracos curtos (menos de 3 s) para a moldura não piscar
    junto = []
    for a, b in out:
        if junto and a - junto[-1][1] < 3:
            junto[-1] = (junto[-1][0], b)
        elif b - a >= 3:
            junto.append((a, b))
    return junto


def pontos(bruto, trechos):
    """acerta cada trecho na primeira/última palavra de verdade (whisper local nas pontas)"""
    res = []
    for t in trechos:
        a, b = tc(t["inicio"]), tc(t["fim"])
        wi = palavras(bruto, max(a - JANELA, 0), 2 * JANELA)
        wf = palavras(bruto, max(b - JANELA, 0), 2 * JANELA + 15)
        i, f = acha(wi, t["primeira_frase"]), acha(wf, t["ultima_frase"], ultima=True)
        assert i is not None, f"não achei a primeira_frase perto de {t['inicio']}: {t['primeira_frase']}"
        assert f is not None, f"não achei a ultima_frase perto de {t['fim']}: {t['ultima_frase']}"
        ini, fim = max(wi[i][0] - 0.15, 0), wf[f][1] + 0.4
        assert fim > ini
        hms = lambda s: f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{s % 60:04.1f}"
        print(f"  de {hms(ini)}  «{' '.join(w[2] for w in wi[i:i + 8])}…»")
        print(f"  até {hms(fim)}  «…{' '.join(w[2] for w in wf[max(f - 7, 0):f + 1])}»"
              f"  | depois viria: «{' '.join(w[2] for w in wf[f + 1:f + 6])}»")
        res.append((ini, fim))
    return res


def professor(titulo, nome=None):
    """nome do professor: o do aula.json ou a última parte do título da tarefa, sem o "Prof."/"Profa." """
    nome = nome or titulo.split("|")[-1]
    return re.sub(r"^\s*prof(a|ª|essora|essor)?\.?\s+", "", nome.strip(), flags=re.I).strip()


def main(arq_json, so_pontos=False):
    r = json.load(open(arq_json, encoding="utf-8"))
    raiz = pasta("aulas")
    bruto = r["bruto"] if os.path.isabs(r["bruto"]) else os.path.join(raiz, r["bruto"])
    sigla = r["sigla"].upper()
    assert sigla in MOLDURA, f"sigla sem moldura: {sigla} (perguntar qual moldura usar)"
    moldura = acervo("molduras-aula", f"{MOLDURA[sigla]}.png")
    assert r.get("genero") in ("professor", "professora"), 'aula.json precisa de "genero": "professor" ou "professora"'
    tmp = tempfile.mkdtemp()
    card = os.path.join(tmp, "card-nome.png")  # gerado na hora; nada fica guardado
    fazer_card(professor(r["titulo"], r.get("professor")), r["genero"], card)
    abertura = acervo(*ABERTURAS[r["abertura"]]) if r.get("abertura") else None
    # Mac: o Finder mostra ":" como "/", então o arquivo fica com o título exato; Windows: troca o que não é aceito
    saida = versao_livre(os.path.join(raiz, "prontas", nome_arquivo(r["titulo"]) + ".mp4"))
    for f in [bruto, moldura, card] + ([abertura] if abertura else []):
        assert os.path.exists(f), f"não encontrei: {f}"

    print("cortes:")
    cortes = pontos(bruto, r["trechos"])
    print(f"aula: {sum(b - a for a, b in cortes) / 60:.0f} min em {len(cortes)} trecho(s) -> {saida}")
    compart = layout(bruto, dur(bruto))
    hms = lambda s: f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{s % 60:04.1f}"
    print("tela compartilhada (com moldura):", ", ".join(f"{hms(a)}-{hms(b)}" for a, b in compart) or "nenhuma")
    if so_pontos:
        ver = os.path.join(os.path.dirname(os.path.abspath(arq_json)), "card-conferir.png")
        shutil.copy(card, ver)
        print("card para conferir:", ver)
        return

    card, card_h = card_png(card, tmp)
    ent, fc, ab = [], [], 1 if abertura else 0
    if abertura:
        ent += ["-i", abertura]
    for a, b in cortes:
        ent += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", bruto]
    n = len(cortes)
    ent += ["-i", moldura, "-i", card]
    km, kc = ab + n, ab + n + 1
    for k in range(n):
        d = cortes[k][1] - cortes[k][0]
        fc.append(f"[{ab + k}:v]fps=30,setsar=1[v{k}]")
        fc.append(f"[{ab + k}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[va][aa]")
    # moldura e card só quando o professor compartilha a tela (câmera em tela cheia fica sem moldura)
    liga, o = [], 0.0
    for a, b in cortes:
        liga += [f"between(t,{o + max(x, a) - a:.2f},{o + min(y, b) - a:.2f})" for x, y in compart if y > a and x < b]
        o += b - a
    quando = f":enable='{'+'.join(liga)}'" if liga else ":enable=0"
    # recorta o azul só até y=960: as caixas vão até 944 e, abaixo, o azul da logo PPG (y 984-1022) sumia junto
    fc.append(f"[{km}:v]format=rgba,split[mc][mb];[mc]crop=1920:960:0:0,colorkey=0x0036FF:0.25:0.05[mt];"
              f"[mb]crop=1920:120:0:960[mbx];[mt][mbx]vstack[m]")
    fc.append(f"[va][m]overlay=0:0{quando}[vm];[vm][{kc}:v]overlay={CAM_X + (CAM_W - CARD_W) // 2}:{CARD_BASE - card_h}{quando},format=yuv420p[vaula]")
    fc.append("[aa]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aaula]")
    if abertura:
        fc.append("[0:v]fps=30,scale=1920:1080,setsar=1,format=yuv420p[vi];[0:a]aresample=48000,aformat=channel_layouts=stereo[ai]")
        fc.append("[vi][ai][vaula][aaula]concat=n=2:v=1:a=1[v][a]")
    else:
        fc.append("[vaula]null[v];[aaula]anull[a]")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    # rápido, qualidade constante e teto de 2 Mbps (o que o usuário usa no CapCut)
    baixo([FF(), "-v", "error", "-nostats", *ent, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "2000k", "-bufsize", "4000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", saida], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("pronto:", saida)
    print("título na Panda:", r["titulo"])


if __name__ == "__main__":
    assert MOLDURA["CBEA"] == "PETFOOD" and MOLDURA["SA"] == "AVES" and MOLDURA["GPERA"] == "PADRÃO"
    assert professor("03/11 | Extensão Rural - Parte II | Prof. Gabriela Tonial Knappmann Bittencourt") == "Gabriela Tonial Knappmann Bittencourt"
    assert professor("x | Profa. Ana Lima") == "Ana Lima" and professor("x | Prof Rui") == "Rui"
    assert professor("x | y", "Paola Martinello") == "Paola Martinello"
    print("ok") if sys.argv[1:] == ["--teste"] else main(sys.argv[1], "--pontos" in sys.argv)
