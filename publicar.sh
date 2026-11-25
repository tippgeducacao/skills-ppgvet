#!/bin/sh
# Publica o pacote ppgvet: roda os testes, valida e dá push. A equipe recebe na próxima sessão.
# Repositório PÚBLICO: nada de senha, chave ou dado de aluno. uso: ./publicar.sh
set -e
cd "$(dirname "$0")"
S=plugins/ppgvet/scripts
PY="${PY:-$(cat "$HOME/.ppgvet/python" 2>/dev/null || echo python3)}"  # PY=<python> ./publicar.sh para usar outro
for s in comum transcrever cortar chamada aula treinamento conferir post instalar retocar checar hf live_titulos live_qr sons imagem aulas_semana checar_texto reels arte aftermovie molde portao; do
  printf "teste %-12s " "$s"; "$PY" "$S/$s.py" --teste
done
# referência quebrada (skill, agente, regra, script ou peça do acervo citada num .md que não existe) barra a publicação
"$PY" - <<'PYEOF'
import re, sys
from pathlib import Path
R = Path("plugins/ppgvet")
quebradas = []
for md in R.rglob("*.md"):
    if "evals" in md.parts:
        continue
    t = md.read_text(encoding="utf-8")
    for n in re.findall(r"ppgvet:([a-z][a-z-]+)", t):
        if not (R / "skills" / n / "SKILL.md").exists() and not (R / "agents" / f"{n}.md").exists():
            quebradas.append(f"{md}: ppgvet:{n}")
    for n in re.findall(r"(?:\$S/|scripts/)([a-z_]+)\.py", t):
        if not (R / "scripts" / f"{n}.py").exists():
            quebradas.append(f"{md}: {n}.py")
    for n in re.findall(r"(?:`|\$\{CLAUDE_PLUGIN_ROOT\}/)(?:regras/)?((?:oficio/)?[a-z-]+)\.md", t):
        if n not in ("SKILL", "NOTAS", "PRODUCT", "DESIGN", "LEIA-ME", "ORIGEM", "README", "roteiro") and not (R / "regras" / f"{n}.md").exists() \
                and not (R / "regras" / "oficio" / f"{n}.md").exists() and not (R / "skills" / md.parent.name / f"{n}.md").exists():
            quebradas.append(f"{md}: {n}.md")
    for n in re.findall(r"acervo[:/]([\w./-]+\.(?:png|mp4|mov|html|css|wav|webp|ttf|woff2))", t):
        if not (R / "acervo" / n).exists():
            quebradas.append(f"{md}: acervo/{n}")
    for n in re.findall(r"(?:acervo/|\$A/)([a-z][\w-]*)", t):  # pasta do acervo citada
        if not (R / "acervo" / n).exists():
            quebradas.append(f"{md}: acervo/{n}")
if quebradas:
    print("Referência quebrada:\n  " + "\n  ".join(sorted(set(quebradas))))
    sys.exit(1)
print("referências ok")
PYEOF
# sempre.md entra em toda sessão de quem instalou: cada caractere custa contexto sempre
n=$(wc -m < plugins/ppgvet/regras/sempre.md); [ "$n" -le 3000 ] || { echo "sempre.md com $n caracteres (máximo 3000)"; exit 1; }
command -v claude >/dev/null && claude plugin validate . && claude plugin validate plugins/ppgvet
[ -z "$(git status --porcelain)" ] || { echo "Há mudanças sem commit: faça o commit antes de publicar"; exit 1; }
git push
