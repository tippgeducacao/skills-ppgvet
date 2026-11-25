#!/usr/bin/env python3
"""Arte estática (post, carrossel, story, anúncio): gera o PNG de uma página HTML e mede antes de entregar.
uso: arte.py <peca.html> --formato feed|carrossel|anuncio|story|story-anuncio|quadrado|youtube|email|capa-reels|shorts|podcast|portal|portal-quadrado [--saida peca.png]  (sai também o .jpg sRGB, o que vai para o Instagram)
     arte.py --teste
Mede no navegador, depois de a fonte carregar: texto que não cabe ou sai da área segura do formato (elemento com
`data-sangra` pode encostar na borda, como faixa ou foto de ponta a ponta), fonte que não é Montserrat, contraste
da letra com o fundo (letra pequena no celular 4,5:1, grande 3:1), cor fora do regras/marca.md e o texto
pelo checar_texto.py (tipo arte). FALHA barra a entrega; AVISO é para olhar na peça (ex.: letra sobre foto).
A fonte é declarada com o nome Montserrat (`@font-face{font-family:Montserrat;src:url(...acervo/fontes/montserrat-variavel.ttf)}`)."""
import json, os, re, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import chrome, print_html  # noqa: E402
from checar_texto import checar  # noqa: E402
from portao import registrar  # noqa: E402

MARCA_MD = Path(__file__).resolve().parent.parent / "regras" / "marca.md"
# formato: (largura, altura, margem dos lados, livre em cima, livre embaixo); fontes em regras/oficio/design.md e video.md
FORMATOS = {"feed": (1080, 1350, 64, 64, 64), "anuncio": (1080, 1350, 64, 64, 64), "carrossel": (1080, 1350, 64, 64, 64), "quadrado": (1080, 1080, 64, 64, 64),
            "story": (1080, 1920, 64, 250, 250), "story-anuncio": (1080, 1920, 65, 269, 672),  # anúncio: 6% lados, 14% topo, 35% base
            "youtube": (1920, 1080, 96, 64, 64), "email": (600, 650, 32, 32, 32), "capa-reels": (1080, 1920, 64, 250, 250),
            "shorts": (1080, 1920, 64, 250, 250), "podcast": (1500, 1500, 96, 96, 96),
            "portal": (1080, 1920, 96, 160, 160), "portal-quadrado": (1000, 1000, 64, 64, 64)}  # capas do portal do aluno (Eduq)
# saída maior que o desenho, pelos tamanhos oficiais (regras/formatos.md); e-mail em dobro para tela retina
ESCALA = {"youtube": 2, "email": 2, "shorts": 2, "podcast": 2, "anuncio": 4 / 3, "story-anuncio": 4 / 3}  # anúncio Meta: 1440x1800 e 1440x2560 (guia de anúncios, 25/11/2026)
JPEG_MAX = 8e6  # a API do Instagram (agendador) só aceita JPEG sRGB até 8 MB


def jpeg(png, jpg):
    """JPEG sRGB sem transparência (fundo branco), qualidade alta; devolve o tamanho em bytes"""
    from PIL import Image, ImageCms
    im = Image.open(png).convert("RGBA")
    fundo = Image.new("RGB", im.size, (255, 255, 255))
    fundo.paste(im, mask=im.split()[3])
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    fundo.save(jpg, "JPEG", quality=92, subsampling=0, icc_profile=srgb)
    return os.path.getsize(jpg)
SEM_TEXTO = "<style>*{color:transparent!important;text-shadow:none!important;-webkit-text-stroke:0!important}</style>"
GRANDE_NEGRITO, GRANDE_NORMAL = 52, 64  # px na peça de 1080 que viram "letra grande" no celular (oficio/design.md)
NAO_E_MONTSERRAT = re.compile(r"^(?!.*montserrat)", re.I)

