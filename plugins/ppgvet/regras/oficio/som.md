# Ofício: som

Lido quando há mixagem além de voz e música (efeitos, ambiente, limpeza), no nível padrão e no caprichado. Os números fixos da casa (voz -16 LUFS, fundo de cada tipo de vídeo) ficam no `video.md`. Fonte: [O] norma, [P] prática profissional, [T] técnica de prompt profissional de terceiro, [N] proposta da casa.

## Camadas
| camada | papel |
|---|---|
| voz | manda em tudo |
| música | clima; nunca compete com a voz |
| ambiente (room tone) | cola os cortes; contínuo e baixo [P] |
| efeito sonoro | dá peso ao movimento; baixo, e o mais forte só no momento mais importante [T] |

## Efeito sincronizado com a imagem
- Alinhar o pico do som (a parte que importa), não o começo do arquivo [T].
- Clique no quadro em que o botão afunda; impacto onde o movimento para; o whoosh cresce na parte mais rápida e o pico cai no corte [T].
- O ouvido aceita som atrasado melhor que adiantado: percebe a partir de +45 ms adiantado e -125 ms atrasado. Na dúvida, 1 quadro depois, nunca antes [O ITU-R BT.1359].
- Um gesto = um som: vários elementos que entram juntos levam um som só [T].
- Efeito que cobre uma palavra: baixar, encurtar ou tirar o efeito, nunca baixar a voz [T].
- Teste do mudo: sem os efeitos, o movimento perde peso; com eles, percebe-se mais o movimento que o som [T].

## Ducking
- Padrão da casa: música fixa e baixa sob a voz (`video.md`), mais natural para fala contínua.
- Ducking por sidechain (música sobe nas pausas) só quando pedirem: ataque curto, liberação lenta (centenas de ms), redução de 6 a 12 dB; conferir que não "bombeia" [P, N].

## Medir sem ouvir
| o quê | como | alvo |
|---|---|---|
| volume e pico real | `"$FF" -i x -af ebur128=peak=true -f null -` | voz -16 LUFS; pico ≤ -1,5 dBTP |
| variação | o mesmo `ebur128` (LRA) | fala de 4 a 10 LU |
| clipping | `astats=measure_overall=Peak_level+Peak_count` | pico < -0,1 dBFS |
| zumbido | espectro com pico isolado em 60, 120, 180 Hz (rede elétrica do Brasil) | nenhum |
| ver o som | `showspectrumpic=s=1200x400` (~650 tokens) | — |
| inteligível | transcrever de novo e comparar com o roteiro | quase nenhuma palavra trocada |

Comparar versões sempre no mesmo volume: mais alto engana como "melhor" [T].

## Erros típicos
Música alta ou com vocal; whoosh em todo corte; efeito maior que a ação; dois sons no mesmo gesto; cauda cortada seca; clipping; um canal mudo; room tone que some no corte.

Fontes: [ITU-R BT.1359 e EBU R37](https://en.wikipedia.org/wiki/Audio-to-video_synchronization) (resumo); EBU R128; [AES TD1008](https://aes.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf); prompt de sound design de terceiro (Zane Hoyer), só a técnica. Conferido em 24/11/2026.
