# Ofício: edição de vídeo

Lido no nível padrão e no caprichado (`nucleo.md`, nível de esforço). As regras fixas da casa (corte na palavra, cor HDR, volume, Instagram) ficam no `video.md`; aqui está como um editor profissional decide. Fonte: [O] norma ou doc oficial, [L] livro clássico, [P] prática profissional publicada, [N] proposta da casa, a calibrar no primeiro lote.

## Decidir o corte
- Todo corte tem motivo: informação nova, reação ou ritmo. Sem motivo, não corta [L].
- Prioridade de Murch: emoção > história > ritmo > direção do olhar > plano da tela > espaço 3D. Quando um corte não atende a todos, abre mão de trás para frente [L].
- Corta onde o pensamento muda (fim de ideia, onde a pessoa piscaria), nunca por tempo fixo nem só porque houve silêncio [L].
- Corte na ação: o gesto começa num plano e termina no outro [P].
- Respiro: depois de uma frase forte, ~0,3 a 0,6 s antes do próximo corte; tirar todas as pausas deixa a fala "metralhadora" [N].
- Room tone: no jump cut, o fundo do som continua entre as falas; se a limpeza de voz zerou o fundo, os cortes ficam audíveis [P].

## Tipos de corte
| corte | quando | erro típico |
|---|---|---|
| seco | quase sempre | — |
| J (o som do próximo plano entra antes da imagem) | puxar para a próxima ideia, entrar em b-roll ou numa pergunta da plateia | adiantar mais de 1 s: a voz "sai do corpo" |
| L (a imagem muda, o som continua) | b-roll sobre a fala, mostrar quem ouve | b-roll sem relação com a fala |
| jump cut | fala de Reels, assumido como estilo | pulo pequeno no mesmo enquadramento parece erro: mudar a escala (punch-in) ou tirar mais |
| match cut | abertura de marca, virada de ideia | forçar formas que não casam |
| cutaway | mostrar o animal, o laudo, o software citado | cutaway genérico ("pessoa digitando") |
| smash cut | humor, virada de gancho | em fala séria de professor |

## B-roll
- Ilustra a palavra dita (laudo quando fala de laudo), não enfeita. Entra em L-cut e fica de 2 a 4 s [P].
- Foto parada: empurrão leve de 1,00 a 1,05; nunca o mesmo movimento em todas [N].

## Transições
| usar | quando | evitar |
|---|---|---|
| corte seco | quase sempre | star wipe, page curl, cubo 3D, spin |
| dissolve de 8 a 15 quadros | passagem de tempo, foto para foto | dissolve entre planos sem relação |
| dip para preto ou branco | fim de bloco, abertura, encerramento | glitch, RGB split, film burn sem motivo |
| zoom-blur de ~0,2 s | Reels energético, troca de seção | em todo corte |

A transição é escolhida pelo sentido (o tempo passou, a seção mudou), nunca para enfeitar.

## Zoom e punch-in
- Esconde o jump cut e marca a ênfase. Seco, ou com rampa expo de 0,25 a 0,4 s; nunca pulsando [N].
- Limite de nitidez: escala ≤ resolução da fonte ÷ resolução da saída (4K para 1080: até 2x; 1080 para 1080: ~1,1x).

## Legenda
| item | limite |
|---|---|
| caracteres por linha | ≤ 25 no 9:16; ≤ 42 no 16:9 [O BBC, Netflix pt-BR] |
| linhas | ≤ 2 (Reels: 1) |
| velocidade de leitura | ≤ 17 caracteres por segundo [O Netflix pt-BR] |
| tempo mínimo na tela | ~0,3 s por palavra [O BBC] |
| corte de plano | a legenda não atravessa o corte [O BBC] |
| quebra de linha | depois de pontuação; não separar artigo do nome, nome do sobrenome, verbo do auxiliar [O Netflix pt-BR] |
| números | de 1 a 10 por extenso, acima em algarismo [O Netflix pt-BR] |
| destaque | 1 palavra por legenda, na cor de destaque da marca; sem emoji |

## Reels de fala
- 0 a 3 s: gancho, com a mensagem e a marca já na tela; tem de funcionar no mudo [O Meta].
- Corpo: uma ideia por plano. Fim: CTA claro e o encerramento da marca.

## Cor
1. Converter o espaço de cor (HDR para BT.709; filtro no `video.md`).
2. Exposição e contraste.
3. Balanço de branco, pela pele.
4. Saturação.
5. Correção de área (pele, céu), separada.
6. Look ou LUT por último.

- Primeiro deixar certo (correção), depois dar intenção (look) [P].
- Pele de qualquer etnia cai perto da mesma linha de matiz no vetorscópio; o que muda entre peles é o brilho. Em pele, matiz e saturação pesam mais que o brilho [P].
- LUT criativa só sobre imagem já corrigida; nunca duas conversões técnicas seguidas.

Fontes: Walter Murch, *In the Blink of an Eye*; [Netflix pt-BR Timed Text](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215600497-Brazilian-Portuguese-Timed-Text-Style-Guide); [BBC Subtitle Guidelines](https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/); [Meta, Tailored Campaigns](https://www.facebook.com/business/ads/automation/tailored-campaigns); Frame.io Insider ([nós de cor](https://blog.frame.io/2024/04/01/new-resolve-template-node-graphs-color-grading/), [linha de pele](https://blog.frame.io/2023/09/18/when-to-use-color-scopes-and-when-not-to/)). Conferido em 24/11/2026.
