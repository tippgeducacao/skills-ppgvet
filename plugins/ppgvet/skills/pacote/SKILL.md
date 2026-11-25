---
name: pacote
description: Pacote de uma entrega que sai sempre junta - entrada de professor, episódio de podcast, aquecimento, abertura de turma e lançamento de pós - num pedido só, com mesmo nome, data e link. Use quando pedirem o pacote ou kit dessas entregas.
---

# Pacote (as peças de uma entrega, de uma vez)

Não cria peça nova: junta as que a `designer`, a `copy`, a `editar-foto` e a `video` já fazem, com um plano só e uma ficha só.

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`. Cada peça segue a skill dela (o `SKILL.md` de `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/`), sem repetir o plano dela: o plano do pacote já cobre.
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`. Pasta: a linha `artes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<artes>`).

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **Qual entrega** (tabela abaixo) e **a ficha:** marca e pós (sigla), data, dia e horário, professor ou convidado (nome conferido, titulação comprovada, foto real), tema e o link do gerador "Links com UTM" (`canais.md`). Podcast: qual podcast, número do episódio e os links dele.
- **Peça fora da tabela:** só com um exemplo pronto (imagem ou link); sem exemplo, fica de fora. Nunca inventar o formato.
- Exemplo: *"pacote de entrada do professor Bruno Lima, pós de Produção de Suínos, primeira aula 10/12 às 19h, foto anexa, link: <do gerador>"*.

## As entregas
| entrega | peças (quem faz) | origem |
|---|---|---|
| **entrada de professor** | post de apresentação no feed, molde `professor` com foto real (`designer`), e legenda (`copy`) · aviso ao responsável pelo tráfego: pós, professor, data e link, em WhatsApp (`copy`) | tarefas do sistema |
| **episódio de podcast** | thumb do YouTube (`designer`, molde `thumb`) · post do episódio (`designer`) e legenda com "O que você irá aprender" em 4 tópicos (`copy`, regras de podcast do `copy.md`) · cortes na ordem e na quantidade do documento de cortes da equipe (`video`) · descrição do player em branco, salvo pedido | tarefas do sistema, `copy.md` |
| **aquecimento** (aula ou evento) | capas dos grupos: data da aula, "é hoje", "última chance", "matrículas encerradas" (`designer`) · post ou story de antecipação (`designer`) · mensagens de 7 dias, 5 dias e do dia, em WhatsApp e e-mail (`copy`) · teaser para soltar no dia (`video`) | modelo de abertura do sistema |
| **abertura de turma** | o aquecimento, mais: 2 criativos para alunos (um com o professor, um geral) · 2 para o comercial ("última chance", "matrículas abertas") · 2 de disparo ("habilidades que você vai desenvolver", diferenciais da pós) · 8 artes de patrocinado (molde `kv` ou `professor` em `anuncio`, e `story` em `story-anuncio`, mudando só gancho e foto) e 8 variações para a secretaria (as mesmas em `feed`), sem "aula gratuita" nem "oportunidade única" · capa do YouTube (molde `thumb`) · QR do link da ficha, lido de volta para conferir (`"$PY" -c "import sys; sys.path.insert(0, '$S'); from live_qr import gerar_qr, ler_qr; gerar_qr('<link>', 'qr.png'); print(ler_qr('qr.png'))"`) · roteiro do vídeo do professor convidando, até 40 s em story, para ele gravar (`copy`) · banner do e-mail (`--formato email`) | modelo de abertura do sistema |
| **lançamento de pós** | KV: 5 a 9 peças, uma ideia cada (molde `kv`, foto real da pós) · capas do portal do aluno (skill `capas-eduq`) | tarefas do sistema, artes da equipe |

## Passo a passo
1. **Ficha:** gravar `<artes>/pacotes/<entrega>-<pos>-<dd-mm>/ficha.txt` com tudo do "O que preciso". Toda peça usa só a ficha; o dia da semana sai da data.
2. **Plano único:** tabela com cada peça, formato, skill que faz e o texto exato de cada uma (a `copy` escreve antes). Esperar o ok.
3. **Fazer, sem parar:** foto (`editar-foto`) → textos (`copy`, com o `checar_texto.py`) → artes (`designer`, com o `arte.py`) → vídeos (`video`, com o `checar.py`). Numerar as peças na ordem de uso (`01-…`, `02-…`).
4. **Conferir o pacote junto** (checklist do modelo do sistema): nome, pós, data, dia, horário e link iguais em todas as peças e mensagens; português de todo criativo que vai para o tráfego; @ de colaborador público; uma folha com todas as artes lado a lado (mesmo grid, mesma cor da pós). Nota de 0 a 10 do pacote; abaixo de 8, corrigir.
5. **Entregar** a pasta, a folha, os textos num `textos.txt` (um bloco por peça) e uma tabela: peça, onde vai, quando publicar. Ajuste vira versão nova da peça (`-v2`).
