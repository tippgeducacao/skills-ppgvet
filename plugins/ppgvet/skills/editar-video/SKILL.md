---
name: editar-video
description: Edição de vídeo da PPGVET/PPG com ffmpeg, whisper local e HyperFrames. Corte de fala, legenda, caixinha de pergunta, cartões de destaque, zoom, cor de iPhone HDR, música, vinheta, Reels 9:16 e compressão. Use quando pedirem para editar, cortar, legendar, montar, comprimir ou "deixar igual à referência" um vídeo, ou um vídeo vertical de alguém falando para o Instagram. Chamada, aula curricular, conferir aula e cortes de live têm skill própria.
disable-model-invocation: true
---

# Editar vídeo

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills), `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças), `${CLAUDE_PLUGIN_ROOT}/regras/video.md` (técnica, motion e Instagram), `${CLAUDE_PLUGIN_ROOT}/regras/bancos-e-referencias.md` (referência, inserções, música e sons).
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"` e `FF=$("$PY" "$S/comum.py" --ff)`.
- Trabalho: `<edicoes>/<assunto>/<video>/`, com roteiro, legenda, `tmp/` e o projeto `hf/`. Entrega: ao lado dos originais (`pasta_saida` no roteiro), como `<assunto>-<tema>-vN.mp4`.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **O vídeo ou o áudio** (arquivo ou link) e **o que quer**: Reels de fala, corte, legenda, compressão, limpar o som…
- **Onde vai** (Instagram, site, WhatsApp) e, se tiver, **uma referência** do estilo (link).
- Para Reels com textos animados: o que destacar, se já souber (senão o Claude propõe no plano).
- Exemplo de pedido: *"edita esse vídeo do Rafael pra Reels, no estilo dessa referência"* + arquivo e link.

## Passo a passo
1. **Ver sem mexer.** Rodar `ffprobe`, olhar a folha de quadros e conferir orientação, cor e os canais de áudio (regras de cor e áudio da câmera em `video.md`). Câmera deitada: `transpose=1` ou `2`, conferir num quadro.
2. **Transcrever local** (o áudio não sai do computador):
   `"$PY" "$S/transcrever.py" X w -- --prompt "Éé... ahn, hum, né, é." -dtw large.v3.turbo -nfa -ml 1 -sow -ojf`
   O prompt faz o whisper escrever os vícios de fala, que sem ele somem. Depois, `"$PY" "$S/blocos.py" a.wav w.json` lista os blocos de fala entre silêncios, com as palavras (o `a.wav` sai de `"$FF" -i X -ar 16000 -ac 1 a.wav`).
3. **Plano** para a pessoa, em português: para cada vídeo, o que sai, textos na tela (pergunta e cartões seguem o "texto da arte" do `oficio/copy.md`), inserções (foto tratada antes pela `editar-foto`), música e o roteiro do motion. Esperar o ok.
4. **Editar** todos, um atrás do outro, sem parar.
5. **Conferir e dar nota** de 0 a 10 (lista em `nucleo.md` mais ritmo, leitura, marca e acabamento); abaixo de 8, corrigir.
6. **Revisão no fim:** folha de quadros e nota de cada vídeo; para os Reels, o link do Studio para ajuste fino. Limpar depois da aprovação: `tmp/`, `hf/` e as prévias (ficam o original, o `roteiro.json`, a `legenda.srt` e a entrega).

## Só áudio (podcast, locução, áudio de WhatsApp)
Mesmo fluxo (ver, plano, fazer, conferir), sem imagem. Regras de som: `oficio/som.md`.
- **Ruído** (zumbido, ar-condicionado, sala): `"$PY" "$S/limpar_voz.py" <entrada> <limpo.wav>` (parte `voz` do kit, sob demanda). Ouvir antes e depois num trecho com `ouvir.py`: voz metálica ou cortada = voltar ao original.
- **Cortar:** transcrever e achar os blocos como nos passos 2 e 3; juntar na fronteira da palavra, com fade de 30 ms.
- **Volume:** -16 LUFS e pico até -1,5 dBTP (a Apple Podcasts pede -16 ±1 e pico até -1): `"$FF" -i <limpo.wav> -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 <saida>`.
- **Entrega** no formato que veio, ou MP3 de 128 kbps (voz) a 48 kHz; nome `<assunto>-<tema>-vN.mp3`.
- **Conferir:** `"$PY" "$S/checar.py" <saida>` (volume, pico e canais). FALHA barra a entrega.

## Vídeo vertical de fala com motion (Reels)
Pessoa falando para a câmera, com caixinha de pergunta, cartões de destaque, legenda, logo, música e vinheta. Usa o HyperFrames (parte `motion` do kit, sob demanda: `nucleo.md`, "Ambiente").

