#!/usr/bin/env python3
"""Peça a partir de um molde da casa (acervo/moldes): preenche, gera PNG e JPEG e confere cada uma com o arte.py.
uso: molde.py ficha.json [--saida <pasta>]   (sem --saida: <artes>/<nome da ficha sem .json>/)
     molde.py --teste
ficha.json: {"pos": "NGB", "marca": "PPGVET" (opcional: sai da pós), "ano": 2026 (opcional),
             "pecas": [{"molde": "kv", "formato": "feed" (opcional), "foto": "<arquivo>", "foco": "50% 40%" (opcional), ...}]}
Texto entre [colchetes] vira ênfase: negrito no título em peso misto (kv, story), cor da marca no título forte; **x** no texto vira negrito.
Moldes, campos (os entre parênteses são opcionais) e formato padrão:
  kv                  foto, rotulo, titulo                              feed (o mesmo do anúncio no feed)
  professor           professor ("Dra. Nome"), cargo, rotulo, (cta, foto: sem ela, acervo/professores)   feed
  carrossel-capa      foto, titulo, apoio                               carrossel
  carrossel-conteudo  titulo, texto, (foto, seta: "" na última de conteúdo)   carrossel
  carrossel-cta       titulo, apoio, cta                                carrossel
  story               foto, rotulo, data ("23/11"), titulo, apoio, (cta)       story ou story-anuncio
  thumb               foto, rotulo, titulo                              youtube
Nunca inventa texto: campo obrigatório vazio para antes de gerar."""
import base64, datetime as dt, html as H, io, json, os, re, string, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo, pasta  # noqa: E402
from aulas_semana import DIAS, achar_foto, contraste, letra_sobre, pos_tabela, titulo_e_nome  # noqa: E402
import arte  # noqa: E402

MOLDES = {"kv": (("foto", "rotulo", "titulo"), "feed"),
          "professor": (("professor", "cargo", "rotulo"), "feed"),
          "carrossel-capa": (("foto", "titulo", "apoio"), "carrossel"),
          "carrossel-conteudo": (("titulo", "texto"), "carrossel"),
          "carrossel-cta": (("titulo", "apoio", "cta"), "carrossel"),
          "story": (("foto", "rotulo", "data", "titulo", "apoio"), "story"),
          "thumb": (("foto", "rotulo", "titulo"), "youtube")}
CLARO, ESCURO, BRANCO = "#FAF9FB", "#1A1A1A", "#FFFFFF"
MARCAS = {"PPGVET": dict(marca="#D24BA8", acao="#00B7AB", faixa="#B84482", tom="claro",  # Jaleco Branco (marca.md)
                         logo="logos/ppgvet/logo-ppgvet.png", logo_branco="logos/ppgvet/logo-ppgvet-branco.png"),
          "PPG": dict(marca="#1670C2", acao="#00ADA3", faixa="#1670C2", tom="escuro",  # Terno Escuro
                      logo="logos/ppg/logo-ppg-educacao.png", logo_branco="logos/ppg/logo-ppg-educacao-branco.png")}
ESCURAS = ("story", "thumb", "carrossel-capa")  # foto de fundo com véu: letra branca nas duas marcas
MESES = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()
MOLDES_DIR = Path(acervo("moldes"))


def enfase(t, titulo=True):
    """escapa o HTML e marca a ênfase: [x] no título, **x** no texto"""
    t = H.escape(t.strip())
    return re.sub(r"\[([^\]]+)\]", r"<b>\1</b>", t) if titulo else re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def tokens(marca, cor_pos):
    """cores do molde, todas do marca.md; texto colorido só onde o contraste passa (4,5:1 pequeno, 3:1 grande)"""
    m = MARCAS[marca]
    le = lambda cor, fundo, minimo, senao: cor if contraste(cor, fundo) >= minimo else senao
    return dict(marca=m["marca"], acao=m["acao"], faixa=m["faixa"], pos=cor_pos, sobre_pos=letra_sobre(cor_pos),
                claro=CLARO, escuro=ESCURO, pos_texto_claro=le(cor_pos, CLARO, 4.5, ESCURO),
                pos_texto_escuro=le(cor_pos, ESCURO, 4.5, BRANCO), destaque_claro=le(m["marca"], CLARO, 3, ESCURO),
                destaque_escuro=le(m["marca"], ESCURO, 3, BRANCO))


