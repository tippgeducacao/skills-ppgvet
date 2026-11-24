---
name: cortes-live
description: Tira cortes de uma live ou aula gravada da PPGVET (Meet/Zoom com moldura) e transforma cada um num post vertical 9:16 para o Instagram, com cartão de perfil "PPGVET - Educação", título roxo, câmera do professor em foco (slide e quem pergunta como apoio, em trechos), legenda, imagem de apoio opcional, encerramento animado e música calma. Também gera a aula completa de uma live, com a abertura PPGVET e sem as partes da live. Aceita o arquivo ou o link da live. Use quando pedirem cortes de live ou de aula, cortes da aula de abertura, aula completa de uma live, ou posts de trechos de aula. Aula curricular do Meet ("Nomear aula como…"): skill `aula-curricular`.
disable-model-invocation: true
---

# Cortes de live → posts

**O plano desta skill:** link ou arquivo da live, tema, se faz a aula completa e o nome da pós dos posts. Depois do ok, tudo sem parar: baixar, transcrever, escolher os cortes, cortar, aula completa e todos os posts. A pessoa revisa os cortes, os títulos e os posts juntos no fim (seção 3).

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills), `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças), `${CLAUDE_PLUGIN_ROOT}/regras/video.md` (técnica, motion e Instagram), `${CLAUDE_PLUGIN_ROOT}/regras/bancos-e-referencias.md` (referência, inserções, música e sons).
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"` e `FF=$("$PY" "$S/comum.py" --ff)`.
- Pasta: a linha `cortes:` de `"$PY" "$S/comum.py" --pastas` (aqui chamada de `<cortes>`). Todos os comandos rodam de dentro de `<cortes>/`.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **A live:** o link (YouTube, Facebook…) ou o arquivo.
- **A pós** que aparece nos posts e o tema da live.
- **Se quer também a aula completa** (a live sem as partes de live, com a abertura).
- Opcional: quantos cortes (o padrão é 7 ou 8) e algum trecho que não pode faltar.
- Exemplo de pedido: *"tira os cortes dessa live de micotoxinas, pós de Sanidade Avícola, e faz a aula completa"* + link.

## Pastas
```
cortes-live/<tema>/
  live-<assunto>.mp4                  gravação inteira (1280x720), nunca mexer
  transcricao-<assunto>.srt   transcricao-<assunto>.leitura.txt
  aula-completa.json   aula-completa-<assunto>.mp4   só a aula, sem a live (passo 1b)
  cortes.json   cortes/corte-<tema>-<titulo>.mp4
  apoio/        imagem ou vídeo + .origem.txt (link e licença)
  posts/post-<titulo>.json   posts/post-<tema>-<titulo>.mp4   posts/.tmp-post/ (cache)
```
`<tema>` é uma palavra curta (micotoxinas, cannabis, comportamento). Na primeira vez, criar a pasta do tema.
- **A pessoa mandou o link da live** (YouTube, Facebook etc.): baixar direto para a pasta, como na skill `baixar-video`:
  `"$PY" -m yt_dlp --quiet --no-warnings --print after_move:filepath --ffmpeg-location "$FF" -S "res:1080,ext:mp4" --merge-output-format mp4 -o "<tema>/live-<assunto>.%(ext)s" "<link>"`. Se o site pedir login, usar a sessão do navegador (`--cookies-from-browser chrome`, regra da `baixar-video`).
- **Mandou o arquivo:** copiar ou mover para a pasta como `live-<assunto>.mp4`.

## 0. Transcrever a live (local, o áudio não sai do computador)
Leva uns 4 min para cada hora de gravação. Rodar em segundo plano:
`"$PY" "$S/transcrever.py" <tema>/live-x.mp4 <tema>/transcricao-x --leitura`

## 1. Escolher os cortes
Ler o `transcricao-x.leitura.txt` inteiro (uma linha por fala, com o tempo), em partes, com Read (offset/limit), sem pular trechos, e propor de 7 a 8 cortes:

