---
name: aftermovie
description: Aftermovie (vídeo-resumo de evento) da PPGVET/PPG - aula prática, fórum, aula de abertura, feira - a partir do material bruto, com triagem dos clipes, molde em blocos, música que fecha na logo e conferência. Pela porta video.
disable-model-invocation: true
---

# Aftermovie (resumo de evento)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/video.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/video.md` (corte, ordem de Murch, transições, cor) e `${CLAUDE_PLUGIN_ROOT}/regras/antislop-midia.md`. Nível de esforço: padrão; campanha ou evento grande, caprichado (`nucleo.md`).
- Em cada comando: `PY=$(cat ~/.ppgvet/python); S="${CLAUDE_PLUGIN_ROOT}/scripts"; FF=$("$PY" "$S/comum.py" --ff)`. Pasta: a linha `edicoes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<edicoes>`).

## O que preciso de você
- **A pasta do material bruto** do evento (todos os clipes), o nome do evento, a marca e a pós.
- **Duração e onde vai:** 30 a 45 s (Reels, story) ou 60 a 90 s (feed, YouTube); 9:16 ou 4:5.
- **A chamada do fim**, se houver (texto e link do gerador, `canais.md`), e a música (da pasta `musicas/`, com mudança de trecho clara e final marcado).
- Exemplo: *"aftermovie de 40 s da aula prática de bovinos em Pará de Minas, pós RNGB, material na pasta Evento-RNGB"*.

## O molde (estudo de 25/11/2026: o que faz o melhor aftermovie da casa)
Vence pela **estrutura**, não pelo corte na batida: lugar → pessoas → detalhes → momento-chave → logo, com o ritmo desacelerando no fim.

| bloco | 30 a 45 s | 60 a 90 s | plano médio | o quê |
|---|---|---|---|---|
| gancho | 0 a 3 s | 0 a 3 s | 0,5 a 0,8 s | os 3 ou 4 planos mais fortes; entende sem som |
| lugar | 3 a 7 | 3 a 10 | ~1 s | aberto, chegada, placa |
| pessoas | 7 a 16 | 10 a 28 | 0,8 a 1,2 s | rostos atentos, professor, turma |
| detalhes | 16 a 26 | 28 a 48 | 0,6 a 1 s | mão, instrumento, animal, ração, tela |
| momento | 26 a 34 | 48 a 66 | 1,5 a 3 s | o ápice, segurado; até 2 sound bites de 3 a 6 s (fala em até 25% do vídeo) |
| fecho | 34 a 45 | 66 a 90 | 2 a 3,5 s | último plano lento; o encerramento da marca entra sozinho |

- **Ritmo:** o bloco troca quando a música muda de trecho (salto de ~4 LU no `ebur128` de curto prazo); corte exato na batida só na troca de bloco. Na versão longa, uma ponte de lugar ou tempo (o quadro da fazenda na parede que vira a fazenda real).
- **Efeito** só com motivo (tempo, lugar, ênfase), um tipo por vídeo, nunca no rosto, nunca piscando; glitch e fim sem logo são slop. Grão leve para unir câmeras pode.
- **Cor:** corrigir plano a plano e casar a pele entre câmeras; depois um look único. Luz roxa de palco puxa a pele para magenta: corrigir antes do look. A cor da marca vem da cena (luz, crachá), não de filtro.
- **Som:** música protagonista; sob o sound bite ela desce e volta (o script faz); 1 a 3 sons reais do lugar (aplauso, riso), baixos.

## Passo a passo
1. **Triagem**, sem assistir tudo: `"$PY" "$S/aftermovie.py" triagem "<pasta do bruto>" --saida "<edicoes>/<evento>"`. Sai o `triagem.json` (nitidez, estourado, escuro, rosto, movimento, som de cada clipe) e a `triagem.jpg` (um quadro por clipe, numerado). Descartar tremido, fora de foco e estourado pelos números; abrir a folha e escolher por bloco. Clipe com voz (`som_db` acima de ~-35): transcrever só esses e escolher o sound bite pelo texto antes da imagem.
2. **Plano:** a tabela dos blocos com os clipes escolhidos (número da folha), o sound bite (frase exata), a música e a chamada. Esperar o ok.
3. **Roteiro** em `<edicoes>/<evento>/roteiro.json` (formato no começo do `aftermovie.py`): os cortes de cada clipe (`de`, `ate`), o `bloco`, o centro do recorte (`x`) e `"fala": true` no sound bite. Prévia: `"$PY" "$S/aftermovie.py" montar <roteiro.json> --previa`; olhar por folha de quadros (`folha.py`) e ajustar.
4. **Final:** o mesmo comando sem `--previa`. O resumo por bloco sai na tela: FALHA (plano abaixo de 0,25 s) barra; AVISO (fala acima de 25%, duração fora da faixa) é para olhar.
5. **Conferir e dar nota:** `checar.py` com `--instagram` (`nucleo.md`), mais o olho: o gancho prende, os detalhes são do assunto real, a pele está certa, a logo fica parada no fim. Abaixo de 8: corrigir. Peça para o Instagram: a pergunta da legenda do post já foi no plano (`nucleo.md`, passo 1).
6. **Entregar** o vídeo e a folha com a nota. Limpar depois da aprovação: as prévias; ficam o `roteiro.json` e a triagem, que servem para refazer.
