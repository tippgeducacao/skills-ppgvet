# Quadros finais 1080x1920: cena com aproximação/afastamento suave (subpixel; o zoompan do ffmpeg
# treme) + cartela animada (fundo borra e clareia, linha 1 sobe palavra por palavra, nome entra
# crescendo, risco cresce do centro, logos deslizam das laterais, brilho passa nas logos).
# uso: patrocinador_final.py <quadros f*.png> <saida> <fonte.ttf> <logo-podcast> <logo-patrocinador>
#      <seg-cartela 3.6> <linha1> <linha2> <INTRO> <POUSO> <M0> <M1> <cor-linha1> <cor-linha2>
#   INTRO = quadros parados de suspense no início (0 se o mascote já está em cena)
#   POUSO = quadro até onde a câmera aproxima 1,0→1,08 (fim da ação principal se nada cai)
#   M0..M1 = quadros em que a câmera afasta de volta a 1,0 (do gesto final até ele parar)
#   cores em hex sem # (ex.: 1A1A1A 408038). Saída: q0001.png… a 24 fps.
import sys, glob, os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
cena, sai, fonte, lpod, lpat, seg = sys.argv[1:7]; linha1, linha2 = sys.argv[7], sys.argv[8]
os.makedirs(sai, exist_ok=True)
W, H, FPS = 1080, 1920, 24
AZUL = (0, 48, 135)
# fundo da cartela: véu claro sobre a cena borrada. VEU=0.88 FUNDO=F5F6F8 quando a cor do nome é clara (24/11)
VEU = float(os.environ.get("VEU", 0.5))
hexcor = lambda h: tuple(int(h.lstrip('#')[k:k + 2], 16) for k in (0, 2, 4))
COR1 = hexcor(sys.argv[13]) if len(sys.argv) > 13 else AZUL   # cor da linha 1 (marca do patrocinador)
COR2 = hexcor(sys.argv[14]) if len(sys.argv) > 14 else COR1   # cor da linha 2
FUNDO = hexcor(os.environ.get("FUNDO", "ECEFF4"))
# câmera: aproxima devagar do 1º quadro (com INTRO quadros parados de suspense) até o POUSO,
# fica parada, e afasta do momento em que o mascote aparece (M0) até ele parar (M1)
INTRO = int(sys.argv[9]) if len(sys.argv) > 9 else 0
POUSO = int(sys.argv[10]) if len(sys.argv) > 10 else 0
M0 = int(sys.argv[11]) if len(sys.argv) > 11 else 115
M1 = int(sys.argv[12]) if len(sys.argv) > 12 else 168
Z = 1.08
arqs = sorted(glob.glob(f"{cena}/f*.png"))
suave = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(max(x, 0.0), 1.0))
def zoom_at(i):  # i < 0 = quadros de suspense
    if i < POUSO and INTRO + POUSO > 0: return 1.0 + (Z - 1.0) * suave((i + INTRO) / (INTRO + POUSO))
    if i < M0: return Z
    return Z - (Z - 1.0) * suave((i - M0) / (M1 - M0))
