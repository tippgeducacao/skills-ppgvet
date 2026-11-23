---
name: editar-foto
description: Edita foto da PPGVET como um fotógrafo profissional - retoque de luz, exposição, balanço de branco, contraste, cor, sombras e realces, pele suave sem "plástico", ruído, nitidez e horizonte torto; enquadramento e recorte no tamanho de uso; ampliar sem borrar (Real-ESRGAN); tirar o fundo (rembg); melhorar rosto borrado (GFPGAN, só no Mac). Para retrato de professor, campo e evento, post de Instagram e produto ou material. Use quando pedirem para editar, melhorar, tratar, retocar ou "deixar profissional" uma foto, corrigir foto escura, amarelada, estourada, granulada ou torta, ampliar, recortar, redimensionar, tirar o fundo ou melhorar um rosto.
---

# Editar foto

O Claude olha a foto, decide o que fazer e explica o porquê; os scripts aplicam. A meta é a foto parecer **bem fotografada, não editada**.

## Antes de começar
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"` e `FF=$("$PY" "$S/comum.py" --ff)`. Se `~/.ppgvet/python` não existir, rodar a skill `instalar` primeiro.
- **Original nunca muda.** Sempre partir do original em alta. A saída é um arquivo novo ao lado, com nome minúsculo-com-hífen (`foto-professor-retocada.jpg`); se já existir, `-v2`. **Menor, mas nunca mais feia.**
- **Não inventar:** a edição não muda a pessoa, o animal, o lugar nem o produto. Nada de apagar ou acrescentar coisa na cena, nem trocar céu ou fundo (tirar o fundo só quando pedirem).
- **Fluxo:** plano (para cada foto ou grupo: tipo, o que vai ser feito, recorte e tamanho de uso) e ok; depois todas sem parar; no fim, a revisão com o antes e depois e a nota de cada uma. Muitas fotos parecidas (mesmo evento, mesma luz): mesmos ajustes para todas, para o conjunto ficar igual.

## 1. O que o pedido pede
| pedido | o que fazer |
|---|---|
| "melhora", "deixa profissional", foto escura, amarelada, estourada, granulada, torta | **retoque** (passos 2 e 3) |
| tamanho de uso (site, card, Instagram, capa) | `recorte` e `largura` no retoque |
| foto pequena ou pixelada | **ampliar** (passo 4), antes do retoque |
| rosto borrado (só no Mac) | **melhorar rosto** (passo 4), antes do retoque |
| recortar a pessoa ou o objeto sem o fundo | **tirar fundo** (passo 4), depois do retoque |

Ordem quando junta várias: ampliar ou melhorar rosto → retoque → tirar fundo.

## 2. Retoque: medir e olhar
`"$PY" "$S/retocar.py" analisar foto.jpg` e abrir a foto. Ler junto:

| medida | sinal | ajuste |
|---|---|---|
| `brilho_medio` | < 45 escura; > 60 clara (45 a 60 é o normal) | `exposicao` ±0,2 a 0,7 |
| `estourado_%` | > 2 (céu, parede, jaleco branco) | `realces` -20 a -50 |
| `preto_%` > 5 ou rosto com `brilho` < 40 | sombra fechada, contraluz | `sombras` +20 a +50 |
| `dominante_b` | > 8 amarelada (lâmpada, galpão); < -4 azulada | `auto_branco` e `temperatura` para o resto |
| `dominante_a` | > 4 magenta; < -4 esverdeada (luz fria, folhagem) | `matiz` |
| `contraste` | < 15 chapada (dia nublado); > 28 dura (sol a pino) | `contraste` ±10 a 25, `clareza` |
| `nitidez` | < 100 mole | `nitidez` 20 a 50 (foto realmente fora de foco: avisar, retoque não salva) |
| foto de celular à noite ou de dentro | granulado visível | `ruido` 20 a 50 |
| horizonte, poste ou parede tortos | olhando a foto | `girar` (graus; positivo = anti-horário) |

