#!/usr/bin/env python3
"""Capas do portal do aluno (Eduq) de uma pós, no padrão da casa: a capa principal e as individuais (Trilha Inicial de
Aprendizado, Abertura, Módulo I a N, Materiais Complementares), cada uma em 1000x1000 e 1080x1920, conferidas pelo arte.py.
uso: eduq.py ficha.json [--saida <pasta>]   (sem --saida: <artes>/eduq/<NOME_DA_POS>/)
     eduq.py --teste
ficha.json: {"pos": "NGB" (sigla do marca.md) ou o nome por extenso, "marca": "PPGVET" ou "PPG" (só para pós fora do marca.md),
             "foto": "<foto real do tema da pós>", "foco": "50% 40%" (opcional), "modulos": 12, "trilha": true,
             "principais": [{"nome": "TURMA 01-27 #01", "foto": "<outra foto>"}] (opcional: variantes da capa principal)}
Regras (marca.md): logo PPG Educação em todas (o portal é do Grupo PPG); fundo na cor da marca da pós; nunca "MBA".
Nomes de arquivo da equipe (o Eduq já está organizado assim): "CAPA PRINCIPAL - 1080x1920.png", "MODULO 3 - 1000x1000.png"."""
import base64, html as H, io, json, os, re, sys, tempfile, unicodedata
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo, pasta  # noqa: E402
from aulas_semana import letra_sobre, pos_tabela  # noqa: E402
import arte  # noqa: E402

COR = {"PPGVET": "#00B7AB", "PPG": "#1670C2"}  # a cor de ação de cada marca (marca.md); a pós só escolhe qual
TAMANHOS = {"1080x1920": "portal", "1000x1000": "portal-quadrado"}
ROMANOS = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split()
# telas do aparelho (acervo/eduq/aparelho.png, 1204x860, do PSD da equipe): cantos sup-esq, sup-dir, inf-dir, inf-esq
NOTEBOOK = [(376.7, 37.2), (1180.9, 83.5), (1158.8, 590.7), (385.5, 520.4)]
CELULAR = [(6.3, 403.9), (192.7, 370.9), (288.3, 800.6), (100.7, 844.2)]
TELA_NOTEBOOK, TELA_CELULAR = (2255, 1428), (1469, 3129)  # tamanho do conteúdo de cada tela no PSD
FIT = """<script>document.fonts.ready.then(()=>{for(const e of document.querySelectorAll('[data-cabe]')){let t=parseFloat(getComputedStyle(e).fontSize);
while((e.scrollHeight>+e.dataset.cabe||e.scrollWidth>e.clientWidth)&&t>24){t-=2;e.style.fontSize=t+'px'}}})</script>"""


