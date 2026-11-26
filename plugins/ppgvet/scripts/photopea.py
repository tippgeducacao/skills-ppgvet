#!/usr/bin/env python3
"""Photopea (photopea.com/api) sem janela: um Chrome invisível abre o Photopea, que recebe arquivos e scripts (no estilo do
Photoshop) e devolve o que for exportado. Serve para preencher os PSDs da equipe sem recriar o visual (scripts/psd.py).
uso:  with Sessao() as pp:
          pp.abrir("modelo.psd")                       # o arquivo vira o documento ativo
          texto = pp.script("app.echoToOE(app.activeDocument.name)")
          png = pp.exportar("png")                      # bytes do documento ativo ("png", "jpg", "psd")
      photopea.py --teste
Sem internet ou com o Photopea fora do ar, levanta Indisponivel: quem chama cai no plano B (o visual em código)."""
import http.server, json, os, queue, shutil, subprocess, sys, tempfile, threading, time
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comum import NAVEGADORES  # noqa: E402

ESPERA_ABRIR, ESPERA_PASSO = 90, 120  # segundos: o Photopea carrega em ~10 s; PSD grande e exportação levam mais
PAGINA = """<!doctype html><meta charset=utf-8><body style="margin:0">
<iframe id=pp style="border:0;width:100vw;height:100vh" src="https://www.photopea.com#%7B%22environment%22%3A%7B%22intro%22%3Afalse%7D%7D"></iframe>
<script>
let fila = Promise.resolve();
const manda = (rota, corpo) => fetch(rota, {method: "POST", body: corpo});
async function proximo() {
  const c = await (await fetch("/proximo")).json();
  const w = document.getElementById("pp").contentWindow;
  if (c.arquivo) w.postMessage(await (await fetch(c.arquivo)).arrayBuffer(), "*"); else w.postMessage(c.js, "*");
}
window.addEventListener("message", e => {
  fila = fila.then(async () => {
    if (e.data instanceof ArrayBuffer) await manda("/arquivo", e.data);
    else if (e.data === "done") { await manda("/pronto", ""); proximo(); }
    else await manda("/texto", String(e.data));
  });
});
</script>"""


# funções que todo script recebe: medida em px (a medida do Photopea é um objeto: .value), achar camada pelo nome (também
# em grupo; o PSD do Mac grava "ç" decomposto, então compara normalizado; camada vem antes de grupo com o mesmo nome)
UTIL = """function px(v){var n=v.value;return (n===undefined||n===null)?v+0:n;}
function caixa(l){var b=l.bounds;return [px(b[0]),px(b[1]),px(b[2]),px(b[3])];}
function acha(c,n,g){n=n.normalize("NFC");for(var k=0;k<c.layers.length;k++){var l=c.layers[k];if(l.name.normalize("NFC")==n&&(g||l.typename!="LayerSet"))return l;if(l.typename=="LayerSet"){var r=acha(l,n,g);if(r)return r;}}return null;}
function camada(n){var l=acha(app.activeDocument,n,false)||acha(app.activeDocument,n,true);if(!l)throw new Error("camada "+n);return l;}
"""


class Indisponivel(RuntimeError):
    """o Photopea não abriu (sem internet, fora do ar): usar o plano B"""


class Travou(RuntimeError):
    """um passo não terminou: no Photopea, erro de script trava a sessão inteira (nem try segura). Quem chama confere
    antes as camadas do modelo para não errar; se travar mesmo assim, a sessão acabou: plano B no que faltar"""