## 3. Retoque: ajustes por tipo de foto e aplicar
| tipo | ajustes típicos | recorte |
|---|---|---|
| **retrato de professor** | `auto_branco`, `sombras` +15 a 30 no rosto, `pele` 25 a 40, `nitidez` 20, `vibracao` +10, `contraste` leve | `3:4` (site, card) ou `1:1`; o rosto fica no terço de cima |
| **campo e evento** (fazenda, granja, aula prática, turma) | `realces` negativo (céu), `sombras` positivo, `clareza` 20 a 35, `vibracao` +15 a 25, `girar` se torto | `4:5` (feed) ou `16:9` (capa) |
| **post de Instagram** | o do tipo da foto + `largura` 1080 | `4:5` (feed) ou `9:16` (story) |
| **produto e material** (livro, kit, apostila) | `auto_branco` (branco tem que ficar branco), `exposicao` positiva, `contraste` +10, `clareza` 15, `nitidez` 30, sem `pele` | `1:1` ou `4:5` |

Limites para não parecer editada: `saturacao` raramente passa de +15 (usar `vibracao`), `pele` nunca passa de 50, `clareza` nunca passa de 40 em rosto, e verde de pasto e pele de gente continuam com cor de verdade.

Aplicar: `"$PY" "$S/retocar.py" aplicar foto.jpg foto-retocada.jpg '{"auto_branco": true, "sombras": 25, "pele": 30, "nitidez": 20, "recorte": "3:4"}'`
(todos os ajustes e faixas: `"$PY" "$S/retocar.py"` sem argumentos). O perfil de cor (ICC) e a orientação da foto são mantidos.

## 4. Ampliar, melhorar rosto, tirar fundo, cortar
| tarefa | comando |
|---|---|
| ampliar foto | `"$PY" "$S/imagem.py" ampliar in.jpg out.png` (4x; `2` ou `3` no fim se 4x for demais) |
| ampliar arte ou ilustração | `"$PY" "$S/imagem.py" ampliar in.png out.png --arte` |
| melhorar rosto (só Mac) | `"$PY" "$S/imagem.py" rosto in.jpg out.png` (devolve 2x). No Windows: usar `ampliar` |
| tirar fundo | `"$PY" "$S/imagem.py" fundo in.jpg out.png` (pessoa: `--pessoa`, que recorta melhor cabelo e ombro) |
| cortar num ponto exato | `"$FF" -i in.png -vf "crop=w:h:x:y,scale=W:-1" out.png` (enquadrar pelo rosto numa proporção: `recorte` do retoque) |

Na primeira vez, o `fundo` baixa o modelo de recorte (de ~170 MB a ~1 GB com `--pessoa`). Avisar que demora.

## 5. Conferir, dar nota e entregar
- Antes e depois lado a lado (mesma altura): `"$FF" -i in.jpg -i out.jpg -filter_complex "[0]scale=-1:700[a];[1]scale=-1:700[b];[a][b]hstack" cmp.jpg` e abrir.
- Perguntas: a pele está com cor de pele? O branco está branco? O céu tem detalhe? Ficou natural?
- Rosto do GFPGAN: não ficou "de plástico" nem mudou a pessoa? Se mudou, usar só o `ampliar`.
- Fundo tirado: olhar as bordas (cabelo, dedos) sobre um fundo escuro e um claro.
- Nota de 0 a 10 em: natural (não parece editada), luz, cor e pele, nitidez, enquadramento. Abaixo de 8: refazer com outra intensidade. Não melhorou: dizer isso e entregar o original.
- Mostrar o antes e depois para a pessoa com o que foi feito, uma linha por ajuste (exemplo: "sombras +25: o rosto estava no escuro").
- Limpar depois da aprovação: as folhas de antes e depois e os arquivos intermediários (ampliada antes do retoque etc.). Ficam o original e a entrega.
- Imagem de terceiros: sempre do assunto real, nunca genérica fingindo ser aluno, professor ou sede, nada gerado por IA, e com `.origem.txt` ao lado (link e licença).
