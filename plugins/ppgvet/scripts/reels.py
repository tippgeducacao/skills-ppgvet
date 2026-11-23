#!/usr/bin/env python3
"""Monta um vídeo vertical de fala (Instagram) a partir do roteiro.json da pasta.
Etapas (cada uma reaproveita o que já existe em tmp/):
  base     corta os blocos de fala da fonte 4K deitada, gira, alterna zoom a cada corte -> tmp/base.mov
  legenda  transcreve a base (whisper local) -> legenda.srt (corrigir à mão e rodar de novo)
  (hf.py   gera o projeto HyperFrames com caixinha, cartões e legenda; render -> tmp/hf.mp4)
  final    fala com motion + vinheta + voz e música (sobe na vinheta) -> saída na pasta dos originais
uso: reels.py pasta/roteiro.json [base|legenda|final] [--previa]"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import baixo, FF, WHISPER, MODELO, caminho, dur, registrar_musica  # noqa: E402

W, H, FPS = 1080, 1920, "30000/1001"
VINHETAS = {"ppgvet": "acervo:logos-animadas/encerramento-ppgvet-vertical.mp4",
            "ppg": "acervo:logos-animadas/encerramento-ppg-vertical.mp4"}
PAD_A, PAD_D = 0.06, 0.10  # folga antes/depois de cada bloco de fala
ZOOM = 1.16
MIN_TROCA = 5.0  # s mínimos num mesmo plano antes de trocar o zoom


def run(cmd):
    baixo(cmd, check=True)


def trechos(r, com_quem=False):
    """Blocos de fala com folga, unidos quando quase encostam (e é a mesma pessoa).
    Bloco [ini, fim] ou [ini, fim, "quem"]. Devolve [(ini, fim), ...] (ou [(ini, fim, quem)]) no tempo da fonte."""
    out = []
    for bl in r["blocos"]:
        a, b, quem = bl[0] - PAD_A, bl[1] + PAD_D, (bl[2] if len(bl) > 2 else None)
        if out and a - out[-1][1] < 0.12 and out[-1][2] == quem:
            out[-1][1] = max(out[-1][1], b)
        else:
            if out and a < out[-1][1]:  # troca de pessoa colada: divide a folga, sem repetir áudio
                out[-1][1] = a = (a + out[-1][1]) / 2
            out.append([max(a, 0), b, quem])
    return out if com_quem else [(a, b) for a, b, _ in out]


def mapa(tr):
    """Converte tempo da fonte -> tempo do vídeo editado."""
    acum, m = 0.0, []
    for a, b in tr:
        m.append((a, b, acum)); acum += b - a

    def f(t):
        for a, b, o in m:
            if t < a: return o
            if t <= b: return o + t - a
        return acum
    return f, acum


def recorte(k, cx, cy, centrar):
    """Crop da fonte girada para o zoom k. centrar: rosto no centro (x) e a 30% do topo (y); senão mantém a posição relativa."""
    if k == 1.0: return ""
    if centrar:
        x = f"max(0,min(iw-iw/{k},iw*{cx}-iw/{k}/2))"; y = f"max(0,min(ih-ih/{k},ih*{cy}-ih/{k}*0.30))"
    else:
        x, y = f"(iw-iw/{k})*{cx}", f"(ih-ih/{k})*{cy}"
    return f"crop=w=iw/{k}:h=ih/{k}:x='{x}':y='{y}',"


def etapa_base(r, pasta, _tr):
    """Uma pessoa (`rosto`): alterna normal e zoom 1,16. Duas ou mais (`rostos` + quem fala em cada bloco):
    alterna aberto, fechado (1,8) e médio (1,35) em quem fala. Troca no máximo a cada MIN_TROCA s; o resto é jump cut."""
    os.makedirs(f"{pasta}/tmp/seg", exist_ok=True)
    tr = trechos(r, com_quem=True)
    rostos = r.get("rostos")
    planos = [(1.0, False), (1.8, True), (1.35, True)] if rostos else [(1.0, False), (ZOOM, False)]
    lista, z, desde, ult = [], 0, 0.0, None
    for i, (a, b, quem) in enumerate(tr):
        # troca de plano só a cada MIN_TROCA s (os outros cortes ficam como jump cut);
        # e quando o close está numa pessoa e outra começa a falar
        if i and ((rostos and quem != ult and planos[z][1]) or (desde >= MIN_TROCA and b - a >= 1.0)):
            z, desde = (z + 1) % len(planos), 0.0
        desde += b - a; ult = quem
        k, centrar = planos[z]
        cx, cy = rostos[quem] if rostos else r.get("rosto", [0.5, 0.33])
        seg = f"{pasta}/tmp/seg/{i:03d}-{z}-{quem or 'x'}.mov"
        lista.append(seg)
        if os.path.exists(seg): continue
        d = b - a
        run([FF(), "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", r["fonte"], "-t", f"{d:.3f}",
             "-vf", f"{r.get('girar', 'transpose=1')},{recorte(k, cx, cy, centrar)}scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,format=yuv420p",
             "-af", f"pan=stereo|c0={r.get('canal', 'c0')}|c1={r.get('canal', 'c0')},aresample=48000,afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03",
             "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "pcm_s16le", seg])
    with open(f"{pasta}/tmp/lista.txt", "w", encoding="utf-8") as fp:
        fp.writelines(f"file '{os.path.abspath(s).replace(os.sep, '/')}'\n" for s in lista)
    run([FF(), "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{pasta}/tmp/lista.txt", "-c", "copy", f"{pasta}/tmp/base.mov"])
    print("base:", f"{pasta}/tmp/base.mov", f"{dur(pasta + '/tmp/base.mov'):.1f}s")


def etapa_legenda(pasta):
    wav = f"{pasta}/tmp/base.wav"
    run([FF(), "-v", "error", "-y", "-i", f"{pasta}/tmp/base.mov", "-ar", "16000", "-ac", "1", wav])
    run([WHISPER(), "-m", MODELO(), "-l", "pt", "-ml", "16", "-sow", "-osrt", "-of", f"{pasta}/legenda-bruta", "-f", wav, "-np"])
    print("revise e salve como legenda.srt:", f"{pasta}/legenda-bruta.srt")


def etapa_final(r, pasta, tr, previa):
    """Fala com motion (render do HyperFrames em tmp/hf.mp4) + vinheta + voz e música."""
    _, total_fala = mapa(tr)
    base, hfv = f"{pasta}/tmp/base.mov", f"{pasta}/tmp/hf.mp4"
    assert os.path.exists(hfv), "falta tmp/hf.mp4: rode hf.py e o render do HyperFrames"
    vinheta = caminho(pasta, r.get("vinheta") or VINHETAS[r.get("marca", "ppgvet")])
    musica = caminho(pasta, r["musica"])
    X = 0.4  # transição fala -> vinheta
    total = total_fala + dur(vinheta) - X
    dm = dur(musica)
    assert dm >= total, f"música curta ({dm:.0f}s para {total:.0f}s): escolha outra, nunca em loop"
    # música medida (LUFS) e ajustada: fundo a -33 LUFS, 17 dB sob a voz (-16), para a fala ficar clara (pedido do usuário);
    # na vinheta, sem voz, sobe a -15,5 LUFS; vale para qualquer faixa
    lufs = float(re.search(r"Input Integrated:\s+(-?[\d.]+)", baixo(
        [FF(), "-hide_banner", "-t", f"{total:.1f}", "-i", musica, "-af", "loudnorm=print_format=summary", "-f", "null", "-"],
        capture_output=True, text=True).stderr).group(1))
    mv = r.get("musica_volume", round(10 ** ((-33 - lufs) / 20), 4))
    mf = r.get("musica_final", round(10 ** ((-15.5 - lufs) / 20), 4))
    t0 = total_fala - X
    fc = [
        f"[0:v]fps={FPS},settb=1001/30000,format=yuv420p[fala]",
        f"[1:v]fps={FPS},scale={W}:{H},setsar=1,format=yuv420p,settb=1001/30000[vin]",
        # "sobe": o final entra de baixo (rápido e freando) com borrão vertical, como nos posts da cortes-live; senão fade
        (f"[fala]tpad=stop_mode=clone:stop_duration={total - total_fala + 1:.3f}[fb];[vin]setpts=PTS-STARTPTS+{t0:.3f}/TB[vs];"
         f"[fb][vs]overlay=x=0:y='{H}*pow(1-clip((t-{t0:.3f})/{X},0,1),3)':eval=frame,"
         f"gblur=sigma=1:sigmaV=45:enable='between(t,{t0:.3f},{t0 + X * 0.7:.3f})',trim=duration={total:.3f}[v]")
        if r.get("transicao") == "sobe" else f"[fala][vin]xfade=transition=fade:duration={X}:offset={t0:.3f}[v]",
        f"[2:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,afade=t=out:st={total_fala - 0.15:.3f}:d=0.15,apad=whole_dur={total:.3f}[voz]",
        # música fixa sob a voz; sobe na vinheta (0,6 s) e sai com fade
        f"[3:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,"
        f"volume='{mv}+({mf}-{mv})*min(1,max(0,(t-{t0:.3f})/0.6))':eval=frame,"
        f"afade=t=in:d=0.8,afade=t=out:st={total - 1.8:.3f}:d=1.8[mus]",
        "[voz][mus]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.7:level=false[a]",
    ]
    destino = pasta if previa else caminho(pasta, r.get("pasta_saida", pasta))  # final vai para a pasta dos originais
    saida = os.path.join(destino, ("previa-" if previa else "") + r["saida"])
    assert previa or not os.path.exists(saida), f"saída já existe, use -vN: {saida}"
    venc = ["-c:v", "libx264", "-crf", "26" if previa else "17", "-preset", "veryfast" if previa else "slow"]
    run([FF(), "-v", "error", "-nostats", "-y", "-i", hfv, "-i", vinheta, "-i", base, "-i", musica,
         "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *venc,
         "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida])
    if not previa:
        registrar_musica(musica, saida)
    print("pronto:", saida, f"{total:.1f}s")


if __name__ == "__main__":
    rot = sys.argv[1]; etapa = sys.argv[2] if len(sys.argv) > 2 else "base"
    pasta = os.path.dirname(os.path.abspath(rot))
    r = json.load(open(rot, encoding="utf-8")); r["fonte"] = caminho(pasta, r["fonte"])
    tr = trechos(r)
    if etapa == "base": etapa_base(r, pasta, tr)
    elif etapa == "legenda": etapa_legenda(pasta)
    elif etapa == "final": etapa_final(r, pasta, tr, "--previa" in sys.argv)
