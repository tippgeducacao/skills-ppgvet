#!/usr/bin/env python3
"""Prepara o computador para o pacote ppgvet (Mac e Windows) com o kit completo e grava ~/.ppgvet/video.json.
uso: instalar.py --conferir            só mostra o que está ok e o que falta (não muda nada)
     instalar.py [--trabalho <pasta>]  instala o que falta (padrão da pasta: Filmes/PPGVET no Mac, Vídeos/PPGVET no Windows)
     instalar.py --rosto               instala só o GFPGAN (melhorar rosto, só no Mac, ~1,6 GB), quando alguém pedir
Kit: ffmpeg completo, whisper + modelo, Python do pacote (Pillow, numpy, rembg, yt-dlp), Real-ESRGAN,
limpeza de voz (DeepFilterNet), Node.js, plugins HyperFrames e animate (com Playwright). O GFPGAN fica fora (raro e pesado).
Usa só a biblioteca padrão do Python: roda antes de existir o ambiente do pacote."""
import glob, json, os, re, shutil, subprocess, sys, urllib.request, zipfile
from pathlib import Path

WIN, MAC = sys.platform == "win32", sys.platform == "darwin"
HOME = Path.home() / ".ppgvet"
CONFIG = HOME / "video.json"
PACOTE = Path(__file__).resolve().parents[1]
MODELO_NOME = "ggml-large-v3-turbo-q5_0.bin"
MODELO_URL = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{MODELO_NOME}"
MODELO_MIN = 500_000_000  # o arquivo tem ~574 MB; menor que isso é download pela metade
ACERVO_PASTAS = ["fontes", "logos", "logos-animadas", "molduras-aula", "intro", "card-professor"]
BIN = "Scripts" if WIN else "bin"
EXE = ".exe" if WIN else ""
VENV_PY = HOME / "venv" / BIN / f"python{EXE}"
DF = HOME / "deepfilternet" / BIN / f"deepFilter{EXE}"
GFP_PY = HOME / "gfpgan" / "bin" / "python"
GFP_MODELO = HOME / "gfpgan" / "GFPGANv1.4.pth"
GFP_URL = "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
# última versão do Real-ESRGAN com programa pronto (ncnn) para Mac e Windows
ESRGAN_URL = ("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/"
              f"realesrgan-ncnn-vulkan-20220424-{'windows' if WIN else 'macos'}.zip")
PIP_PACOTE = ["pillow", "numpy", "opencv-python-headless", "yt-dlp", "rembg[cpu,cli]"]
PLUGINS = {"hyperframes": "https://github.com/heygen-com/hyperframes",  # https: não precisa de chave SSH
           "animate": "https://github.com/cth9191/animate"}


def sh(cmd, **kw):
    print("  $", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), **kw)


def ler_config():
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def barra(p):
    return str(p).replace("\\", "/")  # o Bash do Claude Code no Windows (Git Bash) entende /


def brew():
    return shutil.which("brew") or next((b for b in ("/opt/homebrew/bin/brew", "/usr/local/bin/brew") if os.path.exists(b)), None)


def winget(pacote):
    sh(["winget", "install", "--id", pacote, "-e", "--accept-source-agreements", "--accept-package-agreements"], check=True)


