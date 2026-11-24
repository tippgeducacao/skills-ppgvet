#!/usr/bin/env python3
"""Confere um texto de marketing antes de entregar (regras em regras/oficio/copy.md).
uso: checar_texto.py <arquivo.txt> --tipo legenda|arte|whatsapp|anuncio [--titulo "<título do anúncio>"]
     checar_texto.py --teste
FALHA barra a entrega (corrigir e rodar de novo); AVISO é para olhar e decidir. Sai 1 se houver FALHA."""
import re, sys

LIMITES = {"legenda": 2200, "whatsapp": 600, "anuncio": 600, "arte": 400}  # legenda: limite do Instagram; os outros, da casa
VISIVEL = 125  # a legenda e o texto principal do anúncio mostram ~125 caracteres antes do "mais"

FALHAS = [  # (regex, por quê)
    (r"\bMBA\b", 'é "Pós-Graduação", nunca "MBA" (marca.md)'),
    (r"—|–", "sem travessão (marca.md)"),
    (r"\b(Prof|Profa|Profª|M\.\s?V|Esp)\.\s+[A-ZÁÉÍÓÚ]", "titulação só Dr./Dra. e Me./Ma.; sem comprovação, só o nome (regras de copy da equipe)"),
    (r"(?i)ouça agora nas principais plataformas", "frase proibida pelas regras de copy da equipe"),
    (r"\*\*[^*\n]+\*\*", "sobra de rascunho: **negrito** do Markdown não vira negrito no Instagram nem no WhatsApp"),
    (r"(?i)#(medicinavetrinaria|medicinaveternaria|medicinaveterinária|ppgeducação)\b", "hashtag sem acento e com a grafia certa: #medicinaveterinaria, #ppgeducacao (copy.md)"),
    (r"(?i)ganchos? alternativos?|opç(ão|ões) de (gancho|legenda)|^\s*vers(ão|ões) [a-c1-3]\b", "sobra de rascunho no texto"),
]
# número da marca: só na forma oficial do marca.md; número novo, só com fonte (e entra lá antes)
NUMERO = re.compile(r"(?i)(\+\s?)?(\d{1,3}(?:\.\d{3})+|\d+)\s?(mil|k)?\s?(\+)?\s+(?:de\s+)?"
                    r"(alunos|formados|veterin\w+|profissionais|estudantes|professores)")
OFICIAIS = {("12000", "alunos"), ("300", "professores")}  # sempre com o "+" depois: "12.000+ alunos", "300+ professores"


def numeros_da_marca(texto):
    """números de alunos e professores fora da forma oficial (ignora os pequenos: "25 alunos da turma")"""
    ruins = []
    for m in NUMERO.finditer(texto):
        n = int(m.group(2).replace(".", "")) * (1000 if m.group(3) else 1)
        quem = m.group(5).lower()
        if n < (100 if quem == "professores" else 1000):
            continue
        escrita_oficial = m.group(4) and not m.group(1) and not m.group(3) and (n < 1000 or "." in m.group(2))  # "12.000+", "300+"
        certo = (str(n), quem) in OFICIAIS and escrita_oficial
        if not certo:
            ruins.append(m.group(0).strip())
    return ruins


SIGLAS = ("RNGB", "NGB", "CMCB", "GPL", "SA", "PC", "PS", "CBEA", "CMMV", "QSAOA", "SUZ", "GPERA", "PPT", "MIFV", "GIA",
          "GCC", "CRCV", "GPDCA", "MVPA")  # as do regras/marca.md (o teste confere)
COMENTE_OK = {}  # palavra -> perfil, só as que têm automação ligada (regras/oficio/copy.md); vazio até confirmar

