#!/usr/bin/env python3
"""Cria o card do professor na hora, a partir do card sem nome do acervo (nenhum card com nome fica guardado).
Uso: card.py "Mara Costa" professora <saida.png>     (ou: professor)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import acervo  # noqa: E402

BASE = acervo("card-professor", "card-sem-nome.png")          # barras verde e azul vazias
NOME = acervo("fontes", "artegra-sans-ex-bold.woff2")        # a mesma do Canva
SUB = acervo("fontes", "lexend-exa-variavel.ttf")            # parecida com a do subtítulo
VERDE, AZUL = (0, 196, 179, 255), (0, 124, 242, 255)
MAX_W = 470  # espaço do nome dentro da barra verde


def card(nome, genero, saida):
    orig = Image.open(BASE).convert("RGBA")
    bb = orig.getchannel("A").getbbox()
    im, (ox, oy) = orig.crop(bb), bb[:2]
    s = 37
    if ImageFont.truetype(NOME, s).getlength(nome) > MAX_W:  # nome grande: só o primeiro e o último (regra do usuário)
        nome = f"{nome.split()[0]} {nome.split()[-1]}"
    while ImageFont.truetype(NOME, s).getlength(nome) > MAX_W:  # ainda grande: diminui a letra
        s -= 1
    fn = ImageFont.truetype(NOME, s)
    fs = ImageFont.truetype(SUB, 20)
    fs.set_variation_by_name("Light")
    d = ImageDraw.Draw(im)
    b = fn.getbbox(nome)
    d.text((162 - ox - b[0], 26 - oy - b[1] + (37 - s) // 2), nome, font=fn, fill="white")
    sub = f"{'Professora' if genero.lower().endswith('a') else 'Professor'} do Grupo PPG Educação"
    b = fs.getbbox(sub)
    d.text((171 - ox - b[0], 86 - oy - b[1]), sub, font=fs, fill="white")
    im.save(saida)


if __name__ == "__main__":
    card(sys.argv[1], sys.argv[2], sys.argv[3])