def baixar(url, destino):
    destino = Path(destino)
    parte = destino.with_suffix(destino.suffix + ".part")
    print(f"  baixando {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ppgvet-video-instalar"})
    with urllib.request.urlopen(req, timeout=60) as r, open(parte, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    parte.replace(destino)


def versao_py(cmd):
    try:
        v = subprocess.run([*cmd, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"], capture_output=True, text=True).stdout
        return tuple(map(int, v.strip().split("."))) if v.strip() else None
    except OSError:
        return None


def achar_python(minimo, maximo):
    """um Python entre as versões pedidas (inclusive), como lista de comando"""
    if WIN:
        cands = [["py", f"-3.{m}"] for m in range(maximo[1], minimo[1] - 1, -1)]
    else:
        cands = [[f"python3.{m}"] for m in range(maximo[1], minimo[1] - 1, -1)] + [["/usr/bin/python3"]]
        if brew():
            cands += [[str(Path(brew()).with_name(f"python3.{m}"))] for m in range(maximo[1], minimo[1] - 1, -1)]
    return next((c for c in cands if (v := versao_py(c)) and minimo <= v <= maximo), None)


def garantir_python(minimo, maximo, versao):
    """acha ou instala o Python 3.x pedido (Homebrew no Mac, winget no Windows)"""
    py = achar_python(minimo, maximo)
    if not py:
        winget(f"Python.Python.{versao}") if WIN else sh([brew(), "install", f"python@{versao}"], check=True)
        py = achar_python(minimo, maximo)
    if not py:
        sys.exit(f"Python {versao} instalado, mas não encontrado: feche e abra o Claude Code e rode o instalar de novo.")
    return py


# ---------- achar o que já existe ----------

def achar_ffmpeg():
    if MAC and brew():
        p = subprocess.run([brew(), "--prefix", "ffmpeg-full"], capture_output=True, text=True).stdout.strip()
        if p and os.path.exists(f"{p}/bin/ffmpeg"):
            return f"{p}/bin/ffmpeg", f"{p}/bin/ffprobe"
    if WIN:
        la = os.environ.get("LOCALAPPDATA", "")
        for f in [shutil.which("ffmpeg"), f"{la}/Microsoft/WinGet/Links/ffmpeg.exe",
                  *glob.glob(f"{la}/Microsoft/WinGet/Packages/Gyan.FFmpeg*/**/bin/ffmpeg.exe", recursive=True)]:
            if f and os.path.exists(f):
                return f, str(Path(f).with_name("ffprobe.exe"))
    return None, None


def ffmpeg_completo(ff):
    try:
        filtros = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    except OSError:
        return False
    return all(f" {x} " in filtros for x in ("zscale", "ass", "drawtext"))


def achar_whisper():
    if WIN:
        f = glob.glob(str(HOME / "whisper" / "**" / "whisper-cli.exe"), recursive=True)
        return f[0] if f else None
    w = shutil.which("whisper-cli") or (brew() and Path(brew()).with_name("whisper-cli"))
    return str(w) if w and os.path.exists(w) else None


def whisper_windows():
    """baixa o whisper-cli.exe da versão mais nova que publicou o binário de CPU (whisper-bin-x64.zip)"""
    api = "https://api.github.com/repos/ggml-org/whisper.cpp/releases?per_page=10"
    req = urllib.request.Request(api, headers={"User-Agent": "ppgvet-video-instalar"})
    for rel in json.load(urllib.request.urlopen(req, timeout=60)):
        a = next((a for a in rel["assets"] if a["name"] == "whisper-bin-x64.zip"), None)
        if a:
            z = HOME / "whisper.zip"
            baixar(a["browser_download_url"], z)
            zipfile.ZipFile(z).extractall(HOME / "whisper")
            z.unlink()
            return achar_whisper()
    sys.exit("não achei o whisper para Windows nas últimas versões do whisper.cpp")


def achar_modelo(cfg):
    for m in (cfg.get("modelo"), HOME / "modelos" / MODELO_NOME, Path.home() / ".cache" / "whisper" / MODELO_NOME):
        if m and os.path.exists(m) and os.path.getsize(m) > MODELO_MIN:
            return str(m)
    return None


def achar_esrgan():
    f = glob.glob(str(HOME / "realesrgan" / "**" / f"realesrgan-ncnn-vulkan{EXE}"), recursive=True)
    return f[0] if f else None


def venv_ok():
    if not VENV_PY.exists() or (versao_py([str(VENV_PY)]) or (0, 0)) < (3, 11):
        return False
    return subprocess.run([VENV_PY, "-c", "import PIL, numpy, cv2, rembg, yt_dlp"], capture_output=True).returncode == 0


def gfpgan_ok():
    return GFP_PY.exists() and GFP_MODELO.exists() and subprocess.run(
        [GFP_PY, "-c", "import gfpgan, cv2"], capture_output=True).returncode == 0


def acervo_faltando(a=PACOTE / "acervo"):
    return [p for p in ACERVO_PASTAS if not os.path.isdir(os.path.join(a, p))]


def trabalho_padrao(cfg):
    return cfg.get("trabalho") or str(Path.home() / ("Movies" if MAC else "Videos") / "PPGVET")


def node_ok():
    n = shutil.which("node")
    if not n:
        return False
    v = subprocess.run([n, "--version"], capture_output=True, text=True).stdout.strip().lstrip("v")
    return int(v.split(".")[0] or 0) >= 22


def plugin_ok(nome):
    conf = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    f = conf / "plugins" / "installed_plugins.json"
    return f.exists() and f'"{nome}@' in f.read_text(encoding="utf-8")


def npm_global():
    """pasta global do npm, onde o animate procura o Playwright (npm root -g)"""
    npm = shutil.which("npm")
    r = subprocess.run([npm, "root", "-g"], capture_output=True, text=True).stdout.strip() if npm else ""
    if r and not os.path.isdir(r):  # o npm esconde com *** trecho do caminho que parece chave: usa a pasta pessoal
        r = str(Path(os.environ.get("APPDATA", ""), "npm", "node_modules") if WIN else
                Path.home() / ".npm-global" / "lib" / "node_modules")
    return r


def playwright_ok():
    pastas = [Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"] if WIN else \
        [Path.home() / "Library" / "Caches" / "ms-playwright", Path.home() / ".cache" / "ms-playwright"]
    raiz = npm_global()
    return bool(raiz) and os.path.isdir(os.path.join(raiz, "playwright")) and any(glob.glob(str(p / "chromium*")) for p in pastas)


# ---------- conferir ----------

def conferir():
    cfg = ler_config()
    ff = cfg.get("ffmpeg") or achar_ffmpeg()[0]
    falta = acervo_faltando()
    itens = [
        ("configuração (~/.ppgvet/video.json)", CONFIG.exists()),
        ("ffmpeg completo (zscale, legenda, texto)", bool(ff) and ffmpeg_completo(ff)),
        ("ffmpeg no PATH (para o animate)", bool(shutil.which("ffmpeg"))),
        ("whisper (transcrição local)", bool(cfg.get("whisper") and os.path.exists(cfg["whisper"]))),
        ("modelo do whisper em português (~574 MB)", bool(achar_modelo(cfg))),
        ("Python do pacote (Pillow, numpy, OpenCV, rembg, yt-dlp)", venv_ok()),
        ("Real-ESRGAN (ampliar imagem)", bool(achar_esrgan())),
        ("limpeza de voz (DeepFilterNet)", DF.exists()),
        ("Node.js 22+", node_ok()),
        ("Playwright com Chromium (para o animate)", playwright_ok()),
        ("plugin HyperFrames (textos animados nos Reels)", plugin_ok("hyperframes")),
        ("plugin animate (animações de motion design)", plugin_ok("animate")),
        ("peças padrão do pacote (intro, molduras, vinhetas, fontes)", not falta),
        ("pasta de trabalho " + (f"({cfg['trabalho']})" if cfg.get("trabalho") else "(não escolhida)"), bool(cfg.get("trabalho"))),
    ]
    for nome, ok in itens:
        print(("ok    " if ok else "falta ") + nome)
    if MAC:  # fora do kit: não conta como falta
        print(("ok    " if gfpgan_ok() else "fora  ") + "GFPGAN (melhorar rosto; só quando pedirem: instalar.py --rosto)")
    if falta:
        print("      faltam no pacote:", ", ".join(falta), "(reinstalar o pacote: /plugin)")
    return all(ok for _, ok in itens)


# ---------- instalar ----------

def instalar(trabalho):
    HOME.mkdir(exist_ok=True)
    cfg = ler_config()
    if MAC and not brew():
        sys.exit("Falta o Homebrew. Instale pelo site oficial https://brew.sh (o comando pede a senha do Mac) "
                 "e rode o instalar de novo.")

    print("1/8 ffmpeg completo")
    ff, fp = achar_ffmpeg()
    if not (ff and ffmpeg_completo(ff)):
        winget("Gyan.FFmpeg") if WIN else sh([brew(), "install", "ffmpeg-full"], check=True)
        ff, fp = achar_ffmpeg()
    if not (ff and ffmpeg_completo(ff)):
        sys.exit("ffmpeg completo não encontrado depois da instalação (feche e abra o Claude Code e rode de novo)")
    if MAC and not shutil.which("ffmpeg"):  # o ffmpeg-full fica fora do PATH; o animate procura um ffmpeg no PATH
        sh([brew(), "install", "ffmpeg"], check=True)

    print("2/8 whisper")
    wh = achar_whisper()
    if not wh:
        if MAC:
            sh([brew(), "install", "whisper-cpp"], check=True)
            wh = achar_whisper()
        else:
            wh = whisper_windows()
    modelo = achar_modelo(cfg)
    if not modelo:
        (HOME / "modelos").mkdir(exist_ok=True)
        modelo = str(HOME / "modelos" / MODELO_NOME)
        baixar(MODELO_URL, modelo)
        assert os.path.getsize(modelo) > MODELO_MIN, "o modelo do whisper veio incompleto: rode de novo"

    print("3/8 Python do pacote (yt-dlp e rembg pedem Python 3.11+)")
    if not venv_ok():
        if VENV_PY.exists() and (versao_py([str(VENV_PY)]) or (0, 0)) < (3, 11):
            shutil.rmtree(HOME / "venv")  # versão antiga do pacote criou com Python velho
        if not VENV_PY.exists():
            sh([*garantir_python((3, 11), (3, 13), "3.12"), "-m", "venv", HOME / "venv"], check=True)
        sh([VENV_PY, "-m", "pip", "install", "-q", "--upgrade", "pip", *PIP_PACOTE], check=True)
    (HOME / "python").write_text(barra(VENV_PY), encoding="utf-8")

    print("4/8 pastas")
    trabalho = trabalho or trabalho_padrao(cfg)
    os.makedirs(trabalho, exist_ok=True)
    cfg.update({"ffmpeg": barra(ff), "ffprobe": barra(fp), "whisper": barra(wh), "modelo": barra(modelo),
                "trabalho": barra(trabalho)})
    cfg.pop("acervo", None)  # versão antiga apontava para o Drive
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  configuração salva em", CONFIG)

    print("5/8 imagem: Real-ESRGAN")
    if not achar_esrgan():
        z = HOME / "realesrgan.zip"
        baixar(ESRGAN_URL, z)
        zipfile.ZipFile(z).extractall(HOME / "realesrgan")
        z.unlink()
        if not WIN:
            os.chmod(achar_esrgan(), 0o755)  # o zip não guarda a permissão de executar
    cfg["realesrgan"] = barra(achar_esrgan())
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")

    print("6/8 limpeza de voz (DeepFilterNet, ~1 GB)")
    if not DF.exists():  # torch 2.1.2 só existe para Python 3.9 a 3.11
        sh([*garantir_python((3, 9), (3, 11), "3.11"), "-m", "venv", HOME / "deepfilternet"], check=True)
        sh([DF.with_name(f"pip{EXE}"), "install", "-q", "torch==2.1.2", "torchaudio==2.1.2", "numpy<2", "soundfile",
            "deepfilternet"], check=True)

    print("7/8 Node.js e navegadores (HyperFrames e animate)")
    if not node_ok():
        winget("OpenJS.NodeJS.LTS") if WIN else sh([brew(), "install", "node"], check=True)
    npx, npm = shutil.which("npx"), shutil.which("npm")
    if npx:
        env = dict(os.environ, HYPERFRAMES_FFMPEG_PATH=ff, HYPERFRAMES_FFPROBE_PATH=fp)
        sh([npx, "-y", "hyperframes", "browser", "ensure"], check=True, env=env)
    if npm and not playwright_ok():
        if not os.access(npm_global(), os.W_OK):
            # Node do instalador oficial: pasta global do sistema pede senha. Doc do npm ("Resolving EACCES
            # permissions errors"): mudar a pasta global para dentro da pasta pessoal
            sh([npm, "config", "set", "prefix", Path.home() / ".npm-global"], check=True)
        sh([npm, "install", "-g", "playwright"], check=True)
        sh([shutil.which("node"), Path(npm_global()) / "playwright" / "cli.js", "install", "chromium"], check=True)

    print("8/8 plugins HyperFrames e animate")
    for nome, url in PLUGINS.items():
        if plugin_ok(nome):
            continue
        if shutil.which("claude"):
            sh(["claude", "plugin", "marketplace", "add", url], check=True)
            sh(["claude", "plugin", "install", f"{nome}@{nome}"], check=True)
        else:
            print(f"  digite no Claude Code: /plugin marketplace add {url}  e depois  /plugin install {nome}@{nome}")
    print()
    return conferir()


def instalar_rosto():
    if not MAC:
        sys.exit("O GFPGAN só roda no Mac. No Windows, use 'ampliar' para melhorar a imagem.")
    if not gfpgan_ok():
        if not GFP_PY.exists():
            sh([*garantir_python((3, 11), (3, 13), "3.12"), "-m", "venv", HOME / "gfpgan"], check=True)
        pip = [GFP_PY, "-m", "pip", "install", "-q"]
        sh([*pip, "--upgrade", "pip", "setuptools", "wheel", "torch", "torchvision", "opencv-python", "numpy"], check=True)
        sh([*pip, "--no-build-isolation", "basicsr==1.4.2", "facexlib", "gfpgan"], check=True)  # basicsr importa o torch ao instalar
        consertar_basicsr()
        if not GFP_MODELO.exists():
            baixar(GFP_URL, GFP_MODELO)
    cfg = ler_config()
    cfg["gfpgan"] = barra(GFP_PY)
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = gfpgan_ok()
    print(("ok    " if ok else "falta ") + "GFPGAN (melhorar rosto)")
    return ok


def consertar_basicsr():
    """basicsr 1.4.2 importa torchvision.transforms.functional_tensor, que o torchvision novo não tem mais"""
    for f in glob.glob(str(HOME / "gfpgan" / "lib" / "python3*" / "site-packages" / "basicsr" / "data" / "degradations.py")):
        t = Path(f).read_text(encoding="utf-8")
        Path(f).write_text(consertar_import(t), encoding="utf-8")


def consertar_import(t):
    return re.sub(r"torchvision\.transforms\.functional_tensor\b", "torchvision.transforms.functional", t)


def teste():
    assert barra("C:\\Users\\a\\venv") == "C:/Users/a/venv"
    assert acervo_faltando() == [], acervo_faltando()
    assert acervo_faltando(PACOTE / "nao-existe") == ACERVO_PASTAS
    assert consertar_import("from torchvision.transforms.functional_tensor import rgb_to_grayscale") == \
        "from torchvision.transforms.functional import rgb_to_grayscale"
    assert versao_py([sys.executable]) == sys.version_info[:2]
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--teste"]:
        teste()
    elif a == ["--rosto"]:
        sys.exit(0 if instalar_rosto() else 1)
    elif "--conferir" in a:
        sys.exit(0 if conferir() else 1)
    else:
        ok = instalar(a[a.index("--trabalho") + 1] if "--trabalho" in a else None)
        sys.exit(0 if ok else 1)
