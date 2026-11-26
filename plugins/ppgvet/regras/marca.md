# Marca (vídeo, arte e texto)

Adaptado do guia de marca da PPGVET para vídeo, arte e texto (o guia é o dono; mudou lá, muda aqui). Dono, no pacote, de: marcas e exceções, peças do acervo, cores, pós e as regras de texto da marca; as skills e o `oficio/` só apontam.

## Duas marcas, nunca misturadas
- **PPGVET** (veterinária) e **PPG Educação** (gestão e cooperativismo). Peça da PPG leva a marca da PPG (logo, azul, encerramento); peça da PPGVET, a da PPGVET. O que é da PPGVET (evento, vaga, podcast) é peça da PPGVET.
- **Exceções (decisão do usuário):** live (vMix e moldura do Instagram) e chamada saem sempre com a marca PPGVET, também nas pós da PPG; a aula curricular abre com a intro PPGVET e o card diz "Professor(a) do Grupo PPG Educação"; a moldura de intro de aula leva as duas marcas.
- **Capas da Eduq** (portal do aluno, do Grupo PPG): logo PPG Educação em todas, inclusive nas pós da PPGVET; o visual é o do PSD da equipe (`acervo/eduq/modelos`, preenchido pelo `scripts/eduq.py`); nas pós da PPG, fundo `#0080F6` e pílula `#047FEF` no lugar do verde (sRGB, conferidos pixel a pixel na capa publicada de Crédito Rural em 25/11/2026; com a textura do PSD a pílula sai como a da equipe); no plano B (sem o Photopea) a capa principal usa as peças fixas tiradas do mesmo PSD (`acervo/eduq`), com a mesma pílula.
- Os podcasts (SuinoCast, O Aviário, +Rúmen e PetFood) são da PPGVET. A PPG não tem podcast de veterinária.

