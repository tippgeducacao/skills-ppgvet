#!/usr/bin/env python3
"""Preenche um PSD da equipe (o visual é o deles) trocando o conteúdo de camadas, e devolve PNG e PSD editável.
Motor: Photopea sem janela (scripts/photopea.py). Sem ele (Indisponivel, Travou), quem chama usa o plano B.
uso (Python):
    from psd import preencher
    preencher(pp, "modelo.psd", [
        {"imagem": "FOTO", "arquivo": "foto.jpg", "foco": (.5, .4)},  # entra no lugar e no tamanho da camada (cobre e corta)
        {"texto": "Módulo I", "valor": "Módulo XIII", "largura": 880, "sobe": ["NOTEBOOK"]},  # 2 linhas: cresce para cima
        {"dentro": "TITULO CURSO", "caixa": [61, 540, 940, 884],      # objeto inteligente: edita dentro e volta editável
         "ops": [{"texto_exceto": "pós-graduação", "valor": "MEDICINA\\rFELINA", "caixa_texto": [157, 161, 1171, 490]},
                 {"pintar": "Retângulo 3 copiar 5", "cor": "#0072D6"}]},  # camada de cor por cima da caixa da camada
        {"esconder": "Camada 1"}], {"png": "saida.png", "psd": "saida.psd"})
    psd.py --teste
Camada que não existe para antes de mexer (no Photopea, erro de script trava a sessão inteira)."""
import base64, io, json, os, sys, tempfile, time, unicodedata
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from photopea import Indisponivel, Sessao, Travou  # noqa: E402,F401

JS_CAMADAS = """var o=[];function lista(c,n){for(var k=0;k<c.layers.length;k++){var l=c.layers[k];
o.push({nome:l.name,texto:l.kind==LayerKind.TEXT?l.textItem.contents:null,caixa:caixa(l),grupo:l.typename=="LayerSet"});
if(l.typename=="LayerSet")lista(l);}}lista(app.activeDocument);app.echoToOE(JSON.stringify(o));"""


def js(v):
    return json.dumps(v, ensure_ascii=False)


def camadas(pp):
    """nomes em NFC: o PSD do Mac grava "ç" decomposto"""
    return [dict(c, nome=unicodedata.normalize("NFC", c["nome"])) for c in json.loads(pp.script(JS_CAMADAS) or "[]")]


def _alvos(o):
    nomes = ([] if "texto_exceto" in o else [o.get("imagem") or o.get("texto") or o.get("dentro") or o.get("esconder") or o.get("pintar")])
    return [unicodedata.normalize("NFC", n) for n in nomes + o.get("sobe", []) if n]


def _falta(ops, lista):
    nomes = {c["nome"] for c in lista}
    return [n for o in ops for n in _alvos(o) if n not in nomes]


def abrir_dentro(pp, nome, tentativas=90):
    """abre o objeto inteligente `nome` como documento. No Photopea a abertura é assíncrona (o "done" vem antes):
    espera o documento novo existir"""
    antes = int(pp.script("app.echoToOE(app.documents.length)"))
    pp.script(f"app.activeDocument.activeLayer=camada({js(nome)});")
    pp._passo({"js": 'executeAction(stringIDToTypeID("placedLayerEditContents"), new ActionDescriptor(), DialogModes.NO);'})
    try:  # o "done" extra de quando o objeto termina de abrir; sem consumir, todos os passos seguintes desencontram
        pp._espera(tentativas, "o objeto inteligente não abriu", Travou)
    except Travou:
        pass
    if int(pp.script("app.echoToOE(app.documents.length)")) <= antes:
        raise Travou(f"o objeto inteligente {nome} não abriu")


def recorte(arquivo, caixa, destino, foco=(.5, .5)):
    """corta a foto na proporção da caixa (cobre, sem sobrar fora da caixa; `foco` diz o que fica) e grava JPEG"""
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(arquivo)).convert("RGB")
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    alvo = w / h
    if im.width / im.height > alvo:
        nw = round(im.height * alvo)
        x = round((im.width - nw) * foco[0])
        im = im.crop((x, 0, x + nw, im.height))
    else:
        nh = round(im.width / alvo)
        y = round((im.height - nh) * foco[1])
        im = im.crop((0, y, im.width, y + nh))
    im.save(destino, "JPEG", quality=92)
    return destino


def quebra(texto, maximo):
    """quebra em linhas de até `maximo` caracteres, como a equipe quebra o nome da pós ("...PLANTAS / MEDICINAIS")"""
    linhas, atual = [], ""
    for p in texto.split():
        if atual and len(atual) + 1 + len(p) > maximo:
            linhas.append(atual)
            atual = p
        else:
            atual = (atual + " " + p).strip()
    linhas.append(atual)
    for i in range(len(linhas) - 1):  # linha não termina em "e", "a", "o": a palavra de uma letra desce (como a equipe faz)
        p = linhas[i].split()
        if len(p) > 1 and len(p[-1]) == 1:
            linhas[i], linhas[i + 1] = " ".join(p[:-1]), p[-1] + " " + linhas[i + 1]
    return linhas