def foto_uri(arq, pessoa=False, maximo=1920):
    """foto embutida no HTML (JPEG); retrato em fundo branco (acervo/professores) é cortado em volta da pessoa"""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(arq)).convert("RGB")
    if pessoa:
        cinza = im.convert("L")
        cantos = [cinza.getpixel((x, y)) for x in (2, im.width - 3) for y in (2, im.height - 3)]
        if min(cantos) > 240:  # fundo branco: corta a sobra dos lados e de cima
            x0, y0, x1, y1 = cinza.point(lambda v: 255 if v < 232 else 0).getbbox() or (0, 0, im.width, im.height)
            mx, mt = (x1 - x0) * .22, (y1 - y0) * .06
            im = im.crop((max(0, int(x0 - mx)), max(0, int(y0 - mt)), min(im.width, int(x1 + mx)), im.height))
    if min(im.size) > maximo:  # o lado menor manda: a foto cobre 9:16 e 16:9 sem esticar
        im = im.resize((round(im.width * maximo / min(im.size)), round(im.height * maximo / min(im.size))))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def lockup(nome):
    return (f'<div class="lockup" data-bloco><div class="lk-pg"><span class="lk-pos">PÓS</span><span class="lk-grad">GRADUAÇÃO</span></div>'
            f'<i class="lk-fio"></i><div class="lk-nome">{H.escape(nome)}</div></div>')


def montar(p, ficha, tab):
    """(html, formato, erros, avisos) de uma peça"""
    molde, erros, avisos = p.get("molde"), [], []
    if molde not in MOLDES:
        return None, None, [f'molde "{molde}": use {", ".join(MOLDES)}'], []
    sigla = str(ficha.get("pos", "")).upper()
    if sigla not in tab:
        return None, None, [f'pós "{sigla}": sigla da tabela do regras/marca.md'], []
    nome_pos, marca_pos, cor_pos = tab[sigla]
    marca = str(ficha.get("marca") or marca_pos).upper()
    if marca not in MARCAS:
        return None, None, [f'marca "{marca}": PPGVET ou PPG'], []
    obrig, formato = MOLDES[molde]
    formato = p.get("formato", formato)
    erros += [f"{molde}: falta {c}" for c in obrig if not str(p.get(c, "")).strip()]
    if formato not in arte.FORMATOS:
        erros.append(f'{molde}: formato "{formato}" não existe no arte.py')
    if erros:
        return None, None, erros, avisos
    m = MARCAS[marca]
    tom = "escuro" if molde in ESCURAS else m["tom"]
    if molde == "carrossel-cta":  # a última lâmina inverte o tom e fecha o ritmo
        tom = "claro" if m["tom"] == "escuro" else "escuro"
    w, h, lado, cima, baixo = arte.FORMATOS[formato]
    v = dict(tokens(marca, cor_pos), w=w, h=h, lado=max(lado, int(80 * w / 1080)), cima=max(cima, 72), baixo=max(baixo, 72),
             fonte=Path(acervo("fontes", "montserrat-variavel.ttf")).as_uri(), tom=tom, formato=formato,
             logo=Path(acervo(m["logo_branco"] if tom == "escuro" else m["logo"])).as_uri(),
             logo_branco=Path(acervo(m["logo_branco"])).as_uri(), lockup=lockup(nome_pos), foco=H.escape(p.get("foco", "50% 40%")),
             cta=f'<span class="cta" data-caixa>{H.escape(p["cta"])}</span>' if p.get("cta") else "")
    for c in ("rotulo", "apoio", "cargo"):
        v[c] = enfase(p.get(c, ""), titulo=False)
    v["titulo"], v["texto"] = enfase(p.get("titulo", "")), enfase(p.get("texto", ""), titulo=False)
    v["seta"] = H.escape(p.get("seta", "Arrasta para o lado →"))
    if molde == "professor":
        tit, nome, aviso = titulo_e_nome(p["professor"])
        avisos += [aviso] if aviso else []
        v["nome"] = (f'<span class="tit">{tit}</span>' if tit else "") + H.escape(nome)
        foto = p.get("foto")
        if not foto:
            foto, grafia = achar_foto(nome, acervo("professores"))
            avisos += [grafia] if grafia else []
        if not foto:
            return None, None, [f'professor: sem foto real de "{nome}" (mande a foto; nunca banco nem IA)'], avisos
        p = dict(p, foto=str(foto))
        v["foco"] = H.escape(p.get("foco", "50% 0%"))
    if molde == "story":
        try:
            d, mes = (int(x) for x in p["data"].split("/")[:2])
            hoje = dt.date.today()  # sem "ano": data que já passou há mais de um mês é do ano que vem
            ano = int(ficha.get("ano") or (hoje.year + (dt.date(hoje.year, mes, d) < hoje - dt.timedelta(days=31))))
            semana = DIAS[dt.date(ano, mes, d).weekday()]
        except (ValueError, IndexError):
            return None, None, [f'story: data "{p["data"]}" (dd/mm)'], avisos
        v["dia"], v["mes"] = f"{d:02d}", MESES[mes - 1]
        citado = next((x for x in DIAS if re.search(rf"(?i)\b{x}(?=-feira|\s*,|\s+(?:às|as|dia)\b|\s*\d|\s*$|\s*[.·|])", p["apoio"])), None)
        if citado and citado != semana:
            erros.append(f'story: {p["data"]}/{ano} é {semana}, mas o apoio diz "{citado}"')
    if p.get("foto"):
        if not Path(p["foto"]).exists():
            return None, None, [f'{molde}: foto não encontrada: {p["foto"]}'], avisos
        v["foto"] = foto_uri(p["foto"], pessoa=molde == "professor", maximo=round(h * arte.ESCALA.get(formato, 1)))
    v["com_foto"], v["foto_html"] = ("com-foto", f'<div class="foto" data-sangra><img alt="foto" src="{v["foto"]}" '
                                     f'style="object-position:{v["foco"]}"><div class="veu"></div></div>') if molde == "carrossel-conteudo" and p.get("foto") else ("", "")
    css = string.Template((MOLDES_DIR / "base.css").read_text(encoding="utf-8")).substitute(v)
    corpo = string.Template((MOLDES_DIR / f"{molde}.html").read_text(encoding="utf-8")).safe_substitute(v)
    return f"<!doctype html><meta charset=utf-8><style>{css}</style><body>{corpo}</body>", formato, erros, avisos


