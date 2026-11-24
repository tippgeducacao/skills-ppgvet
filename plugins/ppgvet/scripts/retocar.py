#!/usr/bin/env python3
"""Retoque de foto como um fotógrafo: o Claude mede e olha a foto, escolhe os ajustes, e este script aplica.
uso: retocar.py analisar <foto>                          luz, cor, contraste, nitidez e rostos (para escolher os ajustes)
     retocar.py aplicar <foto> <saida> '<ajustes json>'   aplica (arquivo .json ou o texto do json)
     retocar.py --teste
Ajustes (todos opcionais; 0 ou ausente = não mexe):
  auto_branco true      balanço de branco automático (suave)
  temperatura -100..100 negativo esfria, positivo esquenta     matiz -100..100  negativo verde, positivo magenta
  exposicao  -2..2 (EV)                                        contraste -100..100
  realces    -100..100  negativo recupera céu e parede estourados
  sombras    -100..100  positivo abre sombra (rosto escuro, contraluz)
  clareza    0..100     contraste local (textura, campo)       vibracao -100..100  satura protegendo a pele
  saturacao  -100..100                                         pele 0..100  suaviza pele só nos rostos
  ruido      0..100     tira granulado (foto de celular à noite) nitidez 0..100
  girar      graus      endireita (positivo = anti-horário)    recorte "3:4" "4:5" "1:1" "16:9" "9:16"  (enquadra pelo rosto)
  largura    px         largura final"""
import json, os, sys
from pathlib import Path
import numpy as np
os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")  # aviso interno do OpenCV, não é erro
import cv2  # noqa: E402
try:  # foto HEIC do iPhone abre como qualquer outra (pillow-heif, no essencial do kit)
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass
from PIL import Image, ImageOps

MODELO_ROSTO = Path(__file__).resolve().parents[1] / "modelos" / "face_detection_yunet_2023mar.onnx"


def abrir(arq):
    im = ImageOps.exif_transpose(Image.open(arq))  # foto de celular vem deitada sem isso
    icc = im.info.get("icc_profile")  # perfil de cor: sem ele a foto do iPhone (P3) sai lavada
    return np.asarray(im.convert("RGB"), dtype=np.float32) / 255, icc


def salvar(rgb, saida, icc, largura=None):
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))
    if largura and largura < im.width:
        im = im.resize((int(largura), round(im.height * largura / im.width)), Image.LANCZOS)
    kw = {"icc_profile": icc} if icc else {}
    if saida.lower().endswith((".jpg", ".jpeg")):
        kw.update(quality=92, subsampling=0)
    im.save(saida, **kw)


def rostos(rgb):
    """[(x, y, w, h)] dos rostos, do maior para o menor (YuNet, modelo oficial do OpenCV)"""
    h, w = rgb.shape[:2]
    esc = min(1.0, 1280 / max(h, w))
    bgr = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    if esc < 1:
        bgr = cv2.resize(bgr, (round(w * esc), round(h * esc)), interpolation=cv2.INTER_AREA)
    det = cv2.FaceDetectorYN.create(str(MODELO_ROSTO), "", (bgr.shape[1], bgr.shape[0]), 0.7)
    _, achados = det.detect(bgr)
    caixas = [tuple(int(v / esc) for v in f[:4]) for f in (achados if achados is not None else [])]
    return sorted(caixas, key=lambda c: -c[2] * c[3])


def luz(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0] / 100  # luminosidade 0..1


def analisar(arq):
    rgb, icc = abrir(arq)
    L = luz(rgb)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    cinza = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    r = rostos(rgb)
    info = {
        "tamanho": f"{rgb.shape[1]}x{rgb.shape[0]}",
        "perfil_de_cor": bool(icc),
        "brilho_medio": round(float(L.mean()) * 100),           # 45-60 costuma ser bom
        "estourado_%": round(float((L > 0.98).mean()) * 100, 1),  # >2: realces negativos
        "preto_%": round(float((L < 0.03).mean()) * 100, 1),      # >5: sombras positivas
        "contraste": round(float(L.std()) * 100),               # <15: chapado; >28: duro
        "dominante_a": round(float(lab[..., 1].mean()), 1),     # >+4 magenta, <-4 verde
        "dominante_b": round(float(lab[..., 2].mean()), 1),     # >+8 amarelado/quente, <-4 azulado/frio
        "saturacao_media": round(float(hsv[..., 1].mean()) * 100),
        "nitidez": round(float(cv2.Laplacian(cinza, cv2.CV_64F).var())),  # <100: mole ou desfocada
        "rostos": [{"x": x, "y": y, "w": w, "h": h, "brilho": round(float(L[y:y + h, x:x + w].mean()) * 100)}
                   for x, y, w, h in r[:5]],
    }
    print(json.dumps(info, ensure_ascii=False, indent=1))
    return info