MEDIR = r"""<script>Promise.all([document.fonts.ready,new Promise(r=>document.readyState==="complete"?r():addEventListener("load",r))]).then(()=>{
const out=[], cor=c=>c, sobe=e=>{for(let a=e;a;a=a.parentElement){const s=getComputedStyle(a);
  if(s.backgroundImage&&s.backgroundImage!=='none')return{img:true};
  if(s.backgroundColor&&!/rgba\(0, 0, 0, 0\)|transparent/.test(s.backgroundColor))return{bg:s.backgroundColor};}
  return{bg:getComputedStyle(document.body).backgroundColor};};
const idx=new Map();
for(const e of document.body.querySelectorAll('*')){
  const txt=[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join(' ').trim();
  if(!txt||['SCRIPT','STYLE','PRE'].includes(e.tagName))continue;
  const s=getComputedStyle(e), b=e.getBoundingClientRect(), f=sobe(e);
  const img=[...document.images].some(i=>{const r=i.getBoundingClientRect();return r.left<b.right&&b.left<r.right&&r.top<b.bottom&&b.top<r.bottom&&getComputedStyle(i).zIndex<=s.zIndex});
  let anc=[];for(let a=e.parentElement;a;a=a.parentElement)if(idx.has(a))anc.push(idx.get(a));
  idx.set(e,out.length);
  let viuva=false;if(parseFloat(s.fontSize)>=56){const tops=[],larg=[],tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);for(let n;(n=tw.nextNode());){const re=/\S+/g;let m;
    while((m=re.exec(n.textContent))){const r=document.createRange();r.setStart(n,m.index);r.setEnd(n,m.index+m[0].length);const q=r.getBoundingClientRect();tops.push(Math.round(q.top));larg.push(q.width);}}
    const ult=tops.length?tops[tops.length-1]:0;viuva=new Set(tops).size>1&&tops.filter(t=>Math.abs(t-ult)<4).length===1&&larg[larg.length-1]<.4*b.width;}
  out.push({anc,t:txt.slice(0,60),x0:b.left,y0:b.top,x1:b.right,y1:b.bottom,estoura:e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+2&&s.overflow==='hidden',
    sangra:!!e.closest('[data-sangra]'),fonte:s.fontFamily,tam:parseFloat(s.fontSize),peso:parseInt(s.fontWeight),cor:s.color,fundo:f.bg||null,sobre_img:!!f.img||img,
    alinha:s.textAlign,viuva,caixa:!!e.closest('[data-caixa],[data-bloco]'),bloco:!!e.closest('[data-bloco]'),texto:txt});}
const fotos=[...document.images].map(i=>{const r=i.getBoundingClientRect();return{src:(i.alt||i.src.split('/').pop()).slice(0,40),nw:i.naturalWidth,nh:i.naturalHeight,w:r.width,h:r.height,
  x0:r.left,y0:r.top,x1:r.right,y1:r.bottom,sangra:!!i.closest('[data-sangra]')}});
const p=document.createElement('pre');p.id='medida';p.style.display='none';p.textContent=JSON.stringify({textos:out,fotos});document.body.appendChild(p);});</script>"""


def paleta():
    return {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", MARCA_MD.read_text(encoding="utf-8"))}


def rgb(css):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?", css or "")
    return (int(m[1]), int(m[2]), int(m[3]), float(m[4]) if m[4] else 1.0) if m else None


def contraste(a, b):
    def lum(c):
        c = [x / 255 for x in c[:3]]
        c = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def cores_fora(html):
    """hex do HTML que não está no marca.md (com 3 dígitos vira 6); rgba/transparência de sombra não entra"""
    ok, fora = paleta(), set()
    for c in re.findall(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b", html):
        c = c.upper()
        if len(c) == 4:
            c = "#" + "".join(x * 2 for x in c[1:])
        if c not in ok:
            fora.add(c)
    return sorted(fora)


def medir(html_arq, w, h):
    out = chrome(f"--window-size={w},{h}", "--virtual-time-budget=4000", "--dump-dom", Path(html_arq).resolve().as_uri())
    m = re.search(r'<pre id="medida"[^>]*>(.*?)</pre>', out, re.S)
    if not m:
        raise SystemExit("não consegui medir: a página não terminou de carregar (fonte ou imagem com caminho errado?)")
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))


def dentro(a, b):
    return a["x0"] >= b["x0"] - 1 and a["x1"] <= b["x1"] + 1 and a["y0"] >= b["y0"] - 1 and a["y1"] <= b["y1"] + 1


