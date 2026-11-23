#!/usr/bin/env python3
"""Folha de quadros (um a cada N s, com o tempo escrito) numa imagem só, para olhar o vídeo sem abrir quadro a quadro.
uso: folha.py <video> <saida.jpg> [a cada N s, padrão 5] [colunas, padrão 6] [largura de cada quadro, padrão 320]"""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, acervo, dur, filtro_caminho  # noqa: E402

video, saida = sys.argv[1], sys.argv[2]
cada, col, larg = (float(sys.argv[3]) if len(sys.argv) > 3 else 5), (int(sys.argv[4]) if len(sys.argv) > 4 else 6), \
    (int(sys.argv[5]) if len(sys.argv) > 5 else 320)
lin = max(1, math.ceil(dur(video) / cada / col))
fonte = filtro_caminho(acervo("fontes", "montserrat-bold.ttf"))
vf = (f"fps=1/{cada},scale={larg}:-2,drawtext=fontfile='{fonte}':text='%{{pts\\:hms}}':x=8:y=8:fontsize=22:"
      f"fontcolor=white:box=1:boxcolor=black@0.6,tile={col}x{lin}")
subprocess.run([FF(), "-v", "error", "-y", "-i", video, "-vf", vf, "-frames:v", "1", saida], check=True)
print(saida)