AVISOS = [
    (r"(?i)\bcomente\s+[\"“']?([A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,})", "\"Comente X\" só com palavra que tem automação ligada no perfil: confirmar com quem pediu"),
    (r"(?i)\b(estás|connosco|equipa|ecrã|facto|tu\s+(podes|queres|tens|és|vais))\b", "português de Portugal: escrever como no Brasil, com \"você\""),
    (r"(?i)reconhecid[oa] pelo MEC", 'a prova oficial é "Nota máxima (5) no MEC" (marca.md)'),
    (r"(?i)\b(marque (um|uma|seus?|suas?|o|a) \w+|comente (sim|eu quero|eu)\b|compartilhe com)", "isca de engajamento tira o post da recomendação (Meta): só com algo real por trás (copy.md)"),
    (r"\bNão é [^.!?\n]{1,60}[.!?]\s+É\b", '"Não é X. É Y." soa a texto de IA (a frase de marca "Não é só mais uma pós-graduação" pode)'),
    (r"(?i)\b(nos dias de hoje|no cenário atual|cada vez mais|mergulh\w+|jornada|alavanc\w+|potencializ\w+|desbrav\w+|"
     r"contribuir para a formação|profissionais qualificados|transformador\w*|revolucion\w+|desvend\w+)", "palavra vazia ou de academiquês: trocar por algo concreto"),
    (r"(?i)\b(você|vc)\s+(tem|está|é|sofre|anda)\b[^.?!\n]{0,40}\b(doen\w+|depress\w+|ansiedade|endividad\w+|dívida|desempregad\w+|\d+\s+anos)",
     "anúncio não pode afirmar atributo pessoal de quem lê (saúde, finanças, idade): política de anúncios da Meta"),
]


def checar(texto, tipo, titulo=""):
    """devolve (falhas, avisos), cada um uma lista de frases"""
    falhas, avisos = [], []
    for rx, porque in FALHAS:
        m = re.search(rx, texto, re.M)
        if m:
            falhas.append(f'"{m.group(0).strip()}": {porque}')
    for r in numeros_da_marca(texto):
        falhas.append(f'"{r}": número da marca só como no marca.md ("12.000+ alunos ativos", "300+ professores"); número novo só com fonte')
    for rx, porque in AVISOS:
        if rx.startswith("(?i)\\b(você") and tipo != "anuncio":
            continue
        m = re.search(rx, texto, re.M)
        if m and not (porque.startswith('"Comente') and m.group(1).upper() in COMENTE_OK):
            avisos.append(f'"{m.group(0).strip()}": {porque}')
    n = len(texto)
    if n > LIMITES[tipo]:
        (falhas if tipo == "legenda" else avisos).append(f"{n} caracteres (limite {LIMITES[tipo]} para {tipo})")
    primeira = next((l for l in texto.splitlines() if l.strip()), "")
    if tipo in ("legenda", "anuncio") and len(primeira) > VISIVEL:
        avisos.append(f"a 1ª linha tem {len(primeira)} caracteres: só ~{VISIVEL} aparecem antes do \"mais\"")
    tags = re.findall(r"(?<!\w)#\w+", texto)
    if tipo == "legenda" and len(tags) > 5:  # o app limita a 5 (dez/2025); pelo agendador (API) ainda passam até 30
        avisos.append(f"{len(tags)} hashtags: usar até 5 (limite do app do Instagram)")
    if tipo != "legenda" and tags:
        avisos.append(f"hashtag em {tipo}: só faz sentido na legenda")
    if texto.count("✅") >= 3:
        avisos.append("lista de ✅ em série soa a template")
    linhas = [l for l in texto.splitlines() if l.strip()]
    if tipo == "whatsapp" and len(linhas) > 5:
        avisos.append(f"{len(linhas)} linhas no WhatsApp: acima de 5 o app corta com \"ler mais\"")
    for s in SIGLAS:
        if re.search(rf"(?<![#\w]){s}(?!\w)", texto) and not re.search(rf"\({s}\)", texto):
            avisos.append(f'sigla "{s}" sozinha: escrever o nome da pós por extenso antes (copy.md)')
            break
    links = re.findall(r"https?://\S+", texto)
    if tipo == "anuncio" and links:
        avisos.append("link no texto do anúncio: o destino vai no campo do link e o UTM no modelo de parâmetros da plataforma")
    for l in links:
        if re.search(r"(ppgvet\.com\.br|ppgeducacao\.com\.br)", l) and "utm_source=" not in l and tipo != "anuncio":
            avisos.append(f"{l}: link de site nosso sem UTM; pegar no gerador \"Links com UTM\" do sistema")
    if tipo == "whatsapp" and len(links) > 1:
        avisos.append("mais de um link no WhatsApp: uma ação só")
    if tipo == "anuncio" and titulo and len(titulo) > 40:
        avisos.append(f"título do anúncio com {len(titulo)} caracteres: a Meta recomenda até 40")
    return falhas, avisos


