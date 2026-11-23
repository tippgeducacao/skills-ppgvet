#!/usr/bin/env python3
"""Busca vídeos no Wikimedia Commons. uso: commons.py "termo" ["termo2" ...]"""
import json, sys, time, urllib.parse, urllib.request
for q in sys.argv[1:]:
    u = ("https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrlimit=40"
         "&prop=imageinfo&iiprop=url|size|extmetadata&iiextmetadatafilter=LicenseShortName&format=json&gsrsearch="
         + urllib.parse.quote(q + " filemime:video"))
    for tent in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ppgvet-edicao/1.0"})))
            break
        except Exception:
            time.sleep(5 * (tent + 1))
    else:
        print("falhou:", q); continue
    for p in d.get("query", {}).get("pages", {}).values():
        i = p["imageinfo"][0]
        lic = i["extmetadata"].get("LicenseShortName", {}).get("value", "?")
        if i.get("height", 0) >= 720 and (i.get("duration") or 0) < 600:
            print(f"[{q}] {i['height']}p {i.get('duration') or 0:4.0f}s {lic[:14]:14} {p['title']}")
    time.sleep(2)