## Peças do pacote (pasta `acervo/`, nos roteiros `acervo:<caminho>`)
| peça | arquivo | quando usar |
|---|---|---|
| logo PPGVET | `logos/ppgvet/logo-ppgvet.png` (fundo escuro: `-branco`; deitada: `-horizontal`, `-horizontal-branco`) | logo embaixo do vídeo, cartão de perfil |
| ícone PPGVET | `logos/ppgvet/ppgvet-icon-180.png` (também `-64` e `.svg`) | ícone da caixinha de pergunta, avatar |
| logo PPG Educação | `logos/ppg/logo-ppg-educacao.png` (fundo escuro: `-branco`) | vídeo da marca PPG |
| ícone PPG | `logos/ppg/icone-ppg.png` (fundo escuro: `-branco`) | ícone da caixinha em vídeo PPG |
| podcasts | `logos/podcasts/<suinocast, oaviario, maisrumen, petfood>/`: `logo-<podcast>.png`, `logo-<podcast>-mono.png`, `icone-<podcast>.png` (e as variações `-branco`, `-vazado`, `-balao`) | vídeo, corte ou chamada de episódio do podcast |
| encerramento PPGVET | `logos-animadas/encerramento-ppgvet-vertical.mp4` (1080x1920, 6 s, "Mais que uma formação, uma transformação!") | fim de vídeo vertical PPGVET. Com música, o som da logo sai |
| encerramento PPG (logo 3D PPG) | `logos-animadas/encerramento-ppg-vertical.mp4` (1080x1920, 6 s) | fim de vídeo vertical PPG |
| logo 3D PPGVET | `logos-animadas/logo-ppgvet-horizontal.mp4` (1920x1080, 15 s, mudo) | abertura e fim de vídeo horizontal |
| logo 3D PPG | `logos-animadas/logo-ppg-horizontal.mp4` (1920x1080, 15 s, mudo) | abertura e fim de vídeo horizontal da PPG |
| abertura de aula | `intro/PPGVET.mov` (10,7 s, com slogan) | toda aula curricular, mesmo de pós da PPG |
| molduras das pós | `molduras-aula/<AVES, BOVINOS, PADRÃO, PETFOOD, QUALIDADE, SUÍNOS>.png` | aula curricular (qual moldura de cada pós: tabela abaixo) |
| moldura do post de corte | `molduras/moldura-post-corte-ppgvet.png` e `-ppg.png` (1080x1920: avatar, nome e @ do Instagram; o `post.py` escreve pós e título por cima) | posts da `cortes-live` (`"marca"` no `post.json`) |
| moldura de intro de aula | `molduras/moldura-aula-ppgvet-ppg-16x9.png` (o vídeo entra no retângulo azul x 241..1678, y 134..944) | intro de aula com as duas marcas; treinamento do Academy só com câmera |
| moldura do Academy com tela | `molduras-aula/PADRÃO.png` (tela grande à esquerda, câmera à direita) | treinamento do Academy com tela compartilhada |
| card do professor | `card-professor/card-sem-nome.png` | base do card gerado na hora na aula curricular |
| fotos dos professores | `professores/<nome-sobrenome>.webp` (só quem está nos sites; recorte em fundo branco 1920x1080 ou retrato do site). Dono: este acervo; originais em alta em `~/conhecimento/professores/fotos` (só nesta máquina) | aulas da semana, live, arte e chamada, quando a pessoa não manda a foto |
| títulos das pós | `titulos-pos/titulo-pos-<sigla>.png` (cinza e magenta, 4x) e `-branco.png`; gerados por `scripts/live_titulos.py` | live, arte, qualquer peça com o nome da pós |
| peças da live | `live/`: `titulos-overlay/titulo-live-<sigla>.png` (vMix, topo), `moldura-insta.html` (modelo) e `moldura-insta-exemplo.png`, `qr-live.html`, `molduras-vmix/` (uma pessoa, duas pessoas, slides) | skill `live-vmix` |
| efeitos sonoros | `sons/<interface, transicao, impacto, foley>/<nome>.wav`; origem e licença em `sons/ORIGEM.md` | qualquer vídeo com sound design (`regras/oficio/som.md`) |
| mascotes dos podcasts | `mascotes/<suinocast, oaviario, maisrumen, petfood>/mascote-<podcast>-<pose>.webp` | skill `patrocinador-podcast` |
| fontes | `fontes/`: Montserrat (tudo), Lexend Exa e Artegra Sans (só o card do professor da aula curricular: exceção à regra "só Montserrat", com licença confirmada pelo usuário) | os scripts já usam |

| marca | principal | ação | destaque na legenda (só vídeo) |
|---|---|---|---|
| PPGVET | magenta `#D24BA8` | teal `#00B7AB` | rosa `#E371C0` |
| PPG | azul `#1670C2` | teal `#00ADA3` | teal `#00ADA3` |

Neutros: fundo claro `#FAF9FB`, texto e caixa escura `#1A1A1A`, branco `#FFFFFF`. A paleta da arte é a soma dos códigos deste arquivo (o `scripts/arte.py` reprova qualquer outro).

Tom de faixa com letra branca pequena: `#B84482` (o magenta oficial com letra branca dá 3,95:1 e reprova; usado na faixa "ESTAMOS AO VIVO" da moldura do Instagram da live).

