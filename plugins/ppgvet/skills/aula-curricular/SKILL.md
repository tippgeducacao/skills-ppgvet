---
name: aula-curricular
description: Edita as aulas curriculares gravadas no Meet ("Aula Curricular _ <sala> - <data> - Recording.mp4"). Corta o começo até o "boa noite" do professor, tira o intervalo e o silêncio do fim, põe a abertura animada, a moldura da pós e o card do professor acima da câmera, salva com o nome da tarefa e diz onde subir cada aula na Panda. Use quando mandarem a tarefa da aula ("Inserir abertura animada… Nomear aula como… Anexar no Panda…") ou pedirem para editar aula curricular.
disable-model-invocation: true
---

# Aula curricular (Meet → Panda)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills), `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças), `${CLAUDE_PLUGIN_ROOT}/regras/video.md` (técnica, motion e Instagram).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`.
- Pasta: a linha `aulas:` de `"$PY" "$S/comum.py" --pastas` (aqui chamada de `<aulas>`). As gravações ficam na raiz dela e as prontas em `<aulas>/prontas/`. O trabalho de cada aula (transcrição, `aula.json`, card e folhas) fica numa subpasta própria, `<aulas>/trabalho/<DD-MM>-<sigla>-<professor>/`, para as aulas do lote não se sobrescreverem; os comandos abaixo rodam de dentro dela.

## O plano desta skill
Uma tabela só, com uma linha por tarefa: aula, gravação achada, sigla e moldura, nome e gênero do card, destino na Panda e alerta quando o mês do destino não bate com a data da aula. As dúvidas vão nele: duas salas possíveis sem como decidir pelo quadro, sigla sem moldura, gênero impossível de deduzir pelo nome. Depois do ok, as seções 1 a 4 rodam para cada aula, uma atrás da outra, e a seção 5 fecha o lote com a tabela da Panda.

**Limpar depois da aprovação:** as subpastas de `<aulas>/trabalho/`. Ficam a gravação original e a aula pronta.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **As gravações do Meet**, baixadas e postas na raiz de `<aulas>`.
- **A tarefa de cada aula**, colada (abertura, nome da aula e caminho da Panda).
- Opcional: **o link da pasta da Panda** de cada aula, para a tabela do fim.
- Exemplo de pedido: *"edita essas 3 aulas"* + as tarefas coladas.

Como a tarefa chega e o que tirar de cada linha:
```
Inserir abertura animada: PPGVET
Nomear aula como: 03/11 | Extensão Rural - Parte II | Prof. Gabriela Tonial Knappmann Bittencourt
Anexar a aula editada na plataforma PANDA VÍDEO no seguinte caminho: PPGVET > SANIDADE AVÍCOLA > 2026 > 10.OUTUBRO
```
- **Abertura:** aula curricular **sempre** leva a abertura PPGVET (`"abertura": "PPGVET"`), mesmo quando a tarefa não traz a linha "Inserir abertura animada" e mesmo em pós da marca PPG.
- **Bruto:** a gravação do Meet com a data da aula no nome (`2026_11_03` = 03/11), o arquivo "… - Recording.mp4". O nome da sala nem sempre é o da disciplina (Extensão Rural estava na sala "Sanidade Avícola e Produção e Gestão Avícola"): achar pela data e pela pós do caminho da Panda. Quando houver duas salas parecidas, tirar um quadro de cada e ler o nome do professor na câmera. Sem como decidir: perguntar no plano.
- **Pós → sigla:** pelo nome da pós no caminho da Panda e a tabela de `marca.md`. A moldura sai da sigla. Sigla sem moldura: perguntar no plano.
- **Card do professor:** é gerado na hora, a cada aula, a partir do card sem nome que vem no pacote (`acervo/card-professor/card-sem-nome.png`). Nenhum card com nome fica guardado.
  - O nome vem da tarefa (a parte depois do último "|", sem o "Prof."). Se o nome inteiro não couber, o script usa só o primeiro e o último ("Gabriela Bittencourt").
  - O gênero é deduzido pelo nome e vai no `aula.json` como `"genero": "professora"` ou `"genero": "professor"` (o card escreve "Professora/Professor do Grupo PPG Educação"). Se o nome não deixar claro, perguntar no plano.
  - O `--pontos` (passo 3) gera o `card-conferir.png` ao lado do `aula.json`, para o Claude conferir o nome e o gênero antes de montar.
- **Panda:** a pessoa sobe à mão (não há chave de API para todos). Guardar, para cada aula, o destino que a tarefa diz ou o **link da pasta** da Panda, se a pessoa mandar (`https://dashboard.pandavideo.com.br/#/folders/<id>`). O caminho escrito na tarefa costuma vir errado: avisar se o mês do caminho não bater com a data da aula (exemplo: aula de 03/11 com "10.OUTUBRO" quando a pasta certa é "11.NOVEMBRO").

## 1. Transcrever (em segundo plano, cerca de 4 min por hora de aula)
`"$PY" "$S/transcrever.py" "<bruto>" aula --leitura -- -mc 0 -sns -osrt`
Com várias aulas, transcrever a próxima enquanto a anterior renderiza.

