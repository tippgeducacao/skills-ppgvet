#!/usr/bin/env python3
"""Testes que barram a entrega (regras/nucleo.md, passo 3). Só mede o arquivo final; não muda nada.
uso: checar.py <video ou áudio> [--srt legenda.srt] [--lufs -16] [--car 25] [--instagram [--story]] [--rosto <y>] [--tol 1]
     checar.py --teste
Uma linha por teste (PASSA, AVISO ou FALHA); sai com código 1 se algum FALHA.
--lufs: alvo do volume da skill (padrão -16; chamada -14). --car: caracteres por linha da legenda
(padrão 25 no vertical, 42 no horizontal). --instagram: confere o formato de Reels (regras/formatos.md); com --story, o do story (3 a 60 s, 100 MB).
--tol: tolerância do volume (padrão 1,5; podcast 1, pedido da Apple).
--rosto <y>: o queixo nunca desce até o texto mais alto da peça (y em pixels; Reels do hf.py: 915, topo da legenda);
com --srt, só conta quando a legenda está na tela."""
import json, os, re, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, FFPROBE, baixo  # noqa: E402
from portao import registrar  # noqa: E402

TOL_LUFS, PICO_MAX, PICO_AVISO, CANAIS_DB, CPS = 1.5, -1.0, -1.5, 1.0, 17


def ffmpeg_log(video, filtro, audio=True):
    """roda um filtro de análise e devolve o log (stderr) do ffmpeg"""
    cmd = [FF(), "-hide_banner", "-nostats", "-i", video] + (["-af", filtro, "-vn"] if audio else ["-vf", filtro, "-an"])
    return baixo(cmd + ["-f", "null", "-"], capture_output=True, text=True).stderr


def ler_volume(log):
    """(LUFS integrado, pico real em dBTP) do resumo do filtro ebur128"""
    i = re.search(r"Integrated loudness:\s*I:\s*(-?[\d.]+|-inf)", log)
    p = re.search(r"True peak:\s*Peak:\s*(-?[\d.]+|-inf)", log)
    return float(i.group(1)), float(p.group(1))


def moov_antes(caminho):
    """faststart: o índice (moov) vem antes dos dados (mdat). Anda pelos blocos de topo do MP4."""
    with open(caminho, "rb") as f:
        while (cab := f.read(8)) and len(cab) == 8:
            tam, tipo = struct.unpack(">I4s", cab)
            if tipo in (b"moov", b"mdat"):
                return tipo == b"moov"
            if tam == 1:
                tam = struct.unpack(">Q", f.read(8))[0] - 8
            elif tam == 0:
                return False
            f.seek(tam - 8, 1)
    return False