- cada corte tem de 50 a 95 s e uma ideia completa, que se entende sem o resto da aula;
- a primeira frase prende (dado forte, mito, caso real, erro comum);
- o título dá curiosidade sem prometer o que a fala não entrega.

Escrever o `cortes.json` e seguir direto (a pessoa revisa os cortes, os títulos e os posts juntos no fim):
```json
[{"titulo": "Absorvente de micotoxina é o seguro do carro",
  "inicio": "02:20:08,240", "fim": "02:21:03,860",
  "primeira_frase": "Então gente pra gente concluir…", "ultima_frase": "…"}]
```
Depois: `"$PY" "$S/cortar.py" "<tema>/cortes.json" <tema>`. O script ouve a fala em volta da minutagem, acha a `primeira_frase` e a `ultima_frase` e corta com 3 s de folga em cada lado. Se não achar, avisa e corta pela minutagem com 10 s de folga. Corte que já existe é pulado.

## 1b. Aula completa (versão curricular, sem a live)
As aulas de abertura são lives com este roteiro: vinheta → fala do diretor → coordenador (recados, cidades no chat, vagas) → chamada do professor e ajuste técnico → **aula** → perguntas do chat → encerramento (certificado, avisos) → vinheta. A versão curricular fica só com a **aula**.
- **Começo:** a primeira frase de conteúdo do professor. Fica de fora tudo o que vem antes, inclusive o "boa noite, obrigado pelo convite" e os ajustes ("fecha a janela do Meet").
- **Fim:** a última frase da exposição, quando o professor encerra o conteúdo ("era o que eu tinha, muito obrigado"), **antes das perguntas**. Perguntas, chat, enquete e encerramento ficam de fora.
- **Meio:** não cortar nada.
- **Abertura:** a aula completa leva a abertura PPGVET no começo, como a aula curricular (`"abertura": "PPGVET"`).
- Conferir as duas pontas com quadros: logo depois da abertura, o slide deve estar na tela; no fim, o apresentador não pode aparecer falando.
```json
[{"titulo": "aula completa", "inicio": "00:22:10,330", "fim": "02:22:25,670",
  "primeira_frase": "Então, pessoal, primeira coisa eu queria convidar vocês",
  "ultima_frase": "era o que eu tinha. Muito obrigado",
  "saida": "aula-completa-<assunto>.mp4", "folga": 0.5, "abertura": "PPGVET"}]
```
`"$PY" "$S/cortar.py" "<tema>/aula-completa.json" <tema>`. Rodar em segundo plano, porque são horas de vídeo (cerca de 4 min de render por hora). Conferir as duas pontas com uma folha de quadros e seguir.

