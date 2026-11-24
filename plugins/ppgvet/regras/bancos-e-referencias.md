# Material de fora: referência, inserções, música e sons

Lido quando o trabalho usa material que não é da PPGVET, junto com o `nucleo.md`.

## Referência e inserções
- **Referência de estilo** (vídeo ou print): copiar paleta, ritmo, transições e entrada do texto, nunca o conteúdo, a logo ou a marca dela.
- **Inserções** (imagem ou vídeo de apoio):
  - só quando somam. Sem imagem boa, o vídeo sai sem inserção: o ritmo vem do zoom e dos cartões;
  - sempre do assunto real, nunca genérica fingindo ser aluno, professor ou sede. IA só em último caso, com aprovação (`nucleo.md`);
  - onde procurar, nesta ordem: 1) Drive de insumos da PPGVET (https://drive.google.com/drive/folders/1vg6Wfy3FcLh9WX-qtrpwFund_bTDHy2p); 2) Wikimedia Commons: vídeo com `"$PY" "$S/commons.py" "termo"` (busca só vídeo) e `"$PY" "$S/baixar_commons.py" <pasta> "File:…"` (baixa com a origem); imagem, buscar no site do Commons e baixar com o mesmo `baixar_commons.py`; preferir domínio público ou CC0; 3) Openverse (API pública);
  - todo arquivo de fora vai com um `.origem.txt` ao lado (link e licença);
  - nunca se passar por navegador nem contornar verificação de site.

## Música, sons e efeitos (baixados quando precisar)
**Escolher a música:**
1. `"$PY" "$S/comum.py" --musicas` lista as faixas da pasta `musicas/` da pessoa e marca como `USADA` as que estão entre as 10 últimas usadas. Os scripts anotam sozinhos cada música usada em `musicas/musicas-usadas.txt`.
2. Escolher uma faixa `livre` que combine. Nunca repetir uma das 10 últimas nem repetir faixa dentro da mesma série (exemplo: as chamadas do mesmo professor, os posts da mesma live).
3. Se não houver faixa livre que combine, pedir para a pessoa baixar uma nova (abaixo), com 2 ou 3 palavras de busca para o clima do vídeo (exemplo: "corporate upbeat", "inspiring acoustic", "positive piano").

**Que música serve:**
- animada mas séria, **só instrumental** (sem vocal: conferir com `"$PY" "$S/transcrever.py" musica.mp3 letra`: o `letra.srt` não pode ter frases);
- nada infantil ou brincalhão (ukulele bobo, assobio, "happy");
- batida firme, de ~110 a 130 BPM, para fala de professor; calma só quando pedirem e nos posts de cortes de live;
- **mais longa que o vídeo**, porque nunca vai em loop.

**Onde baixar, nesta ordem.** A pessoa baixa no navegador. O Claude não baixa desses sites, porque eles bloqueiam robô.
1. **Drive de insumos da PPGVET:** https://drive.google.com/drive/folders/1vg6Wfy3FcLh9WX-qtrpwFund_bTDHy2p
2. **Pixabay Music** (https://pixabay.com/music/): grátis para uso comercial e sem crédito obrigatório. Não pode redistribuir o arquivo solto ([resumo da licença](https://pixabay.com/service/license-summary/)). Para baixar: abrir a faixa e clicar em Download.
3. **Mixkit** (https://mixkit.co/free-stock-music/): licença "Stock Music Free". Conferir a licença na página da faixa antes de usar. Para baixar: clicar em Download na faixa.

Não usar a Biblioteca de áudio do YouTube em vídeo para o Instagram: a doc do YouTube diz que é recurso "exclusivo do YouTube Studio" ([ajuda do YouTube](https://support.google.com/youtube/answer/3376882?hl=pt-BR)).

**Depois de baixar:** salvar em `musicas/` com nome minúsculo-com-hífen (`corporativa-inspiradora.mp3`) e criar ao lado um `<nome>.mp3.origem.txt` com o link da página da faixa e a licença. Os scripts usam esse arquivo para escrever o `creditos.txt`.

**Sons (whoosh, pop, digitação) e efeitos visuais (brilho, partículas):** só quando a pessoa pedir. Mesma ordem: insumos, depois Pixabay (https://pixabay.com/sound-effects/) e Mixkit (https://mixkit.co/free-sound-effects/), com `.origem.txt`. Os efeitos visuais costumam vir sobre fundo preto: misturar com `blend=all_mode=screen` no ffmpeg ou `mix-blend-mode: screen` no HyperFrames. Som de efeito vai baixo, abaixo da voz.
