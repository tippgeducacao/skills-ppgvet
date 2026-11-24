# Material de fora: referência, inserções, música e sons

Lido quando o trabalho usa material que não é da PPGVET, junto com o `nucleo.md`. Licenças e termos conferidos em 24/11/2026; conferir de novo na página oficial quando a dúvida for de uso.

## Acesso
- O Claude busca sozinho só por **API oficial** ou link que a pessoa mandou. Site que barra robô (`robots.txt`) ou pede login: a pessoa busca e cola o print, o link ou o arquivo. Nunca se passar por navegador nem contornar verificação de site.
- Todo arquivo de fora vai com um `.origem.txt` ao lado (link e licença).

## Referência (moodboard)
Copiar o como (paleta, ritmo, transição, entrada do texto, composição), nunca o conteúdo, a logo, o layout ou a marca da referência.

| procura | onde | acesso do Claude |
|---|---|---|
| anúncio do setor (oferta, gancho, formato) | Meta Ad Library (https://www.facebook.com/ads/library, Brasil, todos os anúncios, termo do setor) | print: a pessoa busca no site, que é aberto e sem login. Só se o MCP `meta-ads` estiver conectado nesta máquina, o Claude lista os anúncios sozinho (`ads_library_search`) |
| motion, ritmo, corte | Motionographer, Vimeo Staff Picks | Motionographer por link; Vimeo por print |
| foto, direção de arte, design | Cosmos.so, Savee, Dribbble, Behance, Pinterest | Cosmos, Savee e Dribbble por link; Behance e Pinterest por print |
| luz, cor e enquadramento de cinema | FilmGrab (grátis), ShotDeck (pago) | FilmGrab por link; ShotDeck por print |
| Reels de concorrente | Instagram | print ou link do vídeo baixado com `baixar-video` (só para estudo) |

Fluxo de 10 a 15 min (nível caprichado, ou quando pedirem):
1. Perguntar peça, público e 3 palavras de clima; dizer onde buscar pela tabela.
2. A pessoa junta de 6 a 12 referências (prints, links, vídeos).
3. O Claude monta uma folha só (`ffmpeg tile`) e anota em cada uma: paleta (3 a 5 cores), tipografia, ritmo (cortes por segundo, entrada do texto), composição, luz; em anúncio, também gancho, oferta, prova e CTA.
4. Devolve 2 ou 3 direções já nas cores do `marca.md`; a escolhida vira o roteiro do plano.

## Inserções (imagem ou vídeo de apoio)
- Só quando somam. Sem imagem boa, o vídeo sai sem inserção: o ritmo vem do zoom e dos cartões.
- Sempre do assunto real (banco e IA: regra no `nucleo.md`). CC0 libera o direito autoral, não o direito de imagem de quem aparece: pessoa reconhecível só em contexto neutro e real.
- Sem logo ou embalagem de outra marca à vista (parece patrocínio); se não der para evitar, desfocar.
- Onde procurar, nesta ordem:
  1. Drive de insumos da PPGVET (link em "Música", abaixo).
  2. Wikimedia Commons: vídeo com `"$PY" "$S/commons.py" "termo"` (busca só vídeo) e `"$PY" "$S/baixar_commons.py" <pasta> "File:…"` (baixa com a origem); imagem, buscar no site do Commons e baixar com o mesmo `baixar_commons.py`; preferir domínio público ou CC0.
  3. Openverse (`api.openverse.org`, sem chave; filtros `license=cc0,pdm` e `license_type=commercial`).
  4. Pexels ou Pixabay, só pela API e só se a pessoa tiver a chave grátis: uso comercial sem crédito, mas não pode redistribuir o arquivo solto.

## Música
**Escolher:**
1. `"$PY" "$S/comum.py" --musicas` lista as faixas da pasta `musicas/` da pessoa e marca como `USADA` as que estão entre as 10 últimas usadas. Os scripts anotam sozinhos cada música usada em `musicas/musicas-usadas.txt`.
2. Escolher uma faixa `livre` que combine. Nunca repetir uma das 10 últimas nem repetir faixa dentro da mesma série (exemplo: as chamadas do mesmo professor, os posts da mesma live).
3. Se não houver faixa livre que combine, pedir para a pessoa baixar uma nova (abaixo), com 2 ou 3 palavras de busca para o clima do vídeo (exemplo: "corporate upbeat", "inspiring acoustic", "positive piano").

**Que música serve:**
- animada mas séria, **só instrumental** (sem vocal: conferir com `"$PY" "$S/transcrever.py" musica.mp3 letra`: o `letra.srt` não pode ter frases);
- nada infantil ou brincalhão (ukulele bobo, assobio, "happy");
- batida firme, de ~110 a 130 BPM, para fala de professor; calma só quando pedirem e nos posts de cortes de live;
- **mais longa que o vídeo**, porque nunca vai em loop.

**Onde baixar, nesta ordem.** A pessoa baixa no navegador: nenhum banco de música tem API de áudio para uso comercial.
1. **Drive de insumos da PPGVET:** https://drive.google.com/drive/folders/1vg6Wfy3FcLh9WX-qtrpwFund_bTDHy2p
2. **Pixabay Music** (https://pixabay.com/music/): grátis para uso comercial e sem crédito obrigatório. Não pode redistribuir o arquivo solto ([resumo da licença](https://pixabay.com/service/license-summary/)). Preferir faixa **sem o escudo** de Content ID: com ele, o Instagram pode silenciar o vídeo ([FAQ](https://pixabay.com/service/faq/)). Para baixar: abrir a faixa e clicar em Download.
3. **Mixkit** (https://mixkit.co/free-stock-music/): licença "Stock Music Free" (web e rede social sim; TV e rádio não). Conferir a licença na página da faixa antes de usar.

Não usar:
- Biblioteca de áudio do YouTube em vídeo para o Instagram: a doc do YouTube diz que é recurso "exclusivo do YouTube Studio" ([ajuda do YouTube](https://support.google.com/youtube/answer/3376882?hl=pt-BR)).
- Música da biblioteca do próprio Instagram em post de pós ou anúncio: guias de terceiros dizem que conta comercial tem uso limitado (a ajuda da Meta não abriu para conferir); regra da casa: não usar.
- Música famosa ou "em alta" sem licença.

**Depois de baixar:** salvar em `musicas/` com nome minúsculo-com-hífen (`corporativa-inspiradora.mp3`) e criar ao lado um `<nome>.mp3.origem.txt` com o link da página da faixa e a licença. Os scripts usam esse arquivo para escrever o `creditos.txt`.

## Sons e efeitos visuais
Só quando a pessoa pedir ou o nível pedir (`nucleo.md`). Como usar: `oficio/som.md`; para o pico cair no quadro do gesto, `"$PY" "$S/sons.py" pico <som>` dá em quantos ms o som "bate". Onde procurar, nesta ordem:
1. **Acervo do pacote** (`acervo/sons/`): os 23 mais usados em edição: interface (clique, pop, notificação, sucesso, erro, ding, brilho, tique-taque, glitch), transição (whoosh curto e longo, swipe, reverse, riser), impacto (impacto grave, madeira, vidro tilintando, saco caindo) e foley (teclado, obturador, folha virando, clique duplo de mouse, aplausos). Todos com volume parecido: no mix, cada um entra baixo, abaixo da voz. Origem e licença: `acervo/sons/ORIGEM.md`.
2. Drive de insumos.
3. **Kenney** (https://kenney.nl/assets, pacotes Interface Sounds, Impact Sounds, UI Audio, Digital Audio): tudo CC0.
4. **Freesound** (https://freesound.org), filtrado em "Creative Commons 0": a página do som a pessoa abre; o Claude acha sons CC0 pela API do Openverse (`api.openverse.org/v1/audio/?license=cc0`) e baixa a prévia. CC BY só com crédito, e nunca CC BY-NC.
5. Pixabay (https://pixabay.com/sound-effects/) e Mixkit (https://mixkit.co/free-sound-effects/).

Não usar BBC Sound Effects: a licença é só para uso pessoal, educacional ou de pesquisa. Efeito visual sobre fundo preto: misturar com `blend=all_mode=screen` no ffmpeg ou `mix-blend-mode: screen` no HyperFrames. Som de efeito vai baixo, abaixo da voz.
