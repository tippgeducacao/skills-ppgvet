---
name: video
description: Edição de vídeo e áudio da PPGVET/PPG - chamada, depoimento, aula curricular, treinamento, conferir aula que alguém editou, cortes de live, Reels, motion (vinheta, abertura), limpar áudio e baixar vídeo. Use para editar, cortar, legendar ou conferir.
---

# Vídeo

Porta das tarefas de vídeo: acha a tarefa, lê o passo a passo dela e segue. Cada tarefa também pode ser chamada direto, com `/ppgvet:<tarefa>`.

| pedido | tarefa |
|---|---|
| chamada de professor ou depoimento de aluno para o Instagram | `chamada` |
| tarefa de aula curricular do Meet ("Inserir abertura animada… Nomear aula como… Anexar no Panda") | `aula-curricular` |
| treinamento do comercial, de embaixadores ou de ferramenta para o PPGVET Academy | `treinamento-academy` |
| conferir aulas que alguém já editou | `conferir-aula` |
| cortes de live ou de aula gravada em posts 9:16; aula completa de uma live | `cortes-live` |
| Reels de fala, legenda, cor, música, compressão, qualquer outra edição | `editar-video` |
| áudio sozinho (podcast, locução, áudio de WhatsApp): limpar ruído, igualar volume, cortar | `editar-video` ("Só áudio") |
| baixar vídeo de um link (YouTube, Instagram, TikTok…) | `baixar-video` |
| peça de motion sozinha: abertura, vinheta, logo ou texto animado, explicativo animado | `motion` |

1. Ler `${CLAUDE_PLUGIN_ROOT}/skills/<tarefa>/SKILL.md` inteiro e seguir. Nesse arquivo, a raiz do pacote (`CLAUDE_PLUGIN_ROOT`) é `${CLAUDE_PLUGIN_ROOT}`.
2. Pedido que cabe em duas tarefas, ou em nenhuma: perguntar qual, em caixa de opção (regra de perguntas do `nucleo.md`).
3. Foto é a skill `editar-foto`; arte estática, a `designer`; texto, a `copy`; preparar o computador, a `instalar`. Som não tem skill própria: vai dentro do vídeo (`oficio/som.md`) ou no "Só áudio" da `editar-video`.
