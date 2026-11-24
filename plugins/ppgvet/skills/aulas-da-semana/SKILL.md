---
name: aulas-da-semana
description: Arte de Instagram (imagem, não vídeo) - o carrossel "Aulas da semana" da PPGVET/PPG, capa e uma lâmina por aula (pós, dia, horário, professor com foto, tema), no molde da equipe, com cores e nomes oficiais e conferência medida. Use quando pedirem o carrossel das aulas da semana ou mandarem a lista das aulas curriculares da semana para o Instagram.
---

# Aulas da semana (carrossel do Instagram)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (pós, sigla, nome e cor oficiais), `${CLAUDE_PLUGIN_ROOT}/regras/oficio/design.md` e `${CLAUDE_PLUGIN_ROOT}/regras/antislop-midia.md`.
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`. Pasta: a linha `artes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<artes>`).

## O que preciso de você
Se a pessoa chamou sem a lista (ou é a primeira vez), explicar em poucas linhas:
- **A lista da semana**, colada, uma aula por linha: pós, data, horário, professor e o tema. Titulação: regra do `oficio/copy.md` (sem comprovação, só o nome).
- **As fotos dos professores**: a pasta onde estão (nome-sobrenome.jpg) ou os arquivos. Sem foto, a lâmina não sai: nunca foto de banco nem gerada.
- Exemplo: *"faz o carrossel da semana"* + `CBEA | 23/11 | 19h | Dra. Ana Souza | Bem-estar na criação`.

## O molde (o da equipe, com as regras da marca)
| lâmina | o que tem |
|---|---|
| capa | logo, "AULAS DA" fino, "SEMANA" grande na cor da marca, tarja escura com as datas ("23 a 25 de novembro", sem crase), "ARRASTA PARA O LADO" |
| uma por aula | logo, "PÓS-GRADUAÇÃO" na cor da marca, tarja com o nome oficial da pós na cor oficial dela, foto do professor em cartão, caixa escura com o dia (sai da data) e o horário, titulação (só se comprovada) e nome, "AULA:" e o tema, "ARRASTA PARA O LADO" |

- 1080x1350 (4:5): vale pelo app e pelo agendador do sistema.
- Uma pasta por marca: aula de pós da PPG sai num carrossel da PPG, com a logo e o azul da PPG (`marca.md`).
- Módulo comum a várias pós: `"pos": ["RNGB", "GPL"]`; a tarja junta os nomes na cor da marca.
- Só Montserrat, só as cores do `marca.md`, ícones Lucide. Letra sobre a tarja: regra do `marca.md` (o script mede; se nenhuma cor de letra der 4,5:1, a tarja do carrossel todo vai em letra grande).

## Passo a passo
1. **Montar a lista** em `<artes>/trabalho/semana-<dd-mm>.json` (formato no começo de `"$S/aulas_semana.py"`): sigla certa pela tabela do `marca.md` (nome de pós que não bate com nenhuma: perguntar no plano), data `dd/mm`, horário como veio, professor como veio.
2. **Plano**, uma tabela: aula, pós (sigla e nome oficial), dia da semana calculado, horário, professor, foto achada e os avisos. Rodar antes `"$PY" "$S/aulas_semana.py" <json> --fotos <pasta>`: ele para com erro quando falta algo (sigla, data, foto) e avisa titulação que saiu (Esp., PhD, M.V.), grafia que não bate com o nome da foto ("Polleto" × "poletto"), tema longo e aula no fim de semana. Dia da semana que a pessoa escreveu diferente da data: avisar (vale o da data). Esperar o ok.
3. **Gerar**: o mesmo comando. Sai em `<artes>/aulas-semana-<marca>-<dd-mm>/` (nunca sobrescreve: `-v2`), com as lâminas numeradas e a `folha.jpg`.
4. **Conferir**: o script mede cada lâmina no navegador e marca `FALHA` (texto que não cabe, encosta na borda ou cobre outro). FALHA barra a entrega: encurtar o tema com a pessoa ou corrigir e gerar de novo. Abrir a `folha.jpg` e dar nota de 0 a 10 em: dados (nome, pós, dia, horário e tema iguais à lista conferida), leitura no celular, marca e acabamento (`antislop-midia.md`). Abaixo de 8: corrigir.
5. **Entregar**: a pasta, a folha e a nota em uma linha. Ajuste vira versão nova. Limpar depois da aprovação: nada (o `.json` fica para refazer).
