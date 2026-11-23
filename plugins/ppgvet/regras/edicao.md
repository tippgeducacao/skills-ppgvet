# Regras de edição (valem para todas as skills de vídeo)

Cada skill traz só o próprio passo a passo. O que vale para todas está aqui. Marca e peças: `marca.md`, nesta mesma pasta.

## Ambiente
- `PY=$(cat ~/.ppgvet/python)`, `S=<pasta scripts do pacote>` (a skill mostra o caminho) e `FF=$("$PY" "$S/comum.py" --ff)`, o ffmpeg completo (tem zscale, legenda e texto; o `ffprobe` fica na mesma pasta). Se `~/.ppgvet/python` não existir, rodar a skill `instalar` primeiro.
- Pastas desta pessoa: `"$PY" "$S/comum.py" --pastas` (chamadas, aulas, conferir, cortes, edicoes, musicas, downloads).
- Nos roteiros: `acervo:<caminho>` é uma peça do pacote (`acervo:logos-animadas/encerramento-ppgvet-vertical.mp4`) e `musicas:<arquivo>` é uma música da pasta `musicas/` da pessoa.

## Arquivo e versões
- **Original nunca é mexido.** Tudo sai em arquivo novo.
- **Versão nova nunca sobrescreve:** `-v2`, `-v3`… Versão com defeito: avisar e perguntar antes de apagar.
- **Nome de arquivo:** minúsculo, com hífen, do geral ao específico (`assunto-tema-v1.mp4`). Exceções: a aula curricular usa o título da tarefa, e a chamada usa o padrão de pastas dela (`CHAMADA N/`, `chamada <curso> N - <tema>.mp4`).
- **Menor, mas nunca mais feio:** compressão para site ou WhatsApp é H.264 `-crf 23 -preset slow -movflags +faststart`, conferindo que não piorou.
- **Organização:** o trabalho fica na pasta padrão do tipo (`--pastas`), com o nome padrão; a entrega vai onde a skill diz. Nada solto fora disso.

## Como trabalhar
1. **Plano, uma vez:** antes de começar, mostrar o que vai ser feito (cada skill diz o que o plano dela inclui) e perguntar o que falta saber. Esperar o ok.
2. **Depois do ok, fazer tudo sem parar:** o lote inteiro, um atrás do outro. As dúvidas vão no plano; parar no meio só se surgir uma que a pessoa precisa decidir.
3. **Conferir e dar nota** a cada entrega: nota de 0 a 10 em cada critério da skill, mais acabamento geral. Abaixo de 8: corrigir sozinho e conferir de novo. O que vale para todo vídeo:
   - folha de quadros durante todo o tempo de cada gráfico (nada cobre nem encosta no rosto);
   - começo e fim transcritos de novo;
   - volume: `"$FF" -i out.mp4 -af loudnorm=print_format=summary -f null -` (voz ≈ -16 LUFS, pico ≤ -1,5 dBTP) e os dois canais no mesmo nível.
4. **Revisão no fim:** tudo pronto de uma vez (folha de quadros, nota de cada vídeo em uma linha e o que foi feito) para a pessoa aprovar ou pedir ajuste. Ajuste vira versão nova (`-v2`).
5. **Limpar depois da aprovação:** apagar só o que a própria skill criou de intermediário (cada skill lista): `tmp/` e `hf/` dos Reels, `posts/.tmp-post/` dos cortes, transcrições de trabalho, folhas de quadros e prévias. **Nunca** o original, a entrega, a legenda usada no vídeo nem os roteiros (`.json`), que servem para refazer.

- **Não inventar visual, texto, marca nem nome de pessoa:** perguntar no plano. Nome do curso, arte de CTA e grafia de nome vêm da pessoa ou de fonte confiável.
- **Doc oficial:** ferramenta, formato de rede social ou plataforma segue a documentação oficial, conferida na hora quando o detalhe pode ter mudado (limite, formato, licença). Dizer qual doc foi usada.

## PC e tokens
- **PC:** os scripts já rodam com prioridade baixa; o que demora vai em segundo plano. Um whisper por vez (ele já usa todos os núcleos); dá para renderizar um vídeo enquanto transcreve o próximo. Nunca vários renders pesados ao mesmo tempo.
- **Tokens** (quase tudo roda no computador, então quase nada precisa passar pela conversa):
  - comando sem progresso na saída (os scripts já saem em silêncio; ffmpeg com `-v error -nostats`, yt-dlp com `--quiet --no-warnings`, pip com `-q`). Saída longa: só o fim (`| tail -5`);
  - vídeo se olha por folha de quadros (`"$PY" "$S/folha.py" video.mp4 folha.jpg [a cada N s]`), nunca quadro a quadro;
  - transcrição, log e texto grande se buscam com `grep` ou se leem por trecho; inteiros só quando ler a fala é a tarefa (escolher cortes, conferir aula);
  - não reler arquivo já lido nem colar log ou JSON grande na resposta;
  - resposta curta: o que foi feito, onde está, a nota e o que precisa de decisão.