def problemas(caixas, formato, html="", fotos=()):
    w, h, lado, cima, baixo = FORMATOS[formato]
    falhas, avisos = [], []
    for i, a in enumerate(caixas):  # texto em cima de texto (o que está dentro do outro, como um <span>, não conta)
        for j, b in enumerate(caixas[i + 1:], i + 1):
            if i in b.get("anc", ()) or j in a.get("anc", ()) or dentro(a, b) or dentro(b, a):
                continue
            if min(a["x1"], b["x1"]) - max(a["x0"], b["x0"]) > 2 and min(a["y1"], b["y1"]) - max(a["y0"], b["y0"]) > 2:
                falhas.append(f'"{a["t"]}" cobre "{b["t"]}"')
    for i, a in enumerate(fotos):  # logo ou título (imagem) por cima de foto: some na textura
        for b in fotos[i + 1:]:
            peca, foto = (a, b) if b.get("sangra") and not a.get("sangra") else (b, a) if a.get("sangra") and not b.get("sangra") else (None, None)
            if peca and "sobre-foto" not in peca["src"] and min(peca["x1"], foto["x1"]) - max(peca["x0"], foto["x0"]) > 4 and min(peca["y1"], foto["y1"]) - max(peca["y0"], foto["y0"]) > 4:
                avisos.append(f'{peca["src"]} está por cima da foto {foto["src"]}: conferir se lê (melhor em área lisa)')
    for f in fotos:  # foto mostrada maior que o arquivo: esticada, fica mole
        esc = max(f["w"] / f["nw"], f["h"] / f["nh"]) * ESCALA.get(formato, 1) if f["nw"] and f["nh"] else 0
        if esc > 1.25:
            avisos.append(f'{f["src"]} aparece {esc:.1f}x maior que o arquivo: pedir a original ou ampliar com a editar-foto')
    for c in caixas:
        nome = f'"{c["t"]}"'
        if c["estoura"]:
            falhas.append(f"{nome}: o texto não cabe na caixa")
        if not c["sangra"] and (c["x0"] < lado - 1 or c["x1"] > w - lado + 1 or c["y0"] < cima - 1 or c["y1"] > h - baixo + 1):
            falhas.append(f"{nome}: fora da área segura do {formato} ({lado} px dos lados, {cima} em cima, {baixo} embaixo)")
        if NAO_E_MONTSERRAT.match(c["fonte"] or ""):
            falhas.append(f"{nome}: fonte {c['fonte']}: só Montserrat (marca.md)")
        grande = c["tam"] >= (GRANDE_NEGRITO if c["peso"] >= 700 else GRANDE_NORMAL)
        minimo = 3 if grande else 4.5
        letra, fundo = rgb(c["cor"]), rgb(c["fundo"])
        if c["sobre_img"]:
            pass  # medido nos pixels da peça pronta (contraste_real, no main)
        elif letra and fundo:
            r = contraste(letra, fundo)
            if r < minimo:
                falhas.append(f"{nome}: contraste {r:.2f}:1, abaixo de {minimo}:1 (letra {'grande' if grande else 'pequena'} no celular)")
        if c["tam"] < 24:
            avisos.append(f"{nome}: letra de {c['tam']:.0f} px some no celular (a peça aparece com ~0,36 do tamanho)")
    avisos += gosto(caixas)
    for cor in cores_fora(html):
        falhas.append(f"cor {cor} fora do marca.md")
    f_txt, a_txt = checar("\n".join(c["texto"] for c in caixas), "arte")
    return falhas + [f"texto: {x}" for x in f_txt], avisos + [f"texto: {x}" for x in a_txt if "caracteres" not in x]


def gosto(caixas):
    """sinais de peça sem acabamento (regras/antislop-midia.md, "Arte"): só avisos, a decisão é de quem olha"""
    avisos, soltas = [], [c for c in caixas if not c.get("anc") and not c.get("bloco")]
    tams, niveis = sorted({round(c["tam"]) for c in soltas}), 0
    for i, t in enumerate(tams):  # tamanhos a menos de 12% um do outro são o mesmo nível
        niveis += i == 0 or t > tams[i - 1] * 1.12
    if niveis > 4:
        avisos.append(f"{niveis} tamanhos de letra: a hierarquia pede até 3 níveis (título, apoio, detalhe) e um rótulo")
    for c in caixas:
        if c.get("viuva"):
            avisos.append(f'"{c["t"]}": uma palavra sozinha na última linha do título; quebrar a linha antes ou mudar a palavra')
    bordas = []
    for c in soltas:  # texto alinhado à esquerda que não sangra: as bordas da esquerda devem ser poucas (grid)
        if c.get("alinha") in ("left", "start") and not c["sangra"] and not c.get("caixa") and c["tam"] >= 24 and c["x1"] - c["x0"] > 40:
            if not any(abs(c["x0"] - b) <= 8 for b in bordas):
                bordas.append(c["x0"])
    if len(bordas) > 2:
        avisos.append(f"o texto começa em {len(bordas)} bordas diferentes ({', '.join(str(round(b)) for b in sorted(bordas))} px): alinhar ao grid")
    return avisos


