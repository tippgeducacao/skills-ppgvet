"""Configuração e utilitários comuns dos scripts do pacote ppgvet (Mac e Windows).
A configuração de cada pessoa fica em ~/.ppgvet/video.json, gravada pelo instalar.py."""
import json, os, re, subprocess, sys
from pathlib import Path

HOME = Path.home() / ".ppgvet"
CONFIG = HOME / "video.json"
WIN = sys.platform == "win32"
MAC = sys.platform == "darwin"
EXE = ".exe" if WIN else ""

# subpastas de trabalho de cada tipo de vídeo (dentro da pasta "trabalho" escolhida no instalar)
TIPOS = {"chamadas": "chamadas", "aulas": "aulas-curriculares", "conferir": "conferir-aula",
         "cortes": "cortes-live", "edicoes": "edicoes", "musicas": "musicas", "downloads": "downloads"}
USADAS = "musicas-usadas.txt"  # dentro de musicas/: data, música e vídeo, uma por linha


def config():
    if not CONFIG.exists():
        sys.exit("O kit ainda não foi instalado neste computador: rode a skill instalar")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


_C = None


def c(chave):
    global _C
    _C = _C or config()
    v = _C.get(chave)
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
    print(f"export HYPERFRAMES_FFMPEG_PATH='{FF()}' HYPERFRAMES_FFPROBE_PATH='{FFPROBE()}'")
elif __name__ == "__main__" and sys.argv[1:] == ["--ff"]:
    print(FF())  # para comandos soltos: FF=$("$PY" "$S/comum.py" --ff)
elif __name__ == "__main__":
    assert filtro_caminho("C:\\Users\\a\\x.ass") == "C\\:/Users/a/x.ass"
    assert filtro_caminho("/Users/a/x.ass") == "/Users/a/x.ass"
    WIN = True
    assert nome_arquivo("03/11 | Extensão Rural - Parte II | Prof. Ana") == "03-11 - Extensão Rural - Parte II - Prof. Ana"
    WIN = False
    assert nome_arquivo("03/11 | Extensão") == "03:11 | Extensão"
    print("ok")
