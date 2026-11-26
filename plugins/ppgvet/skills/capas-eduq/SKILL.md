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
- **As peças:** quantos módulos, se tem "Trilha Inicial de Aprendizado" e as variantes da capa principal, se houver ("Turma 01/27 #01 e #02"; a última aparece no celular dos módulos, como a equipe faz). A subtarefa do sistema lista tudo.
- **A foto do tema**, do assunto real da pós. Sem foto: procurar nos insumos oficiais do Drive; só sem nada bom lá, banco royalty free com licença comercial. IA só com aprovação (`sempre.md`).
- Exemplo: *"capas da Eduq da pós de Medicina Felina, 12 módulos, com trilha, foto anexa"*.

## Passo a passo
1. **Plano curto:** pós e marca, a lista de peças, a foto e o enquadramento. Esperar o ok.
2. **Gerar:** a ficha em `<artes>/eduq/<pos>.json` (campos: `"$PY" "$S/eduq.py"` sem argumento) e `"$PY" "$S/eduq.py" <artes>/eduq/<pos>.json`. O script preenche os modelos da equipe (`<artes>/eduq/modelos`; faltando, "Preparar os modelos" abaixo) no Photopea sem janela, 2 a 3 minutos para o jogo inteiro. Sai em `<artes>/eduq/<NOME_DA_POS>/` com os nomes que a equipe usa no Eduq ("CAPA PRINCIPAL - 1080x1920.png", "MODULO 3 - 1000x1000.png"; exceção ao minúsculo-com-hífen), os PSDs editáveis em `editaveis/` e a folha `<NOME_DA_POS>-folha.jpg`.
3. **Qual motor:** a última linha diz. "motor: plano B em código" = capas parecidas, sem PSD (o Photopea estava fora ou travou): dizer isso na entrega e oferecer gerar de novo pelo PSD quando ele voltar.
4. **Conferir na folha:** foto do assunto certo e sem outra marca, nome da pós com a grafia conferida e sem "MBA", quebra do nome igual à da equipe (palavra de uma letra não fica no fim da linha), número do módulo certo. Se a equipe já publicou capas da mesma pós, comparar lado a lado. Foto mal enquadrada: o `foco` da ficha (ou o de cada capa principal) e gerar de novo; outra foto no fundo dos módulos: `fundos` por tamanho.
5. **Entregar** a pasta e a folha, com a nota em uma linha. Quem pediu sobe os PNGs na pasta da tarefa no Drive; os PSDs ficam para ajuste fino no Photoshop.

Ajuste vira geração nova da mesma ficha (a ficha é o editável): troca de foto, de nome ou de número de módulos refaz o jogo inteiro.

## Preparar os modelos (máquina nova ou PSD novo da equipe)
Os modelos ficam só na pasta de artes de quem gera (`<artes>/eduq/modelos/`), fora do pacote: o PSD é da equipe e muda com ela.
1. **Fonte:** do Drive da tarefa de uma pós já entregue, os PSDs da equipe da capa principal e do módulo, em 1000x1000 e 1080x1920 (arquivo único de GB não serve: pedir os separados). Original nunca é mexido: trabalhar em cópia.
2. **Montar os 12 arquivos** com o `psd.py` (Photopea sem janela; `camadas` lista o que tem dentro):

| arquivo | de onde sai |
|---|---|
| `principal-<tam>.psd` | capa principal com a `FOTO` trocada por cinza (fica leve); o script usa `FOTO` e o objeto `TITULO CURSO` (nome da pós e a pílula) |
| `modulo-<tam>.psd` | módulo com `NOTEBOOK E CELULAR` vazio; usa `FUNDO`, `NOTEBOOK E CELULAR`, o texto `Módulo I`, "aulas curriculares" e a logo |
| `fundo-<tam>.psd` | o que está dentro do objeto `FUNDO` do módulo (foto e camada de cor); no 1000x1000 o degradê vira pixel, senão ele estica |
| `aparelho.png`, `aparelho-reflexo.png` | o notebook e o celular com a tela vazia (1204x860) e o reflexo, do módulo |
| `pilula-ppgvet.png`, `pilula-ppg.png` | a pílula de dentro do `TITULO CURSO`, na cor de cada marca (`marca.md`) |
| `principal-cima-<tam>.png` | o degradê de cima da capa principal com a logo, fundo transparente |

3. **Mudou camada ou posição?** Atualizar os nomes e caixas no topo do `eduq.py` (`PSD`, `DUAS`, `NOME_NA_PILULA`, `PILULA_XY`, telas do aparelho).
4. **Conferir:** gerar uma pós já publicada e comparar lado a lado com a capa da equipe; batendo, `PPGVET_REFERENCIA=nova "$PY" "$S/eduq.py" --teste` grava as referências novas.
