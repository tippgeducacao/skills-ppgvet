#!/usr/bin/env python3
"""Capas do portal do aluno (Eduq) de uma pós, no padrão da casa: a capa principal e as individuais (Trilha Inicial de
Aprendizado, Abertura, Módulo I a N, Materiais Complementares), cada uma em 1000x1000 e 1080x1920.
Motor: os PSDs da equipe (acervo/eduq/modelos) preenchidos no Photopea (psd.py): sai o PNG e o PSD editável (em editaveis/).
Plano B, com o Photopea fora: as mesmas capas em código (HTML medido pelo arte.py), sem PSD; o aviso sai na tela.
uso: eduq.py ficha.json [--saida <pasta>] [--codigo]   (sem --saida: <artes>/eduq/<NOME_DA_POS>/; --codigo: direto o plano B)
     eduq.py --teste
ficha.json: {"pos": "NGB" (sigla do marca.md) ou o nome por extenso, "marca": "PPGVET" ou "PPG" (só para pós fora do marca.md),
             "foto": "<foto real do tema da pós>", "foco": "50% 40%" (opcional), "modulos": 12, "trilha": true,
             "principais": [{"nome": "TURMA 01-27 #01", "foto": "<outra foto>", "foco": "80% 40%"}] (opcional: variantes da capa
             principal, cada uma com o seu enquadramento; o celular dos módulos mostra a última),
             "fundos": {"1000x1000": "<foto>", "1080x1920": "<foto>"} (opcional: outra foto no fundo dos módulos; sem ela, a "foto")}
Regras (marca.md): logo PPG Educação em todas (o portal é do Grupo PPG); fundo na cor da marca da pós; nunca "MBA".
Nomes de arquivo da equipe (o Eduq já está organizado assim): "CAPA PRINCIPAL - 1080x1920.png", "MODULO 3 - 1000x1000.png"."""
import base64, html as H, io, json, os, re, sys, tempfile, unicodedata
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import abrir_foto, acervo, pasta  # noqa: E402
from aulas_semana import contraste, pos_tabela  # noqa: E402
import arte  # noqa: E402
from psd import Indisponivel, Sessao, Travou, duas_linhas, preencher, quebra, solido  # noqa: E402
from portao import registrar  # noqa: E402

COR = {"PPGVET": dict(fundo="#55978B", pilula="#00857D"),
       "PPG": dict(fundo="#0080F6", pilula="#047FEF", pilula_codigo="#0072D6")}  # plano B: a pílula da equipe não passa 4,5:1 em letra pequena  # exceção da Eduq no marca.md (cores das capas publicadas)
TAMANHOS = {"1080x1920": "portal", "1000x1000": "portal-quadrado"}
ROMANOS = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split()
# telas do aparelho (acervo/eduq/aparelho.png, 1204x860, do PSD da equipe): cantos sup-esq, sup-dir, inf-dir, inf-esq
NOTEBOOK = [(376.7, 37.2), (1180.9, 83.5), (1158.8, 590.7), (385.5, 520.4)]
CELULAR = [(6.3, 403.9), (192.7, 370.9), (288.3, 800.6), (100.7, 844.2)]
TELA_NOTEBOOK, TELA_CELULAR = (2255, 1428), (1469, 3129)  # tamanho do conteúdo de cada tela no PSD
# onde cada coisa fica nos PSDs da equipe (acervo/eduq/modelos/<principal|modulo|fundo>-<tamanho>.psd)
PSD = {"1000x1000": dict(titulo=[61, 540, 940, 884], aparelho=[119, 85, 847, 605], largura=860, cor="Preenchimento de Cor 2",
                         aulas="aulas curriculares", logo="logo - PPG Educação_branca"),
       "1080x1920": dict(titulo=[84, 1225, 998, 1583], aparelho=[113, 564, 970, 1176], largura=920, cor="Preenchimento de Cor 1 copiar",
                         aulas="aulas curriculares copiar 16", logo="logo - PPG Educação_branca copiar 18")}
