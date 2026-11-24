---
name: conferir-aula
description: Confere aulas gravadas que outra pessoa já editou ("AULA 04 PARTE 01.mp4"…), sem precisar assistir em 2x. Confere se a intro e a moldura são as da pós, a cartela (título, nome da aula, numeração, erro de digitação), erro de fala do professor que não foi cortado e corte que come fala. Devolve a lista com o minuto de cada coisa para a pessoa checar. Use quando pedirem para corrigir, conferir ou revisar aulas, ou "ver os erros das aulas". Aula curricular do Meet que a gente mesmo edita: skill `aula-curricular`.
---

# Conferir aula (sem assistir)

Só confere e aponta. Não mexe nos vídeos: quem decide e corrige é a pessoa. **Na dúvida, apontar.** Falso positivo não tem problema, porque a pessoa checa tudo. **Não conferir slides:** o conteúdo é do professor.

**O plano desta skill:** quantas aulas, qual edição ou pós e se já há referência. Depois do ok, o lote inteiro sem parar e o relatório completo no fim. **Limpar** depois que a pessoa usar o relatório: as pastas de cada aula em `resultados/` (o relatório `.md` fica).

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills), `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`.
- Pasta: a linha `conferir:` de `"$PY" "$S/comum.py" --pastas` (aqui chamada de `<conferir>`). A pessoa põe as aulas em `<conferir>/entrada/`, e os resultados saem em `<conferir>/resultados/`.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **As aulas já editadas**, em `<conferir>/entrada/`.
- **A edição (pós)** das aulas, ou "genérica".
- Opcional: a ficha da aula (professor, títulos), para conferir a cartela.
- Exemplo de pedido: *"confere as aulas da pasta entrada, edição de Bovinos"*.

## 0. O que saber antes
- **Edição (pós):** perguntar se não estiver claro. "Pós-graduações com a edição genérica" = `GENERICA`. Pós com edição própria = a sigla dela (`marca.md`). Não adivinhar pelo tema.
- **Referência:** imagem com a intro e a moldura de uma aula aprovada da pós (`<SIGLA>.jpg`). Fica em `<conferir>/referencias/` de cada pessoa; sem ela, a conferência segue sem a linha de cima. A primeira aula aprovada de cada pós vira a referência (passo 4).
- **Ficha da aula** (nome, currículo, títulos): não precisa. Se a pessoa mandar, usar para conferir o nome e o card do professor.

## 1. Pré-conferência (em segundo plano)
Primeiro, transcrever e analisar todas, uma atrás da outra: o whisper já usa todos os núcleos, então rodar em paralelo não acelera. Leva ~2 min para cada 13 min de aula. Enquanto a próxima roda, conferir a que já saiu.
```
C=<conferir>
for f in "$C/entrada/"*.mp4; do n=$(basename "$f" .mp4 | tr 'A-Z ' 'a-z-'); "$PY" "$S/conferir.py" "$f" "$C/resultados/$n"; done
"$PY" "$S/conferir.py" --lote "$C/resultados/lote.jpg" <SIGLA> "$C/entrada/"*.mp4
```
- O glob pula os `._*` (lixo do macOS em disco externo).
- Se o `aula.srt` já existe, a aula não é transcrita de novo.
- `"$PY" "$S/conferir.py" --teste` confere o script.
- `lote.jpg` tem uma linha por aula com a intro (0–10 s) e um quadro do meio (moldura), e a referência da pós na primeira linha, se existir.

Cada aula sai em `<conferir>/resultados/<aula-NN-parte-NN>/`:
- `achados.txt`, com:
  - **cortes com voz encostada:** cada corte da edição (salto da imagem) com voz colada nele, o tipo (meio da fala / começo comido / fim comido) e o que o whisper ouve 2,5 s antes e depois;
  - repetição e fala de regravação ("de novo", "corta", "errei", "desculpa"…);
  - silêncio, tela preta, imagem congelada, volume (LUFS) e pico;
  - primeira e última fala, e cada troca de cena com o que estava sendo dito.
- `leitura.txt`: a fala inteira com o tempo.
- `inicio.jpg` (0–30 s), `fim.jpg` (últimos 24 s) e `cenas-N.jpg` (um quadro depois de cada troca de cena).

## 2. Conferir (Claude, vídeo por vídeo)
**Intro e moldura** (`lote.jpg`, `cenas-N.jpg`):
- com referência: iguais a ela (intro, fundo, logos, posição da câmera e do nome)?
- sem referência: todas as aulas do lote iguais entre si? A marca da intro (PPG Educação ou PPGVET) é a da pós no `marca.md`? Diferente, faltando ou de outra marca = erro. Aqui vale a marca da pós; a abertura sempre PPGVET é só da aula curricular. Avisar no relatório que ainda não há referência da pós.

