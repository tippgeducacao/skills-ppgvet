---
name: patrocinador-podcast
description: Vídeo de boas-vindas a patrocinador dos podcasts da PPGVET com o mascote e o produto - prompts para o Google Flow, conferência de cada geração e edição final com cartela e logos. Use quando pedirem vídeo de patrocinador, boas-vindas a parceiro, prompt de Nano Banana ou Veo (mascote, cenário, produto), folha do mascote ou editar um vídeo do Flow.
---

# Vídeo de patrocinador do podcast (Google Flow + edição)

Meta: comercial 3D bonito e bem animado, com o menor número de erros e de gerações. A pessoa gera no Flow; o Claude prepara as imagens, escreve os prompts, confere cada resultado e faz a edição. Moldes de prompt: [prompts.md](prompts.md).

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/marca.md`, `${CLAUDE_PLUGIN_ROOT}/regras/video.md` e `${CLAUDE_PLUGIN_ROOT}/regras/bancos-e-referencias.md`. Nível de esforço: caprichado (o vídeo carrega a marca do podcast e do parceiro).
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"`, `A="${CLAUDE_PLUGIN_ROOT}/acervo"` e `FF=$("$PY" "$S/comum.py" --ff)`. Recortar fundo usa a parte `foto` do kit (sob demanda).
- Pasta do trabalho: `<patrocinadores>/<patrocinador>-<podcast>/` (minúsculo-com-hífen; `<patrocinadores>` de `"$PY" "$S/comum.py" --pastas`), com `roteiro.md`: pedido original, decisões, cada prompt, o que deu errado em cada versão e a trilha usada. Trabalhos anteriores na mesma pasta servem de exemplo.

## O que preciso de você
- **Podcast** e **patrocinador**, e o pedido ou roteiro (cenário, ação, clima). Roteiro que vem se segue; não inventar cenário, ideia, texto nem cor.
- **Logo do patrocinador** em alta e transparente, e **foto oficial do produto** (site da empresa). Nome e logo como a empresa usa.
- Acesso ao **Google Flow** (a pessoa gera; o Claude não gera nada sem o pedido dela, uma etapa por vez).

## O plano desta skill
Antes de gerar qualquer coisa: o roteiro em cenas (cenário, ação, câmera, onde entra o logo e o texto), as poses do mascote escolhidas e a ordem das etapas no Flow (imagem, depois vídeo). Esperar o ok; depois uma etapa por vez, conferida antes da próxima.

## Regras
- "Animação 3D" = CGI fotorrealista de comercial. A IA nunca escreve marca: logo e texto entram na edição.
- Formato: 9:16, 8 s de cena do Veo, uma cena contínua, câmera parada no Flow (o movimento de câmera sai na edição).
- Versões `-vN` (`nucleo.md`).

## 1. Preparar (Claude)
- **Mascote limpo:** `$A/mascotes/<podcast>/` (5 poses por podcast; O Aviário tem 8). Pôr em fundo branco e recortar: `"$PY" "$S/imagem.py" fundo <in> <out.png>`.
- **Folha do mascote** (o 2º elemento): corpo inteiro à esquerda, closes à direita.
  `"$PY" "$S/patrocinador_folha.py" <saida.png> <corpo.png> <arq:x0,y0,x1,y1> …`
  - Closes só do que a IA erra: o que termina os membros (patas, cascos, asas, pés) e o logo do peito. Para um gesto difícil (aceno), usar como corpo a pose com o gesto certo.
  - Nada de texto grande na folha: um patch PPGVET da manga num close virou "PPGVET" no peito. Recortar asa e pata só no que importa, sem manga com patch.
  - Objeto que não deve aparecer (capacete): escolher pose e recorte sem ele; a referência manda mais que o prompt.
- **Produto:** foto oficial recortada em fundo branco, em pé, rótulo de frente, alta resolução. Sem foto boa: molde 2 do prompts.md, e o Claude aplica a logo verdadeira.
- **Logos** em alta e transparentes: podcast em `$A/logos/podcasts/<podcast>/logo-<podcast>.png`.