def contraste_real(png_fundo, caixas):
    """letra sobre foto ou degradê: contraste com o fundo medido no print da peça sem o texto (o pior 10% de cada caixa)"""
    from PIL import Image
    rgba = Image.open(png_fundo).convert("RGBA")
    im, falhas = Image.new("RGB", rgba.size, (255, 255, 255)), []
    im.paste(rgba, mask=rgba.split()[3])  # transparente vira branco, como no JPEG que é entregue
    for c in caixas:
        letra = rgb(c["cor"])
        if not c["sobre_img"] or not letra:
            continue
        caixa = [round(v) for v in (c["x0"], c["y0"], c["x1"], c["y1"])]
        px = im.crop(caixa).resize((min(200, max(1, caixa[2] - caixa[0])), min(80, max(1, caixa[3] - caixa[1])))).tobytes()
        px = [px[i:i + 3] for i in range(0, len(px), 3)]
        pior = sorted(contraste(letra, p) for p in px)[len(px) // 10]
        grande = c["tam"] >= (GRANDE_NEGRITO if c["peso"] >= 700 else GRANDE_NORMAL)
        if pior < (3 if grande else 4.5):
            falhas.append(f'"{c["t"]}": contraste {pior:.2f}:1 sobre a foto, abaixo de {3 if grande else 4.5}:1: escurecer a foto atrás do texto (degradê)')
    return falhas


def main(html_arq, formato, saida):
    w, h = FORMATOS[formato][:2]
    html = Path(html_arq).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(dir=Path(html_arq).resolve().parent) as t:
        medida = Path(t) / "medida.html"
        medida.write_text(html.replace("</body>", MEDIR + "</body>") if "</body>" in html else html + MEDIR, encoding="utf-8")
        m = medir(medida, w, h)
        falhas, avisos = problemas(m["textos"], formato, html, m["fotos"])
        if any(c["sobre_img"] for c in m["textos"]):  # o mesmo print sem a letra, para medir o fundo de verdade
            sem = Path(t) / "sem-texto.html"
            sem.write_text(html.replace("</body>", SEM_TEXTO + "</body>") if "</body>" in html else html + SEM_TEXTO, encoding="utf-8")
            print_html(sem.resolve().as_uri(), w, h, str(Path(t) / "fundo.png"))
            falhas += contraste_real(Path(t) / "fundo.png", m["textos"])
    print_html(Path(html_arq).resolve().as_uri(), w, h, saida, ESCALA.get(formato, 1))
    jpg = str(Path(saida).with_suffix(".jpg"))
    if jpeg(saida, jpg) > JPEG_MAX and formato in ("feed", "carrossel", "quadrado", "story", "capa-reels"):
        falhas.append(f"{jpg} passa de 8 MB: a API do Instagram recusa")
    for x in falhas:
        print("FALHA:", x)
    for x in avisos:
        print("AVISO:", x)
    print(saida, "ok" if not falhas else f"({len(falhas)} falha(s))")
    registrar(saida, not falhas, len(falhas))
    return not falhas


def teste():
    import portao
    portao.REGISTRO = Path(tempfile.mkdtemp()) / "conferencias.jsonl"  # o teste não suja o registro de verdade
    assert "#D24BA8" in paleta() and "#FAF9FB" in paleta() and "#965594" not in paleta()
    assert FORMATOS["youtube"][0] * ESCALA["youtube"] == 3840 and set(ESCALA) <= set(FORMATOS)
    assert FORMATOS["podcast"][0] * ESCALA["podcast"] == 3000 and FORMATOS["shorts"][1] * ESCALA["shorts"] == 3840
    from PIL import Image
    with tempfile.TemporaryDirectory() as d:  # transparência vira branco e o JPEG leva o perfil sRGB
        Image.new("RGBA", (40, 40), (0, 0, 0, 0)).save(f"{d}/a.png")
        assert jpeg(f"{d}/a.png", f"{d}/a.jpg") > 0
        j = Image.open(f"{d}/a.jpg")
        assert j.mode == "RGB" and j.getpixel((5, 5))[0] > 250 and j.info.get("icc_profile")
    assert cores_fora("a{color:#d24ba8;background:#fff} b{color:#965594}") == ["#965594"]
    assert round(contraste((255, 255, 255), (0xD2, 0x4B, 0xA8)), 2) == 3.95
    caixa = dict(t="x", x0=100, y0=300, x1=900, y1=400, estoura=False, sangra=False, fonte="Arial, sans-serif", tam=40, peso=800,
                 cor="rgb(255, 255, 255)", fundo="rgb(210, 75, 168)", sobre_img=False, texto="Aula nova")
    f, _ = problemas([caixa], "feed")
    assert any("contraste" in x for x in f) and any("fonte" in x for x in f), f  # branco no magenta, letra pequena; fonte errada
    ok = dict(caixa, fonte="Montserrat", cor="rgb(26, 26, 26)", fundo="rgb(250, 249, 251)")
    assert not problemas([ok], "feed")[0]
    assert any("área segura" in x for x in problemas([dict(ok, y0=100, y1=200)], "story")[0])  # nos 250 px de cima do story
    assert not problemas([dict(ok, y0=10, y1=60, sangra=True)], "story")[0]
    assert any("MBA" in x for x in problemas([dict(ok, texto="Conheça o MBA")], "feed")[0])
    assert any("cobre" in x for x in problemas([ok, dict(ok, t="y", y0=380, y1=460)], "feed")[0])  # título de 3 linhas por cima do apoio
    assert not problemas([ok, dict(ok, t="span", x0=200, x1=300, y0=310, y1=390)], "feed")[0]  # palavra dentro do título
    assert any("maior" in x for x in problemas([ok], "feed", "", [dict(src="f.jpg", nw=400, nh=400, w=1080, h=760)])[1])
    foto = dict(src="f.jpg", nw=2000, nh=2000, w=900, h=900, x0=300, y0=450, x1=1200, y1=1350, sangra=True)
    titulo = dict(src="t.png", nw=2000, nh=500, w=500, h=120, x0=64, y0=1100, x1=564, y1=1220, sangra=False)
    assert any("por cima" in x for x in problemas([ok], "feed", "", [foto, titulo])[1])
    assert any("tamanhos" in x for x in gosto([dict(ok, tam=t) for t in (24, 30, 44, 60, 90)]))  # 5 níveis
    assert not gosto([dict(ok, tam=t) for t in (26, 38, 40, 96)])  # 38 e 40 são o mesmo nível
    assert any("sozinha" in x for x in gosto([dict(ok, viuva=True)]))
    assert any("bordas" in x for x in gosto([dict(ok, alinha="left", x0=x, x1=x + 500) for x in (80, 120, 200)]))
    assert not gosto([dict(ok, alinha="left", x0=80, x1=600), dict(ok, alinha="left", x0=84, x1=600), dict(ok, alinha="center", x0=300, x1=700)])
    with tempfile.TemporaryDirectory() as d:  # letra branca: reprova no fundo claro, passa no escuro
        im = Image.new("RGB", (200, 100), (200, 200, 200))
        im.paste((26, 26, 26), (100, 0, 200, 100))
        im.save(f"{d}/f.png")
        b = dict(ok, cor="rgb(255, 255, 255)", sobre_img=True, tam=30, peso=400, y0=0, y1=100)
        assert contraste_real(f"{d}/f.png", [dict(b, x0=0, x1=100)]) and not contraste_real(f"{d}/f.png", [dict(b, x0=100, x1=200)])
        Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(f"{d}/t.png")  # transparente conta como branco: letra branca reprova
        assert contraste_real(f"{d}/t.png", [dict(b, x0=0, x1=100)])
    with tempfile.TemporaryDirectory() as d:  # ponta a ponta no navegador (precisa do Chrome)
        fonte = (Path(__file__).resolve().parent.parent / "acervo" / "fontes" / "montserrat-variavel.ttf").as_uri()
        Path(d, "p.html").write_text(f"""<!doctype html><meta charset=utf-8><style>@font-face{{font-family:Montserrat;src:url('{fonte}')}}
body{{margin:0;width:1080px;height:1350px;background:#FAF9FB;font-family:Montserrat}} h1{{position:absolute;left:64px;top:200px;margin:0;
font-size:90px;color:#1A1A1A}} p{{position:absolute;left:64px;top:400px;margin:0;width:500px;white-space:nowrap;overflow:hidden;
font-size:60px;color:#D24BA8}}</style><body><h1>Aqui tem prática</h1><p>um texto comprido que não cabe aqui dentro</p></body>""", encoding="utf-8")
        assert not main(f"{d}/p.html", "feed", f"{d}/p.png") and Path(d, "p.png").exists()  # o texto que estoura reprova
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a and "--formato" in a:
        formato = a[a.index("--formato") + 1]
        assert formato in FORMATOS, f"formato: {', '.join(FORMATOS)}"
        saida = a[a.index("--saida") + 1] if "--saida" in a else str(Path(a[0]).with_suffix(".png"))
        sys.exit(0 if main(a[0], formato, saida) else 1)
    else:
        sys.exit(__doc__)
