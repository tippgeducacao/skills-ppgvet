#!/usr/bin/env python3
"""Tratar imagem para vídeo (Mac e Windows). Sempre gera arquivo novo; o original não muda.
uso: imagem.py ampliar <entrada> <saida.png> [2|3|4] [--arte]   foto: 4xNomosWebPhoto (ONNX); --arte: Real-ESRGAN anime
     imagem.py fundo   <entrada> <saida.png> [--pessoa]         rembg, tira o fundo (--pessoa: modelo de retrato)
Foto HEIC do iPhone entra direto. Ampliar é último recurso: antes, pedir a foto original em alta.
--arte sem placa de vídeo com Vulkan (Windows): cai para Lanczos até 2x, com aviso."""
import os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import AMPLIAR, EXE, abrir_foto, c, falta_parte  # noqa: E402

PEDACO, BORDA = 192, 16  # a foto é ampliada em pedaços de 192 px (memória baixa), com 16 px de sobra contra emenda


def ampliar_foto(entrada, saida, escala):
    """4x com o NomosWebPhoto, pedaço por pedaço; escala 2 ou 3: reduz o 4x com Lanczos"""
    try:
        import onnxruntime as ort
    except ImportError:
        falta_parte("foto")
    if not AMPLIAR.exists():
        falta_parte("foto")
    import numpy as np
    from PIL import Image
    im = abrir_foto(entrada)
    x = np.asarray(im, np.float32) / 255
    h, w = x.shape[:2]
    s = ort.InferenceSession(str(AMPLIAR), providers=["CPUExecutionProvider"])
    nome = s.get_inputs()[0].name
    y = np.zeros((h * 4, w * 4, 3), np.float32)
    for y0 in range(0, h, PEDACO):
        for x0 in range(0, w, PEDACO):
            a0, b0 = max(0, y0 - BORDA), max(0, x0 - BORDA)
            a1, b1 = min(h, y0 + PEDACO + BORDA), min(w, x0 + PEDACO + BORDA)
            o = s.run(None, {nome: x[a0:a1, b0:b1].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            ya, xa = 4 * (y0 - a0), 4 * (x0 - b0)
            ph, pw = 4 * (min(h, y0 + PEDACO) - y0), 4 * (min(w, x0 + PEDACO) - x0)
            y[4 * y0:4 * y0 + ph, 4 * x0:4 * x0 + pw] = o[ya:ya + ph, xa:xa + pw]
    out = Image.fromarray((np.clip(y, 0, 1) * 255 + .5).astype(np.uint8))
    if escala != 4:
        out = out.resize((w * escala, h * escala), Image.LANCZOS)
    out.save(saida)


def comando(acao, entrada, saida, extra):
    if acao == "ampliar":
        esr = c("realesrgan")
        escala = next((x for x in extra if x in ("2", "3", "4")), "4")
        return [esr, "-i", entrada, "-o", saida, "-n", "realesrgan-x4plus-anime", "-s", escala, "-m", str(Path(esr).parent / "models")]
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
        from PIL import Image
        if entrada.lower().endswith((".heic", ".heif")) or Image.open(entrada).info.get("icc_profile"):
            png = os.path.join(t, "entrada.png")  # rembg e Real-ESRGAN não leem HEIC e ignoram o perfil (P3 do iPhone desbotava)
            abrir_foto(entrada, "RGBA").save(png)
            entrada = png
        if acao == "ampliar" and "--arte" not in extra:
            ampliar_foto(entrada, saida, int(next((x for x in extra if x in ("2", "3", "4")), "4")))
            print(saida)
            return
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