def zoomed(img, z):
    h, w = img.shape[:2]; s = W / w * z
    M = np.array([[s, 0, W / 2 - s * w / 2], [0, s, H / 2 - s * h / 2]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
n = 0
for i in range(-INTRO, 0):
    n += 1; cv2.imwrite(f"{sai}/q{n:04d}.png", zoomed(cv2.imread(arqs[0]), zoom_at(i)))
for i, a in enumerate(arqs):
    n += 1; cv2.imwrite(f"{sai}/q{n:04d}.png", zoomed(cv2.imread(a), zoom_at(i)))
ultimo = cv2.cvtColor(zoomed(cv2.imread(arqs[-1]), 1.0), cv2.COLOR_BGR2RGB)
base = Image.fromarray(ultimo)
# ---- cartela
clamp = lambda x: 0.0 if x < 0 else 1.0 if x > 1 else x
out_cubic = lambda x: 1 - (1 - clamp(x)) ** 3
def out_back(x, k=1.6):
    x = clamp(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2
def logo(p, w):
    im = Image.open(p).convert("RGBA"); im = im.crop(im.getbbox())
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
L1, L2 = logo(lpod, 400), logo(lpat, 400)
tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
def cabe(txt, tam, maxw=960):  # diminui a letra até a linha caber
    while tam > 30 and tmp.textlength(txt, font=ImageFont.truetype(fonte, tam)) > maxw: tam -= 2
    return ImageFont.truetype(fonte, tam)
f1 = cabe(linha1, 74); f2 = cabe(linha2, 96)
palavras = linha1.split(" "); esp = tmp.textlength(" ", font=f1)
larg = [tmp.textlength(p, font=f1) for p in palavras]
x0_l1 = (W - (sum(larg) + esp * (len(palavras) - 1))) / 2
Y1, Y2, CY = 660, 760, 1080
def alfa(im, a):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im
def palavra_img(txt, fnt, cor):
    w = int(tmp.textlength(txt, font=fnt)) + 40; h = int(fnt.size * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).text((20, 10), txt, font=fnt, fill=cor + (255,)); return im
pal_imgs = [palavra_img(p, f1, COR1) for p in palavras]; l2_img = palavra_img(linha2, f2, COR2)
blur_cache = {}
nc = round(float(seg) * FPS)
for k in range(nc):
    t = k / FPS
    b = out_cubic(t / 0.55); sig = round(30 * b)
    if sig not in blur_cache:
        blur_cache[sig] = base.filter(ImageFilter.GaussianBlur(sig)) if sig else base
    bg = Image.blend(blur_cache[sig], Image.new("RGB", (W, H), FUNDO), VEU * b)
    zb = 1 + 0.05 * (t / float(seg))  # aproximação lenta do fundo
    bg = bg.resize((round(W * zb), round(H * zb)), Image.BILINEAR)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    fr = bg.convert("RGBA")
    # palavras da linha 1 sobem uma a uma, saindo do desfoque
    x = x0_l1
    for j, (im, w) in enumerate(zip(pal_imgs, larg)):
        p = (t - 0.35 - 0.09 * j) / 0.45
        if p > 0:
            a = out_cubic(p); dy = 46 * (1 - out_back(p)); bl = 6 * (1 - a)
            im2 = im.filter(ImageFilter.GaussianBlur(bl)) if bl > 0.3 else im
            fr.alpha_composite(alfa(im2, a), (int(x - 20), int(Y1 - 10 + dy)))
        x += w + esp
    # linha 2 entra crescendo
    p = (t - 0.75) / 0.45
    if p > 0:
        s = 0.55 + 0.45 * out_back(p, 2.0); a = out_cubic(p)
        im = l2_img.resize((max(1, round(l2_img.width * s)), max(1, round(l2_img.height * s))), Image.LANCZOS)
        fr.alpha_composite(alfa(im, a), (int(W / 2 - im.width / 2), int(Y2 + l2_img.height / 2 - im.height / 2)))
    # risco do meio cresce do centro
    p = out_cubic((t - 1.05) / 0.35)
    if p > 0:
        ln = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hh = 100 * p
        ImageDraw.Draw(ln).line((540, CY - hh, 540, CY + hh), fill=(140, 150, 165, 255), width=3); fr.alpha_composite(ln)
    # logos deslizam das laterais com leve impulso
    for img, xf, lado, t0 in ((L1, 80, -1, 1.05), (L2, W - 80 - 400, 1, 1.17)):
        p = (t - t0) / 0.55
        if p > 0:
            xx = xf + lado * 120 * (1 - out_back(p)); a = out_cubic(p * 1.4)
            fr.alpha_composite(alfa(img, a), (int(xx), int(CY - img.height / 2)))
    # brilho passando pelas logos
    p = (t - 1.9) / 0.6
    if 0 < p < 1:
        sh = Image.new("L", (W, H), 0); dsh = ImageDraw.Draw(sh)
        cx = -200 + (W + 400) * p
        dsh.polygon([(cx - 60, CY - 160), (cx + 20, CY - 160), (cx - 40, CY + 160), (cx - 120, CY + 160)], fill=150)
        sh = sh.filter(ImageFilter.GaussianBlur(25))
        mascara = Image.new("L", (W, H), 0)
        for img, xf in ((L1, 80), (L2, W - 480)):
            mascara.paste(img.getchannel("A"), (xf, int(CY - img.height / 2)))
        sh = Image.fromarray((np.array(sh, np.float32) * np.array(mascara, np.float32) / 255).astype(np.uint8))
        luz = Image.new("RGBA", (W, H), (255, 255, 255, 0)); luz.putalpha(sh); fr.alpha_composite(luz)
    n += 1; fr.convert("RGB").save(f"{sai}/q{n:04d}.png")
print(n, "quadros")
