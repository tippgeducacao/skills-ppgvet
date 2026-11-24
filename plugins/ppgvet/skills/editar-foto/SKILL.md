---
name: editar-foto
description: Edita foto da PPGVET/PPG como um fotógrafo - luz, cor, pele, nitidez, horizonte, recorte no tamanho de uso, ampliar e tirar o fundo. Use quando pedirem para editar, melhorar, retocar, ampliar, recortar ou tirar o fundo de uma foto.
---

# Editar foto

O Claude olha a foto, decide o que fazer e explica o porquê; os scripts aplicam. A meta é a foto parecer **bem fotografada, não editada**.

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills).
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"` e `FF=$("$PY" "$S/comum.py" --ff)`. Se `~/.ppgvet/python` não existir, rodar a skill `instalar` primeiro.
- **Ampliar, tirar fundo e `luz_pessoa`** são a parte `foto` do kit, sob demanda (~0,7 GB e ~1 GB de modelos na 1ª vez). Se o comando disser "Falta a parte 'X' do kit": avisar em uma linha, rodar `"$PY" "$S/instalar.py" --X` em segundo plano e repetir.
- Arquivo e versões pelo `nucleo.md` (ex.: `foto-professor-retocada.jpg`). Nível padrão ou caprichado: ler também `${CLAUDE_PLUGIN_ROOT}/regras/oficio/foto.md`.
- **Não inventar:** a edição não muda a pessoa, o animal, o lugar nem o produto. Nada de apagar ou acrescentar coisa na cena, nem trocar céu ou fundo (tirar o fundo só quando pedirem).
- **Fluxo:** plano (para cada foto ou grupo: tipo, o que vai ser feito, recorte e tamanho de uso) e ok; depois todas sem parar; no fim, a revisão com o antes e depois e a nota de cada uma. Muitas fotos parecidas (mesmo evento, mesma luz): mesmos ajustes para todas, para o conjunto ficar igual.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **As fotos** (arquivo ou pasta) e **onde vão ser usadas** (site, card de professor, post, capa): isso define o recorte e o tamanho.
- O que incomoda, se souber ("está escura", "tira o fundo").
- Exemplo de pedido: *"deixa essas fotos do evento profissionais pro Instagram"* + pasta.

## 1. O que o pedido pede
| pedido | o que fazer |
|---|---|
| "melhora", "deixa profissional", foto escura, amarelada, estourada, granulada, torta | **retoque** (passos 2 e 3) |
| tamanho de uso (site, card, Instagram, capa) | `recorte` e `largura` no retoque |
| foto pequena, pixelada ou rosto borrado | **pedir a foto original** (arquivo da câmera, não o do WhatsApp, que reduz). Só sem original: **ampliar** (passo 4), antes do retoque, avisando que fica abaixo do ideal |
| recortar a pessoa ou o objeto sem o fundo | **tirar fundo** (passo 4), depois do retoque |

Ordem quando junta várias: ampliar → retoque → tirar fundo.

## 2. Retoque: medir e olhar
`"$PY" "$S/retocar.py" analisar foto.jpg` e abrir a foto. Ler junto:

| medida | sinal | ajuste |
|---|---|---|
| `brilho_medio` | < 45 escura; > 60 clara (45 a 60 é o normal) | `exposicao` ±0,2 a 0,7 |
| `estourado_%` | > 2 (céu, parede, jaleco branco) | `realces` -20 a -50 |
| `preto_%` > 5 ou rosto com `brilho` < 40 | sombra fechada, contraluz | `sombras` +20 a +50; só a pessoa no escuro com fundo bom (contraluz): `luz_pessoa` +30 a +60 |
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

## 4. Ampliar, tirar fundo, cortar
| tarefa | comando |
|---|---|
| ampliar foto | `"$PY" "$S/imagem.py" ampliar in.jpg out.png` (4x com o modelo 4xNomosWebPhoto, o mais natural em rosto e em foto comprimida; `2` ou `3` no fim se 4x for demais; ~45 s por foto pequena). Último recurso: o detalhe que falta é "adivinhado" |
| ampliar arte ou ilustração | `"$PY" "$S/imagem.py" ampliar in.png out.png --arte` |
| tirar fundo | `"$PY" "$S/imagem.py" fundo in.jpg out.png` (pessoa: `--pessoa`, que recorta melhor cabelo e ombro e limpa o halo do fundo antigo) |
| cortar num ponto exato | `"$FF" -i in.png -vf "crop=w:h:x:y,scale=W:-1" out.png` (enquadrar pelo rosto numa proporção: `recorte` do retoque) |

Na primeira vez, o `fundo` baixa o modelo de recorte (~1 GB; um para pessoa, outro para objeto). Avisar que demora.

## 5. Conferir, dar nota e entregar
- Antes e depois lado a lado (mesma altura): `"$FF" -i in.jpg -i out.jpg -filter_complex "[0]scale=-1:700[a];[1]scale=-1:700[b];[a][b]hstack" cmp.jpg` e abrir.
- Perguntas: a pele está com cor de pele? O branco está branco? O céu tem detalhe? Ficou natural?
- Rosto ampliado: não ficou "de plástico" nem mudou a pessoa? Se mudou, ampliar menos (`2`).
- Fundo tirado: olhar as bordas (cabelo, dedos) sobre um fundo escuro e um claro.
- Nota de 0 a 10 em: natural (não parece editada), luz, cor e pele, nitidez, enquadramento. Abaixo de 8: refazer com outra intensidade. Não melhorou: dizer isso e entregar o original.
- Mostrar o antes e depois para a pessoa com o que foi feito, uma linha por ajuste (exemplo: "sombras +25: o rosto estava no escuro").
- Limpar depois da aprovação: as folhas de antes e depois e os arquivos intermediários (ampliada antes do retoque etc.). Ficam o original e a entrega.
- Imagem de terceiros: sempre do assunto real (banco e IA: `sempre.md`), com `.origem.txt` ao lado (link e licença).
