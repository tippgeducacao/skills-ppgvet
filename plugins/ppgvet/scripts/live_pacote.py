#!/usr/bin/env python3
"""Zip da live para jogar na pasta do vMix: os nomes são os que o projeto LIVE.vmix usa (substitui tudo).
uso: live_pacote.py --pasta <pasta da live> --pos <sigla>[,<sigla 2>] --conteudo <slug>
Com 2 pós: QR CRONOGRAMA.png e QR CRONOGRAMA 2.png, e o título do topo com as duas lado a lado."""
import argparse, glob, os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo  # noqa: E402
from live_titulos import overlay_junto  # noqa: E402

a = argparse.ArgumentParser()
a.add_argument('--pasta', required=True); a.add_argument('--pos', required=True); a.add_argument('--conteudo', required=True)
o = a.parse_args()
p, siglas, c = os.path.expanduser(o.pasta), o.pos.lower().split(','), o.conteudo

assert 1 <= len(siglas) <= 2, 'uma ou duas pós por live'
if len(siglas) == 1:
    qrs = {'QR/QR CRONOGRAMA.png': f'{p}/qr-live-cronograma-{c}.png'}
    titulo = acervo('live', 'titulos-overlay', f'titulo-live-{siglas[0]}.png')
else:
    qrs = {f'QR/QR CRONOGRAMA{"" if i == 0 else " 2"}.png': f'{p}/qr-live-cronograma-{c}-{s}.png' for i, s in enumerate(siglas)}
    titulo = overlay_junto(siglas, f'{p}/titulo-live-{c}.png')
ARQUIVOS = {**qrs,  # nome no zip : arquivo gerado
            'OVERLAYS/QR CERTIFICADO.png': f'{p}/qr-live-certificado-{c}.png',
            # moldura: a versão mais nova (-v2, -v3...), já que ajuste nunca sobrescreve
            'OVERLAYS/MOLDURA INSTA.png': max(glob.glob(f'{p}/moldura-insta-{c}*.png'), key=os.path.getmtime,
                                              default=f'{p}/moldura-insta-{c}.png'),
            'OVERLAYS/TITULO.png': titulo,
            'LINKS IMPORTANTES.txt': f'{p}/links-{c}.txt'}
faltam = [k for k, v in ARQUIVOS.items() if not os.path.exists(v)]
assert not faltam, f'faltam: {faltam}'
z = f'{p}/live-{c}.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
    for nome, arq in ARQUIVOS.items():
        f.write(arq, nome)
print('ok', z)
