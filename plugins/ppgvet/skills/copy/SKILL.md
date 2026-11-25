---
name: copy
description: Texto de marketing da PPGVET/PPG como um copywriter da casa - a legenda que vai embaixo do post, arte, WhatsApp, anúncio, e-mail, roteiro de vídeo e pauta, conferidos. Use para copy e todo texto para publicar. Legenda dentro do vídeo - skill video.
---

# Copy (texto de marketing)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/copy.md` (o ofício e as regras da casa) e `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marcas, pós e nomes).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`.

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **O que é:** legenda (de qual post), texto da arte, mensagem de WhatsApp, anúncio, e-mail, roteiro de vídeo (quem vai falar) ou pauta da semana (de qual perfil, e o material que existe: vídeos, fotos, aulas e lives da semana); de qual marca e qual pós, aula, live, podcast ou evento.
- **Os fatos:** data, horário, professor (com titulação comprovada), números, link do gerador "Links com UTM" do sistema (sem ele: `utm.py gerar` monta pela regra do `canais.md` e a pessoa confere no gerador; link antigo: `utm.py arrumar`). O texto só usa o que vier daqui ou de fonte oficial (`marca.md`, site da pós).
- **Para quem e para quê:** quem vai ler e o que deve fazer depois (salvar, clicar no link, responder, confirmar presença).
- Exemplo: *"legenda do carrossel da live de quinta, pós PS, tema bem-estar na maternidade, com o professor Fulano; link: <do gerador>"*.

## Passo a passo
1. **Entender a peça:** tipo, marca, pós, objetivo, nível de consciência de quem lê e o fato que sustenta o texto (`copy.md`). Faltou fato: perguntar; nunca inventar número, nome, titulação, depoimento nem resultado. Número, prova ou nome que a própria pessoa trouxe e que bate de frente com o `marca.md` ("15 mil formados", "MBA", "Prof."): não entra no texto entregue. Mostrar a regra e a forma oficial e perguntar a fonte **antes** de escrever; sem fonte, as versões usam a forma oficial.
2. **Escrever 2 ou 3 versões** que mudam de verdade (gancho e ângulo diferentes: a dor em cena, o número, o professor, a pergunta), cada uma no tamanho e na estrutura do tipo (`copy.md`). Pauta: uma tabela só, sem versões; cada linha com o material real que ela usa.
3. **Conferir cada versão:** salvar num `.txt` e rodar `"$PY" "$S/checar_texto.py" versao.txt --tipo <legenda|arte|whatsapp|anuncio|roteiro|email|pauta>` (anúncio: `--titulo "<título>"`; e-mail: `--titulo "<assunto>"`). FALHA: corrigir e rodar de novo. AVISO: olhar e decidir. Depois, a leitura do ofício: o gancho para no ~125º caractere com sentido completo? Serve para qualquer escola (trocou o nome e continua valendo)? Então refazer.
4. **Mostrar em caixas** (AskUserQuestion; a pauta vai como tabela): as versões como opções, a recomendada primeiro, com uma linha do porquê; "manter o meu texto" no Other. O texto final é de quem pede: ajuste vira versão nova, sem discutir gosto.
5. **Entregar** o texto escolhido pronto para colar, com o resultado da conferência em uma linha. Anúncio: entregar como proposta para o responsável pelo tráfego (não é da equipe de conteúdo publicar).
