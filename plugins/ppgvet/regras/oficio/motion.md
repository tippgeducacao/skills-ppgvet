# Ofício: motion (texto, cartão, abertura)

Lido quando a peça tem motion, no nível padrão e no caprichado. As regras fixas da casa (HyperFrames, roteiro no plano, rosto livre) ficam no `video.md`. Fonte: [O] doc oficial, [L] livro clássico, [T] técnica tirada de prompts profissionais de terceiro, [N] proposta da casa.

## Princípios (Disney, aplicados a texto e interface) [L]
- Antecipação: 2 a 4 quadros no sentido contrário antes do movimento.
- Um herói por momento; o resto fica quieto ou escurece.
- Continuidade: as partes chegam em tempos diferentes (título, depois subtítulo, depois ícone).
- Nunca linear: acelera e desacelera. Objeto anda em arco.
- Ação secundária: o brilho que passa depois que o título assentou.
- Exagero contido: overshoot de escala de 110% para 100%.

## Curvas e durações
| uso | curva | duração |
|---|---|---|
| entrada importante | `cubic-bezier(0.05, 0.7, 0.1, 1)` | 400 a 500 ms [O Material 3] |
| saída (mais curta que a entrada) | `cubic-bezier(0.3, 0, 0.8, 0.15)` | 200 a 250 ms [O Material 3, NN/g] |
| mudança na tela | `cubic-bezier(0.2, 0, 0, 1)` | 250 a 400 ms [O Material 3] |
| palavra de texto em vídeo | expo-out; sobe 0,4 a 0,6 em e desfoca de 8 a 22 px até 0 | ~0,9 s, intervalo de 30 a 90 ms entre palavras [T] |
| mola de "pop" (chip, botão) | frequência 2,0 a 2,6 Hz, amortecimento 0,38 a 0,5 | — [T] |
| mola de objeto pesado | 0,9 a 1,2 Hz, amortecimento 0,55 a 0,8 | — [T] |

Vídeo pode ser um pouco mais lento que interface (é lido, não clicado), mas o erro comum é longo demais, não curto [O NN/g]. Linear só em deriva contínua.

## Coreografia
- Ordem de leitura = ordem de entrada (de cima para baixo, da esquerda para a direita).
- Entradas escalonadas e curtas (≤ ~0,5 s no total); saídas juntas e rápidas [O NN/g, T].
- A próxima cena continua a direção do movimento da anterior [T].

## Texto animado
- Entra no exato momento da palavra falada (tempo do whisper) [T].
- O que é falado não se escreve de novo na tela como frase inteira: na tela vai a palavra-chave, o número, o nome [T].
- Tem de ser lido no celular em 1 s; se não for, cortar palavras [T].
- Variar a entrada pelo sentido e nunca repetir a mesma duas vezes seguidas: subida com desfoque, letra que bate (1,7 para 1 com desfoque), número em odômetro, contorno que se desenha e depois preenche, wipe com borda de luz [T].

## Logo e abertura
- Constrói, trava e fica parada ≥ 1,5 s para ler [N]; o impacto do som cai no quadro da trava [T].

## Só no nível caprichado [T]
- Tabela de batidas antes de construir: tempo, fala, um herói, texto.
- Quadros-chave aprovados antes de animar: um por cena, numa folha rotulada.
- "Nada morto": deriva leve, câmera que empurra devagar, grão animado. Em fala de professor, câmera parada e motion só quando a fala pede.
- Estilo "premium" (vidro, brilho, partículas) só com as cores da marca e com motivo.

Fontes: Thomas & Johnston, *The Illusion of Life*; [Material 3, tokens de movimento](https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-motion.scss); [NN/g, duração de animação](https://www.nngroup.com/articles/animation-duration/); prompts de motion de terceiro (Zane Hoyer, Google Docs), só a técnica. Conferido em 24/11/2026.