## Pós (sigla, nome e moldura da aula curricular)
| sigla | nome | marca | moldura | cor | busca (vai na legenda) |
|---|---|---|---|---|---|
| RNGB | Reprodução, Nutrição e Gestão de Bovinos | PPGVET | BOVINOS | `#580B55` | reprodução bovina |
| NGB | Nutrição e Gestão de Bovinos | PPGVET | BOVINOS | `#00BEA0` | nutrição animal, nutrição de bovinos |
| CMCB | Clínica Médica e Cirúrgica de Bovinos | PPGVET | BOVINOS | `#016752` | buiatria, clínica de bovinos |
| GPL | Gestão na Pecuária Leiteira | PPGVET | BOVINOS | `#6E5A22` | pecuária leiteira |
| SA | Sanidade Avícola | PPGVET | AVES | `#F94C56` | avicultura, sanidade avícola |
| PC | Postura Comercial | PPGVET | AVES | `#DA4C00` | avicultura de postura |
| PS | Produção de Suínos | PPGVET | SUÍNOS | `#974D8A` | suinocultura, produção de suínos |
| CBEA | Comportamento e Bem-Estar Animal | PPGVET | PETFOOD | `#026E66` | comportamento animal, bem-estar animal |
| CMMV | Cannabis Medicinal na Medicina Veterinária | PPGVET | PETFOOD | `#41A514` | cannabis veterinária, canabidiol veterinária |
| QSAOA | Qualidade e Segurança de Alimentos de Origem Animal | PPGVET | QUALIDADE | `#086ED4` | inspeção de produtos de origem animal |
| SUZ | Saúde Única e Zoonoses | PPGVET | QUALIDADE | `#004F5A` | saúde única, one health |
| GPERA | Gestão de Pessoas e Extensão Rural na Agroindústria | PPGVET | PADRÃO | `#3C8246` | extensão rural |
| PPT | Piscicultura e Produção de Tilápia | PPGVET | perguntar | `#0EA5E9` | — |
| MIFV | Medicina Integrativa e Fitoterapia Veterinária com Ênfase em Cães e Gatos | PPGVET | perguntar | `#B05CE6` | medicina integrativa veterinária, fitoterapia veterinária |
| GIA | Gestão da Indústria de Alimentos Ênfase em Tecnologia e Inteligência Artificial | PPGVET | perguntar | `#E16E32` | — |
| MVA | Marketing e Vendas no Agronegócio | PPGVET | perguntar | `#E0287D` | — |
| GCC | Gestão de Cooperativas de Crédito | PPG | PADRÃO | `#1E3A8A` | cooperativas de crédito, cooperativismo |
| CRCV | Crédito Rural, Cooperativismo e Vendas | PPG | PADRÃO | `#FB6D2D` | crédito rural |
| GPDCA | Gestão de Pessoas e Desenvolvimento de Carreira no Agronegócio | PPG | perguntar | `#4F46E5` | — |

A busca é o termo que o profissional digita (pesquisa de palavras-chave de nov/2026; "—" sem medida): entra na legenda, nunca só na hashtag. A coluna moldura é a tabela `MOLDURA` do `scripts/aula.py` (o script é quem manda). Sigla fora dela: perguntar qual moldura usar.
A cor (código exato, do guia de marca) é detalhe da pós: uma cor de pós por peça, e a cor da marca continua a principal. **Letra em cima de qualquer cor** (da pós ou da marca): branca ou `#1A1A1A`, a de mais contraste; letra pequena no celular pede 4,5:1, grande 3:1 (o que é "grande" na peça de 1080 px: `oficio/design.md`). Sem a medida, a cor não leva texto.

## Texto

### Público e dor (o foco do texto de cada pós)
Público: 23 a 45 anos, já formado e trabalhando, que descobriu a lacuna na prática. Dor-mãe: "a graduação não me preparou para o que o mercado cobra hoje". Escrever a dor em cena concreta e mostrar que a pós resolve pela prática.

| sigla | dor | o que queremos que ele alcance |
|---|---|---|
| CMCB | medo de chegar na fazenda e não saber operar; perde o cliente para quem faz | segurança para executar a cirurgia e a clínica no campo |
| NGB | nunca formulou dieta em software; recebe o laudo e não sabe usar (nutrição = até 50% do custo) | formular e gerir a nutrição com números |
| RNGB | domina uma área e trava quando o produtor pergunta das outras | ser o profissional completo de reprodução, nutrição e gestão |
| PS | entrou na indústria sem nunca ter pisado numa granja; não sabe liderar a equipe | dominar a granja, a reprodução e a equipe |
| SA | uma disciplina de avicultura na faculdade; desgaste com o integrado; teto em 1 ou 2 anos | crescer na sanidade avícola e na conversa com o produtor |
| PC | decide por intuição; não lê curva de postura; mercado virando cage-free | decidir por técnica na cadeia do ovo |
| QSAOA | nunca fez PAC nem APPCC do zero; o RT é quem responde; metade quer concurso | estar preparado de verdade (e somar título no concurso) |
| SUZ | setor público; quer ponto na prova de títulos e o que o edital cobra | visão de saúde única que o cargo exige |
| CBEA | trata o sintoma sem entender o animal; fica fora de auditoria e certificação | ler o comportamento e entrar no mercado de bem-estar |
| CMMV | clínica de pequenos saturada (consulta de R$ 70 a 150, 88% já pensaram em largar) | uma área nova e bem paga, com respaldo da RDC 936/2024 |
| GPERA | tem a técnica e não convence o produtor; lidera sem ter aprendido | liderar pessoas e levar o produtor a mudar |
| GCC / CRCV | PPG: governança que trava, indicador que ninguém lê, conversa com o cooperado. PPGVET: técnico que bateu no teto e quer entrar no cooperativismo | decidir e crescer dentro do sistema cooperativo |
| GPL, PPT, MIFV, GIA, GPDCA, MVA | sem pesquisa de público: perguntar antes de escrever | — |