def duas_linhas(texto):
    """quebra em duas linhas de tamanho parecido ("TRILHA INICIAL / DE APRENDIZADO"), como a equipe faz no título longo"""
    p = texto.split()
    meio = min(range(1, len(p)), key=lambda i: abs(len(" ".join(p[:i])) - len(" ".join(p[i:]))))
    return [" ".join(p[:meio]), " ".join(p[meio:])]


def _imagem(pp, alvo, arquivo, caixa=None, trocar=True):
    """a imagem entra no documento ativo no lugar da camada `alvo` (mesma posição na pilha, mesma caixa, opacidade e modo);
    trocar=False: entra logo acima dela, sem apagar. O Photopea converte a cor da imagem para o perfil do PSD"""
    pp.abrir(arquivo)
    cx = js(caixa) if caixa else "null"
    pp.script(f"""var img=app.activeDocument, dst=app.documents[app.documents.length-2];
img.activeLayer.duplicate(dst, ElementPlacement.PLACEATBEGINNING); img.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument=dst; var L=dst.activeLayer, A=camada({js(alvo)}), cx={cx}||caixa(A);
var b=caixa(L), W=cx[2]-cx[0], H=cx[3]-cx[1]; L.resize(W/(b[2]-b[0])*100, H/(b[3]-b[1])*100);
b=caixa(L); L.translate(cx[0]-b[0], cx[1]-b[1]); L.move(A, ElementPlacement.PLACEBEFORE);
""" + ("L.opacity=A.opacity; L.blendMode=A.blendMode; var nome=A.name; A.remove(); L.name=nome;" if trocar else 'L.name=A.name+" cor";'))


# dois cantos da tela com 1% de opacidade: o Photopea mede o objeto ora pela tela, ora pelo que aparece; assim dá o mesmo
JS_LIMITE = """var d=app.activeDocument, L=d.artLayers.add(); L.name="limite (não apagar)"; L.move(d.layers[0], ElementPlacement.PLACEBEFORE);
var W=px(d.width), H=px(d.height), c=new SolidColor(); c.rgb.hexValue="000000";
d.selection.select([[0,0],[1,0],[1,1],[0,1]]); d.selection.fill(c, ColorBlendMode.NORMAL, 1);
d.selection.select([[W-1,H-1],[W,H-1],[W,H],[W-1,H]]); d.selection.fill(c, ColorBlendMode.NORMAL, 1); d.selection.deselect();"""


def _objeto(pp, alvo, psd, caixa):
    """o PSD editado (com JS_LIMITE) entra como objeto inteligente novo no lugar da camada `alvo`, a tela dele na `caixa`"""
    n = len(camadas(pp))
    pp.script("app.open(" + js("data:application/octet-stream;base64," + base64.b64encode(psd).decode()) + ", null, true);")
    for _ in range(100):  # a entrada é assíncrona
        if len(camadas(pp)) > n:
            break
        time.sleep(.2)
    else:
        raise Travou(f"o objeto novo de {alvo} não entrou")
    pp.script(f"""var L=app.activeDocument.activeLayer, A=camada({js(alvo)}), b=caixa(L), c={js(caixa)};
L.resize((c[2]-c[0])/(b[2]-b[0])*100, (c[3]-c[1])/(b[3]-b[1])*100); b=caixa(L); L.translate(c[0]-b[0], c[1]-b[1]);
L.move(A, ElementPlacement.PLACEBEFORE); L.opacity=A.opacity; L.blendMode=A.blendMode; var nome=A.name; A.remove(); L.name=nome;""")


def solido(cor, destino):
    """PNG de uma cor só (cor da marca em sRGB): entra como imagem para o Photopea converter ao perfil do PSD"""
    from PIL import Image
    Image.new("RGB", (8, 8), cor).save(destino)
    return str(destino)


def srgb(png):
    """o PSD da equipe é Adobe RGB e o Photopea exporta nesse perfil; o Eduq e o navegador esperam sRGB (como o Photoshop exporta)"""
    from PIL import Image, ImageCms
    im = Image.open(io.BytesIO(png))
    if im.info.get("icc_profile"):
        perfil = ImageCms.ImageCmsProfile(io.BytesIO(im.info["icc_profile"]))
        im = ImageCms.profileToProfile(im.convert("RGBA" if "A" in im.getbands() else "RGB"), perfil, ImageCms.createProfile("sRGB"))
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return b.getvalue()


