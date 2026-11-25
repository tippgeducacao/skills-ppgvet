#!/usr/bin/env python3
"""Link com UTM pela regra do regras/canais.md (a mesma do gerador "Links com UTM" do sistema, que continua sendo o dono).
uso: utm.py gerar <página> --rede instagram --perfil ppgvet [--campanha escola] [--peca bio]
     utm.py arrumar <link>        formato antigo para o novo (como o "Arrumar" do gerador), tira UTM e click ID de onde não pode
     utm.py conferir <link>       FALHA e AVISO de um link
     utm.py --teste
O link montado aqui é conferido no gerador antes de sair (regra do canais.md)."""
import re, sys, unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

PERFIS = {"instagram": {"ppgvet", "ppgeducacao", "aviario", "suinocast", "maisrumen", "petfood", "avesesuinos",
                        "academiadapecuaria", "academiasuina"},
          "tiktok": {"ppgvet"}, "linkedin": {"ppgvet"}, "youtube": {"ppgvet", "aviario", "suinocast", "maisrumen", "petfood"}}
SEM_PERFIL = {"whatsapp", "email"}  # só a rede
MEIO = {"email": "email"}  # o resto é social (YouTube também)
CLIQUE = ("fbclid", "gclid", "gbraid", "wbraid", "ttclid", "msclkid", "li_fat_id", "dclid")
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
NOME = re.compile(rf"^[a-z]+(?:-[a-z]+)*(?:-(?:{'|'.join(MESES)}|q[1-4])-20\d\d)?$")  # minúsculo, hífen, data só no fim
ANTIGO_MEIO = {"bio", "story", "grupo", "paid", "sdr", "sac", "ia", "automacao", "lembrete"}
ANTIGO_TERMO = {"bio", "story", "dm", "sdr", "sac", "ia", "automacao"}
APELIDO = {"ig": "instagram", "yt": "youtube", "wpp": "whatsapp", "zap": "whatsapp", "li": "linkedin", "tt": "tiktok"}


def nosso(host):
    return bool(re.search(r"(^|\.)(ppgvet|ppgeducacao)\.com\.br$", host or ""))


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def partes(link):
    u = urlsplit(link.strip())
    return u, dict(parse_qsl(u.query, keep_blank_values=True))


def montar(u, q):
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), u.fragment))


def gerar(pagina, rede, perfil="", campanha="", peca=""):
    rede = APELIDO.get(rede, rede)
    u, q = partes(pagina)
    if not nosso(u.hostname):
        raise SystemExit(f"{u.hostname}: só página de site nosso (ppgvet.com.br, ppgeducacao.com.br) leva UTM")
    if rede not in PERFIS and rede not in SEM_PERFIL:
        raise SystemExit(f'rede "{rede}": use {", ".join(sorted(set(PERFIS) | SEM_PERFIL))}')
    if rede in PERFIS and perfil not in PERFIS[rede]:
        raise SystemExit(f'perfil "{perfil}" do {rede}: use {", ".join(sorted(PERFIS[rede]))} (perfil pessoal: pelo gerador do sistema)')
    q = {k: v for k, v in q.items() if not k.startswith("utm_") and k not in CLIQUE}
    q["utm_source"] = rede if rede in SEM_PERFIL else f"{rede}-{perfil}"
    q["utm_medium"] = MEIO.get(rede, "social")
    if campanha:
        q["utm_campaign"] = slug(campanha)
    if peca:
        q["utm_content"] = slug(peca)
    return montar(u, q)


