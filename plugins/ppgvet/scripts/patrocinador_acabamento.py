# Acabamento da cena: brilho suave nas áreas claras, +5% contraste, +8% saturação, leve calor,
# vinheta e (se algo cai) um tranco amortecido no quadro do pouso.
# uso: patrocinador_acabamento.py <pasta-quadros f0001.png…> <pasta-saida> <quadro-do-pouso | 9999 se nada cai>
# (o reflexo correndo pelo vidro saiu: o usuário achou que ficou errado, 31/10/2026)
import sys, glob, os, math, numpy as np, cv2
ent, sai, pouso = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(sai, exist_ok=True)
arqs = sorted(glob.glob(f"{ent}/f*.png"))
h, w = cv2.imread(arqs[0]).shape[:2]
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
vinheta = np.clip(1 - 0.16 * np.clip(r - 0.55, 0, None) ** 1.5 / 0.4, 0.82, 1)[..., None]
for i, a in enumerate(arqs, start=1):
    im = cv2.imread(a).astype(np.float32)
    lum = cv2.cvtColor(np.clip(im, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    clar = np.clip((lum - 215) / 40, 0, 1)
    bloom = cv2.GaussianBlur(im * clar[..., None], (0, 0), 18)
    im = im + 0.22 * bloom
    im = (im - 128) * 1.05 + 128
    hsv = cv2.cvtColor(np.clip(im, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 1.08
    im = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    im[..., 2] *= 1.012; im[..., 0] *= 0.99
    im *= vinheta
    k = i - pouso
    if 0 <= k < 10:
        e = math.exp(-k / 2.3)
        M = np.float32([[1, 0, 4 * e * math.sin(k * 2.4)], [0, 1, 10 * e * math.cos(k * 2.1)]])
        im = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    cv2.imwrite(f"{sai}/f{i:04d}.png", np.clip(im, 0, 255).astype(np.uint8))
