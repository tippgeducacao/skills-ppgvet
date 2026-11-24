#!/usr/bin/env python3
"""QRs da live (overlay 1920x1080 do vMix, modelo acervo/live/qr-live.html) e links importantes (.txt).
uso: live_qr.py --pos <sigla>[,<sigla 2>] --conteudo <slug-da-live> --pasta <pasta> [--certificado <link Even3>]
     live_qr.py --teste
Cronograma: https://<site da pós>/pos-<sigla>?utm_source=youtube-ppgvet&utm_medium=social&utm_campaign=live
&utm_content=<slug>[-qr-code]#cronograma — o QR leva -qr-code; o link do chat, não. O certificado vai sem UTM.
QR pela API pública do QRCode Monkey (sem chave), conferido por leitura antes de salvar."""
import argparse, json, os, re, sys, tempfile, urllib.request
from urllib.parse import urlencode
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo, print_html, url_arquivo  # noqa: E402
from live_titulos import nome  # noqa: E402

SITE = {'PPGVET': 'site.ppgvet.com.br', 'PPG': 'site.ppgeducacao.com.br'}
MARCA_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'regras', 'marca.md')
ESTILO = {'body': 'circular', 'eye': 'frame13', 'eyeBall': 'ball15', 'bodyColor': '#000000', 'bgColor': '#FFFFFF',
          **{f'{k}{i}Color': '#000000' for k in ('eye', 'eyeBall') for i in (1, 2, 3)}}  # modelo "easy", tudo preto


def marcas():
    """sigla -> marca (PPGVET ou PPG), da tabela de pós do regras/marca.md"""
    return dict(re.findall(r'^\| ([A-Z]+) \| [^|]+ \| (PPGVET|PPG) \|', open(MARCA_MD, encoding='utf-8').read(), re.M))


def link(s, conteudo, qr):
    utm = {'utm_source': 'youtube-ppgvet', 'utm_medium': 'social', 'utm_campaign': 'live',
           'utm_content': conteudo + ('-qr-code' if qr else '')}
    return f'https://{SITE[marcas()[s.upper()]]}/pos-{s}?{urlencode(utm)}#cronograma'


def gerar_qr(dado, png):
    req = urllib.request.Request('https://api.qrcode-monkey.com/qr/custom', method='POST',
                                 headers={'content-type': 'application/json'},
                                 data=json.dumps({'data': dado, 'size': 1000, 'file': 'png', 'config': ESTILO}).encode())
    open(png, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    lido = ler_qr(png)
    assert lido == dado, f'QR não lê o link certo: {lido!r}'


def ler_qr(png):
    """O leitor do OpenCV não lê o estilo circular: amostra o centro de cada módulo,
    redesenha os 3 olhos (cantos arredondados caem no branco) e lê a versão quadrada."""
    import cv2, numpy as np
    olho = np.array([[1] * 7, [1, 0, 0, 0, 0, 0, 1], *[[1, 0, 1, 1, 1, 0, 1]] * 3, [1, 0, 0, 0, 0, 0, 1], [1] * 7], bool)
    b = cv2.imread(png, cv2.IMREAD_GRAYSCALE) < 128
    ys, xs = np.where(b)
    x0, x1, y0 = xs.min(), xs.max() + 1, ys.min()
    for n in range(21, 178, 4):
        m = (x1 - x0) / n
        c = lambda i, ori: int(ori + (i + .5) * m)
        grade = np.array([[b[c(r, y0), c(k, x0)] for k in range(n)] for r in range(n)])
        for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)):
            grade[r0:r0 + 7, c0:c0 + 7] = olho
        img = np.pad(np.where(grade, 0, 255).astype(np.uint8), 4, constant_values=255)
        lido = cv2.QRCodeDetector().detectAndDecode(cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_NEAREST))[0]
        if lido:
            return lido
    return ''


def overlay(dado, texto, saida):
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        qr = f'{tmp}/qr.png'
        gerar_qr(dado, qr)
        im = Image.open(qr).convert('L')  # tira a margem branca da API: o cartão já é a margem
        im.crop(im.point(lambda v: 255 if v < 128 else 0).getbbox()).save(qr)
        shot = f'{tmp}/shot.png'
        print_html(url_arquivo(acervo('live', 'qr-live.html'), qr=url_arquivo(qr), texto=texto), 1920, 1080, shot)
        im = Image.open(shot).convert('RGBA')
    assert im.size == (1920, 1080) and im.getpixel((10, 10))[3] == 0, 'overlay sem transparência'
    im.save(saida, optimize=True)
    print('ok', saida)


def main(o):
    siglas = o.pos.lower().split(',')
    assert re.fullmatch(r'[a-z]+(-[a-z]+)*', o.conteudo), 'conteúdo: minúsculo, palavras com hífen, sem número nem acento'
    assert not o.certificado or o.certificado.startswith('https://'), 'link do certificado deve começar com https://'
    for s in siglas:
        assert s.upper() in marcas(), f'pós "{s}" não está no regras/marca.md'
    os.makedirs(o.pasta, exist_ok=True)
    linhas = [f'Links importantes da live ({o.conteudo})', '']
    for s in siglas:  # com 2 pós, um cronograma de cada (arquivo com a sigla no fim)
        fim = f'-{s}' if len(siglas) > 1 else ''
        overlay(link(s, o.conteudo, True), f'Cronograma {nome(s)}', f'{o.pasta}/qr-live-cronograma-{o.conteudo}{fim}.png')
        linhas += [f'Cronograma {nome(s)} (mandar no chat):', link(s, o.conteudo, False), '']
    if o.certificado:
        overlay(o.certificado, 'Acesse o Certificado!', f'{o.pasta}/qr-live-certificado-{o.conteudo}.png')
        linhas += ['Certificado:', o.certificado, '']
    else:
        linhas += ['Certificado: (falta o link da Even3)', '']
    open(f'{o.pasta}/links-{o.conteudo}.txt', 'w', encoding='utf-8').write('\n'.join(linhas))
    print('ok', f'{o.pasta}/links-{o.conteudo}.txt')


if __name__ == '__main__':
    if sys.argv[1:] == ['--teste']:
        m = marcas()
        assert m['PS'] == 'PPGVET' and m['GCC'] == 'PPG' and len(m) == 19, m
        assert link('gcc', 'tema-x', True) == ('https://site.ppgeducacao.com.br/pos-gcc?utm_source=youtube-ppgvet&utm_medium=social'
                                               '&utm_campaign=live&utm_content=tema-x-qr-code#cronograma')
        print('ok')
        sys.exit()
    a = argparse.ArgumentParser()
    a.add_argument('--pos', required=True); a.add_argument('--conteudo', required=True)
    a.add_argument('--pasta', required=True); a.add_argument('--certificado')
    main(a.parse_args())
