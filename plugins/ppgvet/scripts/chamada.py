#!/usr/bin/env python3
"""Monta uma chamada a partir do roteiro.json: fala + legenda no peito + logo + transição para a arte (CTA) + música."""
import json, os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, acervo, caminho, dur, filtro_caminho, registrar_musica  # noqa: E402

W, H, FPS, TRANS = 1080, 1920, 30, 0.3
MUS_VOZ, MUS_ARTE = 0.063, 1.6  # música normalizada a -14 LUFS: -24 dB sob a voz (~22 dB abaixo dela), +4 dB na arte


def ass_tempo(s):
    cs = round(s * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def srt_to_ass(srt, ass, y_centro, inicio=0.0, fim_fala=1e9):
    """a legenda vem do bruto inteiro; o vídeo começa em `inicio`, então os tempos andam junto"""
    blocos = re.split(r"\n\s*\n", open(srt, encoding="utf-8").read().strip())
    linhas = []
    for b in blocos:
        p = b.strip().splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", p[1])
        assert m, f"tempo inválido na legenda: {p[1]}"
        t = [int(x) for x in m.groups()]
        a = t[0] * 3600 + t[1] * 60 + t[2] + t[3] / 1000
        z = t[4] * 3600 + t[5] * 60 + t[6] + t[7] / 1000
        if z <= inicio or a >= fim_fala:
            continue  # fala fora do trecho usado
        a, z = max(a, inicio) - inicio, min(z, fim_fala) - inicio
        linhas.append(f"Dialogue: 0,{ass_tempo(a)},{ass_tempo(z)},L,,0,0,0,,{{\\pos({W // 2},{y_centro})}}{' '.join(p[2:])}")
    open(ass, "w", encoding="utf-8").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Montserrat,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,0,3,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(linhas) + "\n")


def main(roteiro):
    r = json.load(open(roteiro, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(roteiro))
    p = lambda k, d=None: caminho(base, r.get(k, d))
    bruto, arte, musica, saida = p("bruto"), p("arte"), p("musica"), p("saida")
    legenda = p("legenda", "legenda.srt")
    md = r.get("marca_dagua", {})
    logo = caminho(base, md["arquivo"]) if "arquivo" in md else acervo("logos", "ppgvet", "logo-ppgvet.png")
    for f in (bruto, arte, musica, legenda, logo):
        assert os.path.exists(f), f"não encontrei: {f}"
    assert not os.path.exists(saida), f"saída já existe, use um nome -vN: {saida}"

    ini, fim = float(r.get("inicio", 0)), float(r["fim"])
    fala, dur_arte = fim - ini, float(r.get("arte_duracao", 6))
    total = fala + dur_arte - TRANS
    dur_musica = dur(musica)
    assert dur_musica >= total, f"música curta ({dur_musica:.0f} s para {total:.0f} s): escolha outra, nunca em loop"
    ass = os.path.join(tempfile.mkdtemp(), "legenda.ass")
    srt_to_ass(legenda, ass, int(r.get("legenda_y", 1100)), ini, fim)

    fc = (
        f"[0:v]trim={ini}:{fim},setpts=PTS-STARTPTS,fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v0];"
        f"[1:v]scale={md.get('largura', 270)}:-1[lg];"
        f"[v0][lg]overlay=(W-w)/2:{md.get('y', 1430)},ass='{filtro_caminho(ass)}':fontsdir='{filtro_caminho(acervo('fontes'))}',format=yuv420p[fala];"
        f"[2:v]fps={FPS},split[a1][a2];"
        f"[a1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,eq=brightness=-0.08[fundo];"
        f"[a2]scale={W}:-1[frente];"
        f"[fundo][frente]overlay=0:(H-h)/2,setsar=1,format=yuv420p[cta];"
        # transição: sobe a arte com borrão vertical (whip)
        f"[fala][cta]xfade=transition=slideup:duration={TRANS}:offset={fala - TRANS},"
        f"gblur=sigma=1:sigmaV=60:enable='between(t,{fala - TRANS - 0.05},{fala + 0.05})'[v];"
        f"[0:a:{max(int(r.get('audio', 1)) - 1, 0)}]atrim={ini}:{fim},asetpts=PTS-STARTPTS,"
        # voz e música normalizadas antes da mistura: os ganhos valem para qualquer gravação e faixa
        f"loudnorm=I=-16:LRA=11,aresample=48000,afade=t=in:d=0.03,"
        f"afade=t=out:st={fala - 0.03}:d=0.03,apad=whole_dur={total}[voz];"
        # música fixa e baixa sob a voz; sobe só na arte (CTA), em 0,8 s a partir da transição
        f"[3:a]atrim=0:{total},asetpts=PTS-STARTPTS,loudnorm=I=-14:LRA=11,aresample=48000,"
        f"volume='{MUS_VOZ}+({MUS_ARTE}-{MUS_VOZ})*clip((t-{fala - TRANS})/0.8,0,1)':eval=frame,"
        f"afade=t=in:d=0.5,afade=t=out:st={total - 1.5}:d=1.5[mb];"
        f"[voz][mb]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,alimiter=limit=0.6:level=disabled[a]"
    )
    cmd = [FF(), "-v", "error", "-nostats", "-i", bruto, "-i", logo,
           "-loop", "1", "-t", str(dur_arte), "-i", arte, "-i", musica,
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(total),
           "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    shutil.rmtree(os.path.dirname(ass), ignore_errors=True)

    origem = musica + ".origem.txt"
    link = open(origem, encoding="utf-8").read().strip() if os.path.exists(origem) else "(origem não registrada)"
    open(os.path.join(base, "creditos.txt"), "w", encoding="utf-8").write(f"Música: {os.path.basename(musica)} — {link}\n")
    registrar_musica(musica, saida)
    print("pronto:", saida)


if __name__ == "__main__":
    assert ass_tempo(3725.5) == "1:02:05.50" and ass_tempo(0) == "0:00:00.00"
    print("ok") if sys.argv[1:] == ["--teste"] else main(sys.argv[1])