## 2. Cenário (pessoa, Nano Banana Pro) → `ref-cenario.png`
Molde 1. Conferir: vazio, sem texto nem placa, lugar livre para mascote e produto lado a lado, âncora de escala, luz do clima pedido.

## 3. Vídeo (pessoa, Veo 3.1 Quality, 3 elementos) → `video-<patrocinador>-<podcast>-flow-vN.mp4`
Molde 4. Testar o prompt no Fast quando a cena for nova; a versão boa sai no Quality.

## 4. Conferir (Claude, a cada vídeo)
```bash
"$FF" -v error -i <video> -vf "fps=4,scale=270:-1,tile=8x4" -frames:v 1 folha-conferencia.jpg
```
(32 quadros = 8 s, um a cada 0,25 s.) Lista: membros certos em todo quadro (mão humana, dedo, luva, perna levantada) · logo do peito · texto inventado no traje · capacete ou objeto que não era para ter · rótulo do produto legível e sem nada na frente · olhar na direção pedida · boca parada · câmera parada · personagem ou objeto extra (closes da folha virando objeto) · escala · áudio sem música, voz ou bicho.
Erro pequeno num vídeo bom → Omni (molde 5). Erro de ação ou composição → ajustar o prompt e gerar de novo, anotando no roteiro o que mudou e por quê.

## Erros que já custaram geração (e a frase que resolveu)
| erro | correção |
|---|---|
| pata ou asa vira mão humana | close do membro na folha + nome que o modelo conhece ("pig trotters with cloven hooves", "white feathered wings") + "never hands, never fingers" no bloco e no gesto |
| "foot/front trotter" para a mão | levantou a perna; usar "raises his arm, lifting the sleeve… the trotter at the end of this arm" |
| "astronaut" sem capacete | ganhou domo de vidro; "a white hen wearing a white space suit… head bare… never any helmet, glass dome, bubble or visor" |
| texto no traje | "only the small patches shown in image 2, no large lettering anywhere on the suit" |
| mascote do tamanho do produto | âncora visível ("top of his head at the middle of the label"), "same distance from the camera, never closer" |
| aceno cobre o rótulo ou anda até o produto | acenar com o braço de fora; "a clear gap as wide as his own body"; "stays in the same spot" no fim |
| boca abre e fecha | não brigar com a referência: "the same smile as image 2, frozen, jaw never moves" |
| olhar perdido | dar a direção: "lowers his head toward the bag… eyes point down at it… never leaves it" |
| zoom ou pan inventado | "Static camera… locked off on a tripod…"; o movimento sai na edição |
| música, fala ou bicho no áudio | bloco Audio com a trilha inteira descrita + "no musical instruments, no melody, no voices and no animal sounds" |
| líquido vazando do frasco | "sealed vial… the liquid always remains inside… only ripples slightly" |
| logo pequena torta no produto | mascote nunca na frente do rótulo; se torcer, o Claude corrige na edição |
| casco vira mão no aceno (Omni) | anexo = close do casco + "Holstein hoof, 2 rigid toes, waves only from elbow and wrist, never a hand/glove/mitten/paw" |
| quadro final no Frames to Video | só acerta o fim, o meio deforma: não usar quadro final |
| vídeo do Veo tocado ao contrário | fica estranho no todo: nunca inverter |
| 2 vídeos emendados (mergulho + gesto) | gerar o 1º (mergulho no Ingredientes: quadro de partida + quadro do gesto), depois o gesto no Frames to Video a partir do último quadro dele: sem emenda. Emendar 2 cenas diferentes na edição (clarão, corte no voo, dissolvida) foi reprovado |
| trocar o produto depois de gerado | colar a foto na edição ficou com cara de colado (reprovado). Funcionou o Omni, um vídeo por vez: prompt com o tempo em que nada muda, o lugar e o produto descrito peça por peça, anexo = foto oficial; o 2º vídeo leva o último quadro do 1º |

## 5. Edição (Claude) → `<patrocinador>-<podcast>-boas-vindas-vN.mp4`
Padrão aprovado: cena com acabamento + leve aproximação e afastamento + cartela de 3,6 s + música e efeitos mínimos. ~11,6 s, 1080x1920, 24 fps, ~6 MB, -14 LUFS.