Roteiro `roteiro.json` (tempos em segundos do **original**):
```json
{
 "fonte": "/caminho/do/original/video1.MP4", "girar": "transpose=1", "canal": "c0",
 "marca": "ppgvet", "rosto": [0.52, 0.31],
 "blocos": [[5.64, 7.86], [8.89, 13.21]],
 "pergunta": {"texto": "Nutrição de bovinos é um caminho fácil?", "ate": 3.4},
 "destaques": [
   {"linhas": ["A faculdade prepara pouco para a *formulação*"], "de": 20.35, "ate": 24.4}],
 "musica": "musicas:acustica-animada.mp3",
 "pasta_saida": "/caminho/da/pasta/dos/originais", "saida": "assunto-tema-v1.mp4"
}
```
- `blocos`: só a fala que fica. Saem vícios ("né", "é, é"), falso começo, frase repetida (fica a última tomada) e contagem.
  - Para cortar no meio de um bloco, achar a micropausa pela energia e conferir a junção com `"$PY" "$S/ouvir.py" a.wav "ini fim" "ini fim"`, que transcreve só a junção.
  - O começo fica exatamente na primeira palavra útil.
- `girar`: o filtro de rotação do ffmpeg. Vídeo já em pé: `"null"` (com aspas: é o filtro que não faz nada). Sem o campo, o padrão é `transpose=1`, que gira 90°.
- `rosto`: centro do rosto (fração da largura e da altura). O plano alterna entre o normal e um zoom de 1,16 centrado nele, no máximo a cada 5 s. Os outros cortes ficam como jump cut.
- Duas ou mais pessoas: `"rostos": {"ana": [0.25, 0.335], "rafael": [0.75, 0.33]}` e quem fala como 3º item de cada bloco (`[ini, fim, "ana"]`). O plano alterna entre aberto, fechado (1,8) e médio (1,35) em quem fala, no máximo a cada 5 s, ou quando o close está numa pessoa e a outra começa a falar.
- `pergunta` com `"de"` e `"ate"` (tempos do original): a caixinha entra no momento da pergunta, não no começo do vídeo.
- `*palavra*`: destaque na cor da marca (no cartão) ou em rosa (na legenda).
- `marca`: `ppgvet` ou `ppg`. Define as cores, a logo, o ícone da caixinha e a vinheta.
- `musica`: escolhida pela regra de música de `bancos-e-referencias.md`; precisa ser mais longa que o vídeo.

Comandos:
1. `"$PY" "$S/reels.py" roteiro.json base` corta, gira, alterna o zoom e duplica o canal, gerando `tmp/base.mov`.
2. `"$PY" "$S/reels.py" roteiro.json legenda` gera `legenda-bruta.srt`. Revisar e salvar como `legenda.srt`:
   - termos certos (regra de grafia de `nucleo.md`);
   - sem ponto final;
   - `*palavra-chave*`;
   - palavra que ficou no grupo errado volta para o grupo dela.
   Para aplicar trocas em lote: `"$PY" "$S/revisar_legenda.py" <pasta> regras.json`, com `{"trocar": {...}, "chaves": [...]}`.
3. `"$PY" "$S/hf.py" roteiro.json` gera o projeto HyperFrames em `hf/`.
4. Ler a skill `hyperframes` antes. Todo comando do HyperFrames roda com `eval "$("$PY" "$S/comum.py" --hf-env)"` antes, que também define `$HF`, a versão fixa do pacote, para ele achar o ffmpeg completo. No projeto `hf/`:
   - `npx "$HF" check` e `snapshot`;
   - **Studio no navegador** (na revisão do fim, para ajuste fino): `npx "$HF" preview --background`. Mandar para a pessoa o link que ele mostrar (com `#project/hf` no fim); depois dos ajustes, renderizar de novo e parar com `npx "$HF" preview --stop`;
   - render (no Mac com `nice -n 10` na frente): `npx "$HF" render . -o ../tmp/hf.mp4 --fps 30000/1001 --quality delivery`.
5. `"$PY" "$S/reels.py" roteiro.json final` junta a vinheta da marca e a mixagem e salva em `pasta_saida`. `--previa` faz uma versão leve na pasta de trabalho.

O que o `hf.py` desenha, na identidade da marca e com Montserrat, nas faixas do padrão Instagram (`video.md`):
- **Caixinha de pergunta** no estilo do Instagram: entra com pop, o ícone da marca vem depois e a pergunta entra palavra por palavra.
- **Cartões:** barra colorida e o cartão abre da esquerda. O título entra de 4 jeitos, que o `hf.py` alterna sozinho sem repetir o do cartão anterior: `palavras` (uma a uma, com desfoque), `wipe` (revela com borda de luz), `bate` (letra grande que assenta) e `odometro` (o número conta até o valor; escolhido sozinho quando o cartão tem número de até 4 dígitos, como "*30* dias"). Para fixar um, `"entrada": "bate"` no destaque. Em Reels, só cartão de uma linha (`linhas`, sem `itens`), porque a lista com check não agradou. O corte termina na frase forte, sem muleta ("e é comprovado").
- **Legenda simples:** o grupo entra inteiro, branco com sombra.
- **Logo** da marca embaixo, o vídeo todo.
