#!/usr/bin/env python3
"""Gera o projeto HyperFrames (camada de motion) de um vídeo vertical de fala a partir do roteiro.json + legenda.srt.
Fundo: tmp/base.mov (fala já cortada). Por cima: caixinha de pergunta, cartões de destaque e legenda animada.
uso: hf.py pasta/roteiro.json   -> pasta/hf/ (depois: render)"""
import html, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reels import trechos, mapa  # noqa: E402
from comum import baixo, FF, acervo, dur  # noqa: E402

ACERVO = acervo()
LOGOS = acervo("logos")
# cores e logos por marca (marca.md do pacote); nunca misturar PPGVET e PPG
MARCAS = {
    "ppgvet": {"icone": f"{LOGOS}/ppgvet/ppgvet-icon-180.png", "logo": f"{LOGOS}/ppgvet/logo-ppgvet.png",
               "cor": "#D24BA8", "acao": "#00B7AB", "destaque": "#E371C0"},
    # shortcut: destaque da legenda PPG ainda não aprovado pelo usuário (usa o teal da marca); confirmar no 1º vídeo PPG
    "ppg": {"icone": f"{LOGOS}/ppg/icone-ppg.png", "logo": f"{LOGOS}/ppg/logo-ppg-educacao.png",
            "cor": "#1670C2", "acao": "#00ADA3", "destaque": "#00ADA3"},
}
W, H = 1080, 1920
LEG_Y = 915           # topo da legenda: no peito, logo abaixo do queixo
CARD_Y = 1035         # topo dos cartões: abaixo da legenda, acima do logo (1470)
PERG_Y = 1010         # topo da caixinha (avatar incluso)
ROW = 44              # altura de cada item da lista
ENTRADAS = ("palavras", "wipe", "bate")  # rodízio do título do cartão; "odometro" quando o cartão tem número


def numero(tok):
    """palavra que é só número (até 4 dígitos, com % ou + no fim): vira odômetro"""
    m = re.fullmatch(r"\*?(\d{1,4})[%+]?\*?", tok)
    return int(m.group(1)) if m else None


def escolher_entradas(destaques):
    """entrada de cada cartão: a do roteiro ou a próxima do rodízio, nunca a mesma do cartão anterior
    (regras/antislop-midia.md); cartão com número ganha o odômetro"""
    out, ant, k = [], None, 0
    for c in destaques:
        e = c.get("entrada")
        if not e and ant != "odometro" and any(numero(x) is not None for x in " ".join(c["linhas"]).split()):
            e = "odometro"
        while not e or e == ant and "entrada" not in c:
            e, k = ENTRADAS[k % len(ENTRADAS)], k + 1
        out.append(e)
        ant = e
    return out


def marcar(txt):
    """*palavra* -> span de destaque; resto escapado."""
    partes = re.split(r"(\*[^*]+\*)", txt)
    return "".join(f'<span class="hl">{html.escape(p[1:-1])}</span>' if p.startswith("*") else html.escape(p) for p in partes)


def palavras_html(txt, cls="w"):
    """Quebra em palavras (mantendo destaque) para animar uma a uma."""
    out, hl = [], False
    for tok in re.split(r"(\s+)", txt):
        if not tok.strip():
            continue
        abre, fecha = tok.startswith("*"), "*" in tok[1:]
        hl = hl or abre
        out.append(f'<span class="{cls}{" hl" if hl else ""}">{html.escape(tok.replace("*", ""))}</span>')
        if fecha: hl = False
    return " ".join(out)


CSS_BASE = """
@font-face { font-family: 'MontserratV'; src: url('assets/fonts/montserrat-variavel.ttf'); font-weight: 100 900; }
"""
M = MARCAS["ppgvet"]  # trocado em main() conforme o roteiro