def ler_srt(txt):
    """[(início, fim, [linhas])]"""
    blocos = []
    for b in re.split(r"\n\s*\n", txt.replace("\r", "").strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", b)
        if m:
            g = [int(x) for x in m.groups()]
            t = lambda h, mi, s, ms: h * 3600 + mi * 60 + s + ms / 1000
            linhas = [l.strip() for l in b[m.end():].strip().split("\n") if l.strip()]
            blocos.append((t(*g[:4]), t(*g[4:]), linhas))
    return blocos


def checar_legenda(blocos, car):
    """[(nivel, texto)] para linhas longas, mais de 2 linhas e leitura rápida demais"""
    achados = []
    limpa = lambda l: re.sub(r"<[^>]+>|\*", "", l)  # tags e *destaque* não contam
    for a, b, linhas in blocos:
        quando = f"{int(a // 60):02d}:{a % 60:05.2f}"
        if len(linhas) > 2:
            achados.append(("FALHA", f"legenda {quando}: {len(linhas)} linhas (máximo 2)"))
        for l in linhas:
            if len(limpa(l)) > car:
                achados.append(("FALHA", f"legenda {quando}: {len(limpa(l))} caracteres numa linha (máximo {car}): {limpa(l)!r}"))
        n = sum(len(limpa(l)) for l in linhas)
        if b > a and n / (b - a) > CPS and n > 12:
            achados.append(("AVISO", f"legenda {quando}: {n / (b - a):.0f} caracteres por segundo (confortável até {CPS})"))
    return achados


def queixo(faces, alt):
    """parte de baixo do maior rosto, em pixels da altura alt; None sem rosto.
    Rosto com menos de 10% da largura é plateia ao fundo (legenda por cima não incomoda) e não conta."""
    y = max(((w, y + h) for x, y, w, h in faces if w >= 0.10), default=(0, None))[1]
    return None if y is None else y * alt


def rosto_baixo(video, limite, alt):
    """tempos (a cada 1 s) em que o queixo passa do limite. YuNet a 540 de largura, como o retocar.py."""
    import cv2, numpy as np
    from retocar import MODELO_ROSTO
    w, h = 540, round(540 * alt / 1080)
    raw = baixo([FF(), "-v", "error", "-i", video, "-vf", f"fps=1,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                capture_output=True).stdout
    det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (w, h), 0.7)
    ruins = []
    for i in range(len(raw) // (w * h * 3)):
        q = np.frombuffer(raw, np.uint8, w * h * 3, i * w * h * 3).reshape(h, w, 3)
        _, f = det.detect(q)
        y = queixo([(a / w, b / h, c / w, d / h) for a, b, c, d in (f[:, :4] if f is not None else [])], alt)
        if y is not None and y > limite:
            ruins.append(i)
    return ruins


def checar_formato(v, a, fmt, arquivo, story=False):
    """formato de Reels ou de story pela API do Instagram (regras/formatos.md)"""
    r = []
    if (v["width"], v["height"]) != (1080, 1920):
        r.append(("FALHA", f"formato: {v['width']}x{v['height']} (Instagram vertical: 1080x1920)"))
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    fps = num / den
    if v.get("avg_frame_rate") not in (v["r_frame_rate"], None) or not 23 <= fps <= 60:
        r.append(("FALHA", f"fps: {v['r_frame_rate']} (média {v.get('avg_frame_rate')}); precisa ser fixo, de 23 a 60"))
    if v["codec_name"] != "h264" or (a and a["codec_name"] != "aac"):
        r.append(("FALHA", f"codec: {v['codec_name']} + {a and a['codec_name']} (H.264 + AAC)"))
    if a and int(a.get("sample_rate", 0)) > 48000:
        r.append(("FALHA", f"áudio a {a['sample_rate']} Hz (até 48 kHz)"))
    d, tam = float(fmt["duration"]), int(fmt["size"])
    dmax, mb = (60, 100) if story else (900, 300)
    if not 3 <= d <= dmax:
        r.append(("FALHA", f"duração {d:.1f} s (de 3 a {dmax} s)"))
    if tam > mb * 1e6:
        r.append(("FALHA", f"{tam / 1e6:.0f} MB (até {mb} MB)"))
    if int(v.get("bit_rate") or 0) > 25e6:
        r.append(("FALHA", f"vídeo a {int(v['bit_rate']) / 1e6:.1f} Mbps (até 25)"))
    if not moov_antes(arquivo):
        r.append(("FALHA", "sem faststart (refazer com -movflags +faststart)"))
    return r or [("PASSA", "formato Instagram")]


def checar(video, srt=None, lufs=-16.0, car=None, instagram=False, rosto=None, story=False, tol=TOL_LUFS):
    info = json.loads(subprocess.run([FFPROBE(), "-v", "error", "-show_streams", "-show_format", "-of", "json", video],
                                     capture_output=True, text=True, check=True).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"
              and not s.get("disposition", {}).get("attached_pic")), None)  # capa embutida no mp3 não é vídeo
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    r = []
    if v:
        cor = [v.get(k) for k in ("color_space", "color_primaries", "color_transfer")]
        r.append(("PASSA", "cor BT.709") if cor == ["bt709"] * 3 else ("FALHA", f"cor {cor} (etiquetar BT.709, video.md)"))
    if a:
        i, p = ler_volume(ffmpeg_log(video, "ebur128=peak=true"))
        r.append(("PASSA" if abs(i - lufs) <= tol else "FALHA", f"volume {i:.1f} LUFS (alvo {lufs:g} ±{tol:g})"))
        r.append(("FALHA" if p > PICO_MAX else "AVISO" if p > PICO_AVISO else "PASSA", f"pico {p:.1f} dBTP (até {PICO_AVISO})"))
        if int(a.get("channels", 1)) >= 2:
            med = [float(re.search(r"mean_volume: (-?[\d.]+|-inf)", ffmpeg_log(video, f"pan=mono|c0=c{c},volumedetect")).group(1))
                   for c in (0, 1)]
            dif = abs(med[0] - med[1])
            r.append(("FALHA" if dif > CANAIS_DB else "PASSA", f"canais {med[0]:.1f} e {med[1]:.1f} dB (diferença até {CANAIS_DB:g})"))
    else:
        r.append(("AVISO", "sem áudio"))
    if v is None:  # arquivo só de áudio: o resto confere imagem
        return r
    log = ffmpeg_log(video, "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=-60dB:d=2", audio=False)
    pretos = [float(x) for x in re.findall(r"black_start:(\d+\.?\d*)", log)]
    congelados = [float(x) for x in re.findall(r"freeze_start: (\d+\.?\d*)", log)]
    r.append(("FALHA", "primeiro quadro preto") if pretos and pretos[0] < 0.05 else ("PASSA", "primeiro quadro"))
    if [t for t in pretos if t >= 0.05]:
        r.append(("AVISO", f"tela preta em {', '.join(f'{t:.1f}s' for t in pretos if t >= 0.05)} (só se previsto: fade)"))
    if congelados:
        r.append(("AVISO", f"imagem parada ≥ 2 s em {', '.join(f'{t:.1f}s' for t in congelados)} (só se previsto: slide, foto)"))
    if srt:
        vertical = v["height"] > v["width"]
        achados = checar_legenda(ler_srt(open(srt, encoding="utf-8").read()), car or (25 if vertical else 42))
        r += achados or [("PASSA", "legenda")]
    if instagram:
        r += checar_formato(v, a, info["format"], video, story)
    if rosto:
        ruins = rosto_baixo(video, rosto, v["height"])
        if srt:  # com a legenda, só conta quando há texto na tela
            leg = ler_srt(open(srt, encoding="utf-8").read())
            ruins = [s for s in ruins if any(a - 0.5 <= s <= b + 0.5 for a, b, _ in leg)]
        r.append(("FALHA" if len(ruins) > 1 else "AVISO", f"rosto desce até a faixa dos textos (y {rosto}) em {', '.join(f'{t}s' for t in ruins[:8])}"
                  + (" …" if len(ruins) > 8 else "") + ": subir o enquadramento") if ruins else ("PASSA", f"rosto acima de y {rosto}"))
    return r


def teste():
    log = "Integrated loudness:\n    I:         -16.3 LUFS\n    Threshold: -26.4 LUFS\n\n  True peak:\n    Peak:       -1.8 dBFS"
    assert ler_volume(log) == (-16.3, -1.8)
    srt = "1\n00:00:01,000 --> 00:00:02,000\nisto é uma linha bem comprida demais para Reels\n\n" \
          "2\n00:00:03,000 --> 00:00:05,000\num\ndois\ntrês\n\n3\n00:00:06,000 --> 00:00:08,000\n*ok*\n"
    b = ler_srt(srt)
    assert [x[0] for x in b] == [1.0, 3.0, 6.0] and b[1][2] == ["um", "dois", "três"]
    ach = checar_legenda(b, 25)
    assert sum(1 for n, t in ach if n == "FALHA") == 2, ach            # linha longa e 3 linhas
    assert any(n == "AVISO" and "por segundo" in t for n, t in ach)   # 47 caracteres em 1 s
    assert checar_legenda(ler_srt("1\n00:00:00,000 --> 00:00:01,000\n*palavra*\n"), 25) == []
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        ftyp, moov, mdat = (struct.pack(">I4s", 16, n) + b"\0" * 8 for n in (b"ftyp", b"moov", b"mdat"))
        open(f"{d}/rapido.mp4", "wb").write(ftyp + moov + mdat)
        open(f"{d}/lento.mp4", "wb").write(ftyp + mdat + moov)
        assert moov_antes(f"{d}/rapido.mp4") and not moov_antes(f"{d}/lento.mp4")
        subprocess.run([FF(), "-v", "error", "-y", "-f", "lavfi", "-i", "sine=d=4", "-ac", "2", f"{d}/som.mp3"], check=True)
        so_audio = checar(f"{d}/som.mp3")
        assert any("volume" in t for _, t in so_audio) and not any("quadro" in t or "cor" in t for _, t in so_audio), so_audio
    v = {"width": 1080, "height": 1920, "r_frame_rate": "30/1", "avg_frame_rate": "30/1", "codec_name": "h264", "bit_rate": "8000000"}
    assert checar_formato(v, {"codec_name": "aac", "sample_rate": "48000"}, {"duration": "30", "size": "20000000"}, f"{__file__}")[0][0] == "FALHA"  # sem faststart
    ok = {"codec_name": "aac", "sample_rate": "48000"}
    assert any("de 3 a 60 s" in t for _, t in checar_formato(v, ok, {"duration": "70", "size": "1000"}, f"{__file__}", story=True))
    assert not any("duração" in t for _, t in checar_formato(v, ok, {"duration": "70", "size": "1000"}, f"{__file__}"))
    assert queixo([(0.4, 0.2, 0.2, 0.25)], 1920) == 0.45 * 1920 and queixo([], 1920) is None
    assert queixo([(0.4, 0.2, 0.2, 0.25), (0.1, 0.7, 0.12, 0.1)], 1920) == 0.45 * 1920 and queixo([(0, 0.8, 0.05, 0.06)], 1920) is None  # vale o maior; plateia ao fundo não conta
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
        sys.exit()
    if not a or not os.path.exists(a[0]):
        sys.exit(__doc__)
    op = lambda k, f=str: f(a[a.index(k) + 1]) if k in a else None
    res = checar(a[0], op("--srt"), op("--lufs", float) or -16.0, op("--car", int), "--instagram" in a, op("--rosto", int), "--story" in a, op("--tol", float) or TOL_LUFS)
    for nivel, texto in res:
        print(f"{nivel:5} {texto}")
    n = sum(nv == "FALHA" for nv, _ in res)
    registrar(a[0], not n, n)
    sys.exit(1 if n else 0)