## 2. Achar os cortes (sem ler a aula inteira)
- **Começo:** ler os primeiros ~30 min de `aula.leitura.txt`. A aula começa no "boa noite" do **professor** iniciando a aula ("Então, boa noite, turma…"), não na conversa de antes (som, câmera, espera, monitor). A abertura animada entra logo antes disso.
- **Intervalo:** `grep -n -i -E "intervalo|minutinhos|café|banheiro|água|pausa|voltamos|voltando|continuar|retomar|avaliação" aula.leitura.txt` e ler em volta.
  - O trecho 1 termina na **última frase de conteúdo antes do aviso**. O aviso inteiro sai, junto com o intervalo: "deixa eu ver que horas são", "vamos fazer um intervalinho, 10 minutinhos, voltamos 8h20?", "até daqui a pouco".
  - O trecho 2 começa quando o professor retoma o conteúdo ("vamos continuar aqui então…", "bom, então a gente…"), sem os ajustes técnicos da volta ("não tá compartilhando ainda, né?").
  - Sem intervalo, é um trecho só.
  - Exemplo: o trecho 1 vai até "…então a gente está indo para o bom caminho." (1:28:55), logo antes de "Vamos só ver que horas são", e o trecho 2 começa em "Bom, então a gente também falou bastante sobre comunicação" (1:42:37).
- **Fim:** ler os últimos ~20 min. A aula vai até a **última fala**: perguntas, agradecimento e "vou encerrando a gravação" ficam. Só o silêncio e o resto vazio saem.
- **Pausa da avaliação:** quando o monitor para a aula para a avaliação e o professor espera em silêncio, cortar igual ao intervalo: vira um trecho a mais. Exemplo: o trecho vai até "…Eduardo? Tranquilo? Então tá." (2:41:57) e o próximo começa em "Então, a partir de agora, a gente vai falar um pouco sobre a IN3" (2:45:08).
- **Meio:** fora isso, não cortar mais nada.

## 3. aula.json e conferir
```json
{"bruto": "Aula Curricular _ ... - Recording.mp4",
 "titulo": "03/11 | Extensão Rural - Parte II | Prof. Gabriela Tonial Knappmann Bittencourt",
 "sigla": "SA", "genero": "professora", "abertura": "PPGVET",
 "panda": "https://dashboard.pandavideo.com.br/#/folders/<id>  (ou o caminho da tarefa)",
 "trechos": [
  {"inicio": "00:24:00,000", "fim": "01:28:55,000", "primeira_frase": "Boa noite, pessoal. Tudo bem?", "ultima_frase": "então a gente está indo para o bom caminho"},
  {"inicio": "01:42:37,000", "fim": "02:56:08,000", "primeira_frase": "Bom, então a gente também falou bastante sobre comunicação", "ultima_frase": "Obrigada, professora, boa noite. Boa noite"}]}
```
- `bruto` é relativo a `<aulas>` (ou um caminho completo).
- `professor` (opcional): o nome para o card, quando o da tarefa não servir. Sem ele, vale o nome da tarefa.
- Copiar as frases da transcrição (5 palavras ou mais). O tempo pode ser aproximado: o script ouve 25 s em volta e acha a palavra exata.
- `"$PY" "$S/aula.py" aula.json --pontos` mostra onde cada corte caiu e o que viria logo depois, e gera o `card-conferir.png`. O Claude confere sozinho: o começo é o "boa noite", nada da volta do intervalo ficou de fora, depois do fim não vem mais fala, e o card (abrir o `card-conferir.png`) tem o nome e o "Professora/Professor" certos. Algo errado: ajustar o `aula.json` e rodar de novo.

## 4. Montar (em segundo plano, cerca de 6 min por hora de aula)
`"$PY" "$S/aula.py" aula.json`. A saída vai para `<aulas>/prontas/<título da tarefa>.mp4`:
- **Mac:** a "/" do título aparece como ":" no terminal e como "/" no Finder.
- **Windows:** não aceita `/ : |` no nome, então eles viram "-". O título exato para a Panda continua o da tarefa.

Se o arquivo já existir, o script cria `<título> -v2.mp4` (depois `-v3`…), nunca sobrescreve.

O que o script faz:
- põe a abertura `acervo/intro/PPGVET.mov` no começo;
- emenda os trechos com fade de 30 ms no áudio;
- põe a moldura da pós por cima do layout do Meet, que já coincide com as áreas dela. **Moldura e card só aparecem enquanto o professor compartilha a tela.** Com a câmera em tela cheia, ou com a tela preta de avatar de quem fala sem câmera, o vídeo fica como o Meet gravou. O script detecta isso sozinho, e o `--pontos` mostra os trechos com tela compartilhada;
- põe o card centralizado sobre a câmera;
- deixa a voz a -16 LUFS;
- grava em 1920x1080 a 30 fps, com teto de 2 Mbps.

## 5. Conferir, dar nota e entregar a tabela
Para cada aula pronta, uma folha de quadros (`"$PY" "$S/folha.py" <aula>.mp4 folha.jpg 300`) e os pontos de emenda. Nota de 0 a 10 em cada critério; abaixo de 8, corrigir e montar de novo:
- começo: abertura e, logo depois, o "boa noite" do professor;
- emendas: nada da conversa do intervalo ou da avaliação ficou, e nenhuma fala de conteúdo foi comida;
- fim: vai até a última fala, sem silêncio sobrando;
- moldura certa da pós e só com tela compartilhada;
- card com o nome e o gênero certos, acima da câmera;
- volume (≈ -16 LUFS) e duração coerente com a gravação.

No fim do lote, uma tabela só, para a pessoa subir à mão:

| aula (arquivo em `<aulas>/prontas/`) | pasta na Panda | título na Panda | duração | nota | observação |
|---|---|---|---|---|---|

- A pasta na Panda é o link que a pessoa mandou ou o caminho da tarefa, com o alerta quando o mês não bate com a data da aula.
- O título na Panda é o título exato da tarefa, com `/` e `|` (no Windows o arquivo troca esses caracteres, a Panda não).
- A Panda fica um tempo "processando" o vídeo depois do upload. Isso é normal.
