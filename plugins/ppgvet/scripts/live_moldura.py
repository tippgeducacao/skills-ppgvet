#!/usr/bin/env python3
"""Moldura do Instagram da live (1080x1920, janela do vídeo transparente), no modelo acervo/live/moldura-insta.html.
uso: live_moldura.py --foto <foto> --tema "<tema>" --pos <sigla>[,<sigla 2>] --saida <arquivo.png> [--largura 500] [--sem-recorte]
Fixo no modelo: fundo, faixa "ESTAMOS AO VIVO", "LINK NA BIO", janela do vídeo e logo PPGVET (em todas as pós)."""
import argparse, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo, falta_parte, print_html, url_arquivo  # noqa: E402

JANELA = (46, 799, 1032, 1354)  # área do vídeo, medida no modelo do Drive (LIVE › OVERLAYS › MOLDURA INSTA.png)

a = argparse.ArgumentParser()
a.add_argument('--foto', required=True); a.add_argument('--tema', required=True)
a.add_argument('--pos', required=True); a.add_argument('--saida', required=True)
a.add_argument('--largura', type=int, default=500, help='largura da foto recortada, em px (500 = ombros do modelo)')
a.add_argument('--sem-recorte', action='store_true', help='foto já vem sem fundo (PNG transparente)')
o = a.parse_args()
from PIL import Image  # noqa: E402

titulos = [acervo('titulos-pos', f'titulo-pos-{s}-branco.png') for s in o.pos.lower().split(',')]
for t in titulos:
    assert os.path.exists(t), f'sem título: {t} (rode live_titulos.py <sigla>)'
assert len(titulos) <= 2, 'no máximo 2 pós por live'
assert not os.path.exists(o.saida), f'saída já existe, use outro nome (-v2): {o.saida}'
with tempfile.TemporaryDirectory() as tmp:
    foto = Image.open(o.foto).convert('RGBA')
    if not o.sem_recorte:
        try:
            from rembg import new_session, remove
        except ImportError:
            falta_parte('foto')
        foto = remove(foto, session=new_session('birefnet-portrait'))  # MIT; o padrão do rembg (BRIA) não é comercial
    foto = foto.crop(foto.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())
    fp = f'{tmp}/foto.png'
    foto.save(fp)
    shot = f'{tmp}/shot.png'
    print_html(url_arquivo(acervo('live', 'moldura-insta.html'), foto=url_arquivo(fp), tema=o.tema, pos=url_arquivo(titulos[0]),
                           **({'pos2': url_arquivo(titulos[1])} if len(titulos) == 2 else {}),
                           logo=url_arquivo(acervo('logos', 'ppgvet', 'logo-ppgvet.png')), largura=o.largura), 1080, 1920, shot)
    im = Image.open(shot).convert('RGBA')
assert im.size == (1080, 1920), im.size
im.paste((0, 0, 0, 0), JANELA)  # janela do vídeo transparente
os.makedirs(os.path.dirname(os.path.abspath(o.saida)), exist_ok=True)
im.save(o.saida, optimize=True)
print('ok', o.saida)
