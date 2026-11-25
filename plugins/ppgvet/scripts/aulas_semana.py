#!/usr/bin/env python3
"""Carrossel "Aulas da semana" do Instagram (1080x1350, 4:5): capa + uma lâmina por aula, no molde da equipe.
uso: aulas_semana.py semana.json [--fotos <pasta das fotos dos professores>] (sem --fotos: acervo/professores)
     aulas_semana.py --teste
semana.json: {"ano": 2026, "aulas": [{"pos": "CBEA" (ou ["RNGB","NGB","GPL"] em módulo comum), "data": "23/11",
  "hora": "19h", "professor": "Dra. Ana Souza", "tema": "Bem-estar na criação",
  "foto": "<arquivo>" (opcional: sem ela, procura pelo nome em --fotos)}]}
Confere antes de gerar (sigla, dia da semana pela data, titulação, foto, grafia do nome pela foto) e depois mede
(texto que não cabe ou encosta, contraste). Uma pasta por marca: PPGVET e PPG nunca no mesmo carrossel."""
import datetime as dt, difflib, json, os, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import NAVEGADORES, acervo, pasta, print_html  # noqa: E402

MARCA_MD = Path(__file__).resolve().parent.parent / "regras" / "marca.md"
W, H, MARGEM = 1080, 1350, 48
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
MARCA = {"PPGVET": {"cor": "#D24BA8", "acao": "#00B7AB", "logo": "logos/ppgvet/logo-ppgvet.png"},
         "PPG": {"cor": "#1670C2", "acao": "#00ADA3", "logo": "logos/ppg/logo-ppg-educacao.png"}}
ESCURO, FUNDO = "#1A1A1A", "#FAF9FB"
TITULOS = ("Dr.", "Dra.", "Me.", "Ma.")  # só estas (regra de copy da equipe); sem titulação comprovada, só o nome
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
       'stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>')
REL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
       'stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>')  # ícones Lucide (ISC)


def pos_tabela():
    """sigla -> (nome, marca, cor), da tabela de pós do regras/marca.md"""
    t = MARCA_MD.read_text(encoding="utf-8")
    return {s: (n.strip(), m, c) for s, n, m, c in
            re.findall(r"^\| ([A-Z]+) \| ([^|]+) \| (PPGVET|PPG) \| [^|]+ \| `(#[0-9A-Fa-f]{6})` \|", t, re.M)}


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def letra_sobre(cor):
    """branco ou o escuro da marca, o que der mais contraste (a tarja é letra pequena no celular: pede 4,5:1)"""
    return max(("#FFFFFF", ESCURO), key=lambda c: contraste(c, cor))


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def titulo_e_nome(prof):
    """'Dra. Ana Souza' -> ('Dra.', 'Ana Souza', None). Fora de Dr./Dra./Me./Ma. a titulação sai e fica só o nome
    (nunca "Prof.", "Esp.", "M.V.", "PhD"), com aviso quando era uma que pode esconder mestrado ou doutorado"""
    prof = " ".join(prof.split())
    m = re.match(r"^(Dra?|Ma?|Me|Prof[aª]?|Esp|M\.?\s?V|PhD)\.?\s+(.+)$", prof, re.I)
    if not m:
        return "", prof, None
    t = m.group(1).capitalize() + "."
    if t in TITULOS:
        return t, m.group(2), None
    if t.startswith("Prof"):
        return "", m.group(2), None
    return "", m.group(2), f'"{m.group(1)}" não entra (só Dr./Dra., Me./Ma. comprovados): ficou só o nome'