def comp(cid, corpo, css, js, dur_s):
    return f"""<template>
  <style>{CSS_BASE}
    #root {{ position: absolute; inset: 0; font-family: 'MontserratV', Montserrat, sans-serif; }}
    {css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-layout-allow-overflow>
{corpo}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    tl.set({{}}, {{}}, {dur_s:.3f});
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def pergunta(texto, ate):
    larg = 720 if len(texto) <= 40 else 880  # pergunta longa: caixinha mais larga para caber em 2 linhas
    fq = 48 if len(texto) <= 50 else 42
    css = f"""
    .stk {{ position: absolute; left: {(W - larg) // 2}px; top: {PERG_Y}px; width: {larg}px; }}
    .stk-card {{ margin-top: 54px; border-radius: 40px; overflow: hidden; background: #fff;
                 box-shadow: 0 28px 70px rgba(0,0,0,.38), 0 6px 18px rgba(0,0,0,.18); }}
    .stk-top {{ background: {M["cor"]}; color: #fff; font-weight: 600; font-size: 28px; text-align: center;
                padding: 66px 40px 20px; letter-spacing: .2px; }}
    .stk-q {{ color: #1A1A1A; font-weight: 750; font-size: {fq}px; line-height: 1.14; text-align: center;
              padding: 26px 46px 32px; letter-spacing: -.3px; }}
    .stk-q .w {{ display: inline-block; }}
    .stk-av {{ position: absolute; left: 50%; top: 0; width: 108px; height: 108px; margin-left: -54px;
               border-radius: 50%; background: #FAF9FB; border: 7px solid #fff;
               box-shadow: 0 8px 22px rgba(0,0,0,.22); display: grid; place-items: center; z-index: 2; }}
    .stk-av img {{ width: 78px; }}"""
    corpo = f"""    <div id="stk" class="stk">
      <div id="stk-av" class="stk-av"><img src="assets/icone.png" alt=""></div>
      <div id="stk-card" class="stk-card">
        <div id="stk-top" class="stk-top">Faça uma pergunta</div>
        <div id="stk-q" class="stk-q">{palavras_html(texto)}</div>
      </div>
    </div>"""
    js = f"""    tl.fromTo("#stk", {{ scale: .55, opacity: 0, transformOrigin: "50% 60%" }},
              {{ scale: 1, opacity: 1, duration: .6, ease: "back.out(1.5)" }}, .05);
    tl.fromTo("#stk-av", {{ scale: 0 }}, {{ scale: 1, duration: .45, ease: "back.out(2.2)" }}, .22);
    tl.fromTo("#stk-top", {{ opacity: 0 }}, {{ opacity: 1, duration: .25, ease: "power2.out" }}, .25);
    tl.fromTo("#stk-q .w", {{ opacity: 0, filter: "blur(6px)" }},
              {{ opacity: 1, filter: "blur(0px)", duration: .16, ease: "power2.out", stagger: .07 }}, .38);
    tl.to("#stk", {{ scale: .9, opacity: 0, filter: "blur(8px)", duration: .26, ease: "power3.in" }}, {ate - 0.26:.3f});"""
    return comp("pergunta", corpo, css, js, ate)


def cartao(i, c, d_total, itens_rel, entrada="palavras"):
    """Cartão branco com barra na cor da marca; o título entra pela `entrada` (palavras, wipe, bate, odometro);
    lista com check que se desenha."""
    cid = f"cartao{i}"
    linhas = " ".join(c["linhas"])
    itens = c.get("itens", [])
    alvo = next((numero(x) for x in linhas.split() if numero(x) is not None), None)
    titulo = palavras_html(linhas)
    if entrada == "odometro" and alvo is not None:  # o número conta de 0 até ele
        titulo = re.sub(r'>(\d{1,4})(?=[%+]?</span>)', r'><span class="n">\1</span>', titulo, count=1)
    css = f"""
    .cd-wrap {{ position: absolute; left: 70px; top: {CARD_Y}px; width: 940px;
                filter: drop-shadow(0 22px 40px rgba(0,0,0,.34)) drop-shadow(0 4px 10px rgba(0,0,0,.16)); }}
    .cd {{ position: relative; background: #fff; border-radius: 28px; padding: 22px 40px 24px 58px; }}
    .cd-bar {{ position: absolute; left: 0; top: 0; bottom: 0; width: 14px; background: {M["cor"]};
               border-radius: 30px 0 0 30px; transform-origin: 50% 0; }}
    .cd-t {{ color: #1A1A1A; font-weight: 750; font-size: 46px; line-height: 1.16; letter-spacing: -.5px; }}
    .cd-t .w {{ display: inline-block; position: relative; }}
    .cd-t {{ position: relative; }}
    .cd-luz {{ position: absolute; top: -8px; bottom: -8px; width: 6px; left: 0; border-radius: 3px; opacity: 0;
               background: #fff; box-shadow: 0 0 14px 4px {M["acao"]}, 0 0 4px 2px {M["acao"]}; }}
    .cd-t .hl {{ color: {M["cor"]}; }}
    .cd-it {{ display: flex; align-items: center; gap: 22px; height: {ROW}px; margin-top: 6px; }}
    .cd-it:first-of-type {{ margin-top: 12px; }}
    .cd-ck {{ width: 36px; height: 36px; flex: none; }}
    .cd-tx {{ color: #1A1A1A; font-weight: 600; font-size: 37px; letter-spacing: -.2px; }}"""
    it_html = "".join(
        f"""
        <div class="cd-it" id="{cid}-it{k}">
          <svg class="cd-ck" id="{cid}-ck{k}" viewBox="0 0 46 46"><circle cx="23" cy="23" r="23" fill="{M["acao"]}"/>
            <path id="{cid}-cp{k}" d="M13 23.5l6.5 6.5L33 16.5" fill="none" stroke="#fff" stroke-width="5"
              stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="32" stroke-dashoffset="32"/></svg>
          <div class="cd-tx" id="{cid}-tx{k}">{html.escape(t)}</div>
        </div>""" for k, t in enumerate(itens))
    corpo = f"""    <div id="{cid}-wrap" class="cd-wrap">
      <div id="{cid}-cd" class="cd">
        <div id="{cid}-bar" class="cd-bar"></div>
        <div id="{cid}-t" class="cd-t"><div id="{cid}-tt">{titulo}</div><div id="{cid}-luz" class="cd-luz"></div></div>{it_html}
      </div>
    </div>"""
    n = len(itens)
    # recorte de baixo: esconde os itens que ainda não entraram (o cartão cresce para baixo)
    inset = lambda k: f"inset(0px 0px {(n - k) * (ROW + 6) + (12 if k == 0 and n else 0)}px 0px round 30px)"
    js = f"""    tl.fromTo("#{cid}-cd", {{ clipPath: "inset(0px 100% {(n) * (ROW + 6) + (12 if n else 0)}px 0px round 30px)" }},
              {{ clipPath: "{inset(0)}", duration: .55, ease: "expo.out" }}, 0);
    tl.fromTo("#{cid}-bar", {{ scaleY: 0 }}, {{ scaleY: 1, duration: .4, ease: "expo.out" }}, 0);
    tl.fromTo("#{cid}-wrap", {{ y: 26 }}, {{ y: 0, duration: .6, ease: "expo.out" }}, 0);
{entrada_js(cid, entrada, alvo)}"""
    if "*" in linhas:
        js += f"""
    tl.fromTo("#{cid}-t .hl", {{ color: "#1A1A1A" }}, {{ color: "{M["cor"]}", duration: .3, ease: "power2.out" }}, .55);"""
    for k, t0 in enumerate(itens_rel):
        js += f"""
    tl.to("#{cid}-cd", {{ clipPath: "{inset(k + 1)}", duration: .45, ease: "expo.out" }}, {t0:.3f});
    tl.fromTo("#{cid}-ck{k}", {{ scale: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: .4, ease: "back.out(2)" }}, {t0 + 0.05:.3f});
    tl.fromTo("#{cid}-cp{k}", {{ strokeDashoffset: 32 }}, {{ strokeDashoffset: 0, duration: .3, ease: "power2.out" }}, {t0 + 0.2:.3f});
    tl.fromTo("#{cid}-tx{k}", {{ opacity: 0, x: -18, filter: "blur(5px)" }},
              {{ opacity: 1, x: 0, filter: "blur(0px)", duration: .3, ease: "power3.out" }}, {t0 + 0.1:.3f});"""
    js += f"""
    tl.to("#{cid}-wrap", {{ opacity: 0, y: -10, filter: "blur(8px)", duration: .26, ease: "power3.in" }}, {d_total - 0.27:.3f});"""
    return comp(cid, corpo, css, js, d_total)


def entrada_js(cid, entrada, alvo):
    """como o título do cartão entra (curvas e durações: regras/oficio/motion.md)"""
    w = f"#{cid}-t .w"
    if entrada == "bate":  # letra que bate: grande e desfocada, assenta no tamanho
        return f"""    tl.fromTo("{w}", {{ opacity: 0, scale: 1.7, filter: "blur(10px)", transformOrigin: "50% 60%" }},
              {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: .34, ease: "expo.out", stagger: .07 }}, .18);"""
    if entrada == "wipe":  # o texto se revela da esquerda, com uma borda de luz na cor de ação
        return f"""    tl.fromTo("#{cid}-tt", {{ clipPath: "inset(0px 100% 0px 0px)" }},
              {{ clipPath: "inset(0px 0% 0px 0px)", duration: .7, ease: "expo.out" }}, .18);
    tl.fromTo("#{cid}-luz", {{ left: "0%", opacity: 1 }}, {{ left: "100%", duration: .7, ease: "expo.out" }}, .18);
    tl.to("#{cid}-luz", {{ opacity: 0, duration: .25, ease: "power2.out" }}, .62);"""
    js = f"""    tl.fromTo("{w}", {{ opacity: 0, filter: "blur(6px)" }},
              {{ opacity: 1, filter: "blur(0px)", duration: .16, ease: "power2.out", stagger: .06 }}, .18);"""
    if entrada == "odometro" and alvo is not None:
        js += f"""
    tl.fromTo("#{cid}-t .n", {{ innerText: 0 }}, {{ innerText: {alvo}, snap: {{ innerText: 1 }}, duration: .9, ease: "expo.out" }}, .22);"""
    return js


def legenda(grupos, d_total):
    """Legenda simples: o grupo entra inteiro (fade curto), branco com sombra; *palavra-chave* em rosa."""
    css = f"""
    .lg {{ position: absolute; left: 0; width: {W}px; top: {LEG_Y}px; text-align: center; padding: 0 70px;
           box-sizing: border-box; color: #fff; font-weight: 800; font-size: 62px; line-height: 1.12;
           letter-spacing: -.3px; opacity: 0;
           text-shadow: 0 3px 2px rgba(0,0,0,.35), 0 6px 22px rgba(0,0,0,.55);
           -webkit-text-stroke: 7px rgba(0,0,0,.55); paint-order: stroke fill; }}  /* contorno: lê em fundo claro */
    .lg .hl {{ color: {M["destaque"]}; }}"""
    corpo, js = [], []
    for gi, (a, b, txt) in enumerate(grupos):
        gid = f"lg{gi}"
        corpo.append(f'    <div id="{gid}" class="lg">{marcar(txt)}</div>')
        js.append(f'    tl.fromTo("#{gid}", {{ opacity: 0 }}, {{ opacity: 1, duration: .08, ease: "power1.out" }}, {a:.3f});')
        js.append(f'    tl.set("#{gid}", {{ opacity: 0, visibility: "hidden" }}, {b:.3f});')
    return comp("legenda", "\n".join(corpo), css, "\n".join(js), d_total)


def ler_srt(srt, d_total):
    gs = []
    for bl in re.split(r"\n\s*\n", open(srt, encoding="utf-8").read().strip()):
        p = bl.strip().splitlines()
        t = [int(x) for x in re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", p[1]).groups()]
        a = t[0] * 3600 + t[1] * 60 + t[2] + t[3] / 1000
        b = t[4] * 3600 + t[5] * 60 + t[6] + t[7] / 1000
        gs.append([max(a, 0.12), min(b, d_total - 0.05), " ".join(p[2:])])
    for i in range(len(gs) - 1):  # um grupo por vez: fecha quando o próximo abre
        gs[i][1] = min(gs[i][1], gs[i + 1][0])
    return gs


def main(rot):
    pasta = os.path.dirname(os.path.abspath(rot))
    r = json.load(open(rot, encoding="utf-8"))
    tr = trechos(r); f, _ = mapa(tr)
    hf = f"{pasta}/hf"
    os.makedirs(f"{hf}/assets/fonts", exist_ok=True); os.makedirs(f"{hf}/compositions", exist_ok=True)
    base = f"{hf}/assets/base.mp4"
    if not os.path.exists(base) or os.path.getmtime(base) < os.path.getmtime(f"{pasta}/tmp/base.mov"):
        # keyframe a cada segundo (seek preciso no render), sem áudio: a mixagem é feita depois no ffmpeg
        baixo([FF(), "-v", "error", "-y", "-i", f"{pasta}/tmp/base.mov", "-an", "-c:v", "libx264",
                        "-crf", "14", "-preset", "fast", "-g", "30", "-pix_fmt", "yuv420p", base], check=True)
    shutil.copy(f"{ACERVO}/fontes/montserrat-variavel.ttf", f"{hf}/assets/fonts/")
    global M
    M = MARCAS[r.get("marca", "ppgvet")]
    shutil.copy(M["icone"], f"{hf}/assets/icone.png")
    shutil.copy(M["logo"], f"{hf}/assets/logo.png")
    D = round(dur(base), 3)

    hosts = []
    # logo da marca embaixo o vídeo todo: 210 px, y 1470..1604 (dentro do recorte 4:5 do feed, que vai até y=1635)
    open(f"{hf}/compositions/marca.html", "w", encoding="utf-8").write(comp("marca",
        f'    <img id="mc-logo" src="assets/logo.png" alt="" style="position:absolute;left:{(W - 210) // 2}px;top:1470px;width:210px;height:auto">',
        "", '    tl.set("#mc-logo", { opacity: 1 }, 0);  // logo fixa desde o primeiro quadro (pedido do usuário)', D))
    hosts.append(("marca", 0, D, "graphics", 2))
    p = r.get("pergunta")
    if p:  # sem "de": abre o vídeo e dura "ate" s; com "de": entra e sai nesses tempos do original
        p0 = f(p["de"]) if "de" in p else 0.0
        pd = (f(p["ate"]) - p0) if "de" in p else p.get("ate", 3.4)
        open(f"{hf}/compositions/pergunta.html", "w", encoding="utf-8").write(pergunta(p["texto"], pd))
        hosts.append(("pergunta", p0, pd, "graphics", 3))
    entradas = escolher_entradas(r.get("destaques", []))
    for i, c in enumerate(r.get("destaques", [])):
        de, ate = f(c["de"]), f(c["ate"])
        rel = [f(t) - de for t in c.get("itens_em", [])]
        open(f"{hf}/compositions/cartao{i}.html", "w", encoding="utf-8").write(cartao(i, c, ate - de, rel, entradas[i]))
        hosts.append((f"cartao{i}", de, ate - de, "graphics", 4 + i))
    open(f"{hf}/compositions/legenda.html", "w", encoding="utf-8").write(legenda(ler_srt(f"{pasta}/legenda.srt", D), D))
    hosts.append(("legenda", 0, D, "captions", 20))

    host_html = "\n".join(
        f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" '
        f'data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="{ti}" data-track-kind="{k}" '
        f'data-width="{W}" data-height="{H}" style="z-index:{ti}"></div>' for h, a, d, k, ti in hosts)
    open(f"{hf}/index.html", "w", encoding="utf-8").write(f"""<!doctype html>
<html>
  <head><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script></head>
  <body style="margin:0;background:#000">
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{W}" data-height="{H}">
      <video id="fala" class="clip" data-start="0" data-duration="{D}" data-track-index="0" src="assets/base.mp4"
        muted playsinline style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;z-index:1"></video>
{host_html}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    print("projeto:", hf, f"{D}s")


def teste():
    assert numero("30") == 30 and numero("*90%*") == 90 and numero("+3") is None and numero("3.000") is None
    cs = [{"linhas": ["sem número"]}, {"linhas": ["outro"]}, {"linhas": ["*30* dias"]}, {"linhas": ["mais 12"]},
          {"linhas": ["fim"]}, {"linhas": ["x"], "entrada": "bate"}]
    e = escolher_entradas(cs)
    assert e == ["palavras", "wipe", "odometro", "bate", "palavras", "bate"], e
    assert all(a != b for a, b in zip(e[:-2], e[1:-1]))                # o rodízio nunca repete seguido
    h = cartao(0, {"linhas": ["*30* dias"]}, 3.0, [], "odometro")
    assert '<span class="n">30</span>' in h and "innerText: 30" in h
    assert "clipPath" in cartao(1, {"linhas": ["oi"]}, 3.0, [], "wipe") and "scale: 1.7" in cartao(2, {"linhas": ["oi"]}, 3.0, [], "bate")
    print("ok")


if __name__ == "__main__":
    teste() if sys.argv[1:] == ["--teste"] else main(sys.argv[1])