class Sessao:
    def __init__(self, espera_abrir=ESPERA_ABRIR):
        self.espera_abrir, self.cmds, self.eventos = espera_abrir, queue.Queue(), queue.Queue()
        self.pasta = Path(tempfile.mkdtemp(prefix="photopea-"))
        self.arquivos, self.n = {}, 0

    def __enter__(self):
        nav = next((n for n in NAVEGADORES + [shutil.which(x) for x in ("google-chrome", "chromium", "msedge")] if n and os.path.exists(n)), None)
        if not nav:
            raise Indisponivel("falta o Google Chrome (ou o Edge)")
        sessao, self.chrome, self.servidor = self, None, None

        class Pedido(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def responde(self, corpo=b"ok", tipo="text/plain"):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def do_GET(self):
                if self.path == "/":
                    return self.responde(PAGINA.encode(), "text/html; charset=utf-8")
                if self.path == "/proximo":
                    return self.responde(json.dumps(sessao.cmds.get()).encode(), "application/json")
                if self.path.startswith("/f/") and self.path[3:] in sessao.arquivos:
                    return self.responde(Path(sessao.arquivos[self.path[3:]]).read_bytes(), "application/octet-stream")
                self.send_response(404)
                self.end_headers()

            def do_POST(self):
                corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                sessao.eventos.put((self.path.strip("/"), corpo))
                self.responde()

        try:  # sem abrir, o with não chama o __exit__: o Chrome ficaria rodando
            self.servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Pedido)
            self.servidor.daemon_threads = True
            threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
            self.chrome = subprocess.Popen([nav, "--headless=new", "--disable-gpu", f"--user-data-dir={self.pasta / 'perfil'}",
                                            "--window-size=1400,1000", f"http://127.0.0.1:{self.servidor.server_port}/"],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._espera(self.espera_abrir, "o Photopea não abriu")  # o primeiro "done" diz que ele está pronto
        except BaseException:
            self.__exit__()
            raise
        return self

    def __exit__(self, *a):
        if self.chrome:
            self.chrome.kill()
            try:
                self.chrome.wait(10)  # no Windows o perfil fica preso até o Chrome sair de vez
            except subprocess.TimeoutExpired:
                pass
        if self.servidor:
            self.cmds.put({"js": ""})  # solta quem espera o próximo comando
            self.servidor.shutdown()
            self.servidor.server_close()
        shutil.rmtree(self.pasta, ignore_errors=True)

    def _espera(self, segundos, porque, erro=Indisponivel):
        """junta textos e arquivos até o "done" do passo"""
        textos, binarios, fim = [], [], time.time() + segundos
        while True:
            try:
                tipo, corpo = self.eventos.get(timeout=max(.1, fim - time.time()))
            except queue.Empty:
                raise erro(f"{porque} em {segundos} s")
            if tipo == "pronto":
                return textos, binarios
            (textos.append(corpo.decode("utf-8", "replace")) if tipo == "texto" else binarios.append(corpo))

    def _passo(self, cmd, espera=ESPERA_PASSO):
        self.cmds.put(cmd)
        return self._espera(espera, "o Photopea não terminou o passo", Travou)

    def abrir(self, caminho):
        self.n += 1
        nome = f"{self.n}{Path(caminho).suffix.lower()}"
        self.arquivos[nome] = str(caminho)
        self._passo({"arquivo": f"/f/{nome}"})

    def script(self, js):
        """roda o script e devolve o que ele mandou com app.echoToOE (o script termina com uma marca: sem ela, não rodou)"""
        textos, _ = self._passo({"js": UTIL + js + '\n;app.echoToOE("__ok__")'})
        if "__ok__" not in textos:  # Travou: quem chama cai no plano B
            raise Travou("script do Photopea parou no meio (erro de script, camada que não existe ou sessão desencontrada): " + " | ".join(textos)[:300])
        return "\n".join(t for t in textos if t != "__ok__")

    def exportar(self, formato="png"):
        """bytes do documento ativo; "psd" guarda as camadas (o editável)"""
        _, binarios = self._passo({"js": f'app.activeDocument.saveToOE("{formato}")'})
        if not binarios:
            raise Travou(f"o Photopea não devolveu o {formato}")
        return binarios[-1]


def teste():
    from PIL import Image
    import io
    s = Sessao(espera_abrir=.01)  # não dá tempo de abrir: o Chrome tem que morrer junto, sem sobrar processo
    try:
        with s:
            raise AssertionError("não era para abrir em 0,01 s")
    except Indisponivel:
        assert s.chrome is None or s.chrome.poll() is not None, "o Chrome ficou rodando"
        assert not s.pasta.exists()
    try:
        with tempfile.TemporaryDirectory() as d, Sessao(espera_abrir=60) as pp:
            Image.new("RGB", (64, 48), (210, 75, 168)).save(f"{d}/a.png")
            pp.abrir(f"{d}/a.png")
            assert pp.script("app.echoToOE(app.activeDocument.width+'x'+app.activeDocument.height)") == "64x48"
            assert pp.script("app.echoToOE(caixa(app.activeDocument.layers[0]).join(','))") == "0,0,64,48"
            png = Image.open(io.BytesIO(pp.exportar("png")))
            assert png.size == (64, 48) and png.convert("RGB").getpixel((5, 5))[0] > 200
    except Indisponivel as e:
        print(f"aviso: Photopea indisponível ({e}); teste pulado")
        return
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    else:
        sys.exit(__doc__)
