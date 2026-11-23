#!/bin/sh
# Publica o pacote ppgvet: roda os testes, valida e dá push. A equipe recebe na próxima sessão.
# Repositório PÚBLICO: nada de senha, chave ou dado de aluno. uso: ./publicar.sh
set -e
cd "$(dirname "$0")"
S=plugins/ppgvet/scripts
PY="$(cat "$HOME/.ppgvet/python" 2>/dev/null || echo python3)"
for s in comum transcrever cortar chamada aula conferir post instalar retocar; do
  printf "teste %-12s " "$s"; "$PY" "$S/$s.py" --teste
done
command -v claude >/dev/null && claude plugin validate . && claude plugin validate plugins/ppgvet
[ -z "$(git status --porcelain)" ] || { echo "Há mudanças sem commit: faça o commit antes de publicar"; exit 1; }
git push