def folha(pngs, saida, alto=520):
    """as peças lado a lado na mesma altura, sem deformar (carrossel: ritmo e grid; revisor: tudo de uma vez)"""
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims = [im.resize((round(im.width * alto / im.height), alto)) for im in ims]
    linhas, linha, larg = [], [], 0
    for im in ims:  # linhas de até ~2400 px
        if linha and larg + im.width > 2400:
            linhas.append(linha)
            linha, larg = [], 0
        linha.append(im)
        larg += im.width + 12
    linhas.append(linha)
    f = Image.new("RGB", (max(sum(i.width + 12 for i in l) for l in linhas), len(linhas) * (alto + 12)), "white")
    for j, l in enumerate(linhas):
        x = 0
        for im in l:
            f.paste(im, (x, j * (alto + 12)))
            x += im.width + 12
    f.save(saida, quality=85)


def gerar(ficha, saida, pasta_ficha="."):
    tab, ok, pngs = pos_tabela(), True, []
    for p in ficha["pecas"]:  # foto com caminho relativo é da pasta da ficha
        if p.get("foto") and not Path(p["foto"]).is_absolute():
            p["foto"] = str(Path(pasta_ficha) / p["foto"])
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(ficha["pecas"], 1):
        doc, formato, erros, avisos = montar(p, ficha, tab)
        for a in avisos:
            print("AVISO:", a)
        if erros:
            for e in erros:
                print("ERRO:", e)
            ok = False
            continue
        nome = saida / f"{i:02d}-{p['molde']}"
        nome.with_suffix(".html").write_text(doc, encoding="utf-8")
        ok = arte.main(str(nome.with_suffix(".html")), formato, str(nome.with_suffix(".png"))) and ok
        pngs.append(nome.with_suffix(".png"))
    if len(pngs) > 1:
        folha(pngs, saida / "folha.jpg")
        print("folha:", saida / "folha.jpg")
    return ok


