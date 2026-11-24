#!/usr/bin/env python3
"""Tratar imagem para vídeo (Mac e Windows). Sempre gera arquivo novo; o original não muda.
uso: imagem.py ampliar <entrada> <saida.png> [2|3|4] [--arte]   Real-ESRGAN (--arte: ilustração ou desenho)
     imagem.py fundo   <entrada> <saida.png> [--pessoa]         rembg, tira o fundo (--pessoa: modelo de retrato)
Foto HEIC do iPhone entra direto. Ampliar sem placa de vídeo com Vulkan (Windows): cai para Lanczos até 2x, com aviso."""
import os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import EXE, c, falta_parte  # noqa: E402


def comando(acao, entrada, saida, extra):
    if acao == "ampliar":
        esr = c("realesrgan")
        escala = next((x for x in extra if x in ("2", "3", "4")), "4")
        modelo = "realesrgan-x4plus-anime" if "--arte" in extra else "realesrgan-x4plus"
        return [esr, "-i", entrada, "-o", saida, "-n", modelo, "-s", escala, "-m", str(Path(esr).parent / "models")]
    if acao == "fundo":
        rembg = Path(sys.executable).with_name(f"rembg{EXE}")  # roda com o Python do pacote, onde o rembg está
        if not rembg.exists():
            falta_parte("foto")
        # modelo sempre explícito: o padrão do rembg 2.0.8x é o BRIA RMBG-2.0, de licença não comercial
        modelo = ["-m", "birefnet-portrait", "-dc"] if "--pessoa" in extra else ["-m", "birefnet-general"]
        return [str(rembg), "i", *modelo, entrada, saida]
    sys.exit(__doc__)


def lanczos(entrada, saida, extra):
    """plano B sem Vulkan: Lanczos até 2x (acima disso só borra)"""
    from PIL import Image
    escala = min(int(next((x for x in extra if x in ("2", "3", "4")), "4")), 2)
    im = Image.open(entrada)
    im.resize((im.width * escala, im.height * escala), Image.LANCZOS).save(saida)
    print(f"AVISO: este computador não tem placa de vídeo com Vulkan; ampliei {escala}x por Lanczos, sem IA. "
          "Para 4x com IA, ampliar num Mac ou num PC com placa de vídeo.", file=sys.stderr)


def main(acao, entrada, saida, extra):
    assert os.path.exists(entrada), f"não encontrei: {entrada}"
    assert not os.path.exists(saida), f"saída já existe, use outro nome (-v2): {saida}"
    with tempfile.TemporaryDirectory() as t:
        if entrada.lower().endswith((".heic", ".heif")):  # rembg e Real-ESRGAN não leem HEIC
            from PIL import Image, ImageOps
            png = os.path.join(t, "entrada.png")
            ImageOps.exif_transpose(Image.open(entrada)).save(png)
            entrada = png
        p = subprocess.run(comando(acao, entrada, saida, extra), capture_output=True, text=True)
        if p.returncode and acao == "ampliar":
            if "vulkan" in (p.stderr + p.stdout).lower() or not os.path.exists(saida):
                lanczos(entrada, saida, extra)
            else:
                sys.exit(p.stderr[-2000:])
        elif p.returncode:
            sys.exit(p.stderr[-2000:])
    print(saida)


def teste():
    from PIL import Image
    with tempfile.TemporaryDirectory() as t:
        Image.new("RGB", (40, 30), "white").save(f"{t}/a.png")
        lanczos(f"{t}/a.png", f"{t}/b.png", ["4"])
        assert Image.open(f"{t}/b.png").size == (80, 60)  # o plano B nunca passa de 2x
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    elif len(sys.argv) < 4:
        sys.exit(__doc__)
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