## 2. Montar os posts (todos, um atrás do outro)
1. `post.json` em `posts/`:
   ```json
   {"corte": "../cortes/corte-micotoxinas-....mp4",
    "inicio": 2.9, "fim": 83.9,
    "titulo": ["A micotoxina que", "trava a reprodução", "por até um ano"],
    "pos": ["Pós-Graduação em Reprodução,", "Nutrição e Gestão de Bovinos"],
    "cameras": [{"de": 0, "recorte": [952, 192, 264, 264]},
                {"de": 21.5, "recorte": [60, 115, 872, 490]},
                {"de": 27.0, "recorte": [952, 192, 264, 264]}],
    "correcoes": {"ócito": "oócito"},
    "apoio": [{"arquivo": "../apoio/apoio-espiga-milho....jpg", "de": 10.8, "ate": 14.2}],
    "musica": "musicas:corporativa-inspiradora.mp3",
    "saida": "post-micotoxinas-....mp4"}
   ```
   - `titulo`: até 3 linhas de no máximo ~18 letras.
   - `pos`: o nome do curso em 2 linhas (nomes em `marca.md`). **Perguntar ou copiar de um post anterior do mesmo curso**, nunca inventar.
   - `marca` (opcional): `ppgvet` (padrão) ou `ppg` (pós da marca PPG, `marca.md`). Escolhe a moldura fixa do post (`acervo/molduras/moldura-post-corte-<marca>.png`: avatar, nome e @), a cor do título e a vinheta do fim.
   - `encerramento` (opcional): troca a vinheta da marca por outro vídeo ou por uma arte de CTA em imagem.
   - `cameras`: o que aparece na caixa grande do post, em trechos (`de` = segundos do post, cada trecho vai até o `de` do próximo; o primeiro começa em 0). `recorte` = área no vídeo (x, y, largura, altura).
     - **O professor é o foco:** a maior parte do post é a câmera dele, falando algo interessante. No layout padrão da moldura: `[952,192,264,264]`.
     - **Slide** (no layout padrão, `[60,115,872,490]`): só como apoio, em trecho curto (de 3 a 8 s), quando o professor aponta ou explica algo que está nele ("olha esse gráfico", "nesse dado aqui"). Depois volta para o professor.
     - **Quem pergunta** (nas perguntas do fim da live): a área onde a pessoa aparece, só enquanto ela pergunta; volta para o professor assim que ele começa a responder.
     - Para achar as áreas: tirar quadros do corte (`"$PY" "$S/folha.py" <tema>/cortes/corte-x.mp4 folha.jpg 5`), medir cada caixa e deixar o rosto inteiro. O slide entra inteiro, com o fundo borrado dele mesmo completando a caixa.
     - Só o professor o tempo todo: um trecho só (`[{"de": 0, "recorte": [952,192,264,264]}]`). Post antigo com `"recorte": [x, y, w, h]` continua funcionando.
2. `"$PY" "$S/post.py" <tema>/posts/post-x.json --legenda` transcreve o corte e mostra o caminho do `.srt` (ler com Read). Com ele:
   - achar o `inicio` (logo antes da primeira frase) e o `fim` (logo depois da última palavra);
   - anotar os erros do whisper em `correcoes`. A legenda sai em minúsculas e sem pontuação, e as correções valem depois disso;
   - na dúvida sobre um nome, pesquisar a grafia certa antes (`nucleo.md`).
3. `apoio` (opcional): uma imagem ou vídeo do assunto real, que cobre a tela de `de` até `ate` (segundos do post), com zoom de entrada e saída. Onde buscar: regra de inserções de `bancos-e-referencias.md`.
4. Música: uma faixa calma, escolhida pela regra de música de `bancos-e-referencias.md`. Diferente entre os posts da mesma live, fora das 10 últimas usadas, nunca em loop.
5. `"$PY" "$S/post.py" <tema>/posts/post-x.json`. Se a saída já existir, o script para: usar outro nome `-vN`.
6. **Conferir e dar nota** (`"$PY" "$S/folha.py" <tema>/posts/post-x.mp4 folha.jpg 2`), de 0 a 10 em cada critério; abaixo de 8, corrigir e montar de novo:
   - o corte prende na primeira frase e fecha a ideia (entende-se sem o resto da live);
   - professor em foco na maior parte; cada troca (slide, quem pergunta) no momento certo;
   - legenda dentro da caixa e sem erro de grafia; título sem cortar e sem prometer o que a fala não entrega;
   - apoio no momento certo; volume (≈ -16 LUFS).

## 3. Revisão e limpeza
- **No fim**, uma tabela: post, título, duração, nota, observação; e a aula completa com as duas pontas. A pessoa aprova ou pede ajuste (ajuste vira `-v2`).
- **Limpar depois da aprovação:** `posts/.tmp-post/`, a pasta `cortes/` (os cortes brutos, se os posts foram aprovados), as folhas de quadros e o `.leitura.txt`. Ficam a live, a transcrição `.srt`, os `.json`, a aula completa e os posts.