def conferir(link, tipo=""):
    """(falhas, avisos) de um link; tipo "anuncio": o UTM vai nos parâmetros da plataforma, não no link"""
    falhas, avisos = [], []
    u, q = partes(link)
    utm = {k: v for k, v in q.items() if k.startswith("utm_")}
    for k in CLIQUE:
        if k in q:
            falhas.append(f"{k} no link: click ID nunca vai escrito no link")
    if not nosso(u.hostname):
        if utm:
            falhas.append(f"{u.hostname}: link para fora vai sem UTM")
        return falhas, avisos
    if tipo == "anuncio":
        if utm:
            falhas.append("anúncio: o UTM vai no modelo de parâmetros da plataforma (no gerador), não no link")
        return falhas, avisos
    src, meio = q.get("utm_source", ""), q.get("utm_medium", "")
    if not src:
        falhas.append("link de site nosso sem UTM: pegar no gerador \"Links com UTM\" (ou utm.py gerar e conferir lá)")
        return falhas, avisos
    if src.startswith("teste"):
        avisos.append("link de teste (utm_source=teste…): nunca no ar")
        return falhas, avisos
    rede, _, perfil = src.partition("-")
    if "_" in src or src in APELIDO or rede in APELIDO:
        falhas.append(f'utm_source "{src}": formato antigo; o certo é <rede>-<perfil> (instagram-ppgvet) ou só a rede (whatsapp) — utm.py arrumar')
    elif rede in SEM_PERFIL and perfil:
        falhas.append(f'utm_source "{src}": {rede} vai só com a rede, sem perfil nem grupo')
    elif rede in PERFIS and perfil not in PERFIS[rede]:
        avisos.append(f'utm_source "{src}": perfil fora da lista; perfil pessoal sai do gerador')
    elif rede not in PERFIS and rede not in SEM_PERFIL:
        falhas.append(f'utm_source "{src}": rede desconhecida')
    certo = MEIO.get(APELIDO.get(rede, rede), "social")
    if meio != certo:
        falhas.append(f'utm_medium "{meio}": o certo para {rede} é "{certo}"')
    for campo in ("utm_campaign", "utm_content"):
        v = q.get(campo)
        if v and not NOME.match(v) and not re.fullmatch(r"[a-z]+(?:-[a-z]+)*-qr-code(?:-[a-z]{3}-20\d\d)?", v):
            falhas.append(f'{campo} "{v}": minúsculo, palavras com hífen, sem número (data só no fim: nov-2026)')
    if q.get("utm_term"):
        avisos.append("utm_term não se usa no orgânico")
    return falhas, avisos


def arrumar(link):
    """(link novo, mudanças): o que dá para consertar sem perguntar"""
    u, q = partes(link)
    mud = []
    for k in CLIQUE:
        if q.pop(k, None) is not None:
            mud.append(f"tirei {k}")
    if not nosso(u.hostname):
        if any(k.startswith("utm_") for k in q):
            q = {k: v for k, v in q.items() if not k.startswith("utm_")}
            mud.append("tirei o UTM (link para fora vai sem)")
        return montar(u, q), mud
    src = q.get("utm_source", "")
    if src:
        p = re.split(r"[-_]", src, maxsplit=1)  # instagram_ppgvet, ig_ppgvet, whatsapp-grupo-x
        rede, resto = APELIDO.get(p[0], p[0]), (p[1] if len(p) > 1 else "")
        novo = rede if rede in SEM_PERFIL else (f"{rede}-{resto}" if resto else src)
        if novo != src:
            q["utm_source"] = novo
            mud.append(f"utm_source {src} → {novo}")
        if rede in PERFIS and not resto:
            mud.append(f'utm_source "{src}": falta o perfil ({", ".join(sorted(PERFIS[rede]))}); não dá para adivinhar')
        meio = MEIO.get(rede, "social")
        termo = q.get("utm_term", "")
        lugar = q.get("utm_medium") if q.get("utm_medium") in ("story", "dm") else termo if termo in ("story", "dm") else ""
        if q.get("utm_medium") != meio:
            mud.append(f'utm_medium {q.get("utm_medium", "(vazio)")} → {meio}')
            q["utm_medium"] = meio
        if termo in ANTIGO_TERMO:
            q.pop("utm_term")
            mud.append(f"tirei utm_term={termo} (formato antigo)")
        if lugar and not q.get("utm_content", "").startswith(lugar):
            q["utm_content"] = f"{lugar}-{q['utm_content']}" if q.get("utm_content") else lugar
            mud.append(f"utm_content começa por {lugar}")
    for campo in ("utm_campaign", "utm_content"):
        v = q.get(campo)
        if v:
            n = slug(v)
            m = re.search(r"-(20\d\d)-(\d\d)$", n)  # <tipo>-<oferta>-aaaa-mm antigo vira -mês-aaaa
            if m and 1 <= int(m.group(2)) <= 12:
                n = n[:m.start()] + f"-{MESES[int(m.group(2)) - 1]}-{m.group(1)}"
            if n != v:
                q[campo] = n
                mud.append(f"{campo} {v} → {n}")
    return montar(u, q), mud


