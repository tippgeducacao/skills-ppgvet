#!/usr/bin/env python3
"""Aftermovie (resumo de evento): triagem do material bruto e montagem pelo roteiro. Regras: skills/aftermovie/SKILL.md.
uso: aftermovie.py triagem <pasta do bruto> [--saida <pasta>]  -> triagem.json + triagem.jpg (1 quadro por clipe, numerado)
     aftermovie.py montar <roteiro.json> [--previa]            -> vídeo na pasta_saida + resumo por bloco
     aftermovie.py --teste
Roteiro: {"formato": "9:16" ou "4:5", "marca": "ppgvet" ou "ppg", "musica": "musicas:faixa.mp3", "saida": "evento-tema-v1.mp4",
          "pasta_saida": "<pasta>", "clipes": [{"arquivo": "bruto/c012.mp4", "de": 3.2, "ate": 4.1, "bloco": "gancho",
          "x": 0.5, "fala": false}]}   x: centro do recorte na largura (0 a 1); fala: true no sound bite (o áudio do clipe entra)."""
import json, os, re, sys, tempfile
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")  # o YuNet avisa de backend a cada clipe; não muda nada
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import baixo, FF, caminho, dur, registrar_musica  # noqa: E402
from reels import VINHETAS, FPS  # noqa: E402

FORMATOS = {"9:16": (1080, 1920), "4:5": (1080, 1350)}
BLOCOS = ("gancho", "lugar", "pessoas", "detalhes", "momento", "fecho")
EXT = (".mp4", ".mov", ".m4v", ".mts")
MIN_PLANO, FALA_MAX = 0.25, 0.25  # plano mais curto pisca; fala acima de 25% vira vídeo de palestra (estudo de 25/11/2026)


def resumo(clipes):
    """total, plano médio por bloco, planos curtos demais e parte com fala"""
    ds = [c["ate"] - c["de"] for c in clipes]
    blocos = {}
    for c, d in zip(clipes, ds):
        blocos.setdefault(c.get("bloco", "?"), []).append(d)
    return {"total": sum(ds), "blocos": {b: (len(v), sum(v) / len(v)) for b, v in blocos.items()},
            "curtos": [i for i, d in enumerate(ds) if d < MIN_PLANO],
            "fala": sum(d for c, d in zip(clipes, ds) if c.get("fala")) / max(sum(ds), 1e-9)}


def inicio_musica(dm, total):
    """a música termina junto com o vídeo: corta de trás para frente"""
    return max(0.0, dm - total)


def volume_musica(base, baixa, janelas):
    """expressão do volume: a música desce sob cada sound bite (0,3 s antes) e volta em 0,5 s"""
    f = "0"
    for a, b in janelas:
        f = f"max({f},min(clip((t-{a:.3f}+0.3)/0.3,0,1),clip(({b:.3f}+0.5-t)/0.5,0,1)))"
    return f"{base}-({base}-{baixa})*{f}"