def teste():
    import tempfile, portao
    portao.REGISTRO = Path(tempfile.mkdtemp()) / "conferencias.jsonl"  # o teste não suja o registro de verdade
    tab = pos_tabela()
    assert "PPGVET ou PPG" in montar({"molde": "kv"}, {"pos": "NGB", "marca": "Escola"}, tab)[2][0]
    t = tokens("PPGVET", tab["SA"][2])  # vermelho da SA não lê em letra pequena no fundo claro
    assert t["pos_texto_claro"] == ESCURO and t["pos_texto_escuro"] == tab["SA"][2]
    assert tokens("PPGVET", tab["CMCB"][2])["pos_texto_claro"] == tab["CMCB"][2]
    assert enfase("[Formule] dietas <já>") == "<b>Formule</b> dietas &lt;já&gt;"
    assert enfase("é **prática** [x]", titulo=False) == "é <b>prática</b> [x]"
    assert montar({"molde": "kv", "rotulo": "x", "titulo": "y"}, {"pos": "NGB"}, tab)[2] == ["kv: falta foto"]
    assert "sigla" in montar({"molde": "kv"}, {"pos": "XYZ"}, tab)[2][0]
    from PIL import Image
    with tempfile.TemporaryDirectory() as d:
        Image.new("RGB", (1600, 1200), (90, 110, 80)).save(f"{d}/f.jpg")
        _, _, e, _ = montar({"molde": "story", "foto": f"{d}/f.jpg", "rotulo": "a", "data": "26/11", "titulo": "t",
                             "apoio": "Sexta, 19h"}, {"pos": "NGB", "ano": 2026}, tab)
        assert e and "quinta" in e[0], e  # 26/11/2026 é quinta
        _, _, e, _ = montar({"molde": "story", "foto": f"{d}/f.jpg", "rotulo": "a", "data": "27/11", "titulo": "t",
                             "apoio": "Segunda turma, sexta às 19h"}, {"pos": "NGB", "ano": 2026}, tab)
        assert not e, e  # "segunda turma" não é dia da semana
        im = Image.new("RGB", (1920, 1080), (255, 255, 255))
        im.paste((40, 60, 80), (800, 200, 1100, 1080))
        im.save(f"{d}/p.jpg")
        from PIL import Image as I
        cortada = I.open(io.BytesIO(base64.b64decode(foto_uri(f"{d}/p.jpg", pessoa=True).split(",")[1])))
        assert cortada.width < 700, cortada.size  # sobrou só a pessoa e uma margem
        from PIL import ImageDraw
        foto = Image.new("RGB", (2400, 1600), (70, 90, 60))
        ImageDraw.Draw(foto).rectangle((0, 0, 2400, 500), fill=(225, 230, 235))  # céu claro: o véu tem que segurar o texto
        foto.save(f"{d}/campo.jpg")
        ficha = {"pos": "NGB", "pecas": [
            {"molde": "kv", "foto": "campo.jpg", "rotulo": "Nova turma", "titulo": "[Formule dietas] no campo."},
            {"molde": "carrossel-conteudo", "titulo": "Uma ideia [só]", "texto": "Texto com **trecho-chave** curto."},
            {"molde": "carrossel-cta", "titulo": "Fale com um [especialista]", "apoio": "Tire suas dúvidas.", "cta": "Falar com um especialista"}]}
        assert gerar(ficha, f"{d}/out", d), "o molde limpo não pode reprovar"
        assert Path(d, "out", "folha.jpg").exists() and Path(d, "out", "01-kv.jpg").exists() and Path(d, "out", "02-carrossel-conteudo.jpg").exists()
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a and a[0].endswith(".json"):
        ficha = json.loads(Path(a[0]).read_text(encoding="utf-8"))
        saida = a[a.index("--saida") + 1] if "--saida" in a else str(Path(pasta("artes")) / Path(a[0]).stem)
        sys.exit(0 if gerar(ficha, saida, Path(a[0]).parent) else 1)
    else:
        sys.exit(__doc__)
