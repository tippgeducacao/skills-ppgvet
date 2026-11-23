#!/usr/bin/env python3
"""Monta um treinamento do PPGVET Academy a partir do treinamento.json: abertura PPGVET + trechos da gravação
(sem os erros) na moldura do Academy. Tela compartilhada do Meet: moldura PADRÃO (tela grande, câmera à direita).
Só câmera (Meet em tela cheia ou câmera do estúdio): câmera no bloco centralizado da moldura de câmera.
Uso: treinamento.py treinamento.json             mostra onde caem os cortes e monta
     treinamento.py treinamento.json --pontos    só mostra onde caem os cortes (para conferir antes)"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aula import ABERTURAS, expr, filtro_moldura, layout, no_video, pontos  # noqa: E402
from comum import FF, acervo, baixo, dur, pasta, versao_livre  # noqa: E402

MOLDURA_TELA = ("molduras-aula", "PADRÃO.png")  # o layout do Meet com tela já coincide com as caixas dela
MOLDURA_CAMERA = ("molduras", "moldura-aula-ppgvet-ppg-16x9.png")
BLOCO = (241, 134, 1438, 811)  # x, y, largura e altura do bloco azul da moldura de câmera (medido no PNG)


def complemento(intervalos, total):
    """o que sobra de [0, total] fora dos intervalos"""
    out, ini = [], 0.0
    for a, b in sorted(intervalos):
        if a > ini:
            out.append((ini, a))
        ini = max(ini, b)
    if total > ini:
        out.append((ini, total))
    return out


def main(arq_json, so_pontos=False):
    r = json.load(open(arq_json, encoding="utf-8"))
    raiz = pasta("treinamentos")
    bruto = r["bruto"] if os.path.isabs(r["bruto"]) else os.path.join(raiz, r["bruto"])
    assert r.get("fonte") in ("meet", "camera"), 'treinamento.json precisa de "fonte": "meet" ou "camera"'
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", r["nome"]), f"nome minúsculo-com-hífen: {r['nome']}"
    saida = versao_livre(os.path.join(raiz, "prontos", r["nome"] + ".mp4"))
    abertura, m_tela, m_cam = acervo(*ABERTURAS["PPGVET"]), acervo(*MOLDURA_TELA), acervo(*MOLDURA_CAMERA)
    for f in (bruto, abertura, m_tela, m_cam):
        assert os.path.exists(f), f"não encontrei: {f}"

    print("cortes:")
    cortes = pontos(bruto, r["trechos"])
    total = sum(b - a for a, b in cortes)
    print(f"treinamento: {total / 60:.0f} min em {len(cortes)} trecho(s) -> {saida}")
    tela = no_video(cortes, layout(bruto, dur(bruto))) if r["fonte"] == "meet" else []
    hms = lambda s: f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{s % 60:04.1f}"
    print("tela compartilhada (no vídeo montado):", ", ".join(f"{hms(a)}-{hms(b)}" for a, b in tela) or "nenhuma")
    if so_pontos:
        return

    ent, fc = ["-i", abertura], []
    for a, b in cortes:
        ent += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", bruto]
    n = len(cortes)
    ent += ["-i", m_tela, "-i", m_cam]
    for k in range(n):
        d = cortes[k][1] - cortes[k][0]
        fc.append(f"[{1 + k}:v]fps=30,scale=1920:1080,setsar=1[v{k}]")
        fc.append(f"[{1 + k}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[va][aa]")
    x, y, w, h = BLOCO
    fc.append(filtro_moldura(1 + n + 1, "mc"))
    cam = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},pad=1920:1080:{x}:{y},setsar=1"
    if tela:
        fc.append(filtro_moldura(1 + n, "mt"))
        fc.append(f"[va]split[vt][vc];[vt][mt]overlay=0:0[vtela];[vc]{cam}[vcp];[vcp][mc]overlay=0:0[vcam]")
        fc.append(f"[vtela][vcam]overlay=0:0:enable='{expr(complemento(tela, total))}',format=yuv420p[vtr]")
    else:
        fc.append(f"[va]{cam}[vcp];[vcp][mc]overlay=0:0,format=yuv420p[vtr]")
    fc.append("[aa]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[atr]")
    fc.append("[0:v]fps=30,scale=1920:1080,setsar=1,format=yuv420p[vi];[0:a]aresample=48000,aformat=channel_layouts=stereo[ai]")
    fc.append("[vi][ai][vtr][atr]concat=n=2:v=1:a=1[v][a]")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    parcial = saida[:-4] + ".parcial.mp4"
    # mesmo padrão da aula curricular: rápido, qualidade constante e teto de 2 Mbps
    baixo([FF(), "-v", "error", "-nostats", *ent, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "2000k", "-bufsize", "4000k",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", parcial], check=True)
    os.replace(parcial, saida)  # render que falha não deixa arquivo quebrado com o nome final
    print("pronto:", saida)


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        assert complemento([(5, 10), (20, 30)], 40) == [(0, 5), (10, 20), (30, 40)]
        assert complemento([], 12) == [(0, 12)] and complemento([(0, 12)], 12) == []
        assert complemento([(0, 5), (3, 8)], 10) == [(8, 10)]
        print("ok")
    else:
        main(sys.argv[1], "--pontos" in sys.argv)
