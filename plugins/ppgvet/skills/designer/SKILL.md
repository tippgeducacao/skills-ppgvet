---
name: designer
description: Arte estática da PPGVET/PPG como um designer da casa - post do feed, carrossel, story, criativo de professor, capa, thumbnail e anúncio, conferida. Use quando pedirem arte, post para o feed ou criativo. Aulas da semana - aulas-da-semana.
---

# Designer (arte estática)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/marca.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/design.md` (o padrão da casa, tirado das artes e dos perfis), `${CLAUDE_PLUGIN_ROOT}/regras/oficio/copy.md` (todo texto da arte) e `${CLAUDE_PLUGIN_ROOT}/regras/antislop-midia.md`.
- Em cada comando: `PY=$(cat ~/.ppgvet/python); S="${CLAUDE_PLUGIN_ROOT}/scripts"; A="${CLAUDE_PLUGIN_ROOT}/acervo"`. Pasta: a linha `artes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<artes>`).

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **A peça:** o que é (post, carrossel, story, criativo de professor, anúncio), onde vai e a marca ou a pós.
- **O objetivo e a ação** (salvar, link na bio, falar com especialista, confirmar presença).
- **O texto**, ou os fatos para escrever (a skill `copy` escreve e confere).
- **As fotos reais** (professor, aula, campo, turma). Professor sem foto anexa: `acervo/professores/<nome-sobrenome>.webp`. Sem foto boa, a peça sai sem foto; nunca banco nem IA fingindo pessoa ou lugar (`sempre.md`).
- Exemplo: *"post para o feed da pós de Suínos chamando para falar com um especialista, com esta foto da aula na granja"*.

## Passo a passo
1. **Referência** (antes do plano; nível padrão e caprichado):
   - Drive conectado: 3 a 5 artes do mesmo tipo nas pastas da equipe, das mais recentes (descer pasta a pasta com `parentId`): artes atuais `1xWSoczhAye1qy_gAeUAQG99GLMD8fS8Y`, artes de 2024 a 2026 `1g5EHmuvCbiIOwAlLUu5WpyYJvk2Sh46y`. Sem Drive: o `oficio/design.md` já resume o padrão, mais os prints que a pessoa mandar.
   - Perfis `@ppgvet_oficial` e `@ppg.educacao`: o que está no ar do mesmo tipo (prints da pessoa, ou a API da Meta, só leitura).
   - Tirar 3 princípios (grid, hierarquia, cor) e desenhar com a marca: copiar o como, nunca a peça.
2. **Plano:** a direção (5 linhas, `antislop-midia.md`), o molde (`oficio/design.md`, "Moldes da casa") ou "fora do molde" com o desenho em palavras, o texto exato de cada campo (a `copy` escreve e confere) e a foto. Peça nova fora do molde: protótipo antes do resto. Esperar o ok.
3. **Montar:**
   - **Peça de molde:** a ficha em `<artes>/<peca>/ficha.json` (campos no `"$PY" "$S/molde.py"` sem argumento) e `"$PY" "$S/molde.py" <artes>/<peca>/ficha.json --saida <artes>/<peca>`. Ele preenche, gera PNG e JPEG, confere cada peça com o `arte.py` e faz a `folha.jpg`.
   - **Fora do molde:** um HTML por peça ou lâmina (`01-capa.html`…), mesmo grid em todas; fonte `@font-face{font-family:Montserrat;src:url('<$A>/fontes/montserrat-variavel.ttf')}`; logos e títulos pelo acervo (`file://`); cores só do `marca.md`; foto tratada antes (`editar-foto`), nunca esticada; faixa ou foto de ponta a ponta com `data-sangra`. Depois `"$PY" "$S/arte.py" <peca>.html --formato <formato>` em cada um.
   - Foto real sempre; sem foto boa, a peça sai sem foto (`sempre.md`).
4. **Medir:** FALHA (texto que estoura, fora da área segura, fonte, contraste medido na peça, inclusive sobre foto, cor fora da marca, texto que a copy barra): corrigir e gerar de novo. AVISO (níveis de letra, palavra sozinha no título, bordas fora do grid, foto esticada): olhar na peça e decidir.
5. **Revisar:**
   - Rápido: nota de 0 a 10 em hierarquia, leitura no celular (~390 px), marca e acabamento (`antislop-midia.md`, "Conferir"); abaixo de 8, corrigir.
   - Padrão e caprichado: chamar o agente `ppgvet:revisor-peca` (ferramenta Agent) com o pedido, a direção, os caminhos dos PNG e da folha, a referência e a saída da medição. "corrige" ou "refaz": ajustar e mandar de volta (rodadas e saída: `nucleo.md`).
6. **Entregar** os JPEG (o que vai para o Instagram) e a folha, com a nota ou o veredito em uma linha. Ajuste vira versão nova (`-v2`); a ficha e o HTML ficam para refazer.

Formatos, tamanhos e área livre: `oficio/design.md`.
