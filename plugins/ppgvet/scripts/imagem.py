#!/usr/bin/env python3
"""Tratar imagem para vídeo (Mac e Windows). Sempre gera arquivo novo; o original não muda.
uso: imagem.py ampliar <entrada> <saida.png> [2|3|4] [--arte]   Real-ESRGAN (--arte: ilustração ou desenho)
     imagem.py fundo   <entrada> <saida.png> [--pessoa]         rembg, tira o fundo (--pessoa: modelo de retrato)"""
import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import EXE, c, falta_parte  # noqa: E402


def comando(acao, entrada, saida, extra):
    assert os.path.exists(entrada), f"não encontrei: {entrada}"
    assert not os.path.exists(saida), f"saída já existe, use outro nome (-v2): {saida}"
    if acao == "ampliar":
        esr = c("realesrgan")
        escala = next((x for x in extra if x in ("2", "3", "4")), "4")
        modelo = "realesrgan-x4plus-anime" if "--arte" in extra else "realesrgan-x4plus"
        return [esr, "-i", entrada, "-o", saida, "-n", modelo, "-s", escala, "-m", str(Path(esr).parent / "models")]
    if acao == "fundo":
        rembg = Path(sys.executable).with_name(f"rembg{EXE}")  # roda com o Python do pacote, onde o rembg está
        if not rembg.exists():
            falta_parte("foto")
        return [str(rembg), "i", *(["-m", "birefnet-portrait"] if "--pessoa" in extra else []), entrada, saida]
    sys.exit(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    subprocess.run(comando(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]), check=True)
    print(sys.argv[3])
