#!/usr/bin/env python3
"""Confere um texto de marketing antes de entregar (regras em regras/oficio/copy.md).
uso: checar_texto.py <arquivo.txt> --tipo legenda|arte|whatsapp|anuncio|roteiro|email|pauta [--titulo "<título do anúncio ou assunto do e-mail>"]
     checar_texto.py --teste
FALHA barra a entrega (corrigir e rodar de novo); AVISO é para olhar e decidir. Sai 1 se houver FALHA."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portao import registrar  # noqa: E402
import utm  # noqa: E402

LIMITES = {"legenda": 2200, "whatsapp": 600, "anuncio": 600, "arte": 400,  # legenda: limite do Instagram; os outros, da casa
           "roteiro": 1000, "email": 2000, "pauta": 8000}  # roteiro: ~150 palavras, 60 s de fala
VISIVEL = 125  # a legenda e o texto principal do anúncio mostram ~125 caracteres antes do "mais"

FALHAS = [  # (regex, por quê)
    (r"\bMBA\b", 'é "Pós-Graduação", nunca "MBA" (sempre.md)'),
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


SIGLAS = ("RNGB", "NGB", "CMCB", "GPL", "SA", "PC", "PS", "CBEA", "CMMV", "QSAOA", "SUZ", "GPERA", "PPT", "MIFV", "GIA", "MVA",
          "GCC", "CRCV", "GPDCA")  # as do regras/marca.md (o teste confere)
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
    (r"(?i)\b(vamos ser sinceros|sejamos honestos|a verdade é que|neste (post|vídeo|texto) (você|vc) vai|ficou alguma dúvida|espero que (tenha|isso) (ajudado|te ajude))",
     "abertura ou fecho de chatbot: começar pelo gancho e fechar na ação (copy.md)"),
    (r"(?i)\b(especialistas|estudos|pesquisas) (dizem|mostram|apontam|afirmam)\b", "autoridade sem dono: dizer quem, qual estudo ou o número (copy.md)"),
    (r"(?i)\b(e isso muda tudo|e é aí que entra|o futuro é promissor)", "fecho de efeito ou conclusão genérica: terminar no fato ou na ação (copy.md)"),
    (r"(?m)^\s*(\w+\.\s+){2,}\w+\.\s*$", "frase picotada (\"Simples. Direto. Eficaz.\"): dizer a uma coisa que importa (copy.md)"),
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
    emojis = re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705]", texto)
    if tipo == "arte" and emojis:
        falhas.append(f'emoji na arte ("{emojis[0]}"): sem emoji na peça; ícone só com função (antislop-midia.md)')
    elif len(emojis) > 3:
        avisos.append(f"{len(emojis)} emojis: no máximo 3, e só quando ajudam a ler")
    if texto.count("!") > 2:
        avisos.append(f'{texto.count("!")} exclamações: no máximo 2; a força vem do fato, não da pontuação')
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
    for l in links:  # regra do canais.md: UTM só em site nosso, no formato do gerador (scripts/utm.py)
        f_l, a_l = utm.conferir(l.rstrip(".,;:!?)"), tipo)
        falhas += [f"{l}: {x}" for x in f_l]
        avisos += [f"{l}: {x}" for x in a_l]
    if tipo == "whatsapp" and len(links) > 1:
        avisos.append("mais de um link no WhatsApp: uma ação só")
    if tipo == "anuncio" and titulo and len(titulo) > 40:
        avisos.append(f"título do anúncio com {len(titulo)} caracteres: a Meta recomenda até 40")
    if tipo == "email":
        if re.match(r"(?i)\s*(re|fwd?|enc|res)\s*:", titulo):
            falhas.append(f'assunto "{titulo}": "Re:" ou "Fwd:" falso engana quem lê (regras do Gmail)')
        if not re.search(r"(?i)descadastr|parar de receber|cancelar (a )?inscri|sair da lista", texto):
            avisos.append("sem link de descadastro no corpo: conferir se a ferramenta de envio põe (regras do Gmail)")
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
    f, a = checar("Veja https://site.ppgvet.com.br/pos-sa e https://site.ppgvet.com.br/pos-pc?utm_source=whatsapp&utm_medium=social", "whatsapp")
    assert sum("sem UTM" in x for x in f) == 1 and len(f) == 1 and any("uma ação só" in x for x in a), (f, a)
    f, _ = checar("Ouça no https://open.spotify.com/show/1?utm_source=instagram-ppgvet e no https://site.ppgvet.com.br/x?utm_source=ig_ppgvet&utm_medium=bio", "legenda")
    assert len(f) == 3, f  # UTM fora do nosso site, fonte antiga e meio errado
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
    f, a = checar("Olá, Ana. As inscrições abriram.", "email", "Re: sua inscrição")
    assert any("Re:" in x for x in f) and any("descadastro" in x for x in a), (f, a)
    f, a = checar("Olá, Ana. As inscrições abriram.\nPara parar de receber, clique aqui.", "email", "Inscrições abertas até sexta")
    assert not f and not a, (f, a)
    assert any("caracteres" in x for x in checar("fala " * 250, "roteiro")[1])
    _, a = checar("Vamos ser sinceros: estudos mostram que a granja mudou.\nSimples. Direto. Eficaz.\nE isso muda tudo.", "legenda")
    assert sum(any(k in x for x in a) for k in ("chatbot", "sem dono", "picotada", "fecho de efeito")) == 4, a
    assert not checar("Aula prática na granja, quinta às 19h. Link na bio.", "legenda")[1]  # texto normal não acende
    assert any("emoji" in x for x in checar("Aula nova 🐄", "arte")[0])
    assert any("emojis" in x for x in checar("🐄🐖🐔🐟 aula", "legenda")[1]) and not checar("Aula 🐄", "legenda")[1]
    assert any("exclamações" in x for x in checar("Vem! Corre! Agora!", "legenda")[1])
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
        registrar(sys.argv[1], not f, len(f))
        sys.exit(1 if f else 0)
    else:
        sys.exit(__doc__)
