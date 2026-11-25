#!/usr/bin/env python3
"""Portão de entrega (hook Stop do pacote): peça reprovada pelo arte.py, checar.py ou checar_texto.py não sai sem correção.
Os scripts gravam cada conferência em ~/.ppgvet/conferencias.jsonl (registrar). No fim do turno, se esta sessão conferiu
uma peça nas últimas 6 horas, a última conferência dela reprovou, não há versão mais nova aprovada e ninguém foi avisado,
o portão devolve o turno uma vez com a lista; depois de avisado, deixa terminar (corrigir é o caminho; se a pessoa decidir
entregar assim, a decisão é dela).
uso: hook Stop (lê o JSON do evento na entrada)  |  portao.py --teste"""
import json, os, re, sys, time
from pathlib import Path

REGISTRO = Path.home() / ".ppgvet" / "conferencias.jsonl"
JANELA, GUARDA = 6 * 3600, 2 * 86400  # cobra as últimas 6 h; apaga o que passou de 2 dias


def registrar(arquivo, ok, falhas, registro=None):
    try:
        with open(registro or REGISTRO, "a", encoding="utf-8") as f:
            f.write(json.dumps({"arquivo": str(Path(arquivo).resolve()), "ok": bool(ok), "falhas": falhas, "quando": time.time()}) + "\n")
    except OSError:
        pass  # sem o registro o portão só não lembra; a conferência em si já falou


def base(arquivo):
    """pasta + nome sem número de ordem e sem versão: 03-kv-v2.png e 01-kv.png são a mesma peça"""
    p = Path(arquivo)
    return str(p.parent / re.sub(r"-v\d+$", "", re.sub(r"^\d+-", "", p.stem)))


def ler(registro, agora):
    """linhas dos últimos 2 dias; linha cortada ou corrompida é pulada sozinha"""
    linhas = []
    try:
        texto = registro.read_text(encoding="utf-8")
    except OSError:
        return linhas, 0
    for l in texto.splitlines():
        try:
            d = json.loads(l)
            if agora - d["quando"] < GUARDA:
                linhas.append(d)
        except (ValueError, KeyError, TypeError):
            pass
    return linhas, texto.count("\n")


def pendentes(linhas, agora, sessao=None):
    """última conferência reprovada de cada peça, sem versão mais nova aprovada; com o histórico, só as desta sessão"""
    ultimo, aprovado = {}, {}
    for l in linhas:
        ultimo[l["arquivo"]] = l
        if l["ok"]:
            aprovado[base(l["arquivo"])] = max(aprovado.get(base(l["arquivo"]), 0), l["quando"])
    return [l for l in ultimo.values() if not l["ok"] and not l.get("avisado") and agora - l["quando"] < JANELA
            and aprovado.get(base(l["arquivo"]), 0) < l["quando"] and os.path.exists(l["arquivo"])
            and (sessao is None or Path(l["arquivo"]).name in sessao)]


def historico(evento, ultimos=600_000):
    """o fim do histórico desta sessão; None quando o evento não traz histórico"""
    if "transcript_path" not in evento:
        return None
    try:
        with open(evento["transcript_path"], "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - ultimos))
            return f.read().decode("utf-8", "ignore")
    except (OSError, TypeError):
        return ""  # histórico ilegível: não dá para saber de quem é a peça, não cobra nada


def portao(evento, registro=None):
    """devolve o JSON do hook (ou None para deixar terminar)"""
    registro, agora = registro or REGISTRO, time.time()
    if evento.get("stop_hook_active"):
        return None
    linhas, total = ler(registro, agora)
    falta = pendentes(linhas, agora, historico(evento))
    if not falta:
        if total > len(linhas):  # poda o que passou de 2 dias e o que estava corrompido
            try:
                registro.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")
            except OSError:
                pass
        return None
    for l in falta:
        l["avisado"] = True
    registro.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")
    lista = "; ".join(f'{Path(l["arquivo"]).name} ({l["falhas"]} falha(s))' for l in falta[:6])
    return {"decision": "block", "reason": f"Portão de entrega (ppgvet): a última conferência reprovou {lista}. Corrija e rode a "
            "conferência de novo antes de entregar; se a pessoa decidiu entregar assim mesmo, diga isso na resposta."}


def teste():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        reg, peca = Path(d, "c.jsonl"), Path(d, "p.png")
        peca.write_bytes(b"x")
        assert portao({}, reg) is None  # sem registro, deixa terminar
        registrar(peca, False, 2, reg)
        r = portao({}, reg)
        assert r and r["decision"] == "block" and "p.png" in r["reason"]
        assert portao({}, reg) is None  # avisado uma vez: não prende em loop
        registrar(peca, False, 1, reg)
        assert portao({"stop_hook_active": True}, reg) is None
        registrar(peca, True, 0, reg)  # corrigido: a última conferência manda
        assert portao({}, reg) is None
        registrar(Path(d, "sumiu.png"), False, 1, reg)  # arquivo apagado (teste, rascunho) não conta
        assert portao({}, reg) is None
        velho = json.dumps({"arquivo": str(peca), "ok": True, "falhas": 0, "quando": time.time() - 3 * 86400})
        reg.write_text(velho + "\n{cortad\n" + reg.read_text(encoding="utf-8"), encoding="utf-8")
        assert portao({}, reg) is None and velho not in reg.read_text(encoding="utf-8") and "cortad" not in reg.read_text(encoding="utf-8")
        assert ler(reg, time.time())[0]  # a linha ruim saiu, as boas ficaram
        v1, v2 = Path(d, "03-kv.png"), Path(d, "05-kv-v2.png")  # versão nova aprovada resolve a antiga
        v1.write_bytes(b"x")
        v2.write_bytes(b"x")
        registrar(v1, False, 1, reg)
        time.sleep(.01)
        registrar(v2, True, 0, reg)
        assert portao({}, reg) is None
        outra = Path(d, "outra.png")
        outra.write_bytes(b"x")
        registrar(outra, False, 1, reg)
        hist = Path(d, "sessao.jsonl")
        hist.write_text('{"x": "fala de site"}\n', encoding="utf-8")
        assert portao({"transcript_path": str(hist)}, reg) is None  # peça de outra sessão não prende esta
        assert portao({"transcript_path": str(Path(d, "nao-existe.jsonl"))}, reg) is None  # sem histórico, não cobra
        hist.write_text('{"x": "arte.py outra.html -> outra.png"}\n', encoding="utf-8")
        assert portao({"transcript_path": str(hist)}, reg)  # a sessão que conferiu é cobrada
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--teste"]:
        teste()
    else:
        try:
            r = portao(json.loads(sys.stdin.read() or "{}"))
        except Exception:  # o portão nunca pode quebrar a sessão de ninguém
            r = None
        if r:
            print(json.dumps(r))