def _sub(pp, sub, lista, d):
    if "texto" in sub or "texto_exceto" in sub:
        _texto(pp, sub, lista)
    elif "pintar" in sub:  # camada de cor na caixa da camada, logo acima dela (o que estiver por cima, como textura, continua)
        caixa = next(c["caixa"] for c in lista if c["nome"] == unicodedata.normalize("NFC", sub["pintar"]))
        _imagem(pp, sub["pintar"], solido(sub["cor"], Path(d) / f"cor-{sub['cor'].lstrip('#')}.png"), caixa, trocar=False)
    else:
        pp.script(f"camada({js(sub['esconder'])}).visible=false;")


def _texto(pp, op, lista):
    """troca o texto; largo demais quebra em duas linhas. Com "sobe", o texto cresce para cima (o de baixo fica no lugar) e as
    camadas de cima encolhem, com topo e centro fixos, para dar o espaço (como a equipe faz na capa de título longo)"""
    nome = op.get("texto")
    if "texto_exceto" in op:
        nome = next(c["nome"] for c in lista if c["texto"] is not None and op["texto_exceto"].lower() not in c["texto"].lower())
    valor = op["valor"]
    saida = pp.script(f"""var t=camada({js(nome)}), a=caixa(t); t.textItem.contents={js(valor)}; var b=caixa(t);
app.echoToOE(JSON.stringify([a,b]));""")
    antes, depois = json.loads(saida)
    if op.get("largura") and depois[2] - depois[0] > op["largura"] and " " in valor and "\r" not in valor:
        valor = "\r".join(duas_linhas(valor))
        depois = json.loads(pp.script(f"var t=camada({js(nome)}); t.textItem.contents={js(valor)}; app.echoToOE(JSON.stringify(caixa(t)));"))
        if depois[2] - depois[0] > op["largura"]:  # duas linhas ainda largas: diminui a letra até caber
            depois = json.loads(pp.script(f"""var t=camada({js(nome)}), b=caixa(t); t.textItem.size=t.textItem.size*{op['largura']}/(b[2]-b[0]);
app.echoToOE(JSON.stringify(caixa(t)));"""))
    if op.get("caixa_texto"):  # encher a caixa (como o nome da pós no título), mantendo o topo
        cx = op["caixa_texto"]
        pp.script(f"""var t=camada({js(nome)}), b=caixa(t), cx={js(cx)};
var f=Math.min((cx[2]-cx[0])/(b[2]-b[0]), (cx[3]-cx[1])/(b[3]-b[1])); t.textItem.size=t.textItem.size*f;
b=caixa(t); t.translate((cx[0]+cx[2])/2-(b[0]+b[2])/2, cx[1]-b[1]);""")
    dy = (depois[3] - depois[1]) - (antes[3] - antes[1])
    if dy > 0 and op.get("sobe"):
        pp.script(f"camada({js(nome)}).translate(0,{antes[3] - depois[3]});")  # o pé do texto fica onde estava
        for outra in op["sobe"]:
            pp.script(f"""var L=camada({js(outra)}), a=caixa(L), f=(a[3]-a[1]-{dy})/(a[3]-a[1]); L.resize(f*100, f*100);
var b=caixa(L); L.translate((a[0]+a[2])/2-(b[0]+b[2])/2, a[1]-b[1]);""")
    so = lambda t: " ".join(unicodedata.normalize("NFC", t or "").split()).lower()
    if so(next((c["texto"] for c in lista if c["nome"] == unicodedata.normalize("NFC", nome)), "")) == so(nome):
        pp.script(f"camada({js(nome)}).name={js(' '.join(valor.split()))};")  # como no Photoshop: a camada com o nome do texto segue o texto