**Cartela, nome da aula e numeração** (`inicio.jpg`; ler em tamanho real, porque na folha a letra fica pequena). Para ver todas de uma vez (a cartela fica parada por volta de 15 s):
`FF=$("$PY" "$S/comum.py" --ff)` e, para cada aula, `"$FF" -v error -y -ss 15 -i "<aula>.mp4" -frames:v 1 -vf "crop=700:560:610:220,scale=467:-2" "$C/resultados/_c-<n>.png"`. Juntar com `hstack`/`vstack` em `cartelas.jpg` (ou ler uma por uma).
- **numeração:** "Aula NN" e "Parte N" batem com o nome do arquivo e com o que o professor diz. No arquivo, AULA = módulo e PARTE = aula da fala: "AULA 03 PARTE 02" = "módulo 3, aula 2";
- **português:** erro de digitação, acento, concordância ou sobra de texto. Exemplo real: "Inclusão no Processo Seletivo **29**";
- **tema:** se o professor anuncia ("abordaremos…", "nesta aula vamos falar de…") ou se o slide de abertura traz o título, o tema da cartela bate com ele (mesmo assunto, não precisa ser palavra por palavra);
- **numeração falada:** "aula 1 do módulo 4", "nos vemos na aula 2", "próxima aula no módulo 4" batem com a sequência real dos arquivos;
- **professor:** nome igual no card, na legenda e em todas as partes (e na ficha, se houver).

**Erro de fala não cortado** (ler `leitura.txt` inteira, não só os achados): frase dita duas vezes, frase abandonada e recomeçada, "de novo"/"deixa eu começar", gaguejo longo, palavra ou número trocado ("módulo 3" numa aula do módulo 4). Como o whisper erra palavras, marcar o que for duvidoso como "ouvir".

**Corte errado** (`cortes com voz encostada` em `achados.txt`):
- ler o "ouvido": palavra pela metade, frase emendada sem sentido ou começo/fim da frase faltando = apontar;
- conferir a primeira fala depois da intro (começa inteira?) e a última antes do encerramento (vai até a despedida?);
- os marcados `[troca de cena]` costumam ser só troca de slide com o professor falando: apontar só se o "ouvido" mostrar problema;
- emenda entre partes: o fim da parte N e o começo da parte N+1 não repetem nem pulam assunto.

**Vídeo e áudio** (`achados.txt`): tela preta fora da intro e do fim; imagem congelada **com fala** (o vídeo travou; congelada sem fala costuma ser o card do professor); silêncio longo no meio; partes da mesma aula com volume muito diferente (mais de 3 LUFS).

## 3. Relatório
Escrever `<conferir>/resultados/relatorio-AAAA-MM-DD.md` e colar no chat **o relatório completo, nunca um resumo**, uma aula por bloco, com o tempo exato para a pessoa pular direto:
```
AULA 04 PARTE 01 (12:47)
- 00:00:15 cartela: "Processo Seletivo 29" (o "29" está sobrando?)
- 00:04:52 corte com voz dos dois lados: "...a inclusão | e a diversidade..." (ouvir)
OK: intro, moldura, numeração, começo e fim
```
Separar o que é erro certo do que é "ouvir"/"conferir". Aula sem nada: "sem erros encontrados". Cada aula leva uma **nota de 0 a 10 da edição** (intro e moldura, cartela, cortes, fala, áudio) na linha do título, para a pessoa saber por onde começar.

## 4. Guardar a referência
Quando a pessoa aprovar uma aula de pós que ainda não tem referência (ou pedir para trocar):
`"$PY" "$S/conferir.py" --salvar-ref <SIGLA> "<aula aprovada>.mp4"`. Ela fica em `<conferir>/referencias/` e vale na hora.

## Aprendizado
Depois que a pessoa checar, o que **não** era erro e o que passou batido vira ajuste no pacote. Anotar com um exemplo real em `<conferir>/aprendizado.md` e avisar quem cuida do pacote. O que já se sabe:
- O card de apresentação do professor (~1:41) fica parado e sem fala de propósito.
- Professor parado na câmera pequena NÃO é imagem travada (o movimento cai, mas não zera). Por isso o detector de imagem congelada só pega quadro idêntico.
- Picos de corte em série logo depois da intro (0:20–0:50) são cortes reais: o editor tirou tropeços da abertura. É ali que mais sobra repetição.
- No "ouvido", a mesma palavra nos dois lados ("em | em vídeo") é normal: a palavra do corte entra nas duas metades. Suspeito é palavra que some, frase que muda de rumo ou dobra que também aparece em `leitura.txt`.
- O whisper inventa "Legenda por…" e "Ahn, né, é." no silêncio; o script já filtra ("Obrigado." só quando cai num silêncio, porque também é despedida real). "Olá pesados/apresados" = "Olá, pessoal".
- Cartela com número sobrando no fim do subtítulo ("Seletivo 29", "Cooperativo 29") apareceu em 2 de 7 aulas do mesmo lote: olhar o fim de toda cartela.
