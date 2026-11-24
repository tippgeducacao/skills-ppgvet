#!/usr/bin/env python3
"""Títulos das pós (acervo): logo colorido em 4x, logo branco (moldura do Instagram) e overlay 1920x1080 do vMix.
uso: live_titulos.py [sigla ...]    (sem sigla: todas)
Pós nova ou nome mudou: pôr a sigla e as linhas em POS (quebras iguais às dos criativos) e rodar só ela.
Saída: acervo/titulos-pos/titulo-pos-<sigla>.png e -branco.png; acervo/live/titulos-overlay/titulo-live-<sigla>.png"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo, print_html, url_arquivo  # noqa: E402

POS = {  # sigla: (linhas, sub) — "|" quebra a linha
    'rngb': ('Reprodução,|Nutrição e Gestão|de Bovinos', ''),
    'ngb': ('Nutrição e Gestão|de Bovinos', ''),
    'cmcb': ('Clínica Médica|e Cirúrgica de|Bovinos', ''),
    'gpl': ('Gestão|na Pecuária|Leiteira', ''),
    'sa': ('Sanidade|Avícola', ''),
    'pc': ('Postura|Comercial', ''),
    'ps': ('Produção|de Suínos', ''),
    'cbea': ('Comportamento|e Bem-Estar Animal', ''),
    'cmmv': ('Cannabis|Medicinal|Veterinária', ''),
    'qsaoa': ('Qualidade e|Segurança de Alimentos|de Origem Animal', ''),
    'suz': ('Saúde Única|e Zoonoses', ''),
    'gpera': ('Gestão de Pessoas|e Extensão Rural|na Agroindústria', ''),
    'ppt': ('Piscicultura e|Produção de Tilápia', ''),
    'mifv': ('Medicina Integrativa e|Fitoterapia Veterinária', ''),
    'gia': ('Gestão da|Indústria de|Alimentos', 'Ênfase em Tecnologia|e Inteligência Artificial'),
    'gcc': ('Gestão de|Cooperativas|de Crédito', ''),
    'crcv': ('Crédito Rural,|Cooperativismo|e Vendas', ''),
    'gpdca': ('Gestão de Pessoas e|Desenvolvimento|de Carreira no|Agronegócio', ''),
    'mvpa': ('Marketing e Vendas|na Produção Animal', ''),
}
ALTURA_OVERLAY, TOPO_OVERLAY = 99, 24  # com sombra: texto sólido de ~88 px a ~31 px do topo
PAD = 40
MODELO = acervo('titulos-pos', 'titulo-pos.html')


def render(params, tmp):
    from PIL import Image
    png = f'{tmp}/bruto.png'
    print_html(url_arquivo(MODELO, **params), 1100, 240, png, escala=4)
    im = Image.open(png).convert('RGBA')
    bb = im.getbbox()
    assert bb, f'{params}: render vazio'
    assert bb[2] < im.width - 8 and bb[3] < im.height - 8, f'{params}: cortado na borda {bb} {im.size}'
    return im.crop((bb[0] - PAD, bb[1] - PAD, bb[2] + PAD, bb[3] + PAD)), bb[3] - bb[1]


def cabe(png, folga=8):
    """o título do topo não pode entrar na janela do vídeo da moldura do vMix mais alta ("uma pessoa")"""
    import numpy as np
    from PIL import Image
    janela = np.asarray(Image.open(acervo('live', 'molduras-vmix', 'moldura-vmix-uma-pessoa.png')).convert('RGBA'))[..., 3] < 20
    titulo = np.asarray(Image.open(png).convert('RGBA'))[..., 3] > 40
    topo, base = np.where(janela.any(axis=1))[0].min(), np.where(titulo.any(axis=1))[0].max()
    assert base + folga <= topo and not (janela & titulo).any(), f'{png}: o título desce até y {base}, a janela começa em y {topo}'
    return png


def gerar(s, tmp):
    from PIL import Image
    linhas, sub = POS[s]
    logo, h = render({'linhas': linhas, 'sub': sub}, tmp)
    logo.save(acervo('titulos-pos', f'titulo-pos-{s}.png'), optimize=True)
    k = ALTURA_OVERLAY / h
    small = logo.resize((round(logo.width * k), round(logo.height * k)), Image.LANCZOS)
    ov = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    ov.alpha_composite(small, ((1920 - small.width) // 2, TOPO_OVERLAY - round(PAD * k)))
    saida = acervo('live', 'titulos-overlay', f'titulo-live-{s}.png')
    ov.save(saida, optimize=True)
    cabe(saida)
    branco, _ = render({'linhas': linhas, 'sub': sub, 'claro': 1}, tmp)
    branco.crop(branco.getbbox()).save(acervo('titulos-pos', f'titulo-pos-{s}-branco.png'), optimize=True)
    print(s, 'ok', logo.size)


def overlay_junto(siglas, saida, vao=40, margem=60):
    """título do topo da live com 2 pós lado a lado, juntas no meio (vão visível de 40 px, aprovado em 24/11),
    na mesma altura dos de uma pós; encolhe se não couber"""
    from PIL import Image
    logos = [Image.open(acervo('titulos-pos', f'titulo-pos-{s}.png')).convert('RGBA') for s in siglas]
    k = min(ALTURA_OVERLAY / (lg.height - 2 * PAD) for lg in logos)
    logos = [lg.crop(lg.getbbox()) for lg in logos]  # sem a margem transparente: o vão é o que se vê
    peq = [lg.resize((round(lg.width * k), round(lg.height * k)), Image.LANCZOS) for lg in logos]
    larg = sum(p.width for p in peq) + vao
    if larg > 1920 - 2 * margem:  # não cabe: as duas diminuem juntas
        f = (1920 - 2 * margem - vao) / (larg - vao)
        peq = [p.resize((round(p.width * f), round(p.height * f)), Image.LANCZOS) for p in peq]
        larg = sum(p.width for p in peq) + vao
    ov = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    x = (1920 - larg) // 2
    for p in peq:
        ov.alpha_composite(p, (x, TOPO_OVERLAY))
        x += p.width + vao
    ov.save(saida, optimize=True)
    return cabe(saida)


def nome(s):
    """nome da pós numa linha (legenda do QR)"""
    return POS[s.lower()][0].replace('|', ' ')


if __name__ == '__main__':
    if sys.argv[1:] == ['--teste']:
        assert nome('PS') == 'Produção de Suínos' and len(POS) == 19
        for s in POS:
            cabe(acervo('live', 'titulos-overlay', f'titulo-live-{s}.png'))
        print('ok')
        sys.exit()
    with tempfile.TemporaryDirectory() as t:
        for sigla in (sys.argv[1:] or POS):
            gerar(sigla.lower(), t)