def achar_foto(nome, fotos):
    """foto pelo nome na pasta (nome-sobrenome.jpg); devolve (arquivo, aviso de grafia ou None)"""
    if not fotos or not Path(fotos).is_dir():
        return None, None
    arqs = {p.stem: p for p in Path(fotos).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")}
    partes = slug(nome).split("-")
    for st, p in arqs.items():  # primeiro e último nome batendo
        if partes[0] in st.split("-") and partes[-1] in st.split("-"):
            return p, None
    perto = difflib.get_close_matches(slug(nome), list(arqs), n=1, cutoff=.75)
    if perto:
        return arqs[perto[0]], f'"{nome}" não bate com a foto "{perto[0]}": conferir a grafia'
    return None, None


def juntar(nomes):
    """nomes das pós de um módulo comum, sem o que já está dentro de outro (NGB dentro de RNGB)"""
    return [n for n in nomes if not any(n != o and n.lower() in o.lower() for o in nomes)]


def preparar(d, fotos=None):
    """valida a lista; devolve ({marca: [aulas prontas]}, erros, avisos)"""
    tab, erros, avisos, por_marca = pos_tabela(), [], [], {}
    ano = int(d.get("ano", dt.date.today().year))
    for i, a in enumerate(d["aulas"], 1):
        siglas = [s.upper() for s in ([a["pos"]] if isinstance(a["pos"], str) else a["pos"])]
        fora = [s for s in siglas if s not in tab]
        if fora:
            erros.append(f"aula {i}: pós {fora} não está no regras/marca.md")
            continue
        marcas = {tab[s][1] for s in siglas}
        if len(marcas) > 1:
            erros.append(f"aula {i}: mistura PPGVET e PPG {siglas}")
            continue
        try:
            dia, mes = map(int, a["data"].split("/")[:2])
            data = dt.date(ano, mes, dia)
        except (ValueError, KeyError):
            erros.append(f'aula {i}: data "{a.get("data")}" (use dd/mm)')
            continue
        if data.weekday() > 4:
            avisos.append(f"aula {i}: {data:%d/%m} cai num {DIAS[data.weekday()]}")
        h = re.fullmatch(r"(\d{1,2})\s*[h:]\s*(\d{2})?", str(a.get("hora", "")).strip().lower())
        if not h:
            erros.append(f'aula {i}: horário "{a.get("hora")}" (use 19h ou 19h30)')
            continue
        tit, nome, aviso_tit = titulo_e_nome(a["professor"])
        if aviso_tit:
            avisos.append(f"aula {i}: {aviso_tit}")
        foto, aviso = (Path(a["foto"]), None) if a.get("foto") else achar_foto(nome, fotos)
        if aviso:
            avisos.append(f"aula {i}: {aviso}")
        if not foto or not foto.exists():
            erros.append(f"aula {i}: falta a foto de {nome}")
            continue
        tema = " ".join(a["tema"].split()).rstrip(".")
        if len(tema) > 110:
            avisos.append(f"aula {i}: tema com {len(tema)} caracteres (mais de 3 linhas): encurtar com quem pediu")
        um = len(siglas) == 1
        por_marca.setdefault(marcas.pop(), []).append({
            "data": data, "hora": f"{int(h.group(1))}h{h.group(2) or '00'}", "titulo": tit, "nome": nome,
            "foto": foto, "tema": tema, "pos": " + ".join(juntar([tab[s][0] for s in siglas])), "cor": tab[siglas[0]][2] if um else None})
    for aulas in por_marca.values():
        aulas.sort(key=lambda x: (x["data"], x["hora"]))
    return por_marca, erros, avisos


def base(m):
    fonte = Path(acervo("fontes", "montserrat-variavel.ttf")).as_uri()
    return f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:M;src:url('{fonte}');font-weight:100 900}}
*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:M;color:{ESCURO};background:{FUNDO};position:relative;
  background-image:linear-gradient(rgba(26,26,26,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(26,26,26,.035) 1px,transparent 1px);background-size:54px 54px}}
.logo{{position:absolute;top:64px;left:50%;transform:translateX(-50%);width:170px}}
.arrasta{{position:absolute;bottom:56px;left:{MARGEM}px;right:{MARGEM}px;text-align:center;font-size:26px;letter-spacing:2px;text-transform:uppercase;font-weight:500}}
.arrasta b{{font-weight:800}}
</style><img class=logo src="{Path(acervo(*MARCA[m]['logo'].split('/'))).as_uri()}">"""


MEDIR = """<script>document.fonts.ready.then(()=>{const r=[],ok=[];for(const e of document.querySelectorAll('[data-m]')){
const b=e.getBoundingClientRect();r.push([e.dataset.m,b.left,b.top,b.right,b.bottom,e.scrollWidth>e.clientWidth+1]);}
const p=document.createElement('pre');p.id='medida';p.style.display='none';p.textContent=JSON.stringify(r);document.body.appendChild(p);});</script>"""


def capa(m, aulas):
    a, b = aulas[0]["data"], aulas[-1]["data"]
    datas = (f"{a.day} a {b.day} de {MESES[b.month - 1]}" if a.month == b.month
             else f"{a.day} de {MESES[a.month - 1]} a {b.day} de {MESES[b.month - 1]}")
    if a == b:
        datas = f"{a.day} de {MESES[a.month - 1]}"
    cor = MARCA[m]["cor"]
    return base(m) + f"""<style>