### Tom (a vibe, não o visual)
Fonte: vídeo manifesto da PPGVET. Falamos como líder do mercado: somos os maiores e os melhores, e dizemos isso com o número do lado. O inimigo é o modelo tradicional: professor que fala, aluno que anota, tudo para a prova. A profissão cobra na hora, no curral, na granja, na mesa do cooperado, com alguém esperando a sua resposta. **Slogan oficial: "Nossa bandeira é a prática"** (sempre assim). Vai em lugares fixos (rodapé, quadro "sobre" do blog, `slogan` no schema), nunca repetido no texto para SEO.

| | família | cena que resume | o visitante pensa |
|---|---|---|---|
| PPGVET | Jaleco Branco: página limpa, com a bota suja dentro (foto de curral, granja, aula no campo) | professor com a mão no animal, a turma em volta | "esse pessoal faz o que eu vou ter que fazer amanhã" |
| PPG | Terno Escuro: página escura, números, gente decidindo | gestor mostrando o indicador ao conselho da cooperativa | "é aqui que se forma quem decide" |


**Frases de marca** (usar como estão): Mais que uma formação, uma transformação · Aqui tem prática · Ponto fora da caixa · Professores que vivem o que ensinam · Eles vêm do mercado para a sala de aula · Excelência profissional não é um dom, é repetição com metodologia · A PPGVET não termina quando a aula acaba · Não é só mais uma pós-graduação · Enquanto outras oferecem pós-graduação, nós oferecemos uma transformação (PPGVET) · A decisão que separa quem assiste de quem lidera o mercado (PPG).

**Sempre**: dizer que somos os maiores e os melhores, com o número do lado · urgência de campanha (contador, últimas vagas, turma fechando) · a mão na massa em foto e vídeo · professor com cargo e empresa · a dor numa cena concreta · frase de efeito curta no título, explicação no corpo.
**Nunca**: cara de faculdade tradicional (beca, capelo, pilha de livro, quadro-negro) · academiquês ("contribuir para a formação de profissionais qualificados") · foto de banco fingindo ser aluno, professor ou sede · texto que serviria para qualquer escola (trocou o nome e continua valendo: refazer).

- **Texto**: português humano, sem travessão, sem cara de IA; nunca inventar número. Frases de marketing, CTAs variados para a mesma ação, superlativo e urgência ficam (não listar como slop).
- **Provas**: Nota máxima (5) no MEC (da ITH) · 12.000+ alunos ativos (sempre assim, nunca "+12.000", "12K+" ou "12 mil+") · 300+ professores · 100+ turmas · 15+ pós-graduações · alunos em todos os estados e em 7 países (usar quando der autoridade) · podcasts entre os 5% mais compartilhados do Spotify.
- **Botões** (rótulo padrão por ação; a copy pode variar, a caixa não: CTA principal em MAIÚSCULAS, secundário normal): Falar com um especialista · Baixar a Ementa Completa · Garantir minha vaga (só matrícula paga) · Liberar meu acesso gratuito · Entrar na comunidade · Ver a pós (ir à página de uma pós) · Ver o curso (curso livre) · Ler o post (blog) · Confirmar presença (evento).