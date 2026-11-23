# Marca nos vídeos

Cópia, para o vídeo, do guia de marca da PPGVET (21/11/2026). Se o guia mudar, este arquivo muda junto.

## Duas marcas, nunca misturadas
- **PPGVET** (veterinária) e **PPG Educação** (gestão e cooperativismo). Vídeo da PPG fecha com a logo da PPG, vídeo da PPGVET com a da PPGVET.
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
| encerramento PPG | `logos-animadas/encerramento-ppg-vertical.mp4` (1080x1920, 6 s) | fim de vídeo vertical PPG |
| logo 3D PPGVET | `logos-animadas/logo-ppgvet-horizontal.mp4` (1920x1080, 15 s, mudo) | abertura e fim de vídeo horizontal |
| abertura de aula | `intro/PPGVET.mov` (10,7 s, com slogan) | toda aula curricular, mesmo de pós da PPG |
| molduras das pós | `molduras-aula/<AVES, BOVINOS, PADRÃO, PETFOOD, QUALIDADE, SUÍNOS>.png` | aula curricular (qual moldura de cada pós: tabela abaixo) |
| moldura de intro de aula | `molduras/moldura-aula-ppgvet-ppg-16x9.png` (o vídeo entra no retângulo azul x 241..1678, y 134..944) | intro de aula com as duas marcas |
| card do professor | `card-professor/card-sem-nome.png` | base do card gerado na hora na aula curricular |
| fontes | `fontes/`: Montserrat (legenda, títulos, Reels), Lexend Exa e Artegra Sans (card do professor) | os scripts já usam |
| referências de aula | `aulas-referencia/<SIGLA>.jpg` (vazia por enquanto; entra quando uma aula da pós for aprovada) | intro e moldura aprovadas de cada pós (`conferir-aula`) |

| marca | principal | ação | destaque na legenda |
|---|---|---|---|
| PPGVET | magenta `#D24BA8` | teal `#00B7AB` | rosa `#E371C0` |
| PPG | azul `#1670C2` | teal `#00ADA3` | teal `#00ADA3` |

## Pós (sigla, nome e moldura da aula curricular)
| sigla | nome | marca | moldura |
|---|---|---|---|
| RNGB | Reprodução, Nutrição e Gestão de Bovinos | PPGVET | BOVINOS |
| NGB | Nutrição e Gestão de Bovinos | PPGVET | BOVINOS |
| CMCB | Clínica Médica e Cirúrgica de Bovinos | PPGVET | BOVINOS |
| GPL | Gestão na Pecuária Leiteira | PPGVET | BOVINOS |
| SA | Sanidade Avícola | PPGVET | AVES |
| PC | Postura Comercial | PPGVET | AVES |
| PS | Produção de Suínos | PPGVET | SUÍNOS |
| CBEA | Comportamento e Bem-Estar Animal | PPGVET | PETFOOD |
| CMMV | Cannabis Medicinal na Medicina Veterinária | PPGVET | PETFOOD |
| QSAOA | Qualidade e Segurança de Alimentos de Origem Animal | PPGVET | QUALIDADE |
| SUZ | Saúde Única e Zoonoses | PPGVET | QUALIDADE |
| GPERA | Gestão de Pessoas e Extensão Rural na Agroindústria | PPGVET | PADRÃO |
| PPT | Piscicultura e Produção de Tilápia | PPGVET | perguntar |
| MIFV | Medicina Integrativa e Fitoterapia Veterinária com Ênfase em Cães e Gatos | PPGVET | perguntar |
| GIA | Gestão da Indústria de Alimentos Ênfase em Tecnologia e Inteligência Artificial | PPGVET | perguntar |
| GCC | Gestão de Cooperativas de Crédito | PPG | PADRÃO |
| CRCV | Crédito Rural, Cooperativismo e Vendas | PPG | PADRÃO |
| GPDCA | Gestão de Pessoas e Desenvolvimento de Carreira no Agronegócio | PPG | perguntar |
| MVPA | Marketing e Vendas na Produção Animal | PPG | perguntar |

A coluna moldura é a tabela `MOLDURA` do `scripts/aula.py` (o script é quem manda). Sigla fora dela: perguntar qual moldura usar.