def preencher(pp, modelo, ops, saidas, pasta_trabalho=None):
    """aplica as operações no modelo e grava as saídas ({"png": caminho, "psd": caminho}); devolve a lista de camadas"""
    d = Path(pasta_trabalho or tempfile.mkdtemp())
    pp.abrir(modelo)
    lista = camadas(pp)
    falta = _falta(ops, lista)
    if falta:
        pp.script("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
        raise ValueError(f"{Path(modelo).name}: camada que não existe no modelo: {', '.join(map(str, falta))}")
    for i, op in enumerate(ops):
        if "imagem" in op:
            caixa = op.get("caixa") or next(c["caixa"] for c in lista if c["nome"] == unicodedata.normalize("NFC", op["imagem"]))
            arq = op["arquivo"] if op.get("inteira") else recorte(op["arquivo"], caixa, d / f"recorte-{i}.jpg", op.get("foco", (.5, .5)))
            _imagem(pp, op["imagem"], arq, caixa)
        elif "dentro" in op:  # o Photopea não salva objeto inteligente aninhado: edita à parte e volta como objeto novo
            abrir_dentro(pp, op["dentro"])
            dentro = camadas(pp)
            falta = _falta(op.get("ops", []), dentro)
            if falta:
                pp.script("while(app.documents.length)app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
                raise ValueError(f"{op['dentro']}: camada que não existe dentro do objeto: {', '.join(map(str, falta))}")
            for sub in op.get("ops", []):
                _sub(pp, sub, dentro, d)
            pp.script(JS_LIMITE)
            editavel = pp.exportar("psd")
            pp.script("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
            _objeto(pp, op["dentro"], editavel, op["caixa"])
        else:
            _sub(pp, op, lista, d)
    for formato, caminho in saidas.items():
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        Path(caminho).write_bytes(srgb(pp.exportar(formato)) if formato == "png" else pp.exportar(formato))
    pp.script("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
    return lista


def teste():
    from PIL import Image
    assert quebra("Fitoterapia Veterinária com Ênfase em Plantas Medicinais", 18) == ["Fitoterapia", "Veterinária com", "Ênfase em Plantas", "Medicinais"]
    assert quebra("Crédito Rural, Cooperativismo e Vendas", 18) == ["Crédito Rural,", "Cooperativismo", "e Vendas"]
    assert duas_linhas("Trilha inicial de aprendizado") == ["Trilha inicial", "de aprendizado"]
    assert _falta([{"texto": "Educação", "sobe": ["X"]}], [{"nome": "Educação"}]) == ["X"]
    with tempfile.TemporaryDirectory() as d:
        Image.new("RGB", (400, 100), (10, 200, 10)).save(f"{d}/larga.jpg")
        assert Image.open(recorte(f"{d}/larga.jpg", [0, 0, 100, 100], f"{d}/r.jpg")).size == (100, 100)
        try:
            with Sessao(espera_abrir=60) as pp:
                Image.new("RGB", (200, 120), (255, 255, 255)).save(f"{d}/modelo.png")
                Image.new("RGB", (50, 50), (210, 75, 168)).save(f"{d}/foto.png")
                Image.new("RGB", (40, 40), (20, 200, 20)).save(f"{d}/obj.png")
                pp.abrir(f"{d}/modelo.png")
                # FOTO com "ç" decomposto, como o PSD do Mac grava; OBJ é um objeto inteligente
                pp.script("var l=app.activeDocument.artLayers.add(); l.name='FOTO Educac\\u0327a\\u0303o'; app.activeDocument.selection.select([[20,20],[120,20],[120,100],[20,100]]);"
                          "app.activeDocument.selection.fill(app.foregroundColor); app.activeDocument.selection.deselect();")
                n = len(camadas(pp))
                pp.script("app.open(" + js("data:image/png;base64," + base64.b64encode(Path(f"{d}/obj.png").read_bytes()).decode()) + ", null, true);")
                while len(camadas(pp)) == n:
                    time.sleep(.2)
                pp.script("app.activeDocument.activeLayer.name='OBJ';")
                Path(f"{d}/m.psd").write_bytes(pp.exportar("psd"))
                pp.script("app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);")
                try:
                    preencher(pp, f"{d}/m.psd", [{"imagem": "NAO EXISTE", "arquivo": f"{d}/foto.png"}], {})
                    raise AssertionError("camada inexistente tem que parar antes")
                except ValueError as e:
                    assert "NAO EXISTE" in str(e)
                preencher(pp, f"{d}/m.psd", [{"imagem": "FOTO Educação", "arquivo": f"{d}/foto.png"},
                                              {"dentro": "OBJ", "caixa": [140, 20, 190, 70], "ops": []}], {"png": f"{d}/s.png", "psd": f"{d}/s.psd"})
                s = Image.open(f"{d}/s.png").convert("RGB")
                assert s.getpixel((70, 60))[0] > 180 and s.getpixel((70, 60))[1] < 120, s.getpixel((70, 60))  # magenta na caixa da FOTO
                assert s.getpixel((165, 45))[1] > 150 and s.getpixel((165, 45))[0] < 80, s.getpixel((165, 45))  # o objeto voltou na caixa
                assert s.getpixel((5, 5)) == (255, 255, 255) and Path(f"{d}/s.psd").stat().st_size > 1000
                preencher(pp, f"{d}/m.psd", [{"pintar": "FOTO Educação", "cor": "#0000FF"}], {"png": f"{d}/c.png"}, d)
                c = Image.open(f"{d}/c.png").convert("RGB")
                assert c.getpixel((70, 60))[2] > 200 and c.getpixel((70, 60))[0] < 60, c.getpixel((70, 60))  # a cor por cima da caixa
                print("ao vivo ok", end=" ")
        except Indisponivel as e:
            print(f"aviso: Photopea indisponível ({e}); parte ao vivo pulada")
            return
    print("ok")

if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    else:
        sys.exit(__doc__)
