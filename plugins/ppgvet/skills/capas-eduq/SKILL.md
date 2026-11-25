---
name: capas-eduq
description: Capas do portal do aluno (Eduq) de uma pós - capa principal, Trilha, Abertura, Módulos e Materiais Complementares em 1000x1000 e 1080x1920, no PSD da equipe, com PNG e PSD editável. Use para capas da Eduq, do portal do aluno ou de módulo.
---

# Capas da Eduq

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` e a exceção da Eduq em `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (logo PPG Educação em todas).
- Em cada comando: `PY=$(cat ~/.ppgvet/python); S="${CLAUDE_PLUGIN_ROOT}/scripts"`. Pasta: a linha `artes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<artes>`).

## O que preciso de você
- **A pós**, com o nome como está na tarefa; fora da tabela do `marca.md`, diga se é PPGVET ou PPG (decide a cor do fundo e da pílula).
- **As peças:** quantos módulos, se tem "Trilha Inicial de Aprendizado" e as variantes da capa principal, se houver ("Turma 01/27 #01 e #02"). A subtarefa do sistema lista tudo.
- **A foto do tema**, do assunto real da pós. Sem foto: procurar nos insumos oficiais do Drive; só sem nada bom lá, banco royalty free com licença comercial. IA só com aprovação (`sempre.md`).
- Exemplo: *"capas da Eduq da pós de Medicina Felina, 12 módulos, com trilha, foto anexa"*.

## Passo a passo
1. **Plano curto:** pós e marca, a lista de peças, a foto e o enquadramento. Esperar o ok.
2. **Gerar:** a ficha em `<artes>/eduq/<pos>.json` (campos: `"$PY" "$S/eduq.py"` sem argumento) e `"$PY" "$S/eduq.py" <artes>/eduq/<pos>.json`. O script preenche os PSDs da equipe (`acervo/eduq/modelos`) no Photopea sem janela, cerca de 2 minutos para o jogo inteiro. Sai em `<artes>/eduq/<NOME_DA_POS>/` com os nomes que a equipe usa no Eduq ("CAPA PRINCIPAL - 1080x1920.png", "MODULO 3 - 1000x1000.png"; exceção ao minúsculo-com-hífen), os PSDs editáveis em `editaveis/` e a folha `<NOME_DA_POS>-folha.jpg`.
3. **Plano B:** se sair o aviso "Photopea fora", as capas vieram do código (parecidas, sem PSD). Dizer isso na entrega e oferecer gerar de novo pelo PSD quando o Photopea voltar.
4. **Conferir na folha:** foto do assunto certo e sem outra marca, nome da pós com a grafia conferida e sem "MBA", quebra do nome igual à da equipe (palavra de uma letra não fica no fim da linha), número do módulo certo. Foto mal enquadrada: mudar o `foco` e gerar de novo.
5. **Entregar** a pasta e a folha, com a nota em uma linha. Quem pediu sobe os PNGs na pasta da tarefa no Drive; os PSDs ficam para ajuste fino no Photoshop.

Ajuste vira geração nova da mesma ficha (a ficha é o editável): troca de foto, de nome ou de número de módulos refaz o jogo inteiro.
