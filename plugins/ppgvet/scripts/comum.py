"""Configuração e utilitários comuns dos scripts do pacote ppgvet (Mac e Windows).
A configuração de cada pessoa fica em ~/.ppgvet/video.json, gravada pelo instalar.py."""
import json, os, re, subprocess, sys
from pathlib import Path
try:  # foto HEIC do iPhone abre como qualquer outra (pillow-heif, no essencial do kit)
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

HOME = Path.home() / ".ppgvet"
CONFIG = HOME / "video.json"
WIN = sys.platform == "win32"
MAC = sys.platform == "darwin"
EXE = ".exe" if WIN else ""

# subpastas de trabalho de cada tipo de vídeo (dentro da pasta "trabalho" escolhida no instalar)
TIPOS = {"chamadas": "chamadas", "aulas": "aulas-curriculares", "conferir": "conferir-aula",
         "cortes": "cortes-live", "treinamentos": "treinamentos", "edicoes": "edicoes", "musicas": "musicas",
         "downloads": "downloads", "lives": "lives",
         "patrocinadores": "patrocinadores", "artes": "artes"}
USADAS = "musicas-usadas.txt"  # dentro de musicas/: data, música e vídeo, uma por linha


def config():
    if not CONFIG.exists():
        sys.exit("O kit ainda não foi instalado neste computador: rode a skill instalar")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


_C = None


PARTES = {"voz": "limpeza de voz, ~30 MB", "motion": "HyperFrames e animate, ~0,6 GB",
          "foto": "ampliar e tirar fundo, ~0,7 GB e ~1 GB de modelo na 1ª vez"}
AMPLIAR = HOME / "modelos" / "4xNomosWebPhoto_esrgan.onnx"  # OpenModelDB, CC-BY 4.0 (Phhofm): o mais natural em foto real
HF = "hyperframes@0.9.90"  # versão fixa: sai versão nova quase todo dia; subir de propósito, depois de testar um render
PARTE_DA_CHAVE = {"realesrgan": "foto"}


def falta_parte(parte):
    """parte do kit que só é instalada quando alguém precisa (regra em regras/nucleo.md, "Ambiente")"""
    sys.exit(f"Falta a parte '{parte}' do kit ({PARTES[parte]}): rode instalar.py --{parte} e depois este comando de novo")


def c(chave):
    global _C
    _C = _C or config()
    v = _C.get(chave)
    if not v and chave in PARTE_DA_CHAVE:
        falta_parte(PARTE_DA_CHAVE[chave])
    if not v:
        sys.exit(f"Falta '{chave}' na configuração: rode a skill instalar")
    return v


FF = lambda: c("ffmpeg")
FFPROBE = lambda: c("ffprobe")
WHISPER = lambda: c("whisper")
MODELO = lambda: c("modelo")


ACERVO = Path(__file__).resolve().parents[1] / "acervo"


def acervo(*partes):
    """peça padrão que vem dentro do pacote: intro, molduras, vinhetas, logos, fontes, card sem nome, referências"""
    return str(ACERVO.joinpath(*partes))


def abrir_foto(arq, modo="RGB"):
    """foto em pé (EXIF) e em sRGB: P3 do iPhone e Adobe RGB viram sRGB pelo perfil embutido; sem isso a cor desbota
    quando o perfil se perde no caminho (JPEG embutido no HTML, Photopea, IA de ampliar)"""
    import io
    from PIL import Image, ImageCms, ImageOps
    im = ImageOps.exif_transpose(Image.open(arq))
    icc = im.info.get("icc_profile")
    alfa = im.getchannel("A") if "A" in im.getbands() else None
    im = im.convert("RGB")
    if icc:
        try:
            im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), ImageCms.createProfile("sRGB"),
                                           renderingIntent=ImageCms.Intent.PERCEPTUAL, outputMode="RGB")
        except (ImageCms.PyCMSError, OSError):
            pass  # perfil quebrado: segue com os números como estão
    if modo == "RGBA":
        im.putalpha(alfa or 255)
    return im


REFERENCIAS = Path(__file__).resolve().parent / "referencias"