## Conteúdo
- **Grafia:** na dúvida sobre um nome (doença, toxina, fármaco, raça, técnica, pessoa, marca, software), **pesquisar a grafia certa** em fonte confiável antes de escrever. Nunca chutar o que o whisper ouviu (exemplo: "NASCE" era NASEM).
- **Referência de estilo** (vídeo ou print): copiar paleta, ritmo, transições e entrada do texto, nunca o conteúdo, a logo ou a marca dela.
- **Inserções** (imagem ou vídeo de apoio):
  - só quando somam. Sem imagem boa, o vídeo sai sem inserção: o ritmo vem do zoom e dos cartões;
  - sempre do assunto real, nunca genérica fingindo ser aluno, professor ou sede. Nada gerado por IA;
  - onde procurar, nesta ordem: 1) Drive de insumos da PPGVET (https://drive.google.com/drive/folders/1vg6Wfy3FcLh9WX-qtrpwFund_bTDHy2p); 2) Wikimedia Commons: vídeo com `"$PY" "$S/commons.py" "termo"` (busca só vídeo) e `"$PY" "$S/baixar_commons.py" <pasta> "File:…"` (baixa com a origem); imagem, buscar no site do Commons e baixar com o mesmo `baixar_commons.py`; preferir domínio público ou CC0; 3) Openverse (API pública);
  - todo arquivo de fora vai com um `.origem.txt` ao lado (link e licença);
  - nunca se passar por navegador nem contornar verificação de site.

## Técnica
- **Corte:** na fronteira da palavra (~60 ms antes, ~100 ms depois), com fade de áudio de 30 ms. Silêncio longo vira uma pausa curta.
- **Cor:**
  - iPhone HDR (`arib-std-b67`/`smpte2084`): converter para BT.709 antes de misturar, com `zscale=t=linear:npl=520,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=1.06`;
  - etiquetar toda saída com `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`.
- **Áudio da câmera:** medir cada canal (`"$FF" -i X -af "pan=mono|c0=c0,volumedetect" -f null -` e depois `c1`). A câmera Sony grava o microfone só num lado; se um lado estiver mudo (~-80 dB), duplicar o canal bom.
- **Ruído na voz** (zumbido, ar-condicionado, sala): `"$PY" "$S/limpar_voz.py" base.mov voz.wav` (DeepFilterNet 3, local) e mixar essa voz no lugar do áudio original. Só quando o ruído incomoda. Antes do lote, gerar uma prévia de um trecho (antes e depois) para a pessoa ouvir.
- **Volume:** voz a -16 LUFS. A música fica fixa e baixa sob a voz, do começo ao fim, com entrada suave, e **sobe** na logo ou no CTA final (a vinheta perde o som próprio). Os scripts já fazem a mixagem, cada um no seu padrão: Reels com fundo a -33 LUFS (17 dB abaixo da voz) e -15,5 LUFS na vinheta; posts de cortes com fundo a ~-35 LUFS; chamada com final a ~-14 LUFS. Nunca subir o fundo acima disso; na dúvida, mais baixo.

## Motion (textos e cartões animados)
- Texto na tela, cartões e inserções são animados no HyperFrames, em nível profissional e na identidade da marca. PNG com fade no ffmpeg não basta.
- Entrada com cauda longa (expo/back out); saída mais curta (blur e fade). Nada cobre nem encosta no rosto. O corte e a fala continuam no ffmpeg.
- **O roteiro do motion entra no plano** (cada texto, cartão e caixinha, com o momento): aprovado o plano, renderizar direto. Na revisão do fim, oferecer o Studio do HyperFrames no navegador para ajuste fino. Na nota, entram também ritmo, leitura e marca.
- Animação de motion design do zero (explicativo, história): plugin **animate**.

## Padrão Instagram vertical (Reels e Stories)
- **Arquivo:** 1080x1920 (9:16), MP4 H.264 + AAC (até 48 kHz, 128 kbps), fps fixo entre 23 e 60 (30, ou o da câmera, como 29,97), `-movflags +faststart`, vídeo até 25 Mbps, de 3 s a 15 min, até 300 MB. Doc oficial da Meta, conferida em 13/11/2026: [IG User Media](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media) e [Reels Publishing API](https://developers.facebook.com/documentation/video-api/guides/reels-publishing).
- **Prévia no feed** = recorte 4:5 central (y 285 a 1635). Rosto, texto e logo ficam dentro dele.
- **Margem livre:** nenhum texto nem logo nos 250 px de cima e nos 250 px de baixo.
- **Anúncio pago** (zona segura da Meta): além disso, 14% de cima, 35% de baixo e 6% dos lados sem texto nem logo. Vídeo orgânico não precisa.
- **Faixas dos Reels** (o `hf.py` já usa), de cima para baixo: rosto até ~y 900; legenda no peito, logo abaixo do queixo (topo em y 915), com contorno escuro; caixinha e cartões de y 1035 a ~1390; logo com 210 px de largura, de y 1470 a 1604. A chamada e os posts de cortes têm o layout deles (está em cada skill).
- **Ritmo dos Reels:** o zoom muda no máximo a cada 5 s; os outros cortes ficam como jump cut no mesmo plano.

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
