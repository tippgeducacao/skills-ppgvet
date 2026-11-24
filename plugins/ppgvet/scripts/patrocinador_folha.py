# Folha de referência do mascote: corpo inteiro à esquerda, closes à direita, fundo branco.
# uso: patrocinador_folha.py <saida.png> <corpo.png> <close> [<close> ...]
#   <close> = arquivo  ou  arquivo:x0,y0,x1,y1  (recorte em pixels daquele arquivo)
# PNG transparente vai sobre branco. 1 a 3 closes = 1 coluna; 4 ou mais = 2 colunas.
import sys, math
from PIL import Image

H, M, G = 1500, 50, 40  # altura, margem, espaço entre peças


def abrir(spec):
    arq, _, caixa = spec.partition(":")
    im = Image.open(arq).convert("RGBA")
    if caixa:
        im = im.crop(tuple(int(v) for v in caixa.split(",")))
    fundo = Image.new("RGBA", im.size, (255, 255, 255, 255))
    fundo.alpha_composite(im)
    im = fundo.convert("RGB")
    bbox = Image.eval(im.convert("L"), lambda v: 255 if v < 245 else 0).getbbox()  # corta a sobra branca
    return im.crop(bbox) if bbox else im


def caber(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


saida, corpo, closes = sys.argv[1], sys.argv[2], sys.argv[3:]
assert closes, "falta pelo menos um close"
corpo = caber(abrir(corpo), 10_000, H - 2 * M)
cols = 1 if len(closes) <= 3 else 2
lins = math.ceil(len(closes) / cols)
cel = (H - 2 * M - (lins - 1) * G) // lins
W = M + corpo.width + 2 * G + cols * cel + (cols - 1) * G + M
folha = Image.new("RGB", (W, H), "white")
folha.paste(corpo, (M, (H - corpo.height) // 2))
x0 = M + corpo.width + 2 * G
for k, spec in enumerate(closes):
    c = caber(abrir(spec), cel, cel)
    cx, cy = x0 + (k % cols) * (cel + G), M + (k // cols) * (cel + G)
    folha.paste(c, (cx + (cel - c.width) // 2, cy + (cel - c.height) // 2))
folha.save(saida)
print(saida, folha.size)
