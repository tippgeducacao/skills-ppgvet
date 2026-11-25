#!/usr/bin/env python3
"""Arte estática (post, carrossel, story, anúncio): gera o PNG de uma página HTML e mede antes de entregar.
uso: arte.py <peca.html> --formato feed|carrossel|story|story-anuncio|quadrado|youtube|email [--saida peca.png]
     arte.py --teste
Mede no navegador, depois de a fonte carregar: texto que não cabe ou sai da área segura do formato (elemento com
`data-sangra` pode encostar na borda, como faixa ou foto de ponta a ponta), fonte que não é Montserrat, contraste
da letra com o fundo (letra pequena no celular 4,5:1, grande 3:1), cor fora do regras/marca.md e o texto
pelo checar_texto.py (tipo arte). FALHA barra a entrega; AVISO é para olhar na peça (ex.: letra sobre foto).
A fonte é declarada com o nome Montserrat (`@font-face{font-family:Montserrat;src:url(...acervo/fontes/montserrat-variavel.ttf)}`)."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import NAVEGADORES, print_html  # noqa: E402
from checar_texto import checar  # noqa: E402

MARCA_MD = Path(__file__).resolve().parent.parent / "regras" / "marca.md"
# formato: (largura, altura, margem dos lados, livre em cima, livre embaixo); fontes em regras/oficio/design.md e video.md
FORMATOS = {"feed": (1080, 1350, 64, 64, 64), "carrossel": (1080, 1350, 64, 64, 64), "quadrado": (1080, 1080, 64, 64, 64),
            "story": (1080, 1920, 64, 250, 250), "story-anuncio": (1080, 1920, 65, 269, 672),  # anúncio: 6% lados, 14% topo, 35% base
            "youtube": (1920, 1080, 96, 64, 64), "email": (600, 650, 32, 32, 32)}
ESCALA = {"youtube": 2, "email": 2}  # thumb sai 3840x2160 (ajuda do YouTube); banner de e-mail em dobro para tela retina
GRANDE_NEGRITO, GRANDE_NORMAL = 52, 64  # px na peça de 1080 que viram "letra grande" no celular (oficio/design.md)
NAO_E_MONTSERRAT = re.compile(r"^(?!.*montserrat)", re.I)

MEDIR = r"""<script>document.fonts.ready.then(()=>{
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
  out.push({anc,t:txt.slice(0,60),x0:b.left,y0:b.top,x1:b.right,y1:b.bottom,estoura:e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+2&&s.overflow==='hidden',
    sangra:!!e.closest('[data-sangra]'),fonte:s.fontFamily,tam:parseFloat(s.fontSize),peso:parseInt(s.fontWeight),cor:s.color,fundo:f.bg||null,sobre_img:!!f.img||img,
    texto:txt});}
const fotos=[...document.images].map(i=>{const r=i.getBoundingClientRect();return{src:i.src.split('/').pop(),nw:i.naturalWidth,nh:i.naturalHeight,w:r.width,h:r.height,
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
    nav = next(n for n in NAVEGADORES + ["/usr/bin/google-chrome", "/usr/bin/chromium"] if n and os.path.exists(n))
    out = subprocess.run([nav, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", f"--window-size={w},{h}",
                          "--virtual-time-budget=4000", "--dump-dom", Path(html_arq).resolve().as_uri()],
                         capture_output=True, text=True, check=True).stdout
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
            if peca and min(peca["x1"], foto["x1"]) - max(peca["x0"], foto["x0"]) > 4 and min(peca["y1"], foto["y1"]) - max(peca["y0"], foto["y0"]) > 4:
                avisos.append(f'{peca["src"]} está por cima da foto {foto["src"]}: conferir se lê (melhor em área lisa)')
    for f in fotos:  # foto mostrada maior que o arquivo: esticada, fica mole
        esc = max(f["w"] / f["nw"], f["h"] / f["nh"]) if f["nw"] and f["nh"] else 0
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
            avisos.append(f"{nome}: letra sobre foto ou degradê: conferir o contraste na peça (mínimo {minimo}:1)")
        elif letra and fundo:
            r = contraste(letra, fundo)
            if r < minimo:
                falhas.append(f"{nome}: contraste {r:.2f}:1, abaixo de {minimo}:1 (letra {'grande' if grande else 'pequena'} no celular)")
        if c["tam"] < 24:
            avisos.append(f"{nome}: letra de {c['tam']:.0f} px some no celular (a peça aparece com ~0,36 do tamanho)")
    for cor in cores_fora(html):
        falhas.append(f"cor {cor} fora do marca.md")
    f_txt, a_txt = checar("\n".join(c["texto"] for c in caixas), "arte")
    return falhas + [f"texto: {x}" for x in f_txt], avisos + [f"texto: {x}" for x in a_txt if "caracteres" not in x]


def main(html_arq, formato, saida):
    w, h = FORMATOS[formato][:2]
    html = Path(html_arq).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(dir=Path(html_arq).resolve().parent) as t:
        medida = Path(t) / "medida.html"
        medida.write_text(html.replace("</body>", MEDIR + "</body>") if "</body>" in html else html + MEDIR, encoding="utf-8")
        m = medir(medida, w, h)
        falhas, avisos = problemas(m["textos"], formato, html, m["fotos"])
    print_html(Path(html_arq).resolve().as_uri(), w, h, saida, ESCALA.get(formato, 1))
    for x in falhas:
        print("FALHA:", x)
    for x in avisos:
        print("AVISO:", x)
    print(saida, "ok" if not falhas else f"({len(falhas)} falha(s))")
    return not falhas


def teste():
    assert "#D24BA8" in paleta() and "#FAF9FB" in paleta() and "#965594" not in paleta()
    assert FORMATOS["youtube"][0] * ESCALA["youtube"] == 3840 and set(ESCALA) <= set(FORMATOS)
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