.bloco{{position:absolute;top:470px;left:{MARGEM}px;right:{MARGEM}px;text-align:center}}
.aulasda{{font-weight:400;font-size:64px;letter-spacing:22px;text-transform:uppercase;margin-right:-22px}}
.semana{{font-weight:900;font-size:210px;line-height:.9;letter-spacing:-6px;color:{cor};text-transform:uppercase}}
.datas{{display:inline-block;margin-top:34px;background:{ESCURO};color:#fff;font-weight:800;font-size:46px;padding:14px 48px;text-transform:uppercase}}
</style><div class=bloco><p class=aulasda>Aulas da</p><p class=semana data-m=semana>Semana</p><p class=datas data-m=datas>{datas}</p></div>
<p class=arrasta><b>Arrasta</b> para o lado</p>""" + MEDIR


def tam_tarja(aulas, m):
    """um tamanho de tarja para o carrossel todo: 40 px; se alguma cor não dá 4,5:1 com letra nenhuma, 52 px
    (letra grande, pede 3:1) em todas"""
    cores = [a["cor"] or MARCA[m]["cor"] for a in aulas]
    return 52 if any(contraste(letra_sobre(c), c) < 4.5 for c in cores) else 40


def lamina(m, a, tam=40):
    """coluna que se acomoda: tarja mais alta ou tema mais longo empurram o resto, e o bloco da foto encolhe"""
    cor, acao = MARCA[m]["cor"], MARCA[m]["acao"]
    tarja = a["cor"] or cor  # módulo comum a várias pós: a cor da marca
    d = a["data"]
    fonte_tema = 36 if len(a["tema"]) <= 75 else 32
    rotulo = f"<p>{a['titulo']}</p>" if a["titulo"] else ""  # sem titulação comprovada, só o nome
    return base(m) + f"""<style>
.col{{position:absolute;top:232px;bottom:48px;left:0;right:0;display:flex;flex-direction:column}}
.pos{{text-align:center;font-weight:900;font-size:98px;line-height:1.05;letter-spacing:-1px;color:{cor};text-transform:uppercase}}
.pos span{{display:inline-block}}
.tarja{{margin-top:22px;background:{tarja};color:{letra_sobre(tarja)};text-align:center;font-weight:800;font-size:{tam}px;line-height:1.18;padding:26px 64px;text-transform:uppercase}}
.meio{{flex:1 1 auto;min-height:340px;max-height:560px;position:relative;margin:44px 64px 0 72px}}
.foto{{z-index:1;position:absolute;left:0;top:0;bottom:0;width:410px;border-radius:40px;overflow:hidden;background:#fff;border:10px solid #fff;box-shadow:0 18px 50px rgba(26,26,26,.12)}}
.foto img{{width:100%;height:100%;object-fit:cover;object-position:50% 18%;border-radius:30px}}
.dir{{position:absolute;left:380px;right:0;top:40px}}
.quando{{background:{ESCURO};color:#fff;border-radius:0 34px 34px 0;padding:32px 28px 32px 66px}}
.linha{{display:flex;gap:20px;align-items:center}} .linha+.linha{{margin-top:24px}}
.linha svg{{width:58px;height:58px;flex:none;color:{acao}}}
.rot{{font-weight:600;font-size:31px;text-transform:uppercase;line-height:1.1}} .val{{font-weight:800;font-size:36px;text-transform:uppercase;line-height:1.1;white-space:nowrap}}
.prof{{margin:44px 0 0 66px}}
.prof p{{font-weight:600;font-size:32px}} .prof p:last-child{{font-weight:800;font-size:44px;line-height:1.08}}
.tema{{margin:36px 90px 0;text-align:center;font-size:{fonte_tema}px;line-height:1.2;text-transform:uppercase}}
.tema b{{font-weight:900;box-shadow:inset 0 -12px 0 {cor}55}}
.col .arrasta{{position:static;margin:auto {MARGEM}px 0;padding-top:24px}}
</style><div class=col><p class=pos><span data-m=pos>Pós-Graduação</span></p><p class=tarja data-m=tarja>{a['pos']}</p>
<div class=meio><div class=foto><img src="{a['foto'].resolve().as_uri()}"></div>
<div class=dir><div class=quando data-m=quando><div class=linha>{CAL}<div><p class=rot>{DIAS[d.weekday()]}</p><p class=val data-m=data>{d.day} de {MESES[d.month - 1]}</p></div></div>
<div class=linha>{REL}<div><p class=rot>Horário</p><p class=val data-m=hora>às {a['hora']}</p></div></div></div>
<div class=prof data-m=prof>{rotulo}<p>{a['nome']}</p></div></div></div>
<p class=tema data-m=tema><b>Aula:</b> {a['tema']}</p>
<p class=arrasta data-m=arrasta><b>Arrasta</b> para o lado</p></div>""" + MEDIR


def medir(html_arq):
    """caixas de cada texto, medidas no navegador depois de a fonte carregar"""
    nav = next(n for n in NAVEGADORES + ["/usr/bin/google-chrome", "/usr/bin/chromium"] if n and os.path.exists(n))
    out = subprocess.run([nav, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", f"--window-size={W},{H}",
                          "--virtual-time-budget=3000", "--dump-dom", Path(html_arq).resolve().as_uri()],
                         capture_output=True, text=True, check=True).stdout
    m = re.search(r'<pre id="medida">(.*?)</pre>', out, re.S)
    return json.loads(m.group(1).replace("&quot;", '"')) if m else []


def problemas(caixas):
    """texto que estoura a caixa, encosta na borda (fora a tarja, que vai de ponta a ponta) ou cobre outro texto"""
    p = []
    for nome, x0, y0, x1, y1, estoura in caixas:
        if estoura:
            p.append(f"{nome}: o texto não cabe")
        if nome != "tarja" and (x0 < MARGEM - 1 or x1 > W - MARGEM + 1 or y1 > H - 30):
            p.append(f"{nome}: encosta na borda")
    soltos = [c for c in caixas if c[0] in ("pos", "tarja", "quando", "prof", "tema", "arrasta")]
    for nome, x0, y0, x1, y1, _ in caixas:
        if nome == "arrasta" and y1 > H - 40:
            p.append("arrasta: sem espaço no fim (tema ou tarja longos demais)")
    for i, a in enumerate(soltos):
        for b in soltos[i + 1:]:
            if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] - 2 and b[2] < a[4] - 2:
                p.append(f"{a[0]} cobre {b[0]}")
    return p


def gerar(d, fotos=None, saida=None):
    por_marca, erros, avisos = preparar(d, fotos)
    for a in avisos:
        print("AVISO:", a)
    if erros:
        sys.exit("Corrigir antes de gerar:\n- " + "\n- ".join(erros))
    pastas = []
    for m, aulas in por_marca.items():
        nome = f"aulas-semana-{m.lower()}-{aulas[0]['data']:%d-%m}"
        alvo = Path(saida or pasta("artes")) / nome
        v = 2
        while alvo.exists():  # nunca sobrescrever
            alvo = alvo.with_name(f"{nome}-v{v}"); v += 1
        alvo.mkdir(parents=True)
        tam = tam_tarja(aulas, m)
        laminas = [("01-capa", capa(m, aulas))] + [(f"{i:02d}-{slug(a['nome'])}", lamina(m, a, tam)) for i, a in enumerate(aulas, 2)]
        falhas = []
        with tempfile.TemporaryDirectory() as t:
            for n, html in laminas:
                h = Path(t) / f"{n}.html"
                h.write_text(html, encoding="utf-8")
                falhas += [f"{n}: {x}" for x in problemas(medir(h))]
                print_html(h.resolve().as_uri(), W, H, str(alvo / f"{n}.png"))
        folha(sorted(alvo.glob("*.png")), alvo / "folha.jpg")
        print(f"{m}: {len(laminas)} lâminas em {alvo}")
        for f in falhas:
            print("FALHA:", f)
        pastas.append((alvo, falhas))
    return pastas


def folha(pngs, saida):
    from PIL import Image
    ims = [Image.open(p).convert("RGB").resize((360, 450)) for p in pngs]
    f = Image.new("RGB", (370 * min(len(ims), 6), 460 * ((len(ims) + 5) // 6)), "white")
    for i, im in enumerate(ims):
        f.paste(im, ((i % 6) * 370, (i // 6) * 460))
    f.save(saida, quality=88)


def teste():
    tab = pos_tabela()
    assert len(tab) >= 19 and tab["CBEA"] == ("Comportamento e Bem-Estar Animal", "PPGVET", "#026E66"), tab.get("CBEA")
    assert letra_sobre("#00BEA0") == ESCURO and letra_sobre("#026E66") == "#FFFFFF"
    assert max(contraste(c, "#DA4C00") for c in ("#FFFFFF", ESCURO)) < 4.5  # laranja da PC: vai com letra grande
    assert contraste("#FFFFFF", "#D24BA8") < 4.5 < contraste("#FFFFFF", ESCURO)
    assert titulo_e_nome("Dra. Ana Souza") == ("Dra.", "Ana Souza", None)
    assert titulo_e_nome("Prof. João Silva") == ("", "João Silva", None) and titulo_e_nome("Ana Souza") == ("", "Ana Souza", None)
    for ruim in ("PhD João Silva", "Esp. Ana Souza", "M.V. Ana Souza"):
        tit, nome, aviso = titulo_e_nome(ruim)
        assert tit == "" and aviso and " " in nome and not nome.startswith(("M.", "V ")), (ruim, nome)
    with tempfile.TemporaryDirectory() as t:
        from PIL import Image
        Image.new("RGB", (600, 800), "#888").save(f"{t}/ana-maria-souza.jpg")
        Image.new("RGB", (600, 800), "#888").save(f"{t}/bruno-lima.jpg")
        assert achar_foto("Ana Souza", t)[0].name == "ana-maria-souza.jpg"
        assert "grafia" in achar_foto("Bruno Limma", t)[1]
        d = {"ano": 2026, "aulas": [
            {"pos": "PC", "data": "23/11", "hora": "19h", "professor": "Ana Souza", "tema": "Tema curto de teste"},
            {"pos": ["RNGB", "NGB", "GPL"], "data": "24/11", "hora": "19h30", "professor": "Me. Bruno Lima", "tema": "Outro tema"},
            {"pos": "GCC", "data": "25/11", "hora": "20:00", "professor": "Ana Souza", "tema": "Tema da PPG"}]}
        pm, erros, avisos = preparar(d, t)
        assert not erros and set(pm) == {"PPGVET", "PPG"}, (erros, pm.keys())  # PPG vai em carrossel próprio
        assert pm["PPGVET"][0]["data"].weekday() == 0 and pm["PPGVET"][1]["cor"] is None  # 23/11/2026 = segunda
        assert pm["PPGVET"][1]["pos"] == "Reprodução, Nutrição e Gestão de Bovinos + Gestão na Pecuária Leiteira", pm["PPGVET"][1]["pos"]
        assert pm["PPG"][0]["hora"] == "20h00"
        _, erros, _ = preparar({"aulas": [{"pos": "XYZ", "data": "1/1", "hora": "19h", "professor": "A B", "tema": "x"}]}, t)
        assert erros and "XYZ" in erros[0]
        assert problemas([["pos", 10, 0, 1070, 100, False]]) == ["pos: encosta na borda"]
        assert problemas([["tema", 90, 1100, 990, 1250, False], ["arrasta", 90, 1240, 990, 1290, False]]) == ["tema cobre arrasta"]
        pastas = gerar({"ano": 2026, "aulas": d["aulas"][:1]}, t, t)  # gera de verdade (precisa do Chrome) e mede
        assert not pastas[0][1], pastas[0][1]
        assert len(list(pastas[0][0].glob("*.png"))) == 2
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    elif len(sys.argv) >= 2:
        fotos = sys.argv[sys.argv.index("--fotos") + 1] if "--fotos" in sys.argv else acervo("professores")
        r = gerar(json.load(open(sys.argv[1], encoding="utf-8")), fotos)
        sys.exit(1 if any(f for _, f in r) else 0)
    else:
        sys.exit(__doc__)
