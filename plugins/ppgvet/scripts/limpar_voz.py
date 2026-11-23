#!/usr/bin/env python3
"""Tira ruído de fundo do microfone (zumbido, ar-condicionado, sala) com DeepFilterNet 3, preservando a voz.
uso: limpar_voz.py <entrada (vídeo ou áudio)> <saida.wav>
Parte 'voz' do kit, instalada quando alguém precisa (instalar.py --voz)."""
import os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, HOME, WIN, baixo, falta_parte  # noqa: E402

DF = HOME / "deepfilternet" / ("Scripts/deepFilter.exe" if WIN else "bin/deepFilter")


def main(entrada, saida):
    if not DF.exists():
        falta_parte("voz")
    t = tempfile.mkdtemp()
    try:
        voz = os.path.join(t, "voz.wav")
        subprocess.run([FF(), "-v", "error", "-y", "-i", entrada, "-vn", "-ac", "1", "-ar", "48000", voz], check=True)
        p = baixo([str(DF), "-o", t, voz], capture_output=True, text=True)
        if p.returncode or not os.path.exists(os.path.join(t, "voz_DeepFilterNet3.wav")):
            sys.exit("DeepFilterNet falhou:\n" + p.stderr[-2000:])
        shutil.move(os.path.join(t, "voz_DeepFilterNet3.wav"), saida)
        print(saida)
    finally:
        shutil.rmtree(t, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
