#!/usr/bin/env python3
"""Sobe a aula pronta na Panda Vídeo, na pasta do caminho da tarefa, e devolve o link. Só para quem tem a chave da API.
A chave fica no Keychain do Mac (nunca em .env nem no pacote):  security add-generic-password -U -a ppgvet -s panda-api -w '<chave>'
Uso: panda.py --chave                                                     sai 0 se este computador tem a chave
     panda.py "<caminho da tarefa>" "<arquivo.mp4>" "<título>"            só mostra a pasta de destino
     panda.py "<caminho da tarefa>" "<arquivo.mp4>" "<título>" --enviar   sobe
     panda.py --teste                                                       confere a retomada (sem rede)"""
import base64, json, os, re, subprocess, sys, time, unicodedata, urllib.request, uuid

API = "https://api-v2.pandavideo.com.br"
UPLOAD = "https://uploader-us01.pandavideo.com.br/files"
PEDACO = 64 * 1024 * 1024


def chave():
    """a chave do Keychain, ou None (Windows, ou Mac sem a chave: a pessoa sobe à mão)"""
    try:
        p = subprocess.run(["security", "find-generic-password", "-a", "ppgvet", "-s", "panda-api", "-w"],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return p.stdout.strip() or None


def req(metodo, url, k, corpo=None, cab=None, tentativas=5):
    cab = {"Authorization": k, "Accept": "application/json", **(cab or {})}
    if isinstance(corpo, (dict, list)):
        corpo, cab["Content-Type"] = json.dumps(corpo).encode(), "application/json"
    for t in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=corpo, headers=cab, method=metodo), timeout=300) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 or t == tentativas - 1:
                raise SystemExit(f"Panda respondeu {e.code} em {metodo} {url}: {e.read()[:300]!r}")
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if t == tentativas - 1:
                raise
        time.sleep(5 * (t + 1))


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper())


def pasta(caminho, k):
    """aceita o link da pasta (dashboard.pandavideo.com.br/#/folders/<id>), que é o jeito preferido do usuário,
    ou o caminho escrito da tarefa (aceita um nível a mais no meio: a tarefa omite 'CURSOS DE PÓS-GRADUAÇÃO')"""
    fs = json.loads(req("GET", f"{API}/folders", k)[2])["folders"]
    pid = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", caminho)
    if pid:
        por_id = {f["id"]: f for f in fs}
        assert pid[0] in por_id, f"a pasta {pid[0]} não existe nesta conta da Panda"
        nomes, f = [], por_id[pid[0]]
        while f:
            nomes.insert(0, f["name"])
            f = por_id.get(f["parent_folder_id"])
        return pid[0], " > ".join(nomes)
    filhos = lambda ids: [f for f in fs if f["parent_folder_id"] in ids]
    atual, nomes = [None], []
    for parte in [p.strip() for p in caminho.split(">") if p.strip()]:
        achou = [f for f in filhos(atual) if norm(f["name"]) == norm(parte)]
        if not achou:  # tenta um nível abaixo
            achou = [f for f in filhos([g["id"] for g in filhos(atual)]) if norm(f["name"]) == norm(parte)]
            if achou:
                pai = next(g for g in fs if g["id"] == achou[0]["parent_folder_id"])
                nomes.append(pai["name"])
        assert len(achou) == 1, (f"pasta '{parte}' {'não existe' if not achou else 'aparece mais de uma vez'} em "
                                 f"{' > '.join(nomes) or 'raiz'}; opções: {sorted(f['name'] for f in filhos(atual))[:30]}")
        atual, nomes = [achou[0]["id"]], nomes + [achou[0]["name"]]
    return atual[0], " > ".join(nomes)


