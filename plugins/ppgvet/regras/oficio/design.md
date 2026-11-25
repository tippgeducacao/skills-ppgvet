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

## Formatos do `arte.py`
Tamanho e limite oficial de cada canal: `formatos.md`. Aqui, só a área livre da casa. Toda peça sai em PNG e em JPEG sRGB (o JPEG é o que vai para o Instagram).

| formato (`arte.py --formato`) | tamanho | área livre (sem texto nem logo) e nota |
|---|---|---|
| `feed`, `carrossel` | 1080x1350 (4:5) | 64 px em volta. A grade do perfil mostra 3:4: essencial no centro. Carrossel: todos na proporção do primeiro |
| `anuncio` | desenha 1080x1350, sai 1440x1800 (recomendado da Meta) | 64 px em volta; o texto longo vai no campo do anúncio |
| `quadrado` | 1080x1080 | 64 px em volta |
| `story`, `story-anuncio`, `capa-reels` | 1080x1920 (o `story-anuncio` sai 1440x2560) | as margens do 9:16 do `video.md`; anúncio: a área livre do `formatos.md` (o `arte.py` mede) |
| `shorts` (thumb) | desenha 1080x1920, sai 2160x3840 | as do story |
| `podcast` (capa) | desenha 1500x1500, sai 3000x3000, sem transparência | 96 px em volta; só o nome do podcast [O] |
| `youtube` (thumb) | desenha 1920x1080, sai 3840x2160 | 96 px dos lados, 64 em cima e embaixo; nada no canto de baixo à direita (a duração cobre) |
| `email` (banner) | desenha 600x650, sai em dobro | 32 px em volta [N] |
| `portal`, `portal-quadrado` (capa do portal do aluno, Eduq) | 1080x1920 e 1000x1000 | um par por bloco ("ABERTURA", "MÓDULO I"…) [N] |

## O que os nossos perfis ensinam (estudo de 24/11/2026: 100 posts e as artes dos designers da casa)
- **Foto e vídeo real vencem:** Reels de campo alcançaram 34 a 50 mil (mediana 2,9 mil); carrossel só com fotos da turma, 28,8 mil. O pior: arte só de texto com foto de banco. Pessoa e lugar de verdade sempre que houver.
- **Molde da casa:** os moldes de `acervo/moldes` (abaixo) já trazem o padrão: logo, margem, 3 níveis em Montserrat, bloco "PÓS │ GRADUAÇÃO │ nome", professor recortado, titulação pela regra do `sempre.md`.
- **Cor:** só os códigos do `marca.md` (as artes antigas derivaram: magenta `#B8569A`/`#CE5A9B`, teal `#00A19C`, azul PPG `#005EF2`; não copiar). Teal e magenta de acento: letra branca sobre o teal `#00B7AB` dá 2,6:1 e sobre o magenta 3,95:1, reprovado para letra pequena; texto em cima vai na caixa escura `#1A1A1A`.
- **Tamanho no celular:** a peça de 1080 px aparece com ~390 pt de largura (×0,36). Letra abaixo de ~52 px em negrito (ou ~64 px normal) é pequena no celular: contraste de 4,5:1.
- **Texto:** regras de texto em `oficio/copy.md`; titulação e "nunca MBA" no `sempre.md`; marcas e exceções no `marca.md`. Na arte: data sem crase ("23 a 25"), dia da semana tirado da data.
- **Carrossel:** mesmo grid em todas as lâminas; 1ª = gancho ou capa que muda a cada edição (capa igual toda semana não dá novidade), meio = uma ideia por lâmina, última = chamada; "ARRASTA PARA O LADO" no rodapé, no mesmo lugar.

## Moldes da casa (`acervo/moldes`, gerados pelo `scripts/molde.py`)
Peça que cabe num molde sai do molde: mesmo sistema em toda a equipe, menos tempo e menos tokens. HTML livre só para o que não cabe (e com a direção do `antislop-midia.md`).

| molde | quando | formato |
|---|---|---|
| `kv` | peça-conceito da pós, lançamento, anúncio de imagem: foto real em cima, gancho em peso misto, rótulo na cor da pós | `feed` ou `anuncio` |
| `professor` | entrada de professor, criativo de professor, anúncio: retrato real, nome com titulação comprovada, cargo e empresa | `feed` ou `anuncio` |
| `carrossel-capa`, `-conteudo`, `-cta` | carrossel: tese sobre foto, uma ideia por lâmina (foto opcional), uma ação no fim em tom invertido | `carrossel` |
| `story` | aviso de aula, live ou evento: data na cor da pós, foto de fundo | `story` ou `story-anuncio` |
| `thumb` | YouTube e podcast: rosto real, 3 a 6 palavras gigantes | `youtube` |
| `capa-portal` | capa do portal do aluno, um par por bloco | `portal` e `portal-quadrado` |

- **Sistema:** PPGVET em fundo claro `#FAF9FB` (Jaleco Branco), PPG em fundo escuro `#1A1A1A` (Terno Escuro); peça com foto de fundo usa véu escuro e letra branca nas duas. Cor da pós no fio do bloco e na faixa do rótulo; no nome da pós só quando lê (o `molde.py` mede). Destaque do título (`[colchetes]`) na cor da marca, só em letra grande.
- **Anúncio (patrocinado):** `kv` ou `professor` em `anuncio` e `story` em `story-anuncio`, até 8 variações mudando só o gancho e a foto (o resto fica, para comparar).

## O que denuncia cara de IA ou de template
Dono: `antislop-midia.md` ("Recusar", linhas "tudo" e "arte").

Fontes: Müller-Brockmann, *Grid Systems in Graphic Design*; Bringhurst, *The Elements of Typographic Style*; Albers, *Interaction of Color*; [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Conferido em 24/11/2026.