```bash
Q=<pasta de rascunho>; mkdir -p "$Q/q" && "$FF" -v error -i <flow.mp4> -q:v 1 "$Q/q/f%04d.png"
"$PY" "$S/patrocinador_acabamento.py" "$Q/q" "$Q/fx" <quadro-do-pouso ou 9999>
"$PY" "$S/patrocinador_final.py" "$Q/fx" "$Q/fin" "$A/fontes/montserrat-bold.ttf" <logo-podcast> <logo-patrocinador> 3.6 "<linha 1>" "<linha 2>" <INTRO> <POUSO> <M0> <M1> <cor1> <cor2>
```
- **Frase sempre** "Bem-vindos ao <Podcast>," / "<Patrocinador>!", no plural (mesmo se o pedido traz outra). O Aviário = "Bem-vindos ao Podcast O Aviário,"; SuinoCast = "Bem-vindos ao SuinoCast,"; +Rúmen = "Bem-vindos ao Mais Rúmen Podcast,"; PetFood: perguntar na 1ª vez. Cores da marca do patrocinador (linha 1 escura, nome na cor principal; hex sem `#`). Logo do podcast à esquerda, patrocinador à direita. Nome do patrocinador em cor clara: `VEU=0.88 FUNDO=F5F6F8` antes do comando.
- Câmera: INTRO 24 (1 s parado de suspense) só se a cena começa vazia; com o mascote já em cena, 0. Aproxima até o POUSO (ou o fim da ação principal), afasta de M0 (gesto final) a M1 (ele para). Exemplos: `0 100 156 192` (mascote já em cena) e `24 53 92 150` (cena começa vazia). Achar os quadros na folha de conferência.
- Sem queda: acabamento com 9999 (sem tranco). Não ampliar com Real-ESRGAN (vira plástico).

Encode e som (cena = (INTRO + nº de quadros)/24; T = cena + 3,6; as logos entram em cena + 1,05):
```bash
"$FF" -v error -y -framerate 24 -i "$Q/fin/q%04d.png" -i <flow.mp4> -i <musica.mp3> -i <pop.wav> [-i <impacto>] -filter_complex "
[0:v]noise=alls=3:allf=t,format=yuv420p[v];
[2:a]atrim=0:$T,asetpts=PTS-STARTPTS,volume='if(lt(t,<cena>),0.58,0.98)':eval=frame,afade=t=in:d=0.4,afade=t=out:st=<T-1.1>:d=1.08,volume=0.85,aformat=channel_layouts=stereo[mus];
[3:a]adelay=<ms das logos>|<ms>,volume=0.5,aformat=channel_layouts=stereo[logos];
[mus][logos]amix=inputs=2:normalize=0:duration=first,volume=1.5,alimiter=limit=0.76:attack=3:release=60:level=false[a]" \
 -map "[v]" -map "[a]" -t $T -c:v libx264 -preset slow -crf 20 -maxrate 12M -bufsize 24M -tune film -pix_fmt yuv420p \
 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -c:a aac -b:a 128k -movflags +faststart <saida-vN.mp4>
"$PY" "$S/checar.py" <saida-vN.mp4> --lufs -14 --instagram
```
- Som do Veo nunca entra (ambiente estranho). Música fixa na cena e sobe na cartela (`video.md`). Queda: whoosh com pico no pouso (`$A/sons/transicao/whoosh-longo.wav`; o pico dá `"$PY" "$S/sons.py" pico <som>`) + o impacto do produto (vidro, saco de grãos: gravação real, regra de sons do `bancos-e-referencias.md`). Na cartela, um pop nas logos (`$A/sons/interface/pop.wav`). Nada mais. Como sincronizar: `oficio/som.md`.
- Cada vídeo com identidade própria: não repetir a trilha do vídeo anterior (ver o roteiro dele); música pela regra do `bancos-e-referencias.md`. Anotar trilha e efeitos no roteiro.

Entregar a versão e esperar a pessoa conferir.
