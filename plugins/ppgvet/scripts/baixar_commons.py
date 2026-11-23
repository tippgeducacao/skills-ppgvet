#!/usr/bin/env python3
"""Baixa arquivos do Commons e grava .origem.txt. uso: baixar_commons.py pasta "File:..." ..."""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
H = {"User-Agent": "ppgvet-video-edicao/1.0 (ferramenta interna; python-urllib)"}


def abrir(url):
    for tent in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=120)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(15 * (tent + 1))
    raise SystemExit("Commons recusou (429) várias vezes: " + url)
pasta = sys.argv[1]
for t in sys.argv[2:]:
    u = ("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata&format=json&titles="
         + urllib.parse.quote(t))
    p = next(iter(json.load(abrir(u))["query"]["pages"].values()))
    i = p["imageinfo"][0]; m = i["extmetadata"]
    nome = re.sub(r"[^a-z0-9]+", "-", t[5:].rsplit(".", 1)[0].lower()).strip("-")[:60] + "." + t.rsplit(".", 1)[1]
    dest = os.path.join(pasta, nome)
    if not os.path.exists(dest):
        open(dest, "wb").write(abrir(i["url"]).read())
    autor = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "?"))
    open(dest + ".origem.txt", "w", encoding="utf-8").write(
        f"{i['descriptionurl']}\nLicença: {m.get('LicenseShortName', {}).get('value', '?')}\nAutor: {autor.strip()}\n")
    print(nome); time.sleep(3)