# título de duas linhas (Trilha, Materiais): aparelho a 82% (topo e centro fixos), título de altura fixa, "aulas" e logo a ~81%.
# 1080x1920 medido na Trilha da Fitoterapia da equipe; 1000x1000 nas mesmas proporções (a equipe não tinha esse)
DUAS = {"1000x1000": dict(aparelho=[182, 85, 784, 515], titulo=[20, 560, 980, 713], aulas=[350, 755, 655, 826], logo=[424, 859, 576, 909]),
        "1080x1920": dict(aparelho=[187, 564, 896, 1070], titulo=[20, 1123, 1060, 1303], aulas=[366, 1352, 722, 1436], logo=[449, 1475, 628, 1534])}
NOME_NA_PILULA = [157, 161, 1171, 490]  # caixa do nome da pós dentro do objeto TITULO CURSO (1328x520)
FIT = """<script>document.fonts.ready.then(()=>{const cabe=e=>e.scrollWidth<=e.clientWidth+1&&e.scrollHeight<=e.clientHeight+1;
for(const e of document.querySelectorAll('[data-cabe]')){let t=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth+1&&t>24){t-=2;e.style.fontSize=t+'px'}}
for(const e of document.querySelectorAll('[data-enche]')){let t=parseFloat(getComputedStyle(e).fontSize);const f=e.style;f.display='block';f.overflow='hidden';
while(!cabe(e)&&t>24){t-=1;f.fontSize=t+'px'}f.display='';f.overflow=''}})</script>"""


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