def sem_acento(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()


def pos_da_ficha(ficha):
    """(nome, marca) pela sigla ou pelo nome no marca.md; fora da tabela, o nome e a marca vêm da ficha"""
    tab, pos = pos_tabela(), str(ficha.get("pos", "")).strip()
    if pos.upper() in tab:
        return tab[pos.upper()][0], tab[pos.upper()][1]
    for nome, marca, _ in tab.values():
        if sem_acento(nome) == sem_acento(pos):
            return nome, marca
    marca = str(ficha.get("marca", "")).upper()
    if marca not in COR:
        raise SystemExit(f'"{pos}" não está no marca.md: diga a marca na ficha ("marca": "PPGVET" ou "PPG") e confira a grafia do nome')
    return pos, marca


def uri(im, fmt="PNG"):
    b = io.BytesIO()
    im.save(b, fmt, **({"quality": 88} if fmt == "JPEG" else {}))
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()


def cobrir(im, tam, foco=(.5, .4)):
    """recorta a foto para cobrir o tamanho, como object-fit: cover"""
    from PIL import Image
    w, h = tam
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x, y = round((im.width - w) * foco[0]), round((im.height - h) * foco[1])
    return im.crop((x, y, x + w, y + h))


def perspectiva(origem, destino):
    """8 coeficientes do Image.PERSPECTIVE (destino -> origem)"""
    import numpy as np
    a, b = [], []
    for (x, y), (u, v) in zip(destino, origem):
        a += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    return np.linalg.solve(np.array(a, float), np.array(b, float)).tolist()


def numero_contorno(n, tam):
    """o número do módulo só em contorno branco, centrado na tela do notebook"""
    from PIL import Image, ImageChops, ImageDraw, ImageFont
    w, h = tam
    fonte = ImageFont.truetype(acervo("fontes", "montserrat-variavel.ttf"), round(h * .98))
    fonte.set_variation_by_name("SemiBold")
    cheio, miolo = Image.new("L", tam), Image.new("L", tam)
    for camada, borda in ((cheio, 20), (miolo, 0)):  # contorno da espessura das capas da equipe
        d = ImageDraw.Draw(camada)
        d.text((w / 2, h * .5), str(n), font=fonte, anchor="mm", fill=255, stroke_width=borda, stroke_fill=255)
    return ImageChops.subtract(cheio, miolo)


def aparelho(foto, numero, principal_vertical, foco):
    """notebook e celular do acervo com a foto (e o número) na tela do notebook e a capa principal na do celular"""
    import numpy as np
    from PIL import Image
    base = Image.open(acervo("eduq", "aparelho.png")).convert("RGBA")
    reflexo = Image.open(acervo("eduq", "aparelho-reflexo.png")).convert("RGBA")
    tela = cobrir(foto, TELA_NOTEBOOK, foco).convert("RGBA")
    veu = Image.linear_gradient("L").resize(TELA_NOTEBOOK).point(lambda v: max(0, min(255, (v - 115) * 2)))  # escurece o pé da tela
    tela = Image.composite(Image.new("RGBA", TELA_NOTEBOOK, (26, 26, 26, 255)), tela, veu)
    if numero:
        tela.paste((255, 255, 255, 255), mask=numero_contorno(numero, TELA_NOTEBOOK))
    cel = cobrir(principal_vertical.convert("RGB"), TELA_CELULAR, (.5, .5)).convert("RGBA")
    for conteudo, quad in ((tela, NOTEBOOK), (cel, CELULAR)):
        ret = [(0, 0), (conteudo.width, 0), (conteudo.width, conteudo.height), (0, conteudo.height)]
        torto = conteudo.transform(base.size, Image.PERSPECTIVE, perspectiva(ret, quad), Image.BICUBIC)
        base.alpha_composite(torto)
    b = np.asarray(base).astype(float) / 255  # reflexo em modo "tela", como no PSD
    r = np.asarray(reflexo).astype(float) / 255
    tela_rgb = 1 - (1 - b[..., :3]) * (1 - r[..., :3])
    b[..., :3] = b[..., :3] * (1 - r[..., 3:]) + tela_rgb * r[..., 3:]
    return Image.fromarray((b * 255).round().astype("uint8"), "RGBA")


CSS = """@font-face{font-family:Montserrat;src:url('${fonte}')}
*{margin:0;box-sizing:border-box}body{position:relative;width:${w}px;height:${h}px;overflow:hidden;font-family:Montserrat;background:#1A1A1A;color:#FFFFFF}
.foto{position:absolute;inset:0}.foto img{width:100%;height:100%;object-fit:cover;display:block}
.veu{position:absolute;inset:0;background:linear-gradient(180deg,rgba(26,26,26,0) ${veu0}%,rgba(26,26,26,.94) ${veu1}%)}
.miolo{position:absolute;left:${lado}px;right:${lado}px;bottom:${baixo}px;display:flex;flex-direction:column;align-items:center;text-align:center}
.pilula{background:${cor};color:${sobre};font-weight:800;font-size:${p}px;letter-spacing:.08em;padding:.45em 1em .4em;text-transform:uppercase}
.titulo{font-weight:900;text-transform:uppercase;line-height:1.02;letter-spacing:-.01em;text-wrap:balance;margin-top:${g}px;width:100%}
.apoio{font-weight:300;text-transform:uppercase;letter-spacing:.06em;line-height:1.15;margin-top:${g2}px}
.logo{width:${logo}px;margin-top:${g3}px}"""

PRINCIPAL = """<div class="foto" data-sangra><img alt="foto" src="${foto}" style="object-position:${foco}"><div class="veu"></div></div>
<div class="miolo"><div class="pilula">Pós-Graduação</div><h1 class="titulo" data-cabe="${cabe}" style="font-size:${t}px">${titulo}</h1>
<img class="logo" alt="logo-sobre-foto" src="${logo_src}"></div>"""

INDIVIDUAL = """<div class="foto" data-sangra style="background:${cor}"><img alt="foto" src="${foto}" style="opacity:.25;object-position:${foco}"><div class="veu"></div></div>
<img alt="aparelho-sobre-foto" src="${aparelho}" style="position:absolute;left:${ax}px;top:${ay}px;width:${aw}px">
<div class="miolo" style="top:${mt}px;bottom:auto"><h1 class="titulo" data-cabe="${cabe}" style="font-size:${t}px">${titulo}</h1><p class="apoio" style="font-size:${a}px">Aulas<br>curriculares</p>
<img class="logo" alt="logo-sobre-foto" src="${logo_src}"></div>"""

# medidas de cada tamanho, tiradas das capas que a equipe já publicou (vertical) e ajustadas ao quadrado
MEDIDAS = {"1080x1920": dict(principal=dict(t=80, cabe=330, p=32, g=26, g3=60, logo=230, veu0=38, veu1=74),
                             individual=dict(t=116, cabe=250, a=50, g=0, g2=22, g3=40, logo=230, veu0=30, veu1=70, ax=113, ay=548, aw=857, mt=1150)),
           "1000x1000": dict(principal=dict(t=76, cabe=250, p=30, g=20, g3=34, logo=190, veu0=30, veu1=70),
                             individual=dict(t=96, cabe=200, a=38, g=0, g2=14, g3=24, logo=180, veu0=22, veu1=64, ax=110, ay=36, aw=780, mt=612))}


def pagina(tipo, tam, valores):
    import string
    w, h = map(int, tam.split("x"))
    _, lado, cima, baixo = arte.FORMATOS[TAMANHOS[tam]][1:]
    v = {"g2": 0, "p": 0, **MEDIDAS[tam][tipo], "w": w, "h": h, "lado": lado, "baixo": baixo,
         "fonte": Path(acervo("fontes", "montserrat-variavel.ttf")).as_uri(),
         "logo_src": Path(acervo("logos", "ppg", "logo-ppg-educacao-branco.png")).as_uri(), **valores}
    css = string.Template(CSS).substitute(v)
    corpo = string.Template(PRINCIPAL if tipo == "principal" else INDIVIDUAL).substitute(v)
    return f"<!doctype html><meta charset=utf-8><style>{css}</style><body>{corpo}{FIT}</body>"


def pecas(ficha):
    """(nome do arquivo sem o tamanho, título, número na tela) de cada capa individual"""
    lista = [("TRILHA INICIAL DE APRENDIZADO", "Trilha inicial de aprendizado", None)] if ficha.get("trilha") else []
    lista.append(("ABERTURA", "Abertura", None))
    n = int(ficha.get("modulos", 0))
    if not 1 <= n <= len(ROMANOS):
        raise SystemExit(f'"modulos": de 1 a {len(ROMANOS)} (a tarefa diz quantos)')
    lista += [(f"MODULO {i}", f"Módulo {ROMANOS[i - 1]}", i) for i in range(1, n + 1)]
    return lista + [("MATERIAIS COMPLEMENTARES", "Materiais complementares", None)]


def gerar(ficha, saida, pasta_ficha="."):
    from PIL import Image, ImageOps
    nome, marca = pos_da_ficha(ficha)
    if re.search(r"\bMBA\b", nome, re.I):
        raise SystemExit('"MBA" não entra na capa: o nome é da Pós-Graduação (marca.md)')
    cor = COR[marca]
    foco = tuple(float(x.rstrip("%")) / 100 for x in str(ficha.get("foco", "50% 40%")).split()[:2])
    abre = lambda f: ImageOps.exif_transpose(Image.open(f if Path(f).is_absolute() else Path(pasta_ficha) / f)).convert("RGB")
    foto = abre(ficha["foto"])
    principais = ficha.get("principais") or [{"nome": "", "foto": ficha["foto"]}]
    saida, ok, pngs = Path(saida), True, []
    saida.mkdir(parents=True, exist_ok=True)
    comum = dict(cor=cor, sobre=letra_sobre(cor), foco=H.escape(str(ficha.get("foco", "50% 40%"))))

    def fazer(arquivo, tipo, tam, valores, d):
        nonlocal ok
        html = Path(d) / f"{arquivo} - {tam}.html"
        html.write_text(pagina(tipo, tam, dict(comum, **valores)), encoding="utf-8")
        png = saida / f"{arquivo} - {tam}.png"
        ok = arte.main(str(html), TAMANHOS[tam], str(png)) and ok
        png.with_suffix(".jpg").unlink(missing_ok=True)  # o Eduq recebe PNG
        pngs.append(png)
        return png

    with tempfile.TemporaryDirectory() as d:
        vertical = None
        for p in principais:
            arq = "CAPA PRINCIPAL" + (f" - {p['nome']}" if p.get("nome") else "")
            im = abre(p["foto"])
            for tam in TAMANHOS:
                w, h = map(int, tam.split("x"))
                png = fazer(arq, "principal", tam, dict(foto=uri(cobrir(im, (w, h), foco), "JPEG"), titulo=H.escape(nome)), d)
                if vertical is None and tam == "1080x1920":
                    vertical = Image.open(png)
        for arq, titulo, numero in pecas(ficha):
            ap = uri(aparelho(foto, numero, vertical, foco))
            for tam in TAMANHOS:
                w, h = map(int, tam.split("x"))
                fazer(arq, "individual", tam, dict(foto=uri(cobrir(foto, (w, h), foco), "JPEG"), aparelho=ap, titulo=H.escape(titulo)), d)
    folha(pngs, saida.parent / f"{saida.name}-folha.jpg")
    print("folha:", saida.parent / f"{saida.name}-folha.jpg")
    return ok


def folha(pngs, destino, alto=420):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims = [i.resize((round(i.width * alto / i.height), alto)) for i in ims]
    por_linha = 8
    linhas = [ims[i:i + por_linha] for i in range(0, len(ims), por_linha)]
    f = Image.new("RGB", (max(sum(i.width + 8 for i in l) for l in linhas), len(linhas) * (alto + 8)), "white")
    for j, l in enumerate(linhas):
        x = 0
        for i in l:
            f.paste(i, (x, j * (alto + 8)))
            x += i.width + 8
    f.save(destino, quality=82)


def pasta_da_pos(nome):
    return re.sub(r"\s+", "_", nome.upper().replace(",", ""))


def teste():
    import portao
    from PIL import Image, ImageDraw
    portao.REGISTRO = Path(tempfile.mkdtemp()) / "conferencias.jsonl"  # o teste não suja o registro de verdade
    assert pos_da_ficha({"pos": "NGB"}) == ("Nutrição e Gestão de Bovinos", "PPGVET")
    assert pos_da_ficha({"pos": "nutricao e gestao de bovinos"})[1] == "PPGVET"
    assert pos_da_ficha({"pos": "Medicina Felina", "marca": "PPGVET"}) == ("Medicina Felina", "PPGVET")
    try:
        pos_da_ficha({"pos": "Medicina Felina"})
        raise AssertionError("pós fora do marca.md sem marca tem que parar")
    except SystemExit as e:
        assert "marca" in str(e)
    assert [p[0] for p in pecas({"modulos": 2, "trilha": True})] == ["TRILHA INICIAL DE APRENDIZADO", "ABERTURA", "MODULO 1", "MODULO 2", "MATERIAIS COMPLEMENTARES"]
    assert pecas({"modulos": 13})[-2][1] == "Módulo XIII"
    assert pasta_da_pos("Piscicultura e Produção de Tilápia") == "PISCICULTURA_E_PRODUÇÃO_DE_TILÁPIA"
    m = numero_contorno(0, (400, 250))
    assert m.getbbox() and m.getpixel((200, 125)) == 0  # só o contorno: o miolo do número fica vazio
    with tempfile.TemporaryDirectory() as d:
        foto = Image.new("RGB", (1800, 1200), (70, 95, 60))
        ImageDraw.Draw(foto).rectangle((0, 0, 1800, 400), fill=(220, 228, 232))  # céu claro: o véu tem que segurar a letra
        foto.save(f"{d}/tema.jpg")
        assert gerar({"pos": "Medicina Felina", "marca": "PPG", "foto": "tema.jpg", "modulos": 1}, f"{d}/MEDICINA_FELINA", d), "capa limpa não pode reprovar"
        nomes = sorted(p.name for p in Path(d, "MEDICINA_FELINA").iterdir())
        assert nomes == sorted(f"{a} - {t}.png" for a in ("CAPA PRINCIPAL", "ABERTURA", "MODULO 1", "MATERIAIS COMPLEMENTARES") for t in TAMANHOS), nomes
        assert Image.open(f"{d}/MEDICINA_FELINA/MODULO 1 - 1000x1000.png").size == (1000, 1000)
        try:
            gerar({"pos": "MBA em Gestão", "marca": "PPG", "foto": "tema.jpg", "modulos": 1}, f"{d}/x", d)
            raise AssertionError("MBA tem que parar")
        except SystemExit as e:
            assert "MBA" in str(e)
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a and a[0].endswith(".json"):
        ficha = json.loads(Path(a[0]).read_text(encoding="utf-8"))
        nome = pos_da_ficha(ficha)[0]
        saida = a[a.index("--saida") + 1] if "--saida" in a else str(Path(pasta("artes")) / "eduq" / pasta_da_pos(nome))
        sys.exit(0 if gerar(ficha, saida, Path(a[0]).parent) else 1)
    else:
        sys.exit(__doc__)
