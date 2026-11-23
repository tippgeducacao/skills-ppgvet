#!/usr/bin/env python3
"""Monta o post vertical de um corte de aula a partir do post-*.json.
Uso: post.py <post.json>              monta o vídeo
     post.py <post.json> --legenda    só transcreve o corte inteiro e mostra o .srt (para achar inicio/fim e correções)"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import baixo, FF, WHISPER, MODELO, acervo, caminho, dur, filtro_caminho, registrar_musica  # noqa: E402

BOLD = acervo("fontes", "montserrat-bold.ttf")
VAR = acervo("fontes", "montserrat-variavel.ttf")  # tem a Regular
LOGO = acervo("logos", "ppgvet", "logo-ppgvet.png")
FIM = acervo("logos-animadas", "encerramento-ppgvet-vertical.mp4")
W, H, FPS = 1080, 1920, 30
CAM = (42, 831, 996)  # x, y e largura da câmera do professor no post


def lufs(f, dur):
    """volume só do trecho usado (muita faixa começa baixa e cresce)"""
    out = baixo([FF(), "-nostats", "-t", f"{dur:.3f}", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def cartao(titulo, pos, saida):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    # avatar: aro em degradê (laranja -> rosa -> roxo) com o logo dentro
    cx, cy, r, aro = 202, 296, 95, 9
    grad = Image.new("RGB", (2 * r, 2 * r))
    stops = [(0, (250, 126, 30)), (0.5, (214, 41, 118)), (1, (154, 46, 186))]
    for y in range(2 * r):
        for x in range(2 * r):
            t = min(max((x + (2 * r - y)) / (4 * r), 0), 1)  # de baixo-esquerda para cima-direita
            (a, ca), (b, cb) = (stops[0], stops[1]) if t < 0.5 else (stops[1], stops[2])
            k = (t - a) / (b - a)
            grad.putpixel((x, y), tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3)))
    m = Image.new("L", (8 * r, 8 * r))
    ImageDraw.Draw(m).ellipse((0, 0, 8 * r - 1, 8 * r - 1), fill=255)
    ImageDraw.Draw(m).ellipse((4 * aro, 4 * aro, 8 * r - 1 - 4 * aro, 8 * r - 1 - 4 * aro), fill=0)  # furo no centro (borda igual)
    im.paste(grad, (cx - r, cy - r), m.resize((2 * r, 2 * r), Image.LANCZOS))
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((142, round(logo.height * 142 / logo.width)), Image.LANCZOS)
    im.paste(logo, (cx - 71, cy - logo.height // 2), logo)

    reg = lambda s: (f := ImageFont.truetype(VAR, s), f.set_variation_by_name("Regular"), f)[2]
    nome = ImageFont.truetype(BOLD, 46)
    d.text((366, 196), "PPGVET - Educação", font=nome, fill="black")
    bx = 366 + d.textlength("PPGVET - Educação", font=nome) + 40
    d.ellipse((bx - 22, 202, bx + 22, 246), fill="#3897f0")  # selo de verificado
    d.line([(bx - 10, 224), (bx - 3, 232), (bx + 11, 216)], fill="white", width=5, joint="curve")
    d.text((366, 258), "@ppgvet_oficial", font=reg(30), fill="#282828")
    for i, l in enumerate(pos):
        d.text((366, 316 + 37 * i), l, font=reg(30), fill="#282828")
    tit = ImageFont.truetype(BOLD, 80)
    for i, l in enumerate(titulo):
        d.text((W / 2, 501 + 81 * i), l, font=tit, fill="#965594", anchor="ma")
    im.save(saida)


def srt(arq):
    for b in re.split(r"\n\s*\n", open(arq, encoding="utf-8").read().strip()):
        p = b.strip().splitlines()
        t = [int(x) for x in re.findall(r"\d+", p[1])]
        yield t[0] * 3600 + t[1] * 60 + t[2] + t[3] / 1000, t[4] * 3600 + t[5] * 60 + t[6] + t[7] / 1000, " ".join(p[2:])


def ass_tempo(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{s % 60:05.2f}"


def legenda_ass(srt_arq, ini, fim, correcoes, saida):
    linhas = []
    for a, b, txt in srt(srt_arq):
        if b <= ini or a >= fim:
            continue
        txt = re.sub(r"[.,!?;:…\"]", "", txt.lower()).strip()  # estilo dos posts: minúsculo, sem pontuação
        for k, v in correcoes.items():
            txt = re.sub(rf"\b{re.escape(k.lower())}\b", v, txt)
        if txt:
            linhas.append(f"Dialogue: 0,{ass_tempo(max(a, ini) - ini)},{ass_tempo(min(b, fim) - ini)},L,,0,0,0,,{txt}")
    open(saida, "w", encoding="utf-8").write(f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: L,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H40000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,2,2,90,90,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(linhas) + "\n")
    return len(linhas)


def soco(a):
    """zoom rápido + volta (transição de entrada/saída do apoio) no instante a"""
    return (f"+between(it,{a - 0.18:.3f},{a:.3f})*1.8*pow((it-{a - 0.18:.3f})/0.18,2)"
            f"+between(it,{a:.3f},{a + 0.35:.3f})*0.8*pow(1-(it-{a:.3f})/0.35,3)")


def trechos_camera(cameras, fala):
    """[(de, ate, [x, y, w, h])]: cada trecho vai do seu "de" até o "de" do próximo (o último, até o fim da fala)"""
    cs = sorted(cameras, key=lambda c: float(c["de"]))
    assert cs and float(cs[0]["de"]) == 0, 'o primeiro trecho de "cameras" começa em 0'
    out = []
    for i, c in enumerate(cs):
        de = float(c["de"])
        ate = float(cs[i + 1]["de"]) if i + 1 < len(cs) else fala
        assert 0 <= de < ate <= fala + 1e-6, f"trecho de câmera fora do corte: {c}"
        out.append((de, ate, [int(v) for v in c["recorte"]]))
    return out


def filtro_cameras(trechos, cw):
    """um trecho por área (professor, slide, quem pergunta), cada um encaixado na caixa cw x cw com fundo
    borrado dele mesmo, emendados em corte seco. shortcut: sem transição entre trechos; pôr xfade se pedirem"""
    n = len(trechos)
    fc = [f"[1:v]fps={FPS},split={n}" + "".join(f"[v{i}]" for i in range(n))]
    for i, (de, ate, (x, y, w, h)) in enumerate(trechos):
        fc.append(f"[v{i}]trim=start={de:.3f}:end={ate:.3f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},split[f{i}][b{i}];"
                  f"[b{i}]scale={cw}:{cw}:force_original_aspect_ratio=increase,crop={cw}:{cw},gblur=sigma=30,"
                  f"eq=brightness=-0.08[g{i}];[f{i}]scale={cw}:{cw}:force_original_aspect_ratio=decrease:flags=lanczos[p{i}];"
                  f"[g{i}][p{i}]overlay=(W-w)/2:(H-h)/2,setsar=1[s{i}]")
    fc.append("".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[q]")
    return fc


def main(post_json, so_legenda=False):
    r = json.load(open(post_json, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(post_json))
    p = lambda f: caminho(base, f)
    corte = p(r["corte"])
    tmp = os.path.join(base, ".tmp-post", os.path.splitext(os.path.basename(post_json))[0])
    os.makedirs(tmp, exist_ok=True)

    srt_arq = os.path.join(tmp, "legenda.srt")
    if not os.path.exists(srt_arq):  # transcrição local do corte inteiro, guardada para não refazer
        wav = os.path.join(tmp, "fala.wav")
        baixo([FF(), "-v", "error", "-y", "-i", corte, "-ar", "16000", "-ac", "1", wav], check=True)
        baixo([WHISPER(), "-m", MODELO(), "-l", "pt", "-ml", "26", "-sow", "-osrt",
                        "-of", srt_arq[:-4], "-f", wav], check=True, capture_output=True)
    if so_legenda:
        print(srt_arq)
        return

    musica, saida = p(r["musica"]), p(r["saida"])
    enc = p(r["encerramento"]) if "encerramento" in r else FIM  # arte de CTA (imagem) ou vídeo no lugar da vinheta
    enc_img = enc.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    for f in (corte, musica, enc, LOGO):
        assert os.path.exists(f), f"não encontrei: {f}"
    assert not os.path.exists(saida), f"saída já existe, use um nome -vN: {saida}"
    assert len(r["titulo"]) <= 3 and len(r["pos"]) <= 2, "título até 3 linhas, pós até 2"

    ini, fim = float(r["inicio"]), float(r["fim"])
    fala, d_fim = fim - ini, (5.0 if enc_img else dur(enc))
    total = fala + d_fim
    assert dur(musica) >= total, "música mais curta que o vídeo: escolha outra (nunca em loop)"
    png, ass = os.path.join(tmp, "cartao.png"), os.path.join(tmp, "legenda.ass")
    cartao(r["titulo"], r["pos"], png)
    assert legenda_ass(srt_arq, ini, fim, r.get("correcoes", {}), ass), "legenda vazia: confira inicio/fim"

    cx, cy, cw = CAM
    ent = ["-loop", "1", "-framerate", str(FPS), "-t", f"{fala:.3f}", "-i", png,
           "-ss", f"{ini:.3f}", "-t", f"{fala:.3f}", "-i", corte]
    if "cameras" in r:  # professor em foco; slide e quem pergunta entram em trechos, como apoio
        fc = filtro_cameras(trechos_camera(r["cameras"], fala), cw)
    else:
        x, y, w, h = r["recorte"]
        fc = [f"[1:v]fps={FPS},crop={w}:{h}:{x}:{y},scale={cw}:-2:flags=lanczos,setsar=1[q]"]
    fc.append(f"[0:v][q]overlay={cx}:{cy}:shortest=1,format=yuv420p[c0]")
    zoom, borrao = "1", ""
    for i, a in enumerate(r.get("apoio", [])):
        de, ate, arq = float(a["de"]), float(a["ate"]), p(a["arquivo"])
        assert os.path.exists(arq) and 0 <= de < ate <= fala, f"apoio inválido: {a}"
        imagem = arq.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ent += (["-loop", "1", "-framerate", str(FPS)] if imagem else []) + ["-t", f"{ate - de:.3f}", "-i", arq]
        k = 2 + i
        fc += [f"[{k}:v]scale={2 * W}:{2 * H}:force_original_aspect_ratio=increase,crop={2 * W}:{2 * H},"
               f"zoompan=z='1+0.08*on/({ate - de:.2f}*{FPS})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
               f"setpts=PTS-STARTPTS+{de}/TB,format=yuv420p[ap{i}]",
               f"[c{i}][ap{i}]overlay=0:0:enable='between(t,{de},{ate})':eof_action=pass[c{i + 1}]"]
        zoom += soco(de) + soco(ate)
        borrao += "".join(f",gblur=sigma=2:sigmaV=40:enable='between(t,{t - 0.108:.3f},{t + 0.175:.3f})'" for t in (de, ate))
    ult = f"c{len(r.get('apoio', []))}"
    if borrao:
        fc.append(f"[{ult}]zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}{borrao}[z]")
        ult = "z"
    k_fim, k_mus = len(r.get("apoio", [])) + 2, len(r.get("apoio", [])) + 3
    SOBE = 0.45  # arte entra subindo por cima dos últimos SOBE s da fala
    ent += (["-loop", "1", "-framerate", str(FPS), "-t", f"{d_fim + SOBE:.3f}"] if enc_img else []) + ["-i", enc, "-i", musica]
    bt709 = "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv"
    # imagem: inteira no centro, com ela mesma desfocada preenchendo o 9:16; vídeo: preenche cortando
    caber = (f"split[e1][e2];[e1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40[eb];"
             f"[e2]scale={W}:{H}:force_original_aspect_ratio=decrease[ef];[eb][ef]overlay=(W-w)/2:(H-h)/2,") if enc_img \
        else f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
    fc += [f"[{ult}]ass='{filtro_caminho(ass)}':fontsdir='{filtro_caminho(acervo('fontes'))}',{bt709},settb=1/{FPS}[falav]",
           f"[{k_fim}:v]fps={FPS},{caber}format=yuv420p,{bt709},setsar=1,settb=1/{FPS}[logo]",
           # encerramento sobe de baixo (rápido e freando) com borrão vertical no movimento; vídeo segura o último quadro no fim
           f"[falav]tpad=stop_mode=clone:stop_duration={d_fim:.3f}[base];[logo]setpts=PTS-STARTPTS+{fala - SOBE:.3f}/TB[lg];"
           f"[base][lg]overlay=x=0:y='{H}*pow(1-clip((t-{fala - SOBE:.3f})/{SOBE},0,1),3)':eval=frame,"
           f"gblur=sigma=1:sigmaV=45:enable='between(t,{fala - SOBE:.3f},{fala - SOBE * 0.3:.3f})',trim=duration={total:.3f}[v]",
           f"[1:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.05,"
           f"afade=t=out:st={fala - 0.12:.3f}:d=0.12,apad=whole_dur={total:.3f}[voz]",
           # música baixinha o vídeo todo (~-35 LUFS sob a voz em -16, qualquer faixa) e +10 dB suave só na logo final
           f"[{k_mus}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={total:.3f},volume={-35 - lufs(musica, total):.1f}dB,"
           f"afade=t=in:d=0.5,afade=t=out:st={total - 1.5:.3f}:d=1.5,volume='1+2.16*clip((t-{fala:.3f})/0.6,0,1)':eval=frame[mus]",
           "[voz][mus]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.84:level=0[a]"]
    baixo([FF(), "-v", "error", "-nostats", *ent, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida], check=True)
    registrar_musica(musica, saida)
    print("pronto:", saida)


def teste():
    t = trechos_camera([{"de": 20, "recorte": [60, 115, 872, 490]}, {"de": 0, "recorte": [952, 192, 264, 264]},
                        {"de": 31.5, "recorte": [952, 192, 264, 264]}], 50)
    assert [(a, b) for a, b, _ in t] == [(0, 20), (20, 31.5), (31.5, 50)], t
    assert "concat=n=3" in ";".join(filtro_cameras(t, 996))
    for ruim in ([{"de": 5, "recorte": [0, 0, 1, 1]}], [{"de": 0, "recorte": [0, 0, 1, 1]}, {"de": 60, "recorte": [0, 0, 1, 1]}]):
        try:
            trechos_camera(ruim, 50)
            raise SystemExit(f"devia recusar: {ruim}")
        except AssertionError:
            pass
    print("ok")


if __name__ == "__main__":
    teste() if sys.argv[1:] == ["--teste"] else main(sys.argv[1], "--legenda" in sys.argv)