def _foco(texto, padrao=None):
    """"50% 40%" -> (.5, .4): o ponto da foto que fica no recorte (sem texto: o padrão)"""
    return padrao if not texto and padrao else tuple(float(x.rstrip("%")) / 100 for x in str(texto or "50% 40%").split()[:2])


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
    """o número do módulo como no PSD da equipe (tela de 2255x1428): Montserrat Black sem preenchimento, contorno de 16 px por
    dentro da letra, o "1" de 198 a 1212 px de altura, centrado"""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
    w, h = tam
    esc = h / 1428
    fonte = ImageFont.truetype(acervo("fontes", "montserrat-variavel.ttf"), 1000)
    fonte.set_variation_by_name("Black")
    b = fonte.getbbox("1")
    fonte = ImageFont.truetype(acervo("fontes", "montserrat-variavel.ttf"), round(1000 * 1014 * esc / (b[3] - b[1])))
    fonte.set_variation_by_name("Black")
    solta = Image.new("L", (w * 2, h * 2))  # desenha, mede o que saiu e põe no lugar (a medida da fonte variável não bate com o desenho)
    ImageDraw.Draw(solta).text((w // 2, h // 2), str(n), font=fonte, fill=255)
    solta = solta.crop(solta.getbbox())
    letra = Image.new("L", tam)
    letra.paste(solta, (round(1127 * w / 2255 - solta.width / 2), round(198 * esc)))
    miolo = letra
    for _ in range(max(1, round(16 * esc / 2))):  # contorno por dentro: a letra menos ela mesma afinada 16 px
        miolo = miolo.filter(ImageFilter.MinFilter(5))
    return ImageChops.subtract(letra, miolo)


def aparelho(foto, numero, principal_vertical, foco):
    """notebook e celular do acervo com a foto (e o número) na tela do notebook e a capa principal na do celular"""
    import numpy as np
    from PIL import Image
    base = Image.open(acervo("eduq", "aparelho.png")).convert("RGBA")
    reflexo = Image.open(acervo("eduq", "aparelho-reflexo.png")).convert("RGBA")
    tela = cobrir(foto, TELA_NOTEBOOK, foco).convert("RGBA")
    # degradê preto da tela, com a curva do PSD da equipe (transparente até 1/6 da altura, preto a partir de 5/6)
    curva = np.interp(np.linspace(0, 1, TELA_NOTEBOOK[1]), [0, .167, .25, .333, .417, .5, .583, .667, .75, .833, 1],
                      [0, 1, 10, 29, 56, 90, 135, 188, 240, 255, 255])
    veu = Image.fromarray(np.repeat(curva.astype("uint8")[:, None], TELA_NOTEBOOK[0], 1), "L")
    tela = Image.composite(Image.new("RGBA", TELA_NOTEBOOK, (0, 0, 0, 255)), tela, veu)
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
.veu{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) ${veu0}%,rgba(0,0,0,.72) ${veu1}%,rgba(0,0,0,1) ${veu2}%)}
.bloco{position:absolute;left:0;right:0;display:flex;flex-direction:column;align-items:center;text-align:center}
.pilula{display:flex;align-items:center;justify-content:center;width:${pw}px;height:${ph}px;background:${pilula};color:#FFFFFF;font-weight:900;font-size:${p}px;letter-spacing:.03em;text-transform:uppercase}
.titulo{text-transform:uppercase}
.principal .titulo{font-weight:900;letter-spacing:-.05em;line-height:1.06;width:${tw}px;height:${th}px;display:flex;align-items:center;justify-content:center;
  -webkit-text-stroke:${traco}px rgba(20,20,20,.95);paint-order:stroke fill;text-shadow:0 ${sombra}px ${sombra}px rgba(0,0,0,.55)}
.individual .titulo{font-weight:800;line-height:1;width:${tw}px;white-space:nowrap}
.apoio{font-weight:500;text-transform:uppercase;line-height:1}
.logo{width:${logo}px}"""

# a capa principal: foto, pílula, nome da pós crescendo até encher a caixa do título (como no PSD) e o logo
PRINCIPAL = """<div class="principal"><div class="foto" data-sangra><img alt="foto" src="${foto}" style="object-position:${foco}"><div class="veu"></div></div>
<div class="bloco" style="top:${pt}px"><div class="pilula">Pós-Graduação</div></div>
<div class="bloco" style="top:${tt}px"><h1 class="titulo" data-enche style="font-size:${t}px">${titulo}</h1></div>
<div class="bloco" style="top:${lt}px"><img class="logo" alt="logo-sobre-foto" src="${logo_src}"></div></div>"""

INDIVIDUAL = """<div class="individual"><div class="foto" data-sangra style="background:${fundo}"><img alt="foto" src="${foto}" style="opacity:.5;mix-blend-mode:soft-light;object-position:${foco}"><div class="veu"></div></div>
<img alt="aparelho-sobre-foto" src="${aparelho}" style="position:absolute;left:${ax}px;top:${ay}px;width:${aw}px">
<div class="bloco" style="top:${tt}px"><h1 class="titulo" data-cabe style="font-size:${t}px">${titulo}</h1>
<p class="apoio" style="font-size:${a}px;margin-top:${g2}px">Aulas<br>curriculares</p><img class="logo" alt="logo-sobre-foto" src="${logo_src}" style="margin-top:${g3}px"></div></div>"""

# medidas tiradas dos PSDs da equipe (posição, tamanho e fonte de cada camada) e das capas publicadas
MEDIDAS = {"1080x1920": dict(principal=dict(t=110, pt=1250, pw=523, ph=63, p=39, tt=1330, tw=760, th=240, lt=1672, logo=190, traco=6, sombra=6,
                                            veu0=46, veu1=64, veu2=78),
                             individual=dict(t=116, tt=1150, tw=880, th=210, a=54, g2=39, g3=54, logo=221, ax=113, ay=564, aw=857,
                                             veu0=55, veu1=72, veu2=84)),
           "1000x1000": dict(principal=dict(t=100, pt=565, pw=502, ph=60, p=37, tt=630, tw=694, th=236, lt=895, logo=155, traco=5, sombra=5,
                                            veu0=34, veu1=56, veu2=80),
                             individual=dict(t=98, tt=587, tw=860, th=170, a=46, g2=34, g3=45, logo=189, ax=203, ay=121, aw=652,
                                             veu0=52, veu1=74, veu2=90))}


def pagina(tipo, tam, valores):
    import string
    w, h = map(int, tam.split("x"))
    _, lado, cima, baixo = arte.FORMATOS[TAMANHOS[tam]][1:]
    v = {"pw": 0, "ph": 0, "p": 0, "th": 0, "traco": 0, "sombra": 0, **MEDIDAS[tam][tipo], "w": w, "h": h,
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


def gerar(ficha, saida, pasta_ficha=".", codigo=False):
    """PSD da equipe pelo Photopea; fora do ar (ou codigo=True), o plano B em código"""
    _base(ficha, pasta_ficha)  # ficha errada (MBA, pós sem marca) para antes de abrir o Photopea
    if not codigo:
        try:
            with Sessao() as pp:
                return gerar_psd(pp, ficha, saida, pasta_ficha)
        except (Indisponivel, Travou) as e:
            print(f"aviso: Photopea fora ({e}); plano B: capas em código, sem PSD editável. Dizer isso na entrega.")
    return gerar_codigo(ficha, saida, pasta_ficha)


def _base(ficha, pasta_ficha):
    nome, marca = pos_da_ficha(ficha)
    if re.search(r"\bMBA\b", nome, re.I):
        raise SystemExit('"MBA" não entra na capa: o nome é da Pós-Graduação (marca.md)')
    foco = _foco(ficha.get("foco"))
    caminho = lambda f: str(f if Path(f).is_absolute() else Path(pasta_ficha) / f)
    principais = [dict(p, foto=caminho(p["foto"])) for p in (ficha.get("principais") or [{"nome": "", "foto": ficha["foto"]}])]
    return nome, marca, foco, caminho(ficha["foto"]), principais


def gerar_psd(pp, ficha, saida, pasta_ficha="."):
    """preenche os PSDs da equipe: foto, nome da pós (e a pílula azul na PPG), fundo, aparelho e título de cada capa"""
    from PIL import Image
    nome, marca, foco, foto, principais = _base(ficha, pasta_ficha)
    saida, ok, pngs = Path(saida), True, []
    (saida / "editaveis").mkdir(parents=True, exist_ok=True)
    modelo = lambda tipo, tam: acervo("eduq", "modelos", f"{tipo}-{tam}.psd")
    linhas = "\r".join(quebra(nome.upper(), 18))

    def fazer(arquivo, tipo, tam, ops, d):
        nonlocal ok
        png = saida / f"{arquivo} - {tam}.png"
        preencher(pp, modelo(tipo, tam), ops, {"png": png, "psd": saida / "editaveis" / f"{arquivo} - {tam}.psd"}, d)
        w, h = map(int, tam.split("x"))
        im = Image.open(png)
        if im.size != (w, h):  # a prancheta do PSD tem 1 px a mais
            im.crop((0, 0, w, h)).save(png, optimize=True)
        falhas = [] if Image.open(png).size == (w, h) else [f"tamanho {Image.open(png).size}"]
        registrar(png, not falhas, falhas)
        ok = ok and not falhas
        pngs.append(png)
        return png

    with tempfile.TemporaryDirectory() as d:
        vertical, fundo = None, {}
        for p in principais:
            arq = "CAPA PRINCIPAL" + (f" - {p['nome']}" if p.get("nome") else "")
            dentro = [{"texto_exceto": "pós-graduação", "valor": linhas, "caixa_texto": NOME_NA_PILULA}]
            if marca == "PPG":  # o modelo é da PPGVET (pílula verde): a pílula da PPG ganha a cor dela por cima
                dentro.append({"pintar": "Retângulo 3 copiar 5", "cor": COR["PPG"]["pilula"]})
            for tam in TAMANHOS:
                png = fazer(arq, "principal", tam, [{"imagem": "FOTO", "arquivo": p["foto"], "foco": _foco(p.get("foco"), foco)},
                                                    {"dentro": "TITULO CURSO", "caixa": PSD[tam]["titulo"], "ops": dentro}], d)
                if tam == "1080x1920":  # o celular dos módulos mostra a última capa principal (a equipe põe a #02)
                    vertical = Image.open(png).convert("RGB")
        for tam in TAMANHOS:  # o fundo das capas individuais: a foto sobre a cor da marca, uma vez por tamanho
            w, h = map(int, tam.split("x"))
            outra = (ficha.get("fundos") or {}).get(tam)
            ops = [{"imagem": "foto-fundo", "arquivo": str(Path(pasta_ficha) / outra) if outra and not Path(outra).is_absolute() else outra or foto, "foco": foco}]
            if marca == "PPG":
                ops.append({"imagem": PSD[tam]["cor"], "arquivo": solido(COR["PPG"]["fundo"], Path(d) / "cor.png"), "inteira": True, "caixa": [0, 0, w, h]})
            fundo[tam] = Path(d) / f"fundo-{tam}.png"
            preencher(pp, modelo("fundo", tam), ops, {"png": fundo[tam]}, d)
        for arq, titulo, numero in pecas(ficha):
            ap = Path(d) / f"aparelho-{numero}.png"
            aparelho(abrir_foto(foto), numero, vertical, foco).save(ap)
            for tam in TAMANHOS:
                w, h = map(int, tam.split("x"))
                duas, cx = len(titulo) > 14, DUAS[tam]
                ops = [{"imagem": "FUNDO", "arquivo": str(fundo[tam]), "inteira": True, "caixa": [0, 0, w, h]},
                       {"imagem": "NOTEBOOK E CELULAR", "arquivo": str(ap), "inteira": True, "caixa": cx["aparelho"] if duas else PSD[tam]["aparelho"]}]
                if duas:  # como a equipe faz no título longo
                    ops += [{"texto": "Módulo I", "valor": "\r".join(duas_linhas(titulo.upper()))},
                            {"encaixar": "Módulo I", "caixa": cx["titulo"], "ancora": "baixo"},
                            {"encaixar": PSD[tam]["aulas"], "caixa": cx["aulas"]}, {"encaixar": PSD[tam]["logo"], "caixa": cx["logo"]}]
                else:
                    ops.append({"texto": "Módulo I", "valor": titulo.upper(), "largura": PSD[tam]["largura"]})
                fazer(arq, "modulo", tam, ops, d)
    folha(pngs, saida.parent / f"{saida.name}-folha.jpg")
    print("folha:", saida.parent / f"{saida.name}-folha.jpg")
    return ok


def gerar_codigo(ficha, saida, pasta_ficha="."):
    from PIL import Image
    nome, marca = pos_da_ficha(ficha)
    if re.search(r"\bMBA\b", nome, re.I):
        raise SystemExit('"MBA" não entra na capa: o nome é da Pós-Graduação (marca.md)')
    foco = _foco(ficha.get("foco"))
    abre = lambda f: abrir_foto(f if Path(f).is_absolute() else Path(pasta_ficha) / f)
    foto = abre(ficha["foto"])
    principais = ficha.get("principais") or [{"nome": "", "foto": ficha["foto"]}]
    saida, ok, pngs = Path(saida), True, []
    saida.mkdir(parents=True, exist_ok=True)
    comum = dict(COR[marca], pilula=COR[marca].get("pilula_codigo", COR[marca]["pilula"]), foco=H.escape(str(ficha.get("foco", "50% 40%"))))

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
                png = fazer(arq, "principal", tam, dict(foto=uri(cobrir(im, (w, h), _foco(p.get("foco"), foco)), "JPEG"), titulo=H.escape(nome)), d)
                if tam == "1080x1920":  # o celular mostra a última capa principal
                    vertical = Image.open(png)
        for arq, titulo, numero in pecas(ficha):
            ap = uri(aparelho(foto, numero, vertical, foco))
            for tam in TAMANHOS:
                w, h = map(int, tam.split("x"))
                m, extra = MEDIDAS[tam]["individual"], {}
                if len(titulo) > 14:  # título longo: duas linhas que crescem para cima, e o aparelho encolhe (topo e centro fixos), como no PSD
                    alto = m["aw"] / 1.4  # proporção do aparelho.png
                    aw = m["aw"] * (alto - m["t"]) / alto
                    extra = dict(tt=m["tt"] - m["t"], aw=round(aw), ax=round(m["ax"] + (m["aw"] - aw) / 2))
                    texto = "<br>".join(H.escape(x) for x in duas_linhas(titulo))
                else:
                    texto = H.escape(titulo)
                fazer(arq, "individual", tam, dict(foto=uri(cobrir(foto, (w, h), foco), "JPEG"), aparelho=ap, titulo=texto, **extra), d)
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
    assert _foco("80% 30%") == (.8, .3) and _foco(None, (.5, .45)) == (.5, .45) and _foco(None) == (.5, .4)
    assert pasta_da_pos("Piscicultura e Produção de Tilápia") == "PISCICULTURA_E_PRODUÇÃO_DE_TILÁPIA"
    for c in COR.values():  # pílula da equipe (a da PPG dá 4,0:1): passa como letra grande em negrito
        assert contraste("#FFFFFF", c["pilula"]) >= 3, c
        assert contraste("#FFFFFF", c.get("pilula_codigo", c["pilula"])) >= 4.5  # o plano B passa no arte.py
    m = numero_contorno(1, TELA_NOTEBOOK)
    caixa = m.getbbox()
    assert abs(caixa[1] - 198) <= 3 and abs(caixa[3] - 1212) <= 3 and abs((caixa[0] + caixa[2]) / 2 - 1127) <= 6, caixa  # como no PSD
    assert m.getpixel(((caixa[0] + caixa[2]) // 2 + 60, 900)) == 0  # só o contorno: o miolo do número fica vazio
    with tempfile.TemporaryDirectory() as d:
        foto = Image.new("RGB", (1800, 1200), (70, 95, 60))
        ImageDraw.Draw(foto).rectangle((0, 0, 1800, 400), fill=(220, 228, 232))  # céu claro: o véu tem que segurar a letra
        foto.save(f"{d}/tema.jpg")
        ficha = {"pos": "Medicina Felina", "marca": "PPG", "foto": "tema.jpg", "modulos": 1}
        esperado = sorted(f"{a} - {t}.png" for a in ("CAPA PRINCIPAL", "ABERTURA", "MODULO 1", "MATERIAIS COMPLEMENTARES") for t in TAMANHOS)
        assert gerar(ficha, f"{d}/B", d, codigo=True), "capa limpa não pode reprovar (plano B)"
        assert sorted(p.name for p in Path(d, "B").glob("*.png")) == esperado
        from comum import igual_referencia
        for peca in ("CAPA PRINCIPAL", "MODULO 1", "MATERIAIS COMPLEMENTARES"):  # o visual não mudou sem querer (cor, posição)
            igual_referencia(f"{d}/B/{peca} - 1000x1000.png", f"eduq-codigo-{peca.split()[0].lower()}")
        assert gerar(ficha, f"{d}/P", d)  # PSD da equipe; com o Photopea fora, cai sozinho no plano B
        assert sorted(p.name for p in Path(d, "P").glob("*.png")) == esperado
        assert Image.open(f"{d}/P/MODULO 1 - 1000x1000.png").size == (1000, 1000)
        if Path(d, "P", "editaveis").exists():
            assert sorted(p.stem for p in Path(d, "P", "editaveis").glob("*.psd")) == [n[:-4] for n in esperado]
            import numpy as np
            pilula = np.asarray(Image.open(f"{d}/P/CAPA PRINCIPAL - 1000x1000.png").convert("RGB").crop((250, 570, 750, 610))).astype(int)
            assert ((pilula[..., 2] > 150) & (pilula[..., 0] < 80)).sum() > 2000, "pílula azul na pós da PPG"
            for peca in ("CAPA PRINCIPAL", "MODULO 1", "MATERIAIS COMPLEMENTARES"):
                igual_referencia(f"{d}/P/{peca} - 1000x1000.png", f"eduq-psd-{peca.split()[0].lower()}")
            print("PSD ok", end=" ")
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
        sys.exit(0 if gerar(ficha, saida, Path(a[0]).parent, "--codigo" in a) else 1)
    else:
        sys.exit(__doc__)
