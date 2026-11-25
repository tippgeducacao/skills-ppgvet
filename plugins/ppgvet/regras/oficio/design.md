# Ofício: design (arte estática, cartões, carrossel)

Lido quando a peça tem arte, cartão ou carrossel, no nível padrão e no caprichado. Cores, fonte (só Montserrat) e frases: `marca.md`. Fonte: [O] norma, [L] livro clássico, [N] proposta da casa.

## Design com intenção
| princípio | o que faz o profissional |
|---|---|
| objetivo | uma peça, uma ação (ler, clicar, salvar) [L Müller-Brockmann] |
| hierarquia | até 3 níveis (título, apoio, detalhe), por tamanho e peso, não por cor [L Bringhurst] |
| grid | colunas e margens fixas; tudo alinha a alguma coisa [L Müller-Brockmann] |
| tipografia | Montserrat em 2 ou 3 pesos; texto corrido de 45 a 75 caracteres por linha [L Bringhurst] |
| contraste | texto 4,5:1; texto grande 3:1 [O WCAG 1.4.3]. "Grande" no WCAG é ≥ 24 px (≥ 18,66 px em negrito) **na tela**: na peça de 1080 px, ver "Tamanho no celular" abaixo |
| cor | a cor muda com a vizinha: testar no fundo real, não na amostra [L Albers]. Marca como acento, neutros na maior parte |
| espaço vazio | dá peso ao que importa; não encher os cantos [L] |

## Usar referência
1. Juntar de 5 a 10 referências do mesmo tipo de peça (como buscar: `bancos-e-referencias.md`).
2. Anotar em cada uma: grid, hierarquia, tipografia, proporção de cor, ritmo e o que a faz parecer cara.
3. Tirar 3 princípios e desenhar do zero com a nossa marca. Copiar o como, nunca o conteúdo, a logo ou o layout.
4. Comparar lado a lado, no mesmo tamanho, no celular.

## Instagram (conferir na doc da Meta na hora: muda)
| formato (`arte.py --formato`) | tamanho | área livre (sem texto nem logo) e nota |
|---|---|---|
| `feed`, `carrossel` | 1080x1350 (4:5) | 64 px em volta. O app aceita até 3:4, mas a API (agendador do sistema) só até 4:5. A grade do perfil mostra 3:4: essencial no centro. Carrossel: todos na proporção do primeiro |
| `quadrado` | 1080x1080 | 64 px em volta |
| `story`, `story-anuncio` | 1080x1920 | as margens do 9:16 do `video.md` (o `arte.py` mede) |
| `youtube` (thumb) | desenha 1920x1080, sai 3840x2160 | 96 px dos lados, 64 em cima e embaixo; nada no canto de baixo à direita (a duração cobre). 16:9, mínimo de 640 de largura ([O] [YouTube](https://support.google.com/youtube/answer/72431)) |
| `email` (banner) | desenha 600x650, sai em dobro | 32 px em volta [N] |

## O que os nossos perfis ensinam (estudo de 24/11/2026: 100 posts e as artes dos designers da casa)
- **Foto e vídeo real vencem:** Reels de campo alcançaram 34 a 50 mil (mediana 2,9 mil); carrossel só com fotos da turma, 28,8 mil. O pior: arte só de texto com foto de banco. Pessoa e lugar de verdade sempre que houver.
- **Molde da casa:** fundo claro `#FAF9FB` (grade leve), logo no topo ao centro, margem de ~10%, até 3 níveis de texto em Montserrat (título Black em caixa alta, apoio Bold, detalhe), bloco "PÓS-GRADUAÇÃO │ nome" (`acervo/titulos-pos`), professor em cartão ou recortado, com a titulação pela regra do `sempre.md`.
- **Cor:** só os códigos do `marca.md` (as artes antigas derivaram: magenta `#B8569A`/`#CE5A9B`, teal `#00A19C`, azul PPG `#005EF2`; não copiar). Teal e magenta de acento: letra branca sobre o teal `#00B7AB` dá 2,6:1 e sobre o magenta 3,95:1, reprovado para letra pequena; texto em cima vai na caixa escura `#1A1A1A`.
- **Tamanho no celular:** a peça de 1080 px aparece com ~390 pt de largura (×0,36). Letra abaixo de ~52 px em negrito (ou ~64 px normal) é pequena no celular: contraste de 4,5:1.
- **Texto:** regras de texto em `oficio/copy.md`; titulação e "nunca MBA" no `sempre.md`; marcas e exceções no `marca.md`. Na arte: data sem crase ("23 a 25"), dia da semana tirado da data.
- **Carrossel:** mesmo grid em todas as lâminas; 1ª = gancho ou capa que muda a cada edição (capa igual toda semana não dá novidade), meio = uma ideia por lâmina, última = chamada; "ARRASTA PARA O LADO" no rodapé, no mesmo lugar.

## O que denuncia cara de IA ou de template
Os sinais gerais (cards iguais, neon, vidro fosco, banco ou IA fingindo pessoa) estão no `antislop-midia.md`. Da arte parada:
- Bolhas 3D genéricas, brilho e sombra borrada grande.
- Mais de uma família de fonte, pesos aleatórios, texto longo em arte de feed.
- Mockup genérico, ícone decorativo sem função, emoji na arte.
- Imagem de IA fingindo cena (bicho de camisa, porco astronauta), interface falsa (card de Threads, app Notas).

Fontes: Müller-Brockmann, *Grid Systems in Graphic Design*; Bringhurst, *The Elements of Typographic Style*; Albers, *Interaction of Color*; [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Conferido em 24/11/2026.