def teste():
    g = gerar("https://site.ppgvet.com.br/pos-ngb", "instagram", "ppgvet", "Nova Turma", "bio")
    assert g == "https://site.ppgvet.com.br/pos-ngb?utm_source=instagram-ppgvet&utm_medium=social&utm_campaign=nova-turma&utm_content=bio", g
    assert gerar("https://site.ppgvet.com.br/x", "whatsapp", campanha="live").endswith("utm_source=whatsapp&utm_medium=social&utm_campaign=live")
    assert "utm_medium=email" in gerar("https://site.ppgeducacao.com.br/", "email")
    assert not any(conferir(g))  # o que o gerar monta passa
    f, _ = conferir("https://site.ppgvet.com.br/pos-sa?utm_source=instagram_ppgvet&utm_medium=bio&utm_campaign=Escola2026")
    assert len(f) == 3, f  # fonte antiga, meio errado, campanha fora do padrão
    assert conferir("https://www.youtube.com/watch?v=1&utm_source=instagram-ppgvet")[0]  # para fora, sem UTM
    assert conferir("https://site.ppgvet.com.br/x?fbclid=abc")[0]
    assert conferir("https://site.ppgvet.com.br/pos-ps")[0]  # nosso sem UTM
    assert conferir("https://site.ppgvet.com.br/x?utm_source=whatsapp-grupo-ps&utm_medium=social")[0]
    assert not conferir("https://site.ppgvet.com.br/x?utm_source=instagram-ppgvet&utm_medium=social&utm_campaign=natal-dez-2026&utm_content=bio-qr-code-nov-2026")[0]
    assert conferir("https://site.ppgvet.com.br/x?utm_source=ig&utm_medium=paid_social", "anuncio")[0]
    n, m = arrumar("https://site.ppgvet.com.br/pos-sa?utm_source=instagram_ppgvet&utm_medium=bio&utm_term=story&utm_campaign=live-sa-2026-11&fbclid=x")
    assert not conferir(n)[0], (n, conferir(n))
    assert "utm_source=instagram-ppgvet" in n and "utm_content=story" in n and "live-sa-nov-2026" in n and "fbclid" not in n, n
    n, _ = arrumar("https://open.spotify.com/show/1?utm_source=instagram-ppgvet")
    assert "utm_" not in n
    n, m = arrumar("https://site.ppgvet.com.br/x?utm_source=ig&utm_medium=bio")
    assert any("falta o perfil" in x for x in m), m  # não inventa o perfil
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    op = lambda k: a[a.index(k) + 1] if k in a else ""
    if a == ["--teste"]:
        teste()
    elif len(a) >= 2 and a[0] == "gerar":
        print(gerar(a[1], op("--rede"), op("--perfil"), op("--campanha"), op("--peca")))
        print("AVISO: conferir no gerador \"Links com UTM\" do sistema antes de publicar")
    elif len(a) == 2 and a[0] == "arrumar":
        novo, mud = arrumar(a[1])
        print(novo)
        for x in mud:
            print(" -", x)
        f, av = conferir(novo)
        for x in f:
            print("FALHA:", x)
        for x in av:
            print("AVISO:", x)
    elif len(a) == 2 and a[0] == "conferir":
        f, av = conferir(a[1])
        for x in f:
            print("FALHA:", x)
        for x in av:
            print("AVISO:", x)
        print("ok" if not f else f"{len(f)} falha(s)")
        sys.exit(1 if f else 0)
    else:
        sys.exit(__doc__)