def mascara_pele(rgb, caixas):
    """pele só dentro dos rostos (um pouco maiores), com borda suave"""
    h, w = rgb.shape[:2]
    m = np.zeros((h, w), np.float32)
    ycc = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb)
    tom = cv2.inRange(ycc, (0, 133, 77), (255, 173, 127)).astype(np.float32) / 255
    for x, y, cw, ch in caixas:
        x0, y0 = max(0, x - cw // 4), max(0, y - ch // 4)
        x1, y1 = min(w, x + cw + cw // 4), min(h, y + ch + ch // 4)
        m[y0:y1, x0:x1] = tom[y0:y1, x0:x1]
    k = max(3, (min(h, w) // 200) * 2 + 1)
    return cv2.GaussianBlur(m, (k * 4 + 1, k * 4 + 1), 0)[..., None]


def enquadrar(rgb, proporcao, caixas):
    """maior recorte na proporção, com o rosto no terço de cima (ou centralizado, sem rosto)"""
    h, w = rgb.shape[:2]
    pa, pb = map(float, proporcao.split(":"))
    alvo = pa / pb
    cw, ch = (w, round(w / alvo)) if w / h < alvo else (round(h * alvo), h)
    cw, ch = min(cw, w), min(ch, h)
    if caixas:
        x, y, fw, fh = caixas[0]
        cx, cy = x + fw / 2, y + fh / 2
        x0, y0 = cx - cw / 2, cy - ch / 3
    else:
        x0, y0 = (w - cw) / 2, (h - ch) / 2
    x0, y0 = int(min(max(x0, 0), w - cw)), int(min(max(y0, 0), h - ch))
    return rgb[y0:y0 + ch, x0:x0 + cw]


def aplicar(entrada, saida, a):
    assert not os.path.exists(saida), f"saída já existe, use outro nome (-v2): {saida}"
    rgb, icc = abrir(entrada)
    g = lambda k: float(a.get(k, 0) or 0)
    if a.get("girar"):
        h, w = rgb.shape[:2]
        t = np.radians(abs(g("girar")))
        zoom = max((w * np.cos(t) + h * np.sin(t)) / w, (w * np.sin(t) + h * np.cos(t)) / h)  # sem canto preto
        M = cv2.getRotationMatrix2D((w / 2, h / 2), g("girar"), zoom)
        rgb = cv2.warpAffine(rgb, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    caixas = rostos(rgb) if (a.get("recorte") or g("pele")) else []
    if a.get("auto_branco"):
        medias = rgb.reshape(-1, 3).mean(0)
        ganho = medias.mean() / np.maximum(medias, 1e-4)
        rgb = rgb * (1 + (ganho - 1) * 0.6)  # 60%: corrige o tom sem deixar a foto sem vida
    if g("temperatura") or g("matiz"):
        t, m = g("temperatura") / 100 * 0.12, g("matiz") / 100 * 0.06
        rgb = rgb * np.array([1 + t, 1 - m, 1 - t], np.float32)
    if g("exposicao"):
        rgb = rgb * 2 ** g("exposicao")
    rgb = np.clip(rgb, 0, 1)
    if g("realces") or g("sombras"):
        L = luz(rgb)[..., None]
        s, r = g("sombras") / 100 * 0.5, g("realces") / 100 * 0.5
        rgb = rgb + s * (1 - L) ** 2 * np.where(s > 0, 1 - rgb, rgb) + r * L ** 2 * np.where(r > 0, 1 - rgb, rgb)
    if g("contraste"):
        rgb = 0.5 + (rgb - 0.5) * (1 + g("contraste") / 100 * 0.6)
    rgb = np.clip(rgb, 0, 1).astype(np.float32)
    if g("clareza"):
        lab = cv2.cvtColor((rgb * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
        lab2 = lab.copy()
        lab2[..., 0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(lab[..., 0])
        rgb2 = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB).astype(np.float32) / 255
        rgb = rgb + (rgb2 - rgb) * g("clareza") / 100
    if g("vibracao") or g("saturacao"):
        hsv = cv2.cvtColor(np.clip(rgb, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
        sat = hsv[..., 1]
        pele = ((hsv[..., 0] > 5) & (hsv[..., 0] < 50)).astype(np.float32)  # laranja da pele: vibração não mexe
        sat = sat * (1 + g("vibracao") / 100 * 0.8 * (1 - sat) * (1 - 0.7 * pele))
        hsv[..., 1] = np.clip(sat * (1 + g("saturacao") / 100), 0, 1)
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    rgb = np.clip(rgb, 0, 1).astype(np.float32)
    if g("ruido"):
        u8 = (rgb * 255).astype(np.uint8)
        f = g("ruido") / 100 * 10
        rgb = cv2.fastNlMeansDenoisingColored(u8, None, f, f, 7, 21).astype(np.float32) / 255
    if g("pele") and caixas:
        u8 = (rgb * 255).astype(np.uint8)
        d = max(5, min(rgb.shape[:2]) // 120)
        liso = cv2.bilateralFilter(u8, d, 40, d).astype(np.float32) / 255
        m = mascara_pele(rgb, caixas) * g("pele") / 100 * 0.7  # até 70%: textura da pele continua (sem "plástico")
        rgb = rgb * (1 - m) + liso * m
    if g("nitidez"):
        borrado = cv2.GaussianBlur(rgb, (0, 0), 1.2)
        rgb = rgb + (rgb - borrado) * g("nitidez") / 100 * 1.2
    if a.get("recorte"):
        rgb = enquadrar(rgb, a["recorte"], caixas)
    salvar(rgb, saida, icc, a.get("largura"))
    print(saida)


def teste():
    import tempfile
    d = tempfile.mkdtemp()
    x = np.linspace(0, 1, 400, dtype=np.float32)
    img = np.stack([np.tile(x, (300, 1)) * 0.9 + 0.08, np.tile(x, (300, 1)) * 0.8, np.tile(x, (300, 1)) * 0.6], -1)
    Image.fromarray((img * 255).astype(np.uint8)).save(f"{d}/a.png")
    info = analisar(f"{d}/a.png")
    assert info["dominante_b"] > 4, info  # foto amarelada
    aplicar(f"{d}/a.png", f"{d}/b.png", {"auto_branco": True})
    b = np.asarray(Image.open(f"{d}/b.png"), np.float32)
    assert abs(b[..., 0].mean() - b[..., 2].mean()) < abs(img[..., 0].mean() - img[..., 2].mean()) * 255 * 0.6
    aplicar(f"{d}/a.png", f"{d}/c.png", {"exposicao": 1, "contraste": 20, "clareza": 30, "vibracao": 30,
                                          "nitidez": 40, "ruido": 20, "realces": -30, "sombras": 30, "girar": 3})
    c = np.asarray(Image.open(f"{d}/c.png"))
    assert c.shape == (300, 400, 3) and c.mean() > np.asarray(Image.open(f"{d}/a.png")).mean()
    aplicar(f"{d}/a.png", f"{d}/r.png", {"recorte": "4:5"})
    w, h = Image.open(f"{d}/r.png").size
    assert abs(w / h - 0.8) < 0.01, (w, h)
    try:
        aplicar(f"{d}/a.png", f"{d}/b.png", {})
        raise SystemExit("devia recusar sobrescrever")
    except AssertionError:
        pass
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a[:1] == ["analisar"] and len(a) == 2:
        analisar(a[1])
    elif a[:1] == ["aplicar"] and len(a) == 4:
        aj = a[3]
        aplicar(a[1], a[2], json.load(open(aj, encoding="utf-8")) if os.path.exists(aj) else json.loads(aj))
    else:
        sys.exit(__doc__)