def lufs(arq, ini, total):
    log = baixo([FF(), "-hide_banner", "-ss", f"{ini:.3f}", "-t", f"{total:.3f}", "-i", arq, "-af", "loudnorm=print_format=summary",
                 "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"Input Integrated:\s+(-?[\d.]+)", log).group(1))


def montar(roteiro, previa=False):
    r = json.load(open(roteiro, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(roteiro))
    W, H = FORMATOS[r.get("formato", "9:16")]
    clipes, res = r["clipes"], resumo(r["clipes"])
    fim = r.get("fim", VINHETAS[r.get("marca", "ppgvet")])  # "fim": null tira o encerramento da marca
    fim = caminho(base, fim) if fim else None
    total = res["total"] + (dur(fim) if fim else 0)
    musica = caminho(base, r["musica"])
    dm = dur(musica)
    assert dm >= total, f"música curta ({dm:.0f}s para {total:.0f}s): escolha outra, nunca em loop"
    ini = inicio_musica(dm, total)
    m = lufs(musica, ini, total)
    alta, baixa = round(10 ** ((-16 - m) / 20), 4), round(10 ** ((-33 - m) / 20), 4)  # protagonista a -16; sob a fala, -33
    ins, fc, pares, t, janelas = [], [], [], 0.0, []
    for i, c in enumerate(clipes):
        d = c["ate"] - c["de"]
        ins += ["-ss", f"{c['de']:.3f}", "-t", f"{d:.3f}", "-i", caminho(base, c["arquivo"])]
        fc.append(f"[{i}:v]setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H}:(iw-{W})*{c.get('x', 0.5)}:(ih-{H})/2,fps={FPS},setsar=1,format=yuv420p[v{i}]")
        if c.get("fala"):
            fc.append(f"[{i}:a]asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,"
                      f"aformat=channel_layouts=stereo,apad=whole_dur={d:.3f},atrim=0:{d:.3f}[a{i}]")
            janelas.append((t, t + d))
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo:d={d:.3f}[a{i}]")
        pares.append(f"[v{i}][a{i}]")
        t += d
    n = len(clipes)
    if fim:
        ins += ["-i", fim]
        fc.append(f"[{n}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p[vf]")
        fc.append(f"anullsrc=r=48000:cl=stereo:d={dur(fim):.3f}[af]")  # o som da logo sai: a música fecha
        pares.append("[vf][af]")
    k = len(pares)
    ins += ["-ss", f"{ini:.3f}", "-t", f"{total:.3f}", "-i", musica]
    fc.append(f"{''.join(pares)}concat=n={k}:v=1:a=1[v][fala]")
    fc.append(f"[{k}:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
              f"volume='{volume_musica(alta, baixa, janelas)}':eval=frame,afade=t=in:d=0.5,afade=t=out:st={total - 1.8:.3f}:d=1.8[mus]")
    fc.append("[fala][mus]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.7:level=false[a]")
    destino = base if previa else caminho(base, r.get("pasta_saida", base))
    saida = os.path.join(destino, ("previa-" if previa else "") + r["saida"])
    assert previa or not os.path.exists(saida), f"saída já existe, use -vN: {saida}"
    venc = ["-c:v", "libx264", "-crf", "26" if previa else "17", "-preset", "veryfast" if previa else "slow"]
    baixo([FF(), "-v", "error", "-nostats", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
           "-t", f"{total:.3f}", *venc, "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida], check=True)
    if not previa:
        registrar_musica(musica, saida)
    print("pronto:", saida, f"{total:.1f}s")
    avisos(res)
    return saida


def avisos(res):
    for b, (q, med) in res["blocos"].items():
        print(f"bloco {b}: {q} planos, média {med:.2f}s")
    if res["curtos"]:
        print(f"FALHA: plano abaixo de {MIN_PLANO}s (pisca) nos clipes {res['curtos']}")
    if res["fala"] > FALA_MAX:
        print(f"AVISO: fala em {res['fala']:.0%} do tempo (até {FALA_MAX:.0%}; acima disso vira palestra)")
    if not (30 <= res["total"] <= 45 or 60 <= res["total"] <= 90):
        print(f"AVISO: {res['total']:.0f}s sem o encerramento, fora de 30 a 45 s e de 60 a 90 s")


def notas(video):
    """nitidez (Laplaciano no centro), luz (estourado e escuro), rosto (YuNet) e movimento em 5 quadros; som em dB"""
    import cv2, numpy as np
    from retocar import MODELO_ROSTO
    L = 480
    raw = baixo([FF(), "-v", "error", "-i", video, "-vf", f"fps=5/{max(dur(video), 0.2):.3f},"
                 f"scale={L}:{L}:force_original_aspect_ratio=decrease,pad={L}:{L}:(ow-iw)/2:(oh-ih)/2",
                 "-frames:v", "5", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    qs = [np.frombuffer(raw, np.uint8, L * L * 3, i * L * L * 3).reshape(L, L, 3) for i in range(len(raw) // (L * L * 3))]
    if not qs:
        return None
    det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (L, L), 0.7)
    cinza = [cv2.cvtColor(q, cv2.COLOR_BGR2GRAY)[L // 4:3 * L // 4, L // 4:3 * L // 4] for q in qs]
    som = re.search(r"mean_volume: (-?[\d.]+)", baixo([FF(), "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "volumedetect",
                                                        "-f", "null", "-"], capture_output=True, text=True).stderr)
    return {"dur": round(dur(video), 2), "nitidez": round(float(np.mean([cv2.Laplacian(g, cv2.CV_64F).var() for g in cinza]))),
            "estourado": round(float(np.mean([(g >= 250).mean() for g in cinza])), 3),
            "escuro": round(float(np.mean([(g <= 5).mean() for g in cinza])), 3),
            "rosto": round(sum(det.detect(q)[1] is not None for q in qs) / len(qs), 2),
            "movimento": round(float(np.mean([np.abs(a.astype(int) - b).mean() for a, b in zip(cinza, cinza[1:])] or [0])), 1),
            "som_db": float(som.group(1)) if som else None, "_meio": qs[len(qs) // 2]}


def triagem(pasta_bruto, saida=None):
    import cv2, numpy as np
    saida = saida or pasta_bruto
    arqs = sorted(f for f in os.listdir(pasta_bruto) if f.lower().endswith(EXT) and not f.startswith("."))
    lista, quadros = [], []
    for i, f in enumerate(arqs, 1):
        n = notas(os.path.join(pasta_bruto, f))
        if not n:
            print(f"AVISO: {f} não abriu")
            continue
        q = cv2.resize(n.pop("_meio"), (320, 320))
        cv2.putText(q, f"#{i}", (8, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
        quadros.append(q)
        lista.append({"n": i, "arquivo": os.path.join(pasta_bruto, f), **n})
    json.dump(lista, open(os.path.join(saida, "triagem.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    col = 6
    quadros += [np.zeros_like(quadros[0])] * (-len(quadros) % col)
    folha = np.vstack([np.hstack(quadros[j:j + col]) for j in range(0, len(quadros), col)])
    cv2.imwrite(os.path.join(saida, "triagem.jpg"), folha, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(f"{len(lista)} clipes: {os.path.join(saida, 'triagem.json')} e triagem.jpg")
    return lista


def teste():
    cl = [{"de": 0, "ate": 0.6, "bloco": "gancho"}, {"de": 2, "ate": 2.1, "bloco": "gancho"}, {"de": 0, "ate": 4, "bloco": "momento", "fala": True}]
    r = resumo(cl)
    assert abs(r["total"] - 4.7) < 1e-9 and r["curtos"] == [1] and abs(r["fala"] - 4 / 4.7) < 1e-9 and r["blocos"]["gancho"][0] == 2
    assert inicio_musica(100, 40) == 60 and inicio_musica(30, 40) == 0
    assert volume_musica(1, 0.1, []) == "1-(1-0.1)*0"
    with tempfile.TemporaryDirectory() as d:  # ponta a ponta: 3 clipes sintéticos, um com fala, sem encerramento
        for i, (tam, freq) in enumerate((("1920x1080", 440), ("1080x1920", 660), ("1280x720", 880))):
            baixo([FF(), "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={tam}:d=2:r=30", "-f", "lavfi", "-i",
                   f"sine=f={freq}:d=2", "-shortest", "-pix_fmt", "yuv420p", f"{d}/c{i}.mp4"], check=True)
        baixo([FF(), "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=20", f"{d}/musica.wav"], check=True)
        assert len(triagem(d)) == 3 and os.path.exists(f"{d}/triagem.jpg")
        json.dump({"formato": "4:5", "musica": "musica.wav", "saida": "t.mp4", "fim": None,
                   "clipes": [{"arquivo": "c0.mp4", "de": 0, "ate": 1, "bloco": "gancho"},
                              {"arquivo": "c1.mp4", "de": 0.5, "ate": 1.5, "bloco": "pessoas", "x": 0.3},
                              {"arquivo": "c2.mp4", "de": 0, "ate": 2, "bloco": "momento", "fala": True}]}, open(f"{d}/r.json", "w"))
        s = montar(f"{d}/r.json", previa=True)
        assert abs(dur(s) - 4) < 0.15, dur(s)
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif len(a) >= 2 and a[0] == "triagem":
        triagem(a[1], a[a.index("--saida") + 1] if "--saida" in a else None)
    elif len(a) >= 2 and a[0] == "montar":
        montar(a[1], "--previa" in a)
    else:
        sys.exit(__doc__)
