#!/usr/bin/env python3
"""Transcreve com o whisper local (o áudio não sai do computador), com prioridade baixa.
uso: transcrever.py <video ou audio> <saida sem extensão> [--leitura] [-- <opções extras do whisper>]
  sem opções extras: só o .srt (-osrt). --leitura também escreve <saida>.leitura.txt (uma linha por fala com o tempo).
  exemplos de opções: chamada  -- -dtw large.v3.turbo -nfa -ml 16 -sow -osrt -ojf
                      aula     -- -mc 0 -sns -osrt
                      reels    -- --prompt "Éé... ahn, hum, né, é." -dtw large.v3.turbo -nfa -ml 1 -sow -ojf"""
import os, re, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, WHISPER, MODELO, baixo  # noqa: E402


def leitura(srt, destino):
    """versão compacta do .srt: 'HH:MM:SS texto' por linha"""
    out = []
    for b in re.split(r"\n\s*\n", open(srt, encoding="utf-8").read().strip()):
        p = b.strip().splitlines()
        if len(p) > 2:
            out.append(f"{p[1][:8]} {' '.join(p[2:])}")
    open(destino, "w", encoding="utf-8").write("\n".join(out) + "\n")


def main(args):
    extra = args[args.index("--") + 1:] if "--" in args else ["-osrt"]
    args = args[:args.index("--")] if "--" in args else args
    entrada, saida = args[0], args[1]
    wav = os.path.join(tempfile.mkdtemp(), "a.wav")
    subprocess.run([FF(), "-v", "error", "-y", "-i", entrada, "-vn", "-ar", "16000", "-ac", "1", wav], check=True)
    baixo([WHISPER(), "-m", MODELO(), "-l", "pt", *extra, "-of", saida, "-f", wav], check=True, capture_output=True)
    shutil.rmtree(os.path.dirname(wav), ignore_errors=True)
    if "--leitura" in args:
        leitura(saida + ".srt", saida + ".leitura.txt")
        print(saida + ".leitura.txt")
    print(saida + (".srt" if "-osrt" in extra else ".json"))


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        d = tempfile.mkdtemp()
        open(f"{d}/x.srt", "w", encoding="utf-8").write("1\n00:22:10,330 --> 00:22:12,000\nEntão, pessoal\n\n2\n01:00:00,000 --> 01:00:01,000\nfim\n")
        leitura(f"{d}/x.srt", f"{d}/x.txt")
        assert open(f"{d}/x.txt", encoding="utf-8").read() == "00:22:10 Então, pessoal\n01:00:00 fim\n"
        print("ok")
    else:
        main(sys.argv[1:])
