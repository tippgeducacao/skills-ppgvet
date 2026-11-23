#!/usr/bin/env python3
"""Blocos de fala (entre silêncios) com as palavras do whisper (tempo DTW) dentro de cada um.
uso: blocos.py audio.wav palavras.json [limiar_db] [silencio_min_s]"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import FF, dur as duracao  # noqa: E402
wav, js = sys.argv[1], sys.argv[2]
db = sys.argv[3] if len(sys.argv) > 3 else "-35"
dmin = sys.argv[4] if len(sys.argv) > 4 else "0.12"
err = subprocess.run([FF(), "-i", wav, "-af", f"silencedetect=n={db}dB:d={dmin}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
dur = duracao(wav)
falas, t = [], 0.0
for a, b in zip(ss, se + [dur]):
    if a > t: falas.append([t, a])
    t = b
if t < dur: falas.append([t, dur])
ws = []
for s in json.load(open(js, encoding="utf-8"))["transcription"]:
    tk = [x for x in s["tokens"] if not x["text"].startswith("[_") and x["t_dtw"] >= 0]
    if tk and s["text"].strip(): ws.append((tk[0]["t_dtw"] / 100 - 0.15, s["text"].strip()))
for i, (a, b) in enumerate(falas):
    txt = " ".join(w for t, w in ws if a - 0.1 <= t < (falas[i + 1][0] - 0.1 if i + 1 < len(falas) else 1e9))
    print(f"{i:3d} {a:7.2f} {b:7.2f} ({b-a:4.2f}) {txt}")