def teste():
    f, a = checar("Conheça o MBA em gestão — vagas abertas", "legenda")
    assert len(f) == 2, f
    f, _ = checar("Aula com Prof. João Silva e Dra. Ana Souza", "arte")
    assert len(f) == 1 and "Prof." in f[0], f
    f, _ = checar("Somos +12.000 alunos e 260 professores", "legenda")
    assert len(f) == 2, f
    for ruim in ("15 mil veterinários formados", "mais de 12 mil alunos", "12K alunos", "12.000 alunos", "12000+ alunos"):
        assert checar(ruim, "legenda")[0], ruim
    assert not checar("Os 25 alunos da turma e os 12 professores do módulo", "legenda")[0]
    f, _ = checar("Mais de 12.000+ alunos ativos e 300+ professores", "legenda")
    assert not f, f
    assert any("hashtags" in x for x in checar("texto\n" + " ".join(f"#t{i}" for i in range(6)), "legenda")[1])
    f, a = checar("Não é só mais uma pós-graduação. É prática todo dia.", "legenda")
    assert not f and a, a
    _, a = checar("Você está endividado e com 40 anos? Mude de área.", "anuncio", "Título com mais de quarenta caracteres aqui dentro")
    assert any("atributo pessoal" in x for x in a) and any("título" in x for x in a), a
    _, a = checar("Veja https://site.ppgvet.com.br/pos-sa e https://site.ppgvet.com.br/pos-pc?utm_source=whatsapp", "whatsapp")
    assert sum("sem UTM" in x for x in a) == 1 and any("uma ação só" in x for x in a), a
    _, a = checar("Comente PÓS que eu te mando o link", "legenda")
    assert any("automação" in x for x in a), a
    f, a = checar("Somos 12 mil profissionais formados. **Inscreva-se** #medicinavetrinaria. Reconhecido pelo MEC, estás à espera?", "legenda")
    assert len(f) >= 3 and len(a) >= 2, (f, a)
    f, _ = checar("Aula nova #medicinaveterinaria #ppgeducacao", "legenda")
    assert not f, f
    import os  # as siglas têm que ser as do regras/marca.md
    md = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "regras", "marca.md"), encoding="utf-8").read()
    assert set(SIGLAS) == set(re.findall(r"^\| ([A-Z]+) \| [^|]+ \| (?:PPGVET|PPG) \|", md, re.M))
    _, a = checar("Pós em Postura Comercial (PC) com aula nova. Marque um amigo que precisa ver!", "legenda")
    assert any("isca" in x for x in a) and not any("sigla" in x for x in a), a
    _, a = checar("Aula nova da CMCB na quinta", "legenda")
    assert any("sigla" in x for x in a), a
    _, a = checar("\n".join(["linha"] * 6), "whatsapp")
    assert any("linhas" in x for x in a), a
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    elif len(sys.argv) >= 4 and "--tipo" in sys.argv:
        tipo = sys.argv[sys.argv.index("--tipo") + 1]
        assert tipo in LIMITES, f"tipo: {', '.join(LIMITES)}"
        titulo = sys.argv[sys.argv.index("--titulo") + 1] if "--titulo" in sys.argv else ""
        f, a = checar(open(sys.argv[1], encoding="utf-8").read(), tipo, titulo)
        for x in f:
            print("FALHA:", x)
        for x in a:
            print("AVISO:", x)
        print("ok" if not f else f"{len(f)} falha(s)")
        sys.exit(1 if f else 0)
    else:
        sys.exit(__doc__)
