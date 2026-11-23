#!/usr/bin/env python3
"""legenda-bruta.srt -> legenda.srt: trocas de texto exatas + palavras-chave em *destaque*, sem ponto final."""
import json, re, sys
pasta, regras = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
bl = [b.splitlines() for b in re.split(r"\n\s*\n", open(f"{pasta}/legenda-bruta.srt", encoding="utf-8").read().strip())]
out = []
for b in bl:
    t = " ".join(b[2:]).strip()
    for a, c in regras.get("trocar", {}).items():
        t = t.replace(a, c)
    t = re.sub(r"[.,;]$", "", t)
    for k in regras.get("chaves", []):  # destaca a palavra/expressão inteira
        t = re.sub(rf"(?<![\w*])({re.escape(k)})(?![\w*])", r"*\1*", t, flags=re.I)
    out.append("\n".join([b[0], b[1], t]))
open(f"{pasta}/legenda.srt", "w", encoding="utf-8").write("\n\n".join(out) + "\n")
print(" | ".join(o.splitlines()[2] for o in out if "*" in o))
