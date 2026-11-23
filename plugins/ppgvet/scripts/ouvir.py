#!/usr/bin/env python3
"""Confere um corte sem ouvir: junta trechos do áudio e transcreve. uso: ouvir.py audio.wav "a b" ["a b" ...]"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, WHISPER, MODELO  # noqa: E402
w, rs = sys.argv[1], [tuple(map(float, r.split())) for r in sys.argv[2:]]
fc = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[s{i}];" for i, (a, b) in enumerate(rs))
fc += "".join(f"[s{i}]" for i in range(len(rs))) + f"concat=n={len(rs)}:v=0:a=1,apad=pad_dur=0.5[o]"
tmp = os.path.join(tempfile.mkdtemp(), "ouvir.wav")
subprocess.run([FF(), "-v", "error", "-y", "-i", w, "-filter_complex", fc, "-map", "[o]", "-ar", "16000", "-ac", "1", tmp], check=True)
out = subprocess.run([WHISPER(), "-m", MODELO(), "-l", "pt",
                      "--prompt", "Éé, ahn, né, é.", "-nt", "-np", "-f", tmp], capture_output=True, text=True, encoding="utf-8").stdout
import shutil
shutil.rmtree(os.path.dirname(tmp), ignore_errors=True)
print(" ".join(out.split()))