def enviar(arq, titulo, pasta_id, k):
    tam, vid = os.path.getsize(arq), str(uuid.uuid4())
    b64 = lambda s: base64.b64encode(s.encode()).decode()
    meta = f"authorization {b64(k)}, folder_id {b64(pasta_id)}, filename {b64(titulo + '.mp4')}, video_id {b64(vid)}"
    _, h, _ = req("POST", UPLOAD, k, b"", {"Tus-Resumable": "1.0.0", "Upload-Length": str(tam), "Upload-Metadata": meta})
    loc = h.get("Location") or h.get("location")
    assert loc, "a Panda não devolveu o endereço do upload"
    off, falhas = 0, 0
    with open(arq, "rb") as f:
        while off < tam:
            f.seek(off)
            dados = f.read(PEDACO)
            try:
                # tentativas=1: repetir o PATCH com o offset velho dá 409 se parte do pedaço já chegou
                _, h, _ = req("PATCH", loc, k, dados, {"Tus-Resumable": "1.0.0", "Upload-Offset": str(off),
                                                     "Content-Type": "application/offset+octet-stream"}, tentativas=1)
                off, falhas = int(h.get("Upload-Offset") or h.get("upload-offset") or off + len(dados)), 0
            except (Exception, SystemExit):  # caiu a conexão ou 409: pergunta à Panda onde parou e continua de lá
                falhas += 1
                if falhas > 5:
                    raise
                time.sleep(10)
                _, h, _ = req("HEAD", loc, k, None, {"Tus-Resumable": "1.0.0"})
                off = int(h.get("Upload-Offset") or h.get("upload-offset"))
            print(f"\r  enviado {off / tam:5.1%} de {tam / 1e9:.2f} GB", end="", flush=True)
    print()
    # o título na Panda é o nome do arquivo (igual aos vídeos que o usuário já sobe). Logo depois do upload,
    # GET /videos/{id} ainda dá 404; a lista da pasta já mostra o vídeo.
    for _ in range(24):
        lista = json.loads(req("GET", f"{API}/videos?folder_id={pasta_id}&limit=100", k)[2])
        v = next((x for x in lista.get("videos", []) if x.get("id") == vid), None)
        if v:
            return vid, v.get("video_player"), v.get("status")
        time.sleep(5)
    return vid, None, "não apareceu na pasta ainda"


def main(caminho, arq, titulo, ok=False):
    assert os.path.exists(arq), f"não encontrei: {arq}"
    k = chave() or sys.exit("Este computador não tem a chave da Panda: subir à mão pela tabela.")
    pid, nomes = pasta(caminho, k)
    print(f"destino: {nomes}\narquivo: {arq} ({os.path.getsize(arq) / 1e9:.2f} GB)\ntítulo:  {titulo}")
    if not ok:
        print("(só conferência; para subir, rodar de novo com --enviar)")
        return
    vid, link, status = enviar(arq, titulo, pid, k)
    print(f"pronto: video_id {vid} | status {status}\nlink: {link}")


def teste():
    """envio falso: o 2º pedaço chega pela metade e a Panda responde 409 na repetição; tem que retomar pelo HEAD"""
    import tempfile
    global PEDACO, req
    real_req, real_sleep, PEDACO = req, time.sleep, 10
    arq = tempfile.mktemp()
    open(arq, "wb").write(bytes(range(35)))
    recebido, falhou = bytearray(), [False]

    def falso(metodo, url, k, corpo=None, cab=None, tentativas=5):
        if metodo == "POST":
            return 201, {"Location": "loc"}, b""
        if metodo == "HEAD":
            return 200, {"Upload-Offset": str(len(recebido))}, b""
        if metodo == "PATCH":
            assert int(cab["Upload-Offset"]) == len(recebido), "PATCH com offset velho"
            if len(recebido) == 10 and not falhou[0]:  # metade do pedaço chega e a conexão cai
                falhou[0] = True
                recebido.extend(corpo[:5])
                raise SystemExit("Panda respondeu 409")
            recebido.extend(corpo)
            return 204, {"Upload-Offset": str(len(recebido))}, b""
        return 200, {}, json.dumps({"videos": []}).encode()  # GET da pasta

    req, time.sleep = falso, lambda s: None
    try:
        enviar(arq, "t", "p", "k")
    finally:
        req, time.sleep = real_req, real_sleep
        os.remove(arq)
    assert falhou[0] and bytes(recebido) == bytes(range(35)), recebido
    print("ok")


if __name__ == "__main__":
    assert norm("10. OUTUBRO") == norm("10.OUTUBRO") and norm("PPG VET") == norm("PPGVET")
    if sys.argv[1:] == ["--teste"]:
        teste()
    elif sys.argv[1:] == ["--chave"]:
        sys.exit(0 if chave() else 1)
    elif len(sys.argv) < 4:
        sys.exit(__doc__)
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], "--enviar" in sys.argv)