def igual_referencia(png, nome, limite=16):
    """teste de molde: a peça tem que bater com a aprovada (scripts/referencias/<nome>.png), em blocos de ~1/32 da largura,
    o que pega cor ou posição que mudou (a pílula desbotada dava 78). Sem referência, ou com PPGVET_REFERENCIA=nova
    (mudança de propósito no molde), grava esta como a aprovada"""
    from PIL import Image, ImageChops
    im = Image.open(png).convert("RGB")
    im = im.resize((32, round(im.height * 32 / im.width)), Image.BOX)
    ref = REFERENCIAS / f"{nome}.png"
    if not ref.exists() or os.environ.get("PPGVET_REFERENCIA") == "nova":
        REFERENCIAS.mkdir(exist_ok=True)
        im.save(ref)
        return
    r = Image.open(ref).convert("RGB")
    dif = 255 if r.size != im.size else max(hi for _, hi in ImageChops.difference(im, r).getextrema())
    assert dif <= limite, (f"{nome}: a peça mudou em relação à aprovada (diferença {dif}, limite {limite}). "
                           "Se a mudança foi de propósito: PPGVET_REFERENCIA=nova e rodar o teste de novo")


def pasta(tipo):
    """pasta de trabalho de um tipo (chamadas, aulas, conferir, cortes, edicoes); o instalar pode trocar cada uma"""
    p = (_C or config()).get("pastas", {}).get(tipo) or str(Path(c("trabalho"), TIPOS[tipo]))
    os.makedirs(p, exist_ok=True)
    return p


def caminho(base, f):
    """caminho do roteiro: relativo à pasta do roteiro, com ~, 'acervo:' (peças do pacote) e 'musicas:' (músicas da pessoa)"""
    f = str(f)
    if f.startswith("acervo:"):
        return acervo(*f[7:].lstrip("/").split("/"))
    if f.startswith("musicas:"):
        return str(Path(pasta("musicas"), *f[8:].lstrip("/").split("/")))
    return os.path.normpath(os.path.join(base, os.path.expanduser(f)))


def registrar_musica(musica, video):
    """anota a música usada, para a próxima escolha não repetir"""
    import datetime
    with open(Path(pasta("musicas"), USADAS), "a", encoding="utf-8") as f:
        f.write(f"{datetime.date.today()}\t{os.path.basename(musica)}\t{os.path.basename(video)}\n")


def musicas(n=10):
    """músicas da pasta da pessoa, marcando as usadas nas últimas n vezes"""
    p = Path(pasta("musicas"))
    log = p / USADAS
    usadas = [l.split("\t")[1] for l in log.read_text(encoding="utf-8").splitlines() if "\t" in l] if log.exists() else []
    recentes = set(usadas[-n:])
    for m in sorted(x.name for x in p.iterdir() if x.suffix.lower() in (".mp3", ".wav", ".m4a")):
        origem = p / (m + ".origem.txt")
        print(("USADA  " if m in recentes else "livre  ") + m + ("" if origem.exists() else "   (sem .origem.txt)"))
    print(f"\n(usadas = entre as últimas {n}; pasta: {p})")


def baixo(cmd, **kw):
    """roda com prioridade baixa (o computador continua usável enquanto transcreve ou renderiza)"""
    if WIN:
        kw["creationflags"] = subprocess.BELOW_NORMAL_PRIORITY_CLASS
    else:
        kw["preexec_fn"] = lambda: os.nice(10)
    return subprocess.run(cmd, **kw)


def dur(f):
    return float(subprocess.run([FFPROBE(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True, check=True).stdout)


NAVEGADORES = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
               "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
               r"C:\Program Files\Google\Chrome\Application\chrome.exe",
               r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
               r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
               r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def chrome(*args):
    """Chrome (ou Edge) sem janela; devolve o que ele escreveu (o DOM, no --dump-dom). Às vezes ele sai com erro sem motivo,
    no meio de um lote (visto em 11/2026): até 3 tentativas, para uma folha de 36 peças não cair por uma"""
    import shutil
    nav = next((n for n in NAVEGADORES + [shutil.which(x) for x in ("google-chrome", "chromium", "msedge")]
                if n and os.path.exists(n)), None)
    if not nav:
        sys.exit("Falta o Google Chrome (ou o Edge) para gerar a imagem: instale o Chrome e rode de novo")
    import time
    cmd = [nav, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", *args]
    for vez in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return r.stdout
        time.sleep(1 + vez)
    erro = [l for l in r.stderr.splitlines() if "cv_display_link" not in l and "allocator" not in l][-3:]
    raise RuntimeError(f"o Chrome falhou 3 vezes (código {r.returncode}): " + " | ".join(erro))


def print_html(url, largura, altura, saida, escala=1):
    """print de uma página (modelo HTML do acervo) com fundo transparente"""
    chrome("--hide-scrollbars", "--default-background-color=00000000", f"--force-device-scale-factor={escala}",
           f"--window-size={largura},{altura}", "--virtual-time-budget=3000", f"--screenshot={saida}", url)


def url_arquivo(caminho, **params):
    """file:// de um arquivo local (Mac e Windows), com parâmetros na query"""
    from urllib.parse import urlencode, quote
    return Path(caminho).resolve().as_uri() + ("?" + urlencode(params, quote_via=quote) if params else "")


def filtro_caminho(p):
    """caminho dentro de um filtro do ffmpeg (ass=, fontsdir=): no Windows 'C:' precisa de escape"""
    p = str(p).replace("\\", "/")
    return re.sub(r"^([A-Za-z]):", r"\1\\:", p).replace("'", r"\'")


def nome_arquivo(titulo):
    """título da tarefa vira nome de arquivo. Mac: '/' vira ':' (o Finder mostra '/'). Windows não aceita \\/:*?"<>|"""
    import unicodedata
    t = unicodedata.normalize("NFC", titulo).strip()
    if WIN:
        return re.sub(r'\s*[\\/:*?"<>|]\s*', lambda m: " - " if "|" in m.group() else "-", t).strip(" .")
    return t.replace("/", ":")


def versao_livre(saida):
    """nunca sobrescreve: arquivo.mp4 -> arquivo -v2.mp4, -v3…"""
    n, base = 2, re.sub(r" -v\d+$", "", os.path.splitext(saida)[0])
    while os.path.exists(saida):
        saida, n = f"{base} -v{n}.mp4", n + 1
    return saida


if __name__ == "__main__" and sys.argv[1:] == ["--pastas"]:
    print("acervo (no pacote):", acervo())
    for t in TIPOS:
        print(f"{t}:", pasta(t))
elif __name__ == "__main__" and sys.argv[1:] == ["--musicas"]:
    musicas()
elif __name__ == "__main__" and sys.argv[1:] == ["--hf-env"]:
    # o ffmpeg completo do Mac (ffmpeg-full) não fica no PATH: o HyperFrames acha por estas variáveis
    import shutil
    if not shutil.which("npx"):
        falta_parte("motion")
    print(f"export HYPERFRAMES_FFMPEG_PATH='{FF()}' HYPERFRAMES_FFPROBE_PATH='{FFPROBE()}' HF='{HF}'")
elif __name__ == "__main__" and sys.argv[1:] == ["--ff"]:
    print(FF())  # para comandos soltos: FF=$("$PY" "$S/comum.py" --ff)
elif __name__ == "__main__":
    assert filtro_caminho("C:\\Users\\a\\x.ass") == "C\\:/Users/a/x.ass"
    assert filtro_caminho("/Users/a/x.ass") == "/Users/a/x.ass"
    WIN = True
    assert nome_arquivo("03/11 | Extensão Rural - Parte II | Prof. Ana") == "03-11 - Extensão Rural - Parte II - Prof. Ana"
    WIN = False
    assert nome_arquivo("03/11 | Extensão") == "03:11 | Extensão"
    import tempfile
    from PIL import Image, ImageCms
    with tempfile.TemporaryDirectory() as d:
        # com perfil passa pela conversão (aqui sRGB -> sRGB, sem mudar a cor); perfil quebrado não derruba; alfa fica
        srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        Image.new("RGB", (8, 8), (70, 138, 127)).save(f"{d}/a.png", icc_profile=srgb)
        assert all(abs(x - y) <= 2 for x, y in zip(abrir_foto(f"{d}/a.png").getpixel((2, 2)), (70, 138, 127)))
        Image.new("RGB", (8, 8), (70, 138, 127)).save(f"{d}/q.png", icc_profile=b"quebrado")
        assert abrir_foto(f"{d}/q.png").getpixel((2, 2)) == (70, 138, 127)
        Image.new("RGBA", (8, 8), (1, 2, 3, 40)).save(f"{d}/t.png")
        assert abrir_foto(f"{d}/t.png", "RGBA").getpixel((2, 2))[3] == 40
        Image.new("RGB", (64, 64), (200, 30, 30)).save(f"{d}/p.png")
        REFERENCIAS = Path(d) / "ref"
        igual_referencia(f"{d}/p.png", "t")  # sem referência: grava
        igual_referencia(f"{d}/p.png", "t")
        Image.new("RGB", (64, 64), (200, 120, 30)).save(f"{d}/q.png")
        try:
            igual_referencia(f"{d}/q.png", "t")
            raise SystemExit("cor mudada tinha que reprovar")
        except AssertionError as e:
            assert "mudou" in str(e)
    print("ok")
